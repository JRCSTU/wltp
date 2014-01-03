#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# Copyright 2013-2014 ankostis@gmail.com
#
# This file is part of wltcg.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.
'''Build a python array from reading WLTC-data files and print it to be includ it as code.

It is used for preparing the WLTC variables for the default Model-data.

For example, to build (and validate) the cycle for WLTC-Class 3.2, execute::

    python buildwltcclass.py class3.2 True

Then copy the output of the program as a python-variable within the wltcg.Model.py.
'''

wltc_data_files = {
    'class1': [],
    'class2': [],
    'class3.1': [
        'class3-1-Low-1',
        'class3-2-Medium-1',
        'class3-3-High-1',
        'class3-4-ExtraHigh-1'
    ],
    'class3.2': [
        'class3-1-Low-1',
        'class3-2-Medium-2',
        'class3-3-High-2',
        'class3-4-ExtraHigh-1'
    ]
}


def read_wltc_class(wltc_class, assert_files = False):
    '''
    :argument: string: wltc_class: ( 'class1' | 'class2' | 'class3.2' )
    :return :generator: with the speed_column floats
    '''

    import collections
    import csv
    import io
    import os


    def iterate_csv(fnames, yieldfun, beginfilefunc = None, endfilefunc = None):
        '''
        :argument: stringarray: fnames: the names of the resource-files
        :argument: function: yieldfunc: how to yield from each csv-row
        :return :generator with the results of the yieldfun(row)
        '''

        for fname in fnames:
            with open(fname, 'rb') as csvfile:  # @UndefinedVariable
                first_line = True
                reader = csv.reader(io.TextIOWrapper(csvfile))
                for row in reader:
                    if (beginfilefunc is not None and first_line):
                        beginfilefunc(row)
                    try:
                        yield yieldfun(row)
                    except csv.Error as e:
                        print('file {}, line {}: {}'.format(fname, reader.line_num, e))
                        raise
                    first_line = False

                if (endfilefunc is not None):
                    endfilefunc(row)



    if (wltc_class not in wltc_data_files):
        raise ValueError('Unknown WLTC-class(%s)!  One of (%s) expected.' %
                         (wltc_class, ', '.join(sorted(wltc_data_files.keys()))))

    mydir = os.path.dirname(__file__)
    class_part_names = [os.path.join(mydir, 'data', '%s.csv' % pname)
                        for pname in wltc_data_files[wltc_class]]

    if (assert_files):
        timer = -1;
        def assert_time_column(row):
            nonlocal timer
            timer += 1
            if (float(row[0]) != timer):
                raise AssertionError('index-col(%s) != expected(%s)' % (row[0], timer))
        def consume(iterator):
            collections.deque(iterator, maxlen=0)

        consume(iterate_csv(class_part_names, assert_time_column))


    def extract_speed_column(row):
        return float(row[1])


    def extract_start_time(row):
        nonlocal parts
        time = int(float(row[0]))
        parts.append([time])


    def extract_end_time(row):
        nonlocal parts
        time = int(float(row[0]))
        parts[-1].append(time)

    parts = []
    speed_profile = iterate_csv(class_part_names, extract_speed_column, extract_start_time, extract_end_time)

    return (speed_profile, parts)

def printSpeedList(timelist):
    print('(', end='\n    ')
    i = 0
    for v in timelist:
        i += 1
        print('%i, ' % v, end='\n    ' if (i % 16 == 0) else '')
    print('\n)\n')

if __name__ == '__main__':
    #print('values#: %s' % list(read_wltc_class('class3.2', assert_files=True)))

    import sys

    (speed_profile, parts) = read_wltc_class(*sys.argv[1:])
    speed_profile = list(speed_profile)
    parts = tuple(map(tuple, parts))

    print('values#  : %s\n\n' % len(speed_profile))
    print("'limits': {}, \n'cycle': ".format(parts))
    printSpeedList(speed_profile)

