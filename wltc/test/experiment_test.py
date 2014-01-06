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
'''
@author: ankostis@gmail.com
@since 5 Jan 2014
'''

from ..experiment import Experiment
from ..model import Model
from .goodvehicle import goodVehicle
import numpy as np
import unittest


class Test(unittest.TestCase):

    def plotResults(self, model):
        import pylab
        gears = model['results']['gears']
        target = model['results']['target']
        realv = model['results']['velocity']
        clutch = model['results']['clutch']

        print('G1: %s, G2: %s' % (np.count_nonzero(gears == 1), np.count_nonzero(gears == 2)))

        pylab.plot(gears * 18)
        pylab.plot(target)
        pylab.plot(clutch * 50)
        pylab.plot(realv)
        pylab.show()



    def testGoodVehicle(self):
        inst = goodVehicle

        model = Model(inst)
        experiment = Experiment(model)
        experiment.run()
        self.assertTrue('results' in model.data, 'No "results" in Model: %s'%model.data)

        #print('sdfdss')
        #print([wltc_data()['cycles']['class3b']['cycle'][k] for k in model.data['results']['driveability_issues'].keys()])
        self.plotResults(model.data)

        np.set_printoptions(edgeitems=16)
        #print(driveability_issues)
        #print(v_max)
        #results['target'] = []; print(results)

    def testUnderPowered(self):
        inst = goodVehicle
        inst['vehicle']['p_rated'] = 50

        model = Model(inst)
        experiment = Experiment(model)
        self.assertRaisesRegex(Exception, 'Downscaling needed', experiment.run) #FIXME: remove when implemented


#     def testPerf(self):
#         for i in range(1000):
#             self.testGoodVehicle()


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()