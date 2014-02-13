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
'''wltc module: The input/output data for the WLTC calculator (Experiment class).
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


class Model(object):
    '''Merges and validates a series of trees making up the modelfor a WLTC experiment.'''

    def __init__(self, *models, skip_validation=False):
        import functools
        from .instances import model_base

        self.data = model_base()
        functools.reduce(merge, [self.data] + list(models))
        if not skip_validation:
            self.validate()


    def validate(self, iter_errors=False):
        from .schemas import model_validator, validate_full_load_curve

        if iter_errors:
            return model_validator().iter_errors(self.data)
        else:
            model_validator().validate(self.data)

        validate_full_load_curve(self.data['vehicle']['full_load_curve'], self.data['params']['f_n_max'])

    def driveability_report(self):
        results = self.data.get('results')
        if (not results is None):
            issues = []
            drv = results['driveability']
            pt = -1
            for t in drv.nonzero()[0]:
                if (pt+1 < t):
                    issues += ['...']
                issues += ['{:>4}: {}'.format(t, drv[t])]
                pt = t

            return '\n'.join(issues)
        return None



if __name__ == '__main__':
    pass
