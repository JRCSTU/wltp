#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2013-2019 European Commission (JRC);
# Licensed under the EUPL (the 'Licence');
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at: http://ec.europa.eu/idabc/eupl

import io
import os
import sys
from typing import Union


##############
#  Utilities
#
def str2bool(v):
    import argparse

    vv = v.lower()
    if vv in ("yes", "true", "on"):
        return True
    if vv in ("no", "false", "off"):
        return False
    try:
        return float(v)
    except:
        raise argparse.ArgumentTypeError("Invalid boolean(%s)!" % v)


def pairwise(t):
    """From http://stackoverflow.com/questions/4628290/pairs-from-single-list"""
    it1 = iter(t)
    it2 = iter(t)
    try:
        next(it2)
    except:
        return []
    return zip(it1, it2)


## From http://code.activestate.com/recipes/578231-probably-the-fastest-memoization-decorator-in-the-/
#
def memoize(f):
    """ Memoization decorator for functions taking one or more arguments. """

    class memodict(dict):
        def __init__(self, f):
            self.f = f

        def __call__(self, *args):
            return self[args]

        def __missing__(self, key):
            ret = self[key] = self.f(*key)
            return ret

    return memodict(f)


## From http://stackoverflow.com/a/4149190/548792
#
class Lazy(object):
    def __init__(self, func):
        self.func = func

    def __str__(self):
        return self.func()


def is_travis():
    return "TRAVIS" in os.environ


def generate_filenames(filename):
    f, e = os.path.splitext(filename)
    yield filename
    i = 1
    while True:
        yield "%s%i%s" % (f, i, e)
        i += 1


def open_file_with_os(fpath):
    ## From http://stackoverflow.com/questions/434597/open-document-with-default-application-in-python
    #     and http://www.dwheeler.com/essays/open-files-urls.html
    import subprocess

    try:
        os.startfile(fpath)
    except AttributeError:
        if sys.platform.startswith("darwin"):
            subprocess.call(("open", fpath))
        elif os.name == "posix":
            subprocess.call(("xdg-open", fpath))
    return


def yaml_dump(o, fp):
    from ruamel import yaml
    from ruamel.yaml import YAML

    y = YAML(typ="rt", pure=True)
    y.default_flow_style = False
    # yaml.canonical = True
    yaml.scalarstring.walk_tree(o)
    y.dump(o, fp)


def yaml_dumps(o) -> str:
    fp = io.StringIO()
    yaml_dump(o, fp)
    return fp.getvalue()


def yaml_load(fp) -> Union[dict, list]:
    from ruamel.yaml import YAML

    y = YAML(typ="rt", pure=True)
    return y.load(fp)


def yaml_loads(txt: str) -> Union[dict, list]:
    fp = io.StringIO(txt)
    return yaml_load(fp)
