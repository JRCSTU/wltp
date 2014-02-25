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
from .. import instances as insts
from .goodvehicle import goodVehicle
import unittest


class Test(unittest.TestCase):

    def testGoodVehicle(self):
        model = goodVehicle()

        exp = Experiment(model)
        model = exp.model
        self.assertEqual(model['vehicle']['full_load_curve'], insts.default_load_curve())


    def testOverlayOnInit(self):
        model = goodVehicle()
        nval = 6000
        model2 = {
            "vehicle": {
                "n_rated":nval,
            }
        }

        exp = Experiment(model, model2)
        model = exp.model
        self.assertEqual(model['vehicle']['n_rated'], nval)

    def testMultiErrors(self):
        model = goodVehicle()
        model2 = {
            "vehicle": {
                "n_rated":-1,
                "n_idle":-2,
            }
        }

        exp = Experiment(model, model2, skip_model_validation=True)
        errors = list(exp.validate(True))
        self.assertIsNotNone(errors)
        self.assertEqual(len(errors), 2)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
