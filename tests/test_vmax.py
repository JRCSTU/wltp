#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2019 European Commission (JRC);
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

from wltp import engine, vehicle, downscale, vmax
from wltp.io import gear_names, veh_names

from . import vehdb

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)


def test_v_max(h5_accdb):
    from . import conftest

    veh_samples = None
    # DEBUG: to reduce clutter in the console.
    # veh_samples = 12
    # DEBUG: to study buggy cars.
    # veh_samples = [76]   # diff det_by_nlim
    # veh_samples = [3, 21, 22, 104, ]  # diff gear
    # veh_samples = [38]  # diff vmax order higher 1st
    # veh_samples = [31]  # [23]

    def make_v_maxes(vehnum):
        props, wot, n2vs = vehdb.load_vehicle_accdb(h5_accdb, vehnum)
        wot = wot.rename({"Pwot": "p"}, axis=1)
        wot["n"] = wot.index
        gwots = engine.interpolate_wot_on_v_grid(wot, n2vs)
        gwots = engine.calc_p_avail_in_gwots(gwots, SM=0.1)
        p_resist = vehicle.calc_road_load_power(
            gwots.index, props.f0, props.f1, props.f2
        )
        rec = vmax.calc_v_max(gwots, p_resist)

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
            keys=gear_names(gear_wot_dfs.keys()),
            names=["item", "gear"],
            verify_integrity=True,
        )

        return wots_df

    veh_nums = vehdb.all_vehnums(h5_accdb)
    if not isinstance(veh_samples, (list, tuple)):
        veh_samples = random.sample(veh_nums, veh_samples) if veh_samples else veh_nums

    recs = [make_v_maxes(vehnum) for vehnum in veh_samples]
    vehres = pd.DataFrame(
        recs,
        columns="vmax_Heinz  vmax_python  gmax_Heinz  gmax_python  wot".split(),
        index=veh_names(veh_samples),
    ).astype({"gmax_Heinz": "Int64", "gmax_python": "Int64"})

    wots_df = pd.concat(
        vehres["wot"].values, keys=veh_names(veh_samples), names=["vehicle"]
    )
    vehres = vehres.drop("wot", axis=1)

    vehres["vmax_diff"] = (vehres["vmax_python"] - vehres["vmax_Heinz"]).abs()
    vehres["gmax_diff"] = (vehres["gmax_python"] - vehres["gmax_Heinz"]).abs()
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
            f"++ nones: {vehres.vmax_python.sum()} (out of {len(veh_samples)})"
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
    # npt.assert_array_equal(vmaxes["vmax_python"], vmaxes["vmax_Heinz"])
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
    assert (vehres["vmax_diff"] == 0).sum() == 125 and (
        vehres["gmax_diff"] == 0
    ).sum() == 119
