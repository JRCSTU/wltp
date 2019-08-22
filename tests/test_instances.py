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

import io
import json
import unittest
from timeit import timeit

import jsonschema
import numpy as np
import numpy.testing as npt
import pandas as pd
import pytest
from jsonschema.exceptions import ValidationError
from pandas import IndexSlice as idx
from toolz import itertoolz as itz

from wltp import cycles, datamodel, utils

from .goodvehicle import goodVehicle


def _calc_wltc_checksums(offset, length, calc_sum=True):
    def calc_v_sums(V, prev=(0, 0)):
        v = V
        if (
            # If running for V (not VAs) ...
            length == 0
            # ... and cumulative from previous part
            and prev[0] != 0
        ):
            # Skip overlapping sample from 2nd part and on.
            v = V.iloc[1:]

        if prev is None:
            prev = (0, 0)

        if calc_sum:
            return (prev[0] + v.sum(), cycles.crc_velocity(v, prev[1], full=True))
        return (cycles.crc_velocity(v, prev[0], full=True),)

    results = []

    def calc_class_sums(cl):
        V = datamodel.get_class_v_cycle(cl)
        cycle_parts = datamodel.get_class_parts_limits(cl, edges=True)

        prev = (0, 0)
        for partno, (start, end) in enumerate(itz.sliding_window(2, cycle_parts)):
            start += offset
            end += offset + length
            sums = calc_v_sums(V.loc[start:end])
            cums = calc_v_sums(V.loc[start:end], prev)
            results.append((cl, f"part-{partno+1}", *sums, *cums))
            prev = cums

        return results

    for cl in datamodel.get_class_names():
        calc_class_sums(cl)

    columns = (
        "class part SUM CRC32 cum_SUM cum_CRC32"
        if calc_sum
        else "class part CRC32 cum_CRC32"
    )
    df = pd.DataFrame(results, columns=columns.split()).set_index(["class", "part"])

    return df


def test_wltc_checksums():
    """
    
    ... NOTE:: 
        The printouts in this TC generate the table 
        in :func:`wltp/cycles/cycles.cycle_checksums()`.
    """
    dfs_dict = {
        "V": _calc_wltc_checksums(0, 0),
        "V_A1": _calc_wltc_checksums(0, -1, calc_sum=False),
        "V_A2": _calc_wltc_checksums(1, 0, calc_sum=False),
    }

    dfs = pd.concat(dfs_dict.values(), keys=dfs_dict.keys(), axis=1)

    def as_csv_txt(dfs):
        sio = io.StringIO()
        dfs.to_csv(sio, sep="\t", float_format="%.1f")
        return "\n" + sio.getvalue()

    exp = cycles.cycle_checksums(full=True)

    ## UNCOMMENT this to printout CRCs.
    #
    # print(as_csv_txt(dfs))
    # print(as_csv_txt(exp))

    crc_idx = [1, 3, 4, 5, 6, 7]
    assert dfs.iloc[:, crc_idx].equals(exp.iloc[:, crc_idx])

    sum_idx = [0, 2]
    npt.assert_allclose(dfs.iloc[:, sum_idx], exp.iloc[:, sum_idx])


def test_indetify_checksums_works_with_all_CRCs():
    def run_assertions(crc):
        assert cycles.identify_cycle_v_crc(crc) == exp
        assert cycles.identify_cycle_v_crc(crc.lower()) == exp
        assert cycles.identify_cycle_v_crc(crc.upper()) == exp
        assert cycles.identify_cycle_v_crc(int(crc, 16)) == exp

    wltc_class = 0
    V = datamodel.get_class_v_cycle(wltc_class)
    crc = cycles.crc_velocity(V)
    exp = ("class1", None, "V")

    run_assertions(crc)

    crc = cycles.crc_velocity(V, full=True)
    run_assertions(crc)


@pytest.mark.parametrize(
    "wltc_class, exp",
    [
        (0, ("class1", None, "V")),
        (1, ("class2", None, "V")),
        (2, ("class3a", None, "V")),
        (3, ("class3b", None, "V")),
    ],
)
def test_full_cycles_in_wltc_checksums(wltc_class, exp):
    V = datamodel.get_class_v_cycle(wltc_class)
    assert cycles.identify_cycle_v(V) == exp


@pytest.mark.parametrize(
    "indexer, exp",
    [
        (idx[:1022], ("class1", "PART-2", "V")),
        (idx[:589], ("class1", "part-1", "V")),
        (idx[1:589], ("class1", "part-3", "V_A2")),  # 1st & 3rd parts are identical
        (idx[1:590], ("class1", "part-1", "V_A2")),
        (idx[1023:], ("class1", "part-3", "V_A2")),
        (idx[1:], ("class1", None, "V_A2")),
    ],
)
def test_identify_wltc_checksums(indexer, exp):
    V = datamodel.get_class_v_cycle(0)
    assert cycles.identify_cycle_v(V.loc[indexer]) == exp


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
            "f0": 100,
            "f1": 0.5,
            "f2": 0.04
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
            cycle = cd["v_cycle"]
            parts = datamodel.get_class_parts_limits(cl, edges=True)
            prev_start = -1
            for start in parts:
                assert 0 <= start <= len(cycle)
                assert prev_start < start

                prev_start = start
            assert prev_start == len(cycle)

    def test_wltc_validate_checksums(self):
        for cl in datamodel.get_class_names():
            ## Test below the helper api in datamodel.
            #
            cycle = datamodel.get_class_v_cycle(cl)
            cd = datamodel.get_class(cl)

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
        mdl["f0"] = mdl["f1"] = mdl["f1"] = None
        mdl = datamodel.merge(datamodel.get_model_base(), mdl)
        with pytest.raises(ValidationError, match="None is not of type 'number'"):
            self.checkModel_valid(mdl)


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
