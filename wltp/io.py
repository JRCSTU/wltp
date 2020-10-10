#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2019-2020 European Commission (JRC);
# Licensed under the EUPL (the 'Licence');
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at: http://ec.europa.eu/idabc/eupl
"""
utilities for starting-up, parsing, naming, indexing and spitting out data

.. testsetup::

  from wltp.io import *
"""
import contextvars
import dataclasses
import functools as fnt
import itertools as itt
import re
from typing import Callable, Iterable, List, Optional, Sequence, Union

import numpy as np
import pandas as pd

from graphtik import optional
from pandalone import mappings

from . import autograph as autog


#: Contains all path/column names used, after code has run code.
#: Don't use it directly, but either
#: - through context-vars to allow for redefinitions, or
#: - call :func:`paths_collected()` at the end of a code run.
_root_pstep = mappings.Pstep()

#: The root-path wrapped in a context-var so that client code
#: can redfine paths & column names momentarily with::
#:
#:      token = wio.pstep_factory.set(mapping.Pstep(<mappings>))
#:      try:
#:          ...
#:      finally:
#:          wio.pstep_factory.reset(token)
#:         ...
pstep_factory = contextvars.ContextVar("root", default=_root_pstep)


def paths_collected(with_orig=False, tag=None) -> List[str]:
    """
    Return path/column names used, after code has run code.

    See :meth:`mappings.Pstep._paths`.
    """
    return _root_pstep._paths(with_orig, tag)


def getdval(mdl, key, default):
    """Returns `default` if `key` not in `mdl` or value is None/NAN"""
    if key in mdl:
        val = mdl[key]
        if val is not None and (not np.isscalar(val) or not np.isnan(val)):
            return val
    return default


def veh_name(v):
    n = pstep_factory.get().names
    v = int(v)
    return f"{n.v}{v:0>3d}"


def veh_names(vlist):
    return [veh_name(v) for v in vlist]


GearGenerator = Callable[[int], str]


def gear_name(g: int) -> str:
    n = pstep_factory.get().names
    return f"{n.g}{g}"


def gear_names(glist):
    return [gear_name(g) for g in glist]


def class_part_name(part_index):
    n = pstep_factory.get().names
    return f"{n.phase_}{part_index}"


def flatten_columns(columns, sep="/"):
    """Use :func:`inflate_columns()` to inverse it"""

    def join_column_names(name_or_tuple):
        if isinstance(name_or_tuple, tuple):
            return sep.join(n for n in name_or_tuple if n)
        return name_or_tuple

    return [join_column_names(names) for names in columns.to_flat_index()]


def inflate_columns(columns, levels=2, sep="/"):
    """Use :func:`flatten_columns()` to inverse it"""

    def split_column_name(name):
        assert isinstance(name, str), ("Inflating Multiindex?", columns)
        names = name.split(sep)
        if len(names) < levels:
            nlevels_missing = levels - len(names)
            names.extend([""] * nlevels_missing)
        return names

    tuples = [split_column_name(names) for names in columns]
    return pd.MultiIndex.from_tuples(tuples, names=["gear", "item"])


