#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2019 European Commission (JRC);
# Licensed under the EUPL (the 'Licence');
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at: http://ec.europa.eu/idabc/eupl
import tests.nbutils as nbu
import pytest

_h5db = "Notebooks/VehData/WltpGS-msaccess.h5"


def _load_vehicle_data(h5db, vehnum):
    iprops, Pwot = nbu.load_vehicle(h5db, vehnum, "iprop", "pwot")
    n2vs = nbu.load_n2v_gear_ratios(iprops)
    return iprops, Pwot, n2vs


def _load_vehicles(h5db):
    veh_nums = nbu.all_vehnums(h5db)
    return [_load_vehicle_data(h5db, vehnum) for vehnum in veh_nums]


@pytest.fixture
def h5db():
    return "Notebooks/VehData/WltpGS-msaccess.h5"


def pytest_generate_tests(metafunc):
    if "heinz_inp_vehicle" in metafunc.fixturenames:
        metafunc.parametrize("heinz_inp_vehicle", _load_vehicles(_h5db))
