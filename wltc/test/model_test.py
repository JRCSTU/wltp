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

from ..model import Model
from .. import instances as insts
from .goodvehicle import goodVehicle
import unittest


class Test(unittest.TestCase):

    def testGoodVehicle(self):
        inst = goodVehicle()

        model = Model(inst)
        self.assertEqual(model.data['vehicle']['full_load_curve'], insts.default_load_curve())


    def testOverlayOnInit(self):
        inst = goodVehicle()
        nval = 6000
        inst2 = {
            "vehicle": {
                "n_rated":nval,
            }
        }

        model = Model(inst, inst2)
        self.assertEqual(model.data['vehicle']['n_rated'], nval)

    def testMultiErrors(self):
        inst = goodVehicle()
        inst2 = {
            "vehicle": {
                "n_rated":-1,
                "n_idle":-2,
            }
        }

        model = Model(inst, inst2, skip_validation=True)
        errors = list(model.validate(True))
        self.assertIsNotNone(errors)
        self.assertEqual(len(errors), 2)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
