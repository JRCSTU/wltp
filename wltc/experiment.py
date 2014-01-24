#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# Copyright 2013-2014 ankostis@gmail.com
#
# This file is part of wltc.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.

'''The main class for the WLTC gear-shift calculator which consumes a Model and the WLTC-data and updates the Model with the results (gears, downscaled velocity-profile) .

An "execution" or a "run" of an experiment is depicted in the following diagram::

                       _______________
     .-------.        |               |      .------------------.
    / Model /-.   ==> |   Experiment  | ==> / Model(augmented) /
   '-------'  /   ==> |---------------|    '------------------'
     .-------'        |  .-----------.|
                      | / WLTC-data / |
                      |'-----------'  |
                      |_______________|

Usage:
======

A usage example::

    >> import wltc

    >> model = wltc.Model({
        "vehicle": {
            "mass":     1500,
            "v_max":    195,
            "p_rated":  100,
            "n_rated":  5450,
            "n_idle":   950,
            "n_min":    None, # Can be overriden by manufacturer.
            "gear_ratios":      [120.5, 75, 50, 43, 37, 32],
            "resistance_coeffs":[100, 0.5, 0.04],
        }
    }

    >> experiment = wltc.Experiment(model)
    >> experiment.run()
    >> print(model.data['results'])
    >> print(model.driveability_report())



    >> {
        'wltc_class':   'class3b'
        'v_class':      [ 0.,  0.,  0., ...,  0.,  0.,  0.],
        'f_downscale':  0,
        'v_target':     [ 0.,  0.,  0., ...,  0.,  0.,  0.],
        'gears':        [0, 0, 0, ..., 0, 0, 0],
        'clutch':       array([ True,  True,  True, ...,  True,  True,  True], dtype=bool),
        'v_real':       [ 0.,  0.,  0., ...,  0.,  0.,  0.],
        'driveability': {...},
    }


For information on the model-data, check the schema::

    print(wltc.instances.model_schema())


Implementation:
===============

Note: ALL_CAPITALS variable denote vectors, usually over the velocity-profile (the cycle),
for instance, GEARS is like that::

     t:||: 0  1  2  3
    ---+-------------
    g1:|[[ 1, 1, 1, 1, ... 1, 1
    g2:|   2, 2, 2, 2, ... 2, 2
    g3:|   3, 3, 3, 3, ... 3, 3
    g4 |   4, 4, 4, 4, ... 4, 4 ]]


Vectors:
--------

V:        floats (#cycle_steps)
    The wltc-class velocity profile.

GEARS:    integers (#gears X #cycle_steps)
    One row for each gear (starting with 1 to #gears).

GEARS_YES:  boolean (#gears X #cycle_steps)
    One row per gear having ``True`` wherever gear is possible for each step.

N_GEARS:  floats (#gears X #cycle_steps)
    One row per gear with the Engine-revolutions required to follow the V-profile (unfeasable revs included),
    produced by multiplying ``V * gear-rations``.

.. log:: logger for the experiment.


@author: ankostis@gmail.com
@since: 1 Jan 2014
'''

import numpy as np
import logging
import re


log = logging.getLogger(__name__)


def _shapes(*arrays):
    import operator
    op_shape = operator.attrgetter('shape')
    return list(map(op_shape, arrays))

def _dtypes(*arrays):
    import operator
    op_shape = operator.attrgetter('dtype')
    return list(map(op_shape, arrays))


