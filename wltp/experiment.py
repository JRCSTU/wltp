#!/usr/bin/env python
#
# Copyright 2013-2014 European Commission (JRC);
# Licensed under the EUPL (the 'Licence');
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at: http://ec.europa.eu/idabc/eupl
'''The core that accepts a vehicle-model and wltc-classes, runs the simulation and updates the model with results (downscaled velocity & gears-profile).

.. Attention:: The documentation of this core module has several issues and needs work.

ALL_CAPITALS variable denote *vectors*, usually over the velocity-profile (the cycle),
for instance, GEARS is like that::

     t:||: 0  1  2  3
    ---+-------------
    g1:|[[ 1, 1, 1, 1, ... 1, 1
    g2:|   2, 2, 2, 2, ... 2, 2
    g3:|   3, 3, 3, 3, ... 3, 3
    g4 |   4, 4, 4, 4, ... 4, 4 ]]


Vectors
-------

V:        floats (#cycle_steps)
    The wltp-class velocity profile.

GEARS:    integers (#gears X #cycle_steps)
    One row for each gear (starting with 1 to #gears).

GEARS_YES:  boolean (#gears X #cycle_steps)
    One row per gear having ``True`` wherever gear is possible for each step.

N_GEARS:  floats (#gears X #cycle_steps)
    One row per gear with the Engine-revolutions required to follow the V-profile (unfeasable revs included),
    produced by multiplying ``V * gear-rations``.

.. Seealso:: :mod:`model` for in/out schemas

:since: 1 Jan 2014

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

    See :mod:`wltp.experiment` for documentation.
    '''


    def __init__(self, *models, skip_model_validation=False, validate_wltc = False):
        """
        ``model`` is a tree (formed by dicts & lists) holding the experiment data.

        ``skip_model_validation`` when true, does not validate the model.
        """

        from wltp.model import wltc_data

        self.dtype = np.float64
        self.set_models(*models, skip_validation=skip_model_validation)
        self.wltc = wltc_data()

        if (validate_wltc):
            self.validateWltc()


    def validateWltc(self, iter_errors=False):
        from .model import wltc_validator

        if iter_errors:
            return wltc_validator().iter_errors(self.wltc)
        else:
            wltc_validator().validate(self.wltc)




    def run(self, overridde_cycle=False):
        '''Invokes the main-calculations and extracts/update Model values!

        @see: Annex 2, p 70
        '''

        model       = self.model
        vehicle     = model['vehicle']

        ## Prepare results
        #
        tabular             = {}
        model['cycle_run']  = tabular

        ## Extract vehicle attributes from model.
        #
        mass                = vehicle['mass']
        p_rated             = vehicle['p_rated']
        n_rated             = vehicle['n_rated']
        n_idle              = vehicle['n_idle']
        n_min_drive         = vehicle['n_min']
        gear_ratios         = vehicle['gear_ratios']
        (f0, f1, f2)        = vehicle['resistance_coeffs']
        params              = model['params']
        v_max               = vehicle['v_max']
        if (v_max is None):
            v_max = n_rated / gear_ratios[-1]


        if (overridde_cycle):
            cycle                   = np.asarray(overridde_cycle)
        else:
            ## Decide WLTC-class.
            #
            class_limits            = self.wltc['classification']['p_to_mass_class_limits']
            class3_velocity_split   = self.wltc['classification']['class3_split_velocity']
            wltc_class              = decideClass(class_limits, class3_velocity_split, mass, p_rated, v_max)
            params['wltc_class']    = wltc_class
            class_data              = self.wltc['classes'][wltc_class]
            cycle                   = np.asarray(class_data['cycle'], dtype=self.dtype)


        ## Velocity-profile
        #
        V                   = np.array(cycle, dtype=self.dtype)
        tabular['v_class']  = V

        ## NOTE: Improved Acceleration calc on central-values with gradient.
        #    The pure_load 2nd-part of the P_REQ from start-to-stop is 0, as it should.
        #
        #A       = np.gradient(V) ## TODO: Enable gradient acceleration-calculation.
        A       = np.diff(V); A = np.append(A, 0) # Restore element lost by diff().
        A       = A / 3.6

        ## Required-Power needed early-on by Downscaling.
        #
        f_inertial          = params.get('f_inertial', 1.1)
        P_REQ               = calcPower_required(V, A, mass, f0, f1, f2, f_inertial)

        if (not overridde_cycle):
            ## Downscale velocity-profile.
            #
            f_downscale_threshold = params.get('f_downscale_threshold', 0.01)
            dsc_data            = class_data['downscale']
            phases              = dsc_data['phases']
            p_max_values        = dsc_data['p_max_values']
            downsc_coeffs       = dsc_data['factor_coeffs']
            dsc_v_split         = dsc_data.get('v_max_split', None)
            f_downscale         = calcDownscaleFactor(P_REQ,
                                                          p_max_values, downsc_coeffs, dsc_v_split,
                                                          p_rated, v_max,
                                                          f_downscale_threshold
            )
            params['f_downscale'] = f_downscale
            if (f_downscale > 0):
                V               = downscaleCycle(V, f_downscale, phases)
            tabular['v_target'] = V


        ## Run cycle to find gears, clutch and real-velocirty.
        #
        load_curve          = vehicle['full_load_curve']
        (V_REAL, GEARS_ORIG, GEARS, CLUTCH, RPM, N_NORM, P_AVAIL, driveability_issues) = \
                            runCycle(V, A, P_REQ,
                                           gear_ratios,
                                           n_idle, n_min_drive, n_rated,
                                           p_rated, load_curve,
                                                       params)
        assert               V.shape == GEARS.shape, _shapes(V, GEARS)

        tabular['v_real']       = V_REAL
        tabular['gears_orig']   = GEARS_ORIG
        tabular['gears']        = GEARS
        tabular['clutch']       = CLUTCH
        tabular['p_available']  = P_AVAIL
        tabular['p_required']   = P_REQ
        tabular['rpm']          = RPM
        tabular['rpm_norm']     = N_NORM
        tabular['driveability'] = driveability_issues


        return model


