#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2019-2020 European Commission (JRC);
# Licensed under the EUPL (the 'Licence');
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at: http://ec.europa.eu/idabc/eupl
"""
formulae estimating `v_max` from wot

The `v_max` is found by the maximum gear where `p_avail_stable` intersects `p_resist`
(Annex 2-fig A2).

.. Note::
    On Aug 2019 Mr Heinz confirmed a shortcut of the vmax discovery procedure,
    implemented here:
    scan 3 gear from top, and stop on first having `v_max` less-or-equal than previous,
    and accept `v_max` from that previous gear.

.. Workaround sphinx-doc/sphinx#6590
.. doctest::
    :hide:

    >>> from wltp.vmax import *
    >>> __name__ = "wltp.vmax"
"""
import logging
from collections import namedtuple
from typing import Union

import numpy as np
import pandas as pd

from graphtik import keyword

from . import autograph as autog
from . import io as wio
from .invariants import v_step, vround

log = logging.getLogger(__name__)

#: Solution results of the equation finding the v-max of each gear:
#:
#: - ``v_max``: in kmh; np.NAN if not found
#: - ``n_vmax``: the engine speed producing v_max; np.NAN if not found
#: - ``g_vmax``: the number of the gear producing v_max
#: - ``is_n_lim``: true if max-WOT(n) reached for VMax (ie. `p_avail_stable` always > `p_resist`)
#: - ``wot``: df with intermediate curves on grid-V used to solve the equation
VMaxRec = namedtuple("VMaxRec", "v_max  n_vmax  g_vmax  is_n_lim  wot")


def _find_p_remain_root(
    gid: int, wot: pd.DataFrame, p_resist: Union[pd.Series, np.ndarray]
) -> VMaxRec:
    """
    Find the velocity (the "x") where `p_avail` (the "y") crosses `p_resist`,

    rounded towards the part of wot where ``p_remain > 0``
    (like MSAccess in e.g. `F new vehicle.form.vbs#L3273`)
    or v @ max p_wot, if `p_remain_stable` is always positive.

    :param gear_gwot:
        A df indexed by grid `v` with (at least) `p_remain_stable` column.
    :return:
        a :class:`VMaxRec` with v_max in kmh or np.NAN
    """
    w = wio.pstep_factory.get().wot

    assert not wot.empty

    wot = wot.copy()  # or else warn, when appending columns.

    wot[w.p_resist] = p_resist
    # Drop NANs for max_WOT case below to work, and save space.
    wot = wot.dropna(subset=(w.p_avail_stable,))
    wot[w.p_remain_stable] = wot[w.p_avail_stable] - p_resist

    if (wot[w.p_remain_stable] > 0).all():
        v_max = wot.index[-1]  # v @ max n
        n_v_max = wot.loc[:, w.n].iloc[-1]

        assert not (np.isnan(v_max) or np.isnan(n_v_max)), locals()
        rec = VMaxRec(v_max, n_v_max, gid, True, wot)
    else:
        v_max = np.NAN

        ## Zero-crossings of p_remain are marked as sign-changes,
        #  particularly interested in "down-crosses":
        #   -1: drop from positive to 0 (perfect match!)
        #   -2: drop from positive to negative
        wot[w.sign_p_remain_stable] = np.sign(wot[w.p_remain_stable])

        ## diff-periods:
        #   ofs=+1: diff with prev-element so zero-crossing is marked on high-index (after cross)
        #   ofs=-1: diff with next-element so zero-crossing is marked on low-index (before cross)
        #  (e.g. `F new vehicle.form.vbs#L3273`).
        #  - Multiplied to preserve sign of down-crossing, for inequality further below.
        #  - Apply `fillna()`` bc `diff()` leaves one period at head or tail.
        #
        offs = -1
        wot[w.zero_crossings] = offs * wot[w.sign_p_remain_stable].diff(
            periods=offs
        ).fillna(0)
        # ... search for down-crossings only.
        # roots_head = wot.index[wot[w.zero_crossings].lt(0, fill_value=0)]  # if no `fill_value` all NANs.
        roots_head = wot.index[wot[w.zero_crossings] < 0]
        # ... and capture v @ lowest of them (where p_remain is either 0 or still positive)
        if roots_head.size > 0:
            v_max = roots_head[0]  # Plain rounding, already close to grid.
            n_v_max = wot.loc[v_max, w.n]

            assert not (np.isnan(v_max) or np.isnan(n_v_max)), locals()
            assert v_max == vround(v_max), (v_max, vround(v_max))
            _i = wot.loc[roots_head[0] :, w.p_remain_stable].iteritems()
            assert next(_i)[1] > 0 and next(_i)[1] <= 0, (
                "Solution is not the last positive p_remain:",
                roots_head[0],
                v_max,
                wot.loc[v_max - 5 * v_step : v_max + 5 * v_step, w.p_remain_stable],
            )
            rec = VMaxRec(v_max, n_v_max, gid, False, wot)
        else:
            rec = VMaxRec(np.NAN, np.NAN, gid, False, wot)

    return rec


