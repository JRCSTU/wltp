#!/usr/bin/env python
# -*- coding: ISO-8859-1 -*-
#
# Copyright 2013-2014 ankostis@gmail.com
#
# This file is part of wltcg.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.

"""Preproc script that reads the tables from the UN-document as CSV, reshapes and stores them as 2-columns CSV.

This utility preprocess the WLTC-cycle speed-profile tables of the spec's word-document
into a format suitable to be consumed by wltcg.
An intermediate human-UI step is required involving a spreadsheet where the word-tables
are copied to be  saved as CSV-files.


Created on Dec 14, 2013

@author: ankostis
"""

import sys


if (__name__ != '__main__'):
    sys.exit("Must be invoked as script!  Name was ({}).".format(__name__))

import os
import numpy as np
import pandas as pd

if (len(sys.argv) == 1):
    inp = sys.stdin
    inpf = '<stdin>'
    out = os.path.abspath("out.df")
else:
    inpf = inp = os.path.abspath(sys.argv[1])
    out = "%s.df" % inp

sys.stderr.write('Transforming 4-to-2 columns: inp(%s) --> out(%s)' % (inpf, out))

df = pd.read_csv(inp, header=-1)

## Use numpy to split and join by 2-columns.
#
twocols = df.values.reshape(-1, 2)

## Revert back to pandas to filter empties and sort.
#
df = pd.DataFrame(twocols)
df = df[pd.notnull(df[0])]
df = df.sort(0, axis=0)

df.to_csv(out, header=False, index=False, encoding='latin')

