#! python
#-*- coding: utf-8 -*-
#
# Copyright 2013-2014 European Commission (JRC);
# Licensed under the EUPL (the 'Licence');
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at: http://ec.europa.eu/idabc/eupl

from __future__ import division, unicode_literals

import unittest
from unittest.case import skipIf
import numpy as np
import numpy.testing as npt

import pandas as pd

from wltp import idgears as idg
import os

def read_all_cycle_data(cycle_run_file, start_col_index=0):
    cycle_run_file = os.path.join(os.path.dirname(__file__), cycle_run_file)
    df = pd.read_table(cycle_run_file, sep=',', index_col=None, comment='#', skiprows=5, header=None)
    df = df.iloc[:, start_col_index:start_col_index+2]
    df = df.convert_objects(convert_numeric=True).dropna()
    
    cols = list('NV')
    if len(set(cols) - set(df.columns)) != 0:
        if df.shape[1] != 2:
            raise ValueError("Expected (at least) 2-column dataset with 'V' [km/h] and 'N' [rpm] columns, got: %s" % df.columns)
        else:
            m = df.median(axis=0)
            df.columns = cols if m.iloc[0] > m.iloc[1] else reversed(cols) # Assume RPMs are bigger numbers.
    return df

file_results = [                                                                # VoverN-DISTORT       DISTORT1           1/DISTORT
    ([ 0.00862961, 0.01414138, 0.02040305, 0.02705056, 0.03361355, 0.03913649], 0.000776115495842, 0.00102891505859 , 0.000623132178672),
    ([ 0.0077537 , 0.01430799, 0.02039729, 0.02715475, 0.03377971, 0.03948467], 0.000182951571423, 0.000319414911246, 0.993806101491),
    ([ 0.00773553, 0.01428506, 0.02039676, 0.02713253, 0.03377312, 0.03950773], 0.00034170109883 , 0.000618105921847, 0.370373235935),
    ([ 0.00701223, 0.01270195, 0.01852081, 0.0244521 , 0.029762  , 0.04085927], 0.000412191410851, 0.00137557327434 , 4.44380835405e-20),
]

class IdgearsTest(unittest.TestCase):

    def test_dequantize(self):
        df = pd.DataFrame([
                           [1,3],
                           [1,3],
                           [2,3],
                           [2,4],
                           [2,4],
                           ])
        ddf = idg.dequantize(df)
        exp = pd.DataFrame([
                           [1,      3],
                           [1.5,    3.333],
                           [2,      3.666],
                           [2,      4],
                           [2,      4],
                           ])
        npt.assert_almost_equal(ddf.values, exp.values, 3)


    def test_dequantize_mean_is_stable(self):
        df = pd.DataFrame(np.random.randn(100).cumsum())
        ddf = idg.dequantize(df)
        self.assertAlmostEqual(df.values.mean(), ddf.values.mean())


    def test_detect_gear_ratios_from_cycle_data(self):
        for start_col_index, result in zip(range(0, 7, 2), file_results):
            ngears = 6
            cycle_df = read_all_cycle_data('VNreal.csv', start_col_index)
            
            ratios, distort = idg.detect_gear_ratios_from_cycle_data(ngears, cycle_df)
            #print("ratios: %s, distort: %s"%(ratios, distort))
            self.assertEqual(ratios.size, ngears)
            self.assertLessEqual(distort, 8e-4)
            
            ## Require exact equality on file_results.
            #
            self.assertAlmostEqual(distort, result[1])
            npt.assert_almost_equal(ratios, result[0])

    def test_identify_gears_from_cycle_data(self):
        for start_col_index, result in zip(range(0, 7, 2), file_results):
            ngears = 6
            cycle_df = read_all_cycle_data('VNreal.csv', start_col_index)
            
            gears, distorts = idg.identify_gears_from_cycle_data(cycle_df, result[0])
            self.assertEqual(gears.dtype, np.int64)
            distort = distorts.mean()
            self.assertTrue((0 <= gears).all())
            self.assertTrue((gears < ngears).all())
            #print(distort)
            self.assertLessEqual(distort, 2e-3)
            self.assertAlmostEqual(distort, result[1])


    def test_identify_gears_ratios_and_iverse(self):
        for start_col_index, result in zip(range(0, 7, 2), file_results):
            ngears = 6
            cycle_df = read_all_cycle_data('VNreal.csv', start_col_index)
            
            gears, distorts = idg.identify_gears_from_ratios(cycle_df['V']/cycle_df['N'], result[0])
            self.assertEqual(gears.dtype, np.int64)
            distort = distorts.mean()
            self.assertTrue((0 <= gears).all())
            self.assertTrue((gears < ngears).all())
            #print(distort)
            self.assertLessEqual(distort, 2e-3)
            self.assertAlmostEqual(distort, result[2])

            gears, distorts = idg.identify_gears_from_ratios(cycle_df['N']/cycle_df['V'], 1/np.array(result[0]))
            self.assertEqual(gears.dtype, np.int64)
            self.assertTrue((0 <= gears).all())
            self.assertTrue((gears < ngears).all())
            distort = 1/distorts.mean()
            #print(distort)
            self.assertLessEqual(distort, 1)
            self.assertAlmostEqual(distort, result[3])


    @skipIf(not 'UI' in os.environ, "No GUI! (demanded in env-var $UI)")
    def test_detect_ratios_and_plot(self):
        from matplotlib import pyplot as plt
        fig = plt.figure()
        
        for i, start_col_index in enumerate(range(0, 7, 2)):
            ngears = 6
            cycle_df = read_all_cycle_data('VNreal.csv', start_col_index)
            
            detekts = idg.run_gear_ratios_detections_on_cycle_data(ngears, cycle_df)
            best_detekt = detekts[0]
            if os.environ['UI']:
                axes = [plt.subplot(4,3,3*i+1), plt.subplot(4,3,3*i+2), plt.subplot(4,3,3*i+3)]
                idg.plot_idgears_results(cycle_df, best_detekt, fig=fig, axes=axes)
                
        if os.environ['UI']:
            plt.show()

if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
