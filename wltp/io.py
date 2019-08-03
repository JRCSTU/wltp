#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2019 European Commission (JRC);
# Licensed under the EUPL (the 'Licence');
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at: http://ec.europa.eu/idabc/eupl
import contextvars
from typing import List

import pandas as pd

from pandalone import mappings


#: Contains all path/column names used, after code has run code.
#: Don't use it directly, but either
#: - through context-vars to allow for redefinitions, or
#: - call :func:`paths_collected()` at the end of a code run.
_root_pstep = mappings.Pstep()

#: The root-path wrapped in a context-var so that cloent code
#: canm redfine paths & column names momentarily with::
#:
#:     with wio.pstep_factory.redined(<this_module>.cols):
#:         ...
pstep_factory = contextvars.ContextVar("root", default=_root_pstep)


def paths_collected(with_orig=False, tag=None) -> List[str]:
    """
    Return path/column names used, after code has run code.
    
    See :meth:`mappings.Pstep._paths`.
    """
    return _root_pstep._paths(with_orig, tag)


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


def veh_name(g):
    return "v%0.3d" % int(g)


def veh_names(vlist):
    return [veh_name(v) for v in vlist]


def gear_name(g):
    return f"g{g}"


def gear_names(glist):
    return [gear_name(g) for g in glist]