@autog.autographed(
    needs=(),
    provides=[
        *VMaxRec._fields[:-2],
        keyword("is_n_lim_vmax", "is_n_lim"),
        keyword("vmax_gwot", "wot"),  # `wot` causes cycle!
    ],
    inp_sideffects=[("gwots", "p_resist"), ("gwots", "p_avail")],
    returns_dict=True,
)
def calc_v_max(gwots: Union[pd.Series, pd.DataFrame]) -> VMaxRec:
    """
    Finds maximum velocity by scanning gears from the top.

    TODO: accept `n_lim`

    :param gwots:
        a dataframe indexed by a grid of rounded velocities,
        containing (at least) `p_resist` and `p_avail_stable` columns for all gears,
        as generated by :func:`~.engine.interpolate_wot_on_v_grid()`, and
        augmented by :func:`~.engine.attach_p_avail_in_gwots()` (in kW) and
        :func:`~.vehicle.calc_p_resist()`.
    :return:
        a :class:`VMaxRec` namedtuple.

    """
    w = wio.pstep_factory.get().wot

    ## Extract it so as to substract it from `p_avail`.
    p_resist = gwots.loc[:, w.p_resist]
    gidx = wio.GearMultiIndexer.from_df(gwots)
    ng = gidx.ng

    def _package_wots_df(recs):
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
            [r.wot for r in recs],
            axis=1,
            keys=[wio.gear_name(r.g_vmax) for r in recs],
            names=["gear", "item"],
            verify_integrity=True,
        )

        return wots_df

    def gear_gwot(gi):
        gridwot = gwots.loc[:, (slice(None), wio.gear_name(gi))]
        gridwot.columns = gridwot.columns.droplevel(1)
        return gridwot

    ## Scan gears from top --> (top - 3) but stop above the 1st gear.
    #
    gids_from_top = list(reversed(range(1, ng + 1)))
    gids_to_scan = gids_from_top[:-1][:4]
    assert gids_from_top, ("Too few gear-ratios?", ng, gidx.gnames)

    all_recs = []
    ok_rec = None
    for gid in gids_to_scan:
        rec = _find_p_remain_root(gid, gear_gwot(gid), p_resist)
        all_recs.append(rec)

        if ok_rec and (np.isnan(rec.v_max) or rec.v_max <= ok_rec.v_max):
            break

        if not np.isnan(rec.v_max):
            ok_rec = rec
    else:
        gear_wots_df = _package_wots_df(all_recs)
        raise ValueError(
            "Cannot find v_max!\n  Insufficient power??",
            gear_wots_df.head(),
            gwots.head(),
        )

    gear_wots_df = _package_wots_df(all_recs)
    return ok_rec._replace(wot=gear_wots_df)
