#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2013-2019 European Commission (JRC);
# Licensed under the EUPL (the 'Licence');
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at: http://ec.europa.eu/idabc/eupl
"""formulae for cyle/vehicle dynamics"""
import logging
from numbers import Number
from typing import Union

import numpy as np
import pandas as pd
from pandas.core.generic import NDFrame

from . import engine
from . import io as wio

Column = Union[NDFrame, np.ndarray, Number]
log = logging.getLogger(__name__)


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

    return A


def calc_default_resistance_coeffs(test_mass, regression_curves):
    """
    Approximating typical P_resistance based on vehicle test-mass.

    The regression-curves are in the model `resistance_coeffs_regression_curves`.
    Use it for rough results if you are missing the real vehicle data.
    """
    a = regression_curves
    f0 = a[0][0] * test_mass + a[0][1]
    f1 = a[1][0] * test_mass + a[1][1]
    f2 = a[2][0] * test_mass + a[2][1]

    return (f0, f1, f2)


def emerge_cycle(V: pd.Series, gwots: pd.DataFrame, n2vs) -> pd.DataFrame:
    c = wio.pstep_factory.get().cycle

    cycle = gwots.reindex(V)
    cycle[c.v_cycle] = cycle.index
    cycle[c.t] = V.index
    cycle = cycle.set_index(c.t, drop=False)

    cycle[c.a_cycle] = calc_acceleration(V)
    cycle[c.run] = V >= 1

    V = cycle[c.v_cycle]
    A = cycle[c.a_cycle]
    RUN = cycle[c.run]

    cycle[c.stop] = ~RUN
    cycle[c.acc] = RUN & (A > 0)
    cycle[c.cruise] = RUN & (A == 0)
    cycle[c.dec] = RUN & (A < 0)

    return cycle


def cycle_add_p_avail_for_gears(cycle: pd.DataFrame, ng, SM) -> pd.DataFrame:
    w = wio.pstep_factory.get().wot

    for gear in range(1, ng + 1):
        gear = wio.gear_name(gear)
        cycle.loc[:, (gear, w.p_avail)] = engine.calc_p_available(
            cycle.loc[:, (gear, w.p)], cycle[(gear, w.ASM)], SM
        )

    return cycle


def flatten_cycle_columns(columns, sep="."):
    def join_column_names(name_or_tuple):
        if isinstance(name_or_tuple, tuple):
            return sep.join(n for n in name_or_tuple if n)
        return name_or_tuple

    return [join_column_names(names) for names in columns.to_flat_index()]


def inflate_cycle_columns(columns, sep=".", levels=2):
    def split_column_name(name):
        assert isinstance(name, str), ("Inflating Multiindex?", columns)
        names = name.split(sep)
        if len(names) < levels:
            nlevels_missing = levels - len(names)
            names.extend([""] * nlevels_missing)
        return names

    tuples = [split_column_name(names) for names in columns]
    return pd.MultiIndex.from_tuples(tuples, names=["gear", "item"])
