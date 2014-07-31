#!/usr/bin/env python
#
# Copyright 2013-2014 European Commission (JRC);
# Licensed under the EUPL (the 'Licence');
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at: http://ec.europa.eu/idabc/eupl
'''
:created: 5 Jan 2014
'''

def goodVehicle():
    goodVehicle = {
        "vehicle": {
            "mass":     1500,
            "v_max":    None,
            "p_rated":  100,
            "n_rated":  5450,
            "n_idle":   950,
            #"n_min":   None,    # Can be overriden by manufacturer.
            "gear_ratios":      [120.5, 75, 50, 43, 37, 32],
            "resistance_coeffs":[100, 0.5, 0.04],
        }
    }
    return goodVehicle