class Experiment(object):
    '''Runs the vehicle and cycle data describing a WLTC experiment.

    See :mod:`wltc.experiment` for documentation.
    '''


    def __init__(self, model, validate_wltc = False):
        """
        ``model`` is a tree (formed by dicts & lists) holding the experiment data.

        ``skip_validation`` when true, does not validate the model.
        """

        from .instances import wltc_data

        self.dtype = np.float32
        self.model = model
        self.wltc = wltc_data()

        if (validate_wltc):
            self.validateWltc()


    def validateWltc(self, iter_errors=False):
        from .schemas import wltc_validator

        if iter_errors:
            return wltc_validator().iter_errors(self.wltc)
        else:
            wltc_validator().validate(self.wltc)




    def run(self):
        '''Invokes the main-calculations and extracts/update Model values!

        @see: Annex 2, p 70
        '''

        data        = self.model.data
        vehicle     = data['vehicle']

        ## Prepare results
        self.results = results = data['results'] = {}

        ## Extract vehicle attributes from model.
        #
        mass                = vehicle['mass']
        v_max               = vehicle['v_max']
        p_rated             = vehicle['p_rated']
        n_rated             = vehicle['n_rated']
        n_idle              = vehicle['n_idle']
        n_min_drive         = vehicle['n_min']
        gear_ratios         = vehicle['gear_ratios']
        (f0, f1, f2)        = vehicle['resistance_coeffs']
        params              = data['params']


        ## Decide WLTC-class.
        #
        class_limits            = self.wltc['classification']['p_to_mass_class_limits']
        class3_velocity_split   = self.wltc['classification']['class3_split_velocity']
        wltc_class              = decideClass(class_limits, class3_velocity_split, mass, p_rated, v_max)
        results['wltc_class']   = wltc_class
        class_data              = self.wltc['classes'][wltc_class]
        cycle                   = np.array(class_data['cycle'])


        ## Velocity-profile
        #
        V                   = np.array(cycle, dtype=self.dtype)
        results['v_class'] = V

        ## Required-Power needed early-on by Downscaling.
        #
        f_inertial          = params.get('f_inertial', 1.1)
        (A, P_REQ)          = calcPower_required(V, mass, f0, f1, f2, f_inertial)


        ## Downscale velocity-profile.
        #
        dsc_data            = class_data['downscale']
        phases              = dsc_data['phases']
        p_max_values        = dsc_data['p_max_values']
        downsc_coeffs       = dsc_data['factor_coeffs']
        dsc_v_split         = dsc_data.get('v_max_split', None)
        f_downscale         = calcDownscaleFactor(P_REQ,
                                                      p_max_values, downsc_coeffs, dsc_v_split,
                                                      p_rated, v_max)
        results['f_downscale'] = f_downscale
        if (f_downscale > 0):
            V               = downscaleCycle(V, f_downscale, phases)
        results['v_target'] = V


        ## Run cycle to find gears, clutch and real-velocirty.
        #
        load_curve          = vehicle['full_load_curve']
        (V_REAL, GEARS, CLUTCH, driveability_issues) = \
                            runCycle(V, A, P_REQ,
                                           gear_ratios,
                                           n_idle, n_min_drive, n_rated,
                                           p_rated, load_curve,
                                                       params)
        assert               V.shape == GEARS.shape, _shapes(V, GEARS)

        results['v_real']       = V_REAL
        results['gears']        = GEARS
        results['clutch']       = CLUTCH
        results['driveability'] = driveability_issues




#######################
## PURE CALCULATIONS ##
#######################


def addDriveabilityMessage(time_steps, msg, driveability_issues):
    driveability_issues[time_steps].append(msg)


def addDriveabilityProblems(GEARS_BAD, reason, driveability_issues):
    failed_steps = GEARS_BAD.nonzero()[0]
    if (failed_steps.size != 0):
        log.warning('%i %s: %s', failed_steps.size, reason, failed_steps)
        for step in failed_steps:
            addDriveabilityMessage(step, reason, driveability_issues)


def decideClass(class_limits, class3_velocity_split, mass, p_rated, v_max):
    '''

    @see: Annex 1, p 19
    '''

    p_m_ratio           = (1000 * p_rated / mass)
    if (p_m_ratio > class_limits[-1]):
        wltc_class      = 'class3'
        ab              = 'b' if v_max >= class3_velocity_split else 'a'
        wltc_class      += ab
    elif (p_m_ratio > class_limits[-2]):
        wltc_class      = 'class2'
    else:
        wltc_class      = 'class1'
    return wltc_class



