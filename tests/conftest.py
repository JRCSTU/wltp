#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2019 European Commission (JRC);
# Licensed under the EUPL (the 'Licence');
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at: http://ec.europa.eu/idabc/eupl
from pathlib import Path

import pytest
from tests import vehdb


@pytest.fixture
def h5_accdb():
    return str(Path("Notebooks/VehData/WltpGS-msaccess.h5").resolve())


@pytest.fixture
def h5_pyalgo():
    return str(Path("Notebooks/VehData/WltpGS-pyalgo.h5").resolve())


# def pytest_generate_tests(metafunc):
#      h5db = "Notebooks/VehData/WltpGS-msaccess.h5"
#     if "heinz_inp_vehicle" in metafunc.fixturenames:
#         metafunc.parametrize("heinz_inp_vehicle", _load_vehicles(h5db))
