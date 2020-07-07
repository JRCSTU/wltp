#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2013-2020 European Commission (JRC);
# Licensed under the EUPL (the 'Licence');
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at: http://ec.europa.eu/idabc/eupl
import pandas as pd

from .. import cycles


def cycle_data():
    """
    The NEDC cycle and related-data.
    """
    data = {
        "parts": [[0, 780], [781, 1179]],
        "V_cycle": pd.Series(cycles.read_V_file("V_nedc.txt"), name="V_cycle"),
    }
    data["V_cycle"].index.name = "t"

    return data
