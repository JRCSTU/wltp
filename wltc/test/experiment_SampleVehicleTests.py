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
loglevel = level=logging.DEBUG
logging.basicConfig(level=loglevel)
logging.getLogger().setLevel(loglevel)
log = logging.getLogger(__name__)

class ExperimentSampleVehs(unittest.TestCase):
    '''Compares a batch of vehicles with results obtained from "Official" implementation.'''


    def setUp(self):
        self.run_comparison = True # NOTE: Set it to False to UPDATE sample-results (assuming they are ok).


    def compare_exp_results(self, tabular, fname, run_comparison):
        tmpfname = os.path.join(tempfile.gettempdir(), '%s.pkl'%fname)
        if (run_comparison):
            try:
                with open(tmpfname, 'rb') as tmpfile:
                    data_prev = pickle.load(tmpfile)
                    ## Compare changed-tabular
                    #
                    npt.assert_equal(tabular['gears'],  data_prev['gears'])
                    # Unreached code in case of assertion.
                    # cmp = tabular['gears'] != data_prev['gears']
                    # if (cmp.any()):
                    #     self.plotResults(data_prev)
                    #     print('>> COMPARING(%s): %s'%(fname, cmp.nonzero()))
                    # else:
                    #     print('>> COMPARING(%s): OK'%fname)
            except FileNotFoundError as ex:  # @UnusedVariable
                print('>> COMPARING(%s): No old-tabular found, 1st time to be stored in: '%fname, tmpfname)
                run_comparison = False

        if (not run_comparison):
            with open(tmpfname, 'wb') as tmpfile:
                pickle.dump(tabular, tmpfile)



    def testSampleVehicles(self, plot_results=False, encoding="ISO-8859-1"):

        run_the_experiments(plot_results=False, encoding="ISO-8859-1")


def run_the_experiments(plot_results=False, encoding="ISO-8859-1"):
    # rated_power,kerb_mass,rated_speed,idling_speed,test_mass,no_of_gears,ndv_1,ndv_2,ndv_3,ndv_4,ndv_5,ndv_6,ndv_7,ID_cat,user_def_driv_res_coeff,user_def_power_curve,f0,f1,f2,Comment
    # 0                                                            5                                10                                                    15                        19
    csvfname = 'sample_vehicles.csv'
    csvfname = os.path.join(mydir, csvfname)
    df = pd.read_csv(csvfname, encoding = encoding, index_col = 0)

    for (ix, row) in df.iterrows():
        veh_num = ix

        inst = goodVehicle()
        veh = inst['vehicle']

        veh['mass'] = row['test_mass']
        veh['resistance_coeffs'] = list(row['f0':'f2'])
        veh['p_rated'] = row['rated_power']
        veh['n_rated'] = row['rated_speed']
        veh['n_idle'] = int(row['idling_speed'])
        ngears = int(row['no_of_gears'])
        veh['gear_ratios'] = list(row[6:6+ngears]) #'ndv_1'

        model = Model(inst)
        experiment = Experiment(model)
        experiment.run()

        results = model.data['results']

        f_downscale = results['f_downscale']
        if (f_downscale > 0):
            log.warning('>> DOWNSCALE %s', f_downscale)


        # ankostis_mdb:  't', "v in km/h","v_orig","a in m/s²","gear","g_min","g_max","gear_modification","error_description"
        # heinz:         't', 'km_h', 'stg', 'gear'

        (root, ext) = os.path.splitext(csvfname)
        outfname = '{}-{:05}{}'.format(root, veh_num, ext)
        df = pd.DataFrame(results['tabular'])
        df.to_csv(outfname, index_label='time')



###################
# COMPARE RESULTS #
###################

def plotResults(veh_fname, my_df, hz_df,  g_diff, ax):
    ax.set_title(veh_fname, fontdict={'fontsize': 8} )
    ax.grid(True)

    tlen = len(my_df.index)
    #ax.set_xticks(np.arange(0.0, tlen, 50.0)) NO! looses auto when zooming.


    clutch = my_df['clutch']
    clutch = clutch.nonzero()[0]
    driveability = my_df['driveability'].apply(lambda s: isinstance(s, str))
    driveability = driveability.nonzero()[0]
    ax.vlines(clutch,  0, 0.2)
    ax.vlines(driveability,  0.2, 0.4, 'c')

    v_max = my_df['v_class'].max()
    ax.hlines(1 / v_max,  0, tlen, color="0.75")

    ax.plot(my_df['v_class'] / v_max)
    ax.plot(my_df['v_target'] / v_max, '-.')
    my_gears = my_df['gears']
    ax.plot(my_gears / my_gears.max(), 'o')
    ax.plot(my_df['v_real'] / v_max)
