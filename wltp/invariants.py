#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2019 European Commission (JRC);
# Licensed under the EUPL (the 'Licence');
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at: http://ec.europa.eu/idabc/eupl
"""definitions & idenmpotent formulae for physics/engineering"""
import functools

import numpy as np
import pandas as pd

v_decimals = 1
v_step = 10 ** -v_decimals


def round1(n, decimals=0):
    """
     Rounding with the Access DB method (all ties half-up: 0.5 --> 1).

    TIP: Double rounding might be needed to achive stability on ties with long decimals
    (see downscale scale vs recurse)

    :param n:
        number/array to round
    :param decimals:
        Number of decimal places to round to (default: 0).
        If decimals is negative, it specifies the number of positions to the left of the decimal point.
        `None` means keep it as it is.

    >>> round1(2.5, None)
    2.5
    >>> round1(2.5)
    3.0
    >>> round1(np.arange(-6.55, 7), 1)
    array([-6.5, -5.5, -4.5, -3.5, -2.5, -1.5, -0.5,
           0.5,  1.5,  2.5,  3.5, 4.5,  5.5,  6.5])
    >>> round1(np.arange(-6.65, 7), 1)
    array([-6.6, -5.6, -4.6, -3.6, -2.7, -1.7, -0.7,
           0.3,  1.3,  2.3,  3.4, 4.4,  5.4,  6.4])
    >>> round1([0.49999999999999994, 5000000000000001.0, -2.4, 2.4])
     array([ 1.e+00,  5.e+15, -2.e+00,  2.e+00])

    .. seealso:: https://en.wikipedia.org/wiki/Rounding#Round_half_to_even
    .. seealso:: https://en.wikipedia.org/wiki/Rounding#Double_rounding
    """

    if decimals is None:
        return n

    if isinstance(n, (list, tuple)):
        n = np.asarray(n)

    multiplier = 10 ** decimals
    return np.floor(multiplier * n + 0.5) / multiplier


#: The rounding of the GTR, used for Vs already close to grid,
#: e.g. to index with results from operations on the grid.
vround = functools.partial(round1, decimals=v_decimals)


def asint(n):
    if hasattr(n, "astype"):
        return n.astype("int")
    else:
        return int(round1(n, 0))


#: The GTR rounding for N (RPM) to integer precision,
#: e.g. for ``n_min_drive_set``.
nround1 = lambda n: asint(round1(n, 0))

#: The GTR rounding for N (RPM) to the nearest 10 RPMs precision,
#: e.g. for ``n_idle``.
nround10 = lambda n: asint(round1(n, -1))


def apply_bool_op_on_columns_with_NANFLAGs(
    df: pd.DataFrame, op, nan_val: int, NANFLAG=-1
) -> pd.Series:
    """NANs assumed `nan_val``, rows with all NANs are skipped.

    :param df:
        a preferably ``dtype=int8`` dataframe with NANFLAGs denoting missing values
    :param op:
        one of :meth:`pd.Series.__or__`, `__and__`, etc
    :param nan_val:
        replace NANs with this value (typically 0 or 1, to cleanly convert to ``astype(bool)``).
        Applied only on rows that are not all NANs.
    :return:
        A series(dtype=int8) with NANFLAG elements where all columns were NANFLAGs.

    Example:

    >>> df0 = pd.DataFrame({'a': [-1, 0, 1], 'b': [-1, -1, -1]})
    >>> df0
       a  b
    0 -1 -1
    1  0 -1
    2  1 -1
    >>> df = df0.copy()
    >>> apply_bool_op_on_columns_with_NANFLAGs(df0, pd.Series.__or__, 0)
    0   -1
    1    0
    2    1
    dtype: int8
    >>> apply_bool_op_on_columns_with_NANFLAGs(df0, pd.Series.__and__, 1)
    0   -1
    1    0
    2    1
    dtype: int8
    """
    assert isinstance(nan_val, int), nan_val

    nan_rows = (df == NANFLAG).all(axis=1)
    rows_to_or = df.loc[~nan_rows].replace(NANFLAG, nan_val).astype(bool)
    (_, col0), *cols = rows_to_or.iteritems()
    for _, col in cols:
        col0 = op(col0, col)

    return col0.reindex(df.index, fill_value=NANFLAG).astype("int8")


def OR_columns_with_NANFLAGs(
    df: pd.DataFrame, nan_val: int = 0, NANFLAG=-1
) -> pd.Series:
    """see :func:`apply_bool_op_on_columns_with_NANFLAGs()`"""
    return apply_bool_op_on_columns_with_NANFLAGs(
        df, pd.Series.__or__, nan_val, NANFLAG
    )


def AND_columns_with_NANFLAGs(
    df: pd.DataFrame, nan_val: int = 1, NANFLAG=-1
) -> pd.Series:
    """see :func:`apply_bool_op_on_columns_with_NANFLAGs()`"""
    return apply_bool_op_on_columns_with_NANFLAGs(
        df, pd.Series.__and__, nan_val, NANFLAG
    )
