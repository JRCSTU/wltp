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
                   'minItems': 3,
                   'maxItems': 7,
                   'description': 'The 3 driving resistance coefficients f0, f1, f2 as defined in Annex 4, in N, N/(km/h), and N/(km/h)² respectively.',
                },
               'full_load_curve': {
                   'title': 'full load power curve',
                   'type': 'array',
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

