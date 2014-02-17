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
    ax.vlines(clutch,  0, 0.2)

    ## Add pickers on driveability lines showing the specific msg.
    #
    driveability = my_df['driveability']
    driveability_true = driveability.apply(lambda s: isinstance(s, str))
    lines = ax.vlines(driveability_true.nonzero()[0],  0.2, 0.4, 'c', picker=5)
    lines.set_urls(driveability[driveability_true])

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

    ## Add pickers on driveability lines showing the specific msg.
    #
    hz_driveability = hz_df['gear_modification']
    hz_driveability_true = ~hz_driveability.apply(np.isreal)
    lines = ax.vlines(hz_driveability_true.nonzero()[0],  0.4, 0.6, 'm', picker=5)
    lines.set_urls(hz_driveability[hz_driveability_true])


    ax.plot(hz_v_target / v_max, '--')
    ax.plot(hz_v_real / v_max, ':')
    ax.plot(hz_gears / hz_gears.max(), '*')

    ax.text(0.7, 0, 'Diffs: %.4f' % g_diff, transform=ax.transAxes, bbox={'facecolor':'red', 'alpha':0.5, 'pad':10})


def plot_diffs_with_heinz(heinz_dir, experiment_num=None):
    if (heinz_dir is None):
        heinz_dir = mydir

    def run_experiments_if_outdated(outfiles):
        ## Run experiment only if algorithm has changed
        #
        mydate = os.path.getmtime(outfiles[0])
        checkfiles = ['../instances.py', '../experiment.py', 'sample_vehicles.csv']
        checkdates = [os.path.getmtime(os.path.join(mydir, f)) for f in checkfiles]
        modifs = [fdate > mydate for fdate in checkdates]
        if (any(modifs)):
            run_the_experiments()



    def read_sample_file(inpfname):
        df = pd.read_csv(inpfname)

        return df

    def read_heinz_file(veh_num):
        vehfpath = os.path.join(heinz_dir, 'heinz_Petrol_veh{:05}.csv'.format(veh_num))
        try:
            inpfname = glob.glob(vehfpath)[0]
        except IndexError:
            raise FileNotFoundError(vehfpath)
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
        diff_gears = (my_gears != gears_hz)
        ndiff_gears = np.count_nonzero(diff_gears)

        ## Count Acceleration-only errors.
        accel = np.gradient(df_my['v_class'])
        diff_gears_accel = diff_gears[accel >= 0]
        ndiff_gears_accel = np.count_nonzero(diff_gears_accel)

        return (df_my, df_hz, ndiff_gears, ndiff_gears_accel)



    fig = plt.figure()
    text_infos = fig.text(0.5, 0.5, '', transform=fig.transFigure, bbox={'facecolor':'grey', 'alpha':0.3, 'pad':10}, horizontalalignment='center', verticalalignment='center')

    def fig_onpick(event):
        pickline = event.artist
        urls = pickline.get_urls()
        rule = urls.iloc[event.ind]
        print(rule)
        text_infos.set_text('Rule: %s' % rule)

        fig.canvas.draw()

    fig.canvas.mpl_connect('pick_event', fig_onpick)


    if experiment_num is None:

        paths = glob.glob(os.path.join(mydir, 'sample_vehicles-*.csv'))
        npaths          = len(paths)

        run_experiments_if_outdated(paths)

        ## NOTE: Limit subplots to facilitate research.
        #
        paths_to_plot = paths
