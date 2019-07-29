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

from wltp import formulae, vmax

from . import vehdb

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)


def test_v_max(h5db):
    from wltp import formulae
    from . import conftest

    # DEBUG: reduce clutter in console.
    veh_samples = None  # [23]

    def make_v_maxes(vehnum, mdl: dict):
        iprops, Pwot, n2vs = conftest._load_vehicle_data(h5db, vehnum)
        rec = vmax.calc_v_max(
            mdl, Pwot["Pwot"], n2vs, iprops.f0, iprops.f1, iprops.f2, 0.1
        )

        return (
            iprops["v_max"],
            rec.v_max,
            iprops["ng_vmax"],
            rec.g_max,
            bool(iprops["vmax_determined_by_n_lim"]),
            rec.determined_by_n_lim,
            rec.wot,
        )

    veh_nums = vehdb.all_vehnums(h5db)
    if not isinstance(veh_samples, (list, tuple)):
        veh_samples = random.sample(veh_nums, veh_samples) if veh_samples else veh_nums

    recs = [make_v_maxes(vehnum, {}) for vehnum in veh_samples]
    vmaxes = pd.DataFrame(
        recs,
        columns="vmax_Heinz vmax_python gmax_Heinz gmax_python det_by_nlim_Heinz det_by_nlim_python wot".split(),
        index=veh_samples,
    ).astype({"gmax_Heinz": "Int64", "gmax_python": "Int64"})

    wots_df = pd.concat(
        vmaxes["wot"].values, keys=[f"v{i}" for i in veh_samples], names=["vehicle"]
    )
    vmaxes = vmaxes.drop("wot", axis=1)

    vmaxes["vmax_diff"] = (vmaxes["vmax_python"] - vmaxes["vmax_Heinz"]).abs()
    vmaxes["gmax_diff"] = (vmaxes["gmax_python"] - vmaxes["gmax_Heinz"]).abs()
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
            f"++ nones: {vmaxes.vmax_python.sum()} (out of {len(veh_samples)})"
            f"\n++++\n{vmaxes}"
        )
    with pd.option_context(
        "display.max_columns",
        20,
        "display.width",
        120,
        "display.float_format",
        "{:0.4f}".format,
    ):
        print(f"\n++++\n{vmaxes.describe()}")
    npt.assert_array_equal(vmaxes["vmax_python"], vmaxes["vmax_Heinz"])
    # assert vmaxes["vmax_diff"].mean() < 0.11 and vmaxes["vmax_diffs"].max() <= 1.5
    assert vmaxes["gmax_diff"].mean() == 0
