#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2013-2019 European Commission (JRC);
# Licensed under the EUPL (the 'Licence');
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at: http://ec.europa.eu/idabc/eupl
"""formulae for cyle/vehicle dynamics"""
import logging


log = logging.getLogger(__name__)


def calc_road_load_power(V, f0, f1, f2):
    """
    The `p_resist` required to overcome vehicle-resistances for various velocities, 
    
    as defined in Annex 2-2.i (calculate `V_max_vehicle`).
    """
    return (f0 * V + f1 * V ** 2 + f2 * V ** 3) / 3600.0


def calc_power_required(V, A, test_mass, f0, f1, f2, f_inertial):
    """

    @see: Annex 2-3.1
    """
    return (
        calc_road_load_power(V, f0, f1, f2) + (f_inertial * A * V * test_mass) / 3600.0
    )


def calc_default_resistance_coeffs(test_mass, regression_curves):
    """
    Approximating typical P_resistance based on vehicle test-mass.

    The regression-curves are in the model `resistance_coeffs_regression_curves`.
    Use it for rough results if you are missing the real vehicle data.
    """
    a = regression_curves
    f0 = a[0][0] * test_mass + a[0][1]
    f1 = a[1][0] * test_mass + a[1][1]
    f2 = a[2][0] * test_mass + a[2][1]

    return (f0, f1, f2)
