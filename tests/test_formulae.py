#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2013-2019 European Commission (JRC);
# Licensed under the EUPL (the 'Licence');
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at: http://ec.europa.eu/idabc/eupl

import logging
import unittest

import numpy as np
import numpy.testing as npt
import pandas as pd

import wltp.experiment as ex
from wltp import model
from wltp.formulae import calc_default_resistance_coeffs, downscaleCycle
from wltp.model import _get_wltc_data


class experimentFuncs(unittest.TestCase):
    def setUp(self):
        logging.basicConfig(level=logging.DEBUG)

    def testDownscaling(self):
        wclasses = _get_wltc_data()["classes"]
        test_data = [
            (pd.Series(wclass["cycle"]), wclass["downscale"]["phases"], f_downscale)
            for wclass in wclasses.values()
            for f_downscale in np.linspace(0.1, 1, 10)
        ]

        for (V, phases, f_downscale) in test_data:
            downscaleCycle(V, f_downscale, phases)

    def testNparray2Bytes(self):
        arr = np.array([0, 9, 10, 36, 255 - ex._escape_char])

        self.assertEqual(ex.np2bytes(arr), b"\x80\x89\x8a\xa4\xff")
        self.assertRaisesRegex(
            AssertionError, "Outside byte-range", ex.np2bytes, (arr + 1)
        )
        self.assertRaisesRegex(
            AssertionError, "Outside byte-range", ex.np2bytes, (arr - 1)
        )

        npt.assert_array_equal(ex.bytes2np(ex.np2bytes(arr)), arr)

    def testRegex2bytes(self):
        regex = br"\g1\g0\g24\g66\g127"

        self.assertEqual(ex.gearsregex(regex).pattern, b"\x81\x80\x98\xc2\xff")

        regex = br"\g1\g0|\g24\g66\g127"

        self.assertEqual(ex.gearsregex(regex).pattern, b"\x81\x80|\x98\xc2\xff")

    def test_calc_default_resistance_coeffs(self):
        tm = 1000  # test_mass

        identity = (1, 0)
        res = calc_default_resistance_coeffs(tm, [identity] * 3)
        print(res)
        self.assertEqual(res, (tm, tm, tm))

        zero = (0, 0)
        res = calc_default_resistance_coeffs(tm, [zero] * 3)
        print(res)
        self.assertEqual(res, (0, 0, 0))

        a_num = 123
        replace = (0, a_num)
        res = calc_default_resistance_coeffs(tm, [replace] * 3)
        print(res)
        self.assertEqual(res, (a_num, a_num, a_num))

    def test_calc_default_resistance_coeffs_base_model(self):
        tm = 1000  # test_mass

        bm = model._get_model_base()
        regression_curves = bm["params"]["resistance_coeffs_regression_curves"]
        res = calc_default_resistance_coeffs(tm, regression_curves)
        print(res)
        self.assertEqual(len(res), 3)


if __name__ == "__main__":
    import sys

    unittest.main(verbosity=2, argv=sys.argv)
