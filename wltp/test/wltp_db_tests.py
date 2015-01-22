#! python
#-*- coding: utf-8 -*-
#
# Copyright 2013-2014 European Commission (JRC);
# Licensed under the EUPL (the 'Licence');
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at: http://ec.europa.eu/idabc/eupl
'''Compares the results of a batch of wltp_db vehicles against phase-1b-alpha Heinz's tool.

* Run as Test-case to generate results for sample-vehicles.
* Run it as cmd-line to compare with Heinz's results.
'''

from __future__ import division, print_function, unicode_literals

from collections import OrderedDict
import glob
import logging
import math
import os
import re
import unittest
from unittest.case import skipIf

from six import string_types
from wltp import utils
from wltp.utils import memoize

import numpy as np
import numpy.testing as npt
import pandas as pd

from ..experiment import Experiment
from ..utils import FileNotFoundError
from .goodvehicle import goodVehicle


overwrite_old_results   = True # NOTE: Set 'False' to UPDATE sample-results or run main() (assuming they are ok).
force_rerun             = False

mydir = os.path.dirname(__file__)
samples_dir = 'wltp_db'
vehs_data_inp_fname = 'wltp_db_vehicles.csv'
vehs_data_out_fname = 'wltp_db_vehicles_out.csv'
gened_fname_regex = r'.*wltp_db_vehicles-(\d+).csv'
heinz_fname_regex = r'.*heinz-(\d+).csv'
gened_fname_glob = 'wltp_db_vehicles-*.csv'
trans_fname_glob = 'trans-wltp_db_vehicles-*.csv'
driver_weight = 70
"For calculating unladen_mass."
encoding = 'UTF-8'
#desc_columns_to_print = ['mean', 'std', 'min', 'max']


def _init_logging(loglevel = logging.DEBUG):
    logging.basicConfig(level=loglevel)
    logging.getLogger().setLevel(level=loglevel)
    log = logging.getLogger(__name__)

    return log
log = _init_logging()


@memoize
def _read_vehicles_inp():
    df = pd.read_csv(vehs_data_inp_fname, encoding=encoding, index_col = 0)

    return df.copy()

def _read_vehicles_out():
    try:
        df = pd.read_csv(vehs_data_out_fname, encoding=encoding, index_col = 0)
        return df
    except Exception:
        ## File corrupts if run interrupted.
        return None

    return df.copy()

def _write_vehicle_data(df):
    df = df.to_csv(vehs_data_out_fname, encoding=encoding)

@memoize
def _read_wots():
    df = pd.read_csv('wot_samples.csv', encoding=encoding, index_col = None)

    return df.copy()

def _select_wot(wots, isDiesel):
    wots_labels = [ 'average Euro 6 Petrol', 'average Euro 6 Diesel']
    wots = wots[['n_norm', wots_labels[isDiesel]]]
    wots.columns = ['n_norm', 'p_norm']

    return wots

def _make_gened_fname(transplant_original_gears, veh_num):
    root, ext = os.path.splitext(vehs_data_inp_fname)
    transplant = 'trans-' if transplant_original_gears else ''
    outfname = '{}{}-{:04}{}'.format(transplant, root, veh_num, ext)

    return outfname

def _make_heinz_fname(veh_num):
    return 'heinz-{:04}.csv'.format(veh_num)


@memoize
def _read_gened_file(inpfname):
    df = pd.read_csv(inpfname, header=0, index_col=0)
    assert not df.empty
    assert df.index.name == 'time', \
            df.index.name

    return df.copy()

@memoize
def _read_heinz_file(veh_num):
    vehfpath = _make_heinz_fname(veh_num)
    try:
        inpfname = glob.glob(vehfpath)[0]
    except IndexError:
        raise FileNotFoundError("Skipped veh_id(%s), no file found: %s" % (veh_num, vehfpath))

    df = pd.read_csv(inpfname, encoding='UTF-8', header=0, index_col=0)
    assert not df.empty
    assert df.index.name == 't', df.index.name

    return df.copy()


_sources_latest_date = None
def _is_file_up_to_date(result_file, other_dependency_files = ()):

    result_fnames = [result_file, vehs_data_out_fname]
    if force_rerun or not all(os.path.exists(f) for f in result_fnames):
        return False
    results_date = max([os.path.getmtime(file) for file in result_fnames])

    if _sources_latest_date is None:
        source_fnames = [__file__, '../../model.py', '../../experiment.py', vehs_data_inp_fname]
        _sources_latest_dep_date = max([os.path.getmtime(file) for file in source_fnames])

    latest_dep_date = max([os.path.getmtime(file) for file in other_dependency_files])
    latest_dep_date = max(latest_dep_date, _sources_latest_dep_date)

    return results_date > latest_dep_date


