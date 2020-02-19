#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2013-2019 European Commission (JRC);
# Licensed under the EUPL (the 'Licence');
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at: http://ec.europa.eu/idabc/eupl
from pathlib import Path
import pytest

import papermill as pm


# "CarsDB-accdb.ipynb" is deadly slow (~5').
@pytest.fixture(
    params=[
        pytest.param("CarsDB-accdb.ipynb", marks=pytest.mark.slower),
        pytest.param("CarsDB-pyalgo.ipynb", marks=pytest.mark.slow),
        "CarsDB-compare.ipynb",
        "VMax.ipynb",
        "Cycler.ipynb",
        "RunVehicle.ipynb",
    ]
)
def notebook(request):
    nb_fname = request.param
    nb_fpath = Path(__file__).parents[1] / "Notebooks" / nb_fname
    return nb_fpath.resolve()


@pytest.fixture
def out_notebook(notebook, tmp_path):
    return tmp_path / notebook.name


def test_run_notebooks(
    notebook, out_notebook, h5_write, del_h5_on_start, vehnums_to_run
):
    pm.execute_notebook(
        str(notebook),
        str(out_notebook),
        cwd="Notebooks",
        parameters={
            "skip_h5_write": not h5_write,
            "force_h5_write": h5_write,
            "del_h5_on_start": del_h5_on_start,
            "vehnums_to_run": vehnums_to_run,
        },
        progress_bar=False,
    )
