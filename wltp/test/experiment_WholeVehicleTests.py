#!/usr/bin/env python
#
# Copyright 2013-2014 European Commission (JRC);
# Licensed under the EUPL (the 'Licence');
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at: http://ec.europa.eu/idabc/eupl
'''Tests check top-level functionality.

:created: 5 Jan 2014
'''


from ..experiment import Experiment
from .goodvehicle import goodVehicle
from matplotlib import pyplot as plt
import logging
import numpy as np
import numpy.testing as npt
import os
import pickle
import tempfile
import unittest

log = logging.getLogger(__name__)

class ExperimentWholeVehs(unittest.TestCase):
    def setUp(self):
        logging.basicConfig(level=logging.DEBUG)
        self.run_comparison = True # NOTE: Set once to False to UPDATE sample-results (assuming they are ok).


    def compare_exp_results(self, tabular, fname, run_comparison):
        tmpfname = os.path.join(tempfile.gettempdir(), '%s.pkl'%fname)
        if (run_comparison):
            try:
                with open(tmpfname, 'rb') as tmpfile:
                    data_prev = pickle.load(tmpfile)
                    ## Compare changed-tabular
                    #
                    npt.assert_equal(tabular['gears'],  data_prev['gears'])
                    # Unreached code in case of assertion.
                    # cmp = tabular['gears'] != data_prev['gears']
                    # if (cmp.any()):
                    #     self.plotResults(data_prev)
                    #     print('>> COMPARING(%s): %s'%(fname, cmp.nonzero()))
                    # else:
                    #     print('>> COMPARING(%s): OK'%fname)
            except FileNotFoundError as ex:  # @UnusedVariable
                print('>> COMPARING(%s): No old-tabular found, 1st time to be stored in: '%fname, tmpfname)
                run_comparison = False

        if (not run_comparison):
            with open(tmpfname, 'wb') as tmpfile:
                pickle.dump(tabular, tmpfile)


    def plotResults(self, model):
        cycle = model['cycle_run']
        gears = cycle['gears']
        target = cycle['v_target']
        realv = cycle['v_real']
        clutch = cycle['clutch']

        clutch = clutch.nonzero()[0]
        plt.vlines(clutch,  0, 40)
        plt.plot(target)
        plt.plot(gears * 12, '+')
        plt.plot(realv)



    def testGoodVehicle(self, plot_results=False):
        logging.getLogger().setLevel(logging.DEBUG)

        model = goodVehicle()

        experiment = Experiment(model)
        model = experiment.run()
        self.assertTrue('cycle_run' in model, 'No result "cycle" in Model: %s'%model)

        print('DRIVEABILITY: \n%s' % experiment.driveability_report())
        cycle = model['cycle_run']
        gears = cycle['gears']
        print('G1: %s, G2: %s' % (np.count_nonzero(gears == 1), np.count_nonzero(gears == 2)))


        self.compare_exp_results(cycle, 'goodveh', self.run_comparison)


        if (plot_results):
            print(model['cycle_run'])
            #print([wltc_data()['classes']['class3b']['cycle_run'][k] for k in model['cycle_run']['driveability_issues'].keys()])
            self.plotResults(model)

            np.set_printoptions(edgeitems=16)
            #print(driveability_issues)
            #print(v_max)
            #results['target'] = []; print(results)
            plt.show()


    def testUnderPowered(self, plot_results=False):
        model = goodVehicle()
        model['vehicle']['p_rated'] = 50

        experiment = Experiment(model)
        model = experiment.run()
        print('DRIVEABILITY: \n%s' % experiment.driveability_report())
        self.compare_exp_results(model['cycle_run'], 'unpower1', self.run_comparison)


        model['vehicle']['mass']         =  1000
        model['vehicle']['p_rated']      =  80
        model['vehicle']['v_max']        =  120
        model['vehicle']['gear_ratios']  = [120.5, 95, 72, 52]

        experiment = Experiment(model)
        model = experiment.run()
        print('DRIVEABILITY: \n%s' % experiment.driveability_report())
        self.compare_exp_results(model['cycle_run'], 'unpower2', self.run_comparison)

        if (plot_results):
            self.plotResults(model)
            plt.show()


if __name__ == "__main__":
    import sys;#sys.argv = ['', 'Test.testName']
    unittest.main(argv = sys.argv[1:])
