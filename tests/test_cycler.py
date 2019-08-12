#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2013-2019 European Commission (JRC);
# Licensed under the EUPL (the 'Licence');
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at: http://ec.europa.eu/idabc/eupl
import itertools as itt

import pandas as pd
import pytest
from jsonschema import ValidationError
from tests import vehdb

from wltp import cycler, datamodel, engine, vehicle
from wltp.cycler import CycleBuilder, CycleMarker
from wltp.vehicle import calc_default_resistance_coeffs


@pytest.fixture
def gwots():
    ## Need a 2-level multiindex columns for swaplevel().
    return pd.DataFrame({("the items", "the gears"): []})


def test_identify_conjecutive_truths_repeat_threshold_1_is_identical():
    V = datamodel.get_class_v_cycle(0)
    A = -V.diff(-1)
    cm = CycleMarker(phase_repeat_threshold=1)

    col1 = (V > 1) & (A < 0)
    col2 = cm._identify_conjecutive_truths((V > 1) & (A < 0), right_edge=False)
    assert col2.equals(col1)

    col2 = cm._identify_conjecutive_truths((V > 1) & (A < 0), right_edge=True)
    assert col2.equals(col1 | col1.shift())


@pytest.mark.parametrize("wltc_class, exp", [(0, 12), (1, 9), (2, 9), (3, 9)])
def test_cycle_init_flag(wltc_class, exp, gwots):
    V = datamodel.get_class_v_cycle(wltc_class)
    cb = CycleBuilder(V)
    CycleMarker().add_phase_markers(cb.cycle, cb.V, cb.A)
    assert cb.cycle.init.sum() == exp


@pytest.mark.parametrize("wltc_class", range(4))
def test_decelstop(wltc_class):
    V = datamodel.get_class_v_cycle(wltc_class)
    cb = CycleBuilder(V)
    cycle = cycler.CycleMarker().add_phase_markers(cb.cycle, cb.V, cb.A)
    n_stops = (cycle["stop"].astype(int).diff() < 0).sum(None)
    n_decels = (cycle["decel"].astype(int).diff() < 0).sum(None)
    n_decelstops = (cycle["decelstop"].astype(int).diff() < 0).sum(None)
    assert n_decelstops < n_decels
    ##  The initial stop has no deceleration before it BUT no diff >0 either!
    assert n_decelstops == n_stops


# TODO: move `t_start` checkj in validations pipeline.
@pytest.mark.parametrize(
    "wltc_class, t_start, err",
    zip(
        range(4),
        (800, 150),
        (
            ValidationError("before the 1st cycle-part"),
            ValidationError("on a cycle stop"),
        ),
    ),
)
def test_validate_t_start(wltc_class, t_start, err):
    V = datamodel.get_class_v_cycle(wltc_class)
    wltc_parts = datamodel.get_class_parts_limits(wltc_class)

    cb = CycleBuilder(V)
    cb.cycle = cycler.CycleMarker().add_phase_markers(cb.cycle, cb.V, cb.A)
    with pytest.raises(type(err), match=str(err)):
        for err in cb.validate_nims_t_start(t_start, wltc_parts):
            raise err


def test_flatten_columns():
    cb = CycleBuilder(pd.Series([1, 2], name="yy"))
    cols = pd.MultiIndex.from_tuples([("a", "aa"), ("b", "")], names=("gear", "item"))
    fcols = cb.flatten_columns(cols)
    infcols = cb.inflate_columns(fcols)
    assert cols.equals(infcols)
    assert cols.names == infcols.names
    with pytest.raises(AssertionError, match="MultiIndex?"):
        cb.inflate_columns(cols)


def test_full_build_smoketest(h5_accdb):
    vehnum = 8
    prop, wot, n2vs = vehdb.load_vehicle_accdb(h5_accdb, vehnum)
    renames = vehdb.accdb_renames()
    prop = prop.rename(renames)
    wot = wot.rename(renames, axis=1)
    wot["n"] = wot.index

    gwots = engine.interpolate_wot_on_v_grid2(wot, n2vs)
    gwots = engine.calc_p_avail_in_gwots(gwots, SM=0.1)
    V = datamodel.get_class_v_cycle(3)  # v008's class

    cb = cycler.CycleBuilder(V)
    cb.cycle = cycler.CycleMarker().add_phase_markers(cb.cycle, cb.V, cb.A)

    kr = 1.03
    SM = 0.1
    cb.cycle["p_req"] = vehicle.calc_power_required(
        cb.V, cb.A, prop.test_mass, prop.f0, prop.f1, prop.f2, kr
    )
    cb.add_wots(gwots)

    acc_cycle = vehdb.load_vehicle_nodes(h5_accdb, vehnum, "cycle")

    diffs = {}

    def cmpr_cols(c1, c2):
        diffs[c1.name] = (c1 - c2).abs()

    acc_cycle["P_tot"], "p_required"
