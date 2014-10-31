#! python
#-*- coding: utf-8 -*-
#
# Copyright 2013-2014 European Commission (JRC);
# Licensed under the EUPL (the 'Licence');
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at: http://ec.europa.eu/idabc/eupl

from __future__ import division, print_function, unicode_literals

import unittest
from unittest.case import skip
from wltp import model

import pandas as pd

from ..experiment import Experiment
from .goodvehicle import goodVehicle


class Test(unittest.TestCase):

    def testGoodVehicle(self):
        mdl = goodVehicle()

        exp = Experiment(mdl)
        mdl = exp._model
        self.assertTrue(pd.DataFrame(mdl['vehicle']['full_load_curve']).equals(pd.DataFrame(model.default_load_curve())))


    @skip("Cascade-models disabled") ##TODO: Re-enabl;e when pandel works.
    def testOverlayOnInit(self):
        mdl = goodVehicle()
        nval = 6000
        mdl2 = {
            "vehicle": {
                "n_rated":nval,
            }
        }

        exp = Experiment(mdl, mdl2)
        mdl = exp._model
        self.assertEqual(mdl['vehicle']['n_rated'], nval)

    def test_get_class_parts_limits(self):
        l = model.get_class_parts_limits('class1')
        self.assertSequenceEqual(l, [589.5])
        
        l = model.get_class_parts_limits('class2')
        self.assertSequenceEqual(l, [589.5, 1022.5, 1477.5])
        
        l = model.get_class_parts_limits('class3a')
        self.assertSequenceEqual(l, [589.5, 1022.5, 1477.5])
        l = model.get_class_parts_limits('class3b')
        self.assertSequenceEqual(l, [589.5, 1022.5, 1477.5])

    def test_get_class_pmr_limits(self):
        l = model.get_class_pmr_limits()
        self.assertSequenceEqual(l, [22, 34])

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
