#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2013-2019 European Commission (JRC);
# Licensed under the EUPL (the 'Licence');
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at: http://ec.europa.eu/idabc/eupl
"""code for generating the cycle"""
import dataclasses
import itertools as itt
import functools as fnt
import logging
from numbers import Number
from typing import Iterable, List
from typing import Sequence as Seq
from typing import Union

import numpy as np
import pandas as pd
from jsonschema import ValidationError
from pandas.core.generic import NDFrame
from toolz import itertoolz as itz

from . import io as wio
from .engine import NMinDrives

Column = Union[NDFrame, np.ndarray, Number]
log = logging.getLogger(__name__)


def timelens(cond, shift=1):
    """Include earlier + later values for some condition index.

    Utility for when reviewing cycle trace "events", to look at them in context.
    """
    for i in range(shift):
        cond |= cond.shift(i - 1) | cond.shift(i + 1)
    return cond


def calc_acceleration(V: Column) -> np.ndarray:
    """
    Acordign to formula in Annex 2-3.1

    :return:
        in m/s^2

        .. Attention::
            the result in the last sample is NAN!

    """
    A = np.diff(V) / 3.6
    A = np.append(A, np.NAN)  # Restore element lost by diff().
    # Panda code same with the above: ``(-V.diff(-1))```

    return A


