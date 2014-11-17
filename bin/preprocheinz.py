#! python
#-*- coding: utf-8 -*-
#
# Copyright 2013-2014 European Commission (JRC);
# Licensed under the EUPL (the 'Licence');
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at: http://ec.europa.eu/idabc/eupl
'''
Converts to CSVs and consolidate input & results tables from Heinz' ms-access db.

:input inp_excel:   one excel-file with input vehicles, exported from the ``vehicle_info`` db-table
:input veh_excel:   many excel-files exported from ``A gearshift_table_check_result_final`` query,
                     one for each row in the above file
:output inp_csv:   a csv from the input-excel, updated with same-valued(steady) columns
:output veh_csv:   multiple CSVs from the input-excels, without the same-valued(steady) columns (moved to inp_vehs)

.. Note: Requires excel-files to be present that were produced from ``A gearshift_table_check_result_final``
ms-access query.
'''

from __future__ import division, print_function, unicode_literals

import glob, os, os.path as path
import re

from openpyxl.exceptions import IllegalCharacterError

import numpy as np, pandas as pd


def heinz_db_result_table_to_csv(heinz_results_glob, inp_vehs_df, cols_to_move, cols_to_rename, cols_to_drop, index_col):

    for heinz_fname in heinz_results_glob:
        print("%s..."%heinz_fname, end='')

        try:
            m = re.match('(\d+)', heinz_fname)
            assert m, heinz_fname
            veh = int(m.groups()[0])

            assert veh in inp_vehs_df.index, "Heinz-out veh(%s) not in inp-vehs!"%veh

            heinz_out_df = pd.read_excel(heinz_fname, 0)

            ## Check veh's fname matches content.
            assert veh == heinz_out_df.ix[0, 'vehicle_no'], "heinz-out[0, 0](%s) != fname-veh(%s)!"%(heinz_out_df.iloc[0, 0], veh)

            ## Check same-valued columns are indeed so.
            #
            steady_cols = cols_to_move + [left for (left, _) in cols_to_rename]
            for col in steady_cols:
                cval = heinz_out_df.ix[0, col]
                assert (heinz_out_df[col] == cval).all(), "move-col(%s): %s != for all-heinz-out(%s)!" %(col, cval, heinz_out_df[col])


            ## Rename same-valued columns with clashing names into input-matrix.
            #
            for (col, ncol) in cols_to_rename:
                cval = heinz_out_df.ix[0, col]
                if ncol in inp_vehs_df.columns:
                    ## Check if overwriting other value.
                    #
                    dval = inp_vehs_df.ix[veh, ncol]
                    if not pd.isnull(dval) and heinz_out_df[col].dtype == inp_vehs_df[ncol].dtype and cval != dval:
                        print("Warn: rename-col(%s->%s): %s != inp-vehs(%s)!" %(col, ncol, cval, dval))
                inp_vehs_df.ix[veh, ncol] = cval

            ## Move same-valued columns into input-matrix.
            #
            for col in cols_to_move:
                cval = heinz_out_df.ix[0, col]
                if col in inp_vehs_df.columns:
                    ## Check if overwriting other value.
                    #
                    dval = inp_vehs_df.ix[veh, col]
                    if not pd.isnull(dval) and heinz_out_df[col].dtype == inp_vehs_df[col].dtype and cval != dval:
                        print("WARN: move-col(%s): %s != inp-vehs(%s)!" %(col, cval, dval))
                inp_vehs_df.ix[veh, col] = cval


            heinz_out_df.index = heinz_out_df[index_col]
            heinz_out_df.index.name = index_col

            heinz_out_df = heinz_out_df.drop(steady_cols + cols_to_drop + [index_col], axis=1)

            (fn, _) = os.path.splitext(heinz_fname)
            outfname = 'heinz-{:04}{}'.format(veh, ".csv")

            heinz_out_df.to_csv(outfname, encoding='UTF-8')
            print("  Stored heiz-out(%s)" %outfname)
        except Exception as ex:
            print("Error: ", ex)

    return inp_vehs_df





