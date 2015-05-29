#! python
#-*- coding: utf-8 -*-
#
# Copyright 2013-2014 European Commission (JRC);
# Licensed under the EUPL (the 'Licence');
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at: http://ec.europa.eu/idabc/eupl

from __future__ import division, print_function, unicode_literals

import doctest
import sys
import unittest
from unittest.case import skip

import pandas as pd
from wltp import model
import wltp

from ..experiment import Experiment
from .goodvehicle import goodVehicle


@unittest.skipIf(sys.version_info < (3, 4), "Doctests are made for py >= 3.3")
class TestDoctest(unittest.TestCase):

    def test_doctests(self):
        failure_count, test_count = doctest.testmod(
            wltp.model,
            optionflags=doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS)
        self.assertGreater(test_count, 0, (failure_count, test_count))
        self.assertEquals(failure_count, 0, (failure_count, test_count))



class Test(unittest.TestCase):

    def testGoodVehicle(self):
        mdl = goodVehicle()

        exp = Experiment(mdl)
        mdl = exp._model
        self.assertTrue(pd.DataFrame(mdl['vehicle']['full_load_curve']).equals(pd.DataFrame(model.default_load_curve())))


    @skip("Cascade-models disabled") ##TODO: Re-enable when pandel works.
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

    def test_get_class_parts_limits_sorted(self):
        classes = model._get_wltc_data()['classes']
        class_limits = {cls: model.get_class_parts_limits(cls, edges=True) for cls in classes.keys()}  
        for (cls,  l) in class_limits.items():
            self.assertSequenceEqual(l, sorted(l), 'Class(%s): Unsorted!'%cls)

    def test_get_class_parts_limits_with_edges(self):
        classes = model._get_wltc_data()['classes']
        class_limits = {cls: model.get_class_parts_limits(cls, edges=True) for cls in classes.keys()}  
        for (cls,  l) in class_limits.items():
            self.assertEqual(l[0], 0, 'Class(%s): Left-edge not 0!'%cls)
        for (cls,  l) in class_limits.items():
            self.assertEqual(l[-1], len(classes[cls]['cycle'])-0.5, 'Class(%s): Section Right-edge not len(cycle)!'%cls)


    def test_get_class_pmr_limits(self):
        l = model.get_class_pmr_limits()
        self.assertSequenceEqual(l, [22, 34])


    def test_get_class_pmr_limits_with_edges(self):
        pmr_limits = model.get_class_pmr_limits(edges=True)  
        self.assertEqual(pmr_limits[0], 0, 'Left-edge not 0!')
        self.assertEqual(pmr_limits[-1], float('inf'), 'PMR-limit: Right-edge not INF!')


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
