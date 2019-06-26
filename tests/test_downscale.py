#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2013-2019 European Commission (JRC);
# Licensed under the EUPL (the 'Licence');
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at: http://ec.europa.eu/idabc/eupl

import logging
import unittest

import numpy as np
import pandas as pd

from wltp import model
from wltp.experiment import calcDownscaleFactor, decideClass, downscaleCycle

log = logging.getLogger(__name__)


class ExperimentDownscale(unittest.TestCase):
    def setUp(self):
        logging.basicConfig(level=logging.DEBUG)

    def testFull_manually(self):
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
        cycle = pd.Series(class_data["cycle"])

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
            cycle = downscaleCycle(cycle, f_downscale, phases)

    def testCompareDownscaleMethodWithSpecs(self):
        """Compare downcalings with the both methods: simplified (scale by multiply) and by_the_spec (iterativelly scale accelerations)."""
        from matplotlib import pyplot as plt

        wltc = model._get_wltc_data()
        wclasses = wltc["classes"]
        results = {}
        for wclass in wclasses.keys():
            for f_downscale in np.arange(0, 4, 0.1):
                class_data = wclasses[wclass]
                cycle = pd.Series(class_data["cycle"])
                phases = class_data["downscale"]["phases"]
                V1 = downscaleCycle(cycle, f_downscale, phases)
                V2 = downscaleCycle_bySpecs(cycle, f_downscale, phases)

                results[(wclass, f_downscale)] = np.abs(V1 - V2).describe()
                if not np.allclose(V1, V2):
                    print("Class(%s), f_dnscl(%s)" % (wclass, f_downscale))
                    plt.plot(cycle, "r")
                    plt.plot(V1, "b")
                    plt.plot(V2, "g")
                    plt.show()
                    raise AssertionError(
                        "Class(%s), f_dnscl(%s)" % (wclass, f_downscale)
                    )

        results = pd.concat(results.values(), keys=results.keys(), axis=1).T
        with pd.option_context("display.max_rows", None):
            print(results)
        print(results.describe())


def downscaleCycle_bySpecs(cycle, f_downscale, phases):
    V = cycle.copy()
    (t0, t1, t2) = phases

    ## Accelaration phase
    #
    for t in range(t0, t1):
        a = cycle[t + 1] - cycle[t]
        V[t + 1] = V[t] + a * (1 - f_downscale)

    ## Decelaration phase
    #
    f_corr = (V[t1] - cycle[t2]) / (cycle[t1] - cycle[t2])
    for t in range(t1 + 1, t2):
        a = cycle[t] - cycle[t - 1]
        V[t] = V[t - 1] + a * f_corr

    return V


if __name__ == "__main__":
    import sys

    # sys.argv = ['', 'Test.testName']
    unittest.main(argv=sys.argv[1:])
