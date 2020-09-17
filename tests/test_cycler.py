#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2013-2020 European Commission (JRC);
# Licensed under the EUPL (the 'Licence');
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at: http://ec.europa.eu/idabc/eupl
import itertools as itt
import textwrap

import numpy as np
import pandas as pd
import pytest
from jsonschema import ValidationError
from tests import goodvehicle, vehdb

from graphtik import compose, config, operation, sfxed
from wltp import cycler, cycles, datamodel, engine
from wltp import io as wio
from wltp import nmindrive, pipelines, vehicle
from wltp.cycler import CycleBuilder, PhaseMarker


@pytest.fixture
def gwots():
    ## Need a 2-level multiindex columns for swaplevel().
    return pd.DataFrame({("the items", "the gears"): []})


def test_identify_consecutive_truths_repeat_threshold_1_is_identical():
    V = datamodel.get_class_v_cycle(0)
    A = -V.diff(-1)
    pm = PhaseMarker(phase_repeat_threshold=1)

    col1 = (V > 1) & (A < 0)
    col2 = pm._identify_consecutive_truths((V > 1) & (A < 0), right_edge=False)
    assert col2.equals(col1)

    col2 = pm._identify_consecutive_truths((V > 1) & (A < 0), right_edge=True)
    assert col2.equals(col1 | col1.shift())


@pytest.mark.parametrize("wltc_class, exp", [(0, 320), (1, 300), (2, 160), (3, 158)])
def test_cycle_initaccel(wltc_class, exp, gwots):
    V = datamodel.get_class_v_cycle(wltc_class)
    cb = CycleBuilder(V)
    PhaseMarker().add_transition_markers(cb.cycle, cb.V, cb.A)
    print(cb.cycle.initaccel.sum())
    assert cb.cycle.initaccel.sum() == exp


@pytest.mark.parametrize("wltc_class", range(4))
def test_stopdecel(wltc_class):
    V = datamodel.get_class_v_cycle(wltc_class)
    cb = CycleBuilder(V)
    cycle = cycler.PhaseMarker().add_transition_markers(cb.cycle, cb.V, cb.A)
    n_stops = (cycle["stop"].astype(int).diff() < 0).sum(None)
    n_decels = (cycle["decel"].astype(int).diff() < 0).sum(None)
    n_stopdecels = (cycle["stopdecel"].astype(int).diff() < 0).sum(None)
    assert n_stopdecels < n_decels
    ##  The initial stop has no deceleration before it BUT no diff >0 either!
    assert n_stopdecels == n_stops


@pytest.mark.parametrize(
    "wltc_class, t_cold_end, err",
    zip(
        range(4),
        (800, 150),
        (
            ValidationError("before the 1st cycle-part"),
            ValidationError("on a cycle stop"),
        ),
    ),
)
def test_validate_t_start(wltc_class, t_cold_end, err):
    """
    .. TODO:: move `t_cold_end` check in validations pipeline.
    """
    V = datamodel.get_class_v_cycle(wltc_class)
    wltc_parts = datamodel.get_class_parts_limits(wltc_class)

    cb = CycleBuilder(V)
    cb.cycle = cycler.PhaseMarker().add_transition_markers(cb.cycle, cb.V, cb.A)
    with pytest.raises(type(err), match=str(err)):
        for err in cb.validate_nims_t_cold_end(t_cold_end, wltc_parts):
            raise err


def test_flatten_columns():
    cols = pd.MultiIndex.from_tuples([("a", "aa"), ("b", "")], names=("gear", "item"))

    fcols = wio.flatten_columns(cols)
    infcols = wio.inflate_columns(fcols)
    assert cols.equals(infcols)
    assert cols.names == infcols.names
    with pytest.raises(AssertionError, match="MultiIndex?"):
        wio.inflate_columns(cols)


def test_full_build_smoketest(h5_accdb):
    vehnum = 8
    veh_class = 3  # v008's class
    t_cold_end = 470  # stop in all classes
    prop, wot, n2vs = vehdb.load_vehicle_accdb(h5_accdb, vehnum)
    renames = vehdb.accdb_renames()
    prop = prop.rename(renames)
    wot = wot.rename(renames, axis=1)
    wot["n"] = wot.index

    V = datamodel.get_class_v_cycle(veh_class)
    wltc_parts = datamodel.get_class_parts_limits(veh_class)

    pm = cycler.PhaseMarker()
    cb = cycler.CycleBuilder(V)
    cb.cycle = pm.add_transition_markers(cb.cycle, cb.V, cb.A)
    for err in cb.validate_nims_t_cold_end(t_cold_end, wltc_parts):
        raise err
    cb.cycle = pm.add_class_phase_markers(cb.cycle, wltc_parts)

    SM = 0.1
    gwots = engine.interpolate_wot_on_v_grid(wot, n2vs)
    gwots = engine.attach_p_avail_in_gwots(gwots, f_safety_margin=SM)
    gwots["p_resist"] = vehicle.calc_p_resist(gwots.index, prop.f0, prop.f1, prop.f2)

    kr = 1.03
    cb.add_wots(gwots)

    cb.cycle["p_inert"] = vehicle.calc_inertial_power(cb.V, cb.A, prop.test_mass, kr)
    cb.cycle["p_req"] = vehicle.calc_required_power(
        cb.cycle["p_inert"], cb.cycle["p_resist"]
    )

    acc_cycle = vehdb.load_vehicle_nodes(h5_accdb, vehnum, "cycle")

    diffs = {}

    def cmpr_cols(c1, c2):
        diffs[c1.name] = (c1 - c2).abs()

    acc_cycle["P_tot"], "p_required"