def _file_pairs(fname_glob):
    """
    Generates pairs of files to compare, skipping non-existent and those with mismatching #_of_rows.

    Example:

    >>> for (veh_num, df_g, df_h) in _file_pairs('wltp_db_vehicles-00*.csv')
            pass
    """

    all_gened = sorted(glob.glob(fname_glob))
    for g_fname in all_gened:
        m = re.match(gened_fname_regex, g_fname)
        veh_num = int(m.groups()[0])

        df_g = _read_gened_file(g_fname)
        df_h = _read_heinz_file(veh_num)

        if df_g.shape[0] != df_h.shape[0]:
            log.warning('Class-mismatched(%s): gened(%s) !+ heinz(%s)!', g_fname, df_g.shape, df_h.shape)
            continue
        if abs(df_g.v_class.sum() - df_h.v_orig.sum()) > 1:
            log.warning('Cycle-mismatched(%s): gened(%s) !+ heinz(%s)!', g_fname, df_g.v_class.sum(), df_h.v_orig.sum())
            continue

        yield (veh_num, df_g, df_h)

def vehicles_applicator(fname_glob, pair_func):
    """
    Applies the fun onto a pair of (generated, heinz) files for each tested-vehicle in the glob and
    appends results to list, preffixed by veh_num.

    :param pair_func: signature: func(veh_no, gened_df, heinz_df)-->sequence_of_numbers
    :return: a dataframe with the columns returned from the pair_func, row_indexed by veh_num
    """

    res = []
    for (veh_num, df_g, df_h) in _file_pairs(fname_glob):
        row = pair_func(veh_num, df_g, df_h)
        res.append([int(veh_num)] + list(row))
    assert len(res) > 0

    ares = np.array(res)
    df = pd.DataFrame(ares[:, 1:], index=ares[:, 0])

    return df


def aggregate_single_columns_means(gened_column, heinz_column):
    """
    Runs experiments and aggregates mean-values from one column of each (gened, heinz) file-sets.
    """
    vehdata = _run_the_experiments(transplant_original_gears=False, compare_results=False)


    res = vehicles_applicator(gened_fname_glob, lambda _, df_g, df_h:(
            df_g[gened_column].mean(), df_h[heinz_column].mean()))
    res.columns = ['gened', 'heinz']
    vehdata = vehdata.merge(res, how='inner', left_index=True, right_index=True).sort()
    return vehdata



class WltpDbTests(unittest.TestCase):
    '''Compares a batch of vehicles with results obtained from "official" implementation.'''

