#!/usr/bin/env python
#-*- coding: utf-8 -*-
#
# Copyright 2013-2014 European Commission (JRC);
# Licensed under the EUPL (the 'Licence');
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at: http://ec.europa.eu/idabc/eupl

from __future__ import division, unicode_literals

def goodVehicle():
    goodVehicle = {
        "vehicle": {
            "test_mass":    1500,
            "v_max":    None,
            "p_rated":  100,
            "n_rated":  5450,
            "n_idle":   950,
            "gear_n_mins":   [700, 900, 1000, 1100, 1200, 1300],
            "gear_ratios":      [120.5, 75, 50, 43, 37, 32],
        },
        "params": {
            "f_safety_margin": [0.9] * 6,
        }
        
    }
    return goodVehicle
