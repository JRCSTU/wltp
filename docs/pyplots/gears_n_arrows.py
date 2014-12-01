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

from matplotlib import pyplot as plt, cm

import pandas as pd


classes = ['class1', 'class2', 'class3b']
part_names = model.get_class_part_names()
def class_name_from_num(cls_num):
    return classes[cls_num-1]

def data_meanN_gears(cls_num):
    """
    Constructs meanN vs gears, hierarchically grouped by: vehicle, python/heinz, class_part
    
    :return: df like that::
                
                                  python                  heinz             
                                    gear            n      gear            n
                1154 Low        2.020374  1078.312480  2.039049  1105.891341
                     Medium     3.577367  1364.552656  3.618938  1353.300231
                     High       4.028571  1694.902241  4.160440  1618.457143
                     ExtraHigh  4.266254  2532.802858  4.424149  2514.894737

    1155 ...
    """
    def means_by_parts(df, cols_in, cols_out):
        df = df.ix[:, cols_in]
        data = df.groupby(pd.cut(df_g.index, bins=parts)).mean()
        data.index = part_names[:len(data.index)]
        data.columns = cols_out
        
        return data

    cls_name = class_name_from_num(cls_num)
    
    vehdata = wltpdb._run_the_experiments(transplant_original_gears=False, compare_results=False)
    vehdata = vehdata[vehdata['class'] == cls_num]    ## Filter only the  Class.
    
    cols_out = ['gear', 'n']
    data = {}
    for (veh_num, df_g, df_h) in wltpdb._file_pairs(wltpdb.gened_fname_glob):
        try:
            class_num = vehdata.loc[veh_num, 'class']
        except KeyError:
            continue
        parts = model.get_class_parts_limits(cls_name, edges=True)
        
        g_data = means_by_parts(df_g, ['gears', 'rpm'], cols_out)
        h_data = means_by_parts(df_h, ['gear', 'n'], cols_out)
        
        veh_data = pd.concat( (g_data, h_data), axis=1, keys=['python', 'heinz'])
        data[veh_num] = veh_data

    df = pd.concat(list(data.values()), axis=0, keys=data.keys())

    return df


def plot(cls_num):
    os.chdir(os.path.join(wltpdb.mydir, wltpdb.samples_dir))

    cls_name = class_name_from_num(cls_num)

    data = data_meanN_gears(cls_num)

    cols = data.keys()
    assert len(cols) == 4, cols
    
    parts = zip(model.get_class_part_names(), [
        dict(data_fmt='1', data_kws=dict(color='#0000ff', markersize=4.8, ), 
            diff_kws=dict(linestyle=':', linewidth=4)
        ),  
        dict(data_fmt='_', data_kws=dict(color='#0033cc', markersize=4.8, fillstyle='none'), 
            diff_kws=dict(linestyle='-.',linewidth=4)
        ),  
        dict(data_fmt='o', data_kws=dict(color='#006699', markersize=4.8, fillstyle='none'), 
            diff_kws=dict(linestyle='-',linewidth=4)
        ), 
        dict(data_fmt='+', data_kws=dict(color='#009966', markersize=4.8, fillstyle='none'), 
            diff_kws=dict(linestyle='--', linewidth=4)
        ), 
    ])
    
    axes_tuple = None
    for (part, kws) in parts:
        try:
                        ## veh         part   N/gear/Py/Heinz
            X = data.loc[(slice(None), part), cols[0]]
            Y = data.loc[(slice(None), part), cols[1]]
            X_REF = data.loc[(slice(None), part), cols[2]]
            Y_REF = data.loc[(slice(None), part), cols[3]]
        except KeyError:
            continue
        axes_tuple, artist_tuple = plots.plot_xy_diffs_arrows(
            X, Y, X_REF, Y_REF,
            data_label='Python, %s'%part, diff_label='Diffs %s'%part,
            diff_cmap=cm.cool, #@UndefinedVariable
            title="%s: Python(arrow-heads) compared to AccessDb-2secAccel (arrow-tails)" % cls_name,
            x_label=r'Mean Gear',
            y_label='$Mean EngineSpeed [rpm]$',
            axes_tuple=axes_tuple,
            **kws
        )

    axes_tuple[0].legend(loc=1, fancybox=True, framealpha=0.5)
    axes_tuple[1].legend(loc=2, fancybox=True, framealpha=0.5)

    return data, axes_tuple


if __name__ == '__main__':
    cls_num = int(sys.argv[1]) if len(sys.argv) > 1 else 2
    data, axes_tuple = plot(cls_num)
    
    ## Add Pick-cursor
    #
    main_axes = axes_tuple[0]
    # Workaround Matplotlib#815: pick_event works only on z-top-axes.
    for ax in axes_tuple[1:]: ax.set_zorder(0.1); main_axes.set_zorder(1)
    fig = main_axes.get_figure()
    cursor = plots.DataCursor(
                              ax=main_axes, 
                              annotations=list(data.index.levels[0]),
                              text_template='Vehicle: {txt}')
    fig.canvas.mpl_connect('pick_event', cursor)

    plt.show()

