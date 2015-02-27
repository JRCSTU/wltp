#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# Copyright 2014 European Commission (JRC);
# Licensed under the EUPL (the 'Licence');
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at: http://ec.europa.eu/idabc/eupl
from unittest.case import skipIf
import tempfile
'''Check xlwings excel functionality.
'''

import unittest
import logging
import os, sys
import pandas as pd
import numpy as np
from numpy import testing as npt
from pandas.core.generic import NDFrame


DEFAULT_LOG_LEVEL   = logging.INFO
def _init_logging(loglevel):
    logging.basicConfig(level=loglevel)
    logging.getLogger().setLevel(level=loglevel)

    log = logging.getLogger(__name__)
    log.trace = lambda *args, **kws: log.log(0, *args, **kws)
    
    return log
log = _init_logging(DEFAULT_LOG_LEVEL)


def from_my_path(*parts):
    return os.path.join(os.path.dirname(__file__), *parts)

def _make_sample_workbook(sheetname, addr, value):
    import xlwings as xw
    wb = xw.Workbook()
    xw.Sheet(1).name = sheetname
    xw.Range(addr).value = value

    return wb

def close_workbook(wb):
    try:
        wb.close()
    except Exception:
        log.warning('Minor failure while closing Workbook!', exc_info=True)


@skipIf(not ('darwin' in sys.platform or 'win32' in sys.platform), "Cannot test xlwings in Linux")
class TestExcel(unittest.TestCase):

    def test_build_excel(self):
        from ..excel import xlsutils 
        
        with tempfile.TemporaryDirectory() as tmpdir:
            wb_inp_fname    = from_my_path('..', 'excel', 'WltpExcelRunner.xlsm')
            wb_out_fname    = from_my_path(tmpdir, 'WltpExcelRunner.xlsm')
            vba_wildcard    = from_my_path('..', 'excel', '*.vba')
            try:
                wb = xlsutils.import_files_into_excel_workbook(vba_wildcard, wb_inp_fname, wb_out_fname)
            finally:
                if wb:
                    close_workbook(wb)



    def test_xlwings_smoketest(self):
        import xlwings as xw
        sheetname   ='shitt'
        addr        ='f6'
        table       = pd.DataFrame([[1,2],[True, 'off']], columns=list('ab'))
        wb = xw.Workbook()
        try:
            xw.Sheet(1).name = sheetname
            xw.Range(addr).value = table
        finally:
            close_workbook(wb)


    def test_excel_refs(self):
        from ..excel.WltpExcelRunner import resolve_excel_ref
        sheetname   ='Input'
        addr        ='d2'
        table       = pd.DataFrame({'a':[1,2,3], 'b':['s','t','u'], 'c':[True,False,True]})
        table.index.name = 'id'
        
        cases = [
            ("@d2",                         'id'),
            ("@e2",                         'a'),
            ("@e3",                         1),
            ("@e3:g3",                      table.iloc[0, :].values.reshape((3,1))),
            ("@1!e2.horizontal",            table.columns.values.reshape((3,1))),
            ("@1!d3.vertical",              table.index.values.reshape((3,1))),
            ("@e4.horizontal",              table.iloc[1, :].values.reshape((3,1))),
            ("@1!e3:g3.vertical",           table.values),
            ("@{sheet}!E2:F2.table(strict=True, header=True)".format(sheet=sheetname),
                                            table),
        ]
        
        errors = []
        wb = _make_sample_workbook(sheetname, addr, table)
        try:
            for i, (inp, exp) in enumerate(cases):
                out = None
                try:
                    out = resolve_excel_ref(inp)
                    log.debug('%i: INP(%s), OUT(%s), EXP(%s)', i, inp, out, exp)
                    if not exp is None:
                        if isinstance(out, NDFrame):
                            out = out.values
                        if isinstance(exp, NDFrame):
                            exp = exp.values
                        if isinstance(out, np.ndarray) or isinstance(exp, np.ndarray):
                            npt.assert_array_equal(out, exp, '%i: INP(%s), OUT(%s), EXP(%s)' % (i, inp, out, exp))
                        else:
                            self.assertEqual(out, exp, '%i: INP(%s), OUT(%s), EXP(%s)' % (i, inp, out, exp))
                except Exception as ex:
                    log.exception('%i: INP(%s), OUT(%s), EXP(%s), FAIL: %s' % (i, inp, out, exp, ex))
                    errors.append(ex)
        finally:
            close_workbook(wb)

        if errors:
            raise Exception('There are %i out of %i errors!'% (len(errors), len(cases)))


    def test_excel_runner_call_from_python(self):
        from ..excel import WltpExcelRunner 
        wb = None
        try:
            wb = WltpExcelRunner.main()
        finally:
            if wb:
                close_workbook(wb)


if __name__ == "__main__":
    unittest.main()