#######################
##       MODEL       ##
#######################


    def set_models(self, *models, skip_validation=False):
        import functools
        from wltp.model import model_base, merge

        self.model = model_base()
        functools.reduce(merge, [self.model] + list(models))
        if not skip_validation:
            self.validate()


    def validate(self, iter_errors=False):
        from .model import model_validator, validate_full_load_curve

        if iter_errors:
            return model_validator().iter_errors(self.model)
        else:
            model_validator().validate(self.model)

        validate_full_load_curve(self.model['vehicle']['full_load_curve'], self.model['params']['f_n_max'])

    def driveability_report(self):
        cycle = self.model.get('cycle_run')
        if (not cycle is None):
            issues = []
            drv = cycle['driveability']
            pt = -1
            for t in drv.nonzero()[0]:
                if (pt+1 < t):
                    issues += ['...']
                issues += ['{:>4}: {}'.format(t, drv[t])]
                pt = t

            return '\n'.join(issues)
        return None





#######################
## PURE CALCULATIONS ##
##  Separate for     ##
##     testability!  ##
#######################


def addDriveabilityMessage(time_step, msg, driveability_issues):
    old = driveability_issues[time_step]
    driveability_issues[time_step] = old + msg


def addDriveabilityProblems(GEARS_BAD, reason, driveability_issues):
    failed_steps = GEARS_BAD.nonzero()[0]
    if (failed_steps.size != 0):
        log.info('%i %s: %s', failed_steps.size, reason, failed_steps)
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



def calcDownscaleFactor(P_REQ, p_max_values, downsc_coeffs, dsc_v_split, p_rated, v_max, f_downscale_threshold):
    '''Check if downscaling required, and apply it.

    :return: (float) the factor

    @see: Annex 1-7, p 68
    '''

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
            if (f_downscale <= f_downscale_threshold):
                f_downscale = 0


    return f_downscale


