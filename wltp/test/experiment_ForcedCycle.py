#! python
#-*- coding: utf-8 -*-
#
# Copyright 2013-2014 European Commission (JRC);
# Licensed under the EUPL (the 'Licence');
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at: http://ec.europa.eu/idabc/eupl

from __future__ import division, print_function, unicode_literals

import logging
import unittest
from wltp.experiment import Experiment
from wltp.test.goodvehicle import goodVehicle

from pandas.core.common import PandasError

import numpy as np
import numpy.testing as npt
import pandas as pd

from ..utils import assertRaisesRegex


class TestForcedCycle(unittest.TestCase):
    def setUp(self):
        logging.basicConfig(level=logging.DEBUG)

    def test_badCycle(self):
        mdl = goodVehicle()

        mdl['params'] = params = {}
        mdl['cycle_run'] = 1

        with assertRaisesRegex(self, PandasError, 'DataFrame constructor not properly called'):
            experiment = Experiment(mdl)
            mdl = experiment.run()


    def test_two_ramps_smoke_test(self):
        mdl = goodVehicle()

        V = np.hstack((np.r_[0:100:2], np.r_[100:0:-2]))
        mdl['cycle_run'] = {'v_target': V}

        experiment = Experiment(mdl)
        mdl = experiment.run()

    def test_two_ramps_with_map(self):
        V = np.array([0,2,5,10,20,30,40,50,30,20,10,5,1,0])
        v_columns = ('v_class', 'v_target')
        slope = [0, 0, 0.1, 0.1, 0.2, 0.2, 0.1, 0.1, 0.1, 0.1, 0.1,0,0,0]
        for col in v_columns:
            results = []
            for s in (slope, None):
                mdl = {
                    "vehicle": {
                        "unladen_mass": 1430,
                        "test_mass":    1500,
                        "v_max":    None,
                        "p_rated":  100,
                        "n_rated":  5450,
                        "n_idle":   950,
                        "gear_ratios":      [120.5, 75, 50, 43, 37, 32],
                        "resistance_coeffs":[100, 0.5, 0.04],
                    }, 'cycle_run': {
                        col: V,
                    }
                }

                if s:
                    mdl['cycle_run']['slope'] = s

                proc = Experiment(mdl)
                mdl = proc.run()

                #print(mdl)

                cycle_run = mdl['cycle_run']
                if s:
                    self.assertIn('slope', cycle_run)
                self.assertIn('gears', cycle_run)
                for vcol in v_columns:
                    npt.assert_array_equal(V, cycle_run[vcol], "V_Column(%s) not overriden!"%vcol)
                results.append(cycle_run['gears'])
            npt.assert_array_equal(V, cycle_run[vcol], "V_Column(%s) not overriden!"%vcol)

    def test_two_ramps_with_slope(self):
        V = np.hstack((np.r_[0:100:2], np.r_[100:0:-2]))
        SLOPE = np.random.rand(V.shape[0])
        v_columns = ('v_class', 'v_target')
        for col in v_columns:
            mdl = goodVehicle()

            mdl['cycle_run'] = pd.DataFrame({
                col: V,
                'slope': SLOPE,
            })
            proc = Experiment(mdl)
            mdl = proc.run()

            #print(pd.DataFrame(mdl['cycle_run']))

            cycle_run = mdl['cycle_run']
            self.assertIn('slope', cycle_run)
            self.assertIn('gears', cycle_run)
            for vcol in v_columns:
                npt.assert_array_equal(V, cycle_run[vcol], "V_Column(%s) not overriden!"%vcol)


if __name__ == "__main__":
    import sys
    unittest.main(verbosity=2, argv=sys.argv)
