#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2019-2020 European Commission (JRC);
# Licensed under the EUPL (the 'Licence');
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at: http://ec.europa.eu/idabc/eupl

import functools as fnt
import logging
import random

import numpy as np
import numpy.testing as npt
import pandas as pd
import pytest
from pandas import IndexSlice as _ix
from toolz import dicttoolz as dtz

from graphtik import compose, operation
from wltp import downscale, engine
from wltp import io as wio
from wltp import pipelines, vehicle, vmax

from . import goodvehicle, vehdb

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)


def _calc_v_max_manual(props, wot, n2vs):
    gwots = engine.interpolate_wot_on_v_grid(wot, n2vs)
    gwots = engine.attach_p_avail_in_gwots(gwots, f_safety_margin=0.1)
    gwots["p_resist"] = vehicle.calc_p_resist(
        gwots.index, props["f0"], props["f1"], props["f2"]
    )
    return vmax.calc_v_max(gwots)


def _calc_v_max_pipelined(props, wot, n2vs):
    pipe = pipelines.vmax_pipeline()
    calc_v_max_op = pipe.find_op_by_name("calc_v_max")
    res = pipe.compute(
        {
            "wot": wot,
            "n2v_ratios": n2vs,
            "f_safety_margin": 0.1,
            "f0": props["f0"],
            "f1": props["f1"],
            "f2": props["f2"],
        },
        outputs=calc_v_max_op.provides,
    )
    assert list(res) == ["v_max", "n_vmax", "g_vmax", "is_n_lim_vmax", "vmax_gwot"]
    assert [op.name for op in res.executed] == [
        "interpolate_wot_on_v_grid",
        "calc_p_resist",
        "attach_p_avail_in_gwots",
        "calc_v_max",
    ]
    ## Restore renamed graphtik-renamed deps.
    #
    renames = {
        "is_n_lim_vmax": "is_n_lim",
        "vmax_gwot": "wot",
    }
    res = dtz.keymap(lambda k: renames.get(k, k), res)
    rec = vmax.VMaxRec(**res)

    return rec


@pytest.fixture(params=[_calc_v_max_manual, _calc_v_max_pipelined])
def v_max_calculator(request):
    return request.param


def test_v_max_goodvehicle(v_max_calculator):
    props = goodvehicle.goodVehicle()
    wot = props["wot"]
    wot = engine.preproc_wot(props, wot)
    vmax_rec = v_max_calculator(props, wot, props["n2v_ratios"])
    vmax_rec[:4] == (190.3, 6089.6, 6, False)


def test_v_max_vehdb(h5_accdb, vehnums_to_run, v_max_calculator):
    from . import conftest

    # DEBUG: to reduce clutter in the console.
    # vehnums_to_run = 12
    # DEBUG: to study buggy cars.
    # vehnums_to_run = [76]   # diff det_by_nlim
    # vehnums_to_run = [3, 21, 22, 104, ]  # diff gear
    # vehnums_to_run = [38]  # diff vmax order higher 1st
    # vehnums_to_run = [31]  # [23]

    def make_v_maxes(vehnum):
        props, wot, n2vs = vehdb.load_vehicle_accdb(h5_accdb, vehnum)

        wot = wot.rename({"Pwot": "p"}, axis=1)
        wot["n"] = wot.index
        rec = v_max_calculator(props, wot, n2vs)

        return (props["v_max"], rec.v_max, props["gear_v_max"], rec.g_vmax, rec.wot)

    def _package_wots_df(gear_wot_dfs):
        assert gear_wot_dfs

        ## Merge all index values into the index of the 1st DF,
        #  or else, themerged-df contains n-gear dupes in each index-value.
        #
        # first_df, *rest_dfs = gear_wot_dfs.values()
        # full_index = np.unique(np.hstack(df.index for df in gear_wot_dfs))
        # first_df = first_df.reindex(full_index)
        wots_df = pd.concat(
            # [first_df] + rest_dfs,
            gear_wot_dfs.values(),
            axis=1,
            # join="inner",
            keys=wio.gear_names(gear_wot_dfs.keys()),
            names=["item", "gear"],
            verify_integrity=True,
        )

        return wots_df

    recs = [make_v_maxes(vehnum) for vehnum in vehnums_to_run]
    vehres = pd.DataFrame(
        recs,
        columns="vmax_accdb  vmax_python  gmax_accdb  gmax_python  wot".split(),
        index=wio.veh_names(vehnums_to_run),
    ).astype({"gmax_accdb": "Int64", "gmax_python": "Int64"})

    wots_df = pd.concat(
        vehres["wot"].values, keys=wio.veh_names(vehnums_to_run), names=["vehicle"]
    )
    vehres = vehres.drop("wot", axis=1)

    vehres["vmax_diff"] = (vehres["vmax_python"] - vehres["vmax_accdb"]).abs()
    vehres["gmax_diff"] = (vehres["gmax_python"] - vehres["gmax_accdb"]).abs()
    with pd.option_context(
        "display.max_rows",
        130,
        "display.max_columns",
        20,
        "display.width",
        120,
        # "display.precision",
        # 4,
        # "display.chop_threshold",
        # 1e-8,
        "display.float_format",
        "{:0.2f}".format,
    ):
        print(
            f"++ nones: {vehres.vmax_python.sum()} (out of {len(vehnums_to_run)})"
            f"\n++++\n{vehres}"
            # f"\n++++\n{wots_df.sample(80, axis=0)}"
        )
    with pd.option_context(
        "display.max_columns",
        20,
        "display.width",
        120,
        "display.float_format",
        "{:0.4f}".format,
    ):
        print(f"\n++++\n{vehres.describe().T}")
    vehres = vehres.dropna(axis=1)
    # npt.assert_array_equal(vmaxes["vmax_python"], vmaxes["vmax_accdb"])
    aggregate_tol = 1e-4  # The digits copied from terminal.
    assert (
        vehres["vmax_diff"].describe()
        - [125.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000]
        < aggregate_tol
    ).all()
    assert (
        vehres["gmax_diff"].describe()
        - [125.0000, 0.1040, 0.3552, 0.0000, 0.0000, 0.0000, 0.0000, 2.0000]
        < aggregate_tol
    ).all()
    assert (vehres["vmax_diff"] == 0).sum() == len(vehnums_to_run) and (
        vehres["gmax_diff"] == 0
    ).sum() == len(vehnums_to_run)
