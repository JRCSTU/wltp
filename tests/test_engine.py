#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2013-2019 European Commission (JRC);
# Licensed under the EUPL (the 'Licence');
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at: http://ec.europa.eu/idabc/eupl
import itertools as itt
import re

import numpy as np
import pandas as pd
import pytest
from jsonschema import ValidationError
from tests import vehdb

from wltp import engine
from wltp import io as wio

_N = [500, 2000, 5000]
_P = [10, 78, 60]
_NP = np.array([_N, _P]).T


@pytest.fixture
def mdl():
    return dict(n_idle=500, n_rated=2000, p_rated=78)


@pytest.mark.parametrize(
    "xy",
    [
        _NP,
        _NP.T,
        _NP.tolist(),
        _NP.T.tolist(),
        pd.DataFrame(_NP),
        pd.DataFrame(_P, index=_N),
        pd.Series(dict(_NP.tolist())),
    ],
)
def test_preproc_wot_equals(mdl, xy):
    got = engine.preproc_wot(mdl, xy)
    assert isinstance(got, pd.DataFrame) and got.shape == (3, 4)
    got = got.reset_index(drop=True)
    exp = engine.preproc_wot(mdl, pd.DataFrame(_NP, columns=["n", "p"]))
    assert (got == exp).all(None)


@pytest.mark.parametrize(
    "wot, err",
    [
        (1, ValueError("DataFrame constructor not properly called!")),
        ([1, 2, 5], ValueError("Wot is missing one of: n")),
        ([[1], [2], [5]], ValueError("Wot is missing one of: n")),
        ([[1, 2, 5]], ValueError("Wot is missing one of: n")),
        ([[1, 2, 3], [3, 4, 5], [5, 6, 7]], ValueError("Wot is missing one of: n")),
        ({"p": _P}, ValueError("Wot is missing one of: n")),
        ({"p": _P, "other": _N}, ValueError("Wot is missing one of: n")),
        ({}, ValueError("Empty WOT:")),
        ((), ValueError("Empty WOT:")),
        ([], ValueError("Empty WOT:")),
        ([[]], ValueError("Empty WOT:")),
        ([[], []], ValueError("Empty WOT:")),
        (pd.DataFrame({"n": [1, 2, 3]}), ValueError("Wot is missing one of: p")),
        (pd.DataFrame({"n_norm": [1, 2, 3]}), ValueError("Wot is missing one of: p")),
        (
            pd.DataFrame({"p": [1, 2, 3], "extra": np.NAN}),
            ValueError("Wot is missing one of: n"),
        ),
        (
            pd.DataFrame({"a": [1, 2, 3], "b": [1, 2, 3]}),
            ValueError("Wot is missing one of: n"),
        ),
    ],
)
def test_parse_wot_errors(mdl, wot, err):
    with pytest.raises(type(err), match=str(err)):
        print(engine.parse_wot(wot))


@pytest.mark.parametrize(
    "wot, n_idle, n_rated, p_rated, err",
    [
        # ([[1, 2], [3, 4]], None, None, None, ValueError("Too few points in wot")),
        (
            {"p": _P, "n": _N},
            None,
            None,
            92,
            ValidationError(re.escape("`p_wot_max`(78) much lower than p_rated(92)!")),
        ),
        (
            {"p": _P, "n": _N},
            None,
            None,
            22,
            ValidationError(re.escape("`p_wot_max`(78) much bigger than p_rated(22)!")),
        ),
    ],
)
def test_validate_wot_errors(mdl, wot, n_idle, n_rated, p_rated, err):
    wot = engine.parse_wot(wot)
    if n_idle is None:
        n_idle = mdl["n_idle"]
    if n_rated is None:
        n_rated = mdl["n_rated"]
    if p_rated is None:
        p_rated = mdl["p_rated"]
    wot = engine.denorm_wot(wot, n_idle, n_rated, p_rated)
    wot = engine.norm_wot(wot, n_idle, n_rated, p_rated)
    with pytest.raises(type(err), match=str(err)):
        for err in engine.validate_wot(wot, n_idle, n_rated, p_rated):
            raise err


