#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2013-2019 European Commission (JRC);
# Licensed under the EUPL (the 'Licence');
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at: http://ec.europa.eu/idabc/eupl
"""formulae for cyle/vehicle dynamics"""
import logging
from typing import Union

import numpy as np
import pandas as pd
from pandas.core.generic import NDFrame
from numbers import Number

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


def begin_cycle_df(V: pd.DataFrame, gwots: pd.DataFrame) -> pd.DataFrame:
    t = wio.pstep_factory.get().cycle_run
    i = wio.pstep_factory.get()
    w = wio.pstep_factory.get().wot

    cycle_run = pd.merge(V, gwots, left_on=t.v, right_on=w.v)

    return cycle_run
