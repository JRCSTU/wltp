#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2019 European Commission (JRC);
# Licensed under the EUPL (the 'Licence');
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at: http://ec.europa.eu/idabc/eupl

import logging
from collections.abc import Mapping
from numbers import Number
from typing import Tuple, Union

import numpy as np
import pandas as pd
from pandas.core.generic import NDFrame
from scipy import interpolate

from . import io as wio
from .invariants import v_decimals, v_step, vround

Column = Union[NDFrame, np.ndarray, Number]
log = logging.getLogger(__name__)


def denormalize_n(wot_df: pd.DataFrame, n_idle, n_rated):
    w = wio.pstep_factory.get().wot
    wot_df[w.n] = n_idle + (n_rated - n_idle) * wot_df[w.n_norm]
    return wot_df


def denormalize_p(wot_df: pd.DataFrame, p_rated):
    w = wio.pstep_factory.get().wot
    wot_df[w.p] = p_rated * wot_df[w.p_norm]
    return wot_df


def denorm_wot(mdl: Mapping, wot_df: pd.DataFrame):
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


def norm_wot(mdl: Mapping, wot_df: pd.DataFrame):
    c = wio.pstep_factory.get()
    w = wio.pstep_factory.get().wot

    if w.n_norm not in wot_df:
        wot_df = normalize_n(wot_df, mdl[c.n_idle], mdl[c.n_rated])
    if w.p_norm not in wot_df:
        wot_df = normalize_p(wot_df, mdl[c.p_rated])

    return wot_df


def _wot_defs() -> Tuple:
    c = wio.pstep_factory.get()
    w = wio.pstep_factory.get().wot
    n_columns = set([w.n, w.n_norm])
    p_columns = set([w.p, w.p_norm])
    return c, w, n_columns, p_columns


def parse_wot(wot) -> pd.DataFrame:
    """
    Make a wot-df from 2D-matrix(lists/numpy), dict, df(1-or-2 cols) or series,

    ensuring the result wot contains one of `p`, `p_norm`, and `n`, `n_norm` columns.

    Use if from interactive code to quickly feed algo with some tabular wot.
    """
    _, w, n_columns, p_columns = _wot_defs()

    wot_orig = wot

    ## Any pandas with index other than 1,2,3...
    #
    something_in_index = False
    if (
        isinstance(wot, (pd.DataFrame, pd.Series))
        and (wot.index != range(len(wot.index))).any()
    ):
        something_in_index = True

    if not isinstance(wot, pd.DataFrame):
        wot = pd.DataFrame(wot)

    if wot.empty:
        raise ValueError(f"Empty WOT: {wot_orig}!")

    if wot.shape[0] <= 2 and wot.shape[0] < wot.shape[1]:
        wot = wot.T

    ## Accept a 1-column df if column-names were unamed or one of the p columnns.
    #
    if (
        wot.shape[1] == 1
        and something_in_index
        and (wot.columns[0] == 0 or wot.columns[0] in p_columns)
    ):
        if wot.columns[0] == 0:
            wot.columns = [w.p]
        wot[w.n] = wot.index
        wot = wot[wot.columns[::-1]]
        log.warning(
            "Assuming single-column WOT to be `%s` with index `%s`.", *wot.columns
        )

    ## Accept 2-columns if column-names were unamed.
    #
    elif wot.shape[1] == 2:
        if tuple(wot.columns) == (0, 1):
            wot.columns = [w.n, w.p]
            log.warning("Assuming the 2-column WOT to be: %s, %s", *wot.columns)

    ## If ony Ps given and index exists,
    #  assume for Ns, respecting its name.
    #
    wot_columns = set(wot.columns)
    if (
        something_in_index
        and bool(wot_columns & p_columns)
        and not bool(wot_columns & n_columns)
    ):
        if wot.index.name is None:
            log.warning("Assuming WOT.index as `n`.")
            wot[w.n] = wot.index
        elif wot.index.name in n_columns:
            wot[wot.index.name] = wot.index

    wot_columns = set(wot.columns)
    if not bool(wot_columns & n_columns):
        raise ValueError(f"Wot is missing one of: {w.n}, {w.n_norm}")
    if not bool(wot_columns & p_columns):
        raise ValueError(f"Wot is missing one of: {w.p}, {w.p_norm}")

    return wot


def validate_wot(mdl: Mapping, wot: pd.DataFrame) -> pd.DataFrame:
    """Higher-level validation of the wot-curves with repect to model."""
    c, w, n_columns, p_columns = _wot_defs()

    wot_columns = set(wot.columns)
    if not bool(wot_columns & n_columns):
        raise ValueError(f"Wot is missing one of: {w.n}, {w.n_norm}")
    if not bool(wot_columns & p_columns):
        raise ValueError(f"Wot is missing one of: {w.p}, {w.p_norm}")

    wot = denorm_wot(mdl, wot)
    wot = norm_wot(mdl, wot)

    if wot.shape[0] < 3:
        raise ValueError(f"Too few points in wot!\n  At least 3 rows needed:\n{wot}")

    ## Higher-level checks in actual data
    #
    n_rated = mdl[c.n_rated]
    n_idle = mdl[c.n_idle]
    p_rated = mdl[c.p_rated]

    if wot[w.p].min() < 0:
        raise ValueError(f"wot(P) reaches negatives({wot[w.p].min()})!\n{wot}")
    if wot[w.p_norm].max() > 1.05:
        raise ValueError(f"wot(P) much bigger than p_rated({p_rated})!\n{wot}")
    if wot[w.p_norm].max() < 0.95:
        raise ValueError(f"wot(P) much lower than p_rated({p_rated})!\n{wot}")

    if wot[w.n_norm].min() < -0.1:
        raise ValueError(f"wot(N) starts much lower than n_idle({n_idle})!\n{wot}")
    if wot[w.n].max() < n_rated <= wot[w.n].max():
        raise ValueError(f"n_rated({n_rated}) is not within wot(N)!\n{wot}")

    return wot


