#! python
#-*- coding: utf-8 -*-
#
# Copyright 2013-2014 European Commission (JRC);
# Licensed under the EUPL (the 'Licence');
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at: http://ec.europa.eu/idabc/eupl
"""
Defines the schema, defaults and validation operations for the data consumed and produced by the :class:`~wltp.experiment.Experiment`.

The model-instance is managed by :class:`pandel.Pandel`.

Example-code to get WLTP-data::

    from wltp.model  import _get_wltc_data
    cycle_data = _get_wltc_data()
    
    for cls, value in cycle_data['classes'].items():
        cycle = np.array(value['cycle'])
        print('%s: \n%s' % (cls, cycle))
"""

from __future__ import division, print_function, unicode_literals

from collections import Mapping, Sized
import json
import logging
from textwrap import dedent

from jsonschema import (RefResolver, ValidationError)
import jsonschema
from numpy import ndarray
from pandas.core.common import PandasError
from pandas.core.generic import NDFrame
from six import string_types
from wltp.cycles import (class1, class2, class3)
from wltp.pandel import PandelVisitor

import itertools as it
import numpy as np
import operator as ops
import pandas as pd


log = logging.getLogger(__name__)

def make_json_defaulter(pd_method):
    def defaulter(o):
        if (isinstance(o, np.ndarray)):
            s = o.tolist()
        elif (isinstance(o, NDFrame)):
            if pd_method is None:
                s = json.loads(pd.DataFrame.to_json(o))
            else:
                method = ops.methodcaller(pd_method)
                s = '%s:%s'%(type(o).__name__, method(o))
        else:
            s =repr(o)
        return s

    return defaulter

def json_dumps(obj, pd_method=None, **kwargs):
    return json.dumps(obj, default=make_json_defaulter(pd_method), **kwargs)
def json_dump(obj, fp, pd_method=None, **kwargs):
    json.dump(obj, fp, default=make_json_defaulter(pd_method), **kwargs)

