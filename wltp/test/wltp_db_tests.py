#!/usr/bin/env python
#
# Copyright 2013-2014 European Commission (JRC);
# Licensed under the EUPL (the 'Licence');
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at: http://ec.europa.eu/idabc/eupl
'''Compares the results of a batch of wltp_db vehicles against phase-1b-alpha Heinz's tool.

* Run as Test-case to generate results for sample-vehicles.
* Run it as cmd-line to compare with Heinz's results.

:created: 28 July 2014
'''

import glob
import logging
import math
import os
import re
import unittest
from unittest.case import skip

import numpy as np
import numpy.testing as npt
import pandas as pd
from wltp.experiment import Experiment
from wltp.experiment import applyDriveabilityRules
from wltp.test.goodvehicle import goodVehicle


mydir = os.path.dirname(__file__)
samples_dir = 'wltp_db'
veh_data_fname = 'wltp_db_vehicles.csv'
gened_fname_regex = r'.*wltp_db_vehicles-(\d+).csv'
heinz_fname_regex = r'.*heinz-(\d+).csv'
gened_fname_glob = 'wltp_db_vehicles-*.csv'
driver_weight = 70
"For calculating unladen_mass."
encoding = 'UTF-8'

def init_logging(loglevel = logging.DEBUG):
    logging.basicConfig(level=loglevel)
    logging.getLogger().setLevel(level=loglevel)
    log = logging.getLogger(__name__)

    return log
log = init_logging()

def read_vehicle_data():
    df = pd.read_csv(veh_data_fname, encoding = encoding, index_col = 0)

    return df

def read_wots():
    df = pd.read_csv('wot_samples.csv', encoding = encoding, index_col = None)

    return df

def select_wot(wots, isDiesel):
    wots_labels = [ 'average Euro 6 Petrol', 'average Euro 6 Diesel']
    wots = wots[['n_norm', wots_labels[isDiesel]]]
    wots.columns = ['n_norm', 'p_norm']

    return wots