#      @classmethod
#     def setUpClass(cls):

    def setUp(self):
        self.run_comparison = overwrite_old_results
        os.chdir(os.path.join(mydir, samples_dir))


    #@skip
    def test0_runExperiment(self, plot_results=False, encoding="UTF-8"):
        _run_the_experiments(transplant_original_gears=False, compare_results=self.run_comparison, encoding=encoding)

    #@skip
    def test0_runExperimentTransplant(self, plot_results=False, encoding="UTF-8"):
        _run_the_experiments(transplant_original_gears=True, compare_results=self.run_comparison, encoding=encoding)



    def test1_Downscale(self):
        """Check mean-downscaled-velocity diff with Heinz within some percent.

        ### Comparison history ###

        Force class3b, Phase-1b-beta(ver <= 0.0.8, Aug-2014) with Heinz maxt gear-time=2sec::

                       python       heinz    diff_prcnt
            count  378.000000  378.000000  0.000000e+00
            mean    45.973545   46.189082  4.688300e-01
            std      1.642335    1.126555 -4.578377e+01
            min     35.866421   36.659117  2.210133e+00
            25%     46.506718   46.504909 -3.892020e-03
            50%     46.506718   46.506504 -4.620879e-04
            75%     46.506718   46.506719  4.116024e-08
            max     46.506718   46.506719  4.116024e-08

        Not forcing class3b, honoring declared v_max & unladen_mass::

                       python       heinz    diff_prcnt
            count  382.000000  382.000000  0.000000e+00
            mean    44.821337   44.846671  5.652189e-02
            std      5.054214    5.050208 -7.933394e-02
            min     28.091672   28.388418  1.056347e+00
            25%     46.506718   46.504868 -3.978244e-03
            50%     46.506718   46.506478 -5.162230e-04
            75%     46.506718   46.506719  4.116033e-08
            max     46.506718   46.506719  4.116033e-08
        """

        pcrnt_limit = 0.09

        res = vehicles_applicator(gened_fname_glob, lambda _, df_g, df_h:
                                          (df_g['v_target'].mean(), df_h['v'].mean()))
        res.columns = ['python', 'heinz']

        df = res.describe()

        df['diff_prcnt'] = 100 * (df.heinz - df.python) / df.min(axis=1)
        print(df)

        diff_prcnt = df.loc['mean', 'diff_prcnt']
        self.assertLess(np.abs(diff_prcnt), pcrnt_limit)


    def _check_gear_diffs(self, fname_glob):
        def read_and_compare_experiment(veh_num, df_my, df_hz):
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

            return (ndiff_gears, ndiff_gears_accel, ndiff_gears_orig)

        res = vehicles_applicator(fname_glob, read_and_compare_experiment)
        res.columns = ['diff_gears', 'diff_accel', 'diff_orig']

        res_totals = res.describe()
        res_totals.loc['sum', :] = res.sum(axis=0)
        res_totals.loc['mean%', :] = 100 * res_totals.loc['mean', :] / 1800 # class3-duration

        return res_totals

    def test2a_gear_diffs(self):
        """Check diff-gears with Heinz stays within some percent.

        ### Comparison history ###

        Class3b-Vehicles, Phase-1b-beta(ver <= 0.0.8, Aug-2014) with Heinz maxt gear-time=2sec::

                         count       MEAN        STD  min  max
            gears        23387  75.931818  56.921729    6  279
            accell       19146  62.162338  48.831155    4  238
            senza rules  16133  52.379870  35.858415   11  170

        Separated test/unladen masses::

                     diff_gears    diff_accel     diff_orig
            count    378.000000    378.000000    378.000000
            mean     104.965608     86.171958     90.235450
            std      100.439783     82.613475    109.283901
            min        6.000000      4.000000     11.000000
            25%       36.250000     25.250000     23.000000
            50%       69.000000     57.500000     51.000000
            75%      142.000000    119.750000    104.750000
            max      524.000000    404.000000    600.000000
            sum    39677.000000  32573.000000  34109.000000
            mean%      5.831423      4.787331      5.013081

        Not forcing class3b, honoring declared v_max & unladen_mass::

                     diff_gears    diff_accel     diff_orig
            count    382.000000    382.000000    382.000000
            mean      75.994764     63.633508     54.083770
            std       58.290971     51.885162     38.762326
            min        2.000000      2.000000      6.000000
            25%       29.000000     22.000000     19.000000
            50%       57.000000     48.500000     45.000000
            75%      111.000000     97.000000     78.750000
            max      279.000000    243.000000    173.000000
            sum    29030.000000  24308.000000  20660.000000
            mean%      4.221931      3.535195      3.004654
        """

        pcrnt_limit = 4.5 #mean%%(!)

        res_totals = self._check_gear_diffs(gened_fname_glob)
        print(res_totals)

        diff_prcnt = res_totals.loc['mean%', ['diff_gears', 'diff_accel']]
        np.testing.assert_array_less(np.abs(diff_prcnt.fillna(0)), pcrnt_limit)

    def test2b_gear_diffs_transplanted(self):
        """Check driveability-only diff-gears with Heinz stays within some percent.

        ### Comparison history ###

        Force class3b, Phase-1b-beta(ver <= 0.0.8, Aug-2014) with Heinz maxt gear-time=2sec::

                    diff_gears   diff_accel  diff_orig
            count   378.000000   378.000000        378
            mean     15.566138     5.634921          0
            std      16.554295     8.136700          0
            min       0.000000     0.000000          0
            25%       5.000000     1.000000          0
            50%      11.000000     3.000000          0
            75%      19.750000     7.000000          0
            max     123.000000    78.000000          0
            sum    5884.000000  2130.000000          0
            mean%     0.864785     0.313051          0

        Not forcing class3b, honoring declared v_max & unladen_mass::

                    diff_gears   diff_accel  diff_orig
            count   382.000000   382.000000        382
            mean     12.599476     4.651832          0
            std      15.375930     7.566103          0
            min       0.000000     0.000000          0
            25%       4.000000     0.000000          0
            50%       9.000000     2.000000          0
            75%      15.000000     6.000000          0
            max     123.000000    78.000000          0
            sum    4813.000000  1777.000000          0
            mean%     0.699971     0.258435          0
        """

        pcrnt_limit = 0.75 # mean%(!)

        res_totals = self._check_gear_diffs(trans_fname_glob)
        print(res_totals)

        diff_prcnt = res_totals.loc['mean%', ['diff_gears', 'diff_accel']]
        np.testing.assert_array_less(np.abs(diff_prcnt.fillna(0)), pcrnt_limit)



    def _check_n_mean(self, fname_glob):
        res = vehicles_applicator(fname_glob, lambda _, df_g, df_h:
                                          (df_g['rpm'].mean(), df_h['n'].mean()))
        res.columns = ['python', 'heinz']

        res_totals = res.describe()
        res_totals['diff_prcnt'] = 100 * (res_totals.heinz - res_totals.python) / res_totals.min(axis=1)

        return res_totals

    def test3a_n_mean(self):
        """Check mean-rpm diff with Heinz stays within some percent.

        ### Comparison history ###

        Class3b-Vehicles, Phase-1b-beta(ver <= 0.0.8, Aug-2014) with Heinz maxt gear-time=2sec::

                               mean         std          min          max
            python      1766.707825  410.762478  1135.458463  3217.428423
            heinz       1759.851498  397.343498  1185.905053  3171.826208
            diff_prcnt    -0.3896     -3.3772       4.4428      -1.4377

        Separated test/unladen masses::

                        python        heinz  diff_prcnt
            count   378.000000   378.000000    0.000000
            mean   1923.908119  1899.366431   -1.292099
            std     628.998854   593.126296   -6.048047
            min    1135.458463  1185.905053    4.442839
            25%    1497.544940  1495.699889   -0.123357
            50%    1740.927971  1752.668517    0.674384
            75%    2121.459309  2111.876041   -0.453780
            max    4965.206982  4897.154914   -1.389625

        Not forcing class3b, honoring declared v_max & unladen_mass::

                        python        heinz  diff_prcnt
            count   382.000000   382.000000    0.000000
            mean   1835.393402  1827.572965   -0.427914
            std     476.687485   464.264779   -2.675781
            min    1135.458463  1185.905053    4.442839
            25%    1486.886555  1482.789006   -0.276341
            50%    1731.983662  1739.781233    0.450210
            75%    2024.534101  2018.716963   -0.288160
            max    3741.849187  3750.927263    0.242609
        
        Keeping idle engine revs::
        
                        python        heinz  diff_prcnt
            count   382.000000   382.000000    0.000000
            mean   1852.183403  1827.572965   -1.346619
            std     473.142045   464.264779   -1.912113
            min    1168.757027  1185.905053    1.467202
            25%    1507.030779  1482.789006   -1.634877
            50%    1749.246014  1739.781233   -0.544021
            75%    2043.861777  2018.716963   -1.245584
            max    3747.026551  3750.927263    0.104102
        """

        pcrnt_limit = 1.5

        res_totals = self._check_n_mean(gened_fname_glob)
        print(res_totals)

        diff_prcnt = res_totals.loc['mean', 'diff_prcnt']
        self.assertLess(np.abs(diff_prcnt), pcrnt_limit)


    def test3b_n_mean_transplanted(self):
        """Check driveability-only mean-rpm diff with Heinz stays within some percent.

        ### Comparison history ###

        Force class3b, Phase-1b-beta(ver <= 0.0.8, Aug-2014) with Heinz maxt gear-time=2sec::

                        python        heinz  diff_prcnt
            count   378.000000   378.000000    0.000000
            mean   1880.045112  1899.366431    1.027705
            std     572.842493   593.126296    3.540904
            min    1150.940393  1185.905053    3.037921
            25%    1477.913404  1495.699889    1.203486
            50%    1739.882957  1752.668517    0.734852
            75%    2073.715015  2111.876041    1.840225
            max    4647.136063  4897.154914    5.380063

        Not forcing class3b, honoring declared v_max & unladen_mass::

                        python        heinz  diff_prcnt
            count   382.000000   382.000000    0.000000
            mean   1818.519842  1827.572965    0.497829
            std     469.276397   464.264779   -1.079474
            min    1150.940393  1185.905053    3.037921
            25%    1467.153958  1482.789006    1.065672
            50%    1730.051632  1739.781233    0.562388
            75%    2010.264758  2018.716963    0.420452
            max    3704.999890  3750.927263    1.239605
        """

        pcrnt_limit = 0.55

        res_totals = self._check_n_mean(trans_fname_glob)
        print(res_totals)

        diff_prcnt = res_totals.loc['mean', 'diff_prcnt']
        self.assertLess(np.abs(diff_prcnt), pcrnt_limit)



    def _check_n_mean__pmr(self, fname_glob):
        vehdata = _read_vehicles_inp()
        vehdata['pmr'] = 1000.0 * vehdata['rated_power'] / vehdata['kerb_mass']
        np.testing.assert_allclose(vehdata.pmr_km, vehdata.pmr)

        res = vehicles_applicator(fname_glob, lambda _, df_g, df_h:
                                          (df_g['rpm'].mean(), df_h['n'].mean()))

        res.columns=['gened_mean_rpm', 'heinz_mean_rpm']
        vehdata = vehdata.merge(res, how='inner', left_index=True, right_index=True).sort()
        self.assertEqual(vehdata.shape[0], res.shape[0])

        df = vehdata.sort('pmr')[['gened_mean_rpm', 'heinz_mean_rpm']]
        dfg = df.groupby(pd.cut(vehdata.pmr, 12), )
        pmr_histogram = dfg.mean()

        dif = (pmr_histogram['heinz_mean_rpm'] - pmr_histogram['gened_mean_rpm']) / pmr_histogram.min(axis=1)
        pmr_histogram['diff_prcnt']= 100 * dif
        pmr_histogram['count']= dfg.count().iloc[:, -1]

        return pmr_histogram

    @skipIf(utils.is_travis(), 'GroupBy probably fails in old pandas, and cannot upgrade it.')
    def test4a_n_mean__PMR(self):
        """Check mean-rpm diff with Heinz stays within some percent for all PMRs.

        ### Comparison history ###


        Force class3b, Phase-1b-beta(ver <= 0.0.8, Aug-2014) with Heinz maxt gear-time=2sec::

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

        Separated test/unladen masses::

                                 gened_mean_rpm  heinz_mean_rpm  diff_prcnt  count
            pmr
            (11.504, 26.225]        1579.612698     1585.721306    0.386716     28
            (26.225, 40.771]        1706.865069     1700.689983   -0.363093     41
            (40.771, 55.317]        1866.150857     1841.779091   -1.323273    119
            (55.317, 69.863]        2122.662626     2085.262950   -1.793523    122
            (69.863, 84.409]        2228.282795     2171.952804   -2.593518     29
            (84.409, 98.955]        1783.316413     1787.378401    0.227777      4
            (98.955, 113.501]       1718.157828     1718.516147    0.020855     31
            (113.501, 128.0475]     2005.415058     1954.763742   -2.591173      2
            (128.0475, 142.594]     1566.601860     1553.383676   -0.850928      1
            (142.594, 157.14]               NaN             NaN         NaN      0
            (157.14, 171.686]               NaN             NaN         NaN      0
            (171.686, 186.232]      1396.061758     1385.176569   -0.785834      1

        Not forcing class3b, honoring declared v_max & unladen_mass::

                                gened_mean_rpm  heinz_mean_rpm  diff_prcnt  count
            pmr
            (9.973, 24.823]        1560.010258     1563.836656    0.245280     33
            (24.823, 39.496]       1725.209986     1725.004638   -0.011904     34
            (39.496, 54.17]        1737.811065     1730.770088   -0.406812    123
            (54.17, 68.843]        1996.999520     1983.753219   -0.667739     94
            (68.843, 83.517]       2051.088434     2034.594136   -0.810692     59
            (83.517, 98.191]       1964.832555     1958.081066   -0.344801      4
            (98.191, 112.864]      1682.122484     1684.443875    0.138004     31
            (112.864, 127.538]     2718.877009     2687.055802   -1.184241      2
            (127.538, 142.211]     1660.925042     1668.155469    0.435325      1
            (142.211, 156.885]             NaN             NaN         NaN      0
            (156.885, 171.558]             NaN             NaN         NaN      0
            (171.558, 186.232]     1396.061758     1385.176569   -0.785834      1
            Mean: 0.419219429398

        pandas 0.15.1::

                                gened_mean_rpm  heinz_mean_rpm  diff_prcnt  count
            pmr                                                                  
            (9.973, 24.823]        2037.027221     2038.842442    0.089111     33
            (24.823, 39.496]       2257.302959     2229.999526   -1.224369     34
            (39.496, 54.17]        1912.075914     1885.792807   -1.393743    123
            (54.17, 68.843]        1716.720028     1717.808457    0.063402     94
            (68.843, 83.517]       1677.882399     1683.916224    0.359610     59
            (83.517, 98.191]       1535.881170     1551.609661    1.024070      4
            (98.191, 112.864]      1571.290286     1589.997331    1.190553     31
            (112.864, 127.538]     1409.308426     1425.965019    1.181898      2
            (127.538, 142.211]     1975.481368     1967.808440   -0.389923      1
            (142.211, 156.885]             NaN             NaN         NaN      0
            (156.885, 171.558]             NaN             NaN         NaN      0
            (171.558, 186.232]     1950.377512     1937.426430   -0.668468      1
            Mean diff_prcnt: 0.632095580562
                                gened_mean_rpm  heinz_mean_rpm  diff_prcnt  count

        Keeping idle engine revs::
            pmr                                                                  
            (9.973, 24.823]        2058.624153     2038.842442   -0.970242     33
            (24.823, 39.496]       2271.419763     2229.999526   -1.857410     34
            (39.496, 54.17]        1927.898841     1885.792807   -2.232803    123
            (54.17, 68.843]        1733.545963     1717.808457   -0.916139     94
            (68.843, 83.517]       1694.461857     1683.916224   -0.626256     59
            (83.517, 98.191]       1553.854990     1551.609661   -0.144710      4
            (98.191, 112.864]      1590.081566     1589.997331   -0.005298     31
            (112.864, 127.538]     1427.367629     1425.965019   -0.098362      2
            (127.538, 142.211]     1989.461646     1967.808440   -1.100372      1
            (142.211, 156.885]             NaN             NaN         NaN      0
            (156.885, 171.558]             NaN             NaN         NaN      0
            (171.558, 186.232]     1960.918157     1937.426430   -1.212522      1
            Mean diff_prcnt: 0.76367613389
        """

        pcrnt_limit = 0.8

        pmr_histogram = self._check_n_mean__pmr(gened_fname_glob)

        print (pmr_histogram)

        diff_prcnt = pmr_histogram['diff_prcnt'].fillna(0).abs().mean()
        print ('Mean diff_prcnt: %s'%diff_prcnt)
        self.assertLess(diff_prcnt, pcrnt_limit)

    
    @skipIf(utils.is_travis(), 'GroupBy probably fails in old pandas, and cannot upgrade it.')
    def test4b_n_mean__PMR_transplanted(self):
        """Check driveability-only mean-rpm diff with Heinz stays within some percent for all PMRs.

        ### Comparison history ###

        Force class3b, Phase-1b-beta(ver <= 0.0.8, Aug-2014) with Heinz maxt gear-time=2sec::

                                gened_mean_rpm  heinz_mean_rpm  diff_prcnt  count
            pmr
            (9.973, 24.823]        1557.225037     1568.360963    0.715113     32
            (24.823, 39.496]       1686.859826     1696.482640    0.570457     34
            (39.496, 54.17]        1771.670097     1789.409819    1.001299    120
            (54.17, 68.843]        2133.400050     2165.214662    1.491263     94
            (68.843, 83.517]       2020.903728     2043.741660    1.130085     59
            (83.517, 98.191]       1886.836446     1890.040533    0.169813      4
            (98.191, 112.864]      1788.434592     1792.693611    0.238142     31
            (112.864, 127.538]     2580.884314     2568.011660   -0.501269      2
            (127.538, 142.211]     1581.625191     1597.571904    1.008249      1
            (142.211, 156.885]             NaN             NaN         NaN      0
            (156.885, 171.558]             NaN             NaN         NaN      0
            (171.558, 186.232]     1367.068837     1385.176569    1.324566      1

        Separated test/unladen masses::

                                 gened_mean_rpm  heinz_mean_rpm  diff_prcnt  count
            pmr
            (11.504, 26.225]        1572.733597     1585.721306    0.825805     28
            (26.225, 40.771]        1690.081663     1700.689983    0.627681     41
            (40.771, 55.317]        1821.319706     1841.779091    1.123327    119
            (55.317, 69.863]        2060.507029     2085.262950    1.201448    122
            (69.863, 84.409]        2142.964427     2171.952804    1.352723     29
            (84.409, 98.955]        1783.214173     1787.378401    0.233524      4
            (98.955, 113.501]       1713.473617     1718.516147    0.294287     31
            (113.501, 128.0475]     1950.373771     1954.763742    0.225084      2
            (128.0475, 142.594]     1543.937285     1553.383676    0.611838      1
            (142.594, 157.14]               NaN             NaN         NaN      0
            (157.14, 171.686]               NaN             NaN         NaN      0
            (171.686, 186.232]      1367.068837     1385.176569    1.324566      1

        Not forcing class3b, honoring declared v_max & unladen_mass::

                                gened_mean_rpm  heinz_mean_rpm  diff_prcnt  count
            pmr
            (9.973, 24.823]        1551.901645     1563.836656    0.769057     33
            (24.823, 39.496]       1713.382835     1725.004638    0.678296     34
            (39.496, 54.17]        1722.174466     1730.770088    0.499114    123
            (54.17, 68.843]        1974.768859     1983.753219    0.454958     94
            (68.843, 83.517]       2026.630271     2034.594136    0.392961     59
            (83.517, 98.191]       1954.817179     1958.081066    0.166966      4
            (98.191, 112.864]      1676.678357     1684.443875    0.463149     31
            (112.864, 127.538]     2678.973439     2687.055802    0.301696      2
            (127.538, 142.211]     1658.577318     1668.155469    0.577492      1
            (142.211, 156.885]             NaN             NaN         NaN      0
            (156.885, 171.558]             NaN             NaN         NaN      0
            (171.558, 186.232]     1367.068837     1385.176569    1.324566      1
            Mean diff_prcnt: 0.469021296461
            
        pandas 0.15.1::
        
                                gened_mean_rpm  heinz_mean_rpm  diff_prcnt  count
            pmr                                                                  
            (9.973, 24.823]        2021.882193     2038.842442    0.838835     33
            (24.823, 39.496]       2204.136804     2229.999526    1.173372     34
            (39.496, 54.17]        1880.733341     1885.792807    0.269016    123
            (54.17, 68.843]        1710.819917     1717.808457    0.408491     94
            (68.843, 83.517]       1677.846860     1683.916224    0.361735     59
            (83.517, 98.191]       1541.587174     1551.609661    0.650141      4
            (98.191, 112.864]      1579.049392     1589.997331    0.693325     31
            (112.864, 127.538]     1411.921405     1425.965019    0.994646      2
            (127.538, 142.211]     1976.193317     1967.808440   -0.426102      1
            (142.211, 156.885]             NaN             NaN         NaN      0
            (156.885, 171.558]             NaN             NaN         NaN      0
            (171.558, 186.232]     1954.662077     1937.426430   -0.889616      1
            Mean diff_prcnt: 0.558773102894
        """

        pcrnt_limit = 0.6

        pmr_histogram = self._check_n_mean__pmr(trans_fname_glob)

        print (pmr_histogram)

        diff_prcnt = pmr_histogram['diff_prcnt'].fillna(0).abs().mean()
        print ('Mean diff_prcnt: %s'%diff_prcnt)
        self.assertLess(diff_prcnt, pcrnt_limit)



    def _check_n_mean__gear(self, fname_glob):
        def avg_by_column(group_column, aggregate_column, df):
            sr = df.groupby(group_column)[aggregate_column].describe()

            ## Ensure 6-gears for all vehicles
            #
            index = [range(7), ['mean', 'std', 'min', 'max']]
            index = pd.MultiIndex.from_product(index, names=['gear', 'aggregate'])
            sr = sr.reindex(index)

            return sr

        vehdata = OrderedDict()

        for (veh_num, df_g, df_h) in _file_pairs(fname_glob):
            df = pd.concat((avg_by_column('gears', 'rpm', df_g), avg_by_column('gear', 'n', df_h)), axis=1)
            df.columns = ['python', 'heinz']
            df['diff%'] = 100 * (df.python - df.heinz) / df.iloc[:, :2].abs().min(axis=1)

            vehdata[veh_num] = df

        vehdata = pd.Panel(vehdata).to_frame(filter_observations=False)

        diff_prcnt_by_gears = vehdata.xs('mean', level=1).mean(axis=1)
        diff_prcnt_by_gears = pd.DataFrame(diff_prcnt_by_gears).unstack()
        diff_prcnt_by_gears.name = 'diff_prcnt_by_gears'

        diff_prcnt_by_gears = diff_prcnt_by_gears[0]
        diff_prcnt_by_gears.columns.name = 'n_mean'

        return diff_prcnt_by_gears

    def test5a_n_mean__gear(self):
        """Check mean-rpm diff% with Heinz stays within some percent for all gears.

        ### Comparison history ###


        Force class3b, Phase-1b-beta(ver <= 0.0.8, Aug-2014) with Heinz maxt gear-time=2sec::

            n_mean      python        heinz      diff%
            gear
            0       732.358286   804.656085  -9.925769
            1       870.080494  1177.547512 -44.450903
            2      1789.787609  1650.383967   6.520319
            3      1921.271483  1761.172027   7.804359
            4      1990.286402  1886.563262   5.401895
            5      2138.445024  2112.552162   1.892950
            6      2030.970322  1987.865039   2.228276

        Not forcing class3b, honoring declared v_max & unladen_mass::

            gear
            0        735.143823   808.795812 -10.052865
            1        799.834530  1139.979330 -47.027383
            2       1598.773915  1582.431975   1.119054
            3       1793.617644  1691.589756   5.768020
            4       1883.863510  1796.957457   5.024360
            5       2095.211754  2052.059948   2.430360
            6       2033.663975  1990.344346   2.238421
        """
        pcrnt_limit = 48

        histogram = self._check_n_mean__gear(gened_fname_glob)

        print (histogram)

        diff_prcnt = histogram['diff%']
        np.testing.assert_array_less(np.abs(diff_prcnt.fillna(0)), pcrnt_limit)

    def test5b_n_mean__gear_transplanted(self):
        """Check mean-rpm diff% with Heinz stays within some percent for all gears.

        ### Comparison history ###


        Force class3b, Phase-1b-beta(ver <= 0.0.8, Aug-2014) with Heinz maxt gear-time=2sec::

            n_mean      python        heinz      diff%
            gear
            0       732.357001   804.656085  -9.926855
            1       966.022039  1177.547512 -24.409425
            2      1678.578373  1650.383967   1.616768
            3      1791.644768  1761.172027   1.700642
            4      1883.504933  1886.563262   0.119165
            5      2099.218160  2112.552162  -0.320293
            6      1985.732086  1987.865039  -0.096754

        Not forcing class3b, honoring declared v_max & unladen_mass::

            n_mean       python        heinz      diff%
            gear
            0        735.077116   808.795812 -10.065886
            1        932.586982  1139.979330 -24.285307
            2       1606.040896  1582.431975   1.379144
            3       1721.141364  1691.589756   1.686708
            4       1803.212699  1796.957457   0.370703
            5       2053.822313  2052.059948   0.142138
            6       1988.195381  1990.344346  -0.097482
        """
        pcrnt_limit = 25

        histogram = self._check_n_mean__gear(trans_fname_glob)

        print (histogram)

        diff_prcnt = histogram['diff%']
        np.testing.assert_array_less(np.abs(diff_prcnt.fillna(0)), pcrnt_limit)




