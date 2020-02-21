#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2019-2020 European Commission (JRC);
# Licensed under the EUPL (the 'Licence');
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at: http://ec.europa.eu/idabc/eupl
import logging
import os
import random
from pathlib import Path
from typing import Optional
from typing import Sequence as Seq

import pytest
from tests import vehdb

from wltp import io as wio


log = logging.getLogger(__name__)


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
        help=(
            "HDF5 vehicles to process (default: 24%% of vehicles).  "
            "To run all vehicles, do not give any vehicle-number."
        ),
    )


@pytest.fixture
def h5_write(request) -> bool:
    return request.config.getoption("--h5-write")


@pytest.fixture
def del_h5_on_start(request) -> bool:
    return request.config.getoption("--h5-del")


def _permatest_and_random_vehnums(h5_accdb):
    sample_ratio = 0.14  # ~x7 test-runs would cover all
    with vehdb.openh5(h5_accdb) as h5db:
        all_vehs = set(vehdb.all_vehnums(h5db))

    permatest_vehs = [
        1,
        # >9 gears
        23,
        # Known bads
        42,
        46,
        48,
        52,
        53,
        90,
        # AccDB not respecting n_min=0.9 x n_idle (Annex 2-3.k.3)
        25,
        # Diffs in gears above 2
        35,
        # Vehicle has too many insufficient powers
        75,
        # Extensions
        117,
        119,
        121,
        125,
    ]
    remain_vehs = all_vehs - set(permatest_vehs)
    sample_size = int(sample_ratio * len(remain_vehs))
    sample_vehs = random.sample(remain_vehs, sample_size)

    run_vehs = permatest_vehs + sample_vehs
    log.info(
        "Sample-testing %s(%.1f%%) out of %s accdb vehicles (%.1f%% at random).",
        len(run_vehs),
        100 * len(run_vehs) / len(all_vehs),
        len(all_vehs),
        100 * sample_ratio,
    )
    return run_vehs


@pytest.fixture
def vehnums_to_run(h5_accdb, request) -> Optional[Seq[int]]:
    cli_vehs = request.config.getoption("--vehnums")

    if isinstance(cli_vehs, list):  # CLI gave some vehs like  `--vehnums 11`
        if not cli_vehs:  # `--vehnums` without veh-numbers
            return None  # signal to test all
        return cli_vehs

    assert cli_vehs is None, cli_vehs  # `None` is default, no --vehnums in CLI.
    return _permatest_and_random_vehnums(h5_accdb)


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
