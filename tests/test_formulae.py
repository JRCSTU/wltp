#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2013-2019 European Commission (JRC);
# Licensed under the EUPL (the 'Licence');
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at: http://ec.europa.eu/idabc/eupl

import logging

import numpy as np
import numpy.testing as npt
import pandas as pd
import pytest

from wltp import experiment
from wltp import model
from wltp.formulae import calc_default_resistance_coeffs, downscale_class_velocity
from wltp.model import _get_wltc_data

logging.basicConfig(level=logging.DEBUG)


def test_smoke_downscaling():
    wclasses = _get_wltc_data()["classes"]
    test_data = [
        (pd.Series(wclass["cycle"]), wclass["downscale"]["phases"], f_downscale)
        for wclass in wclasses.values()
        for f_downscale in np.linspace(0.1, 1, 10)
    ]

    for (V, phases, f_downscale) in test_data:
        downscale_class_velocity(V, f_downscale, phases)


def testNparray2Bytes():
    arr = np.array([0, 9, 10, 36, 255 - experiment._escape_char])

    assert experiment.np2bytes(arr) == b"\x80\x89\x8a\xa4\xff"

    with pytest.raises(AssertionError, match="Outside byte-range"):
        experiment.np2bytes(arr + 1)

    with pytest.raises(AssertionError, match="Outside byte-range"):
        experiment.np2bytes(arr - 1)

    npt.assert_array_equal(experiment.bytes2np(experiment.np2bytes(arr)), arr)


def testRegex2bytes():
    regex = br"\g1\g0\g24\g66\g127"

    assert experiment.gearsregex(regex).pattern == b"\x81\x80\x98\xc2\xff"

    regex = br"\g1\g0|\g24\g66\g127"

    assert experiment.gearsregex(regex).pattern == b"\x81\x80|\x98\xc2\xff"


def test_calc_default_resistance_coeffs():
    tm = 1000  # test_mass

    identity = (1, 0)
    res = calc_default_resistance_coeffs(tm, [identity] * 3)
    print(res)
    assert res == (tm, tm, tm)

    zero = (0, 0)
    res = calc_default_resistance_coeffs(tm, [zero] * 3)
    print(res)
    assert res == (0, 0, 0)

    a_num = 123
    replace = (0, a_num)
    res = calc_default_resistance_coeffs(tm, [replace] * 3)
    print(res)
    assert res == (a_num, a_num, a_num)


def test_calc_default_resistance_coeffs_base_model():
    tm = 1000  # test_mass

    bm = model._get_model_base()
    regression_curves = bm["params"]["resistance_coeffs_regression_curves"]
    res = calc_default_resistance_coeffs(tm, regression_curves)
    print(res)
    assert len(res) == 3
