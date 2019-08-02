#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2019 European Commission (JRC);
# Licensed under the EUPL (the 'Licence');
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at: http://ec.europa.eu/idabc/eupl

import logging

import numpy as np
import pandas as pd
from scipy import interpolate, optimize

from pandalone import mappings

from .invariants import v_decimals, v_step, vround


log = logging.getLogger(__name__)

#: column names
c = mappings.Pstep()


def interpolate_wot_on_v_grid(wot: pd.DataFrame):
    """Return a new linearly interpolated df on v with v_decimals. """
    assert wot.size
    V = wot[c.v]

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

    wot = pd.DataFrame({name: interp(vals) for name, vals in wot.iteritems()})
    ## Throw-away the interpolated v, it's inaccurate, use the "x" (v-grid) instead.
    wot.index = wot[c.v] = V_grid

    return wot
