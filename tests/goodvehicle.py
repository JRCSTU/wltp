#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2013-2020 European Commission (JRC);
# Licensed under the EUPL (the 'Licence');
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at: http://ec.europa.eu/idabc/eupl
from wltp import datamodel, vehicle


def goodVehicle():
    mdl = {
        "test_mass": 1500,
        "p_rated": 100,
        "n_rated": 5450,
        "n_idle": 950,
        # "n_min":   None,    # Can be overridden by manufacturer.
        "gear_ratios": [120.5, 75, 50, 43, 37, 32],
    }
    mdl = datamodel.upd_default_load_curve(mdl)
    mdl = datamodel.upd_resistance_coeffs_regression_curves(mdl)
    (f0, f1, f2) = vehicle.calc_default_resistance_coeffs(
        mdl["test_mass"], mdl["resistance_coeffs_regression_curves"]
    )
    mdl.update(f0=f0, f1=f1, f2=f2)

    return mdl
