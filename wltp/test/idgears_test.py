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

import pandas as pd

from wltp import _idgears as idg

def read_all_cycle_data(cycle_run_file):
    df = pd.read_table(cycle_run_file, sep=',', index_col=None, comment='#', skiprows=2, header=None)
    df = df.convert_objects(convert_numeric=True).dropna()
    
    cols = list('NV')
    if len(set(cols) - set(df.columns)) != 0:
        if df.shape[1] != 2:
            raise ValueError("Expected (at least) 2-column dataset with 'V' [km/h] and 'N' [rpm] columns, got: %s" % df.columns)
        else:
            m = df.median(axis=0)
            df.columns = cols if m.iloc[0] > m.iloc[1] else reversed(cols) # Assume RPMs are bigger numbers.
    return df

class IdgearsTest(unittest.TestCase):


    def test_idgears_from_file(self):
        cycle_df = read_all_cycle_data('VNreal.csv')
        ngears = 5
        
        idg.identify_gears(ngears, cycle_df)
        idg.plot_idgears_results(ngears, cycle_df, gears):    df              = filter_cycle(cycle_df)
        
        best_gears = final_gears[0]
        
        print(best_gears)
        print(final_gears)
        
        plot_idgears_results(ngears, best_gears)
            

if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
