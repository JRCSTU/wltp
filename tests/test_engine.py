#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2013-2020 European Commission (JRC);
# Licensed under the EUPL (the 'Licence');
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at: http://ec.europa.eu/idabc/eupl
import itertools as itt
import re

import numpy as np
import pandas as pd
import pytest
from jsonschema import ValidationError
from numpy import testing as npt
from tests import goodvehicle, vehdb
import toolz.dicttoolz as dtz

from wltp import engine, invariants
from wltp import io as wio
from wltp import pipelines

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
    assert (got.to_numpy() == exp.to_numpy()).all(None)


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
    n_min_drive_set = None
    with pytest.raises(type(err), match=str(err)):
        for verr in engine.validate_wot(wot, n_idle, n_rated, p_rated, n_min_drive_set):
            raise verr

    n_min_drive_set = n_idle + 0.125 * (n_rated - n_idle)
    with pytest.raises(type(err), match=str(err)):
        for verr in engine.validate_wot(wot, n_idle, n_rated, p_rated, n_min_drive_set):
            raise verr

    ## Needs more tests.


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


def test_calc_p_available(h5_accdb, vehnums_to_run):
    def check_p_avail(case):
        _prop, wot, _n2vs = vehdb.load_vehicle_accdb(h5_accdb, case)

        p_avail = engine.calc_p_available(wot["Pwot"], 0.1, wot["ASM"])

        try:
            assert (p_avail - wot["Pavai"] < 1e-12).all()
        except Exception as ex:
            if isinstance(ex, AssertionError) and case == 48:
                print(f"Ignoring known BAD case {case} with ghost ASM.")
            else:
                raise

    for case in vehnums_to_run:
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
        n95 = engine.calc_n95(wot, props["n_rated"], props["p_rated"])
        results.append(n95)

    df = pd.DataFrame(results, columns=["n95_low", "n95_high"], dtype="float64")

    # print(df.describe().values)
    aggregate_tol = 1e-4  # The digits copied from terminal.
    exp = np.array(
        [
            [116.0, 116.0],
            [3656.11189008, 4784.66622629],
            [1337.23040635, 1428.79658641],
            [1680.0, 2897.4405215],
            [2837.63712814, 3750.68145459],
            [3215.01884177, 4142.35055724],
            [4512.5, 6000.03571429],
            [7843.72440418, 8817.60270757],
        ]
    )
    assert (df.describe().values - exp < aggregate_tol).all(None)


@pytest.mark.parametrize(
    "start, end, nsamples",
    [(1, 2, 11), (1, 10, 91), (1.23, 1.44, 2), (1.29, 1.45, 2), (1.201, 1.46, 2)],
)
def test_make_v_grid(start, end, nsamples):
    grid = engine._make_v_grid(start, end)
    assert len(grid) == nsamples
    npt.assert_allclose(grid, invariants.vround(grid))


def test_interpolate_wot_on_v_grid(h5_accdb, vehnums_to_run):
    def interpolate_veh(case):
        _prop, wot, n2vs = vehdb.load_vehicle_accdb(h5_accdb, case)

        wot = wot[["Pwot", "ASM"]]
        wot["n"] = wot.index

        return engine.interpolate_wot_on_v_grid(wot, n2vs)

    results = {wio.veh_name(case): interpolate_veh(case) for case in vehnums_to_run}
    df = pd.concat(
        results.values(),
        axis=0,
        keys=results.keys(),
        names=["vehicle", "v"],
        verify_integrity=True,
    )
    assert df.index.names == ["vehicle", "v"]
    assert (df.index.levels[0] == wio.veh_names(vehnums_to_run)).all()
    assert df.columns.names == ["item", "gear"]
    assert not (set("n Pwot ASM".split()) - set(df.columns.levels[0]))
    npt.assert_allclose(df.index.levels[1], invariants.vround(df.index.levels[1]))


def test_attach_p_avail_in_gwots_smoketest(h5_accdb):
    gwots = pd.DataFrame({("p", "g1"): [], ("ASM", "g1"): []})
    engine.attach_p_avail_in_gwots(gwots, f_safety_margin=0.1)


def test_n_max_pipeline():
    pipe = pipelines.n_max_pipeline()
    props = goodvehicle.goodVehicle()
    wot = engine.preproc_wot(props, props["wot"])
    sol = pipe.compute(
        {
            **dtz.keyfilter(lambda k: k in ("n_rated", "p_rated", "n2v_ratios"), props),
            "wot": wot,
            "cycle": {"V": pd.Series([120])},
            "v_max": 190.3,
            "g_vmax": 6,
        }
    )
    assert (
        list(sol)
        == """
        p_rated n_rated n2v_ratios wot cycle v_max g_vmax n2v_g_vmax
        n95_low n95_high n_max_cycle n_max_vehicle n_max
        """.split()
    )

    steps = [getattr(n, "name", n) for n in sol.plan.steps]
    steps_executed = [getattr(n, "name", n) for n in sol.executed]
    print(steps, steps_executed)
    exp_steps = "calc_n2v_g_vmax calc_n95 calc_n_max_cycle calc_n_max_vehicle calc_n_max".split()
    assert steps == steps_executed == exp_steps
