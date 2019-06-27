#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2013-2019 European Commission (JRC);
# Licensed under the EUPL (the 'Licence');
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at: http://ec.europa.eu/idabc/eupl

import itertools as itt
import logging
import unittest

import numpy as np
import pandas as pd
import pytest

from wltp import model
from wltp.formulae import (
    calcDownscaleFactor,
    decideClass,
    downscale_by_recursing,
    downscale_by_scaling,
    downscaleCycle,
)

log = logging.getLogger(__name__)


def test_smoke():
    logging.getLogger().setLevel(logging.DEBUG)

    test_mass = 1577.3106
    p_rated = 78.6340
    v_max = 186.4861
    f0 = 152.5813
    f1 = 307.5789
    f2 = 0.0486
    f_inertial = 1.03  # TODO: get it from schema-default
    ## Decide WLTC-class.
    #
    wltc = model._get_wltc_data()
    wltc_class = decideClass(wltc, p_rated / test_mass, v_max)
    class_data = wltc["classes"][wltc_class]
    V = pd.Series(class_data["cycle"])

    f_downscale_threshold = 0.01  # TODO: get it from schema-default
    f_downscale_decimals = 3  # TODO: get it from schema-default
    dsc_data = class_data["downscale"]
    phases = dsc_data["phases"]
    p_max_values = dsc_data["p_max_values"]
    downsc_coeffs = dsc_data["factor_coeffs"]
    f_downscale = calcDownscaleFactor(
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
    )
    if f_downscale > 0:
        V = downscaleCycle(V, f_downscale, phases)
        # print(
        #     "Class(%s), f_dnscl(%s), DIFFs:\n%s" % (wclass, f_downscale, diffs[bad_ix])
        # )
        # plt.plot(V, "r")
        # plt.plot(V1, "b")
        # plt.plot(V2, "g")
        # plt.show()
        # raise AssertionError(
        #     "Class(%s), f_dnscl(%s)" % (wclass, f_downscale)
        # )


_wltc = model._get_wltc_data()


def _round(V, v_decimals):
    return V.round(v_decimals + 2).round(v_decimals)


@pytest.mark.parametrize("wclass", _wltc["classes"])
def test_recurse_vs_scaling(wclass):
    """Compare downcalings with the both methods: simplified (scale by multiply) and by_the_spec (iterativelly scale accelerations)."""
    from matplotlib import pyplot as plt

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
    V = pd.Series(class_data["cycle"])
    phases = class_data["downscale"]["phases"]

    bad_accuracies, bad_rounds = {}, {}
    for f_downscale in np.arange(0, 4, 0.1):
        V1 = downscale_by_recursing(V, f_downscale, phases)
        V2 = downscale_by_scaling(V, f_downscale, phases)

        bad_ix = ~np.isclose(V1, V2)
        if bad_ix.any():
            errs = pd.concat(
                (V1, V2, V1 - V2), axis=1, keys=["recurse", "rescale", "diff"]
            )[bad_ix]
            bad_accuracies[f_downscale] = errs

        bad_ix = _round(V1, v_decimals) != _round(V2, v_decimals)
        if bad_ix.any():
            bad_rounds[f_downscale] = pd.concat(
                (V1, V2), axis=1, keys=["recurse", "rescale"]
            )[bad_ix]

    if bad_accuracies:
        errs = pd.concat((bad_accuracies.values()), axis=0, keys=bad_accuracies.keys())
        with pd.option_context(*pd_opts):
            pytest.fail(f"{wclass}: ACCURACY errors!\n{errs}\n{errs.describe()}")

    if bad_rounds:
        rounded = (_round(i, v_decimals) for i in bad_rounds.values())
        rounded = pd.concat(rounded, axis=0, keys=bad_rounds.keys())
        precise = pd.concat((bad_rounds.values()), axis=0, keys=bad_rounds.keys())
        errs = pd.concat((rounded, precise), axis=1, keys=["rounded", "precise"])

        with pd.option_context(*pd_opts):
            pytest.fail(f"{wclass}: ROUNDING errors!\n{errs}\n{errs.describe()}")