@dataclasses.dataclass(frozen=True, eq=True)
class GearMultiIndexer:
    """
    Multi-indexer for 2-level df columns like ``(item, gear)`` with 1-based & closed-bracket `gear`.

    Example 2-level *grid_wots* columns::

        p_avail  p_avail  ... n_foo  n_foo
           g1       g2    ...   g1      g2

    df.columns = gidx[:]

    ... Warning::
        negative indices might not work as expected if :attr:`gnames` do not start from ``g1``
        (e.g. when constructed with :meth:`from_df()` static method)


    **Examples:**

    - Without `items` you get simple gear-indexing:

      >>> G = GearMultiIndexer.from_ngears(5)
      >>> G.gnames
      1    g1
      2    g2
      3    g3
      4    g4
      5    g5
      dtype: object
      >>> G[1:3]
      ['g1', 'g2', 'g3']
      >>> G[::-1]
      ['g5', 'g4', 'g3', 'g2', 'g1']
      >>> G[3:2:-1]
      ['g3', 'g2']
      >>> G[3:]
      ['g3', 'g4', 'g5']
      >>> G[3:-1]
      ['g3', 'g4', 'g5']
      >>> G[-1:-2:-1]
      ['g5', 'g4']

      >>> G[[1, 3, 2]]
      ['g1', 'g3', 'g2']

      >>> G[-1]
      'g5'


    - When `items` are given, you get a "product" MultiIndex:

      >>> G = G.with_item("foo")
      >>> G[1:3]
      MultiIndex([('foo', 'g1'),
                  ('foo', 'g2'),
                  ('foo', 'g3')],
                  names=['item', 'gear'])

      >>> len(G)
      5
      >>> G.shape
      (5, 2)
      >>> G.size
      10

      Use no `items` to reset them:

      >>> G = G.with_item()
      >>> G[:]
      ['g1', 'g2', 'g3', 'g4', 'g5']
      >>> G.shape
      (5,)

    - Notice that **G0** changes "negative" indices:

      >>> G[[-5, -6, -7]]
      ['g1', 'g5', 'g4']
      >>> G = GearMultiIndexer.from_ngears(5, gear0=True)
      >>> G[:]
      ['g0', 'g1', 'g2', 'g3', 'g4', 'g5']
      >>> G[[-5, -6, -7]]
      ['g1', 'g0', 'g5']

    """

    #: 1st level column(s)
    items: Optional[Sequence[str]]
    #: 2-level columns; use a gear_namer like :func:`gear_names()` (default)
    #:
    #: to make a :class:`pd.Series` like::
    #:
    #:     {1: 'g1', 2: 'g2', ...}
    gnames: pd.Series
    #: Setting it to a gear not in :attr:`gnames`, indexing with negatives
    #: may not always work.
    top_gear: int
    #: a function returns the string representation of a gear, like ``1 --> 'g1'``
    gear_namer: GearGenerator
    level_names: Sequence[str] = dataclasses.field(default=("item", "gear"))

    @classmethod
    def from_ngears(
        cls,
        ngears: int,
        items: Sequence[str] = None,
        gear_namer: GearGenerator = gear_name,
        gear0=False,
    ):
        return GearMultiIndexer(
            items,
            pd.Series({i: gear_namer(i) for i in range(int(not gear0), ngears + 1)}),
            ngears,
            gear_namer,
        )

    @classmethod
    def from_gids(
        cls,
        gids: Iterable[int],
        items: Sequence[str] = None,
        gear_namer: GearGenerator = gear_name,
    ):
        gids = sorted(gids)
        gnames = pd.Series({i: gear_namer(i) for i in gids})
        return GearMultiIndexer(items, gnames, gids[-1], gear_namer)

    @classmethod
    @autog.autographed(
        name="make_gwots_multi_indexer",
        needs=["gwots", optional("gear_namer")],
        provides="gidx",
    )
    @autog.autographed(
        name="make_cycle_multi_indexer",
        needs=["cycle/OK_gear", optional("gear_namer")],
        provides="gidx2",
    )
    def from_df(
        cls, df, items: Sequence[str] = None, gear_namer: GearGenerator = gear_name
    ):
        """
        Derive gears from the deepest level columns, sorted, and the last one becomes `ngear`

        :param df:
            the regular or multilevel-level df, not stored, just to get gear-names.

        ... Warning::
            Negative indices might not work as expected if :attr:`gnames`
            does not start from ``g1``.
        """
        gears = df.columns
        if hasattr(gears, "levels"):
            gears = gears.levels[-1]
        gears = [g for g in gears if g]
        gids = [int(i) for i in re.sub("[^0-9 ]", "", " ".join(gears)).split()]
        gnames = pd.Series(gears, index=gids).sort_index()
        return cls(items, gnames, gids[-1], gear_namer)

    def with_item(self, *items: str):
        """
        Makes a gear-indexer producing tuple of (items x gears).

        Example:

        >>> GearMultiIndexer.from_ngears(2, gear0=True).with_item("foo", "bar")[:]
        MultiIndex([('foo', 'g0'),
                    ('foo', 'g1'),
                    ('foo', 'g2'),
                    ('bar', 'g0'),
                    ('bar', 'g1'),
                    ('bar', 'g2')], )
        """
        return type(self)(items or None, self.gnames, self.top_gear, self.gear_namer)  # type: ignore

    def _level_names(self, items=None) -> Optional[Sequence[str]]:
        if items is None:
            items = self.items
        n_levels = 1 if not items else 1 + len(items)
        return (
            self.level_names[:n_levels] if n_levels <= len(self.level_names) else None
        )

    def __getitem__(self, key):
        """
        1-based & closed-bracket indexing, like Series but with `-1` for the top-gear.
        """
        top_gear = self.ng
        # Support partial gears or G0!
        offset = int(top_gear == self.top_gear)

        def from_top_gear(i):
            return offset + (i % top_gear) if isinstance(i, int) and i < 0 else i

        if isinstance(key, slice):
            key = slice(from_top_gear(key.start), from_top_gear(key.stop), key.step)
        elif isinstance(key, int):
            key = from_top_gear(key)
        else:  # assume Iterable[int]
            key = [from_top_gear(g) for g in key]

        gnames = self.gnames.loc[key]

        ## If no items, return just a list of gears.
        #
        if self.items is None:
            if isinstance(gnames, pd.Series):
                gnames = list(gnames)
            return gnames

        ## Otherwise, return a product multi-index.
        #
        if not isinstance(gnames, pd.Series):
            gnames = (gnames,)
        return pd.MultiIndex.from_tuples(
            itt.product(self.items, gnames), names=self._level_names()
        )

    def colidx_pairs(
        self, item: Union[str, Iterable[str]], gnames: Iterable[str] = None
    ):
        if gnames is None:
            gnames = self.gnames
        assert gnames, locals()

        if isinstance(item, str):
            item = (item,)
        return pd.MultiIndex.from_tuples(
            itt.product(item, gnames), names=self._level_names(item)
        )

    def __len__(self):
        """
        The number of gears extracted from 2-level dataframe.

        It equals :attr:`top_gear` if :attr:`gnames` are from 1-->top_gear.
        """
        return len(self.gnames)

    ng = property(__len__)

    @property
    def shape(self):
        y = (1 + len(self.items),) if self.items else ()
        return (self.ng, *y)

    @property
    def size(self):
        return self.ng * ((len(self.items) + 1) if self.items else 1)


@fnt.lru_cache()
def make_autograph(out_patterns=None, *args, **kw) -> autog.Autograph:
    """Configures a new :class:`.Autograph` with func-name patterns for this project. """
    if out_patterns is None:
        out_patterns = "get_ calc_ upd_ make_ create_ decide_ round_ init_ combine_ derrive_".split()
        out_patterns.append(re.compile(r"\battach_(\w+)_in_(\w+)$"))
    return autog.Autograph(out_patterns, *args, **kw)
