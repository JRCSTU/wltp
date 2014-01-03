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
'''
wltcg module: Model for WLTC gear-shift calculator

Vars
----
``default_load_curve``: The normalized full-load-power-curve to use when not explicetely defined by the model.

``model_schema``: Describes the vehicle and cycle data for running WLTC experiment.
'''

wltc_data_files = {
    'class1': [],
    'class2': [],
    'class3.1': [
        'class3-1-Low-1',
        'class3-2-Medium-2',
        'class3-3-High-2',
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
    import pkg_resources


    def iterate_csv_from_resources(fnames, yieldfun):
        '''
        :argument: stringarray: fnames: the names of the resource-files
        :argument: function: yieldfunc: how to yield from each csv-row
        :return :generator with the results of the yieldfun(row)
        '''

        for fname in fnames:
            with pkg_resources.resource_stream('wltcg', fname) as csvfile:  # @UndefinedVariable
                reader = csv.reader(io.TextIOWrapper(csvfile))
                for row in reader:
                    try:
                        yield yieldfun(row)
                    except csv.Error as e:
                        print('file {}, line {}: {}'.format(fname, reader.line_num, e))
                        raise


    def extract_speed_column(row):
        return float(row[1])




    if (wltc_class not in wltc_data_files):
        raise ValueError('Unknown WLTC-class(%s)!  One of (%s) expected.' %
                         (wltc_class, ', '.join(sorted(wltc_data_files.keys()))))

    class_part_names = ['data/%s.csv' % pname for pname in wltc_data_files[wltc_class]]
    if (assert_files):
        timer = -1;
        def assert_time_column(row):
            nonlocal timer
            timer += 1
            if (float(row[0]) != timer):
                raise AssertionError('index-col(%s) != expected(%s)' % (row[0], timer))
        def consume(iterator):
            collections.deque(iterator, maxlen=0)

        consume(iterate_csv_from_resources(class_part_names, assert_time_column))

    return iterate_csv_from_resources(class_part_names, extract_speed_column)


if __name__ == '__main__':
    print('values#: %i' % len(list(read_wltc_class('class3.2', assert_files=True))))

