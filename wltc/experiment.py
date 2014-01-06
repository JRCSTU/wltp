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

'''The actual WLTC gear-shift calculator which consumes 2 Docs, Model and WLTC-data, and updates the first .

An "execution" or a "run" of an experiment is depicted in the following diagram::

                       _______________
     .-------.        |               |      .------------------.
    / model /-.   ==> |   Experiment  | ==> / model(augmented) /
   '-------'  /   ==> |---------------|    '------------------'
     .-------'        |  .-----------.|
                      | / wltc-data / |
                      |'-----------'  |
                      |_______________|

A usage example::

    model = wltc.Doc(json.loads(\'''{
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


Note: ALL_CAPITALS variable denote vectors, usually over the velocity-profile (the cycle),

     t:||: 0  1  2  3
    ---+-------------
    g1:|[[ 1, 1, 1, 1, ... 1, 1
    g2:|   2, 2, 2, 2, ... 2, 2
    g3:|   3, 3, 3, 3, ... 3, 3
    g4 |   4, 4, 4, 4, ... 4, 4 ]]


@author: ankostis@gmail.com
@since: 1 Jan 2014
'''

from .instances import wltc_doc
import logging
import numpy as np

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


    def __init__(self, model, wltc_data = None):
        """
        ``model`` is a tree (formed by dicts & lists) holding the experiment data.

        ``skip_validation`` when true, does not validate the model.
        """

        self.dtype = np.float32
        self.model = model
        if (wltc_data is None):
            self.wltc = wltc_doc()

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
        mass                    = vehicle['mass']
        p_rated                 = vehicle['p_rated']
        n_rated                 = vehicle['n_rated']
        n_idle                  = vehicle['n_idle']
        gear_ratios             = vehicle['gear_ratios']
        (f0, f1, f2)            = vehicle['resistance_coeffs']

        ## Calc foundamental vehicle attributes.
        #
        # TODO: Store them back into the model?
        p_m_ratio               = (1000 * p_rated / mass)
        v_max                   = n_rated / gear_ratios[-1] # FIXME: is v_max ok???
        n_min_drive             = n_idle + 0.235 * (n_rated - n_idle)


        ## Decide WLTC-class.
        #
        class_limits            = self.wltc.data['parameters']['p_to_mass_class_limits']
        class3_velocity_split   = self.wltc.data['parameters']['class3_split_velocity']
        wltc_class              = decideClass(class_limits, class3_velocity_split, p_m_ratio, v_max)
        results['wltc_class']   = wltc_class
        class_data              = self.wltc.data['cycles'][wltc_class]
        cycle                   = class_data['cycle']


        ## Velocity profile.
        V                       = np.array(cycle, dtype=self.dtype)


        ## Downscale velocity-profile.
        #
        dsc_data                = class_data['downscale']
        phases                  = dsc_data['phases']
        max_p_values            = dsc_data['max_p_values']
        downsc_coeffs           = dsc_data['factor_coeffs']
        dsc_v_split             = dsc_data['v_max_split'] if 'v_max_split' in dsc_data else None
        (V, downscale_factor)   = downscaleCycle(V, phases, max_p_values, downsc_coeffs, dsc_v_split, p_rated, v_max)
        results['target']       = V
        results['downscale_factor'] = downscale_factor


        ## Calc possible gears.
        #
        idle_velocity           = self.wltc.data['parameters']['idle_velocity'] # Km/h
        safety_margin           = self.wltc.data['parameters']['power_safety_margin']
        load_curve              = vehicle['full_load_curve']
        (GEARS, driveability_issues)      = calcCycleGears(V, mass, f0, f1, f2, gear_ratios,
                                                             n_idle, n_min_drive, n_rated,
                                                             p_rated, load_curve,
                                                             idle_velocity, safety_margin)
        assert                              V.shape == GEARS.shape, _shapes(V, GEARS)
        results['gears']                    = GEARS
        results['driveability_issues']    = driveability_issues



        np.set_printoptions(edgeitems=16)
        print(driveability_issues)
        print(v_max)
        #results['target'] = []; print(results)




#######################
## PURE CALCULATIONS ##
#######################


def decideClass(class_limits, class3_velocity_split, p_m_ratio, v_max):
    '''

    @see: Annex 1, p 19
    '''

    if (p_m_ratio > class_limits[-1]):
        wltc_class = 'class3'
        ab = 'b' if v_max >= class3_velocity_split else 'a'
        wltc_class += ab
    elif (p_m_ratio > class_limits[-2]):
        wltc_class = 'class2'
    else:
        wltc_class = 'class1'
    return wltc_class



def downscaleCycle(cycle, phases, max_p_values, downsc_coeffs, dsc_v_split, p_max, v_max):
    '''TODO: Implement Downscaling, probably per class'''


    downscale_factor = 0
    return (cycle, downscale_factor)



