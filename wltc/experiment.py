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

'''wltc.experiment module: The actual WLTC gear-shift calculator which consumes a Model and the WLTC-data,
and updates the Model with the results (gears, downscaled velocity-profile) .

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

    model = wltc.Model(json.loads(\'''{
        vehicle": {
            "mass":1300,
            "p_rated":110.625,
            "n_rated":5450,
            "n_idle":950,
            "n_min":500,
            "gear_ratios":[120.5, 75, 50, 43, 33, 28],
            "resistance_coeffs":[100, 0.5, 0.04]
        }
    }\'''))

    experiment = wltc.Experiment(model)
    experiment.run()
    json.dumps(model['results'])



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
        p_rated             = vehicle['p_rated']
        n_rated             = vehicle['n_rated']
        n_idle              = vehicle['n_idle']
        gear_ratios         = vehicle['gear_ratios']
        (f0, f1, f2)        = vehicle['resistance_coeffs']

        ## FIXME: Is v_max correct??.
        # TODO: Store them back into the model?
        v_max               = n_rated / gear_ratios[-1] # FIXME: is v_max ok???


        ## Decide WLTC-class.
        #
        class_limits            = self.wltc['parameters']['p_to_mass_class_limits']
        class3_velocity_split   = self.wltc['parameters']['class3_split_velocity']
        wltc_class              = decideClass(class_limits, class3_velocity_split, mass, p_rated, v_max)
        results['wltc_class']   = wltc_class
        class_data              = self.wltc['cycles'][wltc_class]
        cycle                   = class_data['cycle']


        ## Velocity and power profile.
        #
        V                   = np.array(cycle, dtype=self.dtype)
        P_REQ               = calcPower_required(V, mass, f0, f1, f2)


        ## Downscale velocity-profile.
        #
        dsc_data            = class_data['downscale']
        phases              = dsc_data['phases']
        max_p_values        = dsc_data['max_p_values']
        downsc_coeffs       = dsc_data['factor_coeffs']
        dsc_v_split         = dsc_data['v_max_split'] if 'v_max_split' in dsc_data else None
        downscale_factor    = calcDownscaleFactor(cycle, P_REQ,
                                                      max_p_values, downsc_coeffs, dsc_v_split,
                                                      p_rated, v_max)
        results['downscale_factor'] = downscale_factor
        if (downscale_factor > 0):
            V               = downscaleCycle(cycle, V, downscale_factor, phases)
        results['target']   = V


        ## Calc possible gears.
        #
        v_stopped_threshold = self.wltc['parameters']['v_stopped_threshold'] # Km/h
        p_safety_margin     = self.wltc['parameters']['power_safety_margin']
        load_curve          = vehicle['full_load_curve']
        (GEARS, CLUTCH, driveability_issues)    = calcCycleGears(V, P_REQ,
                                                           mass, f0, f1, f2, gear_ratios,
                                                           n_idle, n_rated,
                                                           p_rated, load_curve,
                                                           v_stopped_threshold, p_safety_margin)
        assert               V.shape == GEARS.shape, _shapes(V, GEARS)
        results['gears']     = GEARS
        results['clutch']    = CLUTCH
        results['driveability_issues']    = driveability_issues



        np.set_printoptions(edgeitems=16)
        #print(driveability_issues)
        #print(v_max)
        #results['target'] = []; print(results)




#######################
## PURE CALCULATIONS ##
#######################


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



def calcDownscaleFactor(cycle, P_REQ, max_p_values, downsc_coeffs, dsc_v_split, p_rated, v_max):
    '''Check if downscaling required, and apply it.

    @return: :float:
    @see: Annex 1-7, p 68
    '''
    downscale_threshold     = 0.1 # Move downscale_threshold to model

    ## Max required power
    #
    p_req_max               = P_REQ[max_p_values[0]]
    r_max                   = (p_req_max / p_rated)

    ## Cycle r0
    #
    if dsc_v_split is not None:
        assert              len(downsc_coeffs) == 2, downsc_coeffs

        downsc_coeffs       = downsc_coeffs[0] if (v_max <= dsc_v_split) else downsc_coeffs[1]

    (r0, a1, b1) = downsc_coeffs


    if (r_max < r0):
        downscale_factor    = 0
    else:
        downscale_factor    = a1 * r_max + b1
        downscale_factor    = round(downscale_factor, 1)
        if (downscale_factor <= downscale_threshold):
            downscale_factor = 0


    return downscale_factor


def downscaleCycle(cycle, V, downscale_factor, phases):
    '''Check if downscaling required, and apply it.

    @see: Annex 1-7, p 64-68
    '''
    #TODO: Implement downscale.

    raise Exception('Downscaling needed, but NOT IMPLEMENTED YET!')



def calcEngineRevs_required(V, gear_ratios, n_idle, n_rated, n_min_gear2):
    '''Calculates the required engine-revolutions to achieve target-velocity for all gears.

    @return :array: N_GEARS:   a (#gears X #velocity) float-array, eg. [3, 150] --> gear(3), time(150)
    @return :array: GEARS:     a (#gears X #velocity) int-array, eg. [3, 150] --> gear(3), time(150)
    @see: Annex 2-3.2, p 71
    '''

    assert              V.ndim == 1, (V.shape, gear_ratios)

    nG                  = len(gear_ratios)
    nV                  = len(V)

    GEARS               = np.tile(np.arange(0, nG, dtype='int8')+ 1, (nV, 1)).T
    assert              GEARS.shape == (nG, nV), (GEARS.shape, gear_ratios, nV)

    GEAR_RATIOS         = np.tile(gear_ratios, (nV, 1)).T
    N_GEARS             = np.tile(V, (nG, 1))
    N_GEARS             = N_GEARS * GEAR_RATIOS
    assert              GEARS.shape  == GEAR_RATIOS.shape == N_GEARS.shape, _shapes(GEARS, GEAR_RATIOS, N_GEARS, V)

    ## FIXME: "incomprehensible" specs for Gear-2.
    #
    clutched_on_gear2   = (N_GEARS[1, :] < n_min_gear2)
    N_GEARS[1, clutched_on_gear2]       = n_idle

    stopped_steps                       = (V == 0)
    N_GEARS [:, stopped_steps]          = n_idle
    GEARS   [:, stopped_steps]          = 0
    return (N_GEARS, GEARS)


def possibleGears_byEngineRevs(V, N_GEARS, ngears,
                               n_idle, n_rated,
                               driveability_issues,
                               n_min_gear2):
    '''Calculates the engine-revolutions limits for all gears and returns where they are accepted.

    @return :list: min-revs for each gear (list[0] --> gear-1)
    @return :list: max-revs for each gear (list[0] --> gear-1)
    @see: Annex 2-3.2, p 71
    '''

    n_max_factor        = 1.2 # TODO: Move v_max_factor to model
    n_max               = n_max_factor * (n_rated - n_idle) + n_idle
    GEARS_YES_MAX       = (N_GEARS <= n_max)

    n_min_drive         = n_idle + 0.125 * (n_rated - n_idle)
    GEARS_YES_MIN       = (N_GEARS >= n_min_drive)
    GEARS_YES_MIN[0, :] = (N_GEARS[0, :] >= n_idle)
    ## FIXME: "incomprehensible" specs for Gear-2.
    GEARS_YES_MIN[1, :] = (N_GEARS[1, :] >= n_min_gear2) | (N_GEARS[1, :] == n_idle) # Set when N_GEAR generated.

    reportDriveabilityProblems(GEARS_YES_MIN, 'low revolutions', driveability_issues)
    reportDriveabilityProblems(GEARS_YES_MAX, 'high revolutions', driveability_issues)

    GEARS_YES       = (GEARS_YES_MIN & GEARS_YES_MAX)

    return GEARS_YES


def calcPower_required(V, test_mass, f0, f1, f2):
    '''

    @see: Annex 2-3.1, p 71
    '''

    kr = 1.1 # some inertial-factor blah, blah, blah

    VV      = V * V
    VVV     = VV * V
    A       = np.diff(V)
    A       = np.append(A, 0) # Restore element lost by diff().
    assert  V.shape == VV.shape == VVV.shape == A.shape, _shapes(V, VV, VVV, A)

    P_REQ   = (f0 * V + f1 * VV + f2 * VVV + kr * A * V * test_mass) / 3600.0
    assert  V.shape == P_REQ.shape, _shapes(V, P_REQ)

    return P_REQ



def calcPower_available(N_GEARS, test_mass, f0, f1, f2, n_idle, n_rated, p_rated, load_curve, p_safety_margin):
    '''

    @see: Annex 2-3.2, p 72
    '''

    N_NORM          = (N_GEARS - n_idle) / (n_rated - n_idle)
    P_WOT           = np.interp(N_NORM, load_curve[0], load_curve[1])
    P_AVAIL         = P_WOT * p_rated * p_safety_margin

    return P_AVAIL

def possibleGears_byPower(V, N_GEARS, P_REQ, mass, f0, f1, f2, gear_ratios,
                          n_idle, n_rated, p_rated, load_curve, p_safety_margin,
                          driveability_issues):
    '''

    @see: Annex 2-3.1 & 3.3, p 71 & 72
    '''

    P_AVAIL     = calcPower_available(N_GEARS, mass, f0, f1, f2, n_idle, n_rated, p_rated, load_curve, p_safety_margin)
    assert      V.shape == P_REQ.shape and N_GEARS.shape == P_AVAIL.shape, \
                                _shapes(V, P_REQ, N_GEARS, P_AVAIL)

    GEARS_YES   = P_AVAIL >= P_REQ

    reportDriveabilityProblems(GEARS_YES, 'power', driveability_issues)

    return GEARS_YES


def applyDriveabilityRules(GEARS):
    '''

    @see: Annex 2-4, p 72
    '''

    ## TODO: Implement driveability rules
    return GEARS


def reportDriveabilityProblems(GEARS_YES, reason, driveability_issues):
    failed_gears = (~GEARS_YES).all(0)
    if (failed_gears.any()):
        failed_steps = failed_gears.nonzero()[0]
        for step in failed_steps:
            driveability_issues[step].append(reason)
        log.warning('%i %s issues: %s', failed_steps.size, reason, failed_steps)


def calcCycleGears(V, P_REQ, mass, f0, f1, f2, gear_ratios,
                   n_idle, n_rated,
                   p_rated, load_curve,
                   v_stopped_threshold, p_safety_margin):
    '''
    @note: modifies V for velocities < v_stopped_threshold
    @return :array: CLUTCH:    a (1 X #velocity) bool-array, eg. [3, 150] --> gear(3), time(150)
    '''

    ## A multimap to collect problems.
    #
    from collections import defaultdict
    driveability_issues         = defaultdict(list)


    ## Apply stopped-vehicle threshold (Annex 2-4(a), p72)
    V[V <= v_stopped_threshold] = 0

    ## FIXME: "incomprehensible" specs for Gear-2.
    n_min_gear2     = max(1.15 * n_idle, 0.03 * (n_rated - n_idle) + n_idle)


    (N_GEARS, GEARS)            = calcEngineRevs_required(V, gear_ratios, n_idle, n_rated, n_min_gear2)

    G_BY_N                      = possibleGears_byEngineRevs(V, N_GEARS,
                                                len(gear_ratios),
                                                n_idle, n_rated,
                                                driveability_issues,
                                                n_min_gear2)

    G_BY_P                      = possibleGears_byPower(V, N_GEARS, P_REQ,
                                                mass, f0, f1, f2, gear_ratios,
                                                n_idle, n_rated, p_rated, load_curve, p_safety_margin,
                                                driveability_issues)
    assert                      G_BY_N.shape == G_BY_P.shape, _shapes(V, G_BY_N, G_BY_P)
    assert                      G_BY_N.dtype == G_BY_P.dtype == 'bool', _dtypes(G_BY_N, G_BY_P)

    GEARS_YES                   = (G_BY_N & G_BY_P)
    GEARS[~GEARS_YES]           = -1
    GEARS                       = GEARS.max(0)
    assert                      V.shape == GEARS.shape, _shapes(V, GEARS)
    assert                      'i' == GEARS.dtype.kind, GEARS.dtype
    assert                      all((GEARS >= -1) & (GEARS <= len(gear_ratios))), (min(GEARS), max(GEARS))


    GEARS                       = applyDriveabilityRules(GEARS)

    CLUTCH                      = (GEARS == 2) & (N_GEARS[1, :] == n_idle)

    return (GEARS, CLUTCH, driveability_issues)



if __name__ == '__main__':
    pass
