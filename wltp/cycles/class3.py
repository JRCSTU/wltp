#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2013-2020 European Commission (JRC);
# Licensed under the EUPL (the 'Licence');
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at: http://ec.europa.eu/idabc/eupl
"""WLTC class data for the highest-power class of vehicles.

Data below extracted from the GTR specs and prepared with the following python scripts
found inside the source-distribution:

* :file:`devtools/printwltcclass.py`
* :file:`devtools/csvcolumns8to2.py`
"""
import pandas as pd

import wltp.io as wio

from .. import cycles


def class_data_a():
    """
    Cycles for vehicles with :abbr:`PMR` > 34 W/kg and max-velocity < 120 km/h.
    """
    c = wio.pstep_factory.get().cycle

    data = {
        "pmr_limits": (34, float("inf")),  ## PMR (low, high]
        "velocity_limits": [0, 120],  ## Km/h [low, high)
        "parts": (589, 1022, 1477),
        "downscale": {
            "phases": [1533, 1724, 1763],
            "p_max_values": {
                "time": 1566,
                # Km/h
                "v": 111.9,
                # m/s^2
                "a": 0.50,
            },
            "factor_coeffs": [0.867, 0.588, -0.510],
        },
        "checksum": 83496.9,
        "part_checksums": [11140.3, 16995.7, 25646.0, 29714.9],
        "V_cycle": pd.Series(cycles.read_V_file("V_class3a.txt"), name=c.V_cycle),
    }
    data["V_cycle"].index.name = c.t

    return data


def class_data_b():
    """
    Cycles for vehicles with :abbr:`PMR` > 34 W/kg and max-velocity >= 120 km/h.
    """
    c = wio.pstep_factory.get().cycle

    cycle = pd.Series(cycles.read_V_file("V_class3b.txt"), name=c.V_cycle)
    cycle.index.name = c.t

    data = class_data_a()
    data.update(
        {
            "checksum": 83758.6,
            "part_checksums": [11140.3, 17121.2, 25782.2, 29714.9],
            "V_cycle": cycle,
            "velocity_limits": [120, float("inf")],  ## Km/h [low, high)
        }
    )

    return data
