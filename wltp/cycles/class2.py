#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2013-2020 European Commission (JRC);
# Licensed under the EUPL (the 'Licence');
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at: http://ec.europa.eu/idabc/eupl
"""WLTC class data for the highest-powered vehicles

Data below extracted from the GTR specs and prepared with the following python scripts
found inside the source-distribution:

* :file:`devtools/printwltcclass.py`
* :file:`devtools/csvcolumns8to2.py`
"""
import pandas as pd

import wltp.io as wio

from .. import cycles


def class_data():
    """
    Cycles for vehicles with 22 < :abbr:`PMR` ≤ 34 W/kg.
    """
    c = wio.pstep_factory.get().cycle

    data = {
        "pmr_limits": (22, 34),  ## PMR (low, high]
        "parts": (589, 1022, 1477),
        "downscale": {
            "phases": [1520, 1725, 1743],
            "p_max_values": {
                "time": 1574,
                # Km/h
                "v": 109.9,
                # m/s^2
                "a": 0.36,
            },
            "factor_coeffs": [0.866, 0.606, -0.525],  ## r0, a1, b1
        },
        "checksum": 81536.9,
        "part_checksums": [11162.2, 17054.3, 24450.6],
        "V_cycle": pd.Series(cycles.read_V_file("V_class2.txt"), name=c.V_cycle),
    }
    data["V_cycle"].index.name = c.t

    return data
