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

    ## PETROL:
    default_load_curve_petrol = [
        [float(x) for x in range(121)],
        [
            10,          11.10006881, 12.20013762, 13.30020643, 14.40027524, 15.50034405, 16.60041286, 17.70048167, 18.80055048, 19.90061929,
            21.0006881,  22.10075691, 23.20082572, 24.30089453, 25.40096334, 26.50103215, 27.50652776, 28.51202337, 29.51751898, 30.5230146,
            31.52851021, 32.3118101,  33.09510998, 33.87840987, 34.66170975, 35.44500964, 36.22830952, 37.01160941, 37.7949093,  38.57820918,
            39.36150907, 40.26837349, 41.17523791, 42.08210234, 42.98896676, 43.89583118, 44.80269561, 45.70956003, 46.61642445, 47.52328888,
            48.4301533,  49.38533685, 50.34052039, 51.29570394, 52.25088749, 53.20607103, 54.16125458, 55.11643813, 56.07162167, 57.02680522,
            57.98198877, 58.87347391, 59.76495905, 60.65644419, 61.54792933, 62.43941448, 63.33089962, 64.22238476, 65.1138699,  66.00535504,
            66.89684019, 67.81541498, 68.73398977, 69.65256456, 70.57113935, 71.48971415, 72.40828894, 73.32686373, 74.24543852, 75.16401331,
            76.08258811, 77.02695446, 77.97132082, 78.91568718, 79.86005353, 80.80441989, 81.74878625, 82.6931526,  83.63751896, 84.58188532,
            85.52625167, 86.39389792, 87.26154416, 88.12919041, 88.99683665, 89.86448289, 90.73212914, 91.59977538, 92.46742163, 93.33506787,
            94.20271412, 94.7824427,  95.36217129, 95.94189988, 96.52162847, 97.10135706, 97.68108565, 98.26081423, 98.84054282, 99.42027141,
            100,         99.55663073, 99.11326146, 98.66989219, 98.22652292, 97.78315366, 97.33978439, 96.89641512, 96.45304585, 96.00967658,
            95.56630731, 94.50967658, 93.45304585, 92.39641512, 91.33978439, 90.28315366, 89.22652292, 88.16989219, 87.11326146, 86.05663073,
            85
        ],
    ]

    ## DIESEL:
    default_load_curve_diesel = [
        [float(x) for x in range(121)],
        [
            10,          11.63276809, 13.26553619, 14.89830428, 16.53107237, 18.16384047, 19.79660856, 21.42937665, 23.06214475, 24.69491284,
            26.32768093, 27.95622138, 29.58476183, 31.21330227, 32.84184272, 34.47038317, 36.09892361, 37.72746406, 39.3560045,  40.98454495,
            42.6130854,  44.28914439, 45.96520339, 47.64126239, 49.31732138, 50.99338038, 52.66943937, 54.34549837, 56.02155737, 57.69761636,
            59.37367536, 60.77573069, 62.17778602, 63.57984135, 64.98189668, 66.38395201, 67.78600734, 69.18806266, 70.59011799, 71.99217332,
            73.39422865, 74.33451834, 75.27480804, 76.21509773, 77.15538742, 78.09567711, 79.0359668,  79.97625649, 80.91654618, 81.85683588,
            82.79712557, 83.35508239, 83.91303921, 84.47099603, 85.02895286, 85.58690968, 86.1448665,  86.70282332, 87.26078015, 87.81873697,
            88.37669379, 88.86173932, 89.34678485, 89.83183038, 90.31687591, 90.80192144, 91.28696697, 91.77201251, 92.25705804, 92.74210357,
            93.2271491,  93.55131403, 93.87547897, 94.19964391, 94.52380885, 94.84797378, 95.17213872, 95.49630366, 95.82046859, 96.14463353,
            96.46879847, 96.64506695, 96.82133544, 96.99760393, 97.17387242, 97.35014091, 97.52640939, 97.70267788, 97.87894637, 98.05521486,
            98.23148335, 98.40833501, 98.58518668, 98.76203834, 98.93889001, 99.11574167, 99.29259334, 99.469445,   99.64629667, 99.82314833,
            100,         98.87110621, 97.74221241, 96.61331862, 95.48442482, 94.35553103, 93.22663724, 92.09774344, 90.96884965, 89.83995585,
            88.71106206, 88.33995585, 87.96884965, 87.59774344, 87.22663724, 86.85553103, 86.48442482, 86.11331862, 85.74221241, 85.37110621,
            85,
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
            'full_load_curve': default_load_curve_diesel, # FIXME: Decide load_curtve by engine-type!
        },
        'params': {
            'v_stopped_threshold':      1,          # Km/h, <=
            'f_inertial':               1.1,
            'f_safety_margin':          0.9,
            'f_n_max':                  1.2,
            'f_n_min':                  0.125,
            'f_n_min_gear2':            0.9,
            'f_n_clutch_gear2':         [1.15, 0.03],
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
        'classes': {
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