class WltpDbTests(unittest.TestCase):
    '''Compares a batch of vehicles with results obtained from "official" implementation.'''


    def setUp(self):
        self.run_comparison = True # NOTE: Set 'False' to UPDATE sample-results or run main() (assuming they are ok).
        os.chdir(os.path.join(mydir, samples_dir))


    @skip
    def test0_SampleVehicles(self, plot_results=False, encoding="UTF-8"):
        _run_the_experiments(plot_results=False, compare_results=self.run_comparison, encoding=encoding)


    def test1_Downscale(self):
        """Check mean-engine-speed diff with Heinz within some percent.

        ### Comparison history ###

        All-Vehicles, Phase-1b-beta(ver <= 0.0.8, Aug-2014)::

                             mean        std        min           max
            python      45.973545   1.640161  35.866421  4.650672e+01
            heinz       46.189082   1.125064  36.659117  4.650672e+01
            diff_prcnt   0.468830 -45.783771   2.210133  4.116024e-08
        """

        pcrnt_limit = 0.5

        h_n = []
        g_n = []
        all_gened = glob.glob(gened_fname_glob)
        for g_fname in all_gened:
            m = re.match(gened_fname_regex, g_fname)
            veh_num = int(m.groups()[0])

            df_g = read_sample_file(g_fname)
            df_h = read_heinz_file(veh_num)

            if df_g.shape[0] != df_h.shape[0]:
                log.warning('Class-mismatched(%s): gened(%s) !+ heinz(%s)!', g_fname, df_g.shape, df_h.shape)
                continue
            if abs(df_g.v_class.sum() - df_h.v_orig.sum()) > 1:
                log.warning('Cycle-mismatched(%s): gened(%s) !+ heinz(%s)!', g_fname, df_g.v_class.sum(), df_h.v_orig.sum())
                continue

            g_n.append(df_g['v_target'].mean())
            h_n.append(df_h['v'].mean())

        g_n = np.array(g_n)
        h_n = np.array(h_n)

        df = pd.DataFrame()
        df['mean'] = [g_n.mean(), h_n.mean()]
        df['std'] = [g_n.std(), h_n.std()]
        df['min'] = [g_n.min(), h_n.min()]
        df['max'] = [g_n.max(), h_n.max()]
        df.index = ['python', 'heinz']

        dff = 100 * (df.loc['heinz', :] - df.loc['python', :]) / df.min(axis=0)
        df.loc['diff_prcnt', :] = dff

        print(df)

        diff_prcnt = df.loc['diff_prcnt', 'mean']
        self.assertLess(abs(diff_prcnt), pcrnt_limit)


    def test2_AvgRPMs(self):
        """Check mean-engine-speed diff with Heinz within some percent.

        ### Comparison history ###

        Class3b-Vehicles, Phase-1b-beta(ver <= 0.0.8, Aug-2014)::

                                   mean         std          min          max
                python      1766.707825  410.762478  1135.458463  3217.428423
                heinz       1759.851498  397.343498  1185.905053  3171.826208
                diff_prcnt    -0.3896     -3.3772       4.4428      -1.4377

        All-Vehicles, Phase-1b-beta(ver <= 0.0.8, Aug-2014)::

                                   mean         std          min          max
                python      1923.908119  628.166294  1135.458463  4965.206982
                heinz       1899.366431  592.341218  1185.905053  4897.154914
                diff_prcnt    -1.292099   -6.048047     4.442839    -1.389625
        """

        pcrnt_limit = 1.3

        h_n = []
        g_n = []
        all_gened = glob.glob(gened_fname_glob)
        for g_fname in all_gened:
            m = re.match(gened_fname_regex, g_fname)
            veh_num = int(m.groups()[0])

            df_g = read_sample_file(g_fname)
            df_h = read_heinz_file(veh_num)

            if df_g.shape[0] != df_h.shape[0]:
                log.warning('Class-mismatched(%s): gened(%s) !+ heinz(%s)!', g_fname, df_g.shape, df_h.shape)
                continue
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

        dff = 100 * (df.loc['heinz', :] - df.loc['python', :]) / df.min(axis=0)
        df.loc['diff_prcnt', :] = dff

        print(df)

        diff_prcnt = df.loc['diff_prcnt', 'mean']
        self.assertLess(abs(diff_prcnt), pcrnt_limit)


    def test2_PMRatio(self):
        """Check mean-engine-speed diff with Heinz within some percent for all PMRs.

        ### Comparison history ###


        Class3b-Vehicles, Phase-1b-beta(ver <= 0.0.8, Aug-2014)::

                                gened_mean_rpm  heinz_mean_rpm  diff_ratio  count
            pmr
            (9.973, 24.823]        1566.018469     1568.360963    0.001496     32
            (24.823, 39.496]       1701.176128     1702.739797    0.000919     32
            (39.496, 54.17]        1731.541637     1724.959671   -0.003816    106
            (54.17, 68.843]        1894.477475     1877.786294   -0.008889     61
            (68.843, 83.517]       1828.518522     1818.720627   -0.005387     40
            (83.517, 98.191]       1824.060716     1830.482140    0.003520      3
            (98.191, 112.864]      1794.673461     1792.693611   -0.001104     31
            (112.864, 127.538]     3217.428423     3171.826208   -0.014377      1
            (127.538, 142.211]     1627.952896     1597.571904   -0.019017      1
            (142.211, 156.885]             NaN             NaN         NaN      0
            (156.885, 171.558]             NaN             NaN         NaN      0
            (171.558, 186.232]     1396.061758     1385.176569   -0.007858      1

        All-Vehicles, Phase-1b-beta(ver <= 0.0.8, Aug-2014)::

                                gened_mean_rpm  heinz_mean_rpm  diff_prcnt  count
            pmr
            9.973, 24.823]        1566.018469     1568.360963    0.149583     32
            (24.823, 39.496]       1694.829888     1696.482640    0.097517     34
            (39.496, 54.17]        1806.916712     1789.409819   -0.978361    120
            (54.17, 68.843]        2219.059646     2165.214662   -2.486820     94
            (68.843, 83.517]       2078.194023     2043.741660   -1.685749     59
            (83.517, 98.191]       1898.241000     1890.040533   -0.433878      4
            (98.191, 112.864]      1794.673461     1792.693611   -0.110440     31
            (112.864, 127.538]     2606.773081     2568.011660   -1.509394      2
            (127.538, 142.211]     1627.952896     1597.571904   -1.901698      1
            (142.211, 156.885]             NaN             NaN         NaN      0
            (156.885, 171.558]             NaN             NaN         NaN      0
            (171.558, 186.232]     1396.061758     1385.176569   -0.785834      1

        """

        pcrnt_limit = 2.5

        vehdata = read_vehicle_data()
        vehdata['pmr'] = 1000.0 * vehdata['rated_power'] / vehdata['kerb_mass']
        np.testing.assert_allclose(vehdata.pmr_km, vehdata.pmr)

        all_gened = glob.glob(gened_fname_glob)
        for g_fname in all_gened:
            m = re.match(gened_fname_regex, g_fname)
            veh_num = int(m.groups()[0])

            df_g = read_sample_file(g_fname)
            df_h = read_heinz_file(veh_num)

            if df_g.shape[0] != df_h.shape[0]:
                log.warning('Class-mismatched(%s): gened(%s) !+ heinz(%s)!', g_fname, df_g.shape, df_h.shape)
                continue
            if abs(df_g.v_class.sum() - df_h.v_orig.sum()) > 1:
                log.warning('Cycle-mismatched(%s): gened(%s) !+ heinz(%s)!', g_fname, df_g.v_class.sum(), df_h.v_orig.sum())
                continue


            vehdata.loc[veh_num, 'gened_mean_rpm'] = df_g['rpm'].mean()
            vehdata.loc[veh_num, 'heinz_mean_rpm'] = df_h['n'].mean()

        df = vehdata.sort('pmr')[['gened_mean_rpm', 'heinz_mean_rpm']]
        dfg = df.groupby(pd.cut(vehdata.pmr, 12))
        pmr_hist = dfg.mean()

        dif = (pmr_hist['heinz_mean_rpm'] - pmr_hist['gened_mean_rpm']) / pmr_hist.min(axis=1)
        pmr_hist['diff_prcnt']= 100 * dif
        pmr_hist['count']= dfg.count().iloc[:, -1]

        print (pmr_hist)

        diff_prcnt = pmr_hist['diff_prcnt']
        np.testing.assert_array_less(abs(diff_prcnt.fillna(0)), pcrnt_limit)


    def test2_GearDiffs(self):
        """Check diff-gears with Heinz within some percent.

        ### Comparison history ###

        Class3b-Vehicles, Phase-1b-beta(ver <= 0.0.8, Aug-2014)::

                         count       MEAN        STD  min  max
            gears        23387  75.931818  56.921729    6  279
            accell       19146  62.162338  48.831155    4  238
            senza rules  16133  52.379870  35.858415   11  170

        All-Vehicles, Phase-1b-beta(ver <= 0.0.8, Aug-2014)::

                         count        MEAN         STD  min  max  diff_prcnt
            gears        39677  104.965608  100.439783    6  524    5.831423
            accell       32573   86.171958   82.613475    4  404    4.787331
            senza rules  34109   90.235450  109.283901   11  600    5.013081
        """

        pcrnt_limit = 6

        (g_diff, diff_results) = _compare_gears_with_heinz()

        df = pd.DataFrame([
            [ g_diff[0].sum(), g_diff[0].mean(), g_diff[0].std(), g_diff[0].min(), g_diff[0].max() ],
            [ g_diff[1].sum(), g_diff[1].mean(), g_diff[1].std(), g_diff[1].min(), g_diff[1].max() ],
            [ g_diff[2].sum(), g_diff[2].mean(), g_diff[2].std(), g_diff[2].min(), g_diff[2].max() ]
        ], columns=['count', 'MEAN', 'STD', 'min', 'max'], index=['gears', 'accell','senza rules'])

        df['diff_prcnt'] = 100 * df['MEAN'] / 1800 # class3-duration

        print(df)

        np.testing.assert_array_less(abs(df['diff_prcnt']), pcrnt_limit)


