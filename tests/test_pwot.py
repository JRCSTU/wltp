#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2013-2019 European Commission (JRC);
# Licensed under the EUPL (the 'Licence');
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at: http://ec.europa.eu/idabc/eupl
import re

import numpy as np
import pandas as pd
import pytest
from tests import vehdb

from wltp import pwot

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
    got = pwot.preproc_wot(mdl, xy)
    assert isinstance(got, pd.DataFrame) and got.shape == (3, 4)
    got = got.reset_index(drop=True)
    exp = pwot.preproc_wot(mdl, pd.DataFrame(_NP, columns=["n", "p"]))
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
        print(pwot.parse_wot(wot))


@pytest.mark.parametrize(
    "wot, n_idle, n_rated, p_rated, err",
    [
        # ([[1, 2], [3, 4]], None, None, None, ValueError("Too few points in wot")),
        (
            {"p": _P, "n": _N},
            None,
            None,
            100,
            ValueError(re.escape("wot(P) much lower than p_rated(100)!")),
        ),
        (
            {"p": _P, "n": _N},
            None,
            None,
            20,
            ValueError(re.escape("wot(P) much bigger than p_rated(20)!")),
        ),
    ],
)
def test_validate_wot_errors(mdl, wot, n_idle, n_rated, p_rated, err):
    if n_idle is not None:
        mdl["n_idle"] = n_idle
    if n_rated is not None:
        mdl["n_rated"] = n_rated
    if p_rated is not None:
        mdl["p_rated"] = p_rated

    wot = pwot.parse_wot(wot)
    with pytest.raises(type(err), match=str(err)):
        print(pwot.validate_wot(mdl, wot))


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
    pwot.preproc_wot(mdl, wot)


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
        wot = pwot.preproc_wot(
            props.rename({"idling_speed": "n_idle", "rated_speed": "n_rated"}), wot
        )
        n95 = pwot.calc_n95(wot, props["n_rated"])
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