###################
# RUN EXPERIMENTS #
###################



def _run_the_experiments(transplant_original_gears=False, plot_results=False, compare_results=False, encoding="UTF-8"):
    
    ## If file existent, it contains also calculated fields 
    #    from the previous experiment run.
    # 
    out_df = _read_vehicles_out()
    
    inp_df = _read_vehicles_inp()
    ## Reconstruct the columns only presetn in the out_df.
    #
    inp_df['pmr'] = np.NAN
    inp_df['wltc_class'] = ''
    inp_df['f_downscale'] = np.NAN
    
    
    wots = _read_wots()

    failed_vehicles = 0
    for (ix, row) in inp_df.iterrows():
        veh_num = ix
        heinz_fname = _make_heinz_fname(veh_num)
        outfname = _make_gened_fname(transplant_original_gears, veh_num)

        if not out_df is None and _is_file_up_to_date(outfname, [heinz_fname]):
            inp_df.loc[ix] = out_df.loc[ix]
            continue

        model = goodVehicle()
        veh = model['vehicle']

        veh['test_mass'] = row['test_mass']
        veh['unladen_mass'] = row['kerb_mass']
        veh['resistance_coeffs'] = list(row['f0_real':'f2_real'])
        veh['p_rated'] = row['rated_power']
        veh['n_rated'] = row['rated_speed']
        veh['n_idle'] = int(row['idling_speed'])
        veh['v_max'] = row['v_max']
        ngears = int(row['no_of_gears'])
        veh['gear_ratios'] = list(row['ndv_1':'ndv_%s'%ngears]) #'ndv_1'
        veh['full_load_curve'] = _select_wot(wots, row['IDcat'] == 2)

        if (transplant_original_gears):
            log.warning(">>> Transplanting gears from Heinz's!")
            df_h = _read_heinz_file(veh_num)

            model['cycle_run'] = {'gears_orig': df_h['g_max'].values}

        try:
            experiment = Experiment(model)
            model = experiment.run()
        except Exception as ex:
            log.warning('VEHICLE_FAILED(%s): %s', veh_num, str(ex))
            failed_vehicles += 1
            continue
        else:
            params  = model['params']
            veh     = model['vehicle']

            inp_df.loc[ix, 'pmr'] = veh['pmr']
            inp_df.loc[ix, 'wltc_class'] = veh['wltc_class']
            inp_df.loc[ix, 'f_downscale'] = params['f_downscale']
            
            # ankostis_mdb:  't', "v in km/h","v_orig","a in m/s²","gear","g_min","g_max","gear_modification","error_description"
            # heinz:         't', 'km_h', 'stg', 'gear'
            cycle_df = pd.DataFrame(model['cycle_run'])

            _compare_exp_results(cycle_df, outfname, compare_results)
            
            cycle_df.to_csv(outfname, index_label='time')
    fail_limit_prcnt = 0.1
    assert failed_vehicles < fail_limit_prcnt * inp_df.shape[0], \
            'TOO MANY(>%f) vehicles have Failed(%i out of %i)!'% (fail_limit_prcnt, failed_vehicles, inp_df.shape[0])

    if not transplant_original_gears:
        _write_vehicle_data(inp_df)
        
    return inp_df

