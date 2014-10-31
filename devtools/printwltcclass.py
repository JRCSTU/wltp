#! python
#-*- coding: utf-8 -*-
#
# Copyright 2013-2014 European Commission (JRC);
# Licensed under the EUPL (the 'Licence');
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at: http://ec.europa.eu/idabc/eupl
'''Build a python array from reading WLTC-data files and print it to be included as code.

It is used for preparing the WLTC variables for the default Model-data.
For example, to print (and optionally validate) the cycle for WLTC-Class 3.2, execute::

    python3 buildwltcclass.py class3.2 True

Or for printing all classes::

    python3 buildwltcclass.py

Then copy-paste the output of the program as a python-variable within the respective
 wltp.classes.classX.py modules.
'''

from __future__ import division, print_function, unicode_literals

import collections
import csv
import os, io


wltc_data_files = {
    'class1': [
        'class1-1-Low',
        'class1-2-Medium',
    ],
    'class2': [
        'class2-1-Low',
        'class2-2-Medium',
        'class2-3-High',
        'class2-4-ExtraHigh'
    ],
    'class3a': [
        'class3-1-Low',
        'class3-2a-Medium',
        'class3-3a-High',
        'class3-4-ExtraHigh'
    ],
    'class3b': [
        'class3-1-Low',
        'class3-2b-Medium',
        'class3-3b-High',
        'class3-4-ExtraHigh'
    ]
}


def read_wltc_class(wltc_class, assert_files = False):
    '''
    :argument: string: wltc_class: ( 'class1' | 'class2' | 'class3a| 'class3b' )
    :return :generator: with the speed_column floats
    '''

    def iterate_csv(fnames, yieldfun, beginfilefunc = None, endfilefunc = None):
        '''
        :argument: stringarray: fnames: the names of the resource-files
        :argument: function: yieldfunc: how to yield from each csv-row
        :return :generator with the results of the yieldfun(row)
        '''

        for fname in fnames:
            with io.open(fname, 'rb') as csvfile:  # @UndefinedVariable
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


def print_class_data(wltc_class, assert_files = False):
    '''Prepares and pretty-prints python variables with the data for the spec'ed WLTC-class.'''

    def print_speed_list(timelist):
        print('[', end='\n    ')
        i = 0
        for v in timelist:
            i += 1
            print('%.1f, ' % v, end='\n    ' if (i % 16 == 0) else '')
        print('\n]\n')

    (speed_profile, parts) = read_wltc_class(wltc_class, assert_files)
    speed_profile = list(speed_profile)

    print('\n\n>>> CLASS: %s\nvalues#  : %s\n' % (wltc_class, len(speed_profile)))
    print("'parts': {}, \n'cycle': ".format(parts))
    print_speed_list(speed_profile)




if __name__ == '__main__':
    #print('values#: %s' % list(read_wltc_class('class3.2', assert_files=True)))

    import sys

    if (len(sys.argv) > 1):
        print_class_data(*sys.argv[1:])
    else:
        for wltc_class in sorted(wltc_data_files):
            print_class_data(wltc_class, True)

