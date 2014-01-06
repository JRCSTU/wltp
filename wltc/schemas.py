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
'''wltc module: Model json-all_schemas for WLTC gear-shift calculator.'''


def model_schema():
    '''The json-schema for input/output of the WLTC experiment.

    :return :dict:
    '''

    from textwrap import dedent

    schema = {
        '$schema': 'http://json-schema.org/draft-04/schema#',
        'title': 'Json-schema describing the input for a WLTC experiment.',
        'type': 'object', 'additionalProperties': False,
        'required': ['vehicle'],
        'properties': {
            'vehicle': {
                'title': 'vehicle model',
                'type': 'object', 'additionalProperties': False,
                'required': ['mass', 'p_rated', 'n_rated', 'n_idle', 'gear_ratios', 'resistance_coeffs', 'full_load_curve'],
                'description': 'The vehicle attributes required for generating the WLTC velocity-profile downscaling and gear-shifts.',
                'properties': {
                   'mass': {
                       'title': 'vehicle test mass',
                       '$ref': '#/definitions/positiveInteger',
                       'description': 'The test mass of the vehicle in kg.',
                    },
                   'p_rated': {
                       'title': 'maximum rated power',
                       '$ref': '#/definitions/positiveNumber',
                       'description': 'The maximum rated engine power as declared by the manufacturer.',
                   },
                   'n_rated': {
                       'title': 'rated engine revolutions',
                       '$ref': '#/definitions/positiveInteger',
                       'description': dedent('''
                           The rated engine revolutions at which an engine develops its maximum power.
                           If the maximum power is developed over an engine revolutions range,
                           it is determined by the mean of this range.
                           This is called 's' in the specs.
                       '''),
                    },
                   'n_idle': {
                       'title': 'idling revolutions',
                       '$ref': '#/definitions/positiveInteger',
                       'description': 'The idling engine revolutions as defined of Annex 1.',
                    },
                   'n_min': {
                       'title': 'minimum engine revolutions',
                       '$ref': '#/definitions/positiveInteger',
                       'description': dedent('''
                        minimum engine revolutions for gears > 2 when the vehicle is in motion. The minimum value
                        is determined by the following equation:
                            n_min = n_idle + 0.125 * (n_rated - n_idle)
                        Higher values may be used if requested by the manufacturer.
                       '''),
                    },
                   'gear_ratios': {
                       'title': 'gear ratios',
                       '$ref': '#/definitions/positiveNumbers',
                       'maxItems': 24,
                       'minItems': 3,
                       'description':
                       'An array with the gear-ratios obtained by dividing engine-revolutions (1/min) by vehicle-velocity (km/h).',
                    },
                   'resistance_coeffs': {
                       'title': 'driving resistance coefficients',
                       'type': 'array', 'items': {'type': 'number', 'minimum': 0},
                       'minItems': 3,
                       'maxItems': 3,
                       'description': 'The 3 driving resistance coefficients f0, f1, f2 as defined in Annex 4, in N, N/(km/h), and N/(km/h)² respectively.',
                    },
                   'full_load_curve': {
                       'title': 'full load power curve',
                       'type': 'array',
                       'items': [
                            {
                               'title': 'normalized engine revolutions',
                               'description': dedent('''
                                    The normalized engine revolutions, within [0%, 120%]::
                                        n_norm = 100 * (n - n_idle) / (n_rated  - n_idle)
                                    '''),
                               'type': 'array', 'additionalItems': False,
                               'maxItems': 360,
                               'minItems': 7,
                               'items': {
                                   'type': 'number',
                                   'minimum': 0,
                                   'exclusiveMinimum': False,
                                   'maximum': 120,
                                   'exclusiveMaximum': False,
                                },
                            },
                            {
                               'title': 'normalized full-load power curve',
                               'description': dedent('''
                                    The normalised values of the full-power load against the p_rated,
                                    within [0%, 100%]::
                                        p_norm = 100 * p / p_rated
                                '''),
                               'type': 'array', 'additionalItems': False,
                               'maxItems': 360,
                               'minItems': 7,
                               'items': {
                                   'minimum': -10,
                                   'exclusiveMinimum': False,
                                   'maximum': 110,
                                   'exclusiveMaximum': False,
                                }
                            },
                        ],
                       'description': dedent('''
                            A 2-dimensional array holding the full load power curve in 2 rows
                            Example::
                                [
                                    [ 0, 10, 20, 30, 40, 50, 60, 70. 80, 90 100, 110, 120 ],
                                    [ 6.11, 21.97, 37.43, 51.05, 62.61, 72.49, 81.13, 88.7, 94.92, 98.99, 100., 96.28, 87.66 ]
                                ]

                       '''),
                    },
                }  #veh-props
            }, # veh
            'params': {
                'type': 'object', 'additionalProperties': False,
                'required': [
                    'v_stopped_threshold',
                    'f_safety_margin',
                    'f_n_max',
                    'f_n_min',
                    'f1_n_min_gear2',
                    'f2_n_min_gear2',
                    'f_n_clutch_gear2',
                ],
                'properties': {
                    'v_stopped_threshold': {
                        'description': 'Velocity (Km/h) under which (<=) to idle gear-shift (Annex 2-3.3, p71).',
                        'type': 'number',
                        'default': 1,
                    },
                    'f_safety_margin': {
                        'description': 'Safety-margin factor for load-curve due to transitional effects (Annex 2-3.3, p72.',
                        'type': 'number',
                        'default': 0.9,
                    },
                    'f_n_max': {},
                    'f_n_min': {},
                    'f1_n_min_gear2': {},
                    'f2_n_min_gear2': {},
                    'f_n_clutch_gear2': {},
                }
            },
            'results': {}, #TODO: results model-schema
        },
        'definitions': {
            'positiveInteger': {
                'type': 'integer',
                'minimum': 0,
                'exclusiveMinimum': True,
            },
            'positiveNumber': {
                'type': 'number',
                'minimum': 0,
                'exclusiveMinimum': True,
            },
            'positiveIntegers': {
                'type': 'array',
               'items': { '$ref': '#/definitions/positiveInteger' },
            },
            'positiveNumbers': {
                'type': 'array',
               'items': { '$ref': '#/definitions/positiveNumber' },
            },
            'mergeableArray': {
                'type': 'object', '': False,
                'required': ['$merge', '$list'],
                'properties': {
                    '$merge': {
                        'enum': ['merge', 'replace', 'append_head', 'append_tail', 'overwrite_head', 'overwrite_tail'],
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

    return schema

def wltc_schema():
    '''The json-schema for the WLTC-data required to run a WLTC experiment.

    :return :dict:
    '''

    schema = {
        '$schema': 'http://json-schema.org/draft-04/schema#',
        'title': 'WLTC data',
        'type': 'object', 'additionalProperties': False,
        'required': ['cycles', 'classification'],
        'properties': {
            'cycles': {
                'type': 'object', 'additionalProperties': False,
                'required': ['class1', 'class2', 'class3a', 'class3b'],
                'properties': {
                    'class1': {'$ref': '#/definitions/class'},
                    'class2': {'$ref': '#/definitions/class'},
                    'class3a': {'$ref': '#/definitions/class'},
                    'class3b': {'$ref': '#/definitions/class'},
                }
            },
            'classification': {
                'type': 'object', 'additionalProperties': False,
                'required': ['p_to_mass_class_limits', 'class3_split_velocity'],
                'properties': {
                    'p_to_mass_class_limits': {
                        'description': 'Power_to_unladen-mass ratio (W/kg) used to select class (Annex 1, p19).',
                        'type': 'array',
                        'default': [22, 34],
                    },
                    'class3_split_velocity': {
                        'description': 'Velocity (Km/h) under which (<) version-B from class3 is selected (Annex 1, p19).',
                        'type': 'integer',
                        'default':120,
                    },
                }
            },
        },
        'definitions': {
            'class': {
                'title': 'WLTC class data',
                'type': 'object', 'additionalProperties': False,
                'required': ['parts', 'downscale', 'cycle'],
                'properties': {
                    'parts': {
                        'type': 'array', 'items': {
                            'type': 'array', 'items': {'type': 'integer',},
                            'minItems': 2,
                            'maxItems': 2,
                        }
                    },
                    'downscale': {
                        'type': 'object', 'additionalProperties': False,
                        'required': ['phases', 'max_p_values', 'factor_coeffs'],
                        'properties': {
                            'phases': {
                                'type': 'array', 'additionalItems': False,
                                'items': {
                                    'type': 'array', 'additionalItems': False,
                                    'items': {
                                        'type': 'integer'
                                    },
                                    'maxItems': 2, 'minItems': 2,
                                },
                                'maxItems': 2, 'minItems': 2,
                            },
                            'deccel_phase': {
                                'type': 'array', 'additionalItems': False,
                                'items': {'type': 'integer'},
                                'maxItems': 2, 'minItems': 2,
                            },
                            'max_p_values': {
                                'type': 'array', 'additionalItems': False,
                                'items': { 'type': 'number'},
                                'maxItems': 3, 'minItems': 3,
                            },
                            'factor_coeffs': {
                                'type': 'array',
                            },
                            'v_max_split': {
                                'type': 'number',
                            },
                        }
                    },
                    'cycle': {
                        'type': 'array',
                        'items': {'type': 'number',},
                        'minItems': 906, # class1's length
                    }
                },
            }
        }
    }

    return schema


def model_validator():
    from jsonschema import Draft4Validator
    schema = model_schema()
    return Draft4Validator(schema)

def wltc_validator():
    from jsonschema import Draft4Validator
    schema = wltc_schema()
    return Draft4Validator(schema)



if __name__ == '__main__':
    import json
    print('Model: %s' % json.dumps([model_schema(), wltc_schema()], indent=1))

