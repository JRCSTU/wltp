#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2019 European Commission (JRC);
# Licensed under the EUPL (the 'Licence');
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at: http://ec.europa.eu/idabc/eupl
import contextvars
import pandas as pd


#: Contains all path/column names used, after code has run code.
_base_path = None


def pstep_ctxvar(name, *tags) -> contextvars.ContextVar:
    """Make a new Pstep (as contextvar to change temporarily change) for naming paths & column-names."""
    global _base_path

    from pandalone import mappings

    if _base_path is None:
        _base_path = mappings.Pstep()

    p = getattr(_base_path, name)
    for t in tags:
        p._tag(t)

    return contextvars.ContextVar(name, default=p)


def make_xy_df(data, xname=None, yname=None, auto_transpose=False) -> pd.DataFrame:
    """
    Make a X-indexed df from 2D-matrix(lists/numpy), dict, df(1-or-2 cols) or series.

    :param auto_transpose:
        If not empty, ensure longer dimension is the rows (axis-0).
    """
    try:
        df = data if isinstance(data, pd.DataFrame) else pd.DataFrame(data)

        if auto_transpose and not df.empty and df.shape[0] < df.shape[1]:
            df = df.T

        ## Handle empties
        #
        if df.shape[1] == 0:
            if yname is None:
                yname = 0  # default name for the 1st column
            df[yname] = pd.np.NaN
        else:
            if df.shape[1] > 2:
                if not xname == yname == None:
                    if xname not in df.columns or yname not in df.columns:
                        raise ValueError(
                            f"Columns X={xname}, Y={yname} not found in {df.columns}"
                        )
                    else:
                        df = df.loc[:, [xname, yname]]
                        df.set_index(xname)
                else:
                    raise ValueError(
                        f"Expected 2 columns at most, not {df.shape[1]}: {df.columns}"
                    )
            if df.shape[1] == 2:
                df = df.set_index(df.columns[0])

            if yname is not None:
                df.columns = [yname]

        if xname is not None:
            df.index.name = xname

        return df
    except Exception as ex:
        raise ValueError(f"Invalid XY input(type: {type(data)}), due to: {ex}") from ex
