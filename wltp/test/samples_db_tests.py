#! python
#-*- coding: utf-8 -*-
#
# Copyright 2013-2014 European Commission (JRC);
# Licensed under the EUPL (the 'Licence');
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at: http://ec.europa.eu/idabc/eupl
'''Compares the results of synthetic vehicles from JRC against pre-phase-1b Heinz's tool.

* Run as Test-case to generate results for sample-vehicles.
* Run it as cmd-line to compare with Heinz's results.
'''

from __future__ import division, print_function, unicode_literals

import glob
import logging
import math
import os
import re
import unittest
from unittest.case import skip

from matplotlib import pyplot as plt
from six import string_types

import numpy as np
import numpy.testing as npt
import pandas as pd

from ..experiment import Experiment
from ..utils import FileNotFoundError
from .goodvehicle import goodVehicle


overwrite_old_results = True # NOTE: Set 'False' to UPDATE sample-results or run main() (assuming they are ok).


mydir = os.path.dirname(__file__)
vehs_data_inp_fname = 'sample_vehicles.csv'
samples_dir = 'samples_db'
gened_fname_regex = r'.*sample_vehicles-(\d+).csv'
heinz_fname_regex = r'.*heinz-(\d+).csv'
gened_fname_glob = 'sample_vehicles-*.csv'
driver_weight = 70
"For calculating unladen_mass."
encoding="ISO-8859-1"


def init_logging(loglevel = logging.DEBUG):
    logging.basicConfig(level=loglevel)
    logging.getLogger().setLevel(level=loglevel)
    log = logging.getLogger(__name__)

    return log
log = init_logging()

def make_heinz_fname(veh_num):
    return 'heinz_Petrol_veh{:05}.csv'.format(veh_num)

def read_vehicle_data():
    csvfname = os.path.join(mydir, samples_dir, vehs_data_inp_fname)
    df = pd.read_csv(csvfname, encoding = encoding, index_col = 0)

    return df