def downscaleCycle(V, f_downscale, phases):
    '''Downscale just by scaling the 2 phases demarked by the 3 time-points with different factors,
    no recursion as implied by the specs.

    @see: Annex 1-7, p 64-68
    '''
    (t0, t1, t2)    = phases

    ## Accelaration phase
    #
    ix_acc          = np.arange(t0, t1 + 1)
    offset_acc      = V[t0]
    acc_scaled      = (1 - f_downscale) * (V[ix_acc] - offset_acc) + offset_acc
    assert          acc_scaled[0] == V[t0], ('smooth-start: ', acc_scaled[0],  V[t0])

    ## Decelaration phase
    #
    ix_dec          = np.arange(t1 + 1, t2 + 1)
    offset_dec      = V[t2]
    f_corr          = (acc_scaled[-1] - offset_dec) / (V[t1] - offset_dec)
    dec_scaled      = f_corr * (V[ix_dec] - offset_dec) + offset_dec
    assert          dec_scaled[-1] == V[t2], ('smooth-finish: ', dec_scaled[-1],  V[t2])

    scaled          = np.hstack((acc_scaled, dec_scaled))
    assert          (1 - f_downscale) * abs(scaled[t1 - t0] - scaled[t1 - t0 + 1]) <= abs(V[t1] - V[t1 + 1]), \
                                    ('smooth-tip: ', scaled[t1 - t0], scaled[t1 - t0 + 1], V[t1], V[t1 + 1])

    V_DSC           = np.hstack((V[:t0], scaled, V[t2 + 1:]))
    assert          V.shape == V_DSC.shape, _shapes(V, V_DSC)

    return V_DSC


def calcEngineRevs_required(V, gear_ratios, n_idle, v_stopped_threshold):
    '''Calculates the required engine-revolutions to achieve target-velocity for all gears.

    :return: array: N_GEARS:   a (#gears X #velocity) float-array, eg. [3, 150] --> gear(3), time(150)
    :rtype: array: GEARS:     a (#gears X #velocity) int-array, eg. [3, 150] --> gear(3), time(150)

    @see: Annex 2-3.2, p 71
    '''

    assert              V.ndim == 1 and len(V) > 100, (V.shape, gear_ratios, n_idle)

    nG                  = len(gear_ratios)
    nV                  = len(V)

    GEARS               = np.tile(np.arange(0, nG, dtype='int8')+ 1, (nV, 1)).T
    assert              GEARS.shape == (nG, nV), (GEARS.shape, gear_ratios, nV)

    GEAR_RATIOS         = np.tile(gear_ratios, (nV, 1)).T       ## TODO: Prepend row for idle-gear in N_GEARS
    N_GEARS             = np.tile(V, (nG, 1)) * GEAR_RATIOS
    assert              GEARS.shape  == GEAR_RATIOS.shape == N_GEARS.shape, _shapes(GEARS, GEAR_RATIOS, N_GEARS, V)

    stopped_steps                       = (V == 0)              ## (Annex 2-3.2 & Annex 2-4(a), p72)
    N_GEARS [:, stopped_steps]          = n_idle
    GEARS   [:, stopped_steps]          = 0

    return (N_GEARS, GEARS)


