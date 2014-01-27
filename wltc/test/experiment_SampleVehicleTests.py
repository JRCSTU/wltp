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
from ..model import Model
from .goodvehicle import goodVehicle
from matplotlib import pyplot as pylab
import logging
import numpy as np
import numpy.testing as npt
import os
import pickle
import tempfile
import unittest

class ExperimentSampleVehs(unittest.TestCase):
    def setUp(self):
        logging.basicConfig(level=logging.DEBUG)
        self.run_comparison = True


    def compare_exp_results(self, results, fname, run_comparison):
        tmpfname = os.path.join(tempfile.gettempdir(), '%s.pkl'%fname)
        if (run_comparison):
            try:
                with open(tmpfname, 'rb') as tmpfile:
                    data_prev = pickle.load(tmpfile)
                    ## Compare changed-results
                    #
                    npt.assert_equal(results['gears'],  data_prev['gears'])
                    # Unreached code in case of assertion.
                    # cmp = results['gears'] != data_prev['gears']
                    # if (cmp.any()):
                    #     self.plotResults(data_prev)
                    #     print('>> COMPARING(%s): %s'%(fname, cmp.nonzero()))
                    # else:
                    #     print('>> COMPARING(%s): OK'%fname)
            except FileNotFoundError as ex:
                print('>> COMPARING(%s): No old-results found, 1st time to be stored in: '%fname, tmpfname)
                run_comparison = False

        if (not run_comparison):
            with open(tmpfname, 'wb') as tmpfile:
                pickle.dump(results, tmpfile)


    def plotResults(self, model):
        results = model['results']
        gears = results['gears']
        target = results['v_target']
        realv = results['v_real']
        clutch = results['clutch']

        clutch = clutch.nonzero()[0]
        pylab.vlines(clutch,  0, 40)
        pylab.plot(target)
        pylab.plot(gears * 12, '+')
        pylab.plot(realv)



    def testSampleVehicles(self, plot_results=False, encoding="ISO-8859-1"):
        import pandas as pd

        logging.getLogger().setLevel(logging.DEBUG)

        # rated_power,kerb_mass,rated_speed,idling_speed,test_mass,no_of_gears,ndv_1,ndv_2,ndv_3,ndv_4,ndv_5,ndv_6,ndv_7,ID_cat,user_def_driv_res_coeff,user_def_power_curve,f0,f1,f2,Comment
        # 0                                                            5                                10                                                    15                        19
        csvfname = 'sample_vehicles.csv'
        mydir = os.path.dirname(__file__)
        csvfname = os.path.join(mydir, csvfname)
        df = pd.read_csv(csvfname, encoding = encoding, index_col = 0)

        for (ix, row) in df.iterrows():
            veh_num = ix

            inst = goodVehicle()
            veh = inst['vehicle']

            veh['mass'] = row[4]
            veh['resistance_coeffs'] = list(row[16:19])
            veh['p_rated'] = row[0]
            veh['n_rated'] = row[2]
            veh['n_idle'] = int(row[3])
            ngears = row[5]
            veh['gear_ratios'] = list(row[6:6+ngears])

            model = Model(inst)
            experiment = Experiment(model)
            experiment.run()

            results = model.data['results']
            # ankostis_mdb:  't', "v in km/h","v_orig","a in m/s²","gear","g_min","g_max","gear_modification","error_description"
            # heinz:         't', 'km_h', 'stg', 'gear'

            (root, ext) = os.path.splitext(csvfname)
            outfname = '%s-%i%s' % (root, veh_num, ext)
            df = pd.DataFrame(results, columns=['v_target', 'v_real', 'gears', 'clutch'])
            df.to_csv(outfname, index_label='time')


if __name__ == "__main__":
    import sys;#sys.argv = ['', 'Test.testName']
    unittest.main(argv = sys.argv[1:])
