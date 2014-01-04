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
'''wltcg module: Model json-all_schemas for WLTC gear-shift calculator.'''


def model_schema():
    '''The json-schema for input/output of the WLTC experiment.

    :return :dict:
    '''

    from textwrap import dedent

    schema = {
        '$schema': 'http://json-schema.org/draft-04/schema#',
        'title': 'Json-schema describing the input for a WLTC experiment.',
        'type': 'object', 'additionalproperties': False,
        'required': ['vehicle'],
        'properties': {
            'vehicle': {
                'title': 'vehicle model',
                'type': 'object', 'additionalproperties': False,
                'required': ['mass', 'p_rated', 'n_rated', 'n_idle', 'gear_ratios', 'resistance_coeffs', 'full_load_curve'],
                'description': 'The vehicle attributes required for generating the WLTC speed-profile downscaling and gear-shifts.',
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
                       'type': 'array', 'items': {'type': 'number'},
                       'minItems': 3,
                       'maxItems': 3,
                       'description': 'The 3 driving resistance coefficients f0, f1, f2 as defined in Annex 4, in N, N/(km/h), and N/(km/h)² respectively.',
                    },
                   'full_load_curve': {
                       'title': 'full load power curve',
                       'type': 'array',
                       'items': {
                           'type': 'array', 'additionalItems': False,
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
                }  #veh-props
            }, # veh
            'results': {}, #TODO: results model-schema
        },
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
                'type': 'object', 'additionalProperties': False,
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
        'type': 'object', 'additionalproperties': False,
        'required': ['classes', 'limits'],
        'properties': {
            'classes': {
                'type': 'object', 'additionalproperties': False,
                'required': ['class1', 'class2', 'class3a', 'class3b'],
                'properties': {
                    'class1': {'$ref': '#/definitions/class'},
                    'class2': {'$ref': '#/definitions/class'},
                    'class3a': {'$ref': '#/definitions/class'},
                    'class3b': {'$ref': '#/definitions/class'},
                }
            },
            'limits': {
            },
        },
        'definitions': {
            'class': {
                'title': 'WLTC class data',
                'type': 'object', 'additionalproperties': False,
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
                        'type': 'object', 'additionalproperties': False,
                        'required': ['accel_phase', 'deccel_phase', 'max_p_time', 'max_p_speed', 'max_p_accel'],
                        'properties': {
                            'accel_phase': {'type': 'array', 'items': {'type': 'integer'}},
                            'deccel_phase': {'type': 'array', 'items': {'type': 'integer'}},
                            'max_p_time': {'type': 'integer'},
                            'max_p_speed': {'type': 'number'}, # Km/h
                            'max_p_accel': {'type': 'number'}, # m/s2
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

