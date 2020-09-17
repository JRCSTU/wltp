#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2013-2020 European Commission (JRC);
# Licensed under the EUPL (the 'Licence');
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at: http://ec.europa.eu/idabc/eupl
"""
formulae for cycle/vehicle dynamics

>>> from wltp.vehicle import *
>>> __name__ = "wltp.vehicle"
"""
import logging
from typing import Mapping

import pandas as pd

from . import autograph as autog
from . import io as wio
from .invariants import Column

log = logging.getLogger(__name__)


def calc_unladen_mass(mro, driver_mass):
    return mro - driver_mass


def calc_mro(unladen_mass, driver_mass):
    return unladen_mass + driver_mass


def calc_p_m_ratio(p_rated, unladen_mass):
    return 1000 * p_rated / unladen_mass


@autog.autographed(needs=["wltc_data/classes", ..., ...])
def decide_wltc_class(wltc_classes_data: Mapping[str, dict], p_m_ratio, v_max):
    """Vehicle classification according to Annex 1-2. """
    assert isinstance(p_m_ratio, (int, float)) and isinstance(
        v_max, (int, float)
    ), locals()

    c = wio.pstep_factory.get().cycle_data

    class_limits = {
        cl: (cd[c.pmr_limits], cd.get(c.velocity_limits))
        for (cl, cd) in wltc_classes_data.items()
    }

    for (cls, ((pmr_low, pmr_high), v_limits)) in class_limits.items():
        if pmr_low < p_m_ratio <= pmr_high and (
            not v_limits or v_limits[0] <= v_max < v_limits[1]
        ):
            wltc_class = cls
            break
    else:
        raise ValueError(
            "Cannot determine wltp-class for PMR(%s)!\n  Class-limits(%s)"
            % (p_m_ratio, class_limits)
        )

    return wltc_class


@autog.autographed(
    needs=["gwots/index", ..., ..., ...], provides="gwots/p_resist"
)
@autog.autographed(
    domain="cycle", needs=["cycle/V", ..., ..., ...], provides="cycle/P_resist"
)
def calc_p_resist(V: Column, f0, f1, f2):
    """
    The `p_resist` required to overcome vehicle-resistances for various velocities,

    as defined in Annex m-2.i (calculate `V_max_vehicle`).
    """
    VV = V * V
    VVV = VV * V
    return (f0 * V + f1 * VV + f2 * VVV) / 3600.0


@autog.autographed(needs=["gwots/index", "gwots/A", ..., ...], provides="gwots/p_inert")
@autog.autographed(
    domain="cycle", needs=["cycle/V", "cycle/A", ..., ...], provides="cycle/P_inert"
)
def calc_inertial_power(V, A, test_mass, f_inertial):
    """
    Power demands of the cycle accelerations, Annex 2-3.1.

    :param test_mass:
        .. jsonschema:: data-schema.yaml#/properties/test_mass
    :param f_inertial:
        .. jsonschema:: data-schema.yaml#/properties/f_inertial
    """
    return (A * V * test_mass * f_inertial) / 3600.0


@autog.autographed(needs=["gwots/p_resist", "gwots/p_inert"], provides="gwots/p_req")
@autog.autographed(
    domain="cycle", needs=["cycle/P_resist", "cycle/P_inert"], provides="cycle/P_req"
)
def calc_required_power(p_resist: Column, p_inert: Column) -> Column:
    """
    Equals :math:`road_loads + inertial_power`

    @see: Annex 2-3.1
    """
    return p_resist + p_inert


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
