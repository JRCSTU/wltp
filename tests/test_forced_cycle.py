#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2013-2020 European Commission (JRC);
# Licensed under the EUPL (the 'Licence');
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at: http://ec.europa.eu/idabc/eupl

import logging
import unittest

import numpy as np
import numpy.testing as npt
import pandas as pd
import pytest
from tests.goodvehicle import goodVehicle

from wltp.experiment import Experiment, datamodel

try:
    from pandas.core.common import PandasError
except ImportError:
    ## Pandas-0.20.1 dropped this classs.
    #  See https://github.com/pydata/pandas-datareader/issues/305
    PandasError = ValueError


@pytest.mark.xfail(reason="Force-cycle will change on next commit.")
class TestForcedCycle(unittest.TestCase):
    def test_badCycle(self):
        mdl = goodVehicle()
        mdl["cycle"] = 1

        with self.assertRaisesRegex(
            PandasError, "DataFrame constructor not properly called"
        ):
            experiment = Experiment(mdl)
            mdl = experiment.run()

    def test_two_ramps_smoke_test(self):
        mdl = goodVehicle()
        mdl = datamodel.upd_resistance_coeffs_regression_curves(mdl)

        V = np.hstack((np.r_[0:100:2], np.r_[98:0:-2]))
        mdl["cycle"] = {"v_target": V}

        experiment = Experiment(mdl)
        mdl = experiment.run()


if __name__ == "__main__":
    import sys

    unittest.main(verbosity=2, argv=sys.argv)
