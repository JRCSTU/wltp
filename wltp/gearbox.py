#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2019 European Commission (JRC);
# Licensed under the EUPL (the 'Licence');
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at: http://ec.europa.eu/idabc/eupl

import logging
from collections import namedtuple
from collections.abc import Mapping
from typing import Tuple, Union

import numpy as np
import pandas as pd
from scipy import interpolate, optimize

from . import io as wio
from .invariants import nround1, nround10

log = logging.getLogger(__name__)


#: temporary use this till gear-ratios become a table (like wot).
NMinDrives = namedtuple(
    "NMinDrives",
    (
        "n_min_drive1",
        "n_min_drive2_up",
        "n_min_drive2_stand",
        "n_min_drive2",
        "n_min_drive_set",
        "n_min_drive_up",
        "n_min_drive_up_start",
        "n_min_drive_down",
        "n_min_drive_down_start",
    ),
)


def calc_fixed_n_min_drives(mdl: Mapping, n_idle: int, n_rated: int) -> NMinDrives:
    """
    Calculate minimum revolutions according to Annex 2-2.k.

    Assumes model has been validated, but
    not yet called :func:`wltp.model.yield_n_min_errors()`.

    """
    # TODO: accept ARRAY `n_min_drive`
    c = wio.pstep_factory.get()

    n_idle = nround10(n_idle)
    n_min_drive_set = n_idle + 0.125 * (n_rated - n_idle)

    n_min_drive_up = mdl.get(c.n_min_drive_up, n_min_drive_set)
    n_min_drive_up_start = mdl.get(c.n_min_drive_up_start, n_min_drive_up)

    n_min_drive_down = mdl.get(c.n_min_drive_down, n_min_drive_set)
    n_min_drive_down_start = mdl.get(c.n_min_drive_down_start, n_min_drive_down)

    nmins = NMinDrives(
        n_min_drive1=n_idle,
        n_min_drive2_up=1.15 * n_idle,
        n_min_drive2_stand=n_idle,
        n_min_drive2=0.9 * n_idle,
        n_min_drive_set=n_min_drive_set,
        n_min_drive_up=n_min_drive_up,
        n_min_drive_up_start=n_min_drive_up_start,
        n_min_drive_down=n_min_drive_down,
        n_min_drive_down_start=n_min_drive_down_start,
    )

    nmins = NMinDrives(*(n and nround1(n) for n in nmins))

    return nmins