#     vehfpath = os.path.join(samples_dir, 'heinz_Petrol_veh{:05}.dri'.format(veh_num))
#     inpfname = glob.glob(vehfpath)[0]
#     out_df = pd.read_csv(inpfname, encoding='latin-1')


###################
# COMPARE RESULTS #
###################

def _compare_exp_results(tabular, outfname, run_comparison):
    if (run_comparison):
        try:
            data_prev = _read_gened_file(outfname)
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
        except FileNotFoundError:
            print('>> COMPARING(%s): No old-tabular found, 1st time to run' % outfname)
            run_comparison = False



## TODO: Move into wltp/plots
#
def _plotResults(veh_fname, df_g, df_h,  res, ax, plot_diffs_gears_only=True, plot_original_gears = False):
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

    ax.text(0.7, 0, 'Diffs: %.4f' % res, transform=ax.transAxes, bbox={'facecolor':'red', 'alpha':0.5, 'pad':10})



def plot_diffs_with_heinz(diff_results, res, transplant_original_gears=False):
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
    fig.suptitle('%s: ±DIFFs: count(%i), min(%i), MEAN(%.2f±%.2f), max(%i).' % (orig, res[0].sum(), res[0].min(), res[0].mean(), res[0].std(), res[0].max()))

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
    unittest.main()

