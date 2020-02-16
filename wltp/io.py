#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2019 European Commission (JRC);
# Licensed under the EUPL (the 'Licence');
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at: http://ec.europa.eu/idabc/eupl
"""utilities for starting-up, parsing, naming, indexing and spitting out data"""
import contextvars
import dataclasses
import itertools as itt
from typing import Iterable, List, Union

import numpy as np
import pandas as pd

from pandalone import mappings

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


def gear_name(g):
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


@dataclasses.dataclass
class GearMultiIndexer:
    """
    Utility for dataframe-columns with 2-level `:class:`pd.MultiIndex` `(item, gear)` columns

    like *grid_wots*::

        p_avail  p_avail  ... n_foo  n_foo
             g1       g2  ...    g1     g2

    """

    #: initialized from the 2-level dataframe
    gnames: List[str]

    #: separator for flattening/inflating levels
    multi_column_separator: str = "."

    @classmethod
    def from_df(cls, df):
        """
        :param df:
            the 2-level df, not stored, just to get gear-names.
        """
        return cls([g for g in df.columns.levels[1] if g])

    def __init__(self, gnames):
        """
        :param gnames:
            From :func:`gear_names()`, or avoid cstor & call directly classmethod :meth:`from_df()`.
        """
        self.gnames = gnames

    def colidx_pairs(
        self, item: Union[str, Iterable[str]], gnames: Iterable[str] = None
    ):
        if gnames is None:
            gnames = self.gnames
        assert gnames, locals()

        if isinstance(item, str):
            item = (item,)
        return pd.MultiIndex.from_tuples(itt.product(item, gnames))

    def colidx_pairs1(self, item: str, gear_idx: Iterable[int]):
        """Using gear indices ie 0, 1, 2"""
        return self.colidx_pairs(item, [self.gnames[i] for i in gear_idx])

    def colidx_pairs2(self, item: str, gears: Iterable[int]):
        """Using gear ids ie 1, 2, 3"""
        return self.colidx_pairs(item, [self.gnames[i - 1] for i in gears])

    @property
    def ng(self):
        """the number of gears extracted from 2-level dataframe"""
        return len(self.gnames)
