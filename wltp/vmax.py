#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2019 European Commission (JRC);
# Licensed under the EUPL (the 'Licence');
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at: http://ec.europa.eu/idabc/eupl

import logging
from collections import namedtuple
from typing import List, Union
from pandalone import mappings
import numpy as np
import pandas as pd
from scipy import interpolate, optimize

from .utils import make_xy_df


log = logging.getLogger(__name__)

#: column names
c = mappings.Pstep()

#: Solution results of the equation finding the v-max of each gear:
#:   - v_max, p_max: in kmh, kW, `Nan` if not found
#:   - optimize_result: the ``scipy.optimize.root`` result structure
#:   - wot: intermediate curves for solving the equation
GearVMaxRec = namedtuple("GearVMaxRec", "v_max  p_max  optimize_result  wot")
#: Global resulta for v-max.
#:   - v_max, p_max: in kmh, kW, `Nan` if not found
#:   - gears_df: intermediate scalars related to each gear (scalar-item x gear)
#:   - wots_df: intermediate curves for solving each gear equation (N x (gear, curve))
#:     with mult-indexed columns.  Gear-0 contains the common columns.
VMaxRec = namedtuple("VMaxRec", "v_max  p_max  gears_df  wots_df")


def _interpolate_wot_on_v_grid(pv: pd.DataFrame):
    from .formulae import round1

    v_decimals = 1
    step = 10 ** -v_decimals
    V = pv[c.v]

    ## Clip grid inside min/max of wot(N).
    #
    v_wot_min = round1(V.min(), v_decimals)
    if v_wot_min < pv[c.n].min():
        v_wot_min += step
    #
    v_wot_max = round1(V.max(), v_decimals) + step
    if v_wot_max > pv[c.n].max():
        v_wot_max -= step

    V_grid = np.arange(v_wot_min, v_wot_max, step)
    #  To interpolate on grid points, must keep the original data-points.
    new_v_index = np.unique(np.append(V, V_grid))

    pv = (
        pv.set_index(c.v, drop=False).reindex(new_v_index)
        ## No need for `limit_direction="both"` kw,
        # to extrapolate point before min wot(N),
        # grid has already been clipped inside min/max wot(N), above.
        .interpolate()
    )

    return pv.reindex(V_grid)


def _find_p_remain_root(wot: pd.DataFrame) -> optimize.OptimizeResult:
    """
    Find the velocity (the "x") where power (the "y") gets to zero.

    :param wot: 
        df with: n, v, p_remain
    :return:
        optimization result (structure)
    """
    wot = _interpolate_wot_on_v_grid(wot)
    assert not wot.isnull().any(None), wot[wot.isnull()]

    wot[c.sign_p_remain] = np.sign(wot[c.p_remain])

    ## period=-1: diff with next-element so zero-crossing is marked on low-index
    #  (e.g. `F new vehicle.form.vbs#L3273`).
    wot[c.zero_crosings] = wot[c.sign_p_remain].diff(periods=-1).fillna(0)
    # assert (wot[c.zero_crosings] <= 0).all(), wot.loc[wot[c.zero_crosings] > 0, c.zero_crosings]

    roots = wot.index[wot[c.zero_crosings] != 0]
    has_root = roots.size > 0
    x = roots[0] if has_root else np.NAN
    res = optimize.OptimizeResult(
        {"x": x, "success": has_root, "status": None, "message": None, "nit": -1}
    )

    return res


def _calc_gear_v_max(g, wot: pd.DataFrame, n2v, f0, f1, f2) -> GearVMaxRec:
    """
    The `v_max` for a gear `g` is the solution of :math:`0.1 * P_{avail}(g) = P_{road_loads}`.

    :param df:
        A dataframe containing at least `c.p_avail` column in kW,
        indexed by N in min^-1.
        NOTE: the power must already have been **reduced** by safety-margin,
        
        .. attention:: it appends columns in this dataframe.
        
    :param n2v:
        The n/v ratio as defined in Annex 1-2 for the gear to 
        calc its `v_max` (if it exists). 
    :return:
        a :class:`GearVMaxRec` namedtuple.

    """
    from . import formulae

    wot[c.v] = wot.index / n2v
    wot[c.p_road_loads] = formulae.calc_road_load_power(wot[c.v], f0, f1, f2)
    wot[c.p_remain] = wot[c.p_avail] - wot[c.p_road_loads]
    res = _find_p_remain_root(wot)

    v_max = np.NAN
    if res.success:
        n = res.x * n2v
        if wot.index.min() <= n <= wot.index.max():
            v_max = res.x
        elif n > wot.index.max():
            v_max = wot.index.max() / n2v

    return GearVMaxRec(v_max, -1, res, wot)


def calc_v_max(
    Pwots: Union[pd.Series, pd.DataFrame], gear_n2v_ratios, f0, f1, f2, f_safety_margin
) -> VMaxRec:
    """
    Finds the maximum velocity achieved by all gears.

    :param Pwots:
        A a 2D-matrix(lists/numpy), dict, df(1-or-2 cols) or series 
        containing the corresponding P(kW) value for each N in its index,
        or a 2-column matrix. 
    :param gear_n2v_ratios:
        A sequence of n/v ratios, as defined in Annex 1-2.e.
        It's length defines the number of gears to process.
    :return:
        a :class:`VMaxRec` namedtuple.
    """
    ng = len(gear_n2v_ratios)

    def _drop_maxv_common_columns(dfs):
        for df in dfs:
            df.drop(columns=[c.p_wot, c.p_avail], inplace=True)

    def _package_gears_df(v_maxes, p_maxes, optimize_results):
        """note: each arg is a list of items"""
        items1 = pd.DataFrame.from_dict({"v_max": v_maxes, "p_max": p_maxes})
        items2 = pd.DataFrame.from_records(optimize_results)[
            ["success", "status", "message", "nit"]
        ]
        items2.columns = "solver_ok solver_status solver_msg solver_nit".split()
        return pd.concat((items1, items2), axis=1)

    def _package_wots_df(wot, solution_dfs):
        _drop_maxv_common_columns(solution_dfs)
        wots_df = pd.concat(solution_dfs, axis=1, keys=range(0, ng + 1))
        wot[c.n] = wot.index
        ###wots_df.index = wot.values

        return wots_df

    wot = make_xy_df(Pwots, xname=c.n, yname=c.p_wot, auto_transpose=True)
    wot[c.n] = wot.index
    wot[c.p_avail] = wot[c.p_wot] * (1.0 - f_safety_margin)

    recs: List[GearVMaxRec] = []
    for g, n2v in reversed(list(enumerate(gear_n2v_ratios, 1))):
        rec = _calc_gear_v_max(g, wot.copy(), n2v, f0, f1, f2)
        if not recs or recs[-1].v_max < rec.v_max:
            recs.append(rec)

    *gears_infos, wot_solution_dfs = zip(*recs)

    gears_df = _package_gears_df(*gears_infos)
    wots_df = _package_wots_df(wot, wot_solution_dfs)
    v_max = gears_df["v_max"].max()
    p_max = gears_df["p_max"].max()

    return VMaxRec(v_max, p_max, gears_df, wots_df)