class ExperimentSampleVehs(unittest.TestCase):
    '''Compares a batch of vehicles with results obtained from "Official" implementation.'''


    def setUp(self):
        self.run_comparison = overwrite_old_results


    #@skip
    def test0_runExperiments(self, plot_results=False, encoding="ISO-8859-1"):
        _run_the_experiments(plot_results=False, compare_results=self.run_comparison, encoding="ISO-8859-1")


    #@skip
    def test1_AvgRPMs(self):
        """Check mean-engine-speed diff with Heinz within some percent.

        Results::

                               mean         std          min          max
            python      1876.555626  146.755857  1652.457262  2220.657166
            heinz       1892.048584  148.248303  1660.710716  2223.772904
            diff_prcnt     0.008256    0.010170     0.004995     0.001403

        Keeping idle engine revs::
        
                               mean         std          min          max
            python      1898.453462  146.889032  1674.151741  2239.621701
            heinz       1892.048584  148.248303  1660.710716  2223.772904
            diff_prcnt    -0.003385    0.009254    -0.008094    -0.007127

        """

        pcrnt_limit = 3

        h_n = []
        g_n = []
        all_gened = glob.glob(os.path.join(mydir, samples_dir, gened_fname_glob))
        for g_fname in all_gened:
            m = re.match(gened_fname_regex, g_fname)
            veh_num = int(m.groups()[0])
            df_g = read_sample_file(g_fname)
            df_h = read_heinz_file(veh_num)

            if abs(df_g.v_class.sum() - df_h.v_orig.sum()) > 1:
                log.warning('Cycle-mismatched(%s): gened(%s) !+ heinz(%s)!', g_fname, df_g.v_class.sum(), df_h.v_orig.sum())
                continue

            g_n.append(df_g['rpm'].mean())
            h_n.append(df_h['n'].mean())

        g_n = np.array(g_n)
        h_n = np.array(h_n)

        df = pd.DataFrame()
        df['mean'] = [g_n.mean(), h_n.mean()]
        df['std'] = [g_n.std(), h_n.std()]
        df['min'] = [g_n.min(), h_n.min()]
        df['max'] = [g_n.max(), h_n.max()]
        df.index = ['python', 'heinz']

        dff = (df.loc['heinz', :] - df.loc['python', :]) / df.min(axis=0)
        df.loc['diff_prcnt', :] = dff

        print(df)

        diff_prcnt = df.loc['diff_prcnt', 'mean']
        self.assertLess(abs(diff_prcnt), pcrnt_limit/100)


    def test1_PMRatio(self):
        """Check mean-engine-speed diff with Heinz within some percent for all PMRs.

        Results::

                                gened_mean_rpm  heinz_mean_rpm  diff_prcnt  count
            pmr
            (40.759, 49.936]       1814.752308     1822.011660    0.004000      4
            (49.936, 59.00401]     1861.137208     1879.822876    0.010040      4
            (59.00401, 68.072]     2015.693195     2031.240237    0.007713      3
            (68.072, 77.14]        1848.735584     1859.116047    0.005615      5
            (77.14, 86.208]                NaN             NaN         NaN      0
            (86.208, 95.276]       1786.879366     1807.764020    0.011688      5
            (95.276, 104.344]      1956.288657     1980.523043    0.012388      3
            (104.344, 113.412]     1929.718933     1947.787155    0.009363      3
            (113.412, 122.48]      2033.321183     2051.602998    0.008991      1
            (122.48, 131.548]      1781.487338     1781.591893    0.000059      1
            (131.548, 140.616]             NaN             NaN         NaN      0
            (140.616, 149.684]     1895.125082     1907.872848    0.006727      1

        Keeping idle engine revs::
        
                                gened_mean_rpm  heinz_mean_rpm  diff_prcnt  count
            pmr                                                                  
            (40.759, 49.936]       2079.060852     2071.114936   -0.003837      4
            (49.936, 59.00401]     1915.715680     1911.017351   -0.002459      4
            (59.00401, 68.072]     1941.701195     1930.170461   -0.005974      3
            (68.072, 77.14]        1867.228321     1863.086063   -0.002223      5
            (77.14, 86.208]                NaN             NaN         NaN      0
            (86.208, 95.276]       1803.169294     1795.347029   -0.004357      5
            (95.276, 104.344]      1813.784185     1807.303905   -0.003586      3
            (104.344, 113.412]     1929.050124     1929.524894    0.000246      3
            (113.412, 122.48]      1716.185416     1704.537479   -0.006833      1
            (122.48, 131.548]      1769.131368     1750.813992   -0.010462      1
            (131.548, 140.616]             NaN             NaN         NaN      0
            (140.616, 149.684]     2083.586370     2084.413659    0.000397      1

        """

        pcrnt_limit = 3

        vehdata = read_vehicle_data()
        vehdata['pmr'] = 1000.0 * vehdata['rated_power'] / vehdata['kerb_mass']

        all_gened = glob.glob(os.path.join(mydir, samples_dir, gened_fname_glob))
        for g_fname in all_gened:
            m = re.match(gened_fname_regex, g_fname)
            veh_num = int(m.groups()[0])
            df_g = read_sample_file(g_fname)
            df_h = read_heinz_file(veh_num)

            if abs(df_g.v_class.sum() - df_h.v_orig.sum()) > 1:
                log.warning('Cycle-mismatched(%s): gened(%s) !+ heinz(%s)!', g_fname, df_g.v_class.sum(), df_h.v_orig.sum())
                continue

            vehdata.loc[veh_num, 'gened_mean_rpm'] = df_g['rpm'].mean()
            vehdata.loc[veh_num, 'heinz_mean_rpm'] = df_h['n'].mean()

        df = vehdata.sort('pmr')[['gened_mean_rpm', 'heinz_mean_rpm']]
        dfg = df.groupby(pd.cut(vehdata.pmr, 12))
        df = dfg.mean()

        dif = (df['heinz_mean_rpm'] - df['gened_mean_rpm']) / df.min(axis=1)
        df['diff_prcnt']= dif
        df['count']= dfg.count().iloc[:, -1]

        print (df)

        diff_prcnt = df['diff_prcnt']
        np.testing.assert_array_less(abs(diff_prcnt.fillna(0)), pcrnt_limit/100)



def _run_the_experiments(transplant_original_gears=False, plot_results=False, compare_results=False, encoding="ISO-8859-1"):
    # rated_power,kerb_mass,rated_speed,idling_speed,test_mass,no_of_gears,ndv_1,ndv_2,ndv_3,ndv_4,ndv_5,ndv_6,ndv_7,ID_cat,user_def_driv_res_coeff,user_def_power_curve,f0,f1,f2,Comment
    # 0                                                            5                                10                                                    15                        19
    df = read_vehicle_data()

    for (ix, row) in df.iterrows():
        veh_num = ix

        model = goodVehicle()
        veh = model['vehicle']

        veh['test_mass'] = row['test_mass']
        veh['unladen_mass'] =  veh['test_mass'] - driver_weight
        veh['resistance_coeffs'] = list(row['f0':'f2'])
        veh['p_rated'] = row['rated_power']
        veh['n_rated'] = row['rated_speed']
        veh['n_idle'] = int(row['idling_speed'])
        ngears = int(row['no_of_gears'])
        veh['gear_ratios'] = list(row[6:6+ngears]) #'ndv_1'

        if (transplant_original_gears):
            log.warning(">>> Transplanting gears from Heinz's!")
            df_h = read_heinz_file(veh_num)

            forced_cycle = df_h['g_max']
            forced_cycle.columns = ['gears_orig']

            model['forced_cycle'] = forced_cycle

        experiment = Experiment(model)
        model = experiment.run()

        params = model['params']

        f_downscale = params['f_downscale']
        if (f_downscale > 0):
            log.warning('>> DOWNSCALE %s', f_downscale)


        # ankostis_mdb:  't', "v in km/h","v_orig","a in m/s²","gear","g_min","g_max","gear_modification","error_description"
        # heinz:         't', 'km_h', 'stg', 'gear'

        (root, ext) = os.path.splitext(vehs_data_inp_fname)
        outfname = os.path.join(mydir, samples_dir, '{}-{:05}{}'.format(root, veh_num, ext))
        df = pd.DataFrame(model['cycle_run'])

        _compare_exp_results(df, outfname, compare_results)
        df.to_csv(outfname, index_label='time')


