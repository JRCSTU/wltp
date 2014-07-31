#!/usr/bin/env python
#
# Copyright 2013-2014 European Commission (JRC);
# Licensed under the EUPL (the 'Licence');
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at: http://ec.europa.eu/idabc/eupl
'''Testing of the pure-tree data (just dictionary & lists), without the Model/Experiment classes.

:created: 29 Dec 2013
'''

from .. import model
import json
import jsonschema
import unittest


class Test(unittest.TestCase):

    def setUp(self):
        self.goodVehicle_jsonTxt = '''{"vehicle": {
            "mass":1300,
            "v_max":195,
            "p_rated":110.625,
            "n_rated":5450,
            "n_idle":950,
            "n_min":500,
            "gear_ratios":[120.5, 75, 50, 43, 33, 28],
            "resistance_coeffs":[100, 0.5, 0.04]
            %s
        }}'''


    def testWltcData(self):
        mdl = model.wltc_data()
        validator = model.wltc_validator()

        validator.validate(mdl)


    def testModelBase(self):
        mdl = model.model_base()

        self.assertRaises(jsonschema.ValidationError, model.model_validator().validate, mdl)


    def testModelInstance_missingLoadCurve(self):
        json_txt = self.goodVehicle_jsonTxt % ('')
        mdl = json.loads(json_txt)
        validator = model.model_validator()

        self.assertRaisesRegex(jsonschema.ValidationError, "'full_load_curve' is a required property", validator.validate, mdl)


    def testModelInstance_simplInstanceeFullLoadCurve(self):
        json_txt = self.goodVehicle_jsonTxt % \
            (', "full_load_curve":[[ 1,  1,  1,  1,  1,  1,  1,  1,  1],   [ 0.23,  0.23, 0.23, 0.23, 0.23, 0.23, 0.23, 0.23, 0.23]]')
        mdl = json.loads(json_txt)

        model.model_validator().validate(mdl)
        self.assertNotEqual(mdl['vehicle']['full_load_curve'], model.default_load_curve())


    def testModelInstance_defaultLoadCurve(self):
        json_txt = self.goodVehicle_jsonTxt % \
            (', "full_load_curve":%s' % (json.dumps(model.default_load_curve())))
        mdl = json.loads(json_txt)
        validator = model.model_validator()

        validator.validate(mdl)



if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
