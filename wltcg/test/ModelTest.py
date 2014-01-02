'''
Created on 29 Dec 2013

@author: ankostis
'''
import json
import jsonschema
import unittest

from .. import model_base
from .. import get_model_validator
from .. import default_load_curve


class Test(unittest.TestCase):

    def setUp(self):
        self.goodVehicle_jsonTxt = '''{
            "mass":5,
            "p_rated":5,
            "n_rated":5,
            "p_max":5,
            "n_idle":5,
            "n_min":5,
            "gear_ratios":[5, 5, 6],
            "resistance_coeffs":[1, 2, 3]
            %s
        }'''


    def testEmptyModel(self):
        json_txt = '''{
        }'''
        model = json.loads(json_txt)

        self.assertRaises(jsonschema.ValidationError, get_model_validator().validate, model)


    def testBaseModel(self):
        model = model_base

        self.assertRaises(jsonschema.ValidationError, get_model_validator().validate, model)


    def testGoodVehicleNoLoadCurve(self):
        json_txt = self.goodVehicle_jsonTxt % ('')
        model = json.loads(json_txt)

        get_model_validator().validate(model)
        self.assertIsNotNone(model['full_load_curve'])
        self.assertEqual(model['full_load_curve'], default_load_curve)


    def testFullLoadCurve_simple(self):
        json_txt = self.goodVehicle_jsonTxt % \
            (', "full_load_curve":[[1, 2.3], [1, 2.3], [1, 2.3], [1, 2.3], [1, 2.3], [1, 2.3], [1, 2.3], [1, 2.3], [1, 2.3]]')
        model = json.loads(json_txt)

        get_model_validator().validate(model)
        self.assertNotEqual(model['full_load_curve'], default_load_curve)


    def testFullLoadCurve_default(self):
        json_txt = self.goodVehicle_jsonTxt % \
            (', "full_load_curve":%s' % (json.dumps(default_load_curve)))
        model = json.loads(json_txt)

        get_model_validator().validate(model)
        self.assertEqual(model['full_load_curve'], default_load_curve)



if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()