def test_forced_cycle_bad():
    with pytest.raises(AttributeError, match="'int' object has no attribute 'index'"):
        cycler.init_cycle_velocity(1)

    V = pd.Series([1, 2, 3], name="VV")
    with pytest.raises(ValueError, match=r"^Cycle had dupe columns: \['VV'\]"):
        cycler.init_cycle_velocity(V, V)


def test_forced_cycle_two_ramps():
    V = datamodel.get_class_v_cycle("class1").rename("foo")
    forced = pd.DataFrame({"V": np.hstack((np.r_[0:100:2], np.r_[98:0:-2]))})
    forced["A"] = 0

    cycle = cycler.init_cycle_velocity(V, forced)

    assert (cycle["V"].dropna() == forced.V).all()


def test_cycler_pipeline():  # wltc_class):
    wltc_class = 0
    aug = wio.make_autograph()
    ops = aug.wrap_funcs(
        [
            *pipelines.cycler_pipeline().ops,
            # fake Vs
            operation(
                lambda v: v.rename("V_dsc"),
                "FAKE.V_dsc",
                "wltc_class_data/V_cycle",
                "V_dsc",
            ),
        ]
    )
    pipe = compose(..., *ops)
    props = goodvehicle.goodVehicle()
    inp = {
        **props,
        "wltc_data": datamodel.get_wltc_data(),
        "wltc_class": wltc_class,
        "v_max": 190.3,
        "g_vmax": 6,
        # "n_min_drives":  nmindrive.mdl_2_n_min_drives.compute(props)
    }
    datamodel.validate_model(inp, additional_properties=True)

    with config.evictions_skipped(True):
        sol = pipe.compute(inp)

    exp = [
        ("t", ""),
        ("V_cycle", ""),
        ("V_dsc", ""),
        ("V", ""),
        ("A", ""),
        ("va_phase", ""),
        ("phase_1", ""),
        ("phase_2", ""),
        ("phase_3", ""),
        ("accel_raw", ""),
        ("run", ""),
        ("stop", ""),
        ("decel", ""),
        ("initaccel", ""),
        ("stopdecel", ""),
        ("up", ""),
        ("P_resist", ""),
        ("P_inert", ""),
        ("P_req", ""),
        ("n", "g1"),
        ("n", "g2"),
        ("n", "g3"),
        ("n", "g4"),
        ("n", "g5"),
        ("n", "g6"),
        ("n_norm", "g1"),
        ("n_norm", "g2"),
        ("n_norm", "g3"),
        ("n_norm", "g4"),
        ("n_norm", "g5"),
        ("n_norm", "g6"),
        ("p", "g1"),
        ("p", "g2"),
        ("p", "g3"),
        ("p", "g4"),
        ("p", "g5"),
        ("p", "g6"),
        ("p_avail", "g1"),
        ("p_avail", "g2"),
        ("p_avail", "g3"),
        ("p_avail", "g4"),
        ("p_avail", "g5"),
        ("p_avail", "g6"),
        ("p_avail_stable", "g1"),
        ("p_avail_stable", "g2"),
        ("p_avail_stable", "g3"),
        ("p_avail_stable", "g4"),
        ("p_avail_stable", "g5"),
        ("p_avail_stable", "g6"),
        ("p_norm", "g1"),
        ("p_norm", "g2"),
        ("p_norm", "g3"),
        ("p_norm", "g4"),
        ("p_norm", "g5"),
        ("p_norm", "g6"),
    ]

    print(list(sol["cycle"].columns))
    assert list(sol["cycle"].columns) == exp
    assert not (
        {
            "class_phase_boundaries",
            "n2v_g_vmax",
            "n95_low",
            "n95_high",
            "n_max_cycle",
            "n_max_vehicle",
            "n_max",
        }
        - sol.keys()
    )

    steps = [getattr(n, "name", n) for n in sol.plan.steps]
    steps_executed = [getattr(n, "name", n) for n in sol.executed]
    print("\n".join(textwrap.wrap(" ".join(steps), 90)))
    # print("\n".join(textwrap.wrap(" ".join(steps_executed), 90)))
    exp_steps = """
        get_wltc_class_data get_class_phase_boundaries PhaseMarker interpolate_wot_on_v_grid
        attach_p_avail_in_gwots calc_n2v_g_vmax calc_n95 calc_n_max_vehicle
        make_gwots_multi_indexer FAKE.V_dsc init_cycle_velocity calc_acceleration
        attach_class_phase_markers calc_phase_accel_raw calc_phase_run_stop calc_phase_decel
        calc_phase_initaccel calc_phase_stopdecel calc_phase_up calc_p_resist calc_inertial_power
        calc_required_power calc_n_max_cycle calc_n_max attach_wots derrive_initial_gear_flags
        derrive_ok_n_flags concat_frame_columns make_cycle_multi_indexer derrive_ok_gears
        make_incrementing_gflags make_G_min make_G_max0

        """.split()
    assert steps == steps_executed == exp_steps