#     ax.plot(my_df['rpm'] / my_df['rpm'].max())
#     p_req = my_df['p_required'] / my_df['p_required'].max()
#     p_req[p_req < 0] = 0
#     ax.plot(p_req)

    hz_v_real = hz_df['v']
    hz_v_target = hz_df['v_downscale']
    hz_gears = hz_df['gear']
    hz_driveability = ~hz_df['gear_modification'].apply(np.isreal)
    hz_driveability = hz_driveability.nonzero()[0]
    ax.vlines(hz_driveability,  0.4, 0.6, 'm')

    ax.plot(hz_v_target / v_max, '--')
    ax.plot(hz_v_real / v_max, ':')
    ax.plot(hz_gears / hz_gears.max(), '*')

    ax.text(0.7, 0, 'Diffs: %.4f' % g_diff, transform=ax.transAxes, bbox={'facecolor':'red', 'alpha':0.5, 'pad':10})


def plot_diffs_with_heinz(heinz_dir, exp_num=None):
    if (heinz_dir is None):
        heinz_dir = mydir

    def read_sample_file(inpfname):
        df = pd.read_csv(inpfname)

        return df

    def read_heinz_file(veh_num):
        vehfpath = os.path.join(heinz_dir, 'heinz_Petrol_veh{:05}.csv'.format(veh_num))
        inpfname = glob.glob(vehfpath)[0]
        df = pd.read_csv(inpfname, encoding='latin-1', header=0, index_col=3)
        assert df['vehicle_no'][0] == veh_num

#         vehfpath = os.path.join(heinz_dir, 'heinz_Petrol_veh{:05}.dri'.format(veh_num))
#         inpfname = glob.glob(vehfpath)[0]
#         df = pd.read_csv(inpfname, encoding='latin-1')

        return df

    def read_and_compare_experiment(myfname, veh_num):
        df_my = read_sample_file(myfname)
        df_hz = read_heinz_file(veh_num)

        my_gears = df_my['gears']
        gears_hz = df_hz['gear']
        accel = np.gradient(df_my['v_class'])
        diff_gears = (my_gears != gears_hz) & (accel >= 0)  # Ignore rrors i9n decceleration phases.
        ngear_diffs = np.count_nonzero(diff_gears)

        return (df_my, df_hz, ngear_diffs)




    fig = plt.figure()

    if exp_num is None:

        paths = glob.glob(os.path.join(mydir, 'sample_vehicles-*.csv'))
        npaths          = len(paths)

        ## NOTE: Limit subplots to facilitate research.
        #
        #paths_to_plot = paths[:1]
        paths_to_plot = paths[0:1] + paths[7:9]

        ## Decide subplot-grid dimensions.
        #
        npaths_to_plot  = len(paths_to_plot)
        w = math.ceil(math.sqrt(npaths_to_plot))
        h = w-1 if ((w-1) * w >= npaths_to_plot) else w

        g_diff = np.zeros(npaths)
        nplotted = 0
        for (n, inpfname) in enumerate(paths):
            log.info(">> Reading: %s", inpfname)

            m = re.match('.*sample_vehicles-(\d+).csv', inpfname)
            assert m


            veh_num = int(m.group(1))
            (df_my, df_hz, ngear_diffs)  = read_and_compare_experiment(inpfname, veh_num)
            g_diff[n]           = ngear_diffs


            if (inpfname in paths_to_plot):
                nplotted += 1
                ax = fig.add_subplot(w, h, nplotted)
                plotResults(os.path.basename(inpfname), df_my, df_hz, ngear_diffs, ax)

        fig.suptitle('DIFFs: count(%i), min(%.4f), MEAN(%.4f), max(%.4f).' % (g_diff.sum(), g_diff.min(), g_diff.mean(), g_diff.max()))
        log.info('DIFFs: count(%i), min(%.4f), MEAN(%.4f), max(%.4f).', g_diff.sum(), g_diff.min(), g_diff.mean(), g_diff.max())

        ## RESULTS:
        #    0.0.5-alpha:                 min(0.6108%), MEAN(3.6276%), max(12.1599%)
        #    0.0.5-alpha:    count(1960), min(11.0000), MEAN(65.3333), max(219.0000)
        #

    else:
        inpfname = os.path.join(mydir, 'sample_vehicles-{:05}.csv'.format(exp_num))

        (df_my, df_hz, gd)  = read_and_compare_experiment(inpfname, veh_num)

        ax = fig.axes()
        plotResults(os.path.basename(inpfname), df_my, df_hz, gd, ax)
        log.info('DIFF: %.4f%%.', gd)


    fig.tight_layout()
    plt.show()

if __name__ == "__main__":
    import sys

    heinz_dir = None
    exp_num = None
    try:
        if len(sys.argv) > 1:
            heinz_dir = sys.argv[1]

            if len(sys.argv) > 2:
                exp_num = int(sys.argv[2])

    except (ValueError, IndexError) as ex:
        exit('Help: \n  <cmd> [heinz_dir [vehicle_num]]\neg: \n  python experiment_SampleVehicleTests d:\Work/Fontaras\WLTNED\HeinzCycles\for_JRC_Petrol_* \nor \n  d:\Work/Fontaras\WLTNED\HeinzCycles\for_JRC_Petrol_*  2357')

#     run_the_experiments()
    plot_diffs_with_heinz(heinz_dir, exp_num)
