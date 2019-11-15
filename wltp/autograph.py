#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2019 European Commission (JRC);
# Licensed under the EUPL (the 'Licence');
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at: http://ec.europa.eu/idabc/eupl
import inspect
from pathlib import Path
from typing import Any, Callable, Iterable, List, Mapping, Set, Tuple, Union

from boltons.iterutils import first
from toolz import dicttoolz as dtz

from graphtik import optional, sideffect
from graphtik.nodes import FunctionalOperation

from .utils import asdict, aslist, astuple

_my_project_dir = Path(__file__).parent

_FnKey = Union[str, Iterable[str]]


def is_regular_class(name, item):
    return inspect.isclass(item) and name[0].isupper()


def _is_in_my_project(item) -> bool:
    in_my_project = False
    try:
        path = inspect.getfile(item)
    except TypeError:
        pass  # raised for builtins e.g.`sys`
    else:
        try:
            Path(path).relative_to(_my_project_dir)
            in_my_project = True
        except ValueError:
            pass  # raised when unrelated

    return in_my_project


## UNUSED
class Prefkey:
    """Index into dicts with a key or a joined(pefix+key), where prefix: tuple"""

    sep = "/"

    def prefkey(self, d, key: _FnKey, default: Union[Callable, Any] = None):
        if key in d:
            return d[key]

        if isinstance(key, tuple):
            if key[-1] in d:
                return d[key[-1]]

            key = self.sep.join(key)
            if key in d:
                return d[key]

        if callable(default):
            return default()
        return default


class FnHarvester:
    """
    Collect callables, classes & their methods into ``collected`` atribute.

    :param excludes:
        names to exclude;  they can/be/prefixed or not
    :param base_modules:
        skip function/classes not in these modules; if not given, include all items.
    :param predicate:
        any user callable accepting a single argument returning falsy to exclude 
        the visited item
    :param include_methods:
        Whether to collect methods from classes

    **Example:**

    >>> from wltp import cycler, downscale, engine, vehicle, vmax

    >>> modules = (cycler, downscale, engine, vehicle, vmax)
    >>> funcs = FnHarvester(
    ...     include_methods=False,
    ...     predicate=_is_in_my_project
    ... ).harvest(*modules)
    >>> len(funcs)
    67
    >>> sorted(list(zip(*funcs))[0])
    [('wltp.cycler', 'CycleBuilder'),
     ('wltp.cycler', 'NMinDrives'),
     ('wltp.cycler', 'PhaseMarker'),
    ...

    >>> excludes = "utils io invariant cycles datamodel idgears plots".split()
    >>> excludes = (
    ...     "utils wio inv cycles datamodel idgears plots "
    ...     "GearMultiIndexer VMaxRec "
    ...     "timelens "
    ... ).split()
    >>> funcs = FnHarvester(
    ...     excludes=(excludes),
    ...     base_modules=modules
    ... ).harvest()
    >>> len(funcs)
    41
    >>> sorted(list(zip(*funcs))[0])
    [('wltp.cycler', 'CycleBuilder'),
     ('wltp.cycler', 'CycleBuilder', 'add_columns'),
    ...
     ('wltp.vmax', 'calc_v_max')]

    """

    include_methods: bool = True

    def __init__(
        self,
        *,
        excludes: Iterable[_FnKey] = None,
        base_modules: Iterable = None,
        predicate: Callable[[Any], bool] = None,
        include_methods=True,
        sep="/",
    ):
        if include_methods is not None:
            self.include_methods = bool(include_methods)
        self._seen: Set = set()
        self.excludes = set(excludes or ())
        self.base_modules = set(base_modules or ())
        self.predicate = predicate
        self.sep = sep
        self.collected: List[Tuple[str, Callable]] = []

    def _join_prefixes(self, *names):
        return self.sep.join(names)

    def is_harvestable(self, path, name, item):
        if (
            name.startswith("_")
            or item in self._seen
            or name in self.excludes
            or self._join_prefixes(*path, name) in self.excludes
        ):
            return False

        self._seen.add(item)

        return (
            (callable(item) or is_regular_class(name, item) or inspect.ismodule(item))
            and (not self.base_modules or inspect.getmodule(item) in self.base_modules)
            and (not self.predicate or self.predicate(item))
        )

    def _harvest(self, path, name, item):
        if not self.is_harvestable(path, name, item):
            return

        if inspect.ismodule(item):
            for named_member in inspect.getmembers(item):
                # Reset path on modules
                self._harvest((item.__name__,), *named_member)
            return

        is_class = is_regular_class(name, item)
        if callable(item) or is_class:
            self.collected.append((path + (name,), item))
            if not is_class:
                return

        # names = set(list(zip(*items))[1])
        # dupe_names = self.collected.keys() - names
        # if dupe_names:
        #     raise ValueError(f"Duplicate names: {dupe_names}")

        if self.include_methods:
            for named_member in inspect.getmembers(item, predicate=callable):
                self._harvest(path + (name,), *named_member)

    def harvest(self, *baseitems, path=None):
        """
        :param baseitems:
            items with ``__name__``, like module, class, functions.
            If nothing is given, `attr:`baseModules` is used instead.
        :param path:
            a tuple of strings to prepend in the result tuple-names (aka path)
        """
        if not baseitems:
            baseitems = self.base_modules
        for bi in baseitems:
            self._harvest(astuple(path, "path"), bi.__name__, bi)

        return self.collected


