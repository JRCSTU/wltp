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

'''The actual WLTC gear-shift calculator.

An "execution" or a "run" of an experiment is depicted in the following diagram::

                       _______________
     .-------.        |               |      .------------------.
    / Model /-.   ==> |   Experiment  | ==> / Model(augmented) /
   '-------'  /   ==> |---------------|    '------------------'
     .-------'        |  .-----------.|
                      | / WLTC-data / |
                      |'-----------'  |
                      |_______________|

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



@author: ankostis@gmail.com
@since: 1 Jan 2014
'''

import numpy as np


def _shapes(*arrays):
    import operator
    op_shape = operator.attrgetter('shape')
    return list(map(op_shape, arrays))


class Experiment(object):
    '''Runs the vehicle and cycle data describing a WLTC experiment.

        Note: ALL_CAPITALS variable denote vectors, usually over the velocity-profile (the cycle),
        arranged in rows for each gear.
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
        class_limits            = self.wltc['limits']['p_to_mass']
        class3_velocity_split   = self.wltc['limits']['class3_velocity']
        wltc_class              = decideClass(class_limits, class3_velocity_split, p_m_ratio, v_max)
        results['wltc_class']   = wltc_class
        class_data              = self.wltc['cycles'][wltc_class]
        cycle                   = class_data['cycle']


        ## Velocity profile.
        V                       = np.array(cycle, dtype=self.dtype)


        ## Downscale velocity-profile.
        #
        (V, downscale_factor)   = downscaleCycle(V, class_data['downscale'], p_rated, v_max)
        results['target']       = V
        results['downscale_factor'] = downscale_factor


        ## Calc possible gears.
        #
        GEARS                   = calcCycleGears(V, mass, f0, f1, f2, gear_ratios, n_idle, n_min_drive, n_rated)
        assert                  GEARS.shape == V.shape, _shapes(GEARS, V)
        results['gears']        = GEARS



        np.set_printoptions(edgeitems=16)
        print(v_max)
        results['target'] = []; print(results)




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



def downscaleCycle(cycle, downscale_params, p_max, v_max):
    '''TODO: Implement Downscaling, probably per class'''

    downscale_factor = 0
    return (cycle, downscale_factor)



def calcEngineRevs_required(V, gear_ratios):
    '''Calculates the required engine-revolutions to achieve target-velocity for all gears.

    @return :array: a (gears X velocity) array, [3, 150] --> gear(3), time(150)
    @see: Annex 2-3.2, p 71
    '''

    zero_velocity  = 1 # Km/h
    N_GEARS     = np.tile(V, (len(gear_ratios), 1))
    N_GEARS[N_GEARS <= zero_velocity] = 0
    GR          = np.tile(gear_ratios, (len(V), 1)).T
    assert      N_GEARS.shape == GR.shape and GR.shape[0] == len(gear_ratios), \
                        [len(gear_ratios)] + _shapes(N_GEARS, GR)

    N_GEARS     = N_GEARS * GR

    return N_GEARS


def calcEngineRevs_minMax(V, gear_ratios, n_idle, n_min_drive, n_rated):
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


def possibleGears_byEngineRevs(V, f0, f1, f2, gear_ratios, n_idle, n_min_drive, n_rated):

    N_GEARS         = calcEngineRevs_required(V, gear_ratios)
    (n_min, n_max)  = calcEngineRevs_minMax(V, gear_ratios, n_idle, n_min_drive, n_rated)
    N_MIN           = np.tile(n_min, (len(V), 1)).T
    N_MAX           = np.tile(n_max, (len(V), 1)).T
    assert          N_GEARS.shape == N_MIN.shape == N_MAX.shape, _shapes(N_GEARS, N_MIN, N_MAX)

    GEARS           = np.logical_and(N_MIN <= N_GEARS, N_GEARS <= N_MAX)

    gear2_n_min_limit = n_idle # TODO: calc n_min for Gear-2.

    return GEARS


def calcRequiredPower(V, test_mass, f0, f1, f2):
    '''

    @see: Annex 2-3.1 & 3.3, p 71 & 72
    '''

    kr = 1.1 # some inertial-factor blah, blah, blah

    VV      = V * V
    VVV     = VV * V
    A       = np.diff(V)
    A       = np.append(A, 0) # Restore element lost by diff().
    assert  A.shape == V.shape == VV.shape == VVV.shape, _shapes(V, VV, VVV, A)

    P_REQ   = (f0 * V + f1 * VV + f2 * VVV + kr * A * V * test_mass) / 3600.0
    assert  V.shape == P_REQ.shape, _shapes(V, P_REQ)

    return P_REQ


def possibleGears_byPower(V, mass, f0, f1, f2, gear_ratios):

    P_REQ   = calcRequiredPower(V, mass, f0, f1, f2) # TODO:Pwot
    GEARS     = np.tile(V, (len(gear_ratios), 1))

    return GEARS


def applyDriveabilityRules(GEARS):
    '''

    @see: Annex 2-4, p 72
    '''

    ## TODO: Implement after-process rules
    return GEARS


def calcCycleGears(V, mass, f0, f1, f2, gear_ratios, n_idle, n_min_drive, n_rated):
    G_BY_N      = possibleGears_byEngineRevs(
                        V, f0, f1, f2, gear_ratios, n_idle, n_min_drive, n_rated)
    G_BY_P      = possibleGears_byPower(V, mass, f0, f1, f2, gear_ratios)
    assert      G_BY_N.shape == G_BY_P.shape, _shapes(G_BY_N, G_BY_P)

    GEARS       = np.dstack((G_BY_N, G_BY_P))
    GEARS       = np.max(GEARS, (2, 0))
    assert      GEARS.shape == V.shape, _shapes(GEARS, V)

    GEARS = applyDriveabilityRules(GEARS)

    return GEARS



if __name__ == '__main__':
    pass
