#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2013-2020 European Commission (JRC);
# Licensed under the EUPL (the 'Licence');
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at: http://ec.europa.eu/idabc/eupl
"""
All :term:`pipeline` definitions for running the WLTP gear-shifting algorithm

.. Workaround sphinx-doc/sphinx#6590
.. doctest::
    :hide:

    >>> from wltp.pipelines import *
    >>> __name__ = "wltp.pipelines"
"""
import functools as fnt

from graphtik import compose, keyword, modify, operation, optional, sfxed, vararg
from graphtik.pipeline import Pipeline

from . import autograph as autog
from . import cycler, cycles, downscale, engine
from . import io as wio
from . import vehicle, vmax


calc_wltc_distances = operation(
    cycles.calc_wltc_distances,
    needs=["wltc_class_data/V_cycle", "class_phases_grouper"],
    provides="wltc_distances",
)
calc_dsc_distances = calc_wltc_distances.withset(
    name="calc_dsc_distances",
    needs=["V_dsc", "class_phases_grouper"],
    provides="dsc_distances",
)
calc_capped_distances = calc_wltc_distances.withset(
    name="calc_capped_distances",
    needs=["V_capped", "class_phases_grouper"],
    provides="capped_distances",
)

calc_compensated_distances = calc_wltc_distances.withset(
    name="calc_compensated_distances",
    needs=["V_compensated", "compensated_phases_grouper"],
    provides="compensated_distances",
)


make_compensated_phases_grouper = operation(
    cycles.make_class_phases_grouper,
    name="make_compensated_phases_grouper",
    needs="compensated_phase_boundaries",
    provides="compensated_phases_grouper",
)


@fnt.lru_cache()
def v_distances_pipeline(aug: autog.Autograph = None, **pipeline_kw) -> Pipeline:
    """
    Pipeline to provide per-phase & total distances for `V_cycle`, `V_dsc`, `V_capped` & `V_compensated`.

    .. graphtik::
        :hide:
        :name: v_distances_pipeline

        >>> pipe = v_distances_pipeline()
    """
    aug = aug or wio.make_autograph()
    funcs = [
        cycles.get_wltc_class_data,
        cycles.get_class_phase_boundaries,
        cycles.make_class_phases_grouper,
        calc_wltc_distances,
        calc_dsc_distances,
        calc_capped_distances,
        downscale.make_compensated_phase_boundaries,
        make_compensated_phases_grouper,
        calc_compensated_distances,
    ]

    ops = [aug.wrap_fn(fn) for fn in funcs]
    pipe = compose(..., *ops, **pipeline_kw)

    return pipe


@fnt.lru_cache()
def wltc_class_pipeline(aug: autog.Autograph = None, **pipeline_kw) -> Pipeline:
    """
    Pipeline to provide `p_m_ratio` (Annex 1, 2).

    .. graphtik::
        :height: 600
        :hide:
        :name: wltc_class_pipeline

        >>> pipe = wltc_class_pipeline()
    """
    aug = aug or wio.make_autograph()
    funcs = [
        vehicle.calc_unladen_mass,
        vehicle.calc_mro,
        vehicle.calc_p_m_ratio,
        vehicle.decide_wltc_class,
    ]
    ops = [aug.wrap_fn(fn) for fn in funcs]
    pipe = compose(..., *ops, **pipeline_kw)

    return pipe


@fnt.lru_cache()
def p_req_pipeline(
    aug: autog.Autograph = None, domains=None, **pipeline_kw
) -> Pipeline:
    """
    Pipeline to provide `V_compensated` traces (Annex 1, 9).

    .. graphtik::
        :height: 600
        :hide:
        :name: p_req_pipeline

        >>> pipe = p_req_pipeline()
    """
    aug = aug or wio.make_autograph()
    funcs = [
        vehicle.calc_p_resist,
        vehicle.calc_inertial_power,
        vehicle.calc_required_power,
    ]
    ops = [aug.wrap_fn(fn) for fn in funcs]
    pipe = compose(..., *ops, **pipeline_kw)

    return pipe


@fnt.lru_cache()
def gwots_pipeline(aug: autog.Autograph = None, **pipeline_kw) -> Pipeline:
    """
    Pipeline to provide `P_avail` for each gear (Annex 2, 3.4).

    .. graphtik::
        :hide:
        :name: gwots_pipeline

        >>> pipe = gwots_pipeline()
    """
    aug = aug or wio.make_autograph()
    funcs = [
        engine.interpolate_wot_on_v_grid,
        engine.attach_p_avail_in_gwots,
        vehicle.attach_p_resist_in_gwots,
    ]
    ops = [aug.wrap_fn(fn) for fn in funcs]
    pipe = compose(..., *ops, **pipeline_kw)

    return pipe


