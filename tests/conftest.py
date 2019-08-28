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


def pytest_addoption(parser):
    parser.addoption(
        "--h5-write",
        action="store_true",
        default=False,
        help="update h5db files (default: false)",
    )


@pytest.fixture
def h5_write(request):
    return request.config.getoption("--h5-write")


@pytest.fixture
def h5_accdb():
    return str(Path("Notebooks/VehData/WltpGS-msaccess.h5").resolve())


@pytest.fixture
def h5_pyalgo():
    return str(Path("Notebooks/VehData/WltpGS-pyalgo.h5").resolve())