def _run_the_experiments(transplant_original_gears=False, plot_results=False, compare_results=False, encoding="UTF-8"):
    # rated_power,kerb_mass,rated_speed,idling_speed,test_mass,no_of_gears,ndv_1,ndv_2,ndv_3,ndv_4,ndv_5,ndv_6,ndv_7,ID_cat,user_def_driv_res_coeff,user_def_power_curve,f0,f1,f2,Comment
    # 0                                                            5                                10                                                    15                        19
    df = read_vehicle_data()
    wots = read_wots()

    for (ix, row) in df.iterrows():
        veh_num = ix

        model = goodVehicle()
        veh = model['vehicle']

        veh['test_mass'] = row['test_mass']
        veh['unladen_mass'] = row['test_mass'] - driver_weight
        veh['resistance_coeffs'] = list(row['f0_real':'f2_real'])
        veh['p_rated'] = row['rated_power']
        veh['n_rated'] = row['rated_speed']
        veh['n_idle'] = int(row['idling_speed'])
        ngears = int(row['no_of_gears'])
        veh['gear_ratios'] = list(row['ndv_1':'ndv_%s'%ngears]) #'ndv_1'
        veh['full_load_curve'] = select_wot(wots, row['IDcat'] == 2)

        ## Override always class-3.
        model['params'] = {'wltc_class': 'class3b'}

        try:
            experiment = Experiment(model)
            model = experiment.run()
        except Exception as ex:
            log.warning('VEHICLE_FAILED(%s): %s', veh_num, str(ex))
        else:
            if (transplant_original_gears):
                log.warning(">>> Transplanting gears from Heinz's!")
                cycle_run = model['cycle_run']
                df_h = read_heinz_file(veh_num)
                GEARS = np.array(df_h['g_max'])
                cycle_run['gears_orig'] = GEARS.copy()

                V = np.array(cycle_run['v_class'])
                A = np.append(np.diff(V), 0)
                CLUTCH = np.array(cycle_run['clutch'])
                driveability_issues = np.empty_like(V, dtype=object)
                driveability_issues[:] = ''
                applyDriveabilityRules(V, A, GEARS, CLUTCH, len(veh['gear_ratios']), driveability_issues)

                cycle_run['gears'] = GEARS

            params = model['params']

            f_downscale = params['f_downscale']
            if (f_downscale > 0):
                log.warning('>> DOWNSCALE %s', f_downscale)


            # ankostis_mdb:  't', "v in km/h","v_orig","a in m/s²","gear","g_min","g_max","gear_modification","error_description"
            # heinz:         't', 'km_h', 'stg', 'gear'

            (root, ext) = os.path.splitext(veh_data_fname)
            outfname = '{}-{:05}{}'.format(root, veh_num, ext)
            df = pd.DataFrame(model['cycle_run'])

            _compare_exp_results(df, outfname, compare_results)
            df.to_csv(outfname, index_label='time')



