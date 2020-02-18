#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2013-2019 European Commission (JRC);
# Licensed under the EUPL (the 'Licence');
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at: http://ec.europa.eu/idabc/eupl
"""software utils unrelated to physics or engineering"""
import contextlib
import contextvars
import io
import os
import sys
from collections.abc import Mapping
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


class Token(str):
    def __eq__(self, other):
        return self is other

    def __hash__(self):
        return id(self)

    def __bool__(self):
        return True

    def __str__(self):
        return "T(%s)" % super().__str__()

    def __repr__(self):
        return "T(%s)" % super().__str__()


def aslist(i, argname, allowed_types=list):
    if not i:
        return i if isinstance(i, allowed_types) else []

    if isinstance(i, str):
        i = [i]
    elif not isinstance(i, allowed_types):
        try:
            i = list(i)
        except Exception as ex:
            raise ValueError(f"Argument {argname!r} not an iterable, but {i!r}\n  {ex}")

    return i


def astuple(i, argname):
    if not i:
        return ()

    if isinstance(i, str):
        i = (i,)
    else:
        try:
            i = tuple(i)
        except Exception as ex:
            raise ValueError(f"Cannot tuple-ize arg-{argname!r}({i!r}) due to: {ex}")

    return i


def asdict(i, argname):
    if not i:
        return i if isinstance(i, dict) else {}

    if isinstance(i, tuple) and len(i) == 2:
        i = dict([i])
    elif not isinstance(i, Mapping):
        try:
            i = dict(i)
        except Exception as ex:
            raise ValueError(f"Argument {argname!r} not an mapping, but {i!r}\n  {ex}")

    return i


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


def make_json_defaulter(pd_method):
    import json
    import numpy as np
    from pandas.core.generic import NDFrame

    def defaulter(o):
        if isinstance(o, np.ndarray):
            s = o.tolist()
        elif isinstance(o, NDFrame):
            if pd_method is None:
                s = json.loads(pd.DataFrame.to_json(o))
            else:
                method = ops.methodcaller(pd_method)
                s = "%s:%s" % (type(o).__name__, method(o))
        else:
            s = repr(o)
        return s

    return defaulter


def json_dumps(obj, pd_method=None, **kwargs):
    import json

    return json.dumps(obj, default=make_json_defaulter(pd_method), **kwargs)


def json_dump(obj, fp, pd_method=None, **kwargs):
    import json

    json.dump(obj, fp, default=make_json_defaulter(pd_method), **kwargs)


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


@contextlib.contextmanager
def ctxtvar_redefined(var: contextvars.ContextVar, value):
    token = var.set(value)
    try:
        yield value
    finally:
        var.reset(token)
