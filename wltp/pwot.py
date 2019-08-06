#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2019 European Commission (JRC);
# Licensed under the EUPL (the 'Licence');
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at: http://ec.europa.eu/idabc/eupl

import logging
from typing import Tuple

import numpy as np
import pandas as pd
from scipy import interpolate, optimize

from . import io as wio
from .invariants import v_decimals, v_step, vround

log = logging.getLogger(__name__)


def denormalize_n(wot_df: pd.DataFrame, n_idle, n_rated):
    w = wio.pstep_factory.get().wot
    wot_df[w.n] = n_idle + (n_rated - n_idle) * wot_df[w.n_norm]
    return wot_df


def denormalize_p(wot_df: pd.DataFrame, p_rated):
    w = wio.pstep_factory.get().wot
    wot_df[w.p] = p_rated * wot_df[w.p_norm]
    return wot_df


def denorm_wot(mdl, wot_df: pd.DataFrame):
    c = wio.pstep_factory.get()
    w = wio.pstep_factory.get().wot

    if w.n not in wot_df:
        wot_df = denormalize_n(wot_df, mdl[c.n_idle], mdl[c.n_rated])
    if w.p not in wot_df:
        wot_df = denormalize_p(wot_df, mdl[c.p_rated])

    return wot_df


def normalize_n(wot_df: pd.DataFrame, n_idle, n_rated):
    w = wio.pstep_factory.get().wot
    wot_df[w.n_norm] = (wot_df[w.n] - n_idle) / (n_rated - n_idle)
    return wot_df


def normalize_p(wot_df: pd.DataFrame, p_rated):
    w = wio.pstep_factory.get().wot
    wot_df[w.p_norm] = wot_df[w.p] / p_rated
    return wot_df


def norm_wot(mdl, wot_df: pd.DataFrame):
    c = wio.pstep_factory.get()
    w = wio.pstep_factory.get().wot

    if w.n_norm not in wot_df:
        wot_df = normalize_n(wot_df, mdl[c.n_idle], mdl[c.n_rated])
    if w.p_norm not in wot_df:
        wot_df = normalize_p(wot_df, mdl[c.p_rated])

    return wot_df


def pre_proc_wot(mdl, wot) -> pd.DataFrame:
    """
    Make a df from 2D-matrix(lists/numpy), dict, df(1-or-2 cols) or series,

    ensuring the result wot contains one of `p`, `p_norm`, and `n`, `n_norm` columns.
    """
    w = wio.pstep_factory.get().wot

    input_was_pandas = isinstance(wot, (pd.DataFrame, pd.Series))
    if not isinstance(wot, pd.DataFrame):
        wot = pd.DataFrame(wot)

    if wot.empty:
        raise ValueError(f"Empty WOT: {mdl.get('wot')}!")

    if wot.shape[0] <= 2 and wot.shape[0] < wot.shape[1]:
        wot = wot.T

    ## Accept a 1-column df if column-names were unamed or one of the p columnns.
    #
    if (
        wot.shape[1] == 1
        and input_was_pandas
        and (wot.columns[0] == 0 or wot.columns[0] in (w.p, w.p_norm))
    ):
        if wot.columns[0] == 0:
            wot.columns = [w.p]
        wot[w.n] = wot.index
        wot = wot[wot.columns[::-1]]
        log.warning(
            "Assuming single-column WOT to be `%s` with index `%s`.", *wot.columns
        )
    elif wot.shape[1] == 2:
        ## Accept 2-columns if column-names were unamed.
        #
        if tuple(wot.columns) == (0, 1):
            wot.columns = [w.n, w.p]
            log.warning("Assuming the 2-column WOT to be: %s, %s", *wot.columns)

    if not any(c in wot.columns for c in [w.n, w.n_norm]):
        raise ValueError(f"Wot is missing one of: {w.n}, {w.n_norm}")
    if not any(c in wot.columns for c in [w.p, w.p_norm]):
        raise ValueError(f"Wot is missing one of: {w.p}, {w.p_norm}")

    wot = denorm_wot(mdl, wot)
    wot = norm_wot(mdl, wot)

    return wot


def interpolate_wot_on_v_grid(wot: pd.DataFrame):
    """Return a new linearly interpolated df on v with v_decimals. """
    w = wio.pstep_factory.get().wot

    assert wot.size, "Empty wot!"

    V = wot[w.v]

    ## Clip V-grid inside min/max of wot-N.
    #
    vmul = 10 ** v_decimals
    v_wot_min = vround(np.ceil(V.min() * vmul) / vmul)
    v_wot_max = vround(np.floor(V.max() * vmul) / vmul)

    ## Using np.arange() because np.linspace() steps are not reliably spaced,
    #  and apply the GTR-rounding.
    #
    V_grid = vround(np.arange(v_wot_min, v_wot_max, v_step))
    assert V_grid.size, ("Empty wot?", v_wot_min, v_wot_max)
    ## Add endpoint manually because np.arange() is not adding it reliably.
    #
    if V_grid[-1] != v_wot_max:
        V_grid = np.hstack((V_grid, [v_wot_max]))

    assert 0 <= V_grid[0] - V.min() < v_step, (
        "V-grid start below/too-far min(N_wot): ",
        V.min(),
        v_wot_min,
        V_grid[0:7],
        v_step,
    )
    assert 0 <= V.max() - V_grid[-1] < v_step, (
        "V-grid end above/too-far max(N_wot): ",
        V_grid[-7:],
        v_wot_max,
        V.max(),
        v_step,
    )

    def interp(C):
        return interpolate.interp1d(V, C, copy=False, assume_sorted=True)(V_grid)

    wot_grid = pd.DataFrame({name: interp(vals) for name, vals in wot.iteritems()})
    ## Throw-away the interpolated v, it's inaccurate, use the "x" (v-grid) instead.
    wot_grid.index = wot_grid[w.v] = V_grid

    return wot_grid


def calc_n95(wot: pd.DataFrame, n_rated) -> Tuple[float, float]:
    """
    Find wot's n95_low/high (Annex 2-2.g).

    Split `P_norm` in 2 sections around `n_rated`, and interpolate separately
    each section.  
    
    :return:
        a tuple with (low, hgh); both can be np.NAN if failed to find (error info-logged)
    """
    w = wio.pstep_factory.get().wot

    assert wot.size, "Empty wot!"
    assert not set([w.n, w.p_norm]) - set(wot.columns), (
        "Wot missing columns:",
        [w.n, w.p_norm],
        wot.columns,
    )
    assert wot[w.n].min() < n_rated <= wot[w.n].max()

    def interp_n95(label, P, N_norm):
        if len(P) < 2:
            wot_location = "below" if label == "low" else "above"
            raise ValueError(
                f"BAD wot, too few points {wot_location} n_rated({n_rated})!\n {wot}"
            )
        n_intep = interpolate.interp1d(P, N_norm, copy=False, assume_sorted=True)
        try:
            n95 = n_intep(0.95).item()
        except Exception as ex:
            if isinstance(ex, ValueError) and str(ex).startswith("A value in x_new"):
                log.info(f"Cannot find n95_{label} due to: {ex}")
                n95 = np.NAN
            else:
                raise
        return n95

    wot_low = wot.loc[wot[w.n] <= n_rated, :]
    n95_low = interp_n95("low", wot_low[w.p_norm], wot_low[w.n])

    # INVERSED so ``interp1d(assume_sorted=True)`` does not blow.
    wot_high = wot.loc[wot[w.n] >= n_rated, :].iloc[::-1]
    n95_high = interp_n95("high", wot_high[w.p_norm], wot_high[w.n])

    return n95_low, n95_high
