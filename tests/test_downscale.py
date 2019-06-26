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
from wltp.experiment import (
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
    dsc_data = class_data["downscale"]
    phases = dsc_data["phases"]
    p_max_values = dsc_data["p_max_values"]
    downsc_coeffs = dsc_data["factor_coeffs"]
    f_downscale = calcDownscaleFactor(
        p_max_values,
        downsc_coeffs,
        p_rated,
        f_downscale_threshold,
        test_mass,
        f0,
        f1,
        f2,
        f_inertial,
    )
    if f_downscale > 0:
        V = downscaleCycle(V, f_downscale, phases)


_wltc = model._get_wltc_data()


@pytest.mark.parametrize(
    "wclass, f_downscale", itt.product(_wltc["classes"], np.arange(0, 4, 0.1))
)
def test_recurse_vs_scaling(wclass, f_downscale):
    """Compare downcalings with the both methods: simplified (scale by multiply) and by_the_spec (iterativelly scale accelerations)."""
    from matplotlib import pyplot as plt

    v_decimals = 1
    class_data = _wltc["classes"][wclass]
    V = pd.Series(class_data["cycle"])
    phases = class_data["downscale"]["phases"]
    V1 = downscale_by_recursing(V, f_downscale, phases)
    V2 = downscale_by_scaling(V, f_downscale, phases)

    bad_ix = ~np.isclose(V1, V2)
    with pd.option_context("display.max_rows", None):
        assert (
            not bad_ix.any()
        ), f"\n{pd.concat((V1, V2), axis=1)[bad_ix]}\n{np.abs(V1 - V2).describe()}"

    bad_ix = V1.round(v_decimals) != V2.round(v_decimals)
    with pd.option_context(
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
    ):
        ## MANY FAILURES below!!!
        assert True or not bad_ix.any(), pd.concat(
            (V1, V2, V1.round(v_decimals), V2.round(v_decimals)),
            axis=1,
            keys=[
                ("rounded", "recurse"),
                ("rounded", "scale"),
                ("precise", "recurse"),
                ("precise", "scale"),
            ],
        )[bad_ix]
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
