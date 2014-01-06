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
'''wltc.cycles.class2 module: WLTC-class data for gear-shift calculator.

Data below extracted from the specs and prepared with the followinf python scripts
found inside the source-distribution:

* ``./util/printwltcclass.py``

* ``./util/csvcolumns8to2.py``
'''
def class_data():
    data = {
        'parts': [[0, 589], [590, 1022], [1023, 1477], [1478, 1800]],
        'downscale': {
            'phases':       [1520, 1725, 1742],
            'p_max_values': [1574, 109.9, 0.36],    ## t, V(Km/h), Accel(m/s2)
            'factor_coeffs': [None,                 ## r0, a1, b1
                              [1, .6, -.6]],
            'v_max_split': 105,                     ## V (Km/h), >
        },
        'cycle': [
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 2, 4,
            7, 9, 11, 12, 13, 13, 13, 13, 12, 11, 8, 6, 3, 1, 0, 0,
            0, 0, 1, 2, 3, 4, 5, 6, 6, 7, 7, 8, 9, 10, 10, 11,
            12, 13, 14, 14, 14, 14, 14, 13, 13, 12, 11, 11, 10, 9, 9, 8,
            7, 4, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 2, 3, 4,
            5, 7, 9, 11, 13, 15, 16, 16, 17, 18, 20, 22, 23, 24, 25, 26,
            27, 28, 29, 30, 32, 33, 35, 37, 38, 39, 40, 40, 39, 36, 35, 32,
            31, 30, 29, 29, 29, 28, 26, 23, 20, 17, 15, 13, 13, 12, 12, 12,
            12, 12, 12, 12, 12, 13, 14, 16, 19, 21, 23, 23, 24, 24, 25, 25,
            26, 27, 28, 29, 32, 35, 37, 39, 40, 41, 42, 42, 43, 44, 45, 47,
            49, 50, 50, 50, 49, 49, 48, 48, 48, 48, 47, 47, 45, 43, 40, 38,
            36, 35, 35, 34, 34, 34, 34, 33, 33, 33, 33, 33, 33, 33, 33, 33,
            33, 32, 32, 32, 32, 32, 31, 31, 30, 30, 30, 30, 32, 33, 35, 37,
            38, 39, 40, 40, 41, 43, 44, 46, 47, 49, 49, 48, 48, 47, 47, 46,
            45, 45, 45, 45, 46, 46, 46, 46, 47, 47, 47, 47, 48, 48, 48, 48,
            47, 47, 46, 45, 43, 42, 40, 39, 37, 36, 35, 34, 33, 33, 32, 30,
            28, 25, 23, 20, 17, 15, 13, 13, 13, 15, 16, 17, 18, 18, 19, 19,
            19, 20, 20, 20, 18, 16, 14, 13, 12, 12, 12, 12, 12, 14, 16, 18,
            21, 25, 28, 31, 34, 34, 33, 31, 30, 29, 27, 27, 26, 25, 25, 25,
            24, 23, 23, 21, 20, 19, 18, 18, 17, 16, 15, 13, 11, 8, 6, 3,
            1, 0, 0, 0, 0, 0, 0, 0, 1, 3, 5, 8, 10, 12, 12, 13,
            14, 15, 16, 18, 19, 20, 22, 23, 25, 27, 28, 30, 31, 31, 30, 29,
            28, 27, 26, 26, 25, 24, 23, 22, 21, 20, 19, 18, 17, 16, 15, 14,
            14, 13, 13, 13, 12, 12, 11, 10, 9, 7, 5, 2, 1, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 1, 2, 5, 7, 10, 12, 15, 17, 19, 21, 24, 26, 28, 29, 31,
            33, 34, 36, 38, 39, 40, 41, 42, 43, 44, 45, 45, 44, 42, 39, 36,
            33, 30, 27, 23, 21, 19, 17, 16, 14, 13, 13, 16, 18, 20, 21, 22,
            23, 24, 25, 26, 26, 26, 27, 27, 30, 33, 35, 38, 40, 42, 44, 46,
            47, 48, 49, 50, 51, 51, 50, 47, 44, 41, 38, 35, 32, 29, 26, 23,
            20, 17, 14, 11, 8, 5, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 3, 6, 9, 11, 14, 16,
            18, 20, 23, 26, 30, 32, 34, 34, 33, 32, 30, 27, 25, 22, 20, 17,
            15, 13, 12, 13, 16, 18, 20, 23, 26, 29, 32, 34, 36, 38, 39, 40,
            41, 41, 42, 44, 45, 47, 48, 50, 52, 53, 55, 56, 58, 59, 61, 62,
            63, 63, 63, 62, 60, 58, 56, 55, 53, 52, 51, 51, 51, 50, 50, 50,
            51, 51, 52, 53, 53, 54, 55, 55, 56, 57, 57, 58, 59, 60, 61, 62,
            63, 64, 65, 66, 67, 68, 68, 69, 70, 70, 71, 71, 72, 72, 73, 74,
            74, 74, 73, 71, 70, 68, 67, 66, 64, 63, 62, 62, 61, 61, 60, 60,
            59, 59, 59, 59, 58, 58, 57, 56, 56, 55, 55, 55, 55, 54, 54, 54,
            54, 53, 53, 52, 51, 50, 48, 47, 45, 43, 40, 38, 35, 32, 30, 27,
            25, 23, 22, 20, 19, 18, 18, 17, 16, 15, 14, 14, 15, 17, 18, 19,
            20, 21, 21, 22, 23, 24, 24, 24, 24, 23, 23, 22, 21, 21, 20, 19,
            18, 16, 16, 14, 14, 13, 13, 12, 12, 12, 12, 12, 13, 13, 14, 15,
            17, 18, 20, 21, 23, 25, 27, 28, 30, 32, 33, 35, 36, 38, 39, 41,
            43, 45, 46, 48, 50, 52, 54, 55, 56, 57, 59, 59, 60, 61, 62, 62,
            62, 63, 63, 63, 64, 64, 64, 65, 66, 67, 67, 68, 69, 70, 70, 71,
            72, 73, 73, 74, 74, 74, 74, 74, 73, 72, 71, 71, 70, 69, 68, 68,
            67, 67, 65, 63, 61, 58, 55, 52, 50, 48, 47, 46, 46, 47, 47, 47,
            48, 48, 49, 50, 50, 51, 51, 51, 51, 51, 50, 49, 47, 46, 45, 44,
            43, 43, 43, 42, 41, 41, 40, 39, 39, 39, 39, 39, 40, 40, 41, 42,
            43, 44, 44, 45, 46, 47, 47, 48, 48, 49, 49, 49, 49, 49, 48, 48,
            47, 47, 46, 46, 46, 46, 46, 46, 46, 46, 46, 46, 46, 46, 46, 45,
            45, 44, 44, 43, 43, 43, 43, 43, 43, 43, 43, 43, 42, 42, 42, 42,
            42, 42, 42, 41, 41, 41, 41, 41, 40, 40, 39, 38, 37, 35, 33, 30,
            27, 25, 22, 18, 15, 12, 8, 6, 3, 1, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 1, 3, 5, 8, 11, 14, 17, 20, 22, 23, 24, 24, 25,
            25, 25, 25, 25, 25, 26, 26, 26, 26, 26, 27, 27, 28, 28, 29, 30,
            31, 33, 35, 37, 39, 40, 41, 42, 43, 43, 44, 44, 45, 45, 46, 46,
            47, 47, 48, 48, 49, 49, 50, 50, 50, 51, 51, 51, 51, 51, 51, 51,
            51, 51, 51, 51, 52, 52, 52, 52, 52, 53, 53, 53, 53, 53, 53, 53,
            53, 53, 55, 56, 58, 60, 63, 65, 66, 68, 70, 71, 72, 73, 74, 75,
            76, 77, 77, 78, 78, 78, 78, 78, 78, 78, 78, 79, 79, 79, 80, 80,
            80, 81, 81, 81, 81, 81, 80, 80, 79, 78, 76, 75, 74, 72, 71, 71,
            70, 71, 71, 72, 73, 74, 74, 75, 75, 75, 74, 73, 71, 69, 67, 65,
            63, 61, 59, 56, 54, 52, 50, 49, 48, 47, 46, 46, 46, 47, 48, 49,
            51, 53, 54, 56, 58, 60, 61, 62, 62, 62, 62, 63, 63, 63, 63, 63,
            63, 63, 63, 64, 64, 66, 67, 69, 71, 73, 74, 76, 77, 78, 79, 80,
            81, 82, 83, 83, 84, 84, 85, 85, 84, 84, 83, 82, 81, 80, 78, 77,
            76, 75, 74, 74, 73, 73, 72, 71, 70, 69, 67, 65, 63, 61, 59, 56,
            54, 52, 50, 49, 48, 47, 46, 46, 45, 43, 40, 38, 35, 32, 30, 29,
            30, 30, 30, 30, 31, 33, 33, 34, 35, 36, 37, 38, 39, 40, 40, 41,
            42, 43, 43, 44, 44, 45, 46, 47, 48, 49, 50, 51, 51, 52, 53, 55,
            56, 58, 60, 63, 65, 66, 68, 70, 71, 71, 72, 72, 73, 72, 71, 71,
            70, 70, 70, 69, 69, 68, 68, 67, 67, 67, 66, 65, 63, 60, 56, 52,
            48, 45, 41, 38, 36, 34, 34, 34, 36, 38, 41, 43, 46, 49, 51, 53,
            56, 57, 59, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 70, 70, 70,
            70, 70, 70, 70, 71, 71, 71, 71, 71, 71, 71, 71, 71, 71, 71, 71,
            71, 71, 71, 71, 72, 72, 72, 72, 73, 73, 73, 74, 74, 74, 73, 72,
            71, 70, 69, 68, 67, 66, 66, 66, 66, 66, 66, 66, 66, 66, 66, 66,
            67, 67, 67, 67, 67, 68, 68, 69, 69, 69, 69, 68, 68, 67, 67, 67,
            66, 66, 65, 64, 62, 60, 58, 56, 54, 53, 51, 49, 47, 45, 42, 39,
            36, 33, 29, 25, 22, 18, 15, 12, 9, 6, 3, 1, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 1, 2, 4, 6, 8, 10, 13, 15, 17,
            19, 21, 23, 25, 26, 28, 29, 31, 33, 35, 38, 40, 42, 43, 44, 45,
            45, 46, 47, 48, 49, 51, 52, 54, 55, 56, 57, 58, 59, 60, 60, 60,
            61, 61, 61, 61, 62, 63, 64, 65, 66, 68, 69, 70, 70, 71, 72, 73,
            74, 74, 75, 75, 76, 77, 78, 78, 79, 81, 82, 83, 85, 87, 88, 89,
            90, 91, 92, 93, 93, 94, 95, 95, 96, 97, 98, 98, 99, 100, 101, 101,
            102, 103, 105, 106, 107, 108, 109, 111, 112, 113, 114, 115, 116, 116, 117, 117,
            118, 118, 117, 117, 116, 115, 114, 113, 113, 112, 112, 111, 111, 111, 110, 110,
            109, 108, 107, 106, 106, 106, 106, 107, 107, 107, 108, 108, 109, 110, 110, 111,
            112, 112, 113, 113, 114, 114, 114, 114, 114, 114, 114, 114, 114, 114, 114, 115,
            115, 116, 117, 118, 118, 119, 119, 119, 119, 119, 119, 119, 118, 118, 118, 118,
            118, 118, 119, 119, 119, 119, 119, 119, 119, 120, 120, 120, 120, 120, 120, 120,
            120, 120, 120, 119, 119, 119, 119, 119, 119, 119, 119, 119, 119, 119, 119, 119,
            119, 119, 118, 118, 118, 119, 119, 119, 120, 120, 120, 120, 120, 121, 121, 121,
            121, 121, 121, 121, 121, 121, 121, 121, 120, 120, 120, 120, 120, 119, 119, 119,
            119, 120, 120, 120, 120, 121, 121, 121, 122, 122, 122, 122, 123, 123, 122, 122,
            121, 119, 118, 115, 113, 111, 108, 106, 104, 101, 98, 95, 93, 91, 90, 90,
            90, 90, 90, 90, 89, 89, 89, 89, 88, 88, 88, 87, 87, 86, 86, 85,
            85, 84, 83, 83, 82, 81, 81, 80, 78, 76, 74, 72, 69, 65, 62, 58,
            54, 50, 47, 43, 40, 37, 34, 31, 28, 25, 22, 18, 16, 13, 11, 8,
            6, 4, 2, 0, 0, 0, 0, 0, 0,
        ],
    }

    return data