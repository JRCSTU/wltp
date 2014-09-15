#!/usr/bin/env python
#-*- coding: utf-8 -*-
#
# Copyright 2013-2014 European Commission (JRC);
# Licensed under the EUPL (the 'Licence');
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at: http://ec.europa.eu/idabc/eupl
'''
Testing of the pure-tree data (just dictionary & lists), without the Model/Experiment classes.
'''

from __future__ import print_function, unicode_literals

import json
import unittest

import jsonschema
from jsonschema.exceptions import ValidationError

from .. import model
from .goodvehicle import goodVehicle


class InstancesTest(unittest.TestCase):

    def setUp(self):
        self.goodVehicle_jsonTxt = '''{"vehicle": {
            "unladen_mass":1230,
            "test_mass":   1300,
            "v_max":   195,
            "p_rated": 110.625,
            "n_rated": 5450,
            "n_idle":  950,
            "n_min":   500,
            "gear_ratios":[120.5, 75, 50, 43, 33, 28],
            "resistance_coeffs":[100, 0.5, 0.04]
            %s
        }}'''

    def checkModel_valid(self, mdl):
        def consume_errs(errs):
            for e in errs:
                self.assertIsNone(e, e)

        try:
            model.validate_model(mdl, iter_errors=False)
            consume_errs(model.validate_model(mdl, iter_errors=True))
            model.validate_model(mdl, additional_properties=False)
            model.validate_model(mdl, additional_properties=True)
            consume_errs(model.validate_model(mdl, iter_errors=True, additional_properties=True))
            consume_errs(model.validate_model(mdl, iter_errors=True, additional_properties=False))
            model.validate_model(mdl, iter_errors=False, additional_properties=True)
            model.validate_model(mdl, iter_errors=False, additional_properties=False)
        except:
            print('Model failed: ', mdl)
            raise

    def checkModel_invalid(self, mdl, ex=None):
        if not ex:
            ex = jsonschema.ValidationError
        try:
            self.assertRaises(ex, model.validate_model, mdl, iter_errors=False)
            errs = list(model.validate_model(mdl, iter_errors=True))
            self.assertGreater(len(errs), 0, errs)
            self.assertRaises(ex, model.validate_model, mdl, additional_properties=False)
            self.assertRaises(ex, model.validate_model, mdl, additional_properties=True)
            errs = list(model.validate_model(mdl, iter_errors=True, additional_properties=True))
            self.assertGreater(len(errs), 0, errs)
            errs = list(model.validate_model(mdl, iter_errors=True, additional_properties=False))
            self.assertGreater(len(errs), 0, errs)
            self.assertRaises(ex, model.validate_model, mdl, iter_errors=False, additional_properties=True)
            self.assertRaises(ex, model.validate_model, mdl, iter_errors=False, additional_properties=False)
        except:
            print('Model failed: ', mdl)
            raise


    def test_validate_wltc_data(self):
        wltc = model.wltc_data()
        validator = model.wltc_validator()

        validator.validate(wltc)

    def test_validate_class_parts(self):
        wltc = model.wltc_data()

        for cl, cd in wltc['classes'].items():
            cycle = cd['cycle']
            parts = cd['parts']
            prev_high = -1
            for i, (low, high) in enumerate(parts):
                self.assertLess(low, high, cl)
                self.assertLess(high, len(cycle), 'class(%s), part(%s)'%(cl, i))
                self.assertGreater(low, prev_high, cl)

                prev_high = high
            self.assertEqual(prev_high, len(cycle)-1)


    def testModelBase_plainInvalid(self):
        mdl = model.model_base()

        self.checkModel_invalid(mdl)

    def testModelBase_fullValid(self):
        bmdl = model.model_base()
        json_txt = self.goodVehicle_jsonTxt % ('')
        mdl = json.loads(json_txt)
        bmdl['vehicle'].update(goodVehicle()['vehicle'])

        self.checkModel_valid(bmdl)


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
            (', "full_load_curve":%s' % (model.json_dumps(model.default_load_curve())))
        mdl = json.loads(json_txt)
        validator = model.model_validator()

        validator.validate(mdl)


    def testFullLoadCurve_valid(self):
        import numpy as np
        import pandas as pd

        flc = np.array([[0.01,0.5,1,1.2], [0.11,0.77,1,0.88]])
        cases = [
            flc.tolist(),
            flc.T.tolist(),
            flc,
            flc.T,
            {'n_norm':flc[0], 'p_norm':flc[1]},
            {'n_norm':flc[0], 'p_norm':flc[1], 'foo':[1,2,3,4], 'bar':[0,0,0,4]},
            {'foo':[1,2,3,4], 'bar':[0,0,0,0], 'n_norm':flc[0], 'p_norm':flc[1]},
            {'foo':[1,2,3,4], 'n_norm':flc[0], 'bar':[0,0,0,0], 'p_norm':flc[1]},
            pd.Series(flc[1], index=flc[0]),
            pd.DataFrame({'n_norm':flc[0], 'p_norm':flc[1]}),
            pd.DataFrame({'n_norm':flc[0], 'p_norm':flc[1], 'foo':[1,2,3, 4], 'bar':[0,0,0,0]}),
            pd.DataFrame({'foo':[1,2,3,4], 'bar':[0,0,0,0], 'n_norm':flc[0], 'p_norm':flc[1]}),
            pd.DataFrame({'foo':[1,2,3,4], 'n_norm':flc[0], 'bar':[0,0,0,0], 'p_norm':flc[1]}),
        ]

        for c in cases:
            mdl = goodVehicle()
            mdl = model.merge(model.model_base(), mdl)
            mdl['vehicle']['full_load_curve'] = c
            self.checkModel_valid(mdl)


    def testFullLoadCurve_invalid(self):
        import numpy as np
        import pandas as pd
        cases = [
            None,
            [],
            {},
            [[1,2,3],[4,5,6]],
            np.array([[1,2,3],[4,5,6]]),
            pd.DataFrame({'speed':[10,11,12], 'foo':[1,2,3]}),

            pd.DataFrame({'velocity':[100,200,300], 'alt':[0,1,0]}),

#             pd.Series([5,6,'a']),
        ]

        for c in cases:
            mdl = model.model_base()
            mdl = model.merge(model.model_base(), mdl)
            del mdl['vehicle']['full_load_curve']
            mdl['vehicle']['full_load_curve'] = c
            self.checkModel_invalid(mdl, ex=ValidationError)


    def testForcedCycle_valid(self):
        import numpy as np
        import pandas as pd
        cycles = [
            None,
            [1,2,3],
            np.array([5,6,7]),
            pd.Series([5,6,7]),
            pd.DataFrame({'v':[10,11,12]}),
            pd.DataFrame({'foo':[10,11,12]}),
            pd.DataFrame({'v':[10,11,12], 'foo':[1,2,3]}),
            pd.DataFrame({'v':[100,200,300], 'altitude':[0,1,0]}),
            pd.DataFrame({'v':[101,201,301,401,402], 'altitude':[0,1,0,1,1], 'foo':[1,2,3,4,5], 'bar':[0,0,0,0,0], }),

            [[1,2,3],[4,5,6]],
            np.array([[1,2,3],[4,5,6]]),
            pd.DataFrame({'speed':[10,11,12], 'foo':[1,2,3]}),

            pd.DataFrame({'velocity':[100,200,300], 'alt':[0,1,0]}),

        ]

        for c in cycles:
            mdl = model.model_base()
            mdl['vehicle'].update(goodVehicle()['vehicle'])

            mdl['params']['forced_cycle'] = c
            self.checkModel_valid(mdl)

    def testForcedCycle_invalid(self):
        import numpy as np
        import pandas as pd
        cycles = [
            0,
            [[1,2,3], [4,5,6], [7,8,9]],
            np.array([1]),
            np.array([[1,2,3], [4,5,6], [7,8,9]]),
        ]

        for c in cycles:
            mdl = model.model_base()
            mdl['vehicle'].update(goodVehicle()['vehicle'])

            mdl['params']['forced_cycle'] = c
            self.assertRaises(ValidationError, model.validate_model, mdl, additional_properties=False)
            #self.checkModel_invalid(mdl, ex=ValidationError)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
