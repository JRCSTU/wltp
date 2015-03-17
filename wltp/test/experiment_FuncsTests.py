#!/usr/bin/env python
#-*- coding: utf-8 -*-
#
# Copyright 2013-2014 European Commission (JRC);
# Licensed under the EUPL (the 'Licence');
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at: http://ec.europa.eu/idabc/eupl

from __future__ import division, print_function, unicode_literals

import logging
import unittest
from wltp import model

import numpy as np
import numpy.testing as npt
import wltp.experiment as cycgen

from ..experiment import downscaleCycle
from ..model import _get_wltc_data
from ..utils import assertRaisesRegex


class experimentFuncs(unittest.TestCase):
    def setUp(self):
        logging.basicConfig(level=logging.DEBUG)

    def testDownscaling(self):
        wclasses = _get_wltc_data()['classes']
        test_data = [(np.array(wclass['cycle']), wclass['downscale']['phases'], f_downscale)
                    for wclass in wclasses.values()
                    for f_downscale in np.linspace(0.1, 1, 10)]

        for (V, phases, f_downscale) in test_data:
            downscaleCycle(V, f_downscale, phases)


    def testNparray2Bytes(self):
        arr = np.array([0, 9, 10, 36, 255-cycgen._escape_char])

        self.assertEqual(cycgen.np2bytes(arr), b'\x80\x89\x8a\xa4\xff')
        assertRaisesRegex(self, AssertionError, 'Outside byte-range', cycgen.np2bytes, (arr + 1))
        assertRaisesRegex(self, AssertionError, 'Outside byte-range', cycgen.np2bytes, (arr - 1))

        npt.assert_array_equal(cycgen.bytes2np(cycgen.np2bytes(arr)), arr)


    def testRegex2bytes(self):
        regex = b'\g1\g0\g24\g66\g127'

        self.assertEqual(cycgen.gearsregex(regex).pattern,  b'\x81\x80\x98\xc2\xff')

        regex = b'\g1\g0|\g24\g66\g127'

        self.assertEqual(cycgen.gearsregex(regex).pattern,  b'\x81\x80|\x98\xc2\xff')

    def test_calc_default_resistance_coeffs(self):
        tm = 1000 # test_mass

        identity = (1,0)
        res = cycgen.calc_default_resistance_coeffs(tm, [identity]*3)
        print(res)
        self.assertEqual(res, (tm, tm, tm))

        zero = (0,0)
        res = cycgen.calc_default_resistance_coeffs(tm, [zero]*3)
        print(res)
        self.assertEqual(res, (0, 0, 0))

        a_num = 123
        replace = (0, a_num)
        res = cycgen.calc_default_resistance_coeffs(tm, [replace]*3)
        print(res)
        self.assertEqual(res, (a_num, a_num, a_num))


    def test_calc_default_resistance_coeffs_base_model(self):
        tm = 1000 # test_mass

        bm = model._get_model_base()
        regression_curves = bm['params']['resistance_coeffs_regression_curves']
        res = cycgen.calc_default_resistance_coeffs(tm, regression_curves)
        print(res)
        self.assertEqual(len(res), 3)

    def test_def_calcPower_available_power_margins__no_cold_reduction__single_pm_(self):
        t = np.arange(0, 1000, 100)
        gear_safety_margins = 0.9 
        p_avail_cold_reduce = None
        pm = cycgen.calcPower_available_power_margins(t, gear_safety_margins, p_avail_cold_reduce)
        self.assertEqual(pm.shape, (1, len(t)))

    def test_def_calcPower_available_power_margins__no_cold_reduction(self):
        t = np.arange(0, 1000, 100)
        ngears = 3
        gear_safety_margins = [0.9] * ngears 
        p_avail_cold_reduce = None
        pm = cycgen.calcPower_available_power_margins(t, gear_safety_margins, p_avail_cold_reduce)
        self.assertEqual(pm.shape, (ngears, len(t)))

    def test_def_calcPower_available_power_margins(self):
        t = np.arange(0, 1000, 100)
        ngears = 3
        gear_safety_margins = [0.9] * ngears 
        p_avail_cold_reduce = {
                'f_cold_margin': 0.3,
                'f_heating_rate': 0.01,
            }
        pm = cycgen.calcPower_available_power_margins(t, gear_safety_margins, p_avail_cold_reduce)
        self.assertEqual(pm.shape, (ngears, len(t)))
        print(pm)

if __name__ == "__main__":
    import sys
    unittest.main(verbosity=2, argv=sys.argv)
