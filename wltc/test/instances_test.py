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
'''Testing of the pure-tree data (just dictionary & lists), without the Model/Experiment classes.

@author: ankostis@gmail.com
@since 29 Dec 2013
'''
import json
import jsonschema
import unittest

import wltc.schemas as schemas
import wltc.instances as insts


class Test(unittest.TestCase):

    def setUp(self):
        self.goodVehicle_jsonTxt = '''{"vehicle": {
            "mass":1300,
            "p_rated":110.625,
            "n_rated":5450,
            "n_idle":950,
            "n_min":500,
            "gear_ratios":[120.5, 75, 50, 43, 33, 28],
            "resistance_coeffs":[100, 0.5, 0.04]
            %s
        }}'''


    def testWltcData(self):
        model = insts.wltc_data()
        validator = schemas.wltc_validator()

        validator.validate(model)


    def testModelBase(self):
        model = insts.model_base()

        self.assertRaises(jsonschema.ValidationError, schemas.model_validator().validate, model)


    def testModelInstance_missingLoadCurve(self):
        json_txt = self.goodVehicle_jsonTxt % ('')
        model = json.loads(json_txt)
        validator = schemas.model_validator()

        self.assertRaisesRegex(jsonschema.ValidationError, "'full_load_curve' is a required property", validator.validate, model)


    def testModelInstance_simplInstanceeFullLoadCurve(self):
        json_txt = self.goodVehicle_jsonTxt % \
            (', "full_load_curve":[[1, 2.3], [1, 2.3], [1, 2.3], [1, 2.3], [1, 2.3], [1, 2.3], [1, 2.3], [1, 2.3], [1, 2.3]]')
        model = json.loads(json_txt)

        schemas.model_validator().validate(model)
        self.assertNotEqual(model['vehicle']['full_load_curve'], insts.default_load_curve())


    def testModelInstance_defaultLoadCurve(self):
        json_txt = self.goodVehicle_jsonTxt % \
            (', "full_load_curve":%s' % (json.dumps(insts.default_load_curve())))
        model = json.loads(json_txt)
        validator = schemas.model_validator()

        validator.validate(model)



if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()