def calcDownscaleFactor(P_REQ, p_max_values, downsc_coeffs, dsc_v_split, p_rated, v_max):
    '''Check if downscaling required, and apply it.

    @return: :float:
    @see: Annex 1-7, p 68
    '''
    downscale_threshold     = 0.1 # Move downscale_threshold to model

    ## Max required power
    #
    p_req_max               = P_REQ[p_max_values[0]]
    r_max                   = (p_req_max / p_rated)

    ## Cycle r0
    #
    if dsc_v_split is not None:
        assert              len(downsc_coeffs) == 2, downsc_coeffs

        downsc_coeffs       = downsc_coeffs[0] if (v_max <= dsc_v_split) else downsc_coeffs[1]

    if (downsc_coeffs is None):
        f_downscale         = 0
    else:
        (r0, a1, b1) = downsc_coeffs

        if (r_max < r0):
            f_downscale     = 0
        else:
            f_downscale     = a1 * r_max + b1
            f_downscale     = round(f_downscale, 1)
            if (f_downscale <= downscale_threshold):
                f_downscale = 0


    return f_downscale


def downscaleCycle(V, f_downscale, phases):
    '''Downscale just by scaling the 2 phases demarked by the 3 time-points with different factors,
    no recursion as implied by the specs.

    @see: Annex 1-7, p 64-68
    '''
    ERR = 1e-10
    (t0, t1, t2)    = phases

    ## Accelaration phase
    #
    ix_acc          = np.arange(t0, t1 + 1)
    offset_acc      = V[t0]
    acc_scaled      = (1 - f_downscale) * (V[ix_acc] - offset_acc) + offset_acc
    assert          abs(acc_scaled[0] - V[t0]) < ERR, \
                                    ('smooth-start: ', acc_scaled[0],  V[t0])

    ## Deccelaration phase
    #
    ix_dec          = np.arange(t1 + 1, t2 + 1)
    offset_dec      = V[t2]
    f_corr          = (acc_scaled[-1] - offset_dec) / (V[t1] - offset_dec)
    dec_scaled      = f_corr * (V[ix_dec] - offset_dec) + offset_dec
    assert          abs(dec_scaled[-1] - V[t2]) < ERR, \
                                    ('smooth-finish: ', dec_scaled[-1],  V[t2])

    scaled          = np.hstack((acc_scaled, dec_scaled))
    assert          abs(scaled[t1 - t0] - scaled[t1 - t0 + 1]) <= abs(V[t1] - V[t1 + 1]), \
                                    ('smooth-tip: ', scaled[t1 - t0], scaled[t1 - t0 + 1], V[t1], V[t1 + 1])

    V_DSC           = np.hstack((V[:t0], scaled, V[t2 + 1:]))
    assert          V.shape == V_DSC.shape, _shapes(V, V_DSC)

    return V_DSC


def calcEngineRevs_required(V, gear_ratios, n_idle):
    '''Calculates the required engine-revolutions to achieve target-velocity for all gears.

    @return :array: N_GEARS:   a (#gears X #velocity) float-array, eg. [3, 150] --> gear(3), time(150)
    @return :array: GEARS:     a (#gears X #velocity) int-array, eg. [3, 150] --> gear(3), time(150)
    @see: Annex 2-3.2, p 71
    '''

    assert              V.ndim == 1 and len(V) > 100, (V.shape, gear_ratios, n_idle)

    nG                  = len(gear_ratios)
    nV                  = len(V)

    GEARS               = np.tile(np.arange(0, nG, dtype='int8')+ 1, (nV, 1)).T
    assert              GEARS.shape == (nG, nV), (GEARS.shape, gear_ratios, nV)

    GEAR_RATIOS         = np.tile(gear_ratios, (nV, 1)).T     ## TODO: Prepend row for idle-gear in N_GEARS
    N_GEARS             = np.tile(V, (nG, 1)) * GEAR_RATIOS
    assert              GEARS.shape  == GEAR_RATIOS.shape == N_GEARS.shape, _shapes(GEARS, GEAR_RATIOS, N_GEARS, V)

    stopped_steps                       = (V == 0)
    N_GEARS [:, stopped_steps]          = n_idle
    GEARS   [:, stopped_steps]          = 0

    return (N_GEARS, GEARS)


