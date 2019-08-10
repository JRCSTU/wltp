#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2013-2019 European Commission (JRC);
# Licensed under the EUPL (the 'Licence');
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at: http://ec.europa.eu/idabc/eupl
import itertools as itt

import pandas as pd
import pytest

from wltp import cycler, datamodel
from wltp.vehicle import calc_default_resistance_coeffs


@pytest.mark.parametrize(
    "wltc_class, long_phase_duration", itt.product(range(4), (1, 2, 4))
)
def test_emerge_cycle_long_phase_duration_1_is_identical(
    wltc_class, long_phase_duration
):
    long_phase_duration = 1
    V = datamodel.get_class_v_cycle(wltc_class)
    cycle = cycler.emerge_cycle(V, pd.DataFrame([]), long_phase_duration)
    assert all(
        (cycle[cname] != cycle[f"{cname}_long"]).sum() == 0
        for cname in "stop acc cruise dec".split()
    )


@pytest.mark.parametrize(
    "wltc_class, long_phase_duration, exp",
    [
        # duration=2
        (0, 2, [0, 4, 29, 2]),
        (1, 2, [0, 4, 23, 1]),
        (2, 2, [0, 3, 34, 5]),
        (3, 2, [0, 0, 31, 4]),
        # duration=4
        (0, 4, [0, 4, 45, 2]),
        (1, 4, [0, 11, 45, 5]),
        (2, 4, [0, 15, 63, 19]),
        (3, 4, [0, 14, 62, 20]),
        # duration=7: stop must start to differ
        (3, 7, [10, 98, 66, 113]),
    ],
)
def test_emerge_cycle_long_phase_duration(wltc_class, long_phase_duration, exp):
    V = datamodel.get_class_v_cycle(wltc_class)
    cycle = cycler.emerge_cycle(V, pd.DataFrame([]), long_phase_duration)
    missmatches = [
        (cycle[cname] != cycle[f"{cname}_long"]).sum()
        for cname in "stop acc cruise dec".split()
    ]
    # print(missmatches)
    assert missmatches == exp


def test_flatten_columns():
    cols = pd.MultiIndex.from_tuples([("a", "aa"), ("b", "")], names=("gear", "item"))
    fcols = cycler.flatten_cycle_columns(cols)
    infcols = cycler.inflate_cycle_columns(fcols)
    assert cols.equals(infcols)
    assert cols.names == infcols.names
    with pytest.raises(AssertionError, match="MultiIndex?"):
        cycler.inflate_cycle_columns(cols)