def read_sample_file(inpfname):
    df = pd.read_csv(inpfname)

    return df


def read_heinz_file(veh_num, heinz_dir=None):
    if (heinz_dir is None):
        heinz_dir = os.path.join(mydir, samples_dir)

    vehfpath = os.path.join(heinz_dir, make_heinz_fname(veh_num))
    try:
        inpfname = glob.glob(vehfpath)[0]
    except IndexError:
        raise FileNotFoundError(vehfpath)
    df = pd.read_csv(inpfname, encoding='latin-1', header=0, index_col=3)
    assert df['vehicle_no'][0] == veh_num

#     vehfpath = os.path.join(samples_dir, 'heinz_Petrol_veh{:05}.dri'.format(veh_num))
#     inpfname = glob.glob(vehfpath)[0]
#     df = pd.read_csv(inpfname, encoding='latin-1')

    return df


###################
# COMPARE RESULTS #
###################

def _compare_exp_results(tabular, outfname, run_comparison):
    if (run_comparison):
        try:
            data_prev = read_sample_file(outfname)
            ## Compare changed-tabular
            #
            npt.assert_array_equal(tabular['gears'],  data_prev['gears'])
            # Unreached code in case of assertion.
            # cmp = tabular['gears'] != data_prev['gears']
            # if (cmp.any()):
            #     self._plotResults(data_prev)
            #     print('>> COMPARING(%s): %s'%(fname, cmp.nonzero()))
            # else:
            #     print('>> COMPARING(%s): OK'%fname)
        except FileNotFoundError:
            print('>> COMPARING(%s): No old-tabular found, 1st time to run' % outfname)
            run_comparison = False


def _plotResults(veh_fname, df_g, df_h,  g_diff, ax, plot_diffs_gears_only=True, plot_original_gears = False):
    if (plot_original_gears):
        my_gear_col = 'gears_orig'
        hz_gear_col = 'g_max'
    else:
        my_gear_col = 'gears'
        hz_gear_col = 'gear'

    ax.grid(True)

    ax2 = ax.twinx()

    tlen = len(df_g.index)
    #ax.set_xticks(np.arange(0.0, tlen, 50.0)) NO! looses auto when zooming.


    clutch = df_g['clutch']
    clutch = clutch.nonzero()[0]
    ax.vlines(clutch,  0, 0.2)

    ## Add pickers on driveability lines showing the specific msg.
    #
    driveability = df_g['driveability']
    driveability_true = driveability.apply(lambda s: isinstance(s, string_types))
    lines = ax2.vlines(driveability_true.nonzero()[0],  2, 4, 'c', picker=5)
    lines.set_urls(driveability[driveability_true])

    v_max = df_g['v_class'].max()
    ax.hlines(1 / v_max,  0, tlen, color="0.75")

    ax.plot(df_g['v_class'] / v_max)
    ax.plot(df_g['v_target'] / v_max, '-.')

#     ax.plot(df_g['rpm'] / df_g['rpm'].max())
#     p_req = df_g['p_required'] / df_g['p_required'].max()
#     p_req[p_req < 0] = 0
#     ax.plot(p_req)

    ## Plot gear diffs.
    #
    my_gears = df_g[my_gear_col]
    hz_v_real = df_h['v']
    hz_v_target = df_h['v_downscale']
    hz_gears = df_h[hz_gear_col]


    orig_gears = df_g['gears_orig']
    if plot_diffs_gears_only:
        diff_gears = my_gears != hz_gears
        difft = diff_gears.nonzero()[0]
        difft = set().union(difft,
                    difft+1, difft+2, difft+3, difft+4, difft+5, difft+6,
                    difft-1, difft-2, difft-3, difft-4, difft-5, difft-6,
        )
        difft = list(difft)
        my_gears = my_gears[difft]
        hz_gears = hz_gears[difft]
        ax2.plot(difft, my_gears.tolist(), 'o', color='red')
        ax2.plot(difft, orig_gears[difft].tolist(), 'v', color='green')
        ax2.plot(difft, hz_gears.tolist(), '*', color='blue')
    else:
        ax2.plot(my_gears.tolist(), 'o', color='red')
        ax2.plot(hz_gears.tolist(), '*', color='blue')



    ax.plot(df_g['v_real'] / v_max)

    ## Add pickers on driveability lines showing the specific msg.
    #
    hz_driveability = df_h['gear_modification']
    hz_driveability_true = ~hz_driveability.apply(np.isreal)
    lines = ax2.vlines(hz_driveability_true.nonzero()[0],  0, 2, 'm', picker=5)
    lines.set_urls(hz_driveability[hz_driveability_true])


    ax.plot(hz_v_target / v_max, '--')
    ax.plot(hz_v_real / v_max, ':')

    ax.text(0.7, 0, 'Diffs: %.4f' % g_diff, transform=ax.transAxes, bbox={'facecolor':'red', 'alpha':0.5, 'pad':10})


