#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2013-2020 European Commission (JRC);
# Licensed under the EUPL (the 'Licence');
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at: http://ec.europa.eu/idabc/eupl

import itertools as itt
import logging
import unittest

import numpy as np
import pandas as pd
import pytest

from graphtik import compose, operation
from wltp import cycles, datamodel, downscale
from wltp import invariants as inv
from wltp import io as wio
from wltp.invariants import round1

from .vehdb import oneliner

log = logging.getLogger(__name__)


def test_smoke1():
    test_mass = 1577.3106
    p_rated = 78.6340
    v_max = 186.4861
    f0 = 152.5813
    f1 = 307.5789
    f2 = 0.0486
    f_inertial = 1.03  # TODO: get it from schema-default
    ## Decide WLTC-class.
    #
    wltc = datamodel.get_wltc_data()
    wltc_class = downscale.decide_wltc_class(
        wltc["classes"], p_rated / test_mass, v_max
    )
    class_data = wltc["classes"][wltc_class]
    V = pd.Series(class_data["V_cycle"])

    f_dsc_threshold = 0.01  # TODO: get it from schema-default
    f_dsc_decimals = 3  # TODO: get it from schema-default
    dsc_data = class_data["downscale"]
    phases = dsc_data["phases"]
    p_max_values = dsc_data["p_max_values"]
    downsc_coeffs = dsc_data["factor_coeffs"]
    f_dsc_raw = downscale.calc_f_dsc_raw(
        p_max_values, downsc_coeffs, p_rated, test_mass, f0, f1, f2, f_inertial,
    )
    f_dsc = downscale.calc_f_dsc(f_dsc_raw, f_dsc_threshold, f_dsc_decimals,)
    if f_dsc > 0:
        V = downscale.calc_V_dsc_raw(V, f_dsc, phases)
        # print(
        #     "Class(%s), f_dnscl(%s), DIFFs:\n%s" % (wclass, f_dsc, diffs[bad_ix])
        # )
        # plt.plot(V, "r")
        # plt.plot(V1, "b")
        # plt.plot(V2, "g")
        # plt.show()
        # raise AssertionError(
        #     "Class(%s), f_dnscl(%s)" % (wclass, f_dsc)
        # )


def test_smoke2():
    wclasses = datamodel.get_wltc_data()["classes"]
    test_data = [
        (pd.Series(wclass["V_cycle"]), wclass["downscale"]["phases"], f_dsc)
        for wclass in wclasses.values()
        for f_dsc in np.linspace(0.1, 1, 10)
    ]

    for (V, phases, f_dsc) in test_data:
        downscale.calc_V_dsc_raw(V, f_dsc, phases)


_wltc = datamodel.get_wltc_data()


@pytest.mark.parametrize("wclass", _wltc["classes"])
def test_recurse_vs_scaling(wclass):
    """Compare downcalings with the both methods: simplified (scale by multiply) and by_the_spec (iterativelly scale accelerations)."""
    from matplotlib import pyplot as plt

    # Scaling == Recurse only with this!!
    def double_round(n, decimals):
        return round1(round1(n, decimals + 2), decimals)

    pd_opts = [
        "display.max_rows",
        None,
        "display.max_columns",
        None,
        "display.precision",
        16,
        "display.float_format",
        "{:0.16f}".format,
        "display.width",
        160,
    ]
    v_decimals = 1
    class_data = _wltc["classes"][wclass]
    V = pd.Series(class_data["V_cycle"])
    phases = class_data["downscale"]["phases"]

    bad_accuracies, bad_rounds = {}, {}
    for f_dsc in np.arange(0, 4, 0.1):
        V1 = downscale.downscale_by_recursing(V, f_dsc, phases)
        V2 = downscale.downscale_by_scaling(V, f_dsc, phases)

        bad_ix = ~np.isclose(V1, V2)
        if bad_ix.any():
            errs = pd.concat(
                (V1, V2, V1 - V2), axis=1, keys=["recurse", "rescale", "diff"]
            )[bad_ix]
            bad_accuracies[f_dsc] = errs

        bad_ix = (
            double_round(V1, v_decimals).to_numpy()
            != double_round(V2, v_decimals).to_numpy()
        )
        if bad_ix.any():
            bad_rounds[f_dsc] = pd.concat(
                (V1, V2, (V1 - V2).abs()), axis=1, keys=["recurse", "rescale", "diff"]
            )[bad_ix]

    if bad_accuracies:
        errs = pd.concat((bad_accuracies.values()), axis=0, keys=bad_accuracies.keys())
        with pd.option_context(*pd_opts):
            pytest.fail(f"{wclass}: ACCURACY errors!\n{errs}\n{errs.describe()}")

    if bad_rounds:
        rounded = (double_round(i, v_decimals) for i in bad_rounds.values())
        rounded = pd.concat(rounded, axis=0, keys=bad_rounds.keys())
        precise = pd.concat((bad_rounds.values()), axis=0, keys=bad_rounds.keys())
        errs = pd.concat((rounded, precise), axis=1, keys=["rounded", "precise"])

        with pd.option_context(*pd_opts):
            pytest.fail(f"{wclass}: ROUNDING errors!\n{errs}\n{errs.describe()}")


