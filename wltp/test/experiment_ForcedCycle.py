#!/usr/bin/env python
#
# Copyright 2013-2014 European Commission (JRC);
# Licensed under the EUPL (the 'Licence');
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at: http://ec.europa.eu/idabc/eupl
'''
:created: 10-Aug 2014
'''

import logging
import unittest

import numpy as np
import pandas as pd
from wltp.experiment import Experiment
from wltp.test.goodvehicle import goodVehicle


class TestForcedCycle(unittest.TestCase):
    def setUp(self):
        logging.basicConfig(level=logging.DEBUG)

    def test_badCycle(self):
        model = goodVehicle()

        V = pd.DataFrame({'foo': [1,2,3], 'b': [4,5,6]})
        model['params'] = params = {}
        params['forced_cycle'] = V

        self.assertRaises(ValueError, Experiment, model)


    def test_two_ramps(self):
        model = goodVehicle()

        V = np.hstack((np.r_[0:100:2], np.r_[100:0:-2]))
        model['params'] = params = {}
        params['forced_cycle'] = V
        experiment = Experiment(model)
        model = experiment.run()

    def test_two_ramps_with_slope(self):
        model = goodVehicle()

        V = np.hstack((np.r_[0:100:2], np.r_[100:0:-2]))
        SLOPE = np.random.rand(V.shape[0])
        model['params'] = params = {}
        params['forced_cycle'] = pd.DataFrame({
            'v': V,
            'slope': SLOPE,
        })
        experiment = Experiment(model)
        model = experiment.run()

        print(pd.DataFrame(model['cycle_run']))



if __name__ == "__main__":
    import sys
    unittest.main(verbosity=2, argv=sys.argv)
