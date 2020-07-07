#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2013-2020 European Commission (JRC);
# Licensed under the EUPL (the 'Licence');
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at: http://ec.europa.eu/idabc/eupl
"""WLTC class data for the low-powered vehicles

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
    Cycles for vehicles with :abbr:`PMR` ≤ 22 W/kg.
    """
    c = wio.pstep_factory.get().cycle

    data = {
        "pmr_limits": (0, 22),  ## PMR (low, high]
        "lengths": (589, 433, 589),
        "downscale": {
            "phases": [651, 848, 907],
            "p_max_values": {
                "time": 764,
                # Km/h
                "v": 61.4,
                # m/s^2
                "a": 0.22,
            },
            "factor_coeffs": [0.978, 0.680, -0.665],  ## r0, a1, b1
        },
        "checksum": 41139.6,
        "part_checksums": [11988.4, 17162.8, 11988.4],
        "V_cycle": pd.Series(cycles.read_V_file("V_class1.txt"), name=c.V_cycle),
    }
    data["V_cycle"].index.name = c.t

    return data
