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
wltcg module: WLTC gear-shift calculator

Vars
----
``default_load_curve``: The normalized full-load-power-curve to use when not explicetely defined by the model.

``model_schema``: Describes the vehicle and cycle data for running WLTC experiment.
'''


from jsonschema import validators, Draft4Validator
import jsonschema
from jsonschema.compat import iteritems as _iteritems
import operator
import pkg_resources
import sys
from textwrap import dedent

from ._version import __version_info__


__author__ = "ankostis@gmail.com"
__copyright__ = "Copyright (C) 2013 ankostis"
__license__ = "AGPLv3"
__version__ = '.'.join(__version_info__)



default_load_curve = [
    [0, 6.11], [1, 7.63], [2, 9.18], [3, 10.75], [4, 12.33], [5, 13.93], [6, 15.53], [7, 17.14], [8, 18.75],
    [9, 20.36], [10, 21.97], [11, 23.57], [12, 25.16], [13, 26.75], [14, 28.32], [15, 29.88], [16, 31.42],
    [17, 32.95], [18, 34.46], [19, 35.96], [20, 37.43], [21, 38.89], [22, 40.32], [23, 41.74], [24, 43.13],
    [25, 44.51], [26, 45.86], [27, 47.19], [28, 48.49], [29, 49.78], [30, 51.05], [31, 52.29], [32, 53.52],
    [33, 54.72], [34, 55.90], [35, 57.07], [36, 58.21], [37, 59.34], [38, 60.45], [39, 61.54], [40, 62.61],
    [41, 63.66], [42, 64.70], [43, 65.73], [44, 66.73], [45, 67.73], [46, 68.71], [47, 69.67], [48, 70.62],
    [49, 71.56], [50, 72.49], [51, 73.40], [52, 74.30], [53, 75.20], [54, 76.07], [55, 76.94], [56, 77.80],
    [57, 78.65], [58, 79.49], [59, 80.31], [60, 81.13], [61, 81.94], [62, 82.73], [63, 83.52], [64, 84.29],
    [65, 85.06], [66, 85.81], [67, 86.55], [68, 87.28], [69, 88.00], [70, 88.70], [71, 89.40], [72, 90.07],
    [73, 90.74], [74, 91.39], [75, 92.02], [76, 92.63], [77, 93.23], [78, 93.81], [79, 94.38], [80, 94.92],
    [81, 95.44], [82, 95.93], [83, 96.41], [84, 96.86], [85, 97.29], [86, 97.69], [87, 98.06], [88, 98.40],
    [89, 98.71], [90, 98.99], [91, 99.24], [92, 99.46], [93, 99.64], [94, 99.78], [95, 99.89], [96, 99.96],
    [97, 99.99], [98, 99.98], [99, 100.00], [100, 100.00], [101, 99.69], [102, 99.50], [103, 99.27],
    [104, 98.99], [105, 98.66], [106, 98.29], [107, 97.86], [108, 97.39], [109, 96.86], [110, 96.28],
    [111, 95.65], [112, 94.97], [113, 94.24], [114, 93.45], [115, 92.62], [116, 91.73], [117, 90.79],
    [118, 89.80], [119, 88.75], [120, 87.66]
]

model_base = {
    "mass": None,
    "p_rated":None,
    "n_rated":None,
    "p_max":None,
    "n_idle":None,
    "n_min":None,
    "gear_ratios":[],
    "resistance_coeffs":[],
    'full_load_curve': default_load_curve,
}


model_schema = {
            '$schema': 'http://json-schema.org/draft-04/schema#',
            'title': 'Json-schema describing the vehicle attributes used to generate WLTC gear-shifts profile.',
            'type': 'object',
            'properties': {
               'mass': {
                   'title': 'vehicle mass',
                   '$ref': '#/definitions/positiveInteger',
                   'description': 'The test mass of the vehicle in kg.',
                },
               'p_rated': {
                   'title': 'maximum rated power',
                   '$ref': '#/definitions/positiveInteger',
                   'description': 'The maximum rated engine power as declared by the manufacturer.',
               },
               'n_rated': {
                   'title': 'rated engine speed',
                   '$ref': '#/definitions/positiveInteger',
                   'description': dedent('''
                       The rated engine speed at which an engine develops its maximum power.
                       If the maximum power is developed over an engine speed range,
                       it is determined by the mean of this range.
                       This is called 's' in the specs.
                   '''),
                },
               'n_idle': {
                   'title': 'idling speed',
                   '$ref': '#/definitions/positiveInteger',
                   'description': 'The idling speed as defined of Annex 1.',
                },
               'n_min': {
                   'title': 'minimum engine speed',
                   '$ref': '#/definitions/positiveInteger',
                   'description': dedent('''
                    minimum engine speed for gears > 2 when the vehicle is in motion. The minimum value
                    is determined by the following equation:
                        n_min = n_idle + 0.125 * (n_rated - n_idle)
                    Higher values may be used if requested by the manufacturer.
                   '''),
                },
               'gear_ratios': {
                   'title': 'gear ratios',
                   '$ref': '#/definitions/positiveIntegers',
                   'maxItems': 24,
                   'minItems': 3,
                   'description':
                   'An array with the gear-ratios obtained by dividing engine-revolutions (1/min) by vehicle-speed (km/h).',
                },
               'resistance_coeffs': {
                   'title': 'driving resistance coefficients',
                   '$ref': '#/definitions/positiveIntegers',
                   'description': 'The 3 driving resistance coefficients f0, f1, f2 as defined in Annex 4, in N, N/(km/h), and N/(km/h)² respectively.',
                },
               'full_load_curve': {
                   'title': 'full load power curve',
                   'type': 'array',
                   'default': default_load_curve,
                   'items': {
                       'type': 'array',
                       'items': [
                            {
                                'title': 'n_norm',
                                'description': 'A percent of n_rated.',
                                'type': 'integer',
                                'minimum': 0,
                                'maximum': 150,
                            },
                            {
                                'title': 'p_norm',
                                'description': 'A percent of p_rated.',
                                'type': 'number',
                                'minimum': 0,
                                'exclusiveMinimum': True,
                                'maximum': 100,
                                'exclusiveMaximum': False,
                            }
                        ],
                       'additionalItems': False,
                    },
                   'maxItems': 150,
                   'minItems': 7,
                   'description': dedent('''
                        A 2-dimensional array holding the full load power curve
                        where column-1 is the normalized engine revolutions:
                            n_norm = 100 * (n - n_idle) / (n_rated  - n_idle)
                        and column-2 is the normalised power against the p_rated:
                            p_norm = 100 * p / p_rated
                   '''),
                },
            }, # props
            'required': ['mass', 'p_rated', 'n_rated', 'n_idle', 'gear_ratios', 'resistance_coeffs'],
            'definitions': {
                'positiveInteger': {
                    'type': 'integer',
                    'minimum': 0,
                    'exclusiveMinimum': True,
                },
                'positiveIntegers': {
                    'type': 'array',
                   'items': { '$ref': '#/definitions/positiveInteger' },
                },
                'mergeableArray': {
                    'type': 'object',
                    'required': ['$merge', '$list'],
                    'additionalProperties': False,
                    'properties': {
                        '$merge': {
                            'enum': ['merge', 'replace', 'append_tail', 'append_tail', 'overwrite_head', 'overwrite_tail'],
                            'description': dedent('''
                                merge       := appends any non-existent elements
                                replace     := (default) all items replaced
                            '''),
                        },
                        '$list': {
                            'type': 'array',
                        }
                    },
                },
                'mergeableObject': {
                    'type': 'object',
                    'additionalProperties': True,
                    'properties': {
                        '$merge': {
                            'type': 'boolean',
                            'description': dedent('''
                                true    := (default) merge properties
                                false   := replace properties
                            '''),
                        },
                    },
                },
            }
        }



## From http://python-jsonschema.readthedocs.org/en/latest/faq/
#
def extend_with_default(validator_class):
    '''A jsonschema validator that sets missing defaults.

    Not from http://python-jsonschema.readthedocs.org/en/latest/faq/
    '''

    properties_validator = validator_class.VALIDATORS["properties"]

    def set_defaults(validator, properties, instance, schema):
        for error in properties_validator(
            validator, properties, instance, schema,
        ):
            yield error

        for prop, subschema in _iteritems(properties):
            if "default" in subschema:
                instance.setdefault(prop, subschema["default"])

    return validators.extend(  # @UndefinedVariable
        validator_class, {"properties" : set_defaults},
    )


_ValidatorWithDefaults = extend_with_default(Draft4Validator)
_model_validator = _ValidatorWithDefaults(model_schema)
def get_model_validator():
    '''A jsonschema.validator for the vehicle and cycle data specifying a WLTC experiment.'''
    return _model_validator
    ## TODO: Is json-validator multithreaded?



__all__ = ['wltc_cycles', 'default_load_curve', 'model_schema', 'get_model_validator', 'Experiment']

