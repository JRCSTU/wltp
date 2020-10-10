#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2013-2020 European Commission (JRC);
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
## Emulate Py3.8 typing
#
try:
    from typing import Final  # type: ignore # PY3.8+ only
    from typing import Literal  # type: ignore # PY3.8+ only
except ImportError:

    class _NoOp:
        def __getitem__(self, key):
            return key

    Final = _NoOp()
    Literal = _NoOp()


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


def aslist(i, argname: Union[str, None], allowed_types=list):
    """
    Converts iterables (except strings) into a list.

    :param argname:
        If string, it's used in the exception raised when `i` not an iterable.
        If `None`, wraps non-iterables in a single-item list.
    """
    if not i:
        return i if isinstance(i, allowed_types) else []

    if isinstance(i, str):
        i = [i]
    elif not isinstance(i, allowed_types):
        try:
            i = list(i)
        except Exception as ex:
            if argname is None:
                return [i]
            raise ValueError(f"Cannot list-ize {argname}({i!r}) due to: {ex}") from None

    return i


def astuple(i, argname: Union[str, None]) -> tuple:
    """
    Converts iterables (except strings) into a tuple.

    :param argname:
        If string, it's used in the exception raised when `i` not an iterable.
        If `None`, wraps non-iterables in a single-item tuple, and no exception
        is ever raised.
    """
    if not i:
        return ()

    if isinstance(i, str):
        i = (i,)
    else:
        try:
            i = tuple(i)
        except Exception as ex:
            if argname is None:
                return (i,)
            raise ValueError(
                f"Cannot tuple-ize {argname}({i!r}) due to: {ex}"
            ) from None

    return i


def asdict(i, argname: str):
    """
    Converts iterables-of-pairs or just a pair-tuple into a dict.

    :param argname:
        Used in the exception raised when `i` not an iterable.
    """
    if not i:
        return i if isinstance(i, dict) else {}

    if isinstance(i, tuple) and len(i) == 2:
        i = dict([i])
    elif not isinstance(i, Mapping):
        try:
            i = dict(i)
        except Exception as ex:
            raise ValueError(f"Cannot dict-ize {argname}({i!r}) due to: {ex}") from None

    return i


## From http://stackoverflow.com/a/4149190/548792
#
class Lazy(object):
    def __init__(self, func):
        self.func = func

    def __str__(self):
        return self.func()


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
    import operator
    import pandas as pd
    from pandas.core.generic import NDFrame

    def defaulter(o):
        if isinstance(o, np.ndarray):
            s = o.tolist()
        elif isinstance(o, NDFrame):
            if pd_method is None:
                s = json.loads(pd.DataFrame.to_json(o))
            else:
                method = operator.methodcaller(pd_method)
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


@contextlib.contextmanager
def pwd_changed(path: os.PathLike):
    """Temporarily change working-dir to (and yield) given `path`."""
    from pathlib import Path

    prev_cwd = Path.cwd()
    path = Path(path)
    os.chdir(path)
    try:
        yield path
    finally:
        os.chdir(prev_cwd)


@contextlib.contextmanager
def matlab_pwd_changed(path: os.PathLike, oc: "oct2py.octave"):  # type: ignore
    """
    Temporarily change Matlab's Oct2Pyc session's working-dir to (and yield) given `path`.

    :return:
        yields the given path as a :class:`pathlib.Path` instance
    """
    from pathlib import Path

    prev_cwd = Path.cwd().as_posix()
    path = Path(path)
    oc.cd(path.as_posix())
    try:
        yield path
    finally:
        oc.cd(prev_cwd)
