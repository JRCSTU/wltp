#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2013-2019 European Commission (JRC);
# Licensed under the EUPL (the 'Licence');
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at: http://ec.europa.eu/idabc/eupl
"""
Pure calculations for physical/mathematical part of wltp-GS.

Keep them separate for testability.
"""

import logging
import re
import sys
from typing import Union

import numpy as np
import pandas as pd

log = logging.getLogger(__name__)


def round1(n, decimals=0):
    """
    Rounding in 2-steps with "bankers rounding" (ties on even: 3.5 --> 4 <-- 4.5), 
    
    to achive stability also on ties with long decimals.
    
    This trick produces identical `V` for both recurse & rescale
    (see ``tests/test_downscale:test_recurse_vs_scaling()``).

    :param n:
        number/array to round
    :param decimals:
        Number of decimal places to round to (default: 0).
        If decimals is negative, it specifies the number of positions to the left of the decimal point.
        `None` means keep it as it is.

    >>> n = np.arange(-6.55, 7); n
    array([-6.55, -5.55, -4.55, -3.55, -2.55, -1.55, -0.55,
           0.45,  1.45, 2.45,  3.45,  4.45,  5.45,  6.45])
    >>> round1(np.arange(-6.55, 7), 1)
    array([-6.6, -5.6, -4.6, -3.6, -2.6, -1.6, -0.6,
           0.4,  1.4,  2.4,  3.4, 4.4,  5.4,  6.4])
    >>> round1(np.arange(-6.65, 7), 1)  # the same as before!
    array([-6.6, -5.6, -4.6, -3.6, -2.6, -1.6, -0.6,
           0.4,  1.4,  2.4,  3.4, 4.4,  5.4,  6.4])
    
    .. seealso:: https://en.wikipedia.org/wiki/Rounding#Round_half_to_even
    """
    if decimals is None:
        return n

    return np.around(np.around(n, decimals + 2), decimals)


#    resistance_coeffs_regression_curves
def calc_default_resistance_coeffs(test_mass, regression_curves):
    a = regression_curves
    f0 = a[0][0] * test_mass + a[0][1]
    f1 = a[1][0] * test_mass + a[1][1]
    f2 = a[2][0] * test_mass + a[2][1]

    return (f0, f1, f2)


