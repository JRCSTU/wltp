#!/usr/bin/env python
#-*- coding: utf-8 -*-
#
# Copyright 2013-2014 European Commission (JRC);
# Licensed under the EUPL (the 'Licence');
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at: http://ec.europa.eu/idabc/eupl

import os

from matplotlib import pyplot as plt
from wltp import plots
from wltp.test import wltp_db_tests as wltpdb


def prepare_data(gened_column, heinz_column):
    gened_column='rpm' 
    heinz_column='n'
    vehdata = wltpdb.aggregate_single_columns_means(gened_column, heinz_column)
    vehdata['pmr'] = 1000.0 * vehdata['rated_power'] / vehdata['kerb_mass']

    return vehdata.pmr, vehdata.gened, vehdata.heinz


if __name__ == '__main__':
    os.chdir(os.path.join(wltpdb.mydir, wltpdb.samples_dir))
    
    (X, Y, Y_REF) = prepare_data(gened_column='rpm', heinz_column='n')

    plots.pmr_xy_diffs_scatter(
        X, Y, Y_REF, 
        quantity_name='EngineSpeed', 
        quantity_units='rpm', 
        title="Python vs Access-db(2sec rule)",
        x_label=r'$PMR [W/kg]$',
        axis=plt.subplot(111), 
    )
    plt.show()
    