def possibleGears_byEngineRevs(V, A, N_GEARS,
                               ngears, n_idle,
                               n_min_drive, n_clutch_gear2, n_min_gear2, n_max,
                               v_stopped_threshold,
                               driveability_issues):
    '''
    Calculates the engine-revolutions limits for all gears and returns for which they are accepted.

    My interpratation for Gear2 ``n_min`` limit::

                              _____________                ______________
                          ///INVALID///|   CLUTCHED   |  GEAR-2-OK
        EngineRevs(N): 0-----------------------+---------------------------->
        for Gear-2                     |       |      +--> n_clutch_gear2   := n_idle + MAX(
                                       |       |                                      0.15% * n_idle,
                                       |       |                                      3%    * n_range)
                                       |       +---------> n_idle
                                       +-----------------> n_min_gear2      := 90% * n_idle


    :return: GEARS_YES: possibibilty for all the gears on each cycle-step
            (eg: [0, 10] == True --> gear(1) is possible for t=10)
    :rtype: list(booleans, nGears x CycleSteps)

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
    GEARS_YES_MIN[0, :]     = (N_GEARS[0, :] >= n_idle) | (V <= v_stopped_threshold) # FIXME: move V==0 into own gear.

    ## NOTE: "interpratation" of specs for Gear-2
    #        and FIXME: NOVATIVE rule: "Clutching gear-2 only when Decelerating.".
    N_GEARS2                = N_GEARS[1, :]
    GEARS_YES_MIN[1, :]     = ((N_GEARS2 >= n_min_gear2) & (A <= 0)) | ((N_GEARS2 >= n_min_gear2) & (A > 0))

    ## Revert impossibles to min-gear, n_min & clutched.
    #
    GEARS_BAD = CLUTCH      = (~GEARS_YES_MIN).all(axis=0) ## TODO: Clutch on gear2 (f=will be fixed when add also CLUTCH_GEARS)
    GEARS_YES_MIN[0, GEARS_BAD]                     = True # Revert to min-gear.
    addDriveabilityProblems(GEARS_BAD, 'g1: Revolutions too low!', driveability_issues)

    GEARS_YES               = (GEARS_YES_MIN & GEARS_YES_MAX)

    return (GEARS_YES, CLUTCH)


def calcPower_required(V, A, test_mass, f0, f1, f2, f_inertial):
    '''

    @see: Annex 2-3.1, p 71
    '''

    VV      = V * V
    VVV     = VV * V
    assert  V.shape == VV.shape == VVV.shape == A.shape, _shapes(V, VV, VVV, A)

    P_REQ   = (f0 * V + f1 * VV + f2 * VVV + f_inertial * A * V * test_mass) / 3600.0
    assert  V.shape == P_REQ.shape, _shapes(V, P_REQ)

    return P_REQ



def calcPower_available(N_GEARS, n_idle, n_rated, p_rated, load_curve, p_safety_margin):
    '''

    @see: Annex 2-3.2, p 72
    '''

    N_NORMS         = (N_GEARS - n_idle) / (n_rated - n_idle)
    P_WOTS          = np.interp(N_NORMS, load_curve[0], load_curve[1]) # When outside of load_curve, accept max-min gear.
#     from scipy.interpolate import interp1d
#     intrerp_f       = interp1d(load_curve[0], load_curve[1], kind='linear', bounds_error=False, fill_value=0, copy=False)
#     P_WOT           = intrerp_f(N_NORMS)
    P_AVAILS        = P_WOTS * p_rated * p_safety_margin

    return (P_AVAILS, N_NORMS)

def possibleGears_byPower(N_GEARS, P_REQ,
                          n_idle, n_rated, p_rated, load_curve, p_safety_margin,
                          driveability_issues):
    '''

    @see: Annex 2-3.1 & 3.3, p 71 & 72
    '''

    (P_AVAIL, N_NORMS)      = calcPower_available(N_GEARS, n_idle, n_rated, p_rated, load_curve, p_safety_margin)
    assert      N_GEARS.shape == P_AVAIL.shape, \
                                _shapes(P_REQ, N_GEARS, P_AVAIL)

    GEARS_YES   = P_AVAIL >= P_REQ

    GEARS_BAD = (~GEARS_YES).all(axis=0)
    addDriveabilityProblems(GEARS_BAD, 'Insufficient power!', driveability_issues)

    return (GEARS_YES, P_AVAIL, N_NORMS)

def selectGears(GEARS_MX, G_BY_N, G_BY_P, driveability_issues):
    assert                  G_BY_N.shape == G_BY_P.shape, _shapes(G_BY_N, G_BY_P)
    assert                  G_BY_N.dtype == G_BY_P.dtype == 'bool', _dtypes(G_BY_N, G_BY_P)

    GEARS_YES               = G_BY_N & G_BY_P
    GEARS_MX[~GEARS_YES]    = -1                ## NOTE: Invalid gears will be smoothed-away in extra_rule(1).
    assert                  G_BY_N.dtype == G_BY_P.dtype == 'bool', _dtypes(G_BY_N, G_BY_P)
    GEARS                   = GEARS_MX.max(axis=0)

    return GEARS




_escape_char = 128

_regex_gears2regex = re.compile(r'\\g(\d+)')

def dec_byte_repl(m):
    return chr(_escape_char + int(m.group(1)))


def gearsregex(gearspattern):
    '''
    :param gearspattern: regular-expression or substitution that escapes decimal-bytes written as: ``\g\d+``
                        with adding +128, eg::

                            \g124|\g7 --> unicode(128+124=252)|unicode(128+7=135)
    '''

    assert          isinstance(gearspattern, str), 'Not str: %s' % gearspattern

    regex           = _regex_gears2regex.sub(dec_byte_repl, gearspattern)
    return          re.compile(bytes(regex, 'latin_1'))


def np2bytes(NUMS):
    if (NUMS < -1).any() or (NUMS >= (256 - _escape_char)).any():
        assert          all(NUMS >= -1)  and all(NUMS < (256 - _escape_char)), 'Outside byte-range: %s' % NUMS[(NUMS < -1) | (NUMS >= (256 - _escape_char))]

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

def rule_checkSingletons(bV, GEARS, CLUTCH, driveability_issues, re_zeros):
    re_singletons = gearsregex('(\g0)')

def rule_a(bV, GEARS, CLUTCH, driveability_issues, re_zeros):
    """Rule (a): Clutch & set to 1st-gear before accelerating from standstill.

     Implemented with a regex, outside rules-loop:
     Also ensures gear-0 always followed by gear-1.

     NOTE: Rule(A) not inside x2 loop, and last to run.
    """

    for m in re_zeros.finditer(bV):
        t_accel                 = m.end()
        # Exclude zeros at the end.
        if (t_accel == len(bV)):
            break
        GEARS[t_accel - 1:t_accel]          = 1
        CLUTCH[t_accel - 1:t_accel - 2]     = True
        addDriveabilityMessage(t_accel-1, '(a: X-->0)', driveability_issues)
    assert_regexp_unmatched(b'\x00[^\x00\x01]', GEARS.astype('uint8').tostring(), 'Jumped gears from standstill')


def step_rule_b1(t, pg, g, V, A, GEARS, driveability_issues):
    """Rule (b1): Do not skip gears while accelerating."""

    if ((pg+1) < g and A[t-1] > 0):
        pg          = pg+1
        GEARS[t]    = pg
        addDriveabilityMessage(t, '(b1: %i-->%i)' % (g, pg), driveability_issues)
        return True
    return False


def step_rule_b2(t, pg, g, V, A, GEARS, driveability_issues):
    """Rule (b2): Hold gears for at least 3sec when accelerating."""

    if ((pg != GEARS[t-3:t-1]).any()):  # A[t-1] > 0):  NOTE: Not checking Accel on the final step of rule(b2)!
        #assert g > pg, 'Rule e & g missed downshift(%i: %i-->%i) in acceleration!'%(t, pg, g)
        if (g < pg):
            addDriveabilityMessage(t, 'Rule e or g missed downshift(%i: %i-->%i) in acceleration?'%(t, pg, g), driveability_issues)
        hold = False
        if (pg == GEARS[t-2] and (A[t-3:t-1] > 0).all()):
            hold = True; n = 2
        elif  (A[t-2] > 0):
            hold = True; n = 1
        if (hold):
            GEARS[t]        = pg
            addDriveabilityMessage(t, '(b2(%i): %i-->%i)' % (n, g, pg), driveability_issues)

            return True
    return False


def step_rule_c1(t, pg, g, V, A, GEARS, driveability_issues):
    """Rule (c1): Skip gears <3sec when decelerating. """

    if ((pg != GEARS[t-3:t-1]).any() and (A[t-2:t] < 0).all()):
        pt = t - 2
        while (pt >= t-3 and GEARS[pt] == pg):
            pt -= 1

        ## Skip even further...
        #
        if (GEARS[t+1] < g):
            t += 1
            g = GEARS[t]

        GEARS[pt+1:t] = g
        for tt in range(pt+1, t):
            addDriveabilityMessage(tt, '(c1: %i-->%i)' % (pg, g), driveability_issues)
        return True
    return False


def rule_c2(bV, A, GEARS, CLUTCH, driveability_issues, re_zeros):
    """Rule (c2): Skip 1st-gear while decelerating to standstill.

     Implemented with a regex, outside rules-loop:
     Search for zeros in _reversed_ V & GEAR profiles,
     for as long Accel is negative.
     NOTE: Rule(c2) is the last rule to run.
    """

    nV          = len(bV)
    for m in re_zeros.finditer(bV[::-1]):
        t_stop  = m.end()
        # Exclude zeros at the end.
        if (t_stop == nV):
            break
        t = nV - t_stop - 1
        while (A[t] < 0 and GEARS[t] == 1):
            addDriveabilityMessage(t, '(c2: %i-->0)'% GEARS[t], driveability_issues)
            GEARS[t]   = 0
            CLUTCH[t]  = False
            t -= 1


def step_rule_d(t, pg, g, V, A, GEARS, driveability_issues):
    """Rule (d): Cancel shifts after peak velocity."""

    if (A[t-2] > 0 and  A[t-1] < 0 and GEARS[t-2] == pg):
        GEARS[t]    = pg
        addDriveabilityMessage(t, '(d: %i-->%i)' % (g, pg), driveability_issues)
        return True
    return False


def step_rule_e(t, pg, g, V, A, GEARS, driveability_issues):
    """Rule (e): Cancel shifts lasting 5secs or less."""

    if (pg > g):
        ## Travel back in time for 5secs.
        #
        pt = t-2
        while (pt >= t-5 and GEARS[pt] == pg):
            pt -= 1

        if (GEARS[pt] < pg): # NOTE: Apply rule(e) also for any LOWER initial/final gears (not just for i-1).
            GEARS[pt+1:t] = g
            for tt in range(pt+1, t):
                addDriveabilityMessage(tt, '(e: %i-->%i)' % (pg, g), driveability_issues)
            return True
    return False


def step_rule_f(t, pg, g, V, A, GEARS, driveability_issues):
    """Rule(f): Cancel 1sec downshifts (under certain circumstances)."""

    if (pg < g and GEARS[t-2] >= g):
        # NOTE: Nowhere to apply it since rule(b2) would have eliminated 1-sec shifts.  Moved before rule(b)!
        # NOTE: Applying rule(f) also for i-2, i-3, ... signular-downshifts.
        # FIXME: Rule(f) implement further constraints.
        # NOTE: Rule(f): What if extra conditions unsatisfied? Allow shifting for 1 sec only??
        GEARS[t-1] = min(g, GEARS[t-2])
        addDriveabilityMessage(t-1, '(f: %i-->%i)' % (pg, g), driveability_issues)
        return True

    return False


def step_rule_g(t, pg, g, V, A, GEARS, driveability_issues):
    """Rule(g): Cancel upshift during acceleration if later downshifted for at least 2sec."""

    if (pg > g and (GEARS[t:t+2] == g).all() and (A[t-1:t+2] > 0).all()):
        ## Travel back in time for as long accelerating and same gear.
        #
        pt = t-2
        while (GEARS[pt] == pg and A[pt] > 0):
            pt -= 1

        GEARS[pt+1:t] = g
        for tt in range(pt+1, t):
            addDriveabilityMessage(tt, '(g: %i-->%i)' % (pg, g), driveability_issues)
        return True

    return False


def applyDriveabilityRules(V, A, GEARS, CLUTCH, ngears, driveability_issues):
    '''
    @note: Modifies GEARS.
    @see: Annex 2-4, p 72
    '''

    def apply_step_rules(rules, isStopOnFirstApplied):
        for t in t_range:
            if (GEARS[t-1] != GEARS[t]):       ## All rules triggered by a gear-shift.
                for rule in rules:
                        if (rule(t, GEARS[t-1], GEARS[t], V, A, GEARS, driveability_issues) and \
                                            (isStopOnFirstApplied or GEARS[t-1] == GEARS[t])):
                            break

    ## V --> byte-array to search by regex.
    #
    V                           = V.copy(); V[V > (255 - _escape_char)] = (255 - _escape_char)
    bV                          = np2bytes(V)
    re_zeros                    = gearsregex('\g0+')

    ## NOTE: Extra_rule(1): Smooth-away INVALID-GEARS.
    #
    for t in range(2, len(GEARS)):      # Start from 2nd element to accomodate rule(e)'s backtracking.
        if (GEARS[t] < 0):
            GEARS[t] = GEARS[t-1]

    ## Loop X 2 driveability-rules.
    #
    t_range = range(5, len(GEARS))      # Start from 5th element to accomodate rule(e)'s backtracking.
    for _ in [0, 1]:
        apply_step_rules([step_rule_g, step_rule_f], False)                   # NOTE: Rule-order and first-to-apply flag unimportant.
        apply_step_rules([step_rule_e, step_rule_b1, step_rule_b2], False)    # NOTE: Rule-order for b1 &b2 unimportant.
        apply_step_rules([step_rule_c1], False)

        rule_c2(bV, A, GEARS, CLUTCH, driveability_issues, re_zeros)

    rule_a(bV, GEARS, CLUTCH, driveability_issues, re_zeros)


def runCycle(V, A, P_REQ, gear_ratios,
                   n_idle, n_min_drive, n_rated,
                   p_rated, load_curve,
                   params):
    '''Calculates gears, clutch and actual-velocity for the cycle (V).
    Initial calculations happen on engine_revs for all gears, for all time-steps of the cycle (N_GEARS array).
    Driveability-rules are applied afterwards on the selected gear-sequence, for all steps.

    :param V: the cycle, the velocity profile
    :param A: acceleration of the cycle (diff over V) in m/sec^2
    :return: CLUTCH:    a (1 X #velocity) bool-array, eg. [3, 150] --> gear(3), time(150)

    :rtype: array
    '''

    ## A multimap to collect problems.
    #
    driveability_issues         = np.empty_like(V, dtype='object')
    driveability_issues[:]      = ''



    ## Read and calc model parameters.
    #
    n_range                     = (n_rated - n_idle)

    f_n_max                     = params.get('f_n_max', 1.2)
    n_max                       = n_idle + f_n_max * n_range

    if n_min_drive is None:
        f_n_min                 = params.get('f_n_min', 0.125)
        n_min_drive             = n_idle + f_n_min * n_range

    f_n_min_gear2               = params.get('f_n_min_gear2', 0.9)
    n_min_gear2                 = f_n_min_gear2 * n_idle

    f_n_clutch_gear2            = params.get('f_n_clutch_gear2', [1.15, 0.03])
    n_clutch_gear2              = max(f_n_clutch_gear2[0] * n_idle, f_n_clutch_gear2[1] * n_range + n_idle)

    p_safety_margin             = params.get('f_safety_margin', 0.9)
    v_stopped_threshold         = params.get('v_stopped_threshold', 1) # Km/h


    (N_GEARS, GEARS_MX)         = calcEngineRevs_required(V, gear_ratios, n_idle, v_stopped_threshold)

    (G_BY_N, CLUTCH)            = possibleGears_byEngineRevs(V, A, N_GEARS,
                                                len(gear_ratios), n_idle,
                                                n_min_drive, n_clutch_gear2, n_min_gear2, n_max,
                                                v_stopped_threshold,
                                                driveability_issues)

    (G_BY_P, P_AVAILS, N_NORMS) = possibleGears_byPower(N_GEARS, P_REQ,
                                                n_idle, n_rated, p_rated, load_curve, p_safety_margin,
                                                driveability_issues)

    GEARS                       = selectGears(GEARS_MX, G_BY_N, G_BY_P, driveability_issues)
    assert                      V.shape == GEARS.shape, _shapes(V, GEARS)
    assert                      'i' == GEARS.dtype.kind, GEARS.dtype
    assert                      ((GEARS >= -1) & (GEARS <= len(gear_ratios))).all(), (min(GEARS), max(GEARS))
    GEARS_ORIG                  = GEARS.copy()

    CLUTCH[(GEARS == 2) & (N_GEARS[1, :] < n_clutch_gear2)] = True

    applyDriveabilityRules(V, A, GEARS, CLUTCH, len(gear_ratios), driveability_issues)

    P_AVAIL                     = P_AVAILS[GEARS - 1, range(len(V))]
    N_NORM                      = N_NORMS[GEARS - 1, range(len(V))]
    RPM                         = N_GEARS[GEARS - 1, range(len(V))]

    ## Calculate real-celocity.
    #
    # TODO: Simplify V_real calc by avoiding multiply all.
    V_REAL                      = (N_GEARS.T / np.asarray(gear_ratios)).T[GEARS - 1, range(len(V))]

    return (V_REAL, GEARS_ORIG, GEARS, CLUTCH, RPM, N_NORM, P_AVAIL, driveability_issues)



if __name__ == '__main__':
    pass
