#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2013-2020 European Commission (JRC);
# Licensed under the EUPL (the 'Licence');
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at: http://ec.europa.eu/idabc/eupl
"""formulae downscaling cycles based on pmr/test_mass ratio """
import logging
from typing import Mapping

import pandas as pd

from . import invariants as inv
from . import io as wio
from .autograph import autographed

log = logging.getLogger(__name__)


@autographed(needs=["wltc_data/classes", ..., ...])
def decide_wltc_class(wltc_classes_data: Mapping[str, dict], p_m_ratio, v_max):
    """Vehicle classification according to Annex 1-2. """
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


@autographed(
    needs=[
        "wltc_class_data/downscale/p_max_values",
        "wltc_class_data/downscale/factor_coeffs",
        ...,
        ...,
        ...,
        ...,
        ...,
        ...,
    ]
)
def calc_f_dsc_orig(
    wltc_dsc_p_max_values, wltc_dsc_coeffs, p_rated, test_mass, f0, f1, f2, f_inertial,
):
    """
    Check if downscaling required, and apply it.

    :return: (float) the factor

    @see: Annex 1-7, p 68
    """
    c = wio.pstep_factory.get().cycle

    ## Max required power at critical point.
    #
    pmv = wltc_dsc_p_max_values[c.v]
    pma = wltc_dsc_p_max_values[c.a]
    p_req_max = (
        f0 * pmv + f1 * pmv ** 2 + f2 * pmv ** 3 + f_inertial * pma * pmv * test_mass
    ) / 3600.0
    r_max = p_req_max / p_rated

    (r0, a1, b1) = wltc_dsc_coeffs

    if r_max >= r0:
        f_dsc = a1 * r_max + b1
    else:
        f_dsc = 0

    return f_dsc


def calc_f_dsc(f_dsc_orig: float, f_dsc_threshold: float, f_dsc_decimals,) -> float:
    """
    ATTENTION: by the spec, f_dsc MUST be > 0.01 to apply, but
    in :file:`F_new_vehicle.form.txt:(3537, 3563, 3589)` a +0.5 is ADDED!
    (see CHANGES.rst)
    """
    f_dsc = inv.round1(f_dsc_orig, f_dsc_decimals)
    return 0 if f_dsc <= f_dsc_threshold else f_dsc


@autographed(
    needs=["wltc_class_data/v_cycle", ..., "wltc_class_data/downscale/phases",]
)
def calc_v_dsc(v_class: pd.Series, f_dsc, dsc_phases) -> pd.Series:
    """
    Downscale velocity profile by `f_dsc`.

    :return:
        the downscaled velocity profile, not-rounded
        (by the Spec should have 1 decimal only)

    - The Spec demarks 2 UP/DOWN phases with 3 time-points in `dsc_phases`,
      eg. for class3:

      - 1533: the "start" of downscaling
      - 1724: the "tip"
      - 1763: the "end"

    - V @ start & end (1533, 1763) must remain unchanged (by the Spec & asserted).
    - The "tip" is scaled with the UP-phase (by the Spec).
    - Those numbers are recorded in the model @ ``<class>/downscale/phases/``
    - The code asserts that the scaled V remains as smooth at tip as originally
      (and a bit more, due to the downscaling).

    Compare v075(class-3a) with AccDB:
        V_accdb V_python      diff%
        45.1636	45.1637	-0.000224059  # middle on tip(eg. 1724), both scale & recurse
        45.1636	45.1637	-0.000122941  # on tip, scale & recurse, round(1)
        45.1636	45.1637	-5.39439e-05  # on tip-1
        45.1636	45.1636	0             # on tip-1, scale & recurse, round(1)
        45.1636	45.1637	-6.48634e-05  # on tip+1
        45.1636	45.1636	0             # on tip+1, scale & recurse, round(1)

    @see: Annex 1-8, p 64-68
    """
    # return downscale_by_recursing(V, f_dsc, phases)
    return downscale_by_scaling(v_class, f_dsc, dsc_phases)


def downscale_by_recursing(V, f_dsc, phases):
    """Downscale by recursing (according to the Spec). """
    V_DSC = V.copy()
    (t0, t1, t2) = phases

    ## Accelaration phase
    #
    for t in range(t0, t1):
        a = V[t + 1] - V[t]
        V_DSC[t + 1] = V_DSC[t] + a * (1 - f_dsc)

    ## Deceleration phase
    #
    f_corr = (V_DSC[t1] - V[t2]) / (V[t1] - V[t2])
    for t in range(t1 + 1, t2):
        a = V[t] - V[t - 1]
        V_DSC[t] = V_DSC[t - 1] + a * f_corr

    return V_DSC


def downscale_by_scaling(V: pd.Series, f_dsc, phases) -> pd.Series:
    """
    Multiply the UP/DOWN phases with 2 factors (no recurse, against the Spec).

    Example, for class-3:

    .. math::

        V_{dsc}[1520:1725] = V[1520] + (V[1520:1725] - V[1520]) \times (1 - f_{dsc})

        V_{dsc}[1526:1743] = V[1743] + (V[1526:1743] - V[1743]) \times f_{corr}

    """
    V_DSC = V.copy()
    (t0, t1, t2) = phases
    f_scale = 1 - f_dsc

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

    ## FIXME: `f_scale` multipliers should have been on the other side(!) of inequality,
    #  but then assertion fails frequently.
    assert f_scale * abs(V_DSC[t1 + 1] - V_DSC[t1]) <= abs(V[t1 + 1] - V[t1]), (
        f"Smooth-tip violation diff_V_DSC({abs(V_DSC[t1 + 1] - V_DSC[t1])})"
        f" !<= diff_V({abs(V[t1 + 1] - V[t1])})!"
    )

    return V_DSC
