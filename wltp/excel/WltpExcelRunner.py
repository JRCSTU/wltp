#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Sample `xlwings` script
#######################

The functions included provide for running a batch of experiments in an excel-table
with json-pointer paths as headers (see accompanying :file:`.xlsm`).

You can debug it by running it directly as a python script, as suggested by :
  http://docs.xlwings.org/debugging.html

<< EDIT THIS SCRIPT TO PUT YOUR EXCEL/XLWINGS PYTHON-CODE, BELOW >>
"""


from __future__ import division, print_function, unicode_literals

import os, re, operator, logging

import pandas as pd
import xlwings as xw

from wltp.experiment import Experiment
import pandalone.pandata as pdl
import traceback

DEFAULT_LOG_LEVEL = logging.INFO


def _init_logging(loglevel):  ## DEPRECATE!
    logging.basicConfig(level=loglevel)
    logging.getLogger().setLevel(level=loglevel)

    log = logging.getLogger(__name__)
    log.trace = lambda *args, **kws: log.log(0, *args, **kws)

    return log


log = _init_logging(DEFAULT_LOG_LEVEL)


## TODO: Convert Excel-ref RC-notation to A1
_excel_ref_specifier_regex = re.compile(
    r"""^\s*
            @
            (?:(?P<sheet>.+)!)?             # Sheet-name optional-group
            (?P<ref>                        # start Cell-ref
                (?:[A-Z]+\d+ | R\d+C\d+ | \(\d+,\d+\))        # FROM-ref, RC/A1 notation, or tuple
                (?:                             # start TO-Cell-ref optional-group
                    :
                    (?:[A-Z]+\d+ | R\d+C\d+ | \(\d+,\d+\))        # RC/A1 notation, or tuple
                )?                              # end TO-Cell-ref optional-group
            )                               # end Cell-ref
            (?:                             # start Shape-specifier optional-group
                \.
                (?P<shape>table|vertical|horizontal)     # See respective xw.Range attributes
            )?                              # end Shape-specifier
            (?:\((?P<range_kws>                   # start RANGE-kws expression
                [^)]*
            )\))?                            # end RANGE-kws
            (?:{(?P<pandas_kws>                   # start PANDAS-kws expression
                [^)]*
            )})?                            # end PANDAS-kws
            \s*$""",
    re.X + re.IGNORECASE,
)
_undefined = object()


def _parse_kws(kws_str):
    if kws_str:
        local_vars = {}
        exec("kws = dict(%s)" % kws_str, None, local_vars)
        return local_vars["kws"]
    return {}


def resolve_excel_ref(ref_str, default=_undefined):
    """
    if `ref_str` is an *excel-ref*, it returns the referred-contents as DataFrame or a scalar, `None` otherwise.

    Excel-ref examples::

            @a1
            @E5.column
            @some sheet_name!R1C5.TABLE
            @1!a1:c5.table(header=False)
            @3!a1:C5.horizontal(strict=True; atleast_2d=True)
            @sheet-1!A1.table(asarray=True){columns=['a','b']}
            @any%sheet^&name!A1:A6.vertical(header=True)        ## Setting Range's `header` kw and
                                                                #      DataFrame will parse 1st row as header

    The *excel-ref* syntax is case-insensitive apart from the key-value pairs,
    which it is given in BNF-notation:

    .. productionlist::
            excel_ref   : "@"
                        : [sheet "!"]
                        : cells
                        : ["." shape]
                        : ["(" range_kws ")"]
                        : ["{" df_kws "}"]
            sheet       : sheet_name | sheet_index
            sheet_name  : <any character>
            sheet_index : `integer`
            cells       : cell_ref [":" cell_ref]
            cell_ref    : A1_ref | RC_ref | tuple_ref
            A1_ref      : <ie: "A1" or "BY34">
            RC_ref      : <ie: "R1C1" or "R24C34">
            tuple_ref   : <ie: "(1,1)" or "(24,1)", the 1st is the row>
            shape       : "." ("table" | "vertical" | "horizontal")
            range_kws   : kv_pairs                    # keywords for xlwings.Range(**kws)
            df_kws      : kv_pairs                    # keywords for pandas.DataFrafe(**kws)
            kv_pairs    : <python code for **keywords ie: "a=3.14, f = 'gg'">


    Note that the "RC-notation" is not converted, so Excel may not support it (unless overridden in its options).
    """

    matcher = _excel_ref_specifier_regex.match(ref_str)
    if matcher:
        ref = matcher.groupdict()
        log.info("Parsed string(%s) as Excel-ref: %s", ref_str, ref)

        sheet = ref.get("sheet") or ""
        try:
            sheet = int(sheet)
        except ValueError:
            pass
        cells = ref["ref"]
        range_kws = _parse_kws(ref.get("range_kws"))
        ref_range = xw.Range(sheet, cells, **range_kws)
        range_shape = ref.get("shape")
        if range_shape:
            ref_range = operator.attrgetter(range_shape.lower())(ref_range)

        v = ref_range.value

        if ref_range.row1 != ref_range.row2 or ref_range.col1 != ref_range.col2:
            ## Parse as DataFrame when more than one cell.
            #
            pandas_kws = _parse_kws(ref.get("pandas_kws"))
            if "header" in range_kws and not "columns" in pandas_kws:
                ##Do not ignore explicit-columns.
                v = pd.DataFrame(v[1:], columns=v[0], **pandas_kws)
            else:
                v = pd.DataFrame(v, **pandas_kws)

        log.debug("Excel-ref(%s) value: %s", ref, v)

        return v
    else:
        if default is _undefined:
            raise ValueError("Invalid excel-ref(%s)!" % ref_str)
        else:
            return default


def add_cycle_run_as_sheet(veh_id, mdl_out):
    sheet = "cycle_%s" % veh_id
    try:
        sh = xw.Sheet(sheet)
        log.info("Sheet(%s) already exists. Clearing it", sheet)
        sh.clear()
    except Exception:
        xw.Sheet.add(sheet)
    xw.Range(sheet, "A1").value = mdl_out["cycle_run"]


def read_table_as_df(range):
    """
    Expects excel-table with jsonpointer paths as Header and 1st column named `id` as index,
    like this::

        id     vehicle/test_mass  vehicle/p_rated           vehicle/gear_ratios
        veh_1               1500              100  [120.75, 75, 50, 43, 37, 32]
        veh_2               1600               80  [120.75, 75, 50, 43, 37, 32]
        veh_3               1200               60  [120.75, 75, 50, 43, 37, 32]

    """
    vehs = xw.Range(0, range).table.value
    vehs = pd.DataFrame(vehs[1:], columns=vehs[0]).set_index("id")

    return vehs


def build_models(vehs_df, **locals_kws):
    """
    Builds all input-dataframes as Experiment classes and returns them in a list of (veh_id, exp) pairs.

    :param vehs_df:     A dataframe indexed by veh_id, and with columns *json-pointer* paths into the model
    :return: a list of (veh_id, :class:`wltp.experiment.Experiment`) tuples
    """
    experiment_pairs = []
    for veh_id, row in vehs_df.iterrows():
        try:
            mdl_in = {}
            for colname, colval in row.items():
                log.debug("veh_id(%s): Column(%s): %s", veh_id, colname, colval)
                if not colval or (isinstance(colval, str) and not colval.strip()):
                    continue
                if isinstance(colval, str):

                    ## Is it an excel-ref like:
                    #        @<sheet_name>!A1[:R10:c1].table
                    #
                    try:
                        colval = resolve_excel_ref(colval)
                    except ValueError:
                        ## Try to parse value as python-code.
                        #
                        try:
                            old_v = colval
                            colval = eval(
                                colval, globals(), locals_kws
                            )  ## NOTE: Total insecure, but we're scientists, aren't we?
                        except Exception:
                            log.info(
                                "Failed parsing value(%s) as python code due to: %s\n  Assuming plain string.",
                                old_v,
                                traceback.format_exc(),
                            )
                        else:
                            log.info(
                                "Parsed value(%s) as python code into: %s",
                                old_v,
                                colval,
                            )
                pdl.set_jsonpointer(mdl_in, colname, colval)

            exp = Experiment(mdl_in)

            experiment_pairs.append((veh_id, exp))
        except Exception as ex:
            raise Exception("Invalid model for vehicle(%s): %s" % (veh_id, ex)) from ex

    return experiment_pairs


def run_experiments(experiment_pairs):
    """
    Iterates `veh_df` and runs experiment_pairs.

    :param vehs_df:     A dataframe indexed by veh_id, and with columns *json-pointer* paths into the model
    """
    for veh_id, exp in experiment_pairs:
        try:
            mdl_out = exp.run()

            add_cycle_run_as_sheet(veh_id, mdl_out)
        except Exception as ex:
            raise Exception(
                "Experiment failed for vehicle(%s): %s" % (veh_id, ex)
            ) from ex


def _get_active_workbook():
    from win32com.client import dynamic  # @UnusedImport

    com_app = dynamic.Dispatch("Excel.Application")  # @UndefinedVariable
    com_wb = com_app.ActiveWorkbook
    wb = xw.Workbook(xl_workbook=com_wb)

    return wb


def _open_my_workbook():
    excel_fname = os.path.join(
        os.path.dirname(__file__),
        "%s.xlsm" % os.path.splitext(os.path.basename(__file__))[0],
    )
    wb_path = os.path.abspath(excel_fname)
    wb = xw.Workbook(wb_path)

    return wb


def main():
    log.info("CWD: %s", os.getcwd())

    ## Open and run experiments
    #
    # wb = _open_my_workbook()
    wb = _get_active_workbook()

    vehs_df = read_table_as_df("D2")
    log.info("%s", vehs_df)
    exp_pairs = build_models(vehs_df)
    run_experiments(exp_pairs)

    return wb


if __name__ == "__main__":
    main()
