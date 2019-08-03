#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2019 European Commission (JRC);
# Licensed under the EUPL (the 'Licence');
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at: http://ec.europa.eu/idabc/eupl

import logging
from collections import namedtuple
from contextvars import ContextVar
from typing import List, Union

import numpy as np
import pandas as pd

from pandalone import mappings, pandata

from . import io as wio
from . import power, pwot
from .invariants import v_decimals, v_step, vround

log = logging.getLogger(__name__)

#: column names as contextvar,
#: that client code can change momentarily with::
#:
#:     with utils.ctxtvar(<this_module>.cols):
#:         ...
cols: ContextVar = wio.pstep_ctxvar(__name__)


#: Solution results of the equation finding the v-max of each gear:
#:   - v_max: in kmh, or np.NAN if not found
#:   - g_max: the number of the gear producing v_max
#:   - wot: intermediate curves for solving the equation
VMaxRec = namedtuple("VMaxRec", "v_max  g_max determined_by_n_lim  wot")


def _find_p_remain_root(wot: pd.DataFrame) -> VMaxRec:
    """
    Find the velocity (the "x") where `p_remain` (the "y") down-crosses zero,
    
    rounded towards the part of wot where p_remain > 0
    (like MSAccess in e.g. `F new vehicle.form.vbs#L3273`)
    or v @ max p_wot, if p_remain is always positive.

    :param wot: 
        grid-interpolated df indexed by v with (at least): p_remain
    :return:
        a :class:`VMaxRec` with v_max in kmh or np.NAN
    """
    c = cols.get()

    assert not wot.empty
    assert not wot.isnull().any(None), wot[wot.isnull()]
    assert (wot.index == wot[c.v]).all(), wot.loc[wot.index != wot[c.v], :]

    determined_by_n_lim = False
    if (wot[c.p_remain] > 0).all():
        v_max = wot.index[-1]  # v @ max n
        determined_by_n_lim = True
    else:
        v_max = np.NAN
        ## Zero-crossings of p_remain are marked as sign-changes,
        #  particularly interested in "down-crosses":
        #   -1: drop from positive to 0 (perfect match!)
        #   -2: drop from positive to negative
        wot[c.sign_p_remain] = np.sign(wot[c.p_remain])

        ## diff-periods:
        #   ofs=+1: diff with prev-element so zero-crossing is marked on high-index (after cross)
        #   ofs=-1: diff with next-element so zero-crossing is marked on low-index (before cross)
        #  (e.g. `F new vehicle.form.vbs#L3273`).
        #  - Multiplied to preserve sign of down-crossing, for inequality further below.
        #  - Apply `fillna()`` bc `diff()` leaves one period at head or tail.
        #
        offs = -1
        wot[c.zero_crosings] = offs * wot[c.sign_p_remain].diff(periods=offs).fillna(0)
        # ... search for down-crossings only.
        roots_head = wot.index[wot[c.zero_crosings] < 0]
        # ... and capture v @ lowest of them (where p_remain is either 0 or still positive)
        if roots_head.size > 0:
            v_max = roots_head[0]  # Plain rounding, alreaydy close to grid.
            assert v_max == vround(v_max), (v_max, vround(v_max))
            _i = wot.loc[roots_head[0] :, c.p_remain].iteritems()
            assert next(_i)[1] > 0 and next(_i)[1] <= 0, (
                "Solution is not the last positive p_remain:",
                roots_head[0],
                v_max,
                wot.loc[v_max - 5 * v_step : v_max + 5 * v_step, c.p_remain],
            )

    return VMaxRec(v_max, None, determined_by_n_lim, wot)


def _calc_gear_v_max(g, wot: pd.DataFrame, n2v, f0, f1, f2) -> VMaxRec:
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
        a :class:`VMaxRec` namedtuple.

    """
    c = cols.get()

    wot[c.v] = wot.index / n2v
    wot[c.p_road_loads] = power.calc_road_load_power(wot[c.v], f0, f1, f2)
    wot[c.p_remain] = wot[c.p_avail] - wot[c.p_road_loads]
    grid_wot = pwot.interpolate_wot_on_v_grid(wot)
    return _find_p_remain_root(grid_wot)._replace(g_max=g)


def calc_v_max(
    mdl: dict,
    wot: Union[pd.Series, pd.DataFrame],
    gear_n2v_ratios,
    f0,
    f1,
    f2,
    f_safety_margin,
) -> VMaxRec:
    """
    Finds the maximum velocity achieved by all gears.

    :param mdl: 
        store solution wot (see code where)
    :param wot:
        A a 2D-matrix(lists/numpy), dict, df(1-or-2 cols) or series 
        containing the corresponding P(kW) value for each N in its index,
        or a 2-column matrix. 
    :param gear_n2v_ratios:
        A sequence of n/v ratios, as defined in Annex 1-2.e.
        It's length defines the number of gears to process.
    :return:
        a :class:`VMaxRec` namedtuple.
    """
    c = cols.get()

    ng = len(gear_n2v_ratios)

    def _package_wots_df(gear_wot_dfs):
        assert gear_wot_dfs

        ## Merge all index values into the index of the 1st DF,
        #  or else, themerged-df contains n-gear dupes in each index-value.
        #
        # first_df, *rest_dfs = gear_wot_dfs
        # full_index = np.unique(np.hstack(df.index for df in gear_wot_dfs))
        # first_df = first_df.reindex(full_index)
        # wots_df = pd.concat(
        #     [first_df] + rest_dfs,
        #     axis=1,
        #     join="inner",
        wots_df = pd.concat(
            gear_wot_dfs,
            axis=1,
            keys=wio.gear_names(range(ng, ng - len(gear_wot_dfs) - 1, -1)),
            names=["gear", "wot_item"],
            verify_integrity=True,
        )

        return wots_df

    wot = wio.make_xy_df(wot, xname=c.n, yname=c.p_wot, auto_transpose=True)
    wot[c.n] = wot.index
    wot[c.p_avail] = wot[c.p_wot] * (1.0 - f_safety_margin)

    ## Scan gears from high --> low-4 but stop at most on 2nd gear.
    #  TODO: apply selective logic for ng-x gears from Heinz-DB?
    #
    rec_prev = rec_vmax = None
    recs: List[VMaxRec] = []
    gears_from_top = list(reversed(list(enumerate(gear_n2v_ratios, 1))))
    ## Exclude 1st gear and stop on 4th gear from top (as per GTR).
    gears_to_scan = gears_from_top[:-1][:4]
    for g, n2v in gears_to_scan:
        rec = _calc_gear_v_max(g, wot.copy(), n2v, f0, f1, f2)
        recs.append(rec)
        ## It is `<=`` in Heinz-db.
        if rec_prev and not np.isnan(rec.v_max) and rec.v_max <= rec_prev.v_max:
            rec_vmax = rec_prev
            break
        rec_prev = rec

    gear_wots_df = _package_wots_df([r.wot for r in recs])
    if rec_vmax:
        return rec_vmax._replace(wot=gear_wots_df)
    raise ValueError("Cannot find v_max!\n  Insufficient power??", gear_wots_df, wot)
