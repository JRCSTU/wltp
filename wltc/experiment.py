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

    import wltc

    model = wltc.Model({
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

    experiment = wltc.Experiment(model)
    experiment.run()
    json.dumps(model['results'])



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


def reportDriveabilityProblems(GEARS_YES, reason, driveability_issues):
    failed_gears = (~GEARS_YES).all(0)
    if (failed_gears.any()):
        failed_steps = failed_gears.nonzero()[0]
        for step in failed_steps:
            driveability_issues[step].append(reason)
        log.warning('%i %s issues: %s', failed_steps.size, reason, failed_steps)



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

    GEAR_RATIOS         = np.tile(gear_ratios, (nV, 1)).T
    N_GEARS             = np.tile(V, (nG, 1)) * GEAR_RATIOS
    assert              GEARS.shape  == GEAR_RATIOS.shape == N_GEARS.shape, _shapes(GEARS, GEAR_RATIOS, N_GEARS, V)

    stopped_steps                       = (V == 0)
    N_GEARS [:, stopped_steps]          = n_idle
    GEARS   [:, stopped_steps]          = 0

    return (N_GEARS, GEARS)


def possibleGears_byEngineRevs(V, A, N_GEARS, ngears,
                               n_idle,
                               n_min_drive, n_clutch_gear2, n_min_gear2, n_max,
                               driveability_issues):
    '''Calculates the engine-revolutions limits for all gears and returns where they are accepted.

    @return :list: min-revs for each gear (list[0] --> gear-1)
    @return :list: max-revs for each gear (list[0] --> gear-1)
    @see: Annex 2-3.2, p 71
    '''

    GEARS_YES_MAX           = (N_GEARS <= n_max)

    ## Apply n_min_drive for all gears but 1 & 2
    #
    GEARS_YES_MIN           = (N_GEARS >= n_min_drive)
    GEARS_YES_MIN[0, :]     = (N_GEARS[0, :] >= n_idle) | (V == 0) # V == 0 --> neutral # FIXME: del V==0
    N_GEARS2                = N_GEARS[1, :]
    ## NOTE: "interpratation" of specs for Gear-2
    #        and FIXME: NOVATIVE rule: "Clutching gear-2 only when Deccelerating.".
    GEARS_YES_MIN[1, :]     = (N_GEARS2 >= n_min_gear2) | \
                                        ((N_GEARS2 <= n_clutch_gear2) & (A <= 0)) | (V == 0) # FIXME: del V==0

    reportDriveabilityProblems(GEARS_YES_MIN, 'low revolutions', driveability_issues)
    reportDriveabilityProblems(GEARS_YES_MAX, 'high revolutions', driveability_issues)

    GEARS_YES               = (GEARS_YES_MIN & GEARS_YES_MAX)

    return GEARS_YES


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
    P_WOT           = np.interp(N_NORM, load_curve[0], load_curve[1])
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

    reportDriveabilityProblems(GEARS_YES, 'power', driveability_issues)

    return GEARS_YES




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


def assert_regex_unmatched(regex, string, msg):
    assert not regex.findall(string), \
            '%s: %s' % (msg, [(m.start(), m.group()) for m in regex.finditer(string)])

def assert_regexp_unmatched(regex, string, msg):
    assert not re.findall(regex, string), \
            '%s: %s' % (msg, [(m.start(), m.group()) for m in re.finditer(regex, string)])


def applyDriveabilityRules(V, GEARS, CLUTCH, ngears):
    '''
    @note: Modifies GEARS.
    @see: Annex 2-4, p 72
    '''

    ## Rule (a):
    #    "Clutch & set to 1st-gear before accelerating from standstill."
    #
    # Also ensures gear-0 always followed by gear-1.
    #
    V                           = V.copy(); V[V > (255 - _escape_char)] = (255 - _escape_char)
    bV                          = np2bytes(V)
    re_standstill               = gearsregex('\g0+')
    for m in re_standstill.finditer(bV):
        t_accel                 = m.end()
        GEARS[t_accel - 1]      = 1
        CLUTCH[t_accel - 1]     = True

    assert_regexp_unmatched(b'\x00[^\x00\x01]', GEARS.astype('uint8').tostring(), 'Jumped gears from standstill')

    ## Apply driveability-rules twice, as by specs.
    #
    for _ in [0, 1]:
        pg                      = 0; # previous gear: GEARS[t-1]
        for (t, g) in enumerate(GEARS[5:], 5):
            if (g != pg):

                ## Rule (b.2):
                #    "Gears remain for at least 3 sec."
                #
                if (any(pg != GEARS[t-3:t-1])):
                    GEARS[t]        = pg
                    log.info('Rule-b.2:   t%i(g%i): hold g%i', t, g, pg)

                ## Rule (b.1):
                #    "Gears not skipped during accelleration."
                #
                elif ((pg+1) < g):
                    pg              = pg+1
                    GEARS[t]        = pg
                    log.info('Rule-b.1:   t%i(%i): unskip %i', t, g, pg)

                ## Rule (d):
                #    "No up-shift after peak speed."
                #
                elif (pg < g and pg == GEARS[t-2] and V[t-2] < V[t-1] > V[t] ):
                    GEARS[t]        = pg
                    log.info('Rule-d:     t%i(%i): de-upshift after peak %i', t, g, pg)

                ## Rule (e):
                #    "No less-than 6-secs in up-shift."
                #
                elif (pg > g and any(g == GEARS[t-6:t])):
                    pg              = g
                    GEARS[t-6:t]    = pg
                    log.info('Rule-e:     t%i(%i): de-upshift when <6sec %i', t, g, pg)

                else:
                    pg              = g


    sGEARS                  = GEARS.astype('uint8').tostring()
    assert_regexp_unmatched(b'\x00[^\x00\x01]', sGEARS, 'Jumped gears from standstill')


def selectGears(V, GEARS_MX, G_BY_N, G_BY_P):
    assert                  G_BY_N.shape == G_BY_P.shape, _shapes(V, G_BY_N, G_BY_P)
    assert                  G_BY_N.dtype == G_BY_P.dtype == 'bool', _dtypes(G_BY_N, G_BY_P)

    GEARS_YES               = G_BY_N & G_BY_P
    GEARS_MX[~GEARS_YES]    = -1
    GEARS                   = GEARS_MX.max(axis=0)

    return GEARS


def runCycle(V, A, P_REQ, gear_ratios,
                   n_idle, n_min_drive, n_rated,
                   p_rated, load_curve,
                   params):
    '''

    @note My interpratation for Gear2 ``n_min`` implementd in possibleGears_byEngineRevs()::

                          ___________                   ______________
                             CLUTCH  |////INVALID//////|  GEAR-2-OK
        EngineRevs(N): 0---------------------+---------------------------->
        for Gear-2                   |       |         |
                    n_clutch_gear2 --+       |         +-- n_min_gear2
                    (-10% * n_idle)       N_IDLE           (1.15% * n_idle)        OR
                                                        (n_idle + (3% * n_range))

    @note: modifies V for velocities < v_stopped_threshold
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

    G_BY_N                      = possibleGears_byEngineRevs(V, A, N_GEARS,
                                                len(gear_ratios),
                                                n_idle,
                                                n_min_drive, n_clutch_gear2, n_min_gear2, n_max,
                                                driveability_issues)

    G_BY_P                      = possibleGears_byPower(V, N_GEARS, P_REQ,
                                                n_idle, n_rated, p_rated, load_curve, p_safety_margin,
                                                driveability_issues)

    GEARS                       = selectGears(V, GEARS_MX, G_BY_N, G_BY_P)
    assert                      V.shape == GEARS.shape, _shapes(V, GEARS)
    assert                      'i' == GEARS.dtype.kind, GEARS.dtype
    assert                      all((GEARS >= -1) & (GEARS <= len(gear_ratios))), (min(GEARS), max(GEARS))


    CLUTCH                      = (GEARS == 2) & (N_GEARS[1, :] < n_clutch_gear2)

    applyDriveabilityRules(V, GEARS, CLUTCH, len(gear_ratios))

    ## TODO: Calculate real-celocity.
    #
    N                         = N_GEARS[GEARS - 1, range(len(V))]
    V_REAL = N
    V_REAL[CLUTCH | (V == 0)]   = 0

    return (V_REAL, GEARS, CLUTCH, driveability_issues)



if __name__ == '__main__':
    pass
