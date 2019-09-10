#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2019 European Commission (JRC);
# Licensed under the EUPL (the 'Licence');
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at: http://ec.europa.eu/idabc/eupl
import logging
from pathlib import Path

import pytest
from tests import vehdb

from wltp import io as wio


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


@pytest.fixture(scope="session", autouse=True)
def cleanup(request):
    """Print used data-psteps once we are finished."""

    def write_data_psteps():
        pstep_paths = set(
            i[:-5] if i.endswith("/ndim") else i for i in wio.paths_collected()
        )
        dtree_file = Path(__file__).parent.parent.joinpath("datatree.txt")
        pstep_paths |= set(dtree_file.read_text().split("\n"))

        dtree_file.write_text("\n".join(sorted(pstep_paths)))

    request.addfinalizer(write_data_psteps)
