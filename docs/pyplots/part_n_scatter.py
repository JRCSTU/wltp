#!/usr/bin/env python
#-*- coding: utf-8 -*-
#
# Copyright 2013-2014 European Commission (JRC);
# Licensed under the EUPL (the 'Licence');
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at: http://ec.europa.eu/idabc/eupl

from matplotlib import pyplot as plt
import os

import numpy as np
from wltp import (plots, model)
from wltp.test import wltp_db_tests as wltpdb


wltc_data = model._get_wltc_data()
def get_class_parts(class_num):
    classes = ['class1', 'class2', 'class3a']
    cls = classes[class_num-1]
    return wltc_data['classes'][cls]['parts']

def prepare_data(gened_column, heinz_column):

    vehdata = wltpdb._run_the_experiments(transplant_original_gears=False, compare_results=False)
    vehdata = vehdata[vehdata['class'] == 3]    #Filter only Class-3 vehs

    data =[]
    for (veh_num, df_g, df_h) in wltpdb._file_pairs(wltpdb.gened_fname_glob):
        try:
            class_num = vehdata.loc[veh_num, 'class']
        except KeyError:
            continue
        for part in get_class_parts(class_num):
            part_slice = slice(*part)
            data.append([
                df_g.ix[part_slice, 'gears'].mean(),
                df_g.ix[part_slice, 'rpm'].mean(),
                df_h.ix[part_slice, 'gear'].mean(),
                df_h.ix[part_slice, 'n'].mean(),
            ])

    data = np.array(data)

    return data


if __name__ == '__main__':
    os.chdir(os.path.join(wltpdb.mydir, wltpdb.samples_dir))

    data = prepare_data(gened_column='rpm', heinz_column='n')

    plots.plot_xy_diffs_scatter(
        *data.T,
        quantity_name='Mean EngineSpeed [rpm]',
        title="Python vs Access-db(2sec rule), Class-3",
        x_label='Mean Gear',
        axis=plt.subplot(111),
        mark_sections=None
    )
    plt.show()