#         paths_to_plot = paths[0:9]
        paths_to_plot = paths[5:6] + paths[7:9] + paths[14:16] + paths[23:24]

        ## Decide subplot-grid dimensions.
        #
        npaths_to_plot  = len(paths_to_plot)
        w = math.ceil(math.sqrt(npaths_to_plot))
        h = w-1 if ((w-1) * w >= npaths_to_plot) else w

        g_diff = np.zeros((2, npaths))
        nplotted = 0
        for (n, inpfname) in enumerate(paths):
            m = re.match('.*sample_vehicles-(\d+).csv', inpfname)
            assert m


            veh_num = int(m.group(1))
            (df_my, df_hz, ndiff_gears, ndiff_gears_accel)  = read_and_compare_experiment(inpfname, veh_num)
            g_diff[0, n]           = ndiff_gears
            g_diff[1, n]           = ndiff_gears_accel

            log.info(">> %i: %s: ±DIFFs(%i), +DIFFs(%i)", n, inpfname, ndiff_gears, ndiff_gears_accel)


            if (inpfname in paths_to_plot):
                nplotted += 1
                ax = fig.add_subplot(w, h, nplotted)
                plotResults(os.path.basename(inpfname), df_my, df_hz, ndiff_gears, ax)

        fig.suptitle('±DIFFs: count(%i), min(%i), MEAN(%.2f±%.2f), max(%i).' % (g_diff[0].sum(), g_diff[0].min(), g_diff[0].mean(), g_diff[0].std(), g_diff[0].max()))
        log.info('#       ±DIFFs: count(%i), min(%i), MEAN(%.2f±%.2f), max(%i).', g_diff[0].sum(), g_diff[0].min(), g_diff[0].mean(), g_diff[0].std(), g_diff[0].max())
        log.info('#       +DIFFs: count(%i), min(%i), MEAN(%.2f±%.2f), max(%i).', g_diff[1].sum(), g_diff[1].min(), g_diff[1].mean(), g_diff[1].std(), g_diff[1].max())

        ## RESULTS:
        #    0.0.5-alpha:                 min(0.6108%), MEAN(3.6276%), max(12.1599%)
        #    0.0.5-alpha:    count(1960), min(11.0000), MEAN(65.3333), max(219.0000)
        #    ±Accel erros    count(6486), min(151.0000), MEAN(216.2000), max(396.0000).
        #
        #    (b2)skip-decel: count(5995), min(137.0000), MEAN(199.8333±78.0727), max(401.0000).
        #                    vehs: 02189=332, 02371=401m 0891=381, 00409=301
        #    Accel only errs count(1894), min(11.0000), MEAN(63.1333±63.211), max(220.0000)
        #
        #    Heinz-db Pwot:
        #       ±DIFFs: count(5758), min(135), MEAN(191.93±67.34), max(363).
        #       +DIFFs: count(1681), min(10), MEAN(56.03±54.33), max(192).
        #    Rule(f) before rule(b):
        #       ±DIFFs: count(5583), min(135), MEAN(186.10±57.99), max(335).
        #       +DIFFs: count(1515), min(10), MEAN(50.50±46.65), max(176).
        #    Rule(f) applied also for i-2, i-3, ... signular-downshifts:
        #       ±DIFFs: count(5568), min(135), MEAN(185.60±57.59), max(335).
        #       +DIFFs: count(1500), min(10), MEAN(50.00±46.26), max(176).
        #    Preciese input values:
        #       ±DIFFs: count(5569), min(135), MEAN(185.63±57.57), max(335).
        #       +DIFFs: count(1501), min(10), MEAN(50.03±46.25), max(176).
    else:
        inpfname = os.path.join(mydir, 'sample_vehicles-{:05}.csv'.format(experiment_num))

        (df_my, df_hz, gd)  = read_and_compare_experiment(inpfname, veh_num)

        ax = fig.axes()
        plotResults(os.path.basename(inpfname), df_my, df_hz, gd, ax)
        log.info('DIFF: %.4f%%.', gd)


    fig.tight_layout()
    plt.show()

if __name__ == "__main__":
    import sys

    heinz_dir = None
    experiment_num = None
    try:
        if len(sys.argv) > 1:
            heinz_dir = sys.argv[1]

            if len(sys.argv) > 2:
                experiment_num = int(sys.argv[2])

    except (ValueError, IndexError) as ex:
        exit('Help: \n  <cmd> [heinz_dir [vehicle_num]]\neg: \n  python experiment_SampleVehicleTests d:\Work/Fontaras\WLTNED\HeinzCycles\for_JRC_Petrol_* \nor \n  d:\Work/Fontaras\WLTNED\HeinzCycles\for_JRC_Petrol_*  2357')

    plot_diffs_with_heinz(heinz_dir, experiment_num)
