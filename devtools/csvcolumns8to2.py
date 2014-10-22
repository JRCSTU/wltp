#! python
#-*- coding: utf-8 -*-
#
# Copyright 2013-2014 European Commission (JRC);
# Licensed under the EUPL (the 'Licence');
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at: http://ec.europa.eu/idabc/eupl
"""Preproc script that reads the tables from the UN-document as CSV, reshapes and stores them as 2-columns CSV.

This utility preprocess the WLTC-cycle speed-profile tables of the spec's word-document
into a format suitable to be consumed by wltp.
An intermediate human-UI step is required involving a spreadsheet where the word-tables
are copied into a spreadsheet to be exported as CSV-files.

It expects odd columns to contain the time-steps, so that by sorting on it to reconstruct the whole cycle-profile.

Example::
    cat multiColumn.txt | python3 csvcolumns8to2.py > out.csv
or::
    python3 csvcolumns8to2.py multiColumn.txt
"""


from __future__ import division, print_function, unicode_literals

def csvcolumns8to2(inp, inpfname, out, outfname):
    import pandas as pd

    sys.stderr.write('Transforming to 2-columns: inp(%s) --> out(%s)\n' % (inpfname, outfname))

    xls     = pd.ExcelFile(inp)
    sheets  = xls.sheet_names
    df      = xls.parse(sheets[0])
    df      = df.convert_objects(convert_numeric=True)


    ## Use numpy to split and join by 2-columns.
    #
    twocols = df.values.reshape(-1, 2)

    ## Revert back to pandas to filter empties and sort.
    #
    df = pd.DataFrame(twocols)
    df = df[pd.notnull(df[0])]
    df = df.sort(0, axis=0)

    df[[0]] = df[[0]].astype(int) # Time

    df.to_csv(out, header=False, index=False, encoding='latin')




if (__name__ == '__main__'):
    import sys
    import os

    inp = sys.stdin
    inpfname = '<stdin>'
    out = sys.stdout
    outfname = '<stdout>'
    if (len(sys.argv) >= 2):
        inpfname = inp = os.path.abspath(sys.argv[1])
    if (len(sys.argv) >= 3):
        outfname = out = os.path.abspath(sys.argv[2])

    csvcolumns8to2(inp, inpfname, out, outfname)

