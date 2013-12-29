'''
Created on 29 Dec 2013

@author: ankostis
'''
import unittest
import json
from wltcg import Model
import jsonschema


class Test(unittest.TestCase):


    def testEmptyModel(self):
        json_txt = '''{
        }'''
        json_input = json.loads(json_txt)

        self.assertRaises(jsonschema.ValidationError, Model.Model, json_input)

    def testGoodVehicle(self):
        json_txt = '''{
            "mass":5,
            "p_rated":5,
            "n_rated":5,
            "p_max":5,
            "n_idle":5,
            "n_min":5,
            "gear_ratios":[5, 5, 6],
            "ngears":[1, 2, 3],
            "resistance_coeffs":[1, 2, 3],
            "full_load_curve":[1, 2, 3]
        }'''
        json_input = json.loads(json_txt)

        Model.Model(json_input)




if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()