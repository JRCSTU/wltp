#!/usr/bin/env python
#
# Copyright 2013-2014 European Commission (JRC);
# Licensed under the EUPL (the 'Licence');
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at: http://ec.europa.eu/idabc/eupl
import argparse
import pandas as pd


##############
#  Utilities
#
def str2bool(v):
    vv = v.lower()
    if (vv in ("yes", "true", "on")):
        return True
    if (vv in ("no", "false", "off")):
        return False
    try:
        return float(v)
    except:
        raise argparse.ArgumentTypeError('Invalid boolean(%s)!' % v)


def pairwise(t):
    '''From http://stackoverflow.com/questions/4628290/pairs-from-single-list'''
    it1 = iter(t)
    it2 = iter(t)
    try:
        next(it2)
    except:
        return []
    return zip(it1, it2)


def ensure_modelpath_Series(mdl, json_path):
    import jsonpointer as jsonp

    part = jsonp.resolve_pointer(mdl, json_path)
    if not isinstance(part, pd.Series):
        part = pd.Series(part)
        jsonp.set_pointer(mdl, json_path, part)

def ensure_modelpath_DataFrame(mdl, json_path):
    import jsonpointer as jsonp

    part = jsonp.resolve_pointer(mdl, json_path)
    if not isinstance(part, pd.Series):
        part = pd.DataFrame(part)
        jsonp.set_pointer(mdl, json_path, part)


## From http://stackoverflow.com/a/4149190/548792
#
class Lazy(object):
    def __init__(self,func):
        self.func=func
    def __str__(self):
        return self.func()