def test_dsc_pipelines(wltc_class):
    aug = wio.make_autograph()
    funcs = [
        cycles.get_wltc_class_data,
        *downscale.downscale_pipeline().ops,
        *downscale.compensate_capped_pipeline().ops,
        *cycles.v_distances_pipeline().ops,
        # fake dsc & cap
        operation(None, "FAKE.V_dsc", "wltc_class_data/V_cycle", "V_dsc"),
    ]
    ops = [aug.wrap_fn(fn) for fn in funcs]
    pipe = compose(..., *ops)
    inp = {
        "wltc_data": datamodel.get_wltc_data(),
        "wltc_class": wltc_class,
        "v_cap": 60,  # class1 max(V) is 60.4
    }
    sol = pipe.compute(inp)
    assert len(sol["compensate_phases_t_extra"]) == len(sol["class_phase_boundaries"])

    exp_t_missing = ([0, 1, 0], [0, 10, 43, 192], [0, 8, 81, 203], [0, 8, 81, 203])
    assert sol["compensate_phases_t_extra"].tolist() == exp_t_missing[wltc_class]

    exp_compensated_phases = [
        [(0, 589), (590, 1023), (1023, 1612)],
        [(0, 589), (599, 1032), (1075, 1530), (1722, 2045)],
        [(0, 589), (597, 1030), (1111, 1566), (1769, 2092)],
        [(0, 589), (597, 1030), (1111, 1566), (1769, 2092)],
    ]
    compensated_phases = sol["compensated_phase_boundaries"]
    assert compensated_phases == exp_compensated_phases[wltc_class]

    V_compensated = sol["V_compensated"]
    assert compensated_phases[-1][-1] == V_compensated.index[-1]
    assert (sol["V_dsc"].sum() - V_compensated.sum()) < inp["v_cap"]

    exp_compensated_distances = [
        [11988.4, 29146.9, 41135.3],
        [11162.2, 28209.7, 51666.1, 70103.2],
        [11140.3, 28110.5, 50564.1, 69069.5],
        [11140.3, 28241.0, 50779.8, 69285.2]
    ]
    compensated_distances = sol["compensated_distances"]
    assert (inv.vround(compensated_distances['cumsum']) == exp_compensated_distances[wltc_class]).all()

    ## No CAPPING

    inp = {
        "wltc_data": datamodel.get_wltc_data(),
        "wltc_class": wltc_class,
        "v_cap": 0,
    }
    sol = pipe.compute(inp)
    assert len(sol["compensate_phases_t_extra"]) == len(sol["class_phase_boundaries"])

    regular_phases = sol["class_phase_boundaries"]
    V_compensated = sol["V_compensated"]
    assert regular_phases[-1][-1] == V_compensated.index[-1]
    assert (sol["V_dsc"].sum() == sol["V_compensated"].sum())
