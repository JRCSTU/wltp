#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2013-2020 European Commission (JRC);
# Licensed under the EUPL (the 'Licence');
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at: http://ec.europa.eu/idabc/eupl
"""
formulae downscaling cycles based on pmr/test_mass ratio

.. Workaround sphinx-doc/sphinx#6590
.. doctest::
    :hide:

    >>> from wltp.downscale import *
    >>> __name__ = "wltp.downscale"
"""
import logging
from typing import List, Optional, Tuple

import boltons.iterutils as itb
import numpy as np
import pandas as pd

from graphtik import operation

from . import autograph as autog
from . import cycles
from . import invariants as inv
from . import io as wio

log = logging.getLogger(__name__)


@autog.autographed(
    needs=[
        "wltc_class_data/downscale/p_max_values",
        "wltc_class_data/downscale/factor_coeffs",
        # TODO: autog accepts ... for all the rest needs.
        ...,
        ...,
        ...,
        ...,
        ...,
        ...,
    ]
)
def calc_f_dsc_raw(
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


def calc_f_dsc(f_dsc_raw: float, f_dsc_threshold: float, f_dsc_decimals,) -> float:
    """
    ATTENTION: by the spec, f_dsc MUST be > 0.01 to apply, but
    in :file:`F_new_vehicle.form.txt:(3537, 3563, 3589)` a +0.5 is ADDED!
    (see CHANGES.rst)
    """
    f_dsc = inv.round1(f_dsc_raw, f_dsc_decimals)
    return 0 if f_dsc <= f_dsc_threshold else f_dsc


@autog.autographed(
    needs=["wltc_class_data/V_cycle", ..., "wltc_class_data/downscale/phases",]
)
def calc_V_dsc_raw(v_class: pd.Series, f_dsc, dsc_phases) -> pd.Series:
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


round_calc_V_dsc = operation(
    inv.vround, name="round_calc_V_dsc", needs="V_dsc_raw", provides="V_dsc"
)


def calc_V_capped(V_dsc, v_cap):
    """Clip all values of `V_dsc` above `v_cap`."""
    return V_dsc.mask(V_dsc > v_cap, other=v_cap) if v_cap and v_cap > 0 else V_dsc


def calc_compensate_phases_t_extra_raw(
    v_cap: Optional[float], dsc_distances, capped_distances, class_phase_boundaries,
) -> pd.Series:
    """
    Extra time each phase needs to run at `v_cap` to equalize `V_capped` distance with `V_dsc`.

    :param v_cap:
        Compensation applies only if `v_cap` > 0.
    :return:
        a series with the # of extra secs for each phase (which may be full of 0s)

    This functions checks zero/null `v_cap` condition.
    """
    lengths = [
        len(i) for i in (class_phase_boundaries, dsc_distances, capped_distances)
    ]
    assert itb.same(
        lengths
    ), f"# of phases missmatched phase-distances: {lengths}\n  {locals()}"

    # What to return when decided not to compensate V-trace.
    no_compensation = pd.Series(0, index=capped_distances.index)

    if not v_cap or v_cap < 0:
        log.info("Skipped distance-compensation due to v_cap(%s)", v_cap)
        return no_compensation

    # Annex 1-9.2.1 simplified:
    #
    # - The 3.6 divisor cancels out with the t_diff formula below.
    #
    # - It also runs a 2-rolling-average window on the values,
    #   which in effect affects only the 1st and last elements
    #   which for phase-boundaries are both 0.
    phase_delta_s = dsc_distances["sum"] - capped_distances["sum"]

    if not phase_delta_s.any():
        log.info("Distance-compensation is not needed.")
        return no_compensation
    assert (phase_delta_s >= 0).all(), f"Capped less than downscaled!?? {locals()}"

    # Annex 1-9.2.2 simplified: 3.6 factor canceled out, above.
    delta_t = phase_delta_s / v_cap

    return delta_t


def round_compensate_phases_t_extra(
    compensate_phases_t_extra_raw: pd.Series,
) -> pd.Series:
    return inv.asint(inv.round1(compensate_phases_t_extra_raw))


def calc_V_compensated(
    v_cap,
    V_dsc: pd.Series,
    V_capped: pd.Series,
    compensate_phases_t_extra,
    class_phases_grouper,
) -> pd.Series:
    """
    Equalize capped-cycle distance to downscaled one.

    :param V_dsc:
        compared against `V_capped` to discover capped amples
    :param V_capped:
        compensated with extra `v_cap` samples as defined by `compensate_phases_t_extra`.
    :param v_cap:
        needed just for verification,

    :return:
        the compensated `V_capped`, same name & index

        .. Note::
            Cutting corners by grouping phases like `VA0`, so an extra 0 needed
            at the end when constructing the compensated trace.
    """
    diffs = V_dsc != V_capped
    if not diffs.any():
        return V_capped

    def compensate_phase(V, diffs, extra_steps):
        if not diffs.any():
            return (V,)

        t = diffs.idxmax()  # capping start time to split_and_extend
        assert V[t] == v_cap, (
            f"`V_capped` missmatch `v_cap`@t={t}: " f"{V[t]} != {v_cap}!\n  {locals()}"
        )

        # Need to slice 1st piece with open-right, but only `iloc` does that
        # (https://stackoverflow.com/a/45523811/548792)
        ti = V.index.get_loc(t)
        head = V.iloc[:ti]
        tail = V.loc[t:]
        wedge = [v_cap] * extra_steps
        return head, wedge, tail

    df = pd.concat((V_capped, diffs), axis=1)
    parts = []
    for extra_steps, (_, phase) in zip(
        compensate_phases_t_extra, df.groupby(class_phases_grouper)
    ):
        V, diffs = phase.iloc[:, 0], phase.iloc[:, 1]
        parts += compensate_phase(V, diffs, extra_steps)
    parts.append([0])  # convert A0 -1 length => full length

    # Assuming 1Hz, t0=0.
    V_compensated = pd.Series(np.hstack(parts))

    return V_compensated


def make_compensated_phase_boundaries(
    class_phase_boundaries, compensate_phases_t_extra
) -> List[Tuple[int, int]]:
    extra_t = compensate_phases_t_extra.cumsum()
    return [
        (a + extra_a, b + extra_b)
        for (a, b), extra_a, extra_b in zip(
            class_phase_boundaries, extra_t.shift(0, fill_value=0), extra_t
        )
    ]


make_compensated_phases_grouper = operation(
    cycles.make_class_phases_grouper,
    name="make_compensated_phases_grouper",
    needs="compensated_phase_boundaries",
    provides="compensated_phases_grouper",
)

calc_compensated_distances = cycles.calc_wltc_distances.withset(
    name="calc_compensated_distances",
    needs=["V_compensated", "compensated_phases_grouper"],
    provides="compensated_distances",
)
