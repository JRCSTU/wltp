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
'''Run as Test-case to generate results for sample-vehicles.
Run it as cmd-line to compare with Heinz's results.

@author: ankostis@gmail.com
@since 5 Jan 2014
'''

from matplotlib import pyplot as plt
from wltc.experiment import Experiment
from wltc.model import Model
from wltc.test.goodvehicle import goodVehicle
import glob
import logging
import math
import numpy as np
import numpy.testing as npt
import os
import pandas as pd
import pickle
import re
import tempfile
import unittest


mydir = os.path.dirname(__file__)
log = logging.getLogger(__name__)

class ExperimentSampleVehs(unittest.TestCase):
    '''Compares a batch of vehicles with results obtained from "Official" implementation.'''


    def setUp(self):
        logging.basicConfig(level=logging.DEBUG)
        self.run_comparison = True # NOTE: Set it to False to UPDTE file-results (assuming they are ok).


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
            except FileNotFoundError as ex:  # @UnusedVariable
                print('>> COMPARING(%s): No old-results found, 1st time to be stored in: '%fname, tmpfname)
                run_comparison = False

        if (not run_comparison):
            with open(tmpfname, 'wb') as tmpfile:
                pickle.dump(results, tmpfile)



    def testSampleVehicles(self, plot_results=False, encoding="ISO-8859-1"):

        logging.getLogger().setLevel(logging.DEBUG)

        # rated_power,kerb_mass,rated_speed,idling_speed,test_mass,no_of_gears,ndv_1,ndv_2,ndv_3,ndv_4,ndv_5,ndv_6,ndv_7,ID_cat,user_def_driv_res_coeff,user_def_power_curve,f0,f1,f2,Comment
        # 0                                                            5                                10                                                    15                        19
        csvfname = 'sample_vehicles.csv'
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

            f_downscale = results['f_downscale']
            if (f_downscale > 0):
                log.warn('>> DOWNSCALE %s', f_downscale)


            # ankostis_mdb:  't', "v in km/h","v_orig","a in m/s²","gear","g_min","g_max","gear_modification","error_description"
            # heinz:         't', 'km_h', 'stg', 'gear'

            (root, ext) = os.path.splitext(csvfname)
            outfname = '{}-{:05}{}'.format(root, veh_num, ext)
            df = pd.DataFrame(results, columns=['v_class', 'v_target', 'v_real', 'gears', 'clutch'])
            df.to_csv(outfname, index_label='time')



###################
# COMPARE RESULTS #
###################

def plotResults(df_my, df_hz, ax):
    ax.grid(True)

    clutch = df_my['clutch']
    clutch = clutch.nonzero()[0]
    ax.plot(df_my['v_class'])
    ax.plot(df_my['v_target'], '-.')
    ax.vlines(clutch,  0, 40)
    ax.plot(df_my['gears'] * 12, 'o')
    ax.plot(df_my['v_real'])

    realv_hz = df_hz['v']
    gears_hz = df_hz['gear']

    ax.plot(realv_hz, ':')
    ax.plot(gears_hz * 12, '*')


def plot_diffs_with_heinz(heinz_dir, exp_num=None):

    def read_sample_file(inpfname):
        df = pd.read_csv(inpfname)

        return df

    def read_heinz_file(veh_num):
        vehfpath = os.path.join(heinz_dir, 'heinz_Petrol_veh{:05}.dri'.format(veh_num))
        inpfname = glob.glob(vehfpath)[0]
        df = pd.read_csv(inpfname, encoding='latin-1')

        return df

    def read_and_compare_files(myfname, veh_num, ax):
        ax.set_title(os.path.basename(myfname), fontdict={'fontsize': 8} )

        df_my = read_sample_file(myfname)
        df_hz = read_heinz_file(veh_num)

        plotResults(df_my, df_hz, ax)


    fig = plt.figure()

    if exp_num is None:

        paths = glob.glob(os.path.join(mydir, 'sample_vehicles-*.csv'))

        paths = paths[:9] # NOTE: Limit to facilitate drawing.

        ## Decide subplot-grid dimensions.
        #
        npaths = len(paths)
        w = math.ceil(math.sqrt(npaths))
        h = w-1 if ((w-1) * w >= npaths) else w

        for (n, inpfname) in enumerate(paths):
            m = re.match('.*sample_vehicles-(\d+).csv', inpfname)
            assert m

            veh_num = int(m.group(1))
            ax = fig.add_subplot(w, h, n+1)
            read_and_compare_files(inpfname, veh_num, ax)

    else:
        inpfname = os.path.join(mydir, 'sample_vehicles-{:05}.csv'.format(exp_num))

        ax = fig.axes()
        read_and_compare_files(inpfname, veh_num, ax)

    fig.tight_layout()
    plt.show()

if __name__ == "__main__":
    import sys

    try:
        heinz_dir = sys.argv[1]
        if len(sys.argv) > 2:
            exp_num = int(sys.argv[2])
        else:
            exp_num = None
    except (ValueError, IndexError) as ex:
        exit('Help: \n  <cmd> heinz_dir [vehicle_num]\neg: \n  python experiment_SampleVehicleTests d:\Work/Fontaras\WLTNED\HeinzCycles\for_JRC_Petrol_* \nor \n  d:\Work/Fontaras\WLTNED\HeinzCycles\for_JRC_Petrol_*  2357')

    plot_diffs_with_heinz(heinz_dir, exp_num)
