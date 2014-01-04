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



# ## From http://python-jsonschema.readthedocs.org/en/latest/faq/
# #
# def extend_with_default(validator_class):
#     '''A jsonschema validator that sets missing defaults.
#
#     Not from http://python-jsonschema.readthedocs.org/en/latest/faq/
#     '''
#
#     properties_validator = validator_class.VALIDATORS["properties"]
#
#     def set_defaults(validator, properties, instance, schema):
#         for error in properties_validator(
#             validator, properties, instance, schema,
#         ):
#             yield error
#
#         for prop, subschema in _iteritems(properties):
#             if "default" in subschema:
#                 instance.setdefault(prop, subschema["default"])
#
#     return validators.extend(  # @UndefinedVariable
#         validator_class, {"properties" : set_defaults},
#     )
#
#
# _ValidatorWithDefaults = extend_with_default(Draft4Validator)
# _model_validator = _ValidatorWithDefaults(model_schema)
# def get_model_validator():
#     '''A jsonschema.validator for the vehicle and cycle data specifying a WLTC experiment.'''
#     return _model_validator
#     ## TODO: Is json-validator multithreaded?



__all__ = []

