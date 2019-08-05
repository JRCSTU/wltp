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

from wltp import model

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
            model.validate_model(mdl, iter_errors=False)
            consume_errs(model.validate_model(mdl, iter_errors=True))
            model.validate_model(mdl, additional_properties=False)
            model.validate_model(mdl, additional_properties=True)
            consume_errs(
                model.validate_model(mdl, iter_errors=True, additional_properties=True)
            )
            consume_errs(
                model.validate_model(mdl, iter_errors=True, additional_properties=False)
            )
            model.validate_model(mdl, iter_errors=False, additional_properties=True)
            model.validate_model(mdl, iter_errors=False, additional_properties=False)
        except:
            print("Model failed: ", mdl)
            raise

    def checkModel_invalid(self, mdl):
        ex = jsonschema.ValidationError
        try:
            self.assertRaises(ex, model.validate_model, mdl, iter_errors=False)
            errs = list(model.validate_model(mdl, iter_errors=True))
            self.assertGreater(len(errs), 0, errs)
            self.assertRaises(
                ex, model.validate_model, mdl, additional_properties=False
            )
            self.assertRaises(ex, model.validate_model, mdl, additional_properties=True)
            errs = list(
                model.validate_model(mdl, iter_errors=True, additional_properties=True)
            )
            self.assertGreater(len(errs), 0, errs)
            errs = list(
                model.validate_model(mdl, iter_errors=True, additional_properties=False)
            )
            self.assertGreater(len(errs), 0, errs)
            self.assertRaises(
                ex,
                model.validate_model,
                mdl,
                iter_errors=False,
                additional_properties=True,
            )
            self.assertRaises(
                ex,
                model.validate_model,
                mdl,
                iter_errors=False,
                additional_properties=False,
            )
        except:
            print("Model failed: ", mdl)
            raise

    def test_validate_wltc_data(self):
        mdl = model.get_model_base()
        mdl = model.merge(mdl, goodVehicle())
        validator = model.model_validator(validate_wltc_data=True, validate_schema=True)

        validator.validate(mdl)

    def test_wltc_validate_class_parts(self):
        wltc = model._get_wltc_data()

        for cl, cd in wltc["classes"].items():
            cycle = cd["cycle"]
            parts = model.get_class_parts_limits(cl, edges=True)
            prev_start = -1
            for start in parts:
                assert 0 <= start <= len(cycle)
                assert prev_start < start

                prev_start = start
            assert prev_start == len(cycle)

    def test_wltc_validate_checksums(self):
        wltc = model._get_wltc_data()

        for cl, cd in wltc["classes"].items():
            cycle = np.array(cd["cycle"])
            numsum = cycle.sum()
            checksum = cd["checksum"]
            self.assertAlmostEqual(numsum, checksum)

            parts = model.get_class_parts_limits(cl)
            cycle_parts = np.split(cycle, parts)
            for partnum, (pchk, cpart) in enumerate(
                zip(cd["part_checksums"], cycle_parts)
            ):
                self.assertAlmostEqual(
                    pchk, cpart.sum(), msg=f"class={cl}, partnum={partnum}"
                )

    def testModelBase_plainInvalid(self):
        mdl = model.get_model_base()
        model.upd_default_load_curve(mdl)

        self.checkModel_invalid(mdl)

    def testModelBase_fullValid(self):
        bmdl = model.get_model_base()
        json_txt = self.goodVehicle_jsonTxt % ("")
        mdl = json.loads(json_txt)
        bmdl.update(goodVehicle())

        self.checkModel_valid(bmdl)

    def testModelInstance_missingLoadCurve(self):
        json_txt = self.goodVehicle_jsonTxt % ("")
        mdl = json.loads(json_txt)
        validator = model.model_validator()

        self.assertRaisesRegex(
            jsonschema.ValidationError,
            "'wot' is a required property",
            validator.validate,
            mdl,
        )

    def testModelInstance_simplInstanceeFullLoadCurve(self):
        mdl = model.get_model_base()
        mdl.update(goodVehicle())
        mdl.update(
            {
                "wot": [
                    [1, 1, 1, 1, 1, 1, 1, 1, 1],
                    [0.23, 0.23, 0.23, 0.23, 0.23, 0.23, 0.23, 0.23, 0.23],
                ]
            }
        )

        model.model_validator().validate(mdl)
        dwot = model.upd_default_load_curve({})["wot"]

        self.assertNotEqual(mdl["wot"], dwot)

    def testModelInstance_defaultLoadCurve(self):
        mdl = model.get_model_base()
        mdl.update(goodVehicle())
        model.upd_default_load_curve(mdl)

        validator = model.model_validator()
        validator.validate(mdl)

        model.upd_default_load_curve(mdl, "diesel")

        validator = model.model_validator()
        validator.validate(mdl)

    def testFullLoadCurve_valid(self):
        import numpy as np
        import pandas as pd

        flc = np.array([[0.01, 0.5, 1, 1.2], [0.11, 0.77, 1, 0.88]])
        cases = [
            flc.tolist(),
            flc.T.tolist(),
            flc,
            flc.T,
            {"n_norm": flc[0], "p_norm": flc[1]},
            {
                "n_norm": flc[0],
                "p_norm": flc[1],
                "foo": [1, 2, 3, 4],
                "bar": [0, 0, 0, 4],
            },
            {
                "foo": [1, 2, 3, 4],
                "bar": [0, 0, 0, 0],
                "n_norm": flc[0],
                "p_norm": flc[1],
            },
            {
                "foo": [1, 2, 3, 4],
                "n_norm": flc[0],
                "bar": [0, 0, 0, 0],
                "p_norm": flc[1],
            },
            pd.Series(flc[1], index=flc[0]),
            pd.DataFrame({"n_norm": flc[0], "p_norm": flc[1]}),
            pd.DataFrame(
                {
                    "n_norm": flc[0],
                    "p_norm": flc[1],
                    "foo": [1, 2, 3, 4],
                    "bar": [0, 0, 0, 0],
                }
            ),
            pd.DataFrame(
                {
                    "foo": [1, 2, 3, 4],
                    "bar": [0, 0, 0, 0],
                    "n_norm": flc[0],
                    "p_norm": flc[1],
                }
            ),
            pd.DataFrame(
                {
                    "foo": [1, 2, 3, 4],
                    "n_norm": flc[0],
                    "bar": [0, 0, 0, 0],
                    "p_norm": flc[1],
                }
            ),
        ]

        for c in cases:
            mdl = goodVehicle()
            mdl = model.merge(model.get_model_base(), mdl)
            mdl["wot"] = c
            self.checkModel_valid(mdl)

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
            mdl = model.get_model_base()
            mdl = model.merge(model.get_model_base(), mdl)
            mdl["wot"] = c
            self.checkModel_invalid(mdl)

    def test_default_resistance_coeffs_missing(self):
        mdl = goodVehicle()
        mdl = model.merge(model.get_model_base(), mdl)
        self.checkModel_valid(mdl)

    def test_default_resistance_coeffs_None(self):
        mdl = goodVehicle()
        mdl["resistance_coeffs"] = None
        mdl = model.merge(model.get_model_base(), mdl)
        self.checkModel_valid(mdl)

    def test_fields_array_or_single_like_gears_SingleNumber(self):
        from pandalone.pandata import set_jsonpointer

        mdl = goodVehicle()
        ngears = len(mdl["gear_ratios"])
        fields_array_or_single_like_gears = [
            # JsonPath                   Values,                    AllowNone
            ("/n_min", [300, [350] * ngears], True),
            ("/f_safety_margin", [3.14, [5.0] * ngears], False),
        ]
        for (field, values, allowNone) in fields_array_or_single_like_gears:
            for value in values if not allowNone else values + [None]:
                mdl = goodVehicle()
                set_jsonpointer(mdl, field, value)
                mdl = model.merge(model.get_model_base(), mdl)
                self.checkModel_valid(mdl)

            ## Check len(gear) mismatch
            #
            mdl = goodVehicle()
            set_jsonpointer(mdl, field, [0.354] * (ngears + 1))
            mdl = model.merge(model.get_model_base(), mdl)
            self.checkModel_invalid(mdl)


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
