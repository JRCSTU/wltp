#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2013-2020 European Commission (JRC);
# Licensed under the EUPL (the 'Licence');
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at: http://ec.europa.eu/idabc/eupl
import itertools as itt

import pandas as pd
import pytest
from jsonschema import ValidationError
from tests import vehdb

from wltp import cycler, datamodel, engine
from wltp import io as wio
from wltp import vehicle
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
    PhaseMarker().add_phase_markers(cb.cycle, cb.V, cb.A)
    print(cb.cycle.initaccel.sum())
    assert cb.cycle.initaccel.sum() == exp


@pytest.mark.parametrize("wltc_class", range(4))
def test_stopdecel(wltc_class):
    V = datamodel.get_class_v_cycle(wltc_class)
    cb = CycleBuilder(V)
    cycle = cycler.PhaseMarker().add_phase_markers(cb.cycle, cb.V, cb.A)
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
    cb.cycle = cycler.PhaseMarker().add_phase_markers(cb.cycle, cb.V, cb.A)
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
    cb.cycle = pm.add_phase_markers(cb.cycle, cb.V, cb.A)
    for err in cb.validate_nims_t_cold_end(t_cold_end, wltc_parts):
        raise err
    cb.cycle = pm.add_class_phase_markers(cb.cycle, wltc_parts)

    SM = 0.1
    gwots = engine.interpolate_wot_on_v_grid(wot, n2vs)
    gwots = engine.attach_p_avail_in_gwots(gwots, SM=SM)
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
