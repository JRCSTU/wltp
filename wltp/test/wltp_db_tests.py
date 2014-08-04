#!/usr/bin/env python
#
# Copyright 2013-2014 European Commission (JRC);
# Licensed under the EUPL (the 'Licence');
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at: http://ec.europa.eu/idabc/eupl
'''Compares the results of a batch of wltp_db vehicles against Heinz's tool.

* Run as Test-case to generate results for sample-vehicles.
* Run it as cmd-line to compare with Heinz's results.

:created: 28 July 2014
'''

from matplotlib import pyplot as plt
from wltp.experiment import Experiment
from wltp.test.goodvehicle import goodVehicle
from wltp.experiment import applyDriveabilityRules
import glob
import logging
import math
import numpy as np
import numpy.testing as npt
import os
import pandas as pd
import re
import unittest


mydir = os.path.dirname(__file__)
samples_folder = 'wltp_db'

def init_logging(loglevel = logging.DEBUG):
    logging.basicConfig(level=loglevel)
    logging.getLogger().setLevel(level=loglevel)
    log = logging.getLogger(__name__)

    return log
log = init_logging()


class WltpDbTests(unittest.TestCase):
    '''Compares a batch of vehicles with results obtained from "official" implementation.'''


    def setUp(self):
        self.run_comparison = True # NOTE: Set 'False' to UPDATE sample-results or run main() (assuming they are ok).
        os.chdir(mydir)


    def testSampleVehicles(self, plot_results=False, encoding="UTF-8"):
        run_the_experiments(plot_results=False, compare_results=self.run_comparison, encoding=encoding)


def run_the_experiments(transplant_original_gears=False, plot_results=False, compare_results=False, encoding="UTF-8"):
    # rated_power,kerb_mass,rated_speed,idling_speed,test_mass,no_of_gears,ndv_1,ndv_2,ndv_3,ndv_4,ndv_5,ndv_6,ndv_7,ID_cat,user_def_driv_res_coeff,user_def_power_curve,f0,f1,f2,Comment
    # 0                                                            5                                10                                                    15                        19
    csvfname = 'wltp_db_vehicles.csv'
    csvfname = os.path.join(mydir, samples_folder, csvfname)
    df = pd.read_csv(csvfname, encoding = encoding, index_col = 0)

    for (ix, row) in df.iterrows():
        veh_num = ix

        model = goodVehicle()
        veh = model['vehicle']

        veh['mass'] = row['test_mass']
        veh['resistance_coeffs'] = list(row['f0_real':'f2_real'])
        veh['p_rated'] = row['rated_power']
        veh['n_rated'] = row['rated_speed']
        veh['n_idle'] = int(row['idling_speed'])
        ngears = int(row['no_of_gears'])
        veh['gear_ratios'] = list(row[6:6+ngears]) #'ndv_1'

        experiment = Experiment(model)
        model = experiment.run()

        if (transplant_original_gears):
            log.warning(">>> Transplanting gears from Heinz's!")
            cycle_run = model['cycle_run']
            hz_df = read_heinz_file(veh_num)
            GEARS = np.array(hz_df['g_max'])
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

        (root, ext) = os.path.splitext(csvfname)
        outfname = '{}-{:05}{}'.format(root, veh_num, ext)
        df = pd.DataFrame(model['cycle_run'])

        compare_exp_results(df, outfname, compare_results)
        df.to_csv(outfname, index_label='time')


def read_sample_file(inpfname):
    df = pd.read_csv(inpfname)

    return df


def read_heinz_file(veh_num, heinz_dir=None):
    if (heinz_dir is None):
        heinz_dir = os.path.join(mydir, samples_folder)

    vehfpath = os.path.join(heinz_dir, 'Heinz-{}-*.csv'.format(veh_num))
    try:
        inpfname = glob.glob(vehfpath)[0]
    except IndexError:
        raise FileNotFoundError("Skipped veh_id(%s), no file found: %s" % (veh_num, vehfpath))

    df = pd.read_csv(inpfname, encoding='UTF-8', header=0, index_col=21)
    assert df['vehicle_no'][0] == veh_num

#     vehfpath = os.path.join(samples_folder, 'heinz_Petrol_veh{:05}.dri'.format(veh_num))
#     inpfname = glob.glob(vehfpath)[0]
#     df = pd.read_csv(inpfname, encoding='latin-1')

    return df


###################
# COMPARE RESULTS #
###################

def compare_exp_results(tabular, outfname, run_comparison):
    if (run_comparison):
        try:
            data_prev = read_sample_file(outfname)
            ## Compare changed-tabular
            #
            npt.assert_array_equal(tabular['gears'],  data_prev['gears'])
            # Unreached code in case of assertion.
            # cmp = tabular['gears'] != data_prev['gears']
            # if (cmp.any()):
            #     self.plotResults(data_prev)
            #     print('>> COMPARING(%s): %s'%(fname, cmp.nonzero()))
            # else:
            #     print('>> COMPARING(%s): OK'%fname)
        except OSError as ex:  # @UnusedVariable
            print('>> COMPARING(%s): No old-tabular found, 1st time to run' % outfname)
            run_comparison = False


