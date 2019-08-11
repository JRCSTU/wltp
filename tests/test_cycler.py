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
from tests import vehdb

from wltp import cycler, datamodel, engine
from wltp.vehicle import calc_default_resistance_coeffs


@pytest.fixture
def gwots():
    ## Need a 2-level multiindex columns for swaplevel().
    return pd.DataFrame({("the items", "the gears"): []})


@pytest.mark.parametrize(
    "wltc_class, long_phase_duration", itt.product(range(4), (1, 2, 4))
)
def test_emerge_cycle_long_phase_duration_1_is_identical(
    wltc_class, long_phase_duration, gwots
):
    V = datamodel.get_class_v_cycle(wltc_class)
    cycle = cycler.emerge_cycle(
        V, V, V, gwots, long_phase_duration=1, up_threshold=-0.1389
    )
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
def test_emerge_cycle_long_phase_duration(wltc_class, long_phase_duration, exp, gwots):
    V = datamodel.get_class_v_cycle(wltc_class)
    cycle = cycler.emerge_cycle(
        V, V, V, gwots, long_phase_duration=long_phase_duration, up_threshold=-0.1389
    )
    missmatches = [
        (cycle[cname] != cycle[f"{cname}_long"]).sum()
        for cname in "stop acc cruise dec".split()
    ]
    # print(missmatches)
    assert missmatches == exp


@pytest.mark.parametrize("wltc_class, exp", [(0, 12), (1, 9), (2, 9), (3, 9)])
def test_emerge_cycle_init(wltc_class, exp, gwots):
    V = datamodel.get_class_v_cycle(wltc_class)
    cycle = cycler.emerge_cycle(
        V, V, V, gwots, long_phase_duration=2, up_threshold=-0.1389
    )
    assert cycle.init.sum() == exp


@pytest.mark.parametrize("wltc_class", range(4))
def test_emerge_cycle_concat_wots_smoketest(h5_accdb, wltc_class):
    prop, wot, n2vs = vehdb.load_vehicle_accdb(h5_accdb, 125)
    renames = vehdb.accdb_renames()
    prop = prop.rename(renames)
    wot = wot[["Pwot", "ASM"]].rename(renames, axis=1)
    wot["n"] = wot.index

    gwots = engine.interpolate_wot_on_v_grid2(wot, n2vs)
    assert (
        gwots.shape[0] > wot.shape[0] and gwots.shape[1] == len(n2vs) * wot.shape[1]
    ), f"\nwot:\n{wot}\ngwot:\n{gwots}"


def test_cycle_add_p_avail_for_gears_smoketest(h5_accdb):
    gwots = pd.DataFrame({("p", "g1"): [], ("ASM", "g1"): []})
    cycler.cycle_add_p_avail_for_gears(gwots, 1, SM=0.1)


def test_flatten_columns():
    cols = pd.MultiIndex.from_tuples([("a", "aa"), ("b", "")], names=("gear", "item"))
    fcols = cycler.flatten_cycle_columns(cols)
    infcols = cycler.inflate_cycle_columns(fcols)
    assert cols.equals(infcols)
    assert cols.names == infcols.names
    with pytest.raises(AssertionError, match="MultiIndex?"):
        cycler.inflate_cycle_columns(cols)