def preproc_wot(mdl: Mapping, wot) -> pd.DataFrame:
    """
    Parses & validates wot from string or other matrix format 
    
    see  :func:`parse_wot()`
    """
    wot = parse_wot(wot)
    wot = validate_wot(mdl, wot)

    return wot


def calc_p_available(P: Column, ASM: Column, f_safety_margin) -> Column:
    """
    Calculate `p_available` acording to Annex 2-3.4.

    :param P: 
        in kW
    :param ASM: 
        in % (e.g. 0.10, 0.35)
    :return: 
        in kW
    """
    w = wio.pstep_factory.get().wot

    total_reduction = 1 - f_safety_margin - ASM
    return P * total_reduction


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


def _make_v_grid(v_wot_min: float, v_wot_max: float) -> np.ndarray:
    assert v_wot_min < v_wot_max, f"Unsorted wot? {v_wot_min}, {v_wot_max}"

    ## Clip V-grid inside min/max of wot-N.
    #
    vmul = 10 ** v_decimals
    v_wot_min2 = vround(np.ceil(v_wot_min * vmul) / vmul)
    v_wot_max2 = vround(np.floor(v_wot_max * vmul) / vmul)

    ## Using np.arange() because np.linspace() steps are not reliably spaced,
    #  and apply the GTR-rounding.
    #
    V_grid = vround(np.arange(v_wot_min2, v_wot_max2, v_step))
    assert V_grid.size, ("Empty wot?", v_wot_min, v_wot_max)
    ## Add endpoint manually because np.arange() is not adding it reliably.
    #
    if V_grid[-1] != v_wot_max:
        V_grid = np.hstack((V_grid, [v_wot_max]))

    assert 0 <= V_grid[0] - v_wot_min < v_step, (
        "V-grid start below/too-far min(N_wot): ",
        v_wot_min,
        v_wot_min2,
        V_grid[0:7],
        v_step,
    )
    assert 0 <= v_wot_max - V_grid[-1] < v_step, (
        "V-grid end above/too-far max(N_wot): ",
        V_grid[-7:],
        v_wot_max2,
        v_wot_max,
        v_step,
    )
    return V_grid


def interpolate_wot_on_v_grid2(wot: pd.DataFrame, n2v_ratios) -> pd.DataFrame:
    """
    Return a new linearly interpolated df on v with v_decimals. 
    
    :param df:
        A df containing at least `n` (in RPM); any other column gets instepolated.

        .. note:: 
            do not include non-linear columns (e.g. p_resistances(v^2))
            because those interpolated values would be highly inaccurate!

    :return:
        the wot interpolated on a v-grid accomodating all gears
    
    """
    w = wio.pstep_factory.get().wot

    assert wot.size, "Empty wot!"

    N = wot[w.n]
    n_wot_min, n_wot_max = N.min(), N.max()
    v_wot_min = n_wot_min / n2v_ratios[0]
    v_wot_max = n_wot_max / n2v_ratios[-1]
    assert v_wot_min < v_wot_max, f"Unsorted n2vs? {v_wot_min}, {v_wot_max}\n{wot}"

    V_grid = _make_v_grid(v_wot_min, v_wot_max)

    def interpolate_gear_wot(wot, n2v):
        V = N / n2v

        def interp(C):
            return interpolate.interp1d(
                V,
                C,
                copy=False,
                assume_sorted=True,
                fill_value=np.NAN,
                bounds_error=False,
            )(V_grid)

        wot_grid = pd.DataFrame({name: interp(vals) for name, vals in wot.iteritems()})
        ## Throw-away any interpolated v, it's inaccurate, use the "x" (v-grid) instead.
        wot_grid[w.v] = V_grid
        wot_grid.set_index(w.v)

        return wot_grid

    wot_grids = {
        wio.gear_name(gnum): interpolate_gear_wot(wot, g)
        for gnum, g in enumerate(n2v_ratios, 1)
    }

    wot_grid = pd.concat(
        wot_grids.values(),
        axis=1,
        keys=wot_grids.keys(),
        names=["gear", "wot_item"],
        verify_integrity=True,
    )

    return wot_grid


def calc_n95(wot: pd.DataFrame, n_rated) -> Tuple[float, float]:
    """
    Find wot's n95_low/high (Annex 2-2.g).

    Split `P_norm` in 2 sections around `n_rated`, and interpolate separately
    each section.  
    
    :wot:
        Must contain `n` & `p_norm`.
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