def possibleGears_byEngineRevs(V, A, N_GEARS,
                               ngears, n_idle,
                               n_min_drive, n_clutch_gear2, n_min_gear2, n_max, v_stopped_threshold,
                               driveability_issues):
    '''Calculates the engine-revolutions limits for all gears and returns for which they are accepted.

    @return GEARS_YES:list(booleans, nGears x CycleSteps): possibibilty for all the gears on each cycle-step
                    (eg: [0, 10] == True --> gear(1) is possible for t=10)
    @see: Annex 2-3.2, p 71
    '''

    ## Identify impossible-gears by n_MAX.
    #
    GEARS_YES_MAX                           = (N_GEARS <= n_max)
    GEARS_BAD                               = (~GEARS_YES_MAX).all(axis=0)
    addDriveabilityProblems(GEARS_BAD, 'g%i: Revolutions too high!' % ngears, driveability_issues)

    ## Replace impossibles with max-gear & revs.
    #
    GEARS_YES_MAX[ngears - 1, GEARS_BAD]    = True
    N_GEARS[ngears - 1, GEARS_BAD]          = n_max


    ## Identify impossible-gears by n_MIN.
    #
    ## TODO: Construct a matrix of n_min_drive for all gears, including exceptions for gears 1 & 2.
    #
    GEARS_YES_MIN           = (N_GEARS >= n_min_drive)
    GEARS_YES_MIN[0, :]     = (N_GEARS[0, :] >= n_idle) | (V <= v_stopped_threshold) # V == 0 --> neutral # FIXME: move V==0 into own gear.
    N_GEARS2                = N_GEARS[1, :]
    ## NOTE: "interpratation" of specs for Gear-2
    #        and FIXME: NOVATIVE rule: "Clutching gear-2 only when Deccelerating.".
    GEARS_YES_MIN[1, :]     = (N_GEARS2 >= n_min_gear2) | \
                                        ((N_GEARS2 <= n_clutch_gear2) & (A <= 0)) | (V <= v_stopped_threshold) # FIXME: move V==0 into own gear.

    ## Revert impossibles to min-gear, n_min & clutched.
    #
    GEARS_BAD = CLUTCH      = (~GEARS_YES_MIN).all(axis=0)
    GEARS_YES_MIN[0, GEARS_BAD]                     = True # Revert to min-gear.
    addDriveabilityProblems(GEARS_BAD, 'g1: Revolutions too low!', driveability_issues)

    GEARS_YES               = (GEARS_YES_MIN & GEARS_YES_MAX)

    return (GEARS_YES, CLUTCH)


def calcPower_required(V, test_mass, f0, f1, f2, f_inertial):
    '''

    @see: Annex 2-3.1, p 71
    '''

    VV      = V * V
    VVV     = VV * V
    A       = np.diff(V)
    A       = np.append(A, 0) # Restore element lost by diff().
    assert  V.shape == VV.shape == VVV.shape == A.shape, _shapes(V, VV, VVV, A)

    P_REQ   = (f0 * V + f1 * VV + f2 * VVV + f_inertial * A * V * test_mass) / 3600.0
    assert  V.shape == P_REQ.shape, _shapes(V, P_REQ)

    return (A, P_REQ)



def calcPower_available(N_GEARS, n_idle, n_rated, p_rated, load_curve, p_safety_margin):
    '''

    @see: Annex 2-3.2, p 72
    '''

    N_NORM          = (N_GEARS - n_idle) / (n_rated - n_idle)
    P_WOT           = np.interp(N_NORM, load_curve[0], load_curve[1], right=0)
    P_AVAIL         = P_WOT * p_rated * p_safety_margin

    return P_AVAIL

def possibleGears_byPower(V, N_GEARS, P_REQ,
                          n_idle, n_rated, p_rated, load_curve, p_safety_margin,
                          driveability_issues):
    '''

    @see: Annex 2-3.1 & 3.3, p 71 & 72
    '''

    P_AVAIL     = calcPower_available(N_GEARS, n_idle, n_rated, p_rated, load_curve, p_safety_margin)
    assert      V.shape == P_REQ.shape and N_GEARS.shape == P_AVAIL.shape, \
                                _shapes(V, P_REQ, N_GEARS, P_AVAIL)

    GEARS_YES   = P_AVAIL >= P_REQ

    GEARS_BAD = (~GEARS_YES).all(axis=0)
    addDriveabilityProblems(GEARS_BAD, 'Insufficient power!', driveability_issues)

    return GEARS_YES


