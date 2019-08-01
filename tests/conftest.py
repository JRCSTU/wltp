#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2019 European Commission (JRC);
# Licensed under the EUPL (the 'Licence');
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at: http://ec.europa.eu/idabc/eupl
from tests import vehdb
import pytest

_h5db = "Notebooks/VehData/WltpGS-msaccess.h5"


@pytest.fixture
def h5db():
    return "Notebooks/VehData/WltpGS-msaccess.h5"


def pytest_generate_tests(metafunc):
    if "heinz_inp_vehicle" in metafunc.fixturenames:
        metafunc.parametrize("heinz_inp_vehicle", _load_vehicles(_h5db))
