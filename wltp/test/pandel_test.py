#!/usr/bin/env python
#
# Copyright 2013-2014 European Commission (JRC);
# Licensed under the EUPL (the 'Licence');
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at: http://ec.europa.eu/idabc/eupl
from jsonschema.exceptions import ValidationError

import unittest
import numpy.testing as npt

import pandas as pd
from wltp import pandel

from ..experiment import Experiment
from .goodvehicle import goodVehicle


class Test(unittest.TestCase):


    def test_ModelMaker_merge(self):
        class MyMaker(pandel.Pandel):
            def _get_json_schema(self, is_prevalidation):
                return {
                    '$schema': 'http://json-schema.org/draft-04/schema#',
                    'type': ['object', 'DataFrame'],
                    'required': [] if is_prevalidation else ['a', 'b'],
                    'properties': {
                        'a': {'type': ['number', 'array']},
                        'b': {'type': ['number', 'array']},
                        'c': {'type': ['number', 'array']},
                    }
                }

        ## Maps
        mm = MyMaker(None)

        (s1, s2) = {'a': 1}, {'a':2}
        mdl = mm._clone_and_merge_submodels(s1, s2)
        self.assertEqual(mdl['a'], 2)

        (s1, s2) = {'a': 1, 'b': 2}, {'a':11, 'c': 3}
        mdl = mm._clone_and_merge_submodels(s1, s2)
        self.assertEqual(mdl['a'], 11)
        self.assertEqual(mdl['b'], 2)
        self.assertEqual(mdl['c'], 3)

        ## DataFranes
        (s1, s2) = pd.DataFrame({'a': [1,2], 'b': [3,4]}), {'a':[11,22], 'c': [5,6]}
        mdl = mm._clone_and_merge_submodels(s1, s2)
        npt.assert_array_equal(mdl['a'], [11,22])
        npt.assert_array_equal(mdl['b'], [3, 4])
        npt.assert_array_equal(mdl['c'], [5, 6])

        ## Series
        (s1, s2) = pd.Series({'a': 1, 'b': 3}), {'a':11, 'c': 5}
        mdl = mm._clone_and_merge_submodels(s1, s2)
        self.assertEqual(mdl['a'], 11)
        self.assertEqual(mdl['b'], 3)
        self.assertEqual(mdl['c'], 5)

        ## Sequences
        l2 = [4,5]
        (s1, s2) = [1,2,3], l2
        mdl = mm._clone_and_merge_submodels(s1, s2)
        npt.assert_array_equal(mdl, l2)

        ## Sequences-->Map
        l2 = [4,5, {'a':11, 'c':33}]
        (s1, s2) = [1,2,{'a':1, 'b':2}], l2
        mdl = mm._clone_and_merge_submodels(s1, s2)
        npt.assert_array_equal(mdl, l2)
        obj = mdl[2]
        self.assertEqual(obj['a'], 11)
        self.assertEqual(obj['c'], 33)
        self.assertTrue('b' not in obj)

        ## Map-->Sequence
        l2 = [4,5, {'a':11, 'c':3}]
        (s1, s2) = {'a':1, 'b':[1,2]}, {'b': l2, 'c':3}
        mdl = mm._clone_and_merge_submodels(s1, s2)
        self.assertEqual(mdl['a'], 1)
        self.assertEqual(mdl['c'], 3)
        npt.assert_array_equal(mdl['b'], l2)

        ## Map-->Map
        (s1, s2) = {'a':1, 'b':{'aa':-1, 'bb':-2}, 'c':3}, {'a': 11, 'b':{'aa':-11, 'cc':-33}, 'd':44}
        mdl = mm._clone_and_merge_submodels(s1, s2)
        self.assertEqual(mdl['a'], 11)
        self.assertEqual(mdl['c'], 3)
        self.assertEqual(mdl['d'], 44)
        self.assertEqual(mdl['b'], {'aa':-11, 'bb':-2, 'cc':-33})



    def test_ModelMaker_build(self):
        class MyMaker(pandel.Pandel):
            def _get_json_schema(self, is_prevalidation):
                return {
                    '$schema': 'http://json-schema.org/draft-04/schema#',
                    'required': [] if is_prevalidation else ['a', 'b'],
                    'properties': {
                        'a': {'type': 'string'},
                        'b': {'type': 'number'},
                        'c': {'type': 'number'},
                    }
                }

        mm = MyMaker([
           {'a': 'foo', 'b': 1},
           {'a': 'bar', 'c': 2},
        ])
        mdl = mm.build()

        self.assertEqual(mdl['a'], 'bar')
        self.assertEqual(mdl['b'], 1)
        self.assertEqual(mdl['c'], 2)


        mm = MyMaker([{'a': 'foo', 'b': 'string'}])     ## Invalid submodel['b'], must be a number
        self.assertRaisesRegex(ValidationError, "Failed validating 'type' in schema\['properties']\['b']", mm.build)




if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