def selectGears(V, GEARS_MX, G_BY_N, G_BY_P, driveability_issues):
    assert                  G_BY_N.shape == G_BY_P.shape, _shapes(V, G_BY_N, G_BY_P)
    assert                  G_BY_N.dtype == G_BY_P.dtype == 'bool', _dtypes(G_BY_N, G_BY_P)

    GEARS_YES               = G_BY_N & G_BY_P
    addDriveabilityProblems((~GEARS_YES).all(axis=0), 'Mismatch power/revs.', driveability_issues)
    GEARS_MX[~GEARS_YES]    = - 1 # FIXME: What to do if no gear foudn for the combination of Power/Revs??
    assert                  G_BY_N.dtype == G_BY_P.dtype == 'bool', _dtypes(G_BY_N, G_BY_P)
    GEARS                   = GEARS_MX.max(axis=0)

    return GEARS




_escape_char = 128

_regex_gears2regex = re.compile(r'\\g(\d+)')

def dec_byte_repl(m):
    return chr(_escape_char + int(m.group(1)))


def gearsregex(gearspattern):
    '''
    @param:  :gearspattern: regular-expression or substitution that escapes decimal-bytes written as: \g\d+
                        with adding +128, eg::
                            \g124|\g7 --> unicode(128+124=252)|unicode(128+7=135)
    '''

    assert          isinstance(gearspattern, str), 'Not str: %s' % gearspattern

    regex           = _regex_gears2regex.sub(dec_byte_repl, gearspattern)
    return          re.compile(bytes(regex, 'latin_1'))


def np2bytes(NUMS):
    assert          all(NUMS >= -1)  and all(NUMS < (256 - _escape_char)), 'Outside byte-range: %s' % NUMS

    return          (NUMS + _escape_char).astype('uint8').tostring()


def bytes2np(bytesarr):
    assert          isinstance(bytesarr, bytes), 'Not bytes: %s' % bytesarr

    return          np.array(list(bytesarr)) - _escape_char


def assert_regexp_unmatched(regex, string, msg):
    assert not re.findall(regex, string), \
            '%s: %s' % (msg, [(m.start(), m.group()) for m in re.finditer(regex, string)])


#=====================
# Driveability rules #
#=====================

def rule_a(bV, GEARS, CLUTCH, driveability_issues, re_zeros):
    """Rule (a): Clutch & set to 1st-gear before accelerating from standstill.

     Implemented with a regex, outside rules-loop:
     Also ensures gear-0 always followed by gear-1.

     NOTE: Rule(A) not inside x2 loop.
    """

    for m in re_zeros.finditer(bV):
        t_accel                 = m.end()
        # Exclude zeros at the end.
        if (t_accel == len(bV)):
            break
        GEARS[t_accel - 1]      = 1
        CLUTCH[t_accel - 1]     = True
        addDriveabilityMessage(t_accel-1, 'g0: Rule(a):   Set g1-clutched from standstill.', driveability_issues)
    assert_regexp_unmatched(b'\x00[^\x00\x01]', GEARS.astype('uint8').tostring(), 'Jumped gears from standstill')


def rule_b1(t, pg, g, V, A, GEARS, driveability_issues):
    """Rule (b1): Do not skip gears while accellerating."""

    if ((pg+1) < g and A[t] > 0):
        pg          = pg+1
        GEARS[t]    = pg
        addDriveabilityMessage(t, 'g%i: Rule(b.1): Do not skip g%i while accellerating.' % (g, pg), driveability_issues)
        return True
    return False


def rule_b2(t, pg, g, V, A, GEARS, driveability_issues):
    """Rule (b2): Hold gears for at least 3sec."""

    # NOTE: rule(b2): Applying it only on non-flats may leave gear for less than 3sec!
    if ((pg != GEARS[t-3:t-1]).any() and (A[t-3:t] != 0).all()):
        GEARS[t]    = pg
        addDriveabilityMessage(t, 'g%i: Rule(b.2): Hold g%i at least 3sec.' % (g, pg), driveability_issues)
        return True
    return False


