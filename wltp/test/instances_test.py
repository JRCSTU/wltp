#!/usr/bin/env python
#
# Copyright 2013-2014 European Commission (JRC);
# Licensed under the EUPL (the 'Licence');
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at: http://ec.europa.eu/idabc/eupl
'''Testing of the pure-tree data (just dictionary & lists), without the Model/Experiment classes.

:created: 29 Dec 2013
'''

import json
import jsonschema
import unittest

from wltp.test.goodvehicle import goodVehicle

from .. import model


class Test(unittest.TestCase):

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


    def testWltcData(self):
        mdl = model.wltc_data()
        validator = model.wltc_validator()

        validator.validate(mdl)


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
            (', "full_load_curve":%s' % (json.dumps(model.default_load_curve())))
        mdl = json.loads(json_txt)
        validator = model.model_validator()

        validator.validate(mdl)


    def testForcedCycle_valid(self):
        import numpy as np
        import pandas as pd
        cycles = [
            None,
            [1,2,3],
            np.array([5,6,7]),
            pd.Series([5,6,7]),
            pd.DataFrame({'v':[10,11,12]}),
            pd.DataFrame({'veloc':[10,11,12]}),
            pd.DataFrame({'v':[10,11,12], 'foo':[1,2,3]}),
            pd.DataFrame({'v':[100,200,300], 'altitude':[0,1,0]}),
            pd.DataFrame({'v':[101,201,301], 'altitude':[0,1,0], 'foo':[1,2,3], 'bar':[0,0,0], }),
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
            [[1,2,3],[4,5,6]],
            np.array([[1,2,3],[4,5,6]]),
            pd.DataFrame({'speed':[10,11,12], 'foo':[1,2,3]}),

            pd.DataFrame({'velocity':[100,200,300], 'alt':[0,1,0]}),

#             pd.Series([5,6,'a']),
        ]

        for c in cycles:
            mdl = model.model_base()
            mdl['vehicle'].update(goodVehicle()['vehicle'])

            mdl['params']['forced_cycle'] = c
            self.checkModel_invalid(mdl, ex=ValueError)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
