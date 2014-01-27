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
from matplotlib import pyplot as pylab
import logging
import numpy as np
import numpy.testing as npt
import os
import pickle
import tempfile
import unittest

class ExperimentWholeVehs(unittest.TestCase):
    def setUp(self):
        logging.basicConfig(level=logging.DEBUG)
        self.run_comparison = True


    def compare_exp_results(self, results, fname, run_comparison):
        tmpfname = os.path.join(tempfile.gettempdir(), '%s.pkl'%fname)
        if (run_comparison):
            try:
                with open(tmpfname, 'rb') as tmpfile:
                    data_prev = pickle.load(tmpfile)
                    ## Compare changed-results
                    #
                    npt.assert_equal(results['gears'],  data_prev['gears'])
                    # Unreached code in case of assertion.
                    # cmp = results['gears'] != data_prev['gears']
                    # if (cmp.any()):
                    #     self.plotResults(data_prev)
                    #     print('>> COMPARING(%s): %s'%(fname, cmp.nonzero()))
                    # else:
                    #     print('>> COMPARING(%s): OK'%fname)
            except FileNotFoundError as ex:
                print('>> COMPARING(%s): No old-results found, 1st time to be stored in: '%fname, tmpfname)
                run_comparison = False

        if (not run_comparison):
            with open(tmpfname, 'wb') as tmpfile:
                pickle.dump(results, tmpfile)


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
        pylab.plot(realv)



    def testGoodVehicle(self, plot_results=False):
        logging.getLogger().setLevel(logging.DEBUG)

        inst = goodVehicle()

        model = Model(inst)
        experiment = Experiment(model)
        experiment.run()
        self.assertTrue('results' in model.data, 'No "results" in Model: %s'%model.data)

        print('DRIVEABILITY: \n%s' % model.driveability_report())
        results = model.data['results']
        gears = results['gears']
        print('G1: %s, G2: %s' % (np.count_nonzero(gears == 1), np.count_nonzero(gears == 2)))


        self.compare_exp_results(results, 'goodveh', self.run_comparison)


        if (plot_results):
            print(model.data['results'])
            #print([wltc_data()['classes']['class3b']['cycle'][k] for k in model.data['results']['driveability_issues'].keys()])
            self.plotResults(model.data)

            np.set_printoptions(edgeitems=16)
            #print(driveability_issues)
            #print(v_max)
            #results['target'] = []; print(results)
            pylab.show()


    def testUnderPowered(self, plot_results=False):
        inst = goodVehicle()
        inst['vehicle']['p_rated'] = 50

        model = Model(inst)
        experiment = Experiment(model)
        experiment.run()
        print('DRIVEABILITY: \n%s' % model.driveability_report())
        self.compare_exp_results(model.data['results'], 'unpower1', self.run_comparison)


        inst['vehicle']['mass']         =  1000
        inst['vehicle']['p_rated']      =  80
        inst['vehicle']['v_max']        =  120
        inst['vehicle']['gear_ratios']  = [120.5, 95, 72, 52]

        model = Model(inst)
        experiment = Experiment(model)
        experiment.run()
        print('DRIVEABILITY: \n%s' % model.driveability_report())
        self.compare_exp_results(model.data['results'], 'unpower2', self.run_comparison)

        if (plot_results):
            self.plotResults(model.data)
            pylab.show()


if __name__ == "__main__":
    import sys;#sys.argv = ['', 'Test.testName']
    unittest.main(argv = sys.argv[1:])