def read_sample_file(inpfname):
    df = pd.read_csv(inpfname, header=0, index_col=0)
    assert df.index.name == 'time', df.index.name

    return df


def read_heinz_file(veh_num):
    vehfpath = 'heinz-{:04}.csv'.format(veh_num)
    try:
        inpfname = glob.glob(vehfpath)[0]
    except IndexError:
        raise FileNotFoundError("Skipped veh_id(%s), no file found: %s" % (veh_num, vehfpath))

    df = pd.read_csv(inpfname, encoding='UTF-8', header=0, index_col=0)
    assert df.index.name == 't', df.index.name


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
            npt.assert_array_equal(tabular['gears'],  data_prev['gears'], outfname)
            # Unreached code in case of assertion.
            # cmp = tabular['gears'] != data_prev['gears']
            # if (cmp.any()):
            #     self._plotResults(data_prev)
            #     print('>> COMPARING(%s): %s'%(fname, cmp.nonzero()))
            # else:
            #     print('>> COMPARING(%s): OK'%fname)
        except OSError as ex:  # @UnusedVariable
            print('>> COMPARING(%s): No old-tabular found, 1st time to run' % outfname)
            run_comparison = False



def _compare_gears_with_heinz(experiment_num=None, transplant_original_gears=False, force_rerun_experiments=False):
    def is_experiments_outdated(outfiles):
        if not outfiles or force_rerun_experiments:
            return True

        resfiles_date = min([os.path.getmtime(file) for file in outfiles])
        checkfiles = ['../../model.py', '../../experiment.py', 'wltp_db_vehicles.csv']
        checkdates = [os.path.getmtime(heinz_fname) for heinz_fname in checkfiles]
        modifs = [fdate > resfiles_date for fdate in checkdates]
        return any(modifs)



    def read_and_compare_experiment(myfname, veh_num):
        df_my = read_sample_file(myfname)
        df_hz = read_heinz_file(veh_num)

        if df_my.shape[0] != df_hz.shape[0]:
            log.warning('Class-mismatched(%s): gened(%s) !+ heinz(%s)!', myfname, df_my.shape, df_hz.shape)

            return None
        if abs(df_my.v_class.sum() - df_hz.v_orig.sum()) > 1:
            log.warning('Cycle-mismatched(%s): gened(%s) !+ heinz(%s)!', myfname, df_my.v_class.sum(), df_hz.v_orig.sum())

            return None

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


    if experiment_num is None:
        paths = glob.glob(gened_fname_glob)

        if is_experiments_outdated(paths):
            _run_the_experiments(transplant_original_gears = transplant_original_gears)
            paths = glob.glob(gened_fname_glob)


        g_diff = []
        diff_results = []
        for (n, inpfname) in enumerate(paths):
            m = re.match(gened_fname_regex, inpfname)
            assert m, inpfname


            veh_num = int(m.group(1))
            file_res                = read_and_compare_experiment(inpfname, veh_num)
            if file_res is None:
                continue
            (df_my, df_hz, ndiff_gears, ndiff_gears_accel, ndiff_gears_orig) = file_res
            diff_results.append((inpfname, ) + file_res)

            g_diff.append((inpfname, ndiff_gears, ndiff_gears_accel, ndiff_gears_orig))

            log.info(">> %i: %s: ±DIFFs(%i), +DIFFs(%i), ±ORIGs(%i)", n, inpfname, ndiff_gears, ndiff_gears_accel, ndiff_gears_orig)

        a = np.array(g_diff)
        g_diff = pd.DataFrame(a[:, 1:])
        g_diff.index = a[:, 0]
        g_diff = g_diff.convert_objects(convert_numeric=True)

        return g_diff, diff_results
        ## RESULTS:
        #    Rule(b2) Correct NOT checking Accel on the final step of rule(b2)!:
        #       ±DIFFs: count(187), min(0), MEAN(6.23±9.27), max(37).
        #       +DIFFs: count(72), min(0), MEAN(2.40±3.76), max(13).
        #       ±ORIGs: count(0), min(0), MEAN(0.00±0.00), max(0).
        #        Switch g with e, make e applied only for equal.
        #           ±DIFFs: count(284), min(0), MEAN(9.47±14.55), max(54).
        #           +DIFFs: count(127), min(0), MEAN(4.23±6.77), max(26).
        #           ±ORIGs: count(0), min(0), MEAN(0.00±0.00), max(0).
        #            Rule(heinz_fname) applied on any singletton downshift:
        #               ±DIFFs: count(292), min(0), MEAN(9.73±14.50), max(49).
        #               +DIFFs: count(131), min(0), MEAN(4.37±6.60), max(25).
        #               ±ORIGs: count(0), min(0), MEAN(0.00±0.00), max(0).
        #    NO TRANSPLANT:
        #       ±DIFFs: count(772), min(7), MEAN(25.73±14.24), max(65).
        #       +DIFFs: count(499), min(2), MEAN(16.63±10.30), max(45).
        #       ±ORIGs: count(779), min(15), MEAN(25.97±8.83), max(43).
        #    Do not allow G2 when V==0:
        #       ±DIFFs: count(670), min(4), MEAN(22.33±13.88), max(61).
        #       +DIFFs: count(499), min(2), MEAN(16.63±10.30), max(45).
        #       ±ORIGs: count(719), min(13), MEAN(23.97±8.83), max(41).


    else:
        inpfname = 'sample_vehicles-{:05}.csv'.format(experiment_num)

        (df_my, df_hz, ndiff_gears, ndiff_gears_accel, ndiff_gears_orig)  = read_and_compare_experiment(inpfname, veh_num)

        log.info(">> %i: %s: ±DIFFs(%i), +DIFFs(%i), ±ORIGs(%i)", n, inpfname, ndiff_gears, ndiff_gears_accel, ndiff_gears_orig)



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
    driveability_true = driveability.apply(lambda s: isinstance(s, str))
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



