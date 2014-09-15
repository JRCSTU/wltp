#!/usr/bin/env python
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

from __future__ import print_function, unicode_literals

from collections import OrderedDict
import glob
import logging
import math
import os
import re
import unittest
from unittest.case import skip
from wltp.experiment import Experiment
from wltp.test.goodvehicle import goodVehicle

import numpy as np
import numpy.testing as npt
import pandas as pd

overwrite_old_results = True # NOTE: Set 'False' to UPDATE sample-results or run main() (assuming they are ok).

mydir = os.path.dirname(__file__)
force_rerun = False
samples_dir = 'wltp_db'
vehs_data_inp_fname = 'wltp_db_vehicles.csv'
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



def _read_vehicle_data():
    df = pd.read_csv(vehs_data_inp_fname, encoding = encoding, index_col = 0)

    return df

def _read_wots():
    df = pd.read_csv('wot_samples.csv', encoding = encoding, index_col = None)

    return df

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


## From http://code.activestate.com/recipes/578231-probably-the-fastest-memoization-decorator-in-the-/
#
def memoize(f):
    """ Memoization decorator for functions taking one or more arguments. """
    class memodict(dict):
        def __init__(self, f):
            self.f = f
        def __call__(self, *args):
            return self[args]
        def __missing__(self, key):
            ret = self[key] = self.f(*key)
            return ret
    return memodict(f)

@memoize
def _read_gened_file(inpfname):
    df = pd.read_csv(inpfname, header=0, index_col=0)
    assert not df.empty
    assert df.index.name == 'time', \
            df.index.name

    return df

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

    return df


def _is_file_up_to_date(result_file, other_dependency_files = None):

    if force_rerun or not os.path.exists(result_file):
        return False

    checkfiles = [__file__, '../../model.py', '../../experiment.py', vehs_data_inp_fname]
    if other_dependency_files:
        checkfiles = checkfiles + list(other_dependency_files)
    latest_dep_date = max([os.path.getmtime(file) for file in checkfiles])

    result_date = os.path.getmtime(result_file)

    return result_date > latest_dep_date

def _file_pairs(fname_glob):
    """
    Generates pairs of files to compare, skipping non-existent and those with mismatching #_of_rows.

    Example:

    >>> for (veh_num, df_g, df_h) in _file_pairs('wltp_db_vehicles-00*.csv')
            pass
    """

    all_gened = glob.glob(fname_glob)
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

