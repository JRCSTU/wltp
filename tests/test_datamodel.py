#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2013-2020 European Commission (JRC);
# Licensed under the EUPL (the 'Licence');
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at: http://ec.europa.eu/idabc/eupl

import functools as fnt
import itertools as itt

import pandas as pd

from graphtik import compose, operation
from wltp import cycles, datamodel
from wltp import io as wio
from wltp import pipelines
from wltp.experiment import Experiment

from .goodvehicle import goodVehicle
from .vehdb import oneliner


def testGoodVehicle():
    mdl = goodVehicle()

    exp = Experiment(mdl)
    mdl = exp._model
    defwot = datamodel.upd_default_load_curve({})["wot"]
    assert pd.DataFrame(mdl["wot"][["n_norm", "p_norm"]]).equals(pd.DataFrame(defwot))


def testOverlayOnInit():
    mdl = goodVehicle()
    n_rated = 6000
    mdl2 = {"n_rated": n_rated}

    exp = Experiment(datamodel.merge(mdl, mdl2))
    mdl = exp._model
    assert mdl["n_rated"] == n_rated


def test_get_class_parts_limits_sorted():
    classes = datamodel.get_wltc_data()["classes"]
    class_limits = {
        cls: datamodel.get_class_parts_limits(cls, edges=True) for cls in classes.keys()
    }
    for (cls, l) in class_limits.items():
        assert l == tuple(sorted(l)), f"Class({cls}): Unsorted!"


def test_get_class_parts_limits_with_edges():
    classes = datamodel.get_wltc_data()["classes"]
    class_limits = {
        cls: datamodel.get_class_parts_limits(cls, edges=True) for cls in classes.keys()
    }
    for (cls, l) in class_limits.items():
        assert l[0] == 0, f"Class({cls}): Left-edge not 0!"
    for (cls, l) in class_limits.items():
        assert (
            l[-1] == len(classes[cls]["V_cycle"]) - 1
        ), f"Class({cls}): Section Right-edge not len(cycle)!"


def test_get_class_pmr_limits():
    l = datamodel.get_class_pmr_limits()
    assert l == [22, 34]


def test_get_class_pmr_limits_with_edges():
    pmr_limits = datamodel.get_class_pmr_limits(edges=True)
    assert pmr_limits[0] == 0, "Left-edge not 0!"
    assert pmr_limits[-1] == float("inf"), "PMR-limit: Right-edge not INF!"


def test_get_class_phase_boundaries():
    wcd = datamodel.get_wltc_data()
    cd = cycles.get_wltc_class_data(wcd["classes"], 3)
    pmr_boundaries = cycles.get_class_phase_boundaries(cd["lengths"], cd["V_cycle"])
    assert len(pmr_boundaries) == 4
    assert pmr_boundaries[0][0] == 0
    assert pmr_boundaries[-1][-1] == 1800
    nums = tuple(itt.chain(*pmr_boundaries))
    assert tuple(sorted(nums)) == nums


def test_v_distances_pipeline(wltc_class):
    aug = wio.make_autograph()
    ops = aug.wrap_funcs(
        [
            *pipelines.v_distances_pipeline().ops,
            # fake dsc & cap
            operation(None, "FAKE.V_dsc", "wltc_class_data/V_cycle", "V_dsc"),
            operation(None, "FAKE.V_cap", "wltc_class_data/V_cycle", "V_capped"),
        ]
    )
    pipe = compose(..., *ops)
    inp = {"wltc_data": datamodel.get_wltc_data(), "wltc_class": wltc_class}
    sol = pipe.compute(inp)
    got = sol["wltc_distances"]
    print(got)
    exp_sums = {
        0: """
                         sum   cumsum
        [0, 589)      11988.4  11988.4
        [589, 1022)   17162.8  29151.2
        [1022, 1611)  11988.4  41139.6
        """,
        1: """
                        sum    cumsum
        [0, 589)      11162.2  11162.2
        [589, 1022)   17054.3  28216.5
        [1022, 1477)  24450.6  52667.1
        [1477, 1800)  28869.8  81536.9
        """,
        2: """
                        sum    cumsum
        [0, 589)      11140.3  11140.3
        [589, 1022)   16995.7  28136.0
        [1022, 1477)  25646.0  53782.0
        [1477, 1800)  29714.9  83496.9
        """,
        3: """
                         sum    cumsum
        [0, 589)      11140.3  11140.3
        [589, 1022)   17121.2  28261.5
        [1022, 1477)  25782.2  54043.7
        [1477, 1800)  29714.9  83758.6
        """,
    }
    assert oneliner(got) == oneliner(exp_sums[wltc_class])