@pytest.mark.parametrize(
    "wot",
    [
        {"p": _P, "n": _N},
        pd.DataFrame({"p": _P}, index=_N),
        pd.DataFrame({"p_norm": [0.1, 1, 0.8]}, index=_N),
        pd.DataFrame({"p": _P}, index=_N),
        pd.DataFrame({"p": _P, "n_norm": [0.1, 1, 1.3]}),
        pd.DataFrame({"n": [700, 2000, 5000], "p_norm": [0.1, 1, 0.8], "extra": 0}),
        pd.Series(_P, name="p", index=_N),
        pd.Series([0.1, 1, 0.8], name="p_norm", index=_N),
        pd.DataFrame({"p_norm": [0.1, 1, 0.8], "extra": 0, "extra2": 0}, index=_N),
        pd.DataFrame({"p": _P, "n": _N, "extr": 0}).set_index("n"),
        # pd.DataFrame(
        #     {"p": _P, "n_norm": [0.1, 1, 1.3], "extr": 0, "extr2": 1}
        # ).set_index("n_norm"),
    ],
)
def test_pre_proc_high_level(mdl, wot):
    engine.preproc_wot(mdl, wot)


def test_calc_p_available(h5_accdb):
    def check_p_avail(case):
        _prop, wot, _n2vs = vehdb.load_vehicle_accdb(h5_accdb, case)

        p_avail = engine.calc_p_available(wot["Pwot"], wot["ASM"], 0.1)

        try:
            assert (p_avail - wot["Pavai"] < 1e-12).all()
        except Exception as ex:
            if isinstance(ex, AssertionError) and case == 48:
                print(f"Ignoring known BAD case {case} with ghost ASM.")
            else:
                raise

    all_cases = vehdb.all_vehnums(h5_accdb)
    for case in all_cases:
        check_p_avail(case)


def test_calc_n95(h5_accdb):
    results = []
    visited_wots = set()
    for case in vehdb.all_vehnums(h5_accdb):
        (props, wot, _a) = vehdb.load_vehicle_accdb(h5_accdb, case)
        vehnum = props["vehicle_no"]
        if vehnum in visited_wots:
            continue
        visited_wots.add(vehnum)

        props = props.rename(
            {
                "idling_speed": "n_idle",
                "rated_speed": "n_rated",
                "rated_power": "p_rated",
            }
        )
        wot = wot.rename({"Pwot": "p", "Pwot_norm": "p_norm"}, axis=1)
        wot["n"] = wot.index
        wot = engine.preproc_wot(
            props.rename({"idling_speed": "n_idle", "rated_speed": "n_rated"}), wot
        )
        n95 = engine.calc_n95(wot, props["n_rated"])
        results.append(n95)

    df = pd.DataFrame(results, columns=["n95_low", "n95_high"], dtype="float64")

    aggregate_tol = 1e-4  # The digits copied from terminal.
    exp = np.array(
        [
            [116.000000, 114.000000],
            [3656.111890, 4735.274406],
            [1337.230406, 1381.795505],
            [1680.000000, 2897.440521],
            [2837.637128, 3750.681455],
            [3215.018842, 4141.843972],
            [4512.500000, 5902.652680],
            [7843.724404, 8817.602708],
        ]
    )
    assert (df.describe().values - exp < aggregate_tol).all(None)


def test_interpolate_wot_on_v_grid(h5_accdb):
    def interpolate_veh(case):
        _prop, wot, n2vs = vehdb.load_vehicle_accdb(h5_accdb, case)

        wot = wot[["Pwot", "ASM"]]
        wot["n"] = wot.index

        return engine.interpolate_wot_on_v_grid2(wot, n2vs)

    all_cases = vehdb.all_vehnums(h5_accdb)
    results = {wio.veh_name(case): interpolate_veh(case) for case in all_cases}
    df = pd.concat(
        results.values(),
        axis=0,
        keys=results.keys(),
        names=["vehicle", "v"],
        verify_integrity=True,
    )
    assert df.index.names == ["vehicle", "v"]
    assert (df.index.levels[0] == wio.veh_names(all_cases)).all()
    assert df.columns.names == ["gear", "wot_item"]
    assert not (set("n Pwot ASM".split()) - set(df.columns.levels[1]))


def test_n_mins_smoke():

    base = engine.calc_fixed_n_min_drives({}, 500, 4000)

    results = [base]
    for values in itt.product([None, 1], [None, 2], [None, 3], [None, 4]):
        mdl = dict(
            zip(
                (
                    "n_min_drive_up",
                    "n_min_drive_up_start",
                    "n_min_drive_down",
                    "n_min_drive_down_start",
                ),
                values,
            )
        )
        res = engine.calc_fixed_n_min_drives(mdl, 500, 4000)
        results.append(res)

    ## They must all produce diffetrent value.
    #
    for v1, v2 in itt.permutations(results, 2):
        assert v1 != v2