def plot_diffs_with_heinz(heinz_dir, experiment_num=None, transplant_original_gears=False, force_rerun_experiments=False):
    def is_experiments_outdated(outfiles):
        if not outfiles or force_rerun_experiments:
            return True

        resfiles_date = min([os.path.getmtime(file) for file in outfiles])
        checkfiles = ['../model.py', '../experiment.py', os.path.join(samples_dir, 'sample_vehicles.csv')]
        checkdates = [os.path.getmtime(os.path.join(mydir, fheinz_fname)) for fheinz_fname in checkfiles]
        modifs = [fdate > resfiles_date for fdate in checkdates]
        return any(modifs)



    def read_and_compare_experiment(samples_dir, myfname, veh_num):
        df_my = read_sample_file(myfname)
        df_hz = read_heinz_file(veh_num, samples_dir)

        ## Count base-calc errors (before dirveability).
        ndiff_gears_orig = np.count_nonzero(df_my['gears_orig'] != df_hz['g_max'])

        ## Count all errors.
        #
        my_gears = df_my['gears']
        gears_hz = df_hz['gear']
        diff_gears = (my_gears != gears_hz)
        ndiff_gears = np.count_nonzero(diff_gears)

        ## Count Acceleration-only errors.
        #
        accel = np.gradient(df_my['v_class'])
        diff_gears_accel = diff_gears[accel >= 0]
        ndiff_gears_accel = np.count_nonzero(diff_gears_accel)

        return (df_my, df_hz, ndiff_gears, ndiff_gears_accel, ndiff_gears_orig)



    fig = plt.figure()
    text_infos = fig.text(0.5, 0.5, '', transform=fig.transFigure, bbox={'facecolor':'grey', 'alpha':0.4, 'pad':10}, horizontalalignment='center', verticalalignment='center', color='blue')

    def fig_onpick(event):
        pickline = event.artist
        urls = pickline.get_urls()
        rule = urls.iloc[event.ind]
        print(rule)
        text_infos.set_text('Rule: %s' % rule)

        fig.canvas.draw()

    fig.canvas.mpl_connect('pick_event', fig_onpick)


    if experiment_num is None:
        paths = glob.glob(os.path.join(mydir, samples_dir, 'sample_vehicles-*.csv'))

        if is_experiments_outdated(paths):
            _run_the_experiments(transplant_original_gears = transplant_original_gears)
            paths = glob.glob(os.path.join(mydir, samples_dir, 'sample_vehicles-*.csv'))

        npaths          = len(paths)

        ## NOTE: Limit subplots to facilitate research.
        #