def plotResults(veh_fname, my_df, hz_df,  g_diff, ax, plot_diffs_gears_only=True, plot_original_gears = False):
    if (plot_original_gears):
        my_gear_col = 'gears_orig'
        hz_gear_col = 'g_max'
    else:
        my_gear_col = 'gears'
        hz_gear_col = 'gear'

    ax.grid(True)

    ax2 = ax.twinx()

    tlen = len(my_df.index)
    #ax.set_xticks(np.arange(0.0, tlen, 50.0)) NO! looses auto when zooming.


    clutch = my_df['clutch']
    clutch = clutch.nonzero()[0]
    ax.vlines(clutch,  0, 0.2)

    ## Add pickers on driveability lines showing the specific msg.
    #
    driveability = my_df['driveability']
    driveability_true = driveability.apply(lambda s: isinstance(s, str))
    lines = ax2.vlines(driveability_true.nonzero()[0],  2, 4, 'c', picker=5)
    lines.set_urls(driveability[driveability_true])

    v_max = my_df['v_class'].max()
    ax.hlines(1 / v_max,  0, tlen, color="0.75")

    ax.plot(my_df['v_class'] / v_max)
    ax.plot(my_df['v_target'] / v_max, '-.')

#     ax.plot(my_df['rpm'] / my_df['rpm'].max())
#     p_req = my_df['p_required'] / my_df['p_required'].max()
#     p_req[p_req < 0] = 0
#     ax.plot(p_req)

    ## Plot gear diffs.
    #
    my_gears = my_df[my_gear_col]
    hz_v_real = hz_df['v']
    hz_v_target = hz_df['v_downscale']
    hz_gears = hz_df[hz_gear_col]


    orig_gears = my_df['gears_orig']
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



    ax.plot(my_df['v_real'] / v_max)

    ## Add pickers on driveability lines showing the specific msg.
    #
    hz_driveability = hz_df['gear_modification']
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
        checkfiles = ['../model.py', '../experiment.py', 'samples/sample_vehicles.csv']
        checkdates = [os.path.getmtime(os.path.join(mydir, heinz_fname)) for heinz_fname in checkfiles]
        modifs = [fdate > resfiles_date for fdate in checkdates]
        return any(modifs)



    def read_and_compare_experiment(samples_folder, myfname, veh_num):
        df_my = read_sample_file(myfname)
        df_hz = read_heinz_file(veh_num, samples_folder)

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
        paths = glob.glob(os.path.join(mydir, samples_folder, 'sample_vehicles-*-*.csv'))

        if is_experiments_outdated(paths):
            run_the_experiments(transplant_original_gears = transplant_original_gears)
            paths = glob.glob(os.path.join(mydir, samples_folder, 'sample_vehicles-*.csv'))

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
            m = re.match('.*sample_vehicles-\w*-(\d+).csv', inpfname)
            assert m, inpfname


            veh_num = int(m.group(1))
            file_res                = read_and_compare_experiment(heinz_dir, inpfname, veh_num)
            (df_my, df_hz, ndiff_gears, ndiff_gears_accel, ndiff_gears_orig) = file_res

            g_diff[0, n]            = ndiff_gears
            g_diff[1, n]            = ndiff_gears_accel
            g_diff[2, n]            = ndiff_gears_orig

            log.info(">> %i: %s: ±DIFFs(%i), +DIFFs(%i), ±ORIGs(%i)", n, inpfname, ndiff_gears, ndiff_gears_accel, ndiff_gears_orig)


            if (inpfname in paths_to_plot):
                nplotted += 1
                ax = fig.add_subplot(w, h, nplotted)
                veh_name = os.path.basename(inpfname)
                ax.set_title('%i: %s'%(n, veh_name), fontdict={'fontsize': 8} )
                plotResults(veh_name, df_my, df_hz, ndiff_gears, ax, plot_original_gears = not transplant_original_gears)

        orig = 'Driveability' if transplant_original_gears else 'Pre-Driveability'
        fig.suptitle('%s: ±DIFFs: count(%i), min(%i), MEAN(%.2f±%.2f), max(%i).' % (orig, g_diff[0].sum(), g_diff[0].min(), g_diff[0].mean(), g_diff[0].std(), g_diff[0].max()))
        log.info('#       ±DIFFs: count(%i), min(%i), MEAN(%.2f±%.2f), max(%i).', g_diff[0].sum(), g_diff[0].min(), g_diff[0].mean(), g_diff[0].std(), g_diff[0].max())
        log.info('#       +DIFFs: count(%i), min(%i), MEAN(%.2f±%.2f), max(%i).', g_diff[1].sum(), g_diff[1].min(), g_diff[1].mean(), g_diff[1].std(), g_diff[1].max())
        log.info('#       ±ORIGs: count(%i), min(%i), MEAN(%.2f±%.2f), max(%i).', g_diff[2].sum(), g_diff[2].min(), g_diff[2].mean(), g_diff[2].std(), g_diff[2].max())

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
        inpfname = os.path.join(mydir, samples_folder, 'sample_vehicles-{:05}.csv'.format(experiment_num))

        (df_my, df_hz, ndiff_gears, ndiff_gears_accel, ndiff_gears_orig)  = read_and_compare_experiment(inpfname, veh_num)

        ax = fig.axes()
        plotResults(os.path.basename(inpfname), df_my, df_hz, ndiff_gears, ax)
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
