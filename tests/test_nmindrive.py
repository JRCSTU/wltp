#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2013-2020 European Commission (JRC);
# Licensed under the EUPL (the 'Licence');
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at: http://ec.europa.eu/idabc/eupl
import itertools as itt

import numpy as np
import pytest

from wltp import nmindrive


@pytest.mark.parametrize(
    "mdl",
    [
        dict(
            zip(
                (
                    "n_min_drive_up",
                    "n_min_drive_up_start",
                    "n_min_drive_down",
                    "n_min_drive_down_start",
                    "t_cold_end",
                ),
                values,
            )
        )
        for values in itt.product([None, 1], [None, 2], [None, 3], [None, 4], [None, 5])
    ],
)
def test_n_mins_smoke(mdl):
    mdl.update(n_idle=500, n_rated=4000)
    base = nmindrive.mdl_2_n_min_drives(**mdl)

    results = [base]
    for values in itt.product([None, 1], [None, 2], [None, 3], [None, 4], [None, 5]):
        mdl = dict(
            zip(
                (
                    "n_min_drive_up",
                    "n_min_drive_up_start",
                    "n_min_drive_down",
                    "n_min_drive_down_start",
                    "t_cold_end",
                ),
                values,
            )
        )
        res = nmindrive.mdl_2_n_min_drives(n_idle=500, n_rated=4000)
        results.append(res)

    ## They must not be any null.
    #
    for _i, nmins in enumerate(results):
        assert (np.isfinite(i) for i in nmins)
