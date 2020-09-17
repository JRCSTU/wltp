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
    ops = aug.wrap_funcs(
        [
            cycles.get_wltc_class_data,
            cycles.get_class_phase_boundaries,
            cycles.make_class_phases_grouper,
            cycles.calc_wltc_distances,
            downscale.make_compensated_phase_boundaries,
        ]
    )

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
    ops = aug.wrap_funcs(
        [
            vehicle.calc_unladen_mass,
            vehicle.calc_mro,
            vehicle.calc_p_m_ratio,
            vehicle.decide_wltc_class,
        ]
    )
    pipe = compose(..., *ops, **pipeline_kw)

    return pipe


@fnt.lru_cache()
def p_req_pipeline(aug: autog.Autograph = None, **pipeline_kw) -> Pipeline:
    """
    Pipeline to provide `P_req` traces (Annex 2, 9).

    .. graphtik::
        :height: 600
        :hide:
        :name: p_req_pipeline

        >>> pipe = p_req_pipeline()
    """
    aug = aug or wio.make_autograph()
    ops = aug.wrap_funcs(
        [
            vehicle.calc_p_resist,
            vehicle.calc_inertial_power,
            vehicle.calc_required_power,
        ]
    )
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
    ops = aug.wrap_funcs(
        [
            engine.interpolate_wot_on_v_grid,
            engine.attach_p_avail_in_gwots,
            *p_req_pipeline(aug).ops,
        ]
    )
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
    ops = aug.wrap_funcs(
        [
            engine.interpolate_wot_on_v_grid,
            vehicle.calc_p_resist,
            engine.attach_p_avail_in_gwots,
            vmax.calc_v_max,
        ]
    )
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
    ops = aug.wrap_funcs(
        [
            cycles.get_wltc_class_data,
            downscale.calc_f_dsc_raw,
            downscale.calc_f_dsc,
            downscale.calc_V_dsc_raw,
            downscale.round_calc_V_dsc,
            downscale.calc_V_capped,
        ]
    )
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
    ops = aug.wrap_funcs(
        [
            cycles.get_wltc_class_data,
            cycles.get_class_phase_boundaries,
            cycles.make_class_phases_grouper,
            downscale.calc_V_capped,
            downscale.calc_compensate_phases_t_extra_raw,
            downscale.round_compensate_phases_t_extra,
            downscale.calc_V_compensated,
        ],
        exclude=["calc_compensated_distances", "make_compensated_phases_grouper"],
    )
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
    aug = aug or wio.make_autograph()
    ops = aug.wrap_funcs(
        [
            *wltc_class_pipeline(aug).ops,
            *vmax_pipeline(aug).ops,
            *downscale_pipeline(aug).ops,
            *compensate_capped_pipeline(aug).ops,
            *v_distances_pipeline(aug).ops,
        ]
    )
    pipe = compose(..., *ops, **pipeline_kw)

    return pipe


@fnt.lru_cache()
def n_max_pipeline(aug: autog.Autograph = None, **pipeline_kw) -> Pipeline:
    """
    Pipeline to provide `n_max`\s (Annex 2, 2.g).

    .. graphtik::
        :hide:
        :name: n_max_pipeline

        >>> pipe = n_max_pipeline()
    """
    aug = aug or wio.make_autograph()
    ops = aug.wrap_funcs(
        [
            engine.calc_n2v_g_vmax,
            engine.calc_n95,
            engine.calc_n_max_cycle,
            engine.calc_n_max_vehicle,
            engine.calc_n_max,
        ]
    )
    pipe = compose(..., *ops, **pipeline_kw)

    return pipe


@fnt.lru_cache()
def cycler_pipeline(
    aug: autog.Autograph = None, domain=("cycle", None), **pipeline_kw
) -> Pipeline:
    """
    Main pipeline to "run" the cycle.

    .. graphtik::
        :height: 600
        :hide:
        :name: cycler_pipeline

        >>> pipe = cycler_pipeline()
    """
    aug = aug or wio.make_autograph(domain=domain)
    ops = aug.wrap_funcs(
        [
            cycles.get_wltc_class_data,
            cycler.init_cycle_velocity,
            cycler.calc_acceleration,
            cycles.get_class_phase_boundaries,
            cycler.attach_class_phase_markers,
            cycler.calc_phase_accel_raw,
            cycler.calc_phase_run_stop,
            cycler.PhaseMarker,
            cycler.PhaseMarker.calc_phase_decel,
            cycler.PhaseMarker.calc_phase_initaccel,
            cycler.PhaseMarker.calc_phase_stopdecel,
            cycler.PhaseMarker.calc_phase_up,
            *gwots_pipeline(aug).ops,
            *p_req_pipeline(aug).ops,
            *n_max_pipeline(aug).ops,
            wio.GearMultiIndexer.from_df,
            cycler.attach_wots,
            cycler.derrive_initial_gear_flags,
            cycler.derrive_ok_n_flags,
            cycler.concat_frame_columns,
            cycler.derrive_ok_gears,
            cycler.make_incrementing_gflags,
            cycler.make_G_min,
            cycler.make_G_max0,
        ],
    )
    pipe = compose(..., *ops, **pipeline_kw)

    return pipe