def calcEngineRevs_required(V, gear_ratios, n_idle, idle_velocity):
    '''Calculates the required engine-revolutions to achieve target-velocity for all gears.

    @return :array: a (gears X velocity) array, [3, 150] --> gear(3), time(150)
    @see: Annex 2-3.2, p 71
    '''

    assert          V.ndim == 1, (V.shape, gear_ratios)

    GEARS           = np.tile(np.arange(1, len(gear_ratios) + 1, dtype='int32'), (len(V), 1)).T
    assert          GEARS.shape[0] == len(gear_ratios), (GEARS.shape, gear_ratios)

    GEAR_RATIOS     = np.tile(gear_ratios, (len(V), 1)).T
    N_GEARS         = np.tile(V, (len(gear_ratios), 1))
    N_GEARS         = N_GEARS * GEAR_RATIOS

    assert          N_GEARS.shape== GEARS.shape  == GEAR_RATIOS.shape, _shapes(N_GEARS, GEARS, GEAR_RATIOS, V)

    low_velocs                  = (V <= idle_velocity)
    N_GEARS [:, low_velocs]     = n_idle
    GEARS   [:, low_velocs]     = 0

    return (N_GEARS, GEARS)


def calcEngineRevs_availableMinMax(gear_ratios, n_idle, n_min_drive, n_rated):
    '''Calculates the engine-revolutions limits for all gears.

    @return :list: min-revs for each gear (index-0 = gear-0)
    @return :list: max-revs for each gear (index-0 = gear-0)
    @see: Annex 2-3.2, p 71
    '''

    n_min           = np.ones_like(gear_ratios) * n_min_drive
    n_min[0]        = n_idle
    n_min[1]        = max(1.15 * n_idle, 0.03 * (n_rated - n_idle) + n_idle)

    n_max           = np.ones_like(gear_ratios) * (n_rated - n_idle) + n_idle

    return (n_min, n_max)


def possibleGears_byEngineRevs(V, N_GEARS, f0, f1, f2, gear_ratios,
                               n_idle, n_min_drive, n_rated,
                               driveability_issues):

    (n_min, n_max)  = calcEngineRevs_availableMinMax(gear_ratios, n_idle, n_min_drive, n_rated)
    N_MIN           = np.tile(n_min, (len(V), 1)).T
    N_MAX           = np.tile(n_max, (len(V), 1)).T
    assert          N_GEARS.shape == N_MIN.shape == N_MAX.shape, _shapes(N_GEARS, N_MIN, N_MAX)

    GEARS_YES_MIN   = (N_MIN <= N_GEARS)
    GEARS_YES_MAX   = (N_GEARS <= N_MAX)
    GEARS_YES       = (GEARS_YES_MIN & GEARS_YES_MAX)
    reportDriveabilityProblems(GEARS_YES, 'low revolutions', driveability_issues)
    reportDriveabilityProblems(GEARS_YES, 'high revolutions', driveability_issues)

    gear2_n_min_limit = n_idle # TODO: impl calc n_min for Gear-2.

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



def calcPower_available(N_GEARS, test_mass, f0, f1, f2, n_idle, n_rated, p_rated, load_curve, safety_margin):
    '''

    @see: Annex 2-3.2, p 72
    '''

    N_NORM          = (N_GEARS - n_idle) / (n_rated - n_idle)
    P_WOT           = np.interp(N_NORM, load_curve[0], load_curve[1])
    P_AVAIL         = P_WOT * p_rated * safety_margin

    return P_AVAIL

def possibleGears_byPower(V, N_GEARS, mass, f0, f1, f2, gear_ratios,
                          n_idle, n_rated, p_rated, load_curve, safety_margin,
                          driveability_issues):
    '''

    @see: Annex 2-3.1 & 3.3, p 71 & 72
    '''

    P_REQ       = calcPower_required(V, mass, f0, f1, f2)
    P_AVAIL     = calcPower_available(N_GEARS, mass, f0, f1, f2, n_idle, n_rated, p_rated, load_curve, safety_margin)
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


def calcCycleGears(V, mass, f0, f1, f2, gear_ratios,
                   n_idle, n_min_drive, n_rated,
                   p_rated, load_curve,
                   idle_velocity, safety_margin):
    ## A multimap to collect problems.
    #
    from collections import defaultdict
    driveability_issues = defaultdict(list)


    (N_GEARS, GEARS)    = calcEngineRevs_required(V, gear_ratios, n_idle, idle_velocity)

    G_BY_N              = possibleGears_byEngineRevs(V, N_GEARS,
                                        f0, f1, f2, gear_ratios,
                                        n_idle, n_min_drive, n_rated,
                                        driveability_issues)

    G_BY_P              = possibleGears_byPower(V, N_GEARS,
                                        mass, f0, f1, f2, gear_ratios,
                                        n_idle, n_rated, p_rated, load_curve, safety_margin,
                                        driveability_issues)
    assert              G_BY_N.shape == G_BY_P.shape, _shapes(V, G_BY_N, G_BY_P)
    assert              G_BY_N.dtype == G_BY_P.dtype == 'bool', _dtypes(G_BY_N, G_BY_P)

    GEARS_YES           = (G_BY_N & G_BY_P)
    GEARS[~GEARS_YES]   = -1
    GEARS               = GEARS.max(0)
    assert              V.shape == GEARS.shape, _shapes(V, GEARS)
    assert              'i' == GEARS.dtype.kind, GEARS.dtype
    assert              all((GEARS >= -1) & (GEARS <= len(gear_ratios))), (min(GEARS), max(GEARS))


    GEARS       = applyDriveabilityRules(GEARS)


    return (GEARS, driveability_issues)



if __name__ == '__main__':
    pass
