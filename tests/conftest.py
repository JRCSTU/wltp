#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2019 European Commission (JRC);
# Licensed under the EUPL (the 'Licence');
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at: http://ec.europa.eu/idabc/eupl
import logging
import os
from pathlib import Path
from typing import Sequence as Seq

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
    parser.addoption(
        "--h5-del",
        action="store_true",
        default=False,
        help="delete HDF5 (accdb/pyalgo) files before writing (default: false)",
    )
    parser.addoption(
        "--vehnums",
        nargs="*",
        type=int,
        default=None,
        help="HDF5 vehicles to process (default: all vehicles)",
    )


@pytest.fixture
def h5_write(request) -> bool:
    return request.config.getoption("--h5-write")


@pytest.fixture
def del_h5_on_start(request) -> bool:
    return request.config.getoption("--h5-del")


@pytest.fixture
def vehnums_to_run(request) -> Seq[int]:
    return request.config.getoption("--vehnums")


@pytest.fixture
def h5_accdb() -> str:
    return str(Path("Notebooks/VehData/WltpGS-msaccess.h5").resolve())


@pytest.fixture
def h5_pyalgo() -> str:
    return str(Path("Notebooks/VehData/WltpGS-pyalgo.h5").resolve())


@pytest.fixture(scope="session", autouse=True)
def cleanup(request):
    """Print used data-psteps once we are finished."""

    def write_data_psteps():
        pstep_paths = set(
            i[:-5]
            if any(i.endswith(suffix) for suffix in "/dtype /keys /ndim".split())
            else i
            for i in wio.paths_collected()
        )
        dtree_file = Path(__file__).parent.parent.joinpath("datatree.txt")
        pstep_paths |= set(dtree_file.read_text().split("\n"))

        dtree_file.write_text("\n".join(sorted(pstep_paths)))

    request.addfinalizer(write_data_psteps)


@pytest.fixture(scope="session")
def is_travis():
    return "TRAVIS" in os.environ