def post_proc_heinz_results():
    """
    Moves columns with repeatitious data into a master-vehicles csv listing all vehicle-parameters.
    """

    inp_vehs_xcls            = 'vehicle_info.xlsx'
    inp_vehs_fname          = 'wltp_db_vehicles.csv'
    inp_vehs_2_fname        = 'wltp_db_vehicles2.csv'
    heinz_results_wildcard  = '*-*.xls'
    index_col               = 't'
    ## Move same-valued columns from heinz-output's --> input-matrix.
    cols_to_move            = [
        'Power_curve_no', 'safety_margin_Pwot', 'additional_margin_at_idling', 'actual_safety_margin',
        'safety_margin_v_max', 'downscale_percentage', 'look_ahead_time', 'vehicle_no', 'kerb_mass', 'test_mass',
        'rated_power', 'rated_speed', 'idling_speed', 'n_min_drive', 'n_min_2', 'vehicle_class', 'n_norm_max', 'no_of_gears',
    ]
    ## Copy renamed same-valued columns from heinz-output's --> input-matrix.
    cols_to_rename          = [
        ('v_max',  'v_max_2'),
        ('f0', 'f0_real'), ('f1', 'f1_real'), ('f2', 'f2_real' )
    ]
    ## Columns to remove from heinz-output's.
    cols_to_drop            = [ 'f0', 'f1', 'f2',  ]


    # (inp_vehs_2_fname, ext) = path.splitext(inp_vehs_fname)
    #inp_vehs_2_fname = '%s-2%s'%(inp_vehs_2_fname, ext)

    heinz_results_glob = glob.glob(heinz_results_wildcard)

    dfin = pd.read_excel(inp_vehs_xcls, 0, index_col=0)
    #dfin = pd.read_csv(inp_vehs_fname, index_col=0, encoding='UTF-8')

    dfin = heinz_db_result_table_to_csv(heinz_results_glob, dfin, cols_to_move, cols_to_rename, cols_to_drop, index_col)

    ## Remove vehs without results (no f0)
    dfin=dfin[~dfin.f0_real.isnull()]

    dfin.to_csv(inp_vehs_2_fname, encoding='UTF-8')
    print("Stored modified inp-vehs(%s)" %inp_vehs_2_fname)


def reindex_db_vehicles():
    heinz_classes_excel = 'gearshift_description_development_DB_mod2.xlsx'
    out_vehs_fname = 'wltp_db_vehicles.xls'

    dfin1 = pd.read_excel(heinz_classes_excel, 0, index_col=None, skiprows=4, parse_cols='C:Z')
    dfin2 = pd.read_excel(heinz_classes_excel, 1, index_col=None, skiprows=4, parse_cols='C:Z')
    dfin3 = pd.read_excel(heinz_classes_excel, 2, index_col=None, skiprows=4, parse_cols='C:Z')

    dfout = pd.concat((dfin1, dfin2, dfin3, ), ignore_index=True)

    ## Move old possible-repetetitious veh_no into comments.
    #
    dfout['description1'] = dfout['vehicle_no'].apply(lambda x: '%s: '%x) + dfout['description1'].apply(lambda x: str(x))
    dfout['vehicle_no'] = dfout.reset_index().index

    dfout = dfout.rename(columns={
        'category': 'ID_cat',
        'description1': 'Comment',
    })
    dfout['eng_id'] = dfout['IDengine']

    ## New cols.
    #
#     dfout['ndv_7'] = np.nan
    dfout['user_def_driv_res_coeff'] = 0
    dfout['user_def_power_curve'] = 0

    dfout = dfout.reindex(columns = [
        'vehicle_no', 'rated_power', 'kerb_mass', 'rated_speed', 'idling_speed', 'test_mass', 'no_of_gears',
        'ndv_1', 'ndv_2', 'ndv_3', 'ndv_4', 'ndv_5', 'ndv_6', 'ndv_7',
        'ID_cat', 'user_def_driv_res_coeff', 'user_def_power_curve', 'f0', 'f1', 'f2', 'Comment',
        'pmr_km', 'v_max', 'g_v_max', 'n_norm_vmax', 'n_vmax',  # Should have dropped them.
    ])

    NGs = dfout.loc[:, 'ndv_1':'ndv_7']
    NGs[NGs == 0] = np.NaN
    dfout.loc[:, 'ndv_1':'ndv_7'] = NGs

    dfout.to_excel(out_vehs_fname, index=False)


if __name__ == '__main__':
    _mydir = path.dirname(__file__)
    os.chdir(path.join(_mydir, '../wltp/test/wltp_db'))

    post_proc_heinz_results() #TODO: have top re-proc heinz-files.
    #reindex_db_vehicles()
