#!/usr/bin/env python
#
# Copyright 2013-2014 European Commission (JRC);
# Licensed under the EUPL (the 'Licence');
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at: http://ec.europa.eu/idabc/eupl
'''The hierarchical data and their schema for the WLTC calculator (defaults, WLTC-data) used by the Model and Experiments classes.

.. Attention:: The documentation of this core module has several issues and needs work.

'''

import numpy as np
from wltp.cycles import (class1, class2, class3)


def model_base():
    '''The base model for running a WLTC experiment.

    It contains some default values for the experiment (ie the default 'full-load-curve' for the vehicles).
    But note that it this model is not valid - you need to iverride its attributes.

    :return :json_tree: with the default values for the experiment.
    '''

    n_norm = np.arange(0.0, 1.21, 0.01)
    ## PETROL:
    default_load_curve_petrol = [
#        np.polyval([-1.0411, 1.3853, -0.5647, 1.1107, 0.0967], n_norm).tolist()
        n_norm.tolist(),
        ## Form Heinz-db
        [
        0.1       ,  0.11100069,  0.12200138,  0.13300206,  0.14400275,
        0.15500344,  0.16600413,  0.17700482,  0.1880055 ,  0.19900619,
        0.21000688,  0.22100757,  0.23200826,  0.24300895,  0.25400963,
        0.26501032,  0.27506528,  0.28512023,  0.29517519,  0.30523015,
        0.3152851 ,  0.3231181 ,  0.3309511 ,  0.3387841 ,  0.3466171 ,
        0.3544501 ,  0.3622831 ,  0.37011609,  0.37794909,  0.38578209,
        0.39361509,  0.40268373,  0.41175238,  0.42082102,  0.42988967,
        0.43895831,  0.44802696,  0.4570956 ,  0.46616424,  0.47523289,
        0.48430153,  0.49385337,  0.5034052 ,  0.51295704,  0.52250887,
        0.53206071,  0.54161255,  0.55116438,  0.56071622,  0.57026805,
        0.57981989,  0.58873474,  0.59764959,  0.60656444,  0.61547929,
        0.62439414,  0.633309  ,  0.64222385,  0.6511387 ,  0.66005355,
        0.6689684 ,  0.67815415,  0.6873399 ,  0.69652565,  0.70571139,
        0.71489714,  0.72408289,  0.73326864,  0.74245439,  0.75164013,
        0.76082588,  0.77026954,  0.77971321,  0.78915687,  0.79860054,
        0.8080442 ,  0.81748786,  0.82693153,  0.83637519,  0.84581885,
        0.85526252,  0.86393898,  0.87261544,  0.8812919 ,  0.88996837,
        0.89864483,  0.90732129,  0.91599775,  0.92467422,  0.93335068,
        0.94202714,  0.94782443,  0.95362171,  0.959419  ,  0.96521628,
        0.97101357,  0.97681086,  0.98260814,  0.98840543,  0.99420271,
        1.        ,  0.99556631,  0.99113261,  0.98669892,  0.98226523,
        0.97783154,  0.97339784,  0.96896415,  0.96453046,  0.96009677,
        0.95566307,  0.94509677,  0.93453046,  0.92396415,  0.91339784,
        0.90283154,  0.89226523,  0.88169892,  0.87113261,  0.86056631,
        0.85
        ]
    ]

    ## DIESEL:
    default_load_curve_diesel = [
#        np.polyval([-0.909, 1.9298, -2.2212, 2.088, 0.095], n_norm).tolist()
        n_norm.tolist(),
        ## Form Heinz-db
        [
         0.1       ,  0.11632768,  0.13265536,  0.14898304,  0.16531072,
        0.1816384 ,  0.19796609,  0.21429377,  0.23062145,  0.24694913,
        0.26327681,  0.27956221,  0.29584762,  0.31213302,  0.32841843,
        0.34470383,  0.36098924,  0.37727464,  0.39356004,  0.40984545,
        0.42613085,  0.44289144,  0.45965203,  0.47641262,  0.49317321,
        0.5099338 ,  0.52669439,  0.54345498,  0.56021557,  0.57697616,
        0.59373675,  0.60775731,  0.62177786,  0.63579841,  0.64981897,
        0.66383952,  0.67786007,  0.69188063,  0.70590118,  0.71992173,
        0.73394229,  0.74334518,  0.75274808,  0.76215098,  0.77155387,
        0.78095677,  0.79035967,  0.79976256,  0.80916546,  0.81856836,
        0.82797126,  0.83355082,  0.83913039,  0.84470996,  0.85028953,
        0.8558691 ,  0.86144867,  0.86702823,  0.8726078 ,  0.87818737,
        0.88376694,  0.88861739,  0.89346785,  0.8983183 ,  0.90316876,
        0.90801921,  0.91286967,  0.91772013,  0.92257058,  0.92742104,
        0.93227149,  0.93551314,  0.93875479,  0.94199644,  0.94523809,
        0.94847974,  0.95172139,  0.95496304,  0.95820469,  0.96144634,
        0.96468798,  0.96645067,  0.96821335,  0.96997604,  0.97173872,
        0.97350141,  0.97526409,  0.97702678,  0.97878946,  0.98055215,
        0.98231483,  0.98408335,  0.98585187,  0.98762038,  0.9893889 ,
        0.99115742,  0.99292593,  0.99469445,  0.99646297,  0.99823148,
        1.        ,  0.98871106,  0.97742212,  0.96613319,  0.95484425,
        0.94355531,  0.93226637,  0.92097743,  0.9096885 ,  0.89839956,
        0.88711062,  0.88339956,  0.8796885 ,  0.87597743,  0.87226637,
        0.86855531,  0.86484425,  0.86113319,  0.85742212,  0.85371106,
        0.85
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
            'full_load_curve': default_load_curve_petrol, # FIXME: Decide load_curtve by engine-type!
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


def merge(a, b, path=[]):
    ''''merges b into a'''

    from collections.abc import Mapping

    for key in b:
        bv = b[key]
        if key in a:
            av = a[key]
            if isinstance(av, Mapping) != isinstance(bv, Mapping):
                raise ValueError("Dict-values conflict at '%s'! a(%s) != b(%s)" %
                                ('/'.join(path + [str(key)]), type(av), type(bv)))
            elif av == bv:
                continue # same leaf value
            elif isinstance(av, Mapping):
                merge(av, bv, path + [str(key)])
                continue
        a[key] = bv
    return a

# works
# print(merge({1:{"a":"A"},2:{"b":"B"}}, {2:{"c":"C"},3:{"d":"D"}}))
# # has conflict
# merge({1:{"a":"A"},2:{"b":"B"}}, {1:{"a":"A"},2:{"b":"C"}})




def model_schema():
    ''':return: The json-schema(dict) for input/output of the WLTC experiment. '''

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
                'required': ['mass', 'v_max', 'p_rated', 'n_rated', 'n_idle', 'gear_ratios', 'resistance_coeffs', 'full_load_curve'],
                'description': 'The vehicle attributes required for generating the WLTC velocity-profile downscaling and gear-shifts.',
                'properties': {
                   'mass': {
                       'title': 'vehicle test mass',
                       '$ref': '#/definitions/positiveNumber',
                       'description': 'The test mass of the vehicle in kg.',
                    },
                   'v_max': {
                       'title': 'maximum vehicle velocity',
                       'type': ['integer', 'null'],
                       'minimum': 0,
                       'exclusiveMinimum': True,
                       'description': dedent('''
                           The maximum velocity as declared by the manufacturer.
                           If ommited, calculated as::
                               v_max = (n_rated * f_n_max (=1.2)) / gear_ratio[last]
                       '''),
                   },
                   'p_rated': {
                       'title': 'maximum rated power',
                       '$ref': '#/definitions/positiveNumber',
                       'description': 'The maximum rated engine power as declared by the manufacturer.',
                   },
                   'n_rated': {
                       'title': 'rated engine revolutions',
                       '$ref': '#/definitions/positiveNumber',
                       'description': dedent('''
                           The rated engine revolutions at which an engine develops its maximum power.
                           If the maximum power is developed over an engine revolutions range,
                           it is determined by the mean of this range.
                           This is called 's' in the specs.
                       '''),
                    },
                   'n_idle': {
                       'title': 'idling revolutions',
                       '$ref': '#/definitions/positiveNumber',
                       'description': 'The idling engine revolutions as defined of Annex 1.',
                    },
                   'n_min': {
                       'title': 'minimum engine revolutions',
                       'type': ['integer', 'null'],
                       'description': dedent('''
                        minimum engine revolutions for gears > 2 when the vehicle is in motion. The minimum value
                        is determined by the following equation::
                            n_min = n_idle + f_n_min(=0.125) * (n_rated - n_idle)
                        Higher values may be used if requested by the manufacturer, by setting this one.
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
                       'type': 'array', 'items': {'type': 'number'},
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
                                    The normalized engine revolutions, within [0.0, 0.15]::
                                        n_norm = (n - n_idle) / (n_rated  - n_idle)
                                    '''),
                               'type': 'array', 'additionalItems': False,
                               'maxItems': 360,
                               'minItems': 7,
                               'items': {
                                   'type': 'number',
                                   'minimum': 0.0,
                                   'exclusiveMinimum': False,
                                   'maximum': 1.5,
                                   'exclusiveMaximum': False,
                                },
                            },
                            {
                               'title': 'normalized full-load power curve',
                               'description': dedent('''
                                    The normalised values of the full-power load against the p_rated,
                                    within [0, 1]::
                                        p_norm = p / p_rated
                                '''),
                               'type': 'array', 'additionalItems': False,
                               'maxItems': 360,
                               'minItems': 7,
                               'items': {
                                   'type': 'number',
                                   'minimum': 0.0,
                                   'exclusiveMinimum': False,
                                   'maximum': 1.0,
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
                'title': 'experiment parameters',
                'type': 'object', 'additionalProperties': False,
                'required': [
                    'v_stopped_threshold',
                    'f_inertial',
                    'f_safety_margin',
                    'f_n_max',
                    'f_n_min',
                    'f_n_min_gear2',
                    'f_n_clutch_gear2',
                ],
                'properties': {
                    'v_stopped_threshold': {
                        'description': 'Velocity (Km/h) under which (<=) to idle gear-shift (Annex 2-3.3, p71).',
                        'type': [ 'number', 'null'],
                        'default': 1,
                    },
                    'f_inertial': {
                        'description': 'Inertial factor used for calculating required-power (Annex 2-3.1, p71).',
                        'type': [ 'number', 'null'],
                        'default': 1.1,
                    },
                    'f_safety_margin': {
                        'description': 'Safety-margin factor for load-curve due to transitional effects (Annex 2-3.3, p72).',
                        'type': [ 'number', 'null'],
                        'default': 0.9,
                    },
                    'f_n_max': {
                        'description': 'For each gear, N :< n_max = n_idle + f_n_max * n_range',
                        'type': [ 'number', 'null'],
                        'default': 1.2,
                    },
                    'f_n_min': {
                        'description': 'For each gear > 2, N :> n_min = n_idle + f_n_min * n_range (unless ``n_min`` overriden by manufacturer)',
                        'type': [ 'number', 'null'],
                        'default': 0.125,
                    },
                    'f_n_min_gear2': {
                        'description': 'Gear-2 is invalid when N :< f_n_min_gear2 * n_idle.',
                        'type': [ 'number', 'null'],
                        'default': 0.9,
                    },
                    'f_n_clutch_gear2': {
                        'description': dedent('''
                            A 2-value number-array(f1, f2) controlling when to clutch gear-2::
                                N < n_clutch_gear2 := max(f1 * n_idle, f2 * n_range + n_idle),
                            unless "clutched"...
                        '''),
                        'type': [ 'array', 'null'],
                        'default': [1.15, 0.03],
                    },
                    'wltc_class': {
                        'description': 'The name of the WLTC-class (found within WLTC-data/classes) as selected by the experiment.',
                        'type': 'string',
                    },
                    'f_downscale': {
                        'description': 'The downscaling-factor as calculated by the experiment (Annex 1-7.3, p68).',
                        'type': 'number',
                    },
                }
            },
            'cycle_run': {}, #TODO: results(cycle) model-schema.
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
        'required': ['classes', 'classification'],
        'properties': {
            'classes': {
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
                        'required': ['phases', 'p_max_values', 'factor_coeffs'],
                        'properties': {
                            'phases': {
                                'type': 'array', 'additionalItems': False,
                                'items': {
                                    'type': 'integer'
                                },
                                'maxItems': 3, 'minItems': 3,
                            },
                            'decel_phase': {
                                'type': 'array', 'additionalItems': False,
                                'items': {'type': 'integer'},
                                'maxItems': 2, 'minItems': 2,
                            },
                            'p_max_values': {
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


def validate_full_load_curve(flc, f_n_max):
    if (min(flc[0]) > 0):
        raise ValueError('The full_load_curve must begin at least from 0%%, not from %f%%!' % min(flc[0]))
    max_x_limit = f_n_max
    if (max(flc[0]) < max_x_limit):
        raise ValueError('The full_load_curve must finish at least on f_n_max(%f%%), not on %f%%!' % (max_x_limit, max(flc[0])))


if __name__ == '__main__':
    import json
    print('Model: %s' % json.dumps([model_schema(), wltc_schema()], indent=1))
    print('Model: %s' % json.dumps(model_base(), indent=1))