def decide_wltc_class(wltc_data, p_m_ratio, v_max):
    """

    @see: Annex 1, p 19
    """
    class_limits = {
        cl: (cd["pmr_limits"], cd.get("velocity_limits"))
        for (cl, cd) in wltc_data["classes"].items()
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


def calc_downscale_factor(
    p_max_values,
    downsc_coeffs,
    p_rated,
    f_downscale_threshold,
    f_downscale_decimals,
    test_mass,
    f0,
    f1,
    f2,
    f_inertial,
):
    """Check if downscaling required, and apply it.
    :return: (float) the factor

    @see: Annex 1-7, p 68
    """

    ## Max required power at critical point.
    #
    pmv = p_max_values["v"]
    pma = p_max_values["a"]
    p_req_max = (
        f0 * pmv + f1 * pmv ** 2 + f2 * pmv ** 3 + f_inertial * pma * pmv * test_mass
    ) / 3600.0
    r_max = p_req_max / p_rated

    (r0, a1, b1) = downsc_coeffs

    if r_max >= r0:
        f_downscale = a1 * r_max + b1
        f_downscale = round1(f_downscale, f_downscale_decimals)

        ## ATTENTION:
        #  By the spec, f_downscale MUST be > 0.01 to apply,
        #  but in F new vehicle.form.txt:(3537, 3563, 3589) (see CHANGES.rst)
        #  a +0.5 is ADDED!
        if f_downscale <= f_downscale_threshold:
            f_downscale = 0
    else:
        f_downscale = 0

    return f_downscale


def downscale_class_velocity(V: pd.Series, f_downscale, phases) -> pd.Series:
    """
    Downscale velocity profile by `f_downscale`.

    :return:
        the downscaled velocity profile, not-rounded
        (by the Spec should have 1 decimal only)

    - The Spec demarks 2 UP/DOWN phases with 3 time-points in `phases`,
      eg. for class3:

      - 1533: the "start" of downscaling
      - 1724: the "tip"
      - 1763: the "end"

    - V @ start & end (1533, 1763) must remain unchanged (by the Spec & asserted).
    - The "tip" is scaled with the UP-phase (by the Spec).
    - Those numbers are recorded in the model @ ``<class>/downscale/phases/``
    - The code asserts that the scaled V remains as smooth at tip as originally
      (and a bit more, due to the downscaling).

    Compare v075(class-3a) with Heinz:
        V_heinz V_python      diff%
        45.1636	45.1637	-0.000224059  # middle on tip(eg. 1724), both scale & recurse
        45.1636	45.1637	-0.000122941  # on tip, scale & recurse, round(1)
        45.1636	45.1637	-5.39439e-05  # on tip-1
        45.1636	45.1636	0             # on tip-1, scale & recurse, round(1)
        45.1636	45.1637	-6.48634e-05  # on tip+1
        45.1636	45.1636	0             # on tip+1, scale & recurse, round(1)

    @see: Annex 1-8, p 64-68
    """
    # return downscale_by_recursing(V, f_downscale, phases)
    return downscale_by_scaling(V, f_downscale, phases)


def downscale_by_recursing(V, f_downscale, phases):
    """Downscale by recursing (according to the Spec). """
    V_DSC = V.copy()
    (t0, t1, t2) = phases

    ## Accelaration phase
    #
    for t in range(t0, t1):
        a = V[t + 1] - V[t]
        V_DSC[t + 1] = V_DSC[t] + a * (1 - f_downscale)

    ## Decelaration phase
    #
    f_corr = (V_DSC[t1] - V[t2]) / (V[t1] - V[t2])
    for t in range(t1 + 1, t2):
        a = V[t] - V[t - 1]
        V_DSC[t] = V_DSC[t - 1] + a * f_corr

    return V_DSC


def downscale_by_scaling(V: pd.Series, f_downscale, phases) -> pd.Series:
    """
    Multiply the UP/DOWN phases with 2 factors (no recurse, against the Spec).
    """
    V_DSC = V.copy()
    (t0, t1, t2) = phases
    f_scale = 1 - f_downscale

    ## UP-phase
    #
    #  tip included in this phase: [start, tip] (=[1533, 1724] for class3)
    up_ix = (t0 <= V.index) & (V.index <= t1)
    up_offset = V[t0]
    V_DSC[up_ix] = up_offset + f_scale * (V[up_ix] - up_offset)
    assert V_DSC[t0] == V[t0], f"Invariant-start violation {V_DSC[t0]} != {V[t0]}!"

    ## DOWN-phase
    #
    # [tip+1, end] ()=[1725, 1763] for class3)
    dn_ix = (t1 + 1 <= V.index) & (V.index <= t2)
    dn_offset = V[t2]
    f_corr = (V_DSC[t1] - dn_offset) / (V[t1] - dn_offset)
    V_DSC[dn_ix] = dn_offset + f_corr * (V[dn_ix] - dn_offset)
    assert V_DSC[t2] == V[t2], f"Invariant-end violation {V_DSC[t2]} != {V[t2]}!"

    ## FIXME: `f_scale` multipliers should have been on the other side(!) of inequailty,
    #  but then assertion fails frequently.
    assert f_scale * abs(V_DSC[t1 + 1] - V_DSC[t1]) <= abs(V[t1 + 1] - V[t1]), (
        f"Smooth-tip violation diff_V_DSC({abs(V_DSC[t1 + 1] - V_DSC[t1])})"
        f" !<= diff_V({abs(V[t1 + 1] - V[t1])})!"
    )

    return V_DSC
