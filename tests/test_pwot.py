#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2013-2019 European Commission (JRC);
# Licensed under the EUPL (the 'Licence');
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at: http://ec.europa.eu/idabc/eupl
import numpy as np
import pandas as pd
from tests import vehdb

from wltp import pwot


def test_calc_n95(h5_accdb):
    results = []
    visited_wots = set()
    for case in vehdb.all_vehnums(h5_accdb):
        (props, wot, _a) = vehdb.load_vehicle_accdb_inputs(h5_accdb, case)
        vehnum = props["vehicle_no"]
        if vehnum in visited_wots:
            continue
        visited_wots.add(vehnum)

        props = props.rename({"idling_speed": "n_idle", "rated_speed": "n_rated"})
        wot = wot.rename({"Pwot": "p", "Pwot_norm": "p_norm"}, axis=1)
        wot["n"] = wot.index
        wot = pwot.pre_proc_wot(
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