def rule_c(bV, A, GEARS, CLUTCH, driveability_issues, re_zeros):
    """Rule (c): Idle while deccelerating to standstill.

     Implemented with a regex, outside rules-loop:
     Search for zeros in _reversed_ V & GEAR profiles,
     for as long Accell is negative.
     NOTE: Rule(c) is the last rule to run, outside x2 loop.
    """

    nV          = len(bV)
    for m in re_zeros.finditer(bV[::-1]):
        t_stop  = m.end()
        # Exclude zeros at the end.
        if (t_stop == nV):
            break
        t = nV - t_stop - 1
        while (A[t] < 0):
            addDriveabilityMessage(t, 'g%i: Rule(c):   Set idle while deccelerating to standstill.'%GEARS[t], driveability_issues)
            GEARS[t]   = 0
            CLUTCH[t]  = False
            t -= 1


def rule_d(t, pg, g, V, A, GEARS, driveability_issues):
    """Rule (d): Cancel shifts after peak velocity."""

    if (A[t-2] > 0 and  A[t-1] < 0 and GEARS[t-2] == pg):
        GEARS[t]    = pg
        addDriveabilityMessage(t, 'g%i: Rule(d):   Cancel shift after peak, restore to g%i.' % (g, pg), driveability_issues)
        return True
    return False


def rule_e(t, pg, g, V, A, GEARS, driveability_issues):
    """Rule (e): Cancel shifts lasting 5secs or less."""

    if (pg == g+1): # FIXME: Apply rule(e) also for any initial/final gear (not just for i-1).
        ## Travel back in time for 5secs.
        #
        pt = t-2
        while (pt >= t-5 and GEARS[pt] == pg):
            pt -= 1

        if (GEARS[pt] == g):
            GEARS[pt:t] = g # Overwrites the 1st element, already == g.
            for tt in range(pt+1, t):
                addDriveabilityMessage(tt, 'g%i: Rule(e):   Cancel lone %isec upshift, restore to g%i.' % (pg, t-pt-1, g), driveability_issues)
            return True
    return False


def rule_f(t, pg, g, V, A, GEARS, driveability_issues):
    """Rule(f): Cancel 1sec downshifts (under certain circumstances)."""

    if (pg == g-1 and GEARS[t-2] == g):
        # TODO: Rule(f) implement further constraints.
        # NOTE: Rule(f): What if extra conditions unsatisfied? Allow shifting for 1 sec only??
        GEARS[t-1] = g
        addDriveabilityMessage(t-1, 'g%i: Rule(g):   Cancel 1sec downshift, restore to g%i.' % (pg, g), driveability_issues)
        return True

    return False


def rule_g(t, pg, g, V, A, GEARS, driveability_issues):
    """Rule(g): Cancel upshifts if later downshifted for at least 2sec during accelleration."""

    if (pg == g and (A[t-1:t+1] > 0).all()):
        ## Travel back in time for as long accelerating and same gear.
        #
        pt = t-2
        pg = g+1
        while (GEARS[pt] == pg and A[pt] > 0):
            pt -= 1

        if (pt != t-2):
            GEARS[pt:t-1] = g
            for tt in range(pt, t-1):
                addDriveabilityMessage(tt, 'g%i: Rule(g):   Cancel %isec accelerated upshift later downshifted, restore to g%i.' % (pg, t-1-pt, g), driveability_issues)
            return True

        return False


def applyDriveabilityRules(V, A, GEARS, CLUTCH, ngears, driveability_issues):
    '''
    @note: Modifies GEARS.
    @see: Annex 2-4, p 72
    '''

    ## V --> byte-array to search by regex.
    #
    V                           = V.copy(); V[V > (255 - _escape_char)] = (255 - _escape_char)
    bV                          = np2bytes(V)
    re_zeros                    = gearsregex('\g0+')

    rule_a(bV, GEARS, CLUTCH, driveability_issues, re_zeros)

    rules = [
        rule_b1,
        rule_b2,
        rule_d,
        rule_e,
        rule_f,
        rule_g
    ]
    ## Apply the V-visiting driveability-rules x 2, as by specs.
    #
    for _ in [0, 1]:
        # Apply rules over all cycle-steps.
        #
        pg = 0;                 # previous gear: GEARS[t-1]
        for (t, g) in enumerate(GEARS[5:], 5):
            if (g != pg):       ## All rules triggered by a gear-shift.

                ## Apply the 1st rule to match.
                #
                for rule in rules:
                    if rule(t, pg, g, V, A, GEARS, driveability_issues):
                        break

            pg = GEARS[t]


    rule_c(bV, A, GEARS, CLUTCH, driveability_issues, re_zeros)