def plot_diffs_with_heinz(diff_results, g_diff, transplant_original_gears=False):
    from matplotlib import pyplot as plt

    def fig_onpick(event):
        pickline = event.artist
        urls = pickline.get_urls()
        rule = urls.iloc[event.ind]
        print(rule)
        text_infos.set_text('Rule: %s' % rule)

        fig.canvas.draw()

    fig = plt.figure()
    text_infos = fig.text(0.5, 0.5, '', transform=fig.transFigure, bbox={'facecolor':'grey', 'alpha':0.4, 'pad':10}, horizontalalignment='center', verticalalignment='center', color='blue')
    fig.canvas.mpl_connect('pick_event', fig_onpick)
    orig = 'Driveability' if transplant_original_gears else 'Pre-Driveability'
    fig.suptitle('%s: ±DIFFs: count(%i), min(%i), MEAN(%.2f±%.2f), max(%i).' % (orig, g_diff[0].sum(), g_diff[0].min(), g_diff[0].mean(), g_diff[0].std(), g_diff[0].max()))

        ## NOTE: Limit subplots to facilitate research.
        #
#         i_to_plot = paths
#         i_to_plot = paths[0:9]
#         i_to_plot = paths[5:6] + paths[7:9] + paths[14:16] + paths[23:24]
    i_to_plot = range[5:8] + range[17:18] + range[22:24]

    ## Decide subplot-grid dimensions.
    #
    npaths_to_plot  = len(i_to_plot)
    w = math.ceil(math.sqrt(npaths_to_plot))
    h = w-1 if ((w-1) * w >= npaths_to_plot) else w

    nplotted = 0

    for (i, diff) in enumerate(diff_results):
        (inpfname, df_my, df_hz, ndiff_gears, ndiff_gears_accel, ndiff_gears_orig) = diff
        if (i in i_to_plot):
            nplotted += 1
            ax = fig.add_subplot(w, h, nplotted)
            veh_name = os.path.basename(inpfname)
            ax.set_title('%i: %s'%(i, veh_name), fontdict={'fontsize': 8} )
            _plotResults(veh_name, df_my, df_hz, ndiff_gears, ax, plot_original_gears = not transplant_original_gears)

    fig.tight_layout()
    plt.show()




if __name__ == "__main__":
    import sys

    heinz_dir               = None
    experiment_num          = None
    compare_original_gears  = False
    force_rerun_experiments = False  # Set to True to recalc experiments or 'compare_original_gears' has changed.
    os.chdir(os.path.join(mydir, samples_dir))
    try:
        if len(sys.argv) > 1:
            heinz_dir = sys.argv[1]

            if len(sys.argv) > 2:
                experiment_num = int(sys.argv[2])

                if len(sys.argv) > 3:
                    compare_original_gears = bool(sys.argv[3])
    except (ValueError, IndexError) as ex:
        exit('Help: \n  <cmd> [heinz_dir [vehicle_num]]\neg: \n  python experiment_SampleVehicleTests d:\Work/Fontaras\WLTNED\HeinzCycles\for_JRC_Petrol_* \nor \n  d:\Work/Fontaras\WLTNED\HeinzCycles\for_JRC_Petrol_*  2357')

    (diff_results, g_diff) = _compare_gears_with_heinz(transplant_original_gears = compare_original_gears, force_rerun_experiments = force_rerun_experiments)
    plot_diffs_with_heinz(diff_results, g_diff, transplant_original_gears = compare_original_gears)
