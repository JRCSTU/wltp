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
'''Check validity of json-schemas themselfs.

@author: ankostis@gmail.com
@since 4 Jan 2014
'''
import jsonschema
import unittest
import wltc.schemas as schemas


class Test(unittest.TestCase):

    def testWltcSchema(self):
        validator = schemas.wltc_validator()
        validator.check_schema(schemas.wltc_schema()) # could invoke directly on class

    def testWltcShema_emptyInstance(self):
        validator = schemas.wltc_validator()
        instance = {}

        self.assertRaises(jsonschema.ValidationError, validator.validate, instance)

    def testModelSchema(self):
        validator = schemas.model_validator()
        validator.check_schema(schemas.model_schema()) # could invoke directly on class

    def testModelShema_emptyInstance(self):
        validator = schemas.model_validator()
        instance = {}

        self.assertRaises(jsonschema.ValidationError, validator.validate, instance)



if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()