@dataclasses.dataclass
class PhaseMarker:
    """Identifies conjecutive truths in series"""

    #: The vehicle is stopped when its velocity is below this number (in kmh),
    #: by Annex 2-4 this is 1.0 kmh.
    running_threshold: float = 1.0

    #: (positive) consider *at least* that many conjecutive samples as
    #: belonging to a `long_{stop/acc/cruise/dec}` generated column,
    #: e.g. for ``phase_repeat_threshold=2`` see the example in :func:`_identify_conjecutive_truths()`.
    #: if 0,unspecified (might break)
    phase_repeat_threshold: int = 2

    #: the acceleration threshold(-0.1389) for identifying n_min_drive_up/down phases,
    #: defined in Annex 2-2.k
    up_threshold: float = -0.1389

    def _identify_conjecutive_truths(
        self, col: pd.Series, right_edge: bool
    ) -> pd.Series:
        """
        Dectect phases with a number of conjecutive trues above some threshold.

        :param col:
            a bolean series
        :param right_edge:
            when true, the `col` includes +1 sample towards the end

        Example:

        .. code-block:: python

            from cycler import PhaseMarker
            cycle = pd.DataFrame({
                        'v': [0,0,3,3,5,8,8,8,6,4,5,6,6,5,0,0],
                    'accel': [0,0,0,1,1,1,0,0,0,1,1,1,0,0,0,0],
                'cruise': [0,0,0,0,0,1,1,1,0,0,0,0,0,0,0,0],
                    'decel': [0,0,0,0,0,0,0,1,1,1,0,0,1,1,1,0],
                    'up': [0,0,1,1,1,1,1,1,0,1,1,1,1,0,0,0],
                'initaccel': [1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0],
                'stopdecel': [0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,0],
            })
            pm = PhaseMarker()
            
            def phase(cond):
                return pm._identify_conjecutive_truths((cycle.v > 1) & cond, True).astype(int)

            RUN = cycle['v'] >= 1
            A = (-cycle.v).diff(-1)  # GTR's acceleration definition
            assert (phase(RUN & (A > 0)) == cycle.accel).all()
            assert (phase(RUN & (A == 0)) == cycle.cruise).all()
            assert (phase(RUN & (A < 0)) == cycle.decel).all()

        Adapted from: https://datascience.stackexchange.com/a/22105/79324
        """
        grouper = (col != col.shift()).cumsum()
        # NOTE: git warns: pandas/core/indexes/base.py:2890: FutureWarning:
        # elementwise comparison failed; returning scalar instead,
        # but in the future will perform elementwise comparison
        col &= col.groupby(grouper).transform("count").ge(self.phase_repeat_threshold)
        if right_edge:
            col |= col.shift()
        return col

    def _accel_after_init(self, V, accel):
        def count_good_rows(group):
            # print(group.index.min(),group.index.max(), (group[c_accel] & group[c_init]).any(None), '\n', group)
            return (
                group.count()
                if (group.iloc[1:] > 0).all() and group.iloc[0] == 0
                else 0
            )

        repeats_grouper = (accel != accel.shift()).cumsum()
        initaccel = V.groupby(repeats_grouper).transform(count_good_rows) > 0

        ## Shift -1 for Annex 2-3.2, +1 for phase definitions @ 4.
        initaccel |= initaccel.shift(-1) | initaccel.shift(1)

        return initaccel

    def _decel_before_stop(self, decels, stops):
        def count_good_rows(group):
            return group.count() if (group & last_decel_sample_before_stop).any() else 0

        last_decel_sample_before_stop = decels & stops
        repeats_grouper = (decels != decels.shift()).cumsum()
        stopdecel = decels.groupby(repeats_grouper).transform(count_good_rows) > 0

        return stopdecel

    def add_phase_markers(
        self, cycle: pd.DataFrame, V: pd.Series, A: pd.Series
    ) -> pd.DataFrame:
        """
        Adds accel/cruise/decel/up phase markers into the given cycle,

        based `V` & `A` columns of a cycle generated by :func:`emerge_cycle()`.
        """
        c = wio.pstep_factory.get().cycle

        assert all(i is not None for i in (cycle, V, A)), (
            "Null in inputs:",
            cycle,
            V,
            A,
        )

        ## Init phase (start from standstill, Annex 2-3.2) starts
        #  for any v > 0 (not v > 0.1 kmh),
        #  so must not use the pre-calculated accel/stop phases below.
        #
        cycle[c.accel_raw] = A > 0

        ## Annex 2-4
        #
        cycle[c.run] = V >= self.running_threshold
        RUN = cycle[c.run]
        #
        def phase(cond):
            return self._identify_conjecutive_truths(cond, right_edge=True)

        ## Driveability rule phases
        #
        cycle[c.stop] = ~RUN
        cycle[c.accel] = phase(RUN & cycle[c.accel_raw])
        cycle[c.cruise] = phase(RUN & (A == 0))
        cycle[c.decel] = phase(RUN & ~cycle[c.accel_raw])

        cycle[c.init] = (V == 0) & (A == 0) & (A.shift(-1) != 0)

        cycle[c.initaccel] = self._accel_after_init(V, cycle[c.accel_raw])
        cycle[c.stopdecel] = self._decel_before_stop(cycle[c.decel], cycle[c.stop])

        ## Annex 2-2.k (n_min_drive).
        cycle[c.up] = phase(RUN & (A >= self.up_threshold))

        # NOTE: this will fail if applied twice!
        cycle.columns = pd.MultiIndex.from_product(
            (cycle.columns, ("",)), names=("item", "gear")
        )

        return cycle

    def add_class_phase_markers(
        self, cycle: pd.DataFrame, wltc_parts: Iterable[int], *, right_edge=True
    ) -> pd.DataFrame:
        """
        Adds low/mid/hight/extra high boolean index into cycle, named as p1, ...

        :param cycle:
            assumes indexed by time
        :param wltc_parts:
            must include edges (see :func:`~datamodel.get_class_parts_limits()`)
        """
        assert all(i is not None for i in (cycle, wltc_parts)), (
            "Null in inputs:",
            cycle,
            wltc_parts,
        )
        assert isinstance(wltc_parts, Iterable), wltc_parts

        for n, (start, end) in enumerate(itz.sliding_window(2, wltc_parts), 1):
            idx = start <= cycle.index
            if right_edge:
                idx &= cycle.index <= end
            else:
                idx &= cycle.index < end
            cycle[wio.class_part_name(n)] = idx

        return cycle