@fnt.lru_cache()
def vmax_pipeline(aug: autog.Autograph = None, **pipeline_kw) -> Pipeline:
    """
    Pipeline to provide vehicle's `v_max` (Annex 2, 2.i).

    .. graphtik::
        :hide:
        :name: vmax_pipeline

        >>> pipe = vmax_pipeline()
    """
    aug = aug or wio.make_autograph()
    funcs = [
        *gwots_pipeline().ops,
        vmax.calc_v_max,
    ]
    ops = [aug.wrap_fn(fn) for fn in funcs]
    pipe = compose(..., *ops, **pipeline_kw)

    return pipe


@fnt.lru_cache()
def downscale_pipeline(aug: autog.Autograph = None, **pipeline_kw) -> Pipeline:
    """
    Pipeline to provide `V_dsc` & `V_capped` traces (Annex 1, 8.2 & 8.3).

    .. graphtik::
        :hide:
        :name: downscale_pipeline

        >>> pipe = downscale_pipeline()
    """
    aug = aug or wio.make_autograph()
    funcs = [
        cycles.get_wltc_class_data,
        downscale.calc_f_dsc_raw,
        downscale.calc_f_dsc,
        downscale.calc_V_dsc_raw,
        downscale.round_calc_V_dsc,
        downscale.calc_V_capped,
    ]
    ops = [aug.wrap_fn(fn) for fn in funcs]
    pipe = compose(..., *ops, **pipeline_kw)

    return pipe


@fnt.lru_cache()
def compensate_capped_pipeline(aug: autog.Autograph = None, **pipeline_kw) -> Pipeline:
    """
    Pipeline to provide `V_compensated` from `V_capped` trace (Annex 1, 9).

    .. graphtik::
        :hide:
        :name: compensate_capped_pipeline

        >>> pipe = compensate_capped_pipeline()
    """
    aug = aug or wio.make_autograph()
    funcs = [
        cycles.get_wltc_class_data,
        calc_dsc_distances,
        calc_capped_distances,
        cycles.get_class_phase_boundaries,
        cycles.make_class_phases_grouper,
        downscale.calc_V_capped,
        downscale.calc_compensate_phases_t_extra_raw,
        downscale.round_compensate_phases_t_extra,
        downscale.calc_V_compensated,
    ]
    ops = [aug.wrap_fn(fn) for fn in funcs]
    pipe = compose(..., *ops, **pipeline_kw)

    return pipe


@fnt.lru_cache()
def scale_trace_pipeline(aug: autog.Autograph = None, **pipeline_kw) -> Pipeline:
    """
    Main pipeline to scale the Velocity trace:

    .. graphtik::
        :height: 800
        :hide:
        :name: scale_trace_pipeline

        >>> netop = scale_trace_pipeline()

    **Example:**

        >>> mdl = {"n_idle": 500, "n_rated": 3000, "p_rated": 80, "t_cold_end": 470}
    """
    funcs = [
        *wltc_class_pipeline().ops,
        *vmax_pipeline().ops,
        *downscale_pipeline().ops,
        *compensate_capped_pipeline().ops,
        *v_distances_pipeline().ops,
    ]
    aug = aug or wio.make_autograph()
    ops = [aug.wrap_fn(fn) for fn in funcs]
    pipe = compose(..., *ops, **pipeline_kw,)

    return pipe


@fnt.lru_cache()
def cycler_pipeline(aug: autog.Autograph = None, **pipeline_kw) -> Pipeline:
    """
    Main pipeline to "run" the cycle.

    .. graphtik::
        :height: 600
        :hide:
        :name: cycler_pipeline

        >>> pipe = cycler_pipeline()
    """
    aug = aug or wio.make_autograph(domains=("cycle", None))
    funcs = [
        cycles.get_wltc_class_data,
        cycler.get_forced_cycle,
        cycler.init_cycle_velocity,
        cycler.calc_acceleration,
        cycles.get_class_phase_boundaries,
        cycler.attach_class_v_phase_markers,
        cycler.calc_class_va_phase_markers,
        *p_req_pipeline(aug).ops,
        # wio.GearMultiIndexer.from_df,
        # attach_wots,
    ]
    ops = [aug.wrap_fn(fn) for fn in funcs]
    pipe = compose(..., *ops, **pipeline_kw)

    return pipe
