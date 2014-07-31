#!/usr/bin/env python
#
# Copyright 2013-2014 European Commission (JRC);
# Licensed under the EUPL (the 'Licence');
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at: http://ec.europa.eu/idabc/eupl
'''
:created: 5 Jan 2014
'''

from ..experiment import Experiment
from wltp import model
from .goodvehicle import goodVehicle
import unittest


class Test(unittest.TestCase):

    def testGoodVehicle(self):
        mdl = goodVehicle()

        exp = Experiment(mdl)
        mdl = exp.model
        self.assertEqual(mdl['vehicle']['full_load_curve'], model.default_load_curve())


    def testOverlayOnInit(self):
        mdl = goodVehicle()
        nval = 6000
        mdl2 = {
            "vehicle": {
                "n_rated":nval,
            }
        }

        exp = Experiment(mdl, mdl2)
        mdl = exp.model
        self.assertEqual(mdl['vehicle']['n_rated'], nval)

    def testMultiErrors(self):
        mdl = goodVehicle()
        mdl2 = {
            "vehicle": {
                "n_rated":-1,
                "n_idle":-2,
            }
        }

        exp = Experiment(mdl, mdl2, skip_model_validation=True)
        errors = list(exp.validate(True))
        self.assertIsNotNone(errors)
        self.assertEqual(len(errors), 2)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
