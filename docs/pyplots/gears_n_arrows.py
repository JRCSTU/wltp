#! python
#-*- coding: utf-8 -*-
#
# Copyright 2013-2014 European Commission (JRC);
# Licensed under the EUPL (the 'Licence');
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at: http://ec.europa.eu/idabc/eupl

import os
import sys
from wltp import (plots, model)
from wltp.test import wltp_db_tests as wltpdb

from matplotlib import pyplot as plt

import numpy as np
import pandas as pd


classes = ['class1', 'class2', 'class3b']
wltc_data = model._get_wltc_data()
def get_class_parts(class_num):
    cls = classes[class_num-1]
    return wltc_data['classes'][cls]['parts']

def data_meanN_gears(cls_num):

    vehdata = wltpdb._run_the_experiments(transplant_original_gears=False, compare_results=False)
    vehdata = vehdata[vehdata['class'] == cls_num]    ## Filter only the  Class.

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

    data = pd.DataFrame(np.array(data), columns=['gened_gear', 'gened_rpm', 'heinz_gear', 'heinz_rpm'])

    return data


def plot(cls_num):
    os.chdir(os.path.join(wltpdb.mydir, wltpdb.samples_dir))

    cls_name = classes[cls_num-1]

    data = data_meanN_gears(cls_num)
    (X, Y, X_REF, Y_REF) = (data.gened_gear, data.gened_rpm, data.heinz_gear, data.heinz_rpm)
    
    kws = dict(data_fmt='ok', data_kws=dict(fillstyle='none'), ref_fmt='og', ref_kws=dict(fillstyle='none'))
    axes_tuple, artists = plots.plot_xy_diffs_arrows(
        X, Y, X_REF, Y_REF,
        ref_label='Access-db %s'%cls_name, data_label='Python %s'%cls_name,
        title="Python vs Access-db(2sec rule), %s" % cls_name,
        x_label=r'Mean Gear',
        y_label='$Mean EngineSpeed [rpm]$',
        axes_tuple=None,
        mark_sections=None,
        **kws
    )

if __name__ == '__main__':
    cls_num = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    plot(cls_num)
    plt.show()