class CycleBuilder:
    """
    Specific choreography of method-calls required, see TCs & notebooks.
    """

    ## Default `safety_margin` redundant here, but facilitates test code.
    SM: float = 0.1
    multi_column_separator: str = "."

    #: The instance that is built.
    cycle: pd.DataFrame
    #: A column within `cycle` populated from the last `velocity` given in the cstor.
    #: to use in subsequent calculations.
    V: pd.Series
    #: A column derived from :ivar:`V`, also within `cycle`, populated on construction,
    #: and used in subsequent calculations.
    A: pd.Series

    gnames: List[str]

    def colidx_pairs(self, item: Union[str, Seq[str]], gnames: Iterable[str] = None):
        if gnames is None:
            gnames = self.gnames
        if isinstance(item, str):
            item = (item,)
        return pd.MultiIndex.from_tuples(itt.product(item, gnames))

    def colidx_pairs1(self, item: str, gear_idx: Iterable[int]):
        """Using gear indixes ie 0, 1, 2"""
        return self.colidx_pairs(item, [self.gnames[i] for i in gear_idx])

    def colidx_pairs2(self, item: str, gears: Iterable[int]):
        """Using gear ids ie 1, 2, 3"""
        return self.colidx_pairs(item, [self.gnames[i - 1] for i in gears])

    def flatten_columns(self, columns):
        sep = self.multi_column_separator

        def join_column_names(name_or_tuple):
            if isinstance(name_or_tuple, tuple):
                return sep.join(n for n in name_or_tuple if n)
            return name_or_tuple

        return [join_column_names(names) for names in columns.to_flat_index()]

    def inflate_columns(self, columns, levels=2):
        sep = self.multi_column_separator

        def split_column_name(name):
            assert isinstance(name, str), ("Inflating Multiindex?", columns)
            names = name.split(sep)
            if len(names) < levels:
                nlevels_missing = levels - len(names)
                names.extend([""] * nlevels_missing)
            return names

        tuples = [split_column_name(names) for names in columns]
        return pd.MultiIndex.from_tuples(tuples, names=["gear", "item"])

    def flat(self) -> pd.DataFrame:
        """return the :ivar:`cycle` with flattened columns"""
        cycle = self.cycle.copy()
        cycle.columns = self.flatten_columns(cycle.columns)
        return cycle

    def __init__(self, *velocities: Union[pd.Series, pd.DataFrame], **kwargs):
        """
        Initialize :ivar:`cycle` with the given velocities and acceleration of the last one.

        :param velocities:
            *named* series, e.g. from :func:`~datamodel.get_class_v_cycle()`,
            all sharing the same time-index  The last one is assumed to be the
            "target" velocity for the rest of the cycle methods.

            If they are a (dataframe, series, series), they are assigned in
            :ivar:`cycle`, :ivar:`V` and :ivar:`A` respectively, and
            no other procesing happens.
        """
        c = wio.pstep_factory.get().cycle

        if len(velocities) == 3:
            cycle, V, A = velocities
            if (
                isinstance(cycle, pd.DataFrame)
                and isinstance(V, pd.Series)
                and isinstance(A, pd.Series)
            ):
                self.cycle = cycle
                self.V = V
                self.A = A

                return

        assert velocities and all(
            (isinstance(i, pd.Series) and i.name and not i.empty for i in velocities)
        ), ("Null/empty inputs:", locals())

        vars(self).update(kwargs)

        ## Ensure time index of velocities is the 1st column.
        cycle = pd.DataFrame(
            dict([(c.t, velocities[0].index), *((v.name, v) for v in velocities)])
        )
        V = cycle.iloc[:, -1]
        cycle = cycle.set_index(c.t, drop=False)

        cycle[c.a] = calc_acceleration(V)

        self.cycle = cycle
        self.V = V
        self.A = cycle[c.a]

    def add_wots(self, gwots: pd.DataFrame):
        """
        Adds the `gwots` joined on the ``v_cap`` column of the `cycle`.

        :param gwots:
            a dataframe of wot columns indexed by a grid of rounded velocities,
            as generated by :func:`~engine.interpolate_wot_on_v_grid2()`, and
            augmented by `:func:`~engine.calc_p_avail_in_gwots()`.

        """
        c = wio.pstep_factory.get().cycle
        cycle = self.cycle

        assert all(
            (isinstance(i, pd.DataFrame) for i in (cycle, gwots))
        ) and isinstance(gwots, pd.DataFrame), locals()

        self.ng = len(gwots.columns.levels[0])
        self.gnames = wio.gear_names(range(1, self.ng + 1))
        gwots = gwots.reindex(self.V).swaplevel(axis=1).sort_index(axis=1)
        cycle = pd.concat((cycle.set_index(self.V), gwots), axis=1, sort=False)
        cycle = cycle.set_index(c.t, drop=False)

        self.cycle = cycle

    # TODO: incorporate `validate_nims_t_cold_en()`  in validations pipeline.
    def validate_nims_t_cold_en(self, t_end_cold: int, wltc_parts: Seq[int]):
        c = wio.pstep_factory.get().cycle

        t_phase1_end = wltc_parts[0]
        if t_phase1_end == 0:  # wltc_parts had edges
            t_phase1_end = wltc_parts[1]

        if t_end_cold:
            if t_end_cold > t_phase1_end:
                yield ValidationError(
                    f"`t_end_cold`({t_end_cold}) must finish before the 1st cycle-part(t_phase_end={t_phase1_end})!"
                )
            if not self.cycle[c.stop].iloc[t_end_cold]:
                yield ValidationError(
                    f"`t_end_cold`({t_end_cold}) must finish on a cycle stop(v={self.V.iloc[t_end_cold]})!"
                )

    def calc_initial_gear_flags(
        self, *, g_vmax: int, n95_max: float, n_max_cycle: float, nmins: NMinDrives
    ) -> pd.DataFrame:
        """
        Heavy lifting calculations for "initial gear" rules of Annex 2: 2.k, 3.2, 3.3 & 3.5.

        :return:
            a dataframe with *nullable* dtype ``Int8`` (for storage efficiency)
            and hierarchical columns, with `1` wherever a gear is allowed,
            for a specific rule (different sets of rules per gear).
            Push it to :meth:`combine_initial_gear_flags()`.
            
        Conditions consolidated & ordered like that::

          0  RULE      CONDITION                ALLOWED GEAR           COMMENTS
          ==========  =======================  =====================  ============================================
          ok-p               p_avail >= p_req  g > 2                  # 3.5

                                        ... AND ...

          MAXn-a                  n ≤ n95_max  g < g_vmax             # 3.3
          MAXn-b              n ≤ n_max_cycle  g_vmax ≤ g             # 3.3

                                        ... AND ...

          MINn-ud/hc      n_mid_drive_set ≤ n  g > 2                  # 3.3 & 2k (up/dn on A ≷ -0.1389, hot/cold)
          MINn-2ii      n_idle ≤ n, stopdecel  g = 2                  # 3.3 & 2k (stopdecel)
          MINn-2iii          0.9 * n_idle ≤ n  g = 2 + clutch         # 3.3 & 2k
          c_initacell               initaccel  g = 1                  # 3.2 & 3.3c (also n ≤ n95_max apply)
          c_a            1.0 ≤ v & !initaccel  g = 1                  # 3.3c (also n ≤ n95_max apply)

                                      ... NOT HERE:
          min-2i          1.15 * n_idle  ≤  n  g = 2 <-- 1            # 3.3 & 2k, driveabilty (needs init-gear)
          c_b                      n < n_idle  n/clutch modifs        # 3.3 & 2k1, driveability!
          stop              !initaccel, v < 1  g = 0, n = n_idle      # 3.2
        """
        c = wio.pstep_factory.get().cycle
        cycle = self.cycle

        assert all(i for i in (g_vmax, n95_max, n_max_cycle, nmins)), (
            "Null inputs:",
            g_vmax,
            n95_max,
            n_max_cycle,
        )

        ## Note: using array-indices below (:= gear_index - 1)
        #
        g2 = self.gnames[2 - 1]  # note this is not a list!
        gears_above_g2 = self.gnames[2:]
        gears_below_gvmax = self.gnames[: g_vmax - 1]
        gears_from_gvmax = self.gnames[g_vmax - 1 :]

        ## (ok-p) rule
        #
        p_req = cycle[c.p_req].fillna(1).values.reshape(-1, 1)
        pidx_above_g2 = self.colidx_pairs(c.p_avail, gears_above_g2)
        ok_p = cycle.loc[:, pidx_above_g2].fillna(0) >= p_req
        ok_p.columns = self.colidx_pairs(c.ok_p, gears_above_g2)

        ## (MAXn-a) rule
        #
        nidx_below_gvmax = self.colidx_pairs(c.n, gears_below_gvmax)
        ok_max_n_gears_below_gvmax = cycle.loc[:, nidx_below_gvmax] < n95_max
        ok_max_n_gears_below_gvmax.columns = self.colidx_pairs(
            c.ok_max_n_gears_below_gvmax, gears_below_gvmax
        )

        ## (MAXn-b) rule
        #
        nidx_above_gvmax = self.colidx_pairs(c.n, gears_from_gvmax)
        # if nidx_above_gvmax:
        ok_max_n_gears_from_gvmax = cycle.loc[:, nidx_above_gvmax] < n_max_cycle
        ok_max_n_gears_from_gvmax.columns = self.colidx_pairs(
            c.ok_max_n_gears_from_gvmax, gears_from_gvmax
        )

        ## (MINn-ud/hc) rules
        #
        t_colds = cycle[c.t] <= nmins.t_end_cold
        t_hots = ~t_colds
        a_ups = cycle[c.up]
        a_dns = ~a_ups
        nidx_above_g2 = self.colidx_pairs(c.n, gears_above_g2)

        ok_min_n_colds_ups = (
            cycle.loc[t_colds & a_ups, nidx_above_g2] >= nmins.n_min_drive_up_start
        )
        ok_min_n_colds_ups.columns = self.colidx_pairs(
            c.ok_min_n_colds_ups, gears_above_g2
        )

        ok_min_n_colds_dns = (
            cycle.loc[t_colds & a_dns, nidx_above_g2] >= nmins.n_min_drive_dn_start
        )
        ok_min_n_colds_dns.columns = self.colidx_pairs(
            c.ok_min_n_colds_dns, gears_above_g2
        )

        ok_min_n_hots_ups = (
            cycle.loc[t_hots & a_ups, nidx_above_g2] >= nmins.n_min_drive_up_start
        )
        ok_min_n_hots_ups.columns = self.colidx_pairs(
            c.ok_min_n_hots_ups, gears_above_g2
        )

        ok_min_n_hots_dns = (
            cycle.loc[t_hots & a_dns, nidx_above_g2] >= nmins.n_min_drive_dn_start
        )
        ok_min_n_hots_dns.columns = self.colidx_pairs(
            c.ok_min_n_hots_dns, gears_above_g2
        )

        ## Gear-2 rules:
        #
        stopdecel = cycle[c.stopdecel]
        nidx_g2 = (c.n, g2)
        #
        # MINn-2ii           n_idle ≤ n, decel-stop  g = 2
        #
        ok_min_n_g2_stopdecel = (
            cycle.loc[stopdecel, nidx_g2] >= nmins.n_min_drive2_stopdecel
        )
        ok_min_n_g2_stopdecel.name = (
            c.ok_min_n_g2_stopdecel,
            g2,
        )  # it's a shorter series
        #
        # min-2iii rule:     0.9 * n_idle ≤ n  g = 2
        #
        ok_min_n_g2 = cycle.loc[~stopdecel, nidx_g2] >= nmins.n_min_drive2
        ok_min_n_g2.name = (c.ok_min_n_g2, g2)  # it's a shorter series

        ## Gear-1 rules
        #
        g1 = self.gnames[1 - 1]  # note this is not a list!
        #
        # (c_initaccel) rule
        #
        ok_min_n_g1_initaccel = cycle[c.initaccel].copy()
        ok_min_n_g1_initaccel.name = (c.ok_min_n_g1_initaccel, g1)
        #
        # c_a rule:     1.0 ≤ v & !initaccel
        #
        ok_min_n_g1 = ~cycle[c.initaccel] & cycle[c.run]
        ok_min_n_g1.name = (c.ok_min_n_g1, g1)  # it's a series

        flag_columns = (
            ok_p,
            # .. AND ...
            ok_max_n_gears_below_gvmax,
            ok_max_n_gears_from_gvmax,
            # .. AND ...
            ok_min_n_colds_ups,
            ok_min_n_colds_dns,
            ok_min_n_hots_ups,
            ok_min_n_hots_dns,
            # .. AND ...
            ok_min_n_g2,
            ok_min_n_g2_stopdecel,
            # .. AND ...
            ok_min_n_g1,
            ok_min_n_g1_initaccel,
        )
        flags = (
            pd.concat(flag_columns, axis=1).sort_index(axis=1, level=0) * 1
        ).astype("Int8")
        flags.columns.names = ("item", "gear")

        return flags

    def _combine_gear_flags(self, gflags):
        """

        :param gflags:
            the initial-gear rule flags grouped for one specific gear
        """
        c = wio.pstep_factory.get().cycle

        flagcols = gflags.columns
        gflags = gflags.fillna(0).astype(bool)

        flags_to_AND = []
        if c.ok_p in flagcols:
            flags_to_AND.append(gflags[c.ok_p])

        # Check only one of n-max rules apply for every gear.
        assert (c.ok_max_n_gears_below_gvmax in gflags) ^ (
            (c.ok_max_n_gears_from_gvmax in gflags)
        ), flagcols
        max_n_colname = (
            # a regular gear...
            c.ok_max_n_gears_below_gvmax
            if c.ok_max_n_gears_below_gvmax in flagcols
            # an overrdive gear...
            else c.ok_max_n_gears_from_gvmax
        )
        flags_to_AND.append(gflags[max_n_colname])

        if c.ok_min_n_colds_ups in flagcols:  # not g1, g2
            assert (
                c.ok_min_n_g2 not in flagcols and c.ok_min_n_g1 not in flagcols
            ), flagcols
            flags_to_AND.append(
                (
                    gflags[c.ok_min_n_colds_ups]
                    | gflags[c.ok_min_n_colds_dns]
                    | gflags[c.ok_min_n_hots_ups]
                    | gflags[c.ok_min_n_hots_dns]
                )
            )
        elif c.ok_min_n_g2 in flagcols:
            assert c.ok_min_n_g1 not in flagcols, flagcols
            flags_to_AND.append(gflags[c.ok_min_n_g2] | gflags[c.ok_min_n_g2_stopdecel])
        elif c.ok_min_n_g1 in flagcols:
            flags_to_AND.append(gflags[c.ok_min_n_g1] | gflags[c.ok_min_n_g1_initaccel])
        else:
            assert False, ("Illegal falgs:", gflags)

        final_flags = flags_to_AND[0]

        # It is a dataframe bc there is still the 2nd level "gear"
        assert isinstance(final_flags, pd.DataFrame)
        for i in flags_to_AND[1:]:
            assert isinstance(i, pd.DataFrame), i  # ... bc the same as above
            assert i.shape[1] == 1, i
            final_flags &= i

        assert (
            isinstance(final_flags, pd.DataFrame) and final_flags.shape[1] == 1
        ), final_flags

        ## To series, or else, groupby does nothing!!
        final_flags = final_flags.iloc[:, 0]

        g = flagcols[0][1]
        final_flags.name = g

        ## To series, or else, groupby does nothing!!
        return final_flags

    def combine_initial_gear_flags(self, flags: pd.Series):
        """Merge together all N-allowed flags using AND+OR boolean logic. """
        c = wio.pstep_factory.get().cycle

        final_ok = flags.groupby(axis=1, level="gear").apply(self._combine_gear_flags)
        final_ok.columns = pd.MultiIndex.from_product(((c.ok_gear,), final_ok.columns))

        return final_ok

    def add_columns(self, *columns: Union[pd.DataFrame, pd.Series]):
        """
        Concatenate more columns into :data:`cycle`.

        :param columns:
            must have appropriate columns, ie. 2-level (item, gear).
        """
        cycle_dfs = [self.cycle, *columns]
        self.cycle = pd.concat(cycle_dfs, axis=1)
