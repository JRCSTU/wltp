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
from wltc.instances import wltc_data
import logging
from numpy.testing.utils import assert_array_equal
'''
@author: ankostis@gmail.com
@since 5 Jan 2014
'''

from .. import experiment as ex
from ..experiment import Experiment
from ..experiment import downscaleCycle
from ..model import Model
from .goodvehicle import goodVehicle
import numpy as np
import numpy.testing as npt
import unittest
from matplotlib import pyplot as pylab


class Test(unittest.TestCase):

    def setUp(self):
        logging.basicConfig(level=logging.DEBUG)


    def plotResults(self, model):
        results = model['results']
        gears = results['gears']
        target = results['v_target']
        realv = results['v_real']
        clutch = results['clutch']

        clutch = clutch.nonzero()[0]
        pylab.vlines(clutch,  0, 40)
        pylab.plot(target)
        pylab.plot(gears * 12, '+')
#         pylab.plot(realv)



    def testDownscaling(self):
        wclasses = wltc_data()['classes']
        test_data = [(np.array(wclass['cycle']), wclass['downscale']['phases'], f_downscale)
                    for wclass in wclasses.values()
                    for f_downscale in np.linspace(0.1, 1, 10)]

        for (V, phases, f_downscale) in test_data:
            downscaleCycle(V, f_downscale, phases)


    def testNparray2Bytes(self):
        arr = np.array([-1, 0, 9, 10, 36, 255-ex._escape_char])

        self.assertEqual(ex.np2bytes(arr), b'\x7f\x80\x89\x8a\xa4\xff')
        self.assertRaisesRegex(AssertionError, 'Outside byte-range', ex.np2bytes, (arr + 1))
        self.assertRaisesRegex(AssertionError, 'Outside byte-range', ex.np2bytes, (arr - 1))

        npt.assert_array_equal(ex.bytes2np(ex.np2bytes(arr)), arr)


    def testRegex2bytes(self):
        regex = '\g1\g0\g24\g66\g127'

        self.assertEqual(ex.gearsregex(regex).pattern,  b'\x81\x80\x98\xc2\xff')

        regex = '\g1\g0|\g24\g66\g127'

        self.assertEqual(ex.gearsregex(regex).pattern,  b'\x81\x80|\x98\xc2\xff')

    def testGoodVehicle(self, skip_plot=False):
        logging.getLogger().setLevel(logging.DEBUG)

        inst = goodVehicle

        model = Model(inst)
        experiment = Experiment(model)
        experiment.run()
        self.assertTrue('results' in model.data, 'No "results" in Model: %s'%model.data)

        print('DRIVEABILITY: \n%s' % model.driveability_report())
        results = model.data['results']
        gears = results['gears']
        print('G1: %s, G2: %s' % (np.count_nonzero(gears == 1), np.count_nonzero(gears == 2)))


        ## Compare changed-results
        #
        import wltc.experiment  # @UnusedImport
        wltc.experiment.T = False
        model2 = Model(inst)
        experiment = Experiment(model2)
        experiment.run()
        cmp = (model.data['results']['gears'] != model2.data['results']['gears'])
        if (cmp.any()):
            self.plotResults(model2.data)
            print((model.data['results']['gears'] != model2.data['results']['gears']).nonzero())

        if (not skip_plot):
            print(model.data['results'])
            #print([wltc_data()['classes']['class3b']['cycle'][k] for k in model.data['results']['driveability_issues'].keys()])
            self.plotResults(model.data)

            np.set_printoptions(edgeitems=16)
            #print(driveability_issues)
            #print(v_max)
            #results['target'] = []; print(results)
            pylab.show()

    def testUnderPowered(self):
        inst = goodVehicle
        inst['vehicle']['p_rated'] = 50

        model = Model(inst)
        experiment = Experiment(model)
        experiment.run()


        inst['vehicle']['p_rated']      =  90
        inst['vehicle']['gear_ratios']  = [120.5, 75, 50, 40, 37, 32]

        model = Model(inst)
        experiment = Experiment(model)
        experiment.run()


#     def testPerf(self):
#         logging.getLogger().setLevel(logging.WARNING)
#         for i in range(1000):
#             self.testGoodVehicle(True)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
