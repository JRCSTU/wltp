#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2013-2019 European Commission (JRC);
# Licensed under the EUPL (the 'Licence');
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at: http://ec.europa.eu/idabc/eupl
"""
Testing of the pure-tree data (just dictionary & lists), without the Model/Experiment classes.
"""

import json
from wltp import utils
import unittest
from timeit import timeit

import jsonschema
import numpy as np
import pandas as pd
from jsonschema.exceptions import ValidationError

from wltp import datamodel
from .goodvehicle import goodVehicle


class InstancesTest(unittest.TestCase):
    def setUp(self):
        self.goodVehicle_jsonTxt = """{
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
        }"""

    def checkModel_valid(self, mdl):
        def consume_errs(errs):
            for e in errs:
                self.assertIsNone(e, e)

        try:
            datamodel.validate_model(mdl, iter_errors=False)
            consume_errs(datamodel.validate_model(mdl, iter_errors=True))
            datamodel.validate_model(mdl, additional_properties=False)
            datamodel.validate_model(mdl, additional_properties=True)
            consume_errs(
                datamodel.validate_model(
                    mdl, iter_errors=True, additional_properties=True
                )
            )
            consume_errs(
                datamodel.validate_model(
                    mdl, iter_errors=True, additional_properties=False
                )
            )
            datamodel.validate_model(mdl, iter_errors=False, additional_properties=True)
            datamodel.validate_model(
                mdl, iter_errors=False, additional_properties=False
            )
        except:
            print("Model failed: ", mdl)
            raise

    def checkModel_invalid(self, mdl):
        ex = jsonschema.ValidationError
        try:
            self.assertRaises(ex, datamodel.validate_model, mdl, iter_errors=False)
            errs = list(datamodel.validate_model(mdl, iter_errors=True))
            self.assertGreater(len(errs), 0, errs)
            self.assertRaises(
                ex, datamodel.validate_model, mdl, additional_properties=False
            )
            self.assertRaises(
                ex, datamodel.validate_model, mdl, additional_properties=True
            )
            errs = list(
                datamodel.validate_model(
                    mdl, iter_errors=True, additional_properties=True
                )
            )
            self.assertGreater(len(errs), 0, errs)
            errs = list(
                datamodel.validate_model(
                    mdl, iter_errors=True, additional_properties=False
                )
            )
            self.assertGreater(len(errs), 0, errs)
            self.assertRaises(
                ex,
                datamodel.validate_model,
                mdl,
                iter_errors=False,
                additional_properties=True,
            )
            self.assertRaises(
                ex,
                datamodel.validate_model,
                mdl,
                iter_errors=False,
                additional_properties=False,
            )
        except:
            print("Model failed: ", mdl)
            raise

    def test_validate_wltc_data(self):
        mdl = datamodel.get_model_base()
        mdl = datamodel.merge(mdl, goodVehicle())
        validator = datamodel.model_validator(
            validate_wltc_data=True, validate_schema=True
        )

        validator.validate(mdl)

    def test_wltc_validate_class_parts(self):
        wltc = datamodel.get_wltc_data()

        for cl, cd in wltc["classes"].items():
            cycle = cd["cycle"]
            parts = datamodel.get_class_parts_limits(cl, edges=True)
            prev_start = -1
            for start in parts:
                assert 0 <= start <= len(cycle)
                assert prev_start < start

                prev_start = start
            assert prev_start == len(cycle)

    def test_wltc_validate_checksums(self):
        wltc = datamodel.get_wltc_data()

        for cl, cd in wltc["classes"].items():
            cycle = np.array(cd["cycle"])
            numsum = cycle.sum()
            checksum = cd["checksum"]
            self.assertAlmostEqual(numsum, checksum)

            parts = datamodel.get_class_parts_limits(cl)
            cycle_parts = np.split(cycle, parts)
            for partnum, (pchk, cpart) in enumerate(
                zip(cd["part_checksums"], cycle_parts)
            ):
                self.assertAlmostEqual(
                    pchk, cpart.sum(), msg=f"class={cl}, partnum={partnum}"
                )

    def testModelBase_plainInvalid(self):
        mdl = datamodel.get_model_base()
        datamodel.upd_default_load_curve(mdl)

        self.checkModel_invalid(mdl)

    def testModelInstance_missingLoadCurve(self):
        json_txt = self.goodVehicle_jsonTxt % ("")
        mdl = json.loads(json_txt)
        validator = datamodel.model_validator()

        self.assertRaisesRegex(
            jsonschema.ValidationError,
            "'wot' is a required property",
            validator.validate,
            mdl,
        )

    def testModelInstance_simplInstanceeFullLoadCurve(self):
        mdl = datamodel.get_model_base()
        mdl.update(goodVehicle())
        mdl.update(
            {
                "wot": [
                    [1, 1, 1, 1, 1, 1, 1, 1, 1],
                    [0.23, 0.23, 0.23, 0.23, 0.23, 0.23, 0.23, 0.23, 0.23],
                ]
            }
        )

        datamodel.model_validator().validate(mdl)
        dwot = datamodel.upd_default_load_curve({})["wot"]

        self.assertNotEqual(mdl["wot"], dwot)

    def testModelInstance_defaultLoadCurve(self):
        mdl = datamodel.get_model_base()
        mdl.update(goodVehicle())
        datamodel.upd_default_load_curve(mdl)

        validator = datamodel.model_validator()
        validator.validate(mdl)

        datamodel.upd_default_load_curve(mdl, "diesel")

        validator = datamodel.model_validator()
        validator.validate(mdl)

    def testFullLoadCurve_invalid(self):
        import numpy as np
        import pandas as pd

        cases = [
            None,
            [],
            {},
            [[1, 2, 3], [4, 5, 6]],
            np.array([[1, 2, 3], [4, 5, 6]]),
            pd.DataFrame({"speed": [10, 11, 12], "foo": [1, 2, 3]}),
            pd.DataFrame({"velocity": [100, 200, 300], "alt": [0, 1, 0]}),
            #             pd.Series([5,6,'a']),
        ]

        for c in cases:
            mdl = datamodel.get_model_base()
            mdl = datamodel.merge(datamodel.get_model_base(), mdl)
            mdl["wot"] = c
            self.checkModel_invalid(mdl)

    def test_default_resistance_coeffs_missing(self):
        mdl = goodVehicle()
        mdl = datamodel.merge(datamodel.get_model_base(), mdl)
        self.checkModel_valid(mdl)

    def test_default_resistance_coeffs_None(self):
        mdl = goodVehicle()
        mdl["resistance_coeffs"] = None
        mdl = datamodel.merge(datamodel.get_model_base(), mdl)
        self.checkModel_valid(mdl)


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
