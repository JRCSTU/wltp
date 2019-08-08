#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2013-2019 European Commission (JRC);
# Licensed under the EUPL (the 'Licence');
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at: http://ec.europa.eu/idabc/eupl

import sys
import unittest
from unittest.case import skip

import pandas as pd
from wltp import datamodel
import wltp

from wltp.experiment import Experiment
from .goodvehicle import goodVehicle


class Test(unittest.TestCase):
    def testGoodVehicle(self):
        mdl = goodVehicle()

        exp = Experiment(mdl)
        mdl = exp._model
        defwot = datamodel.upd_default_load_curve({})["wot"]
        self.assertTrue(
            pd.DataFrame(mdl["wot"][["n_norm", "p_norm"]]).equals(pd.DataFrame(defwot))
        )

    @skip("Cascade-models disabled")  ##TODO: Re-enable when pandel works.
    def testOverlayOnInit(self):
        mdl = goodVehicle()
        nval = 6000
        mdl2 = {"n_rated": nval}

        exp = Experiment(mdl, mdl2)
        mdl = exp._model
        self.assertEqual(mdl["n_rated"], nval)

    def test_get_class_parts_limits_sorted(self):
        classes = datamodel.get_wltc_data()["classes"]
        class_limits = {
            cls: datamodel.get_class_parts_limits(cls, edges=True)
            for cls in classes.keys()
        }
        for (cls, l) in class_limits.items():
            self.assertSequenceEqual(l, sorted(l), "Class(%s): Unsorted!" % cls)

    def test_get_class_parts_limits_with_edges(self):
        classes = datamodel.get_wltc_data()["classes"]
        class_limits = {
            cls: datamodel.get_class_parts_limits(cls, edges=True)
            for cls in classes.keys()
        }
        for (cls, l) in class_limits.items():
            self.assertEqual(l[0], 0, "Class(%s): Left-edge not 0!" % cls)
        for (cls, l) in class_limits.items():
            self.assertEqual(
                l[-1],
                len(classes[cls]["cycle"]),
                "Class(%s): Section Right-edge not len(cycle)!" % cls,
            )

    def test_get_class_pmr_limits(self):
        l = datamodel.get_class_pmr_limits()
        self.assertSequenceEqual(l, [22, 34])

    def test_get_class_pmr_limits_with_edges(self):
        pmr_limits = datamodel.get_class_pmr_limits(edges=True)
        self.assertEqual(pmr_limits[0], 0, "Left-edge not 0!")
        self.assertEqual(pmr_limits[-1], float("inf"), "PMR-limit: Right-edge not INF!")


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