#         paths_to_plot = paths
#         paths_to_plot = paths[0:9]
#         paths_to_plot = paths[5:6] + paths[7:9] + paths[14:16] + paths[23:24]
        paths_to_plot = paths[5:8] + paths[17:18] + paths[22:24]

        ## Decide subplot-grid dimensions.
        #
        npaths_to_plot  = len(paths_to_plot)
        w = math.ceil(math.sqrt(npaths_to_plot))
        h = w-1 if ((w-1) * w >= npaths_to_plot) else w

        g_diff = np.zeros((3, npaths))
        nplotted = 0
        for (n, inpfname) in enumerate(paths):
            m = re.match(gened_fname_regex, inpfname)
            assert m


            veh_num = int(m.group(1))
            (df_my, df_hz, ndiff_gears, ndiff_gears_accel, ndiff_gears_orig) \
                                    = read_and_compare_experiment(heinz_dir, inpfname, veh_num)
            g_diff[0, n]            = ndiff_gears
            g_diff[1, n]            = ndiff_gears_accel
            g_diff[2, n]            = ndiff_gears_orig

            log.info(">> %i: %s: ±DIFFs(%i), +DIFFs(%i), ±ORIGs(%i)", n, inpfname, ndiff_gears, ndiff_gears_accel, ndiff_gears_orig)


            if (inpfname in paths_to_plot):
                nplotted += 1
                ax = fig.add_subplot(w, h, nplotted)
                veh_name = os.path.basename(inpfname)
                ax.set_title('%i: %s'%(n, veh_name), fontdict={'fontsize': 8} )
                _plotResults(veh_name, df_my, df_hz, ndiff_gears, ax, plot_original_gears = not transplant_original_gears)

        orig = 'Driveability' if transplant_original_gears else 'Pre-Driveability'
        fig.suptitle('%s: ±DIFFs: count(%i), min(%i), MEAN(%.2f±%.2f), max(%i).' % (orig, g_diff[0].sum(), g_diff[0].min(), g_diff[0].mean(), g_diff[0].std(), g_diff[0].max()))
        log.info('#       ±DIFFs: count(%i), min(%i), MEAN(%.2f±%.2f), max(%i).', g_diff[0].sum(), g_diff[0].min(), g_diff[0].mean(), g_diff[0].std(), g_diff[0].max())
        log.info('#       +DIFFs: count(%i), min(%i), MEAN(%.2f±%.2f), max(%i).', g_diff[1].sum(), g_diff[1].min(), g_diff[1].mean(), g_diff[1].std(), g_diff[1].max())
        log.info('#       ±ORIGs: count(%i), min(%i), MEAN(%.2f±%.2f), max(%i).', g_diff[2].sum(), g_diff[2].min(), g_diff[2].mean(), g_diff[2].std(), g_diff[2].max())

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
        #    Rule(f) before rule(bheinz_fname:
        #       ±DIFFs: count(5583), min(135), MEAN(186.10±57.99), max(335).
        #       +DIFFs: count(1515), min(10), MEAN(50.50±46.65), max(176).
        #    Rule(f) applied also forheinz_fnamei-2, i-3, ... signular-downshifts:
        #       ±DIFFs: count(5568), min(135), MEAN(185.60±57.59), max(335).
        #       +DIFFs: count(1500), min(10), MEAN(50.00±46.26), max(176).
        #    Precise input values:
        #       ±DIFFs: count(5569), min(135), MEAN(185.63±57.57), max(335).
        #       +DIFFs: count(1501), min(10), MEAN(50.03±46.25), max(176).
        #       ±ORIGs: count(539), min(7), MEAN(17.97±8.83), max(35).
        #    Rule(e): Cancel +1 upshift for ANY previous-gear LOWER than the upshifted one:
        #       ±DIFFs: count(5547), min(135), MEAN(184.90±56.22), max(327).
        #       +DIFFs: count(1490), min(10), MEAN(49.67±45.68), max(173).
        #       ±ORIGs: count(539), min(7), MEAN(17.97±8.83), max(35).
        #    Rule(e): Cancel ANY upshift for ANY previous-gear LOWER than the upshifted one:
        #       ±DIFFs: count(5533), min(135), MEAN(184.43±54.80), max(319).
        #       +DIFFs: count(1477), min(10), MEAN(49.23±44.40), max(161).
        #       ±ORIGs: count(539), min(7), MEAN(17.97±8.83), max(35).
        #    Rule(g): Enable mistakenly impossible rule:
        #       ±DIFFs: count(5151), min(133), MEAN(171.70±41.96), max(288).
        #       +DIFFs: count(1116), min(8), MEAN(37.20±31.94), max(113).
        #       ±ORIGs: count(539), min(7), MEAN(17.97±8.83), max(35).
        #    Rule(g): Apply only on Acell(not Flats):
        #       ±DIFFs: count(5149), min(133), MEAN(171.63±41.77), max(286).
        #       +DIFFs: count(1112), min(8), MEAN(37.07±31.73), max(112).
        #       ±ORIGs: count(539), min(7), MEAN(17.97±8.83), max(35).
        #    Rule(b2): Apply it also for flats (not only Accels):
        #       ±DIFFs: count(5142), min(133), MEAN(171.40±41.15), max(279).
        #       +DIFFs: count(1109), min(8), MEAN(36.97±31.50), max(111).
        #       ±ORIGs: count(539), min(7), MEAN(17.97±8.83), max(35).
        #    Rule(b2): Check if Accell on NEXT- time-step (A[t]).
        #           ±DIFFs: count(5275), min(133), MEAN(175.83±47.54), max(304).
        #           +DIFFs: count(1219), min(8), MEAN(40.63±36.33), max(128).
        #           ±ORIGs: count(539), min(7), MEAN(17.97±8.83), max(35).
        #    Rule(b2): Check if Accell/FLAT on NEXT- time-step (A[t]).
        #           ±DIFFs: count(5306), min(135), MEAN(176.87±47.05), max(303).
        #           +DIFFs: count(1205), min(8), MEAN(40.17±35.84), max(127).
        #           ±ORIGs: count(539), min(7), MEAN(17.97±8.83), max(35).
        #
        # TRANSPLANTED:
        #       ±DIFFs: count(4771), min(122), MEAN(159.03±42.49), max(274).
        #       +DIFFs: count(752), min(3), MEAN(25.07±31.71), max(106).
        #       ±ORIGs: count(0), min(0), MEAN(0.00±0.00), max(0).
        #    Rule(g) more greedy:
        #           ±DIFFs: count(4826), min(122), MEAN(160.87±41.65), max(268).
        #           +DIFFs: count(791), min(3), MEAN(26.37±30.30), max(101).
        #           ±ORIGs: count(0), min(0), MEAN(0.00±0.00), max(0).
        #    Apply Rule(g) on any beginning-gear (not on lower):
        #       ±DIFFs: count(4738), min(122), MEAN(157.93±37.54), max(255).
        #       +DIFFs: count(704), min(3), MEAN(23.47±26.32), max(88).
        #       ±ORIGs: count(0), min(0), MEAN(0.00±0.00), max(0).
        #    Rule(g) on Accell but beggining on Accell OR flat:
        #       ±DIFFs: count(4676), min(122), MEAN(155.87±35.53), max(249).
        #       +DIFFs: count(642), min(3), MEAN(21.40±24.08), max(82).
        #       ±ORIGs: count(0), min(0), MEAN(0.00±0.00), max(0).
        #    NO Rule(c)!
        #       ±DIFFs: count(1828), min(29), MEAN(60.93±37.66), max(157).
        #       +DIFFs: count(587), min(1), MEAN(19.57±24.41), max(81).
        #       ±ORIGs: count(0), min(0), MEAN(0.00±0.00), max(0).
        #    NO RULE(d):             !!!(BUT err++ in ACCEL-phases)!!!
        #           ±DIFFs: count(1799), min(29), MEAN(59.97±36.93), max(156).
        #           +DIFFs: count(592), min(1), MEAN(19.73±24.54), max(81).
        #           ±ORIGs: count(0), min(0), MEAN(0.00±0.00), max(0).
        #     Overlapping application of rules:
        #       ±DIFFs: count(1826), min(29), MEAN(60.87±36.32), max(150).
        #       +DIFFs: count(576), min(1), MEAN(19.20±23.23), max(77).
        #       ±ORIGs: count(0), min(0), MEAN(0.00±0.00), max(0).
        #    NO RULE(d):             !!!(BUT increase in ^^)!!!
        #           ±DIFFs: count(1800), min(29), MEAN(60.00±35.87), max(150).
        #           +DIFFs: count(582), min(1), MEAN(19.40±23.66), max(77).
        #           ±ORIGs: count(0), min(0), MEAN(0.00±0.00), max(0).
        #    AFTER CHECK WITH HEINZ b reorder b1, b2 order:
        #       ±DIFFs: count(1739), min(29), MEAN(57.97±30.61), max(132).
        #       +DIFFs: count(539), min(1), MEAN(17.97±21.02), max(72).
        #       ±ORIGs: count(0), min(0), MEAN(0.00±0.00), max(0).
        #    RENABLED Rule(c2): skip final 1st-gear.
        #       ±DIFFs: count(861), min(2), MEAN(28.70±30.43), max(105).
        #       +DIFFs: count(539), min(1), MEAN(17.97±21.02), max(72).
        #       ±ORIGs: count(0), min(0), MEAN(0.00±0.00), max(0).
        #    Rule(c2) in the x2-loop:
        #       ±DIFFs: count(831), min(1), MEAN(27.70±30.43), max(104).
        #       +DIFFs: count(539), min(1), MEAN(17.97±21.02), max(72).
        #       ±ORIGs: count(0), min(0), MEAN(0.00±0.00), max(0).
        #    Rule(a) after other rules:
        #       ±DIFFs: count(792), min(0), MEAN(26.40±30.53), max(103).
        #       +DIFFs: count(500), min(0), MEAN(16.67±21.15), max(71).
        #       ±ORIGs: count(0), min(0), MEAN(0.00±0.00), max(0).
        #    Rule(g) slightly more greedy: accept any A in starting-T:
        #       ±DIFFs: count(481), min(0), MEAN(16.03±20.84), max(77).
        #       +DIFFs: count(234), min(0), MEAN(7.80±12.90), max(47).
        #       ±ORIGs: count(0), min(0), MEAN(0.00±0.00), max(0).
        #    Rule(b2): check A>0 also for t-1 (not only t-2): But MAX++ & STDEV++
        #           ±DIFFs: count(479), min(0), MEAN(15.97±20.97), max(82).
        #           +DIFFs: count(231), min(0), MEAN(7.70±12.77), max(47).
        #           ±ORIGs: count(0), min(0), MEAN(0.00±0.00), max(0).
        #    Rule(c1): check A<0 also for t-1 (not only t-2): But MAX++ & STDEV++
        #           ±DIFFs: count(474), min(0), MEAN(15.80±21.21), max(83).
        #           +DIFFs: count(230), min(0), MEAN(7.67±12.97), max(47).
        #           ±ORIGs: count(0), min(0), MEAN(0.00±0.00), max(0).
        #    NO RULE(d):             !!!(BUT increase in ^^)!!!
        #           ±DIFFs: count(450), min(0), MEAN(15.00±20.59), max(76).
        #           +DIFFs: count(242), min(0), MEAN(8.07±13.59), max(47).
        #           ±ORIGs: count(0), min(0), MEAN(0.00±0.00), max(0).
        #    Rule(c2): check A<0 also for t (not only t-1):
        #       ±DIFFs: count(476), min(0), MEAN(15.87±21.07), max(78).
        #       +DIFFs: count(233), min(0), MEAN(7.77±13.10), max(47).
        #       ±ORIGs: count(0), min(0), MEAN(0.00±0.00), max(0).
        #    NO RULE(d):             !!!(BUT increase in ^^)!!!
        #           ±DIFFs: count(445), min(0), MEAN(14.83±20.82), max(77).
        #           +DIFFs: count(241), min(0), MEAN(8.03±13.82), max(48).
        #           ±ORIGs: count(0), min(0), MEAN(0.00±0.00), max(0).
        #    First run rules(e & g) in isolation:
        #       ±DIFFs: count(546), min(0), MEAN(18.20±24.69), max(91).
        #       +DIFFs: count(258), min(0), MEAN(8.60±14.79), max(55).
        #       ±ORIGs: count(0), min(0), MEAN(0.00±0.00), max(0).
        #    NO RULE(d):             !!!(BUT increase in ^^)!!!
        #       ±DIFFs: count(500), min(0), MEAN(16.67±23.40), max(87).
        #       +DIFFs: count(254), min(0), MEAN(8.47±14.61), max(55).
        #       ±ORIGs: count(0), min(0), MEAN(0.00±0.00), max(0).
        #    First run rules(f) in isolation: !!!
        #       ±DIFFs: count(348), min(0), MEAN(11.60±15.83), max(61).
        #       +DIFFs: count(101), min(0), MEAN(3.37±5.82), max(25).heinz_fname        #       ±ORIGs: count(0), min(0), MEAN(0.00±0.00), max(0).
        #    Rule(c1): Skip even further on decel.
        #       ±DIFFs: count(256), min(0), MEAN(8.53±13.40), max(48).
        #       +DIFFs: count(101), min(0), MEAN(3.37±5.82), max(25).
        #       ±ORIGs: count(0), min(0), MEAN(0.00±0.00), max(0).
        #    First run rules(e) in isolation, g in main-loop:
        #       ±DIFFs: count(226), min(0), MEAN(7.53±11.74), max(52).
        #       +DIFFs: count(101), min(0), MEAN(3.37±5.41), max(24).
        #       ±ORIGs: count(0), min(0), MEAN(0.00±0.00), max(0).
        #    Rule(c1) in isolation AFTER rest rules:([step_rule_g, step_rule_f][step_rule_e, step_rule_b1, step_rule_b2][step_rule_c1])
        #       ±DIFFs: count(214), min(0), MEAN(7.13±10.57), max(46).
        #       +DIFFs: count(97), min(0), MEAN(3.23±4.96), max(21).
        #       ±ORIGs: count(0), min(0), MEAN(0.00±0.00), max(0).
        #    Rule(e) above rule b1&b2:
        #           ±DIFFs: count(211), min(0), MEAN(7.03±11.47), max(46).
        #           +DIFFs: count(93), min(0), MEAN(3.10±5.88), max(24).
        #           ±ORIGs: count(0), min(0), MEAN(0.00±0.00), max(0).
        #    group rule(e & c1 (OR reversed)) ABOVE rules b1&b2:
        #           ±DIFFs: count(240), min(0), MEAN(8.00±12.87), max(53).
        #           +DIFFs: count(92), min(0), MEAN(3.07±5.83), max(24).
        #           ±ORIGs: count(0), min(0), MEAN(0.00±0.00), max(0).
        #    group rule(e & c1 ) BELOW rules b1&b2:
        #           ±DIFFs: count(230), min(0), MEAN(7.67±11.78), max(46).
        #           +DIFFs: count(106), min(0), MEAN(3.53±5.57), max(21).
        #           ±ORIGs: count(0), min(0), MEAN(0.00±0.00), max(0).
        #    group rule(e & c1 REVERSED) BELOW rules b1&b2:
        #           ±DIFFs: count(236), min(0), MEAN(7.87±12.46), max(52).
        #           +DIFFs: count(109), min(0), MEAN(3.63±5.90), max(24).
        #           ±ORIGs: count(0), min(0), MEAN(0.00±0.00), max(0).
        #    Rule(f) also applied when G(t-1) GT_or_eq G(t+1) (the same also with apply-if-diff BUG fixed):
        #       ±DIFFs: count(187), min(0), MEAN(6.23±9.27), max(37).
        #       +DIFFs: count(72), min(0),heinz_fnameMEAN(2.40±3.76), max(13).
        #       ±ORIGs: count(0), min(0), MEAN(0.00±0.00), max(0).
        #        Ungroup rules(G, F):
        #           ±DIFFs: count(189), min(0), MEAN(6.30±9.42), max(37).
        #           +DIFFs: count(74), min(0), MEAN(2.47±3.88), max(13).
        #           ±ORIGs: count(0), min(0), MEAN(0.00±0.00), max(0).
        #        Ungroup rules(F, G):
        #           ±DIFFs: count(190), min(0), MEAN(6.33±9.48), max(37).
        #           +DIFFs: count(75), min(0), MEAN(2.50±3.96), max(13).
        #           ±ORIGs: count(0), min(0), MEAN(0.00±0.00), max(0).
        #        Rule(b2): check A>0 also till t (not t-1) (the same also with apply-if-diff BUG fixed):
        #           ±DIFFs: count(209), min(0), MEAN(6.97±11.04), max(46).
        #           +DIFFs: count(70), min(0), MEAN(2.33±3.65), max(12).
        #           ±ORIGs: count(0), min(0), MEAN(0.00±0.00), max(0).
        #        Rul(b2): Check A>0 for t-1 only (not only t-2 & t-1):
        #           ±DIFFs: count(202), min(0), MEAN(6.73±10.51), max(41).
        #           +DIFFs: count(64), min(0), MEAN(2.13±3.38), max(11).
        #           ±ORIGs: count(0), min(0), MEAN(0.00±0.00), max(0).
        #        Rule(f) applied on any singletton downshift:
        #           ±DIFFs: count(204), min(0), MEAN(6.80±9.23), max(32).
        #           +DIFFs: count(88), min(0), MEAN(2.93±3.78), max(12).
        #           ±ORIGs: count(0), miheinz_fname(0), MEAN(0.00±0.00), max(0).
        #        Rule(b2) Correct:
        #           ±DIFFs: count(209), min(0), MEAN(6.97±11.04), max(46).
        #           +DIFFs: count(70), min(0), MEAN(2.33±3.65), max(12).
        #           ±ORIGs: count(0), min(0), MEAN(0.00±0.00), max(0).
        #    Rule(b2) Correct NOT checking Accel on the final step of rule(b2)!:
        #       ±DIFFs: count(187), min(0), MEAN(6.23±9.27), max(37).
        #       +DIFFs: count(72), min(0), MEAN(2.40±3.76), max(13).
        #       ±ORIGs: count(0), min(0), MEAN(0.00±0.00), max(0).
        #        Switch g with e, make e applied only for equal.
        #           ±DIFFs: count(284), min(0), MEAN(9.47±14.55), max(54).
        #           +DIFFs: count(127), min(0), MEAN(4.23±6.77), max(26).
        #           ±ORIGs: count(0), min(0), MEAN(0.00±0.00), max(0).
        #            Rule(f) applied on any singletton downshift:
        #               ±DIFFs: count(292), min(0), MEAN(9.73±14.50), max(49).
        #               +DIFFs: count(131), min(0), MEAN(4.37±6.60), max(25).
        #               ±ORIGs: count(0), min(0), heinz_fnameEAN(0.00±0.00), max(0).
        #    NO TRANSPLANT:
        #       ±DIFFs: count(772), min(7), MEAN(25.73±14.24), max(65).
        #       +DIFFs: count(499), min(2), MEAN(16.63±10.30), max(45).
        #       ±ORIGs: count(779), min(15), MEAN(25.97±8.83), max(43).
        #    Do not allow G2 when V==0:
        #       ±DIFFs: count(670), min(4), MEAN(22.33±13.88), max(61).
        #       +DIFFs: count(499), min(2), MEAN(16.63±10.30), max(45).
        #       ±ORIGs: count(719), min(13), MEAN(23.97±8.83), max(41).


    else:
        inpfname = os.path.join(mydir, samples_dir, 'sample_vehicles-{:05}.csv'.format(experiment_num))

        (df_my, df_hz, ndiff_gears, ndiff_gears_accel, ndiff_gears_orig)  = read_and_compare_experiment(inpfname, veh_num)

        ax = fig.axes()
        _plotResults(os.path.basename(inpfname), df_my, df_hz, ndiff_gears, ax)
        log.info(">> %i: %s: ±DIFFs(%i), +DIFFs(%i), ±ORIGs(%i)", n, inpfname, ndiff_gears, ndiff_gears_accel, ndiff_gears_orig)


    fig.tight_layout()
    plt.show()

if __name__ == "__main__":
    import sys

    heinz_dir               = None
    experiment_num          = None
    compare_original_gears  = False
    force_rerun_experiments = False  # Set to True to recalc experiments or 'compare_original_gears' has changed.
    try:
        if len(sys.argv) > 1:
            heinz_dir = sys.argv[1]

            if len(sys.argv) > 2:
                experiment_num = int(sys.argv[2])

                if len(sys.argv) > 3:
                    compare_original_gears = bool(sys.argv[3])
    except (ValueError, IndexError) as ex:
        exit('Help: \n  <cmd> [heinz_dir [vehicle_num]]\neg: \n  python experiment_SampleVehicleTests d:\Work/Fontaras\WLTNED\HeinzCycles\for_JRC_Petrol_* \nor \n  d:\Work/Fontaras\WLTNED\HeinzCycles\for_JRC_Petrol_*  2357')

    plot_diffs_with_heinz(heinz_dir, experiment_num=experiment_num, transplant_original_gears = compare_original_gears, force_rerun_experiments = force_rerun_experiments)
