#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2019 European Commission (JRC);
# Licensed under the EUPL (the 'Licence');
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at: http://ec.europa.eu/idabc/eupl
"""formulae for engine power & revolutions and gear-box"""
import logging
from collections import namedtuple
from collections.abc import Mapping
from numbers import Number
from typing import Tuple, Union

import numpy as np
import pandas as pd
from jsonschema import ValidationError
from pandas.core.generic import NDFrame
from scipy import interpolate

from . import io as wio
from .invariants import nround1, nround10, v_decimals, v_step, vround

Column = Union[NDFrame, np.ndarray, Number]
log = logging.getLogger(__name__)


def _denormalize_n(wot_df: pd.DataFrame, n_idle, n_rated):
    w = wio.pstep_factory.get().wot
    wot_df[w.n] = n_idle + (n_rated - n_idle) * wot_df[w.n_norm]
    return wot_df


def _denormalize_p(wot_df: pd.DataFrame, p_rated):
    w = wio.pstep_factory.get().wot
    wot_df[w.p] = p_rated * wot_df[w.p_norm]
    return wot_df


def denorm_wot(wot_df: pd.DataFrame, n_idle, n_rated, p_rated):
    w = wio.pstep_factory.get().wot

    if w.n not in wot_df:
        wot_df = _denormalize_n(wot_df, n_idle, n_rated)
    if w.p not in wot_df:
        wot_df = _denormalize_p(wot_df, p_rated)

    return wot_df


def _normalize_n(wot_df: pd.DataFrame, n_idle, n_rated):
    w = wio.pstep_factory.get().wot
    wot_df[w.n_norm] = (wot_df[w.n] - n_idle) / (n_rated - n_idle)
    return wot_df


def _normalize_p(wot_df: pd.DataFrame, p_rated):
    w = wio.pstep_factory.get().wot
    wot_df[w.p_norm] = wot_df[w.p] / p_rated
    return wot_df


def norm_wot(wot_df: pd.DataFrame, n_idle, n_rated, p_rated):
    w = wio.pstep_factory.get().wot

    if w.n_norm not in wot_df:
        wot_df = _normalize_n(wot_df, n_idle, n_rated)
    if w.p_norm not in wot_df:
        wot_df = _normalize_p(wot_df, p_rated)

    return wot_df


def parse_wot(wot) -> pd.DataFrame:
    """
    Make a wot-df from 2D-matrix(lists/numpy), dict, df(1-or-2 cols) or series,

    ensuring the result wot contains one of `p`, `p_norm`, and `n`, `n_norm` columns.

    Use if from interactive code to quickly feed algo with some tabular wot.
    """
    w = wio.pstep_factory.get().wot
    n_columns = set([w.n, w.n_norm])
    p_columns = set([w.p, w.p_norm])

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


def validate_wot(
    wot: pd.DataFrame, n_idle, n_rated, p_rated, n_min_drive_set
) -> pd.DataFrame:
    """Higher-level validation of the wot-curves with repect to model."""
    w = wio.pstep_factory.get().wot

    if wot.shape[0] < 3:
        yield ValidationError(
            f"Too few points in wot!\n  At least 3 rows needed:\n{wot}"
        )

    if any(i is None for i in (n_idle, n_rated, p_rated)):
        # These should have been caught by jsonschema.
        return wot

    if wot[w.p].min() < 0:
        yield ValidationError(f"wot(P) reaches negatives({wot[w.p].min()})!\n{wot}")
    if wot[w.p_norm].max() > 1.05:
        yield ValidationError(
            f"`p_wot_max`({wot[w.p].max()}) much bigger than p_rated({p_rated})!\n{wot}"
        )
    if wot[w.p_norm].max() < 0.95:
        yield ValidationError(
            f"`p_wot_max`({wot[w.p].max()}) much lower than p_rated({p_rated})!\n{wot}"
        )

    if n_min_drive_set and wot[w.n].min() > n_min_drive_set:
        yield ValidationError(
            f"wot(N) starts above n_min_drive_set({n_min_drive_set})!\n{wot}"
        )
    if wot[w.n_norm].min() < -0.1:
        yield ValidationError(f"wot(N) starts much lower than n_idle({n_idle})!\n{wot}")
    if wot[w.n].max() < n_rated <= wot[w.n].max():
        yield ValidationError(f"n_rated({n_rated}) is not within wot(N)!\n{wot}")

    ASM = wot.get(w.ASM)
    if ASM is not None:
        if (ASM < 0).any():
            yield ValidationError(f"`{w.ASM}` must not be reach negatives! \n{ASM}")
        if ASM.max() > 0.5 * p_rated:
            ValidationError(
                f"`{w.ASM}_max`({ASM.max()}) must stay below 0.5 x `{d.p_rated}`({p_rated})!"
            )


def preproc_wot(mdl: Mapping, wot) -> pd.DataFrame:
    """
    Parses & validates wot from string or other matrix format 
    
    see  :func:`parse_wot()`
    """
    d = wio.pstep_factory.get()

    wot = parse_wot(wot)

    n_idle = mdl[d.n_idle]
    n_rated = mdl[d.n_rated]
    p_rated = mdl[d.p_rated]

    wot = denorm_wot(wot, n_idle, n_rated, p_rated)
    wot = norm_wot(wot, n_idle, n_rated, p_rated)

    for err in validate_wot(wot, n_idle, n_rated, p_rated, mdl.get(d.n_min_drive_set)):
        raise err

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
    total_reduction = 1 - f_safety_margin - ASM
    return P * total_reduction


