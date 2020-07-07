#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2013-2020 European Commission (JRC);
# Licensed under the EUPL (the 'Licence');
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at: http://ec.europa.eu/idabc/eupl

import pandas as pd

from wltp import datamodel
from wltp.experiment import Experiment

from .goodvehicle import goodVehicle


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
        assert l == sorted(l), f"Class({cls}): Unsorted!"


def test_get_class_parts_limits_with_edges():
    classes = datamodel.get_wltc_data()["classes"]
    class_limits = {
        cls: datamodel.get_class_parts_limits(cls, edges=True) for cls in classes.keys()
    }
    for (cls, l) in class_limits.items():
        assert l[0] == 0, f"Class({cls}): Left-edge not 0!"
    for (cls, l) in class_limits.items():
        assert l[-1] == len(
            classes[cls]["V_cycle"]
        ), f"Class({cls}): Section Right-edge not len(cycle)!"


def test_get_class_pmr_limits():
    l = datamodel.get_class_pmr_limits()
    assert l == [22, 34]


def test_get_class_pmr_limits_with_edges():
    pmr_limits = datamodel.get_class_pmr_limits(edges=True)
    assert pmr_limits[0] == 0, "Left-edge not 0!"
    assert pmr_limits[-1] == float("inf"), "PMR-limit: Right-edge not INF!"
