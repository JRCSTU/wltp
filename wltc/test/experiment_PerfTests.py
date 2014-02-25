#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# Copyright 2013-2014 ankostis@gmail.com
#
# This file is part of wltc.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.
'''
@author: ankostis@gmail.com
@since 5 Jan 2014
'''

from ..experiment import Experiment
from .goodvehicle import goodVehicle
import logging
import unittest
import time


class ExperimentPerf(unittest.TestCase):

    def testPerf(self):
        logging.getLogger().setLevel(logging.WARNING)

        nexp = 100
        start = time.time()
        for _ in range(nexp):
            model = goodVehicle()

            experiment = Experiment(model)

            experiment.run()

        elapsed = (time.time() - start)
        print(">> ELAPSED: %.2fsec, RUN/EXP: %.4fsec"%(elapsed, elapsed/nexp))


if __name__ == "__main__":
    import sys;#sys.argv = ['', 'Test.testName']
    unittest.main(argv = sys.argv[1:])