def _vehicles_applicator(fname_glob, pair_func):
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

        All-Vehicles, Phase-1b-beta(ver <= 0.0.8, Aug-2014) with Heinz maxt gear-time=2sec::

                       python       heinz    diff_prcnt
            count  378.000000  378.000000  0.000000e+00
            mean    45.973545   46.189082  4.688300e-01
            std      1.642335    1.126555 -4.578377e+01
            min     35.866421   36.659117  2.210133e+00
            25%     46.506718   46.504909 -3.892020e-03
            50%     46.506718   46.506504 -4.620879e-04
            75%     46.506718   46.506719  4.116024e-08
            max     46.506718   46.506719  4.116024e-08
        """

        pcrnt_limit = 0.5

        res = _vehicles_applicator(gened_fname_glob, lambda _, df_g, df_h:
                                          (df_g['v_target'].mean(), df_h['v'].mean()))
        res.columns = ['python', 'heinz']

        df = res.describe()

        df['diff_prcnt'] = 100 * (df.heinz - df.python) / df.min(axis=1)
        print(df)

        diff_prcnt = df.loc['mean', 'diff_prcnt']
        self.assertLess(abs(diff_prcnt), pcrnt_limit)


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

        res = _vehicles_applicator(fname_glob, read_and_compare_experiment)
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

        All-Vehicles, Phase-1b-beta(ver <= 0.0.8, Aug-2014) with Heinz maxt gear-time=2sec::

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
        """

        pcrnt_limit = 6

        res_totals = self._check_gear_diffs(gened_fname_glob)
        print(res_totals)

        diff_prcnt = res_totals.loc['mean%', ['diff_gears', 'diff_accel']]
        np.testing.assert_array_less(abs(diff_prcnt.fillna(0)), pcrnt_limit)

    def test2b_gear_diffs_transplanted(self):
        """Check driveability-only diff-gears with Heinz stays within some percent.

        ### Comparison history ###

        All-Vehicles, Phase-1b-beta(ver <= 0.0.8, Aug-2014) with Heinz maxt gear-time=2sec::

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

        """

        pcrnt_limit = 0.9 # mean

        res_totals = self._check_gear_diffs(trans_fname_glob)
        print(res_totals)

        diff_prcnt = res_totals.loc['mean%', ['diff_gears', 'diff_accel']]
        np.testing.assert_array_less(abs(diff_prcnt.fillna(0)), pcrnt_limit)



    def _check_n_mean(self, fname_glob):
        res = _vehicles_applicator(fname_glob, lambda _, df_g, df_h:
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

        All-Vehicles, Phase-1b-beta(ver <= 0.0.8, Aug-2014) with Heinz maxt gear-time=2sec::

                        python        heinz  diff_prcnt
            count   378.000000   378.000000    0.000000
            mean   1923.908119  1899.366431   -1.292099
            std     628.998854   593.126296   -6.048047
            min    1135.458463  1185.905053    4.442839
            25%    1497.544940  1495.699889   -0.123357
            50%    1740.927971  1752.668517    0.674384
            75%    2121.459309  2111.876041   -0.453780
            max    4965.206982  4897.154914   -1.389625
        """

        pcrnt_limit = 1.3

        res_totals = self._check_n_mean(gened_fname_glob)
        print(res_totals)

        diff_prcnt = res_totals.loc['mean', 'diff_prcnt']
        self.assertLess(abs(diff_prcnt), pcrnt_limit)


    def test3b_n_mean_transplanted(self):
        """Check driveability-only mean-rpm diff with Heinz stays within some percent.

        ### Comparison history ###

        All-Vehicles, Phase-1b-beta(ver <= 0.0.8, Aug-2014) with Heinz maxt gear-time=2sec::

                        python        heinz  diff_prcnt
            count   378.000000   378.000000    0.000000
            mean   1880.045112  1899.366431    1.027705
            std     572.842493   593.126296    3.540904
            min    1150.940393  1185.905053    3.037921
            25%    1477.913404  1495.699889    1.203486
            50%    1739.882957  1752.668517    0.734852
            75%    2073.715015  2111.876041    1.840225
            max    4647.136063  4897.154914    5.380063
        """

        pcrnt_limit = 1.1

        res_totals = self._check_n_mean(trans_fname_glob)
        print(res_totals)

        diff_prcnt = res_totals.loc['mean', 'diff_prcnt']
        self.assertLess(abs(diff_prcnt), pcrnt_limit)



    def _check_n_mean__pmr(self, fname_glob):
        vehdata = _read_vehicle_data()
        vehdata['pmr'] = 1000.0 * vehdata['rated_power'] / vehdata['kerb_mass']
        np.testing.assert_allclose(vehdata.pmr_km, vehdata.pmr)

        res = _vehicles_applicator(fname_glob, lambda _, df_g, df_h:
                                          (df_g['rpm'].mean(), df_h['n'].mean()))

        res.columns=['gened_mean_rpm', 'heinz_mean_rpm']
        vehdata = vehdata.merge(res, left_index=True, right_index=True)

        df = vehdata.sort('pmr')[['gened_mean_rpm', 'heinz_mean_rpm']]
        dfg = df.groupby(pd.cut(vehdata.pmr, 12))
        pmr_histogram = dfg.mean()

        dif = (pmr_histogram['heinz_mean_rpm'] - pmr_histogram['gened_mean_rpm']) / pmr_histogram.min(axis=1)
        pmr_histogram['diff_prcnt']= 100 * dif
        pmr_histogram['count']= dfg.count().iloc[:, -1]

        return pmr_histogram

    def test4a_n_mean__PMR(self):
        """Check mean-rpm diff with Heinz stays within some percent for all PMRs.

        ### Comparison history ###


        Class3b-Vehicles, Phase-1b-beta(ver <= 0.0.8, Aug-2014) with Heinz maxt gear-time=2sec::

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

        All-Vehicles, Phase-1b-beta(ver <= 0.0.8, Aug-2014) with Heinz maxt gear-time=2sec::

                                gened_mean_rpm  heinz_mean_rpm  diff_prcnt  count
            pmr
            (9.973, 24.823]        1566.018469     1568.360963    0.149583     32
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

        As above, fixed pandas::

                                 gened_mean_rpm  heinz_mean_rpm  diff_prcnt  count
            pmr
            (11.504, 26.225]        1566.843621     1571.669836    0.308022     56
            (26.225, 40.771]        1689.224356     1687.071424   -0.127614     82
            (40.771, 55.317]        1879.343294     1854.883664   -1.318661    238
            (55.317, 69.863]        2079.120632     2043.072100   -1.764428    244
            (69.863, 84.409]        2309.696901     2246.212296   -2.826296     58
            (84.409, 98.955]        1840.239774     1833.223209   -0.382745      8
            (98.955, 113.501]       1783.820891     1783.428552   -0.021999     62
            (113.501, 128.0475]     2127.523565     2072.590505   -2.650454      4
            (128.0475, 142.594]     1521.154026     1508.182676   -0.860065      2
            (142.594, 157.14]               NaN             NaN         NaN      0
            (157.14, 171.686]               NaN             NaN         NaN      0
            (171.686, 186.232]      1396.061758     1385.176569   -0.785834      2

        """

        pcrnt_limit = 3

        pmr_histogram = self._check_n_mean__pmr(gened_fname_glob)

        print (pmr_histogram)

        diff_prcnt = pmr_histogram['diff_prcnt']
        np.testing.assert_array_less(abs(diff_prcnt.fillna(0)), pcrnt_limit)

    def test4b_n_mean__PMR_transplanted(self):
        """Check driveability-only mean-rpm diff with Heinz stays within some percent for all PMRs.

        ### Comparison history ###

        All-Vehicles, Phase-1b-beta(ver <= 0.0.8, Aug-2014) with Heinz maxt gear-time=2sec::

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

        As above, fixed pandas::

                                 gened_mean_rpm  heinz_mean_rpm  diff_prcnt  count
            pmr
            (11.504, 26.225]        1560.143330     1571.669836    0.738811     56
            (26.225, 40.771]        1676.764115     1687.071424    0.614714     82
            (40.771, 55.317]        1834.250772     1854.883664    1.124868    238
            (55.317, 69.863]        2018.870936     2043.072100    1.198747    244
            (69.863, 84.409]        2211.686221     2246.212296    1.561075     58
            (84.409, 98.955]        1834.280282     1833.223209   -0.057662      8
            (98.955, 113.501]       1779.441691     1783.428552    0.224051     62
            (113.501, 128.0475]     2069.698245     2072.590505    0.139743      4
            (128.0475, 142.594]     1502.435092     1508.182676    0.382551      2
            (142.594, 157.14]               NaN             NaN         NaN      0
            (157.14, 171.686]               NaN             NaN         NaN      0
            (171.686, 186.232]      1367.068837     1385.176569    1.324566      2

        """

        pcrnt_limit = 1.7

        pmr_histogram = self._check_n_mean__pmr(trans_fname_glob)

        print (pmr_histogram)

        diff_prcnt = pmr_histogram['diff_prcnt']
        np.testing.assert_array_less(abs(diff_prcnt.fillna(0)), pcrnt_limit)


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


        All-Vehicles, Phase-1b-beta(ver <= 0.0.8, Aug-2014) with Heinz maxt gear-time=2sec::

            n_mean      python        heinz      diff%
            gear
            0       732.358286   804.656085  -9.925769
            1       870.080494  1177.547512 -44.450903
            2      1789.787609  1650.383967   6.520319
            3      1921.271483  1761.172027   7.804359
            4      1990.286402  1886.563262   5.401895
            5      2138.445024  2112.552162   1.892950
            6      2030.970322  1987.865039   2.228276


        """
        pcrnt_limit = 45

        histogram = self._check_n_mean__gear(gened_fname_glob)

        print (histogram)

        diff_prcnt = histogram['diff%']
        np.testing.assert_array_less(abs(diff_prcnt.fillna(0)), pcrnt_limit)

    def test5b_n_mean__gear_transplanted(self):
        """Check mean-rpm diff% with Heinz stays within some percent for all gears.

        ### Comparison history ###


        All-Vehicles, Phase-1b-beta(ver <= 0.0.8, Aug-2014) with Heinz maxt gear-time=2sec::

            n_mean      python        heinz      diff%
            gear
            0       732.357001   804.656085  -9.926855
            1       966.022039  1177.547512 -24.409425
            2      1678.578373  1650.383967   1.616768
            3      1791.644768  1761.172027   1.700642
            4      1883.504933  1886.563262   0.119165
            5      2099.218160  2112.552162  -0.320293
            6      1985.732086  1987.865039  -0.096754
        """
        pcrnt_limit = 25

        histogram = self._check_n_mean__gear(trans_fname_glob)

        print (histogram)

        diff_prcnt = histogram['diff%']
        np.testing.assert_array_less(abs(diff_prcnt.fillna(0)), pcrnt_limit)






def _run_the_experiments(transplant_original_gears=False, plot_results=False, compare_results=False, encoding="UTF-8"):
    # rated_power,kerb_mass,rated_speed,idling_speed,test_mass,no_of_gears,ndv_1,ndv_2,ndv_3,ndv_4,ndv_5,ndv_6,ndv_7,ID_cat,user_def_driv_res_coeff,user_def_power_curve,f0,f1,f2,Comment
    # 0                                                            5                                10                                                    15                        19
    df = _read_vehicle_data()
    wots = _read_wots()

    failed_vehicles = 0
    for (ix, row) in df.iterrows():
        veh_num = ix
        heinz_fname = _make_heinz_fname(veh_num)
        outfname = _make_gened_fname(transplant_original_gears, veh_num)

        if _is_file_up_to_date(outfname, [heinz_fname]):
            continue

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
        veh['full_load_curve'] = _select_wot(wots, row['IDcat'] == 2)

        ## Override always class-3.
        model['params'] = {'wltc_class': 'class3b'}

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
            params = model['params']

            f_downscale = params['f_downscale']
            if (f_downscale > 0):
                log.warning('>> DOWNSCALE %s', f_downscale)


            # ankostis_mdb:  't', "v in km/h","v_orig","a in m/s²","gear","g_min","g_max","gear_modification","error_description"
            # heinz:         't', 'km_h', 'stg', 'gear'
            df = pd.DataFrame(model['cycle_run'])

            _compare_exp_results(df, outfname, compare_results)
            df.to_csv(outfname, index_label='time')
    fail_limit_prcnt = 0.1
    assert failed_vehicles < fail_limit_prcnt * df.shape[0], \
            'TOO MANY(>%f) vehicles have Failed(%i out of %i)!'% (fail_limit_prcnt, failed_vehicles, df.shape[0])


#     vehfpath = os.path.join(samples_dir, 'heinz_Petrol_veh{:05}.dri'.format(veh_num))
#     inpfname = glob.glob(vehfpath)[0]
#     df = pd.read_csv(inpfname, encoding='latin-1')


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
        except OSError as ex:  # @UnusedVariable
            print('>> COMPARING(%s): No old-tabular found, 1st time to run' % outfname)
            run_comparison = False



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

