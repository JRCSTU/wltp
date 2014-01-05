#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# Copyright 2013-2014 ankostis@gmail.com
#
# This file is part of wltcg.
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

    model = wltcg.Model(json.loads(\'''{
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

    experiment = wltcg.Experiment(model)
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

        Note: ALL_CAPITALS variable denote vectors, usually over the velocity-profile (the cycle).
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



    def decideClass(self, p_m_ratio, v_max):
        '''

        @see: Annex 1, p 19
        '''

        class_limits = self.wltc['limits']['p_to_mass']
        if (p_m_ratio > class_limits[-1]):
            wltc_class = 'class3'
            ab = 'b' if v_max >= self.wltc['limits']['class3_velocity'] else 'a'
            wltc_class += ab
        elif (p_m_ratio > class_limits[-2]):
            wltc_class = 'class2'
        else:
            wltc_class = 'class1'
        return wltc_class


    def downscaleCycle(self, cycle, downscale_params, p_max, v_max):
        '''TODO: Implement Downscaling, probably per class'''

        downscale_factor = 0
        return (cycle, downscale_factor)


    def calcRequiredPower(self, V, test_mass, f0, f1, f2):
        '''

        @see: Annex 2-3.1, p 71
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

    def calcEngineRevsPerGear_required(self, V, gear_ratios):
        '''

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

    def calcEngineRevsPerGear_minMax(self, V, gear_ratios, n_idle, n_min_drive, n_rated):
        '''

        @see: Annex 2-3.2, p 71
        '''

        (n_min, n_max) = (0, 0)
        return (n_min, n_max)


    def run(self):
        '''Runs the main-loop!

        @see: Annex 2, p 70
        '''

        data        = self.model.data
        vehicle     = data['vehicle']

        ## Prepare results
        self.results = results = data['results'] = {}

        ## Extract vehicle attributes from model.
        #
        mass            = vehicle['mass']
        p_rated         = vehicle['p_rated']
        n_rated         = vehicle['n_rated']
        n_idle          = vehicle['n_idle']
        gear_ratios     = vehicle['gear_ratios']

        ## Calc foundamental vehicle attributes.
        #
        # TODO: Store them back into the model?
        p_m_ratio       = (1000 * p_rated / mass)
        v_max           = n_rated / gear_ratios[-1] # FIXME: is v_max ok???
        n_min_drive     = n_idle + 0.235 * (n_rated - n_idle)


        ## Decide WLTC-class.
        #
        wltc_class              = self.decideClass(p_m_ratio, v_max)
        results['wltc_class']   = wltc_class
        class_data              = self.wltc['cycles'][wltc_class]
        cycle                   = class_data['cycle']


        V                       = np.array(cycle, dtype=self.dtype)

        ## Downscale velocity-profile.
        #
        (V, downscale_factor)   = self.downscaleCycle(V, class_data['downscale'], p_rated, v_max)
        results['target']       = V
        results['downscale_factor'] = downscale_factor


        ## Calc gears-shifts.
        #
        (f0, f1, f2)            = vehicle['resistance_coeffs']
        P_REQ                   = self.calcRequiredPower(V, mass, f0, f1, f2)
        N_GEARS                 = self.calcEngineRevsPerGear_required(V, gear_ratios)
        (n_min, n_max)          = self.calcEngineRevsPerGear_minMax(V, gear_ratios, n_idle, n_min_drive, n_rated)

        np.set_printoptions(edgeitems=16)
        print(v_max)
        print(results)


if __name__ == '__main__':
    pass