def runCycle(V, A, P_REQ, gear_ratios,
                   n_idle, n_min_drive, n_rated,
                   p_rated, load_curve,
                   params):
    '''Calculates gears, clutch and actual-velocity for the cycle (V).
    Initial calculations happen on engine_revs for all gears, for all time-steps of the cycle (N_GEARS array).
    Driveability-rules are applied afterwards on the selected gear-sequence, for all steps.

    @note My interpratation for Gear2 ``n_min``::

                          ___________                   ______________
                             CLUTCH  |////INVALID//////|  GEAR-2-OK
        EngineRevs(N): 0---------------------+---------------------------->
        for Gear-2                   |       |         |
                    n_clutch_gear2 --+       |         +-- n_min_gear2
                    (-10% * n_idle)       N_IDLE           (1.15% * n_idle)        OR
                                                        (n_idle + (3% * n_range))

    @note: modifies V for velocities < v_stopped_threshold
    @param: V: the cycle, the velocity profile
    @param: A: acceleration of the cycle (diff over V)
    @return :array: CLUTCH:    a (1 X #velocity) bool-array, eg. [3, 150] --> gear(3), time(150)
    '''

    ## A multimap to collect problems.
    #
    from collections import defaultdict
    driveability_issues         = defaultdict(list)



    ## Read and calc model parameters.
    #
    n_range                     = (n_rated - n_idle)

    f_n_max                     = params.get('f_n_max', 1.2)
    n_max                       = n_idle + f_n_max * n_range

    if n_min_drive is None:
        f_n_min                 = params.get('f_n_min', 0.125)
        n_min_drive             = n_idle + f_n_min * n_range

    f_n_min_gear2               = params.get('f_n_min_gear2', [1.15, 0.03])
    n_min_gear2                 = max(f_n_min_gear2[0] * n_idle, f_n_min_gear2[1] * n_range + n_idle)

    f_n_clutch_gear2            = params.get('f_n_clutch_gear2', 0.9)
    n_clutch_gear2              = f_n_clutch_gear2 * n_idle

    v_stopped_threshold         = params.get('v_stopped_threshold', 1) # Km/h
    p_safety_margin             = params.get('f_safety_margin', 0.9)


    ## Apply stopped-vehicle threshold (Annex 2-4(a), p72)
    V[V <= v_stopped_threshold] = 0

    (N_GEARS, GEARS_MX)         = calcEngineRevs_required(V, gear_ratios, n_idle)

    (G_BY_N, CLUTCH)            = possibleGears_byEngineRevs(V, A, N_GEARS,
                                                len(gear_ratios), n_idle,
                                                n_min_drive, n_clutch_gear2, n_min_gear2, n_max, v_stopped_threshold,
                                                driveability_issues)

    G_BY_P                      = possibleGears_byPower(V, N_GEARS, P_REQ,
                                                n_idle, n_rated, p_rated, load_curve, p_safety_margin,
                                                driveability_issues)

    GEARS                       = selectGears(V, GEARS_MX, G_BY_N, G_BY_P, driveability_issues)
    assert                      V.shape == GEARS.shape, _shapes(V, GEARS)
    assert                      'i' == GEARS.dtype.kind, GEARS.dtype
    assert                      ((GEARS >= -1) & (GEARS <= len(gear_ratios))).all(), (min(GEARS), max(GEARS))


    CLUTCH[(GEARS == 2) & (N_GEARS[1, :] < n_clutch_gear2)] = True

    applyDriveabilityRules(V, A, GEARS, CLUTCH, len(gear_ratios), driveability_issues)

    ## Calculate real-celocity.
    #
    # TODO: Simplify V_real calc by avoiding multiply all.
    V_REAL                      = (N_GEARS.T / np.array(gear_ratios)).T[GEARS - 1, range(len(V))]
    V_REAL[CLUTCH | (V == 0)]   = 0

    return (V_REAL, GEARS, CLUTCH, driveability_issues)



if __name__ == '__main__':
    pass
