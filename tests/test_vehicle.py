#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2013-2019 European Commission (JRC);
# Licensed under the EUPL (the 'Licence');
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at: http://ec.europa.eu/idabc/eupl
from wltp.vehicle import calc_default_resistance_coeffs
from wltp import datamodel


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

    bm = datamodel.get_model_base()
    datamodel.upd_resistance_coeffs_regression_curves(bm)
    regression_curves = bm["resistance_coeffs_regression_curves"]
    res = calc_default_resistance_coeffs(tm, regression_curves)
    print(res)
    assert len(res) == 3
