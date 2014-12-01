#! python
#-*- coding: utf-8 -*-
#
# Copyright 2013-2014 European Commission (JRC);
# Licensed under the EUPL (the 'Licence');
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at: http://ec.europa.eu/idabc/eupl

from matplotlib import pyplot as plt
import os

from wltp import plots
from wltp.test import wltp_db_tests as wltpdb


def data_meanN_pmr(gened_column, heinz_column):
    gened_column='rpm'
    heinz_column='n'
    vehdata = wltpdb.aggregate_single_columns_means(gened_column, heinz_column)

    return vehdata


if __name__ == '__main__':
    os.chdir(os.path.join(wltpdb.mydir, wltpdb.samples_dir))

    classes = [
        ['class1',  dict(data_fmt='4k', data_kws=dict(fillstyle='none'), ref_fmt='4g', ref_kws=dict(fillstyle='none'))],  
        ['class2',  dict(data_fmt='_k', data_kws=dict(fillstyle='none'), ref_fmt='_g', ref_kws=dict(fillstyle='none'))],  
        ['class3a', dict(data_fmt='ok', data_kws=dict(fillstyle='none'), ref_fmt='og', ref_kws=dict(fillstyle='none'))], 
        ['class3b', dict(data_fmt='+k', data_kws=dict(fillstyle='none'), ref_fmt='+g', ref_kws=dict(fillstyle='none'), diff_label='Differences')], 
    ]
    
    vehdata = data_meanN_pmr(gened_column='rpm', heinz_column='n')
    
    axes_tuple = None
    for (cls, kws) in classes:
        cls_data = vehdata[vehdata['wltc_class'] == cls]
        if cls_data.empty:
            continue
        (X, Y, Y_REF) = cls_data.pmr, cls_data.gened, cls_data.heinz
    
        axes_tuple, artists = plots.plot_xy_diffs_scatter(
            X, Y, X, Y_REF,
            ref_label='Access-db %s'%cls, data_label='Python %s'%cls,
            title="Python vs Access-db(2sec rule)",
            x_label=r'$PMR [W/kg]$',
            y_label='$EngineSpeed [rpm]$',
            axes_tuple=axes_tuple,
            **kws
        )

    axes_tuple[1].legend(loc=4, fancybox=True, framealpha=0.5)
    axes_tuple[0].legend(loc=1, fancybox=True, framealpha=0.5)

    plt.show()

