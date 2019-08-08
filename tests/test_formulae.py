#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2013-2019 European Commission (JRC);
# Licensed under the EUPL (the 'Licence');
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at: http://ec.europa.eu/idabc/eupl

import logging

import numpy as np
import numpy.testing as npt
import pandas as pd
import pytest

from wltp import experiment

from . import vehdb

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)


def testNparray2Bytes():
    arr = np.array([0, 9, 10, 36, 255 - experiment._escape_char])

    assert experiment.np2bytes(arr) == b"\x80\x89\x8a\xa4\xff"

    with pytest.raises(AssertionError, match="Outside byte-range"):
        experiment.np2bytes(arr + 1)

    with pytest.raises(AssertionError, match="Outside byte-range"):
        experiment.np2bytes(arr - 1)

    npt.assert_array_equal(experiment.bytes2np(experiment.np2bytes(arr)), arr)


def testRegex2bytes():
    regex = br"\g1\g0\g24\g66\g127"

    assert experiment.gearsregex(regex).pattern == b"\x81\x80\x98\xc2\xff"

    regex = br"\g1\g0|\g24\g66\g127"

    assert experiment.gearsregex(regex).pattern == b"\x81\x80|\x98\xc2\xff"