class Autograph:
    """
    Make a graphtik operation by inspecting a function

    :param out_prefixes:
        if a function-name start with any of these prefixes, it is trimmed
        and a single `provides` is derrived out of it.
    :param overrides:
        a mapping of fn-keys --> dicts with keys:
        fn, name, needs, provides, inp_sideffects, out_sideffects
    **Example:**

    >>> def calc_sum_ab(a, b=0):
    ...     return a + b

    >>> aug = Autograph(out_prefixes=['calc_', 'upd_'])
    >>> aug.wrap_fn(calc_sum_ab)
    FunctionalOperation(name='calc_sum_ab',
                        needs=['a', optional('b')],
                        provides=['sum_ab'],
                        fn='calc_sum_ab')

    """

    def __init__(
        self,
        out_prefixes: _FnKey = None,
        overrides: Mapping[_FnKey, Mapping] = None,
        sep=None,
    ):
        self.out_prefixes = out_prefixes and aslist(out_prefixes, "out_prefixes")
        self.overrides = overrides and asdict(overrides, "overrides")
        if sep is not None:
            self.sep = sep

    def _from_overrides(self, kw):
        """ASSUMES STABLE DICTS!"""
        del kw["self"]
        fnover = self.overrides and self.overrides.get(kw["name"])
        if fnover is not None:
            kw = {
                argname: fnover[argname] if argname in fnover else argval
                for argname, argval in kw.items()
            }
        return kw

    def wrap_fn(
        self,
        fn=None,
        *,
        name: str = None,
        needs=None,
        provides=None,
        inp_sideffects=None,
        out_sideffects=None,
    ):
        kw = self._from_overrides(locals())
        args = "fn name needs provides inp_sideffects out_sideffects".split()
        fn, name, needs, provides, inp_sideffects, out_sideffects = (
            kw[a] for a in args
        )

        if not name and fn:
            name = fn.__name__

        def is_optional_arg(sig_param):
            return sig_param.default is not inspect._empty

        if needs:
            needs = aslist(needs, "needs")
        elif fn:
            sig = inspect.signature(fn)
            needs = [
                optional(name) if is_optional_arg(param) else name
                for name, param in sig.parameters.items()
                if name != "self"
            ]
        else:
            needs = []

        if provides:
            provides = aslist(provides, "provides")
        elif name and self.out_prefixes:
            matched_prefix = first(p for p in self.out_prefixes if name.startswith(p))
            if matched_prefix:
                provides = [name[len(matched_prefix) :]]
        else:
            provides = []

        if inp_sideffects:
            needs.extend(
                [sideffect(i) for i in aslist(inp_sideffects, "inp_sideffects")]
            )
        if out_sideffects:
            provides.extend(
                [sideffect(i) for i in aslist(out_sideffects, "out_sideffects")]
            )

        return FunctionalOperation(fn=fn, name=name, needs=needs, provides=provides)


"""
    >>> from graphtik import compose

    >>> aug = Autograph(['calc_', 'upd_'], {
    ...     'calc_p_available':{'provides': 'p_avail'},
    ...     'calc_road_load_power': {'provides': 'p_resist'},
    ...     'calc_inertial_power': {'provides': 'p_inert'},
    ...      })
    >>> ops = [aug.wrap_fn(name=name[-1], fn=fn) for name, fn in funcs]
    >>> netop = compose('wltp')(*(op for op in ops if op.provides))
    >>> dot = netop.plot('t.pdf')

"""
