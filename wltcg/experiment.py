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


class Experiment(object):
    '''Runs the vehicle and cycle data describing a WLTC experiment. '''


    def __init__(self, model, validate_wltc = False):
        """
        ``model`` is a tree (formed by dicts & lists) holding the experiment data.

        ``skip_validation`` when true, does not validate the model.
        """

        from .instances import wltc_data

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
        '''See Annex 1'''

        class_limits = self.wltc['limits']['p_to_mass']
        if (p_m_ratio > class_limits[-1]):
            wltc_class = 'class3'
            ab = 'b' if v_max >= self.wltc['limits']['class3_speed'] else 'a'
            wltc_class += ab
        elif (p_m_ratio > class_limits[-2]):
            wltc_class = 'class2'
        else:
            wltc_class = 'class1'
        return wltc_class


    def downscaleCycle(self, cycle, downscale_params, p_max, v_max):
        '''TODO: Implement Downscaling, probably per class'''

        return (cycle, 0)


    def calcRequiredPower(self, V, test_mass, f0, f1, f2):
        '''See Annex 2-3.1, p 71'''

        import numpy as np

        kr = 1.1 # some factor blah, blah, blah

        V = np.array(V)
        A = np.diff(V)
        V = V[:-1]
        VV = V * V
        VVV = VV * V
        p_req = (f0 * V + f1 * VV + f2 * VVV + kr * A * V * test_mass) / 3600

        return p_req


    def run(self):
        '''Runs the loop (Annex 2)!'''

        data = self.model.data
        vehicle = data['vehicle']

        ## Prepare results
        self.results = data['results'] = {}

        mass = vehicle['mass']
        p_rated = vehicle['p_rated']
        n_rated = vehicle['n_rated']
        gear_ratios = vehicle['gear_ratios']

        ## Calc foundamental vehicle attributes.
        #
        # TODO: Store them into the model?
        p_m_ratio = (1000 * p_rated / mass)
        v_max = n_rated / gear_ratios[-1] # FIXME: is v_max ok???


        ## Decide class
        #
        wltc_class = self.decideClass(p_m_ratio, v_max)
        self.results['wltc_class'] = wltc_class
        class_data = self.wltc['cycles'][wltc_class]
        cycle = class_data['cycle']


        ## Downscale.
        #
        (cycle, downscale_factor) = self.downscaleCycle(cycle, class_data['downscale'], p_rated, v_max)
        self.results['target'] = cycle
        self.results['downscale_factor'] = downscale_factor

        ## Required power
        #
        (f0, f1, f2) = vehicle['resistance_coeffs']
        p_req = self.calcRequiredPower(cycle, mass, f0, f1, f2)

        print(wltc_class)


if __name__ == '__main__':
    pass