def interpolate_wot_on_v_grid(wot: pd.DataFrame):
    """
    DEPRECATED, use by vmax only
    Interpolated wot on a v-grid from v_min_wot --> v_max_wot, rounded. 
    
    :param wot:
        must contain aat least `v` column
    """
    ## DEPRECATE when vmax switch to `...grid2()` below.
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

        .. Attention:: 
            Do not include non-linear columns (e.g. p_resistances(v^2))
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
        wot_grid.index = V_grid
        wot_grid.index.name = w.v

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


def calc_p_avail_in_gwots(gwots, *, SM) -> pd.DataFrame:
    """
    .. attention:
        Must not interpolate along with wot on grid, or great INNACCURACIES.

    :param gwots:
        a  df with 2-level multindex columns, having at least (`g1`, 'p') & ('g1', 'ASM'))
        for each gears (as retuned by :func:`interpolate_wot_on_v_grid2()`).
    """
    w = wio.pstep_factory.get().wot

    for gear in gwots.columns.levels[0]:
        gwots.loc[:, (gear, w.p_avail)] = calc_p_available(
            gwots.loc[:, (gear, w.p)], gwots[(gear, w.ASM)], SM
        )
    gwots = gwots.sort_index(axis=1)

    return gwots


def calc_n95(wot: pd.DataFrame, n_rated: int, p_rated: Number) -> Tuple[float, float]:
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
            ## Not all WOTs drop again below 95% at top-n.
            #  Accept top-n as `n_max` in such cases (by the GTR);
            # for all others, scream - they should be badly shaped wots.
            #
            if (
                label == "high"
                and isinstance(ex, ValueError)
                and str(ex).startswith("A value in x_new")
            ):
                log.info(
                    "The wot does not drop below 95%% x p_rated(%s) at top n_wot_max(%s);"
                    " assumng n95_high := n_wot_max-->p(%s).",
                    p_rated,
                    wot[w.n].max(),
                    wot[w.p].iloc[-1],
                )
                n95 = wot[w.n].max()
            else:
                raise
        return n95

    wot_low = wot.loc[wot[w.n] <= n_rated, :]
    n95_low = interp_n95("low", wot_low[w.p_norm], wot_low[w.n])

    # INVERSED so ``interp1d(assume_sorted=True)`` does not blow.
    wot_high = wot.loc[wot[w.n] >= n_rated, :].iloc[::-1]
    n95_high = interp_n95("high", wot_high[w.p_norm], wot_high[w.n])

    return n95_low, n95_high


def calc_n_max(n_max1, n_max2, n_max3):
    n_max = max(n_max1, n_max2, n_max3)
    assert np.isfinite(n_max), ("All `n_max` are NANs?", n_max1, n_max2, n_max3, n_max)

    return n_max


#: temporary use this till gear-ratios become a table (like wot).
NMinDrives = namedtuple(
    "NMinDrives",
    (
        "n_min_drive1",
        "n_min_drive2_up",
        "n_min_drive2_stopdecel",
        "n_min_drive2",
        "n_min_drive_set",
        "n_min_drive_up",
        "n_min_drive_up_start",
        "n_min_drive_down",
        "n_min_drive_dn_start",
        "t_end_cold",
    ),
)


def calc_fixed_n_min_drives(mdl: Mapping, n_idle: int, n_rated: int) -> NMinDrives:
    """
    Calculate minimum revolutions according to Annex 2-2.k.

    Assumes model has been validated, but
    not yet called :func:`~datamodel.yield_n_min_errors()`.

    """
    # TODO: accept ARRAY `n_min_drive`
    d = wio.pstep_factory.get()

    n_idle = nround10(n_idle)
    n_min_drive_set = n_idle + 0.125 * (n_rated - n_idle)

    n_min_drive_up = wio.getdval(mdl, d.n_min_drive_up, n_min_drive_set)
    n_min_drive_up_start = wio.getdval(mdl, d.n_min_drive_up_start, n_min_drive_up)

    n_min_drive_down = wio.getdval(mdl, d.n_min_drive_down, n_min_drive_set)
    n_min_drive_dn_start = wio.getdval(mdl, d.n_min_drive_dn_start, n_min_drive_down)

    t_end_cold = wio.getdval(mdl, d.t_end_cold, 0)

    nmins = NMinDrives(
        n_min_drive1=n_idle,
        n_min_drive2_up=1.15 * n_idle,
        n_min_drive2_stopdecel=n_idle,
        n_min_drive2=0.9 * n_idle,
        n_min_drive_set=n_min_drive_set,
        n_min_drive_up=n_min_drive_up,
        n_min_drive_up_start=n_min_drive_up_start,
        n_min_drive_down=n_min_drive_down,
        n_min_drive_dn_start=n_min_drive_dn_start,
        t_end_cold=t_end_cold,
    )

    nmins = NMinDrives(*(n and nround1(n) for n in nmins))

    return nmins


def nmins_from_model(mdl):
    """Repopulates the :class:`NMinDrives` from a (validated) datamodel."""
    return NMinDrives(**{field: mdl[field] for field in NMinDrives._fields})
