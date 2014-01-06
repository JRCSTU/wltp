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
'''wltc.doc module: A Class to merge & validate data for the WLTC calculator (Experiment class).
'''



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

# # works
# print(merge({1:{"a":"A"},2:{"b":"B"}}, {2:{"c":"C"},3:{"d":"D"}}))
# # has conflict
# merge({1:{"a":"A"},2:{"b":"B"}}, {1:{"a":"A"},2:{"b":"C"}})


class Doc(object):
    '''Merges and validates a series of trees making up data for a WLTC experiment.'''

    def __init__(self, validator, *models, skip_validation=False):
        import functools
        self.validator = validator
        self.data = functools.reduce(merge, list(models))
        if not skip_validation:
            self.validate()


    def validate(self, iter_errors=False):
        if iter_errors:
            return self.validator.iter_errors(self.data)
        else:
            self.validator.validate(self.data)



if __name__ == '__main__':
    pass