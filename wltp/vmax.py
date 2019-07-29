#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2019 European Commission (JRC);
# Licensed under the EUPL (the 'Licence');
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at: http://ec.europa.eu/idabc/eupl

import itertools as itt
import logging
from collections import namedtuple
from typing import List, Union

import numpy as np
import pandas as pd
from pandalone import mappings, pandata
from scipy import interpolate, optimize

from .utils import make_xy_df

log = logging.getLogger(__name__)

#: column names
c = mappings.Pstep()
v_decimals = 1
_v_step = 10 ** -v_decimals


#: Solution results of the equation finding the v-max of each gear:
#:   - v_max: in kmh, or np.NAN if not found
#:   - g_max: the number of the gear producing v_max
#:   - wot: intermediate curves for solving the equation
VMaxRec = namedtuple("VMaxRec", "v_max  g_max determined_by_n_lim  wot")


def _interpolate_wot_on_v_grid(wot: pd.DataFrame):
    """Return a new linearly interpolated df on v with v_decimals. """
    from .formulae import round1

    V, N = wot[c.v], wot[c.n]

    ## Clip grid inside min/max of wot(N).
    #
    v_wot_min = round1(V.min(), v_decimals)
    if v_wot_min < V.min():
        v_wot_min += _v_step
    #
    v_wot_max = round1(V.max(), v_decimals) + _v_step
    if v_wot_max > V.max():
        v_wot_max -= _v_step

    V_grid = np.arange(v_wot_min, v_wot_max + _v_step, _v_step)

    Spline = interpolate.InterpolatedUnivariateSpline
    rank = 1

    def interp(C):
        return Spline(V, C, k=rank)(V_grid)

    wot = pd.DataFrame({name: interp(vals) for name, vals in wot.iteritems()})
    wot.index = wot[c.v]

    return wot


def _find_p_remain_root(wot: pd.DataFrame) -> VMaxRec:
    """
    Find the velocity (the "x") where `p_remain` (the "y") down-crosses zero,
    
    rounded towards the part of wot where p_remain > 0
    (like MSAccess in e.g. `F new vehicle.form.vbs#L3273`)
    or v @ max p_wot, if p_remain is always positive.

    :param wot: 
        grid-interpolated df indexed by v with (at least): n, v, p_remain
    :return:
        a :class:`VMaxRec` with v_max in kmh or np.NAN
    """
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
        roots = wot.index[wot[c.zero_crosings] < 0]
        # ... and capture v @ lowest of them (where p_remain is either 0 or still positive)

        if roots.size > 0:
            v_max = roots[0]
            assert (
                wot.loc[v_max, c.p_remain].squeeze() > 0
                and wot.loc[
                    v_max + 0.9 * _v_step : v_max + 1.1 * _v_step, c.p_remain
                ].squeeze()
                <= 0
            ), (wot.loc[v_max - 1 : v_max + 1, c.p_remain], v_max)

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
    from . import formulae

    wot[c.v] = wot.index / n2v
    wot[c.p_road_loads] = formulae.calc_road_load_power(wot[c.v], f0, f1, f2)
    wot[c.p_remain] = wot[c.p_avail] - wot[c.p_road_loads]
    grid_wot = _interpolate_wot_on_v_grid(wot)
    return _find_p_remain_root(grid_wot)._replace(g_max=g)


def calc_v_max(
    mdl: dict,
    Pwots: Union[pd.Series, pd.DataFrame],
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

    def _package_wots_df(gear_wot_dfs):
        wots_df = pd.concat((df for df in gear_wot_dfs), axis=1, keys=range(ng, 0, -1))
        # Restore n column lost above.
        wots_df[c.n] = wots_df.index

        return wots_df

    wot = make_xy_df(Pwots, xname=c.n, yname=c.p_wot, auto_transpose=True)
    wot[c.n] = wot.index
    wot[c.p_avail] = wot[c.p_wot] * (1.0 - f_safety_margin)

    ## Scan gears from highest only if
    #  TODO: apply selective logic for ng-x gears from Heinz-DB?
    #
    rec_prev = rec_vmax = None
    recs: List[VMaxRec] = []
    loop_gears = list(reversed(list(enumerate(gear_n2v_ratios[1:], 2))))
    for g, n2v in loop_gears[:4]:
        rec = _calc_gear_v_max(g, wot.copy(), n2v, f0, f1, f2)
        recs.append(rec)
        if rec_prev and not np.isnan(rec.v_max) and rec.v_max <= rec_prev.v_max:
            rec_vmax = rec_prev
            break
        rec_prev = rec

    gear_wots_df = _package_wots_df([r.wot for r in recs])
    if rec_vmax:
        return rec_vmax._replace(wot=gear_wots_df)
    return VMaxRec(np.NAN, np.NAN, False, gear_wots_df)
