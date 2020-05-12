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

from wltp import datamodel
from wltp.downscale import (
    calc_f_dsc_orig,
    calc_f_dsc,
    calc_v_dsc,
    decide_wltc_class,
    downscale_by_recursing,
    downscale_by_scaling,
)
from wltp.invariants import round1

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
    wltc_class = decide_wltc_class(wltc, p_rated / test_mass, v_max)
    class_data = wltc["classes"][wltc_class]
    V = pd.Series(class_data["v_cycle"])

    f_dsc_threshold = 0.01  # TODO: get it from schema-default
    f_dsc_decimals = 3  # TODO: get it from schema-default
    dsc_data = class_data["downscale"]
    phases = dsc_data["phases"]
    p_max_values = dsc_data["p_max_values"]
    downsc_coeffs = dsc_data["factor_coeffs"]
    f_dsc_orig = calc_f_dsc_orig(
        p_max_values,
        downsc_coeffs,
        p_rated,
        test_mass,
        f0,
        f1,
        f2,
        f_inertial,
    )
    f_dsc = calc_f_dsc(
        f_dsc_orig,
        f_dsc_threshold,
        f_dsc_decimals,
    )
    if f_dsc > 0:
        V = calc_v_dsc(V, f_dsc, phases)
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
        (pd.Series(wclass["v_cycle"]), wclass["downscale"]["phases"], f_dsc)
        for wclass in wclasses.values()
        for f_dsc in np.linspace(0.1, 1, 10)
    ]

    for (V, phases, f_dsc) in test_data:
        calc_v_dsc(V, f_dsc, phases)


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
    V = pd.Series(class_data["v_cycle"])
    phases = class_data["downscale"]["phases"]

    bad_accuracies, bad_rounds = {}, {}
    for f_dsc in np.arange(0, 4, 0.1):
        V1 = downscale_by_recursing(V, f_dsc, phases)
        V2 = downscale_by_scaling(V, f_dsc, phases)

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