def _get_model_base():
    """The base model for running a WLTC experiment.

    It contains some default values for the experiment (ie the default 'full-load-curve' for the vehicles).
    But note that it this model is not valid - you need to override its attributes.

    :return: a tree with the default values for the experiment.
    """

    ## Form Heinz-db
    petrol = [
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
    ## Form Heinz-db
    diesel = [
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

    n_norm = np.arange(0.0, 1.21, 0.01)
#        petrol = np.polyval([-1.0411, 1.3853, -0.5647, 1.1107, 0.0967], n_norm).tolist()
#        diesel = np.polyval([-0.909, 1.9298, -2.2212, 2.088, 0.095], n_norm).tolist()
    default_load_curve = {
        'n_norm': n_norm,
        'p_norm': petrol
    }

    instance = {
        'vehicle': {
            "unladen_mass": None,
            "test_mass":    None,
            "v_max":    None,
            "p_rated":  None,
            "n_rated":  None,
            "n_idle":   None,
            "n_min":    None,
            "gear_ratios":[],
            'full_load_curve': default_load_curve, # FIXME: Decide load_curve by engine-type!
        },
        'params': {
            'resistance_coeffs_regression_curves': [
                [1.40E-01, 7.86E-01],
                [2.75E-05, -3.29E-02],
                [1.11E-05, 2.03E-02]
            ],
            'f_downscale_threshold':    0.01,
            'driver_mass':              75,         # kg
            'v_stopped_threshold':      1,          # km/h, <=
            'f_inertial':               1.1,
            'f_safety_margin':          0.9,
            'f_n_max':                  1.2,
            'f_n_min':                  0.125,
            'f_n_min_gear2':            0.9,
            'f_n_clutch_gear2':         [1.15, 0.03],

            'wltc_data':                _get_wltc_data(),
        }
    }

    return instance


def default_vehicle():
    return _get_model_base()['vehicle']

def default_load_curve():
    return default_vehicle()['full_load_curve']


def _get_wltc_data():
    """The WLTC-data required to run an experiment (the class-cycles and their attributes)..

    Prefer to access wltc-data through :samp:`{model}['wltc_data']`.

    :return: a tree
    """

    ## See schemas for explainations.
    ##
    wltc_data = {
        'classes': {
            'class1': class1.class_data(),
            'class2': class2.class_data(),
            'class3a': class3.class_data_a(),
            'class3b': class3.class_data_b(),
        },
    }

    return wltc_data


_url_model = '/model'
_url_wltc = '/wltc'
def _get_model_schema(additional_properties=False, for_prevalidation=False):
    """
    :param bool additional_properties: when False, 4rd-step(validation) will scream on any non-schema property found.
    :return: The json-schema(dict) for input/output of the WLTC experiment.
    """

    schema = {
        '$schema': 'http://json-schema.org/draft-04/schema#',
        'id': _url_model,
        'title': 'Json-schema describing the input for a WLTC experiment.',
        'type': 'object', 'additionalProperties': additional_properties,
        'required': ['vehicle'],
        'properties': {
            'vehicle': {
                'title': 'vehicle model',
                'type': 'object', 'additionalProperties': additional_properties,
                'required': ['test_mass', 'v_max', 'p_rated', 'n_rated', 'n_idle', 'gear_ratios', 'full_load_curve'],
                'description': 'The vehicle attributes required for generating the WLTC velocity-profile downscaling and gear-shifts.',
                'properties': {
                    'id': {
                        'title': 'Any identifier for the object',
                        'type': ['integer', 'string'],
                    },
                    'unladen_mass': {
                        'title': 'vehicle unladen mass',
                        'type': ['number', 'null'],
                        'minimum': 0,
                        'exclusiveMinimum': True,
                        'description': dedent("""
                            The mass (kg) of the vehicle without the driver, used to decide its class,
                            as defined in Annex-4
                            """),
                    },
                    'test_mass': {
                        'title': 'vehicle test mass',
                        '$ref': '#/definitions/positiveNumber',
                        'description': dedent("""
                            The test mass of the vehicle used in all calculations (kg),
                            as defined in Annex 4.2.1.3.1, pg 94.
                           """),
                    },
                    'v_max': {
                        'title': 'maximum vehicle velocity',
                        'type': ['integer', 'null'],
                        'minimum': 0,
                        'exclusiveMinimum': True,
                        'description': dedent("""
                            The maximum velocity as declared by the manufacturer.
                            If ommited, calculated as:

                                v_max = (n_rated * f_n_max (=1.2)) / gear_ratio[last]
                        """),
                    },
                    'p_rated': {
                        'title': 'maximum rated power',
                        '$ref': '#/definitions/positiveNumber',
                        'description': 'The maximum rated engine power (kW) as declared by the manufacturer.',
                    },
                    'n_rated': {
                        'title': 'rated engine revolutions',
                        '$ref': '#/definitions/positiveNumber',
                        'description': dedent("""
                            The rated engine revolutions at which an engine develops its maximum power.
                            If the maximum power is developed over an engine revolutions range,
                            it is determined by the mean of this range.
                            This is called 's' in the specs.
                        """),
                    },
                    'n_idle': {
                        'title': 'idling revolutions',
                        '$ref': '#/definitions/positiveNumber',
                        'description': 'The idling engine revolutions (Annex 1).',
                    },
                    'n_min': {
                        'title': 'minimum engine revolutions',
                        'type': ['array', 'integer', 'null'],
                        'description': dedent("""
                        Either a number with the minimum engine revolutions for gears > 2 when the vehicle is in motion,
                        or an array with the exact `n_min` for each gear (array must have length equal to gears).
                        
                        If unspecified, the minimum `n` for gears > 2 is determined by the following equation:
                            n_min = n_idle + f_n_min(=0.125) * (n_rated - n_idle)
                        Higher values may be used if requested by the manufacturer, by setting this one.
                       """),
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
                        'type': ['null', 'array'],
                        'items': {'type': 'number'},
                        'minItems': 3,
                        'maxItems': 3,
                        'description': dedent("""
                            The 3 driving resistance coefficients f0, f1, f2,
                            in N, N/(km/h), and N/(km/h)² respectively (Annex 4).

                            If not specified, they are determined based on ``test_mass`` from
                            a pre-calculated regression curve:

                                f0 = a00 * test_mass + a01,
                                f1 = a10 * test_mass + a11,
                                f2 = a20 * test_mass + a21,

                            where ``a00, ..., a22`` specified in ``/params``.
                        """),
                    },
                    'full_load_curve': {
                        'title': 'full load power curve',
                        'description': dedent("""
                            An array/dict/dataframe holding the full load power curve in (at least) 2 columns
                            Example:

                                np.array([
                                    [ 0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120 ],
                                    [ 6.11, 21.97, 37.43, 51.05, 62.61, 72.49, 81.13, 88.7, 94.92, 98.99, 100., 96.28, 87.66 ]
                                ]).T

                            * The 1st column or `n_norm` is the normalized engine revolutions, within [0.0, 0.15]:

                                        n_norm = (n - n_idle) / (n_rated  - n_idle)

                            * The 2nd column or `p_norm` is the normalised values of the full-power load against the p_rated,
                              within [0, 1]: :math:`p_norm = p / p_rated`
                        """),
                        'type': [ 'object', 'array', 'null'],
                    },
                    'pmr': {
                        'title': 'Power to Unladen-Mass',
                        'description': 'Power/unladen-Mass ratio (W/kg).',
                        'type': 'number',
                    },
                    'wltc_class': {
                        'description': 'The name of the WLTC-class (found within WLTC-data/classes) as selected by the experiment.',
                        'type': 'string',
                        'enum': ['class1', 'class2', 'class3a', 'class3b'],
                    },
                }  #veh-props
            }, # veh
            'params': {
                'title': 'experiment parameters',
                'type': 'object', 'additionalProperties': additional_properties,
                'required': [
                    'resistance_coeffs_regression_curves',
                    'driver_mass',
                    'v_stopped_threshold',
                    'f_inertial',
                    'f_safety_margin',
                    'f_n_max',
                    'f_n_min',
                    'f_n_min_gear2',
                    'f_n_clutch_gear2',
                    'wltc_data',
                ],
                'properties': {
                    'resistance_coeffs_regression_curves': {
                        'description': "Regression curve factors for calculating vehicle's ``resistance_coeffs`` when missing.",
                        'type': 'array',
                        'minItems': 3,
                        'maxItems': 3,
                        'items': {
                            'type': 'array',
                            'minItems': 2,
                            'maxItems': 2,
                            'items': {'type': 'number'},
                        },
                    },
                    'f_downscale_threshold': {
                        'title': "Downscale-factor threshold",
                        'description': "The limit for the calculated ``f_downscale``` below which no downscaling happens.",
                        'type': [ 'number', 'null'],
                        'default': 0.01,
                    },
                    'driver_mass': {
                        'title': "Driver's mass (kg)",
                        'description': "The mass (kg) of the vehicle's driver, where: Unladen_mass = (Test_mass - driver_mass) (Annex 1-3.2.6, p9).",
                        'type': [ 'number', 'null'],
                        'default': 75,
                    },
                    'v_stopped_threshold': {
                        'description': 'Velocity (km/h) under which (<=) to idle gear-shift (Annex 2-3.3, p71).',
                        'type': [ 'number', 'null'],
                        'default': 1,
                    },
                    'f_inertial': {
                        'description': "This is the 'kr' inertial-factor used in the 2nd part of the formula for calculating required-power (Annex 2-3.1, p71).",
                        'type': [ 'number', 'null'],
                        'default': 1.1,
                    },
                    'f_safety_margin': {
                        'description': dedent("""
                            Safety-margin factor for load-curve due to transitional effects (Annex 2-3.3, p72).
                            If array, its length must match those of the `gear_ratios`.
                        """),
                        'type': [ 'array', 'number', 'null'],
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
                        'description': dedent("""
                            A 2-value number-array(f1, f2) controlling when to clutch gear-2:
                                N < n_clutch_gear2 := max(f1 * n_idle, f2 * n_range + n_idle),
                            unless "clutched"...
                        """),
                        'type': [ 'array', 'null'],
                        'default': [1.15, 0.03],
                    },
                    'f_downscale': {
                        'description': 'The downscaling-factor as calculated by the experiment (Annex 1-7.3, p68).',
                        'type': 'number',
                    },
                    'wltc_data': {'$ref': _url_wltc},
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
        }
    }

    return schema

def _get_wltc_schema():
    """The json-schema for the WLTC-data required to run a WLTC experiment.

    :return :dict:
    """

    schema = {
        '$schema': 'http://json-schema.org/draft-04/schema#',
        'id': _url_wltc,
        'title': 'WLTC data',
        'type': 'object', 'additionalProperties': False,
        'required': ['classes'],
        'properties': {
            'classes': {
                'type': 'object', 'additionalProperties': False,
                'required': ['class1', 'class2', 'class3a', 'class3b'],
                'properties': {
                    'class1': {'$ref': '#definitions/class'},
                    'class2': {'$ref': '#definitions/class'},
                    'class3a': {'$ref': '#definitions/class'},
                    'class3b': {'$ref': '#definitions/class'},
                }
            },
        },
        'definitions': {
            'class': {
                'title': 'WLTC class data',
                'type': 'object', 'additionalProperties': False,
                'required': ['pmr_limits', 'parts', 'downscale', 'cycle'],
                'properties': {
                    'pmr_limits': {
                        'title': 'PMR (low, high]',
                        'description': 'Power_To_unladen-Mass ratio-limits ((low, high], W/kg) used to select classes (Annex 1, p19).',
                        'type': 'array',
                        'items': {'type': 'number'},
                        'minItems': 2, 'maxItems': 2,
                    },
                    'velocity_limits': {
                        'description': 'Velocity-limits ([low, high), km/h) within which (<) version-a/b from class3 is selected (Annex 1, p19).',
                        'type': 'array',
                        'items': {'type': 'number'},
                        'minItems': 2, 'maxItems': 2,
                    },
                    'parts': {
                        'type': 'array', 'items': {
                            'type': 'array',
                            'items': {'type': 'integer',},
                            'minItems': 2, 'maxItems': 2,
                        }
                    },
                    'downscale': {
                        'type': 'object', 'additionalProperties': False,
                        'required': ['phases', 'p_max_values', 'factor_coeffs'],
                        'properties': {
                            'phases': {
                                'type': 'array', 'additionalItems': False,
                                'items': {'$ref': 'model#definitions/positiveInteger'},
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
                                'description': 'Velocity-limit (<, km/h) for calculating class-2 & 3 ``f_downscaling`` (Annex 1.7.3, p68).',
                                'type': 'number',
                            },
                        }
                    },
                    'checksum': { 'type': 'number'},
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



def get_class_part_names(cls_name=None):
    """
    :param str cls_name: one of 'class1', ..., 'class3b', if missing, returns all 4 part-names
    """
    part_names = ['Low', 'Medium', 'High', 'ExtraHigh']
    
    if cls_name:
        wltc_data = _get_wltc_data()
        cls = wltc_data['classes'][cls_name]
        part_names = part_names[:len(cls['parts'])]
        
    return part_names

def get_class_parts_limits(cls_name, mdl=None, edges=False):
    """
    Parses the supplied in wltc_data and extracts the part-limits for the specified class-name.
    
    :param str cls_name: one of 'class1', ..., 'class3b'
    :param mdl: the mdl to parse wltc_data from, if ommited, parses the results of :func:`_get_wltc_data()`
    :param edges: when `True`, embeds internal limits into (0, len)
    :return: a list of ints with the part-limits, ie for class-3a these are 3 numbers 
    """
    if mdl:
        wltc_data = mdl['wltc_data']
    else:
        wltc_data = _get_wltc_data()
        
    cls = wltc_data['classes'][cls_name]
    parts = cls['parts']
    parts = parts if edges else parts[:-1]
    part_limits = [end+0.5 for (start, end) in parts]
    if edges:
        part_limits.insert(0, 0)
         
    return part_limits

def get_class_parts_index(cls_name, index=None, mdl=None):
    """
    Returns an array equally sized as `index` with zero-based ints denoting the part each second of the cycle belong to.
    
    :param str cls_name: one of 'class1', ..., 'class3b'
    :param list/array index: (Optional) the index to "segment" into parts, defaults to 1Hz class's index  
    :return: a numpy-array of integers with length equal to `index`, or if not given, 
                        the default length of the requested class otherwise

    Get class-checksums example::
    
        >>> from wltp import model
        >>> import pandas as pd
        
        >>> cls = 'class2'
        >>> part_limits = model.get_class_parts_index(cls)
        >>> part_limits
        array([   0,  589, 1022, 1477, 1800])

        >>> cls_data = model._get_wltc_data()['classes'][cls]
        >>> cycle = pd.DataFrame(cls_data['cycle'])
        >>> cycle.groupby(pd.cut(cycle.index, part_limits)).sum()
                            0
        (0, 589]      11162.2
        (589, 1022]   17054.3
        (1022, 1477]  24450.6
        (1477, 1800]  28869.8
        
    """
    limits = get_class_parts_limits(cls_name, mdl=mdl, edges=True)
    limits = np.array(limits).astype(np.int)
    
    if index:
        index = np.asarray(index)

    return limits

def get_class_pmr_limits(mdl=None, edges=False):
    """
    Parses the supplied in wltc_data and extracts the part-limits for the specified class-name.
    
    :param mdl: the mdl to parse wltc_data from, if omitted, parses the results of :func:`_get_wltc_data()`
    :param edges: when `True`, embeds internal limits into (0, len)
    :return: a list with the pmr-limits (2 numbers) 
    """
    if mdl:
        wltc_data = mdl['wltc_data']
    else:
        wltc_data = _get_wltc_data()
        
    pmr_limits_pairs = [cls['pmr_limits'] for cls in wltc_data['classes'].values()]
    pmr_limits = sorted(set(it.chain(*pmr_limits_pairs)))
    if not edges:
        pmr_limits = pmr_limits[1:-1]    ## Exclude 0 and inf
    
    return pmr_limits


def merge(a, b, path=[]):
    """'merges b into a"""

    for key in b:
        bv = b[key]
        if key in a:
            av = a[key]
            if isinstance(av, Mapping) != isinstance(bv, Mapping):
#                 log.debug("Dict-values conflict at '%s'! a(%s) != b(%s)",
#                                 '/'.join(path + [str(key)]), type(av), type(bv))
                pass
            elif av is bv:
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



def model_validator(additional_properties=False, validate_wltc_data=False, validate_schema=False):
    schema = _get_model_schema(additional_properties)
    wltc_schema = _get_wltc_schema() if validate_wltc_data else {} ## Do not supply wltc schema, for speedup.
    resolver = RefResolver(_url_model, schema, store={_url_wltc: wltc_schema})
    validator = PandelVisitor(schema, resolver=resolver, skip_meta_validation=not validate_schema)

    return validator

def validate_model(mdl, additional_properties=False, iter_errors=False, validate_wltc_data=False, validate_schema=False):
    """
    :param bool iter_errors: does not fail, but returns a generator of ValidationErrors

    >>> validate_model(None)
    Traceback (most recent call last):
    jsonschema.exceptions.ValidationError: None is not of type 'object'
    ...

    >>> mdl = _get_model_base()
    >>> err_generator = validate_model(mdl, iter_errors=True)
    >>> sorted(err_generator, key=hash)
    [<ValidationError:
    ...

    >>> mdl = _get_model_base()
    >>> mdl["vehicle"].update({
    ...     "unladen_mass":1230,
    ...     "test_mass":   1300,
    ...     "v_max":   195,
    ...     "p_rated": 110.625,
    ...     "n_rated": 5450,
    ...     "n_idle":  950,
    ...     "n_min":   500,
    ...     "gear_ratios":[120.5, 75, 50, 43, 33, 28],
    ...     "resistance_coeffs":[100, 0.5, 0.04],
    ... })
    >>> err_generator = validate_model(mdl, iter_errors=True)
    >>> len(list(err_generator))
    0
    """

    validator = model_validator(additional_properties=additional_properties, validate_wltc_data=validate_wltc_data)
    validators = [
        validator.iter_errors(mdl),
        yield_load_curve_errors(mdl),
        yield_n_min_errors(mdl),
        yield_safety_margin_errors(mdl),
        yield_forced_cycle_errors(mdl, additional_properties)
    ]
    errors = it.chain(*[v for v in validators if not v is None])

    if iter_errors:
        return errors
    else:
        for error in errors:
            try:
                raise error
            except jsonschema.ValidationError as ex:
                ## Attempt to workround BUG: https://github.com/Julian/jsonschema/issues/164
                #
                if isinstance(ex.instance, NDFrame) or isinstance(ex.instance, ndarray):
                    ex.instance = '%s: %s' % (type(ex.instance), str(ex.instance))
                    ex.instance = str(ex.instance)
                raise



def yield_load_curve_errors(mdl):
    vehicle = mdl['vehicle']
    f_n_max = mdl['params']['f_n_max']
    wot = vehicle['full_load_curve']
    try:
        if not isinstance(wot, pd.DataFrame):
            wot = pd.DataFrame(wot)
        if wot.shape[0] < wot.shape[1]:
            wot = wot.T

        cols = wot.columns
        if wot.shape[1] == 1:
            if cols[0] != 'p_norm':
                log.warning("Assuming the single-column(%s) to be the `p_norm` and the index the `n_norm`.", cols[0])
                cols = ['p_norm']
                wot.columns = cols
            wot['n_norm'] = wot.index
            wot = wot[['n_norm', 'p_norm']]
        elif wot.shape[1] == 2:
            if not all(isinstance(i, string_types) for i in cols):
                wot.columns = ['n_norm', 'p_norm']

        n_norm = wot['n_norm']
        if (min(n_norm) > 0.1):
            yield ValidationError('The full_load_curve must begin at least from 0%%, not from %f%%!' % min(n_norm))
        max_x_limit = f_n_max
        if (max(n_norm) < max_x_limit):
            yield ValidationError('The full_load_curve must finish at least on f_n_max(%f%%), not on %f%%!' % (max_x_limit, max(n_norm)))

        p_norm = wot['p_norm']
        if (min(p_norm) < 0):
            yield ValidationError('The full_load_curve must not contain negative power(%f)!' % min(p_norm))
        if (max(p_norm) > 1):
            yield ValidationError('The full_load_curve must not exceed 1, found %f!' % max(p_norm))

        vehicle['full_load_curve'] = wot
    except (KeyError, PandasError) as ex:
        yield ValidationError('Invalid Full-load-curve, due to: %s' % ex, cause= ex)

def yield_n_min_errors(mdl):
    vehicle = mdl['vehicle']
    ngears = len(vehicle['gear_ratios'])
    n_min = vehicle.get('n_min')
    if not n_min is None:
        try:
                if isinstance(n_min, Sized):
                    if len(n_min) != ngears:
                        yield ValidationError("Length mismatch of n_min(%s) != gear_ratios(%s)!"% (len(n_min), ngears))
                else:
                    vehicle['n_min'] = [n_min] * ngears
        except PandasError as ex:
            yield ValidationError("Invalid 'n_min', due to: %s" % ex, cause= ex)

def yield_safety_margin_errors(mdl):
    params = mdl['params']
    f_safety_margin = params['f_safety_margin']
    ngears = len(mdl['vehicle']['gear_ratios'])
    try:
        if isinstance(f_safety_margin, Sized):
            if len(f_safety_margin) != ngears:
                yield ValidationError("Length mismatch of f_safety_margin(%s) != gear_ratios(%s)!"% (len(f_safety_margin), ngears))
        else:
            params['f_safety_margin'] = [f_safety_margin] * ngears
    except PandasError as ex:
        yield ValidationError("Invalid 'gear_n_min', due to: %s" % ex, cause= ex)


def yield_forced_cycle_errors(mdl, additional_properties):
    params = mdl['params']
    forced_cycle = params.get('forced_cycle')
    if not forced_cycle is None:
        try:
            if not isinstance(forced_cycle, pd.DataFrame):
                forced_cycle = pd.DataFrame(forced_cycle)
                if forced_cycle.shape[0] == forced_cycle.shape[1]:
                    yield ValidationError('The full_load_curve is a square matrix(%s), cannot decide orientation!' % (forced_cycle.shape, ))
            if forced_cycle.shape[0] < forced_cycle.shape[1]:
                forced_cycle = forced_cycle.T
            cols = forced_cycle.columns

            # if not additional_properties and not set(cols) <= set(['v','slide']):
            #     yield ValidationError('Unexpected columns!')

            if forced_cycle.shape[1] == 1:
                if cols[0] == 1:
                    log.warning("Assuming the unamed single-column to be the velocity_profile(v).", cols[0])
                    forced_cycle.columns = ['v']

            params['forced_cycle'] = forced_cycle
        except PandasError as ex:
            yield ValidationError('Invalid forced_cycle, due to: %s' % ex, cause= ex)

get_model_schema = _get_model_schema

if __name__ == '__main__':
    print('Model: %s' % json.dumps([_get_model_schema(), _get_wltc_schema()], indent=1))
    print('Model: %s' % json.dumps(_get_model_base(), indent=1))

