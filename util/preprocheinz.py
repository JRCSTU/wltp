#!/usr/bin/env python
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

:created: 28 Jul 2014
'''

import glob, os, os.path as path
import numpy as np, pandas as pd
import re


def heinz_db_result_table_to_csv(heinz_results_glob, inp_vehs_df, cols_to_move, cols_to_rename, cols_to_drop):

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
            steady_cols = cols_to_move + list(cols_to_rename.keys())
            for col in steady_cols:
                cval = heinz_out_df.ix[0, col]
                assert (heinz_out_df[col] == cval).all(), "move-col(%s): %s != for all-heinz-out(%s)!" %(col, cval, heinz_out_df[col])


            ## Move same-valued columns into input-matrix.
            #
            for col in cols_to_move:
                cval = heinz_out_df.ix[0, col]
                if col in inp_vehs_df.columns:
                    ## Check if overwriting other value.
                    #
                    dval = inp_vehs_df.ix[veh, col]
                    if not np.isnan(dval) and heinz_out_df[col].dtype == inp_vehs_df[col].dtype and cval != dval:
                        print("WARN: move-col(%s): %s != inp-vehs(%s)!" %(col, cval, dval))
                inp_vehs_df.ix[veh, col] = cval


            ## Rename same-valued columns with clashing names into input-matrix.
            #
            for (col, ncol) in cols_to_rename.items():
                cval = heinz_out_df.ix[0, col]
                if ncol in inp_vehs_df.columns:
                    ## Check if overwriting other value.
                    #
                    dval = inp_vehs_df.ix[veh, ncol]
                    if not np.isnan(dval) and heinz_out_df[col].dtype == inp_vehs_df[ncol].dtype and cval != dval:
                        print("Warn: rename-col(%s->%s): %s != inp-vehs(%s)!" %(col, ncol, cval, dval))
                inp_vehs_df.ix[veh, ncol] = cval

            heinz_out_df = heinz_out_df.drop(steady_cols + cols_to_drop, axis=1)

            (fn, _) = os.path.splitext(heinz_fname)
            outfname = 'heinz-{:04}{}'.format(veh, ".csv")
            heinz_out_df.to_csv(outfname, index=None, encoding='UTF-8')
        except Exception as ex:
            print("Error: ", ex)

    return inp_vehs_df





def post_proc_heinz_results():
    inp_vehs_fname          = "JRC_vehicle_info_query.xlsx"
    inp_vehs_2_fname        = 'wltp_db_vehicles.csv'
    heinz_results_wildcard  = '*-*.xls'
    cols_to_move            = [    # Move same-valued columns from heinz-output's --> input-matrix.
        'Power_curve_no', 'safety_margin_Pwot', 'additional_margin_at_idling', 'actual_safety_margin',
        'safety_margin_v_max', 'downscale_percentage', 'look_ahead_time', 'vehicle_no', 'kerb_mass', 'test_mass',
        'rated_power', 'rated_speed', 'idling_speed', 'n_min_drive', 'n_min_2', 'vehicle_class', 'n_norm_max', 'no_of_gears',
    ]
    cols_to_rename          = { 'v_max': 'v_max_2', 'Description': 'comments'}
    cols_to_drop            = [ 'cycle_part', 'f0', 'f1', 'f2', ]


    # (inp_vehs_2_fname, ext) = path.splitext(inp_vehs_fname)
    #inp_vehs_2_fname = '%s-2%s'%(inp_vehs_2_fname, ext)

    heinz_results_glob = glob.glob(heinz_results_wildcard)

    dfin = pd.read_excel(inp_vehs_fname, 0, index_col=0)

    dfin = heinz_db_result_table_to_csv(heinz_results_glob, dfin, cols_to_move, cols_to_rename, cols_to_drop)

    dfin.to_csv(inp_vehs_2_fname, encoding='UTF-8')
    print("Stored modified inp-vehs(%s)" %inp_vehs_2_fname)


def reindex_db_vehicles():
    heinz_classes_excel = 'gearshift_description_development_DB_mod2.xlsx'
    inp_vehs_fname = 'wltp_db_vehicles.csv'

    dfin1 = pd.read_excel(heinz_classes_excel, 0, index_col=None, skiprows=4, parse_cols='C:Z')
    dfin2 = pd.read_excel(heinz_classes_excel, 1, index_col=None, skiprows=4, parse_cols='C:Z')
    dfin3 = pd.read_excel(heinz_classes_excel, 2, index_col=None, skiprows=4, parse_cols='C:Z')

    dfout = pd.concat((dfin1, dfin2, dfin3, ), ignore_index=True)
    dfout = dfout.sort('vehicle_no').reset_index(drop=True)
    dfout.index.name = 'veh_id2'

    dfout.to_csv(inp_vehs_fname, encoding='UTF-8')


# def reindex_heinz_vehiclesOOO():
#     inp_vehs_fname_1 = 'wltp_db_vehicles.csv'
#     inp_vehs_fname_2 = 'gearshift_description_development_DB_mod2.xlsx'
#
#     dfin1 = pd.read_csv(inp_vehs_fname_1, encoding='UTF-8', index_col=0)
#     dfin2a = pd.read_excel(inp_vehs_fname_2, 0, index_col=None, skiprows=4, parse_cols='C:Z')
#     dfin2b = pd.read_excel(inp_vehs_fname_2, 1, index_col=None, skiprows=4, parse_cols='C:Z')
#     dfin2c = pd.read_excel(inp_vehs_fname_2, 2, index_col=None, skiprows=4, parse_cols='C:Z')
#
#     dfin2 = p((dfin2a, dfin2b, dfin2c, ))
#     dfin2 = dfin2.un
#
#     dfin1 = dfin1.join(dfin2.ix[:, 'f0':'f2'], lsuffix='_OLD')
#     dfin1 = dfin1.drop(['f0_OLD', 'f1_OLD', 'f2_OLD'], axis=1)
#
#     dfin1.to_csv(inp_vehs_fname_1, encoding='UTF-8')



if __name__ == '__main__':
    _mydir = path.dirname(__file__)
    os.chdir(path.join(_mydir, '../wltp/test/wltp_db'))

    #post_proc_heinz_results() #TODO: have top re-proc heinz-files.
    reindex_db_vehicles()
