#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# Copyright 2013-2014 ankostis@gmail.com
#
# This file is part of wltc.
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
'''wltc.instances module: The hierarchical data for the WLTC calculator (defaults, WLTC-data)
used by the Model and Experiments classes.
'''

from wltc.cycles import (class1, class2, class3)


def model_base():
    '''The base model for running a WLTC experiment.

    It contains some default values for the experiment (ie the default 'full-load-curve' for the vehicles).
    But note that it this model is not valid - you need to iverride its attributes.

    :return :json_tree: with the default values for the experiment.
    '''

    default_load_curve = [
        [   0.  ,    1.  ,    2.  ,    3.  ,    4.  ,    5.  ,    6.  ,
           7.  ,    8.  ,    9.  ,   10.  ,   11.  ,   12.  ,   13.  ,
          14.  ,   15.  ,   16.  ,   17.  ,   18.  ,   19.  ,   20.  ,
          21.  ,   22.  ,   23.  ,   24.  ,   25.  ,   26.  ,   27.  ,
          28.  ,   29.  ,   30.  ,   31.  ,   32.  ,   33.  ,   34.  ,
          35.  ,   36.  ,   37.  ,   38.  ,   39.  ,   40.  ,   41.  ,
          42.  ,   43.  ,   44.  ,   45.  ,   46.  ,   47.  ,   48.  ,
          49.  ,   50.  ,   51.  ,   52.  ,   53.  ,   54.  ,   55.  ,
          56.  ,   57.  ,   58.  ,   59.  ,   60.  ,   61.  ,   62.  ,
          63.  ,   64.  ,   65.  ,   66.  ,   67.  ,   68.  ,   69.  ,
          70.  ,   71.  ,   72.  ,   73.  ,   74.  ,   75.  ,   76.  ,
          77.  ,   78.  ,   79.  ,   80.  ,   81.  ,   82.  ,   83.  ,
          84.  ,   85.  ,   86.  ,   87.  ,   88.  ,   89.  ,   90.  ,
          91.  ,   92.  ,   93.  ,   94.  ,   95.  ,   96.  ,   97.  ,
          98.  ,   99.  ,  100.  ,  101.  ,  102.  ,  103.  ,  104.  ,
         105.  ,  106.  ,  107.  ,  108.  ,  109.  ,  110.  ,  111.  ,
         112.  ,  113.  ,  114.  ,  115.  ,  116.  ,  117.  ,  118.  ,
         119.  ,  120.  ],
       [   6.11,    7.63,    9.18,   10.75,   12.33,   13.93,   15.53,
          17.14,   18.75,   20.36,   21.97,   23.57,   25.16,   26.75,
          28.32,   29.88,   31.42,   32.95,   34.46,   35.96,   37.43,
          38.89,   40.32,   41.74,   43.13,   44.51,   45.86,   47.19,
          48.49,   49.78,   51.05,   52.29,   53.52,   54.72,   55.9 ,
          57.07,   58.21,   59.34,   60.45,   61.54,   62.61,   63.66,
          64.7 ,   65.73,   66.73,   67.73,   68.71,   69.67,   70.62,
          71.56,   72.49,   73.4 ,   74.3 ,   75.2 ,   76.07,   76.94,
          77.8 ,   78.65,   79.49,   80.31,   81.13,   81.94,   82.73,
          83.52,   84.29,   85.06,   85.81,   86.55,   87.28,   88.  ,
          88.7 ,   89.4 ,   90.07,   90.74,   91.39,   92.02,   92.63,
          93.23,   93.81,   94.38,   94.92,   95.44,   95.93,   96.41,
          96.86,   97.29,   97.69,   98.06,   98.4 ,   98.71,   98.99,
          99.24,   99.46,   99.64,   99.78,   99.89,   99.96,   99.99,
          99.98,  100.  ,  100.  ,   99.69,   99.5 ,   99.27,   98.99,
          98.66,   98.29,   97.86,   97.39,   96.86,   96.28,   95.65,
          94.97,   94.24,   93.45,   92.62,   91.73,   90.79,   89.8 ,
          88.75,   87.66
        ]
    ]

    instance = {
        'vehicle': {
            "mass":     None,
            "v_max":    None,
            "p_rated":  None,
            "n_rated":  None,
            "n_idle":   None,
            "n_min":    None,
            "gear_ratios":[],
            "resistance_coeffs":[],
            'full_load_curve': default_load_curve,
        },
        'params': {
            'v_stopped_threshold':      1,          # Km/h, <=
            'f_safety_margin':          0.9,
            'f_n_max':                  1.2,
            'f_n_min':                  0.125,
            'f_n_min_gear2':            [1.15, 0.03],
            'f_n_clutch_gear2':         0.9,
        }
    }

    return instance


def default_vehicle():
    return model_base()['vehicle']

def default_load_curve():
    return default_vehicle()['full_load_curve']


def results_base():
    instance = {
        'wltc_class': None,
        'v_target': [],
        'gears': [],
        'v_real': [],
        'downscale_factor': None,
        'driveability': None,
    }

    return instance


def wltc_data():
    '''The WLTC-data required to run an experiment (the class-cycles and their attributes)..

    :return :json_tree:
    '''

    ## See schemas for explainations.
    ##
    wltc_data = {
        'cycles': {
            'class1': class1.class_data(),
            'class2': class2.class_data(),
            'class3a': class3.class_data_a(),
            'class3b': class3.class_data_b(),
        },
        'classification': {
            'p_to_mass_class_limits':   [22, 34], #  W/kg, <=, choose class1/2/3
            'class3_split_velocity':    120,       # Km/h, <, choose class3a/3b
        }
    }

    return wltc_data


if __name__ == '__main__':
    import json
    print('Model: %s' % json.dumps(model_base(), indent=1))

