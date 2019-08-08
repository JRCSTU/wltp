#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2013-2019 European Commission (JRC);
# Licensed under the EUPL (the 'Licence');
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at: http://ec.europa.eu/idabc/eupl
import pytest
from jsonschema.exceptions import ValidationError

from wltp import gearbox

from .goodvehicle import goodVehicle
import itertools as itt


def test_n_mins_smoke():

    base = gearbox.calc_fixed_n_min_drives({}, 500, 4000)

    results = [base]
    for values in itt.product([None, 1], [None, 2], [None, 3], [None, 4]):
        mdl = dict(
            zip(
                (
                    "n_min_drive_up",
                    "n_min_drive_up_start",
                    "n_min_drive_down",
                    "n_min_drive_down_start",
                ),
                values,
            )
        )
        res = gearbox.calc_fixed_n_min_drives(mdl, 500, 4000)
        results.append(res)

    ## They must all produce diffetrent value.
    #
    for v1, v2 in itt.permutations(results, 2):
        assert v1 != v2
