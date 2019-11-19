#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2019 European Commission (JRC);
# Licensed under the EUPL (the 'Licence');
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at: http://ec.europa.eu/idabc/eupl
import inspect
import logging
from collections import ChainMap
from pathlib import Path
from typing import Any, Callable, Iterable, List, Mapping, Set, Tuple, Union

from boltons.iterutils import first

from graphtik import optional, sideffect
from graphtik.op import FunctionalOperation, reparse_operation_data

from .utils import asdict, aslist, astuple

log = logging.getLogger(__name__)

_my_project_dir = Path(__file__).parent

_FnKey = Union[str, Iterable[str]]


def is_regular_class(name, item):
    return inspect.isclass(item) and name[0].isupper()


def _is_in_my_project(item) -> bool:
    """UNUSED"""
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


class Prefkey:
    """Index into dicts with a key or a joined(pefix+key), where prefix: tuple"""

    sep = "/"

    def __init__(self, sep=None):
        if sep is not None:
            self.sep = sep

    def _join_path_names(self, *names):
        return self.sep.join(str(i) for i in names)

    def _prefkey(self, d, key: _FnKey, default: Union[Callable, Any] = None):
        if isinstance(key, tuple):
            long_key = self.sep.join(key)
            if long_key in d:
                return d[long_key]

            if key[-1] in d:
                return d[key[-1]]
        if key in d:
            return d[key]

        if callable(default):
            return default()
        return default


class FnHarvester(Prefkey):
    """
    Collect callables, classes & their methods into ``collected`` atribute.

    :param collected:
        a list of 2-tuples::

            (name_path, item_path)

        where the 2 paths correspond to the same items;
        the last path element is always a callable, and
        the previous items may be modules and/or classes,
        in case non-modules are given directly in :meth:`harvest()`::

            [module, [class, ...] callable

        E.g. the path of a class constructor is ``(module_name, class_name)``.
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
        sep=None,
    ):
        super().__init__(sep)
        if include_methods is not None:
            self.include_methods = bool(include_methods)
        self._seen: Set = set()
        self.excludes = set(excludes or ())
        self.base_modules = set(base_modules or ())
        self.predicate = predicate
        self.collected: List[Tuple[str, Callable]] = []

    def is_harvestable(self, name_path, item):
        name = name_path[-1]
        if (
            name.startswith("_")
            or name in self.excludes
            or item in self._seen
            or self._join_path_names(*name_path) in self.excludes
        ):
            return False

        self._seen.add(item)

        return (
            (callable(item) or is_regular_class(name, item) or inspect.ismodule(item))
            and (not self.base_modules or inspect.getmodule(item) in self.base_modules)
            and (not self.predicate or self.predicate(item))
        )

    def _collect(self, name_path, item_path):
        """Obey decorated `name`"""
        fn = item_path[-1]
        decors = get_autograph_decors(fn)
        if decors and "name" in decors:
            name_path = name_path[:-1] + (decors["name"],)

        self.collected.append((name_path, item_path))

    def _harvest(self, name_path, item_path):
        name = name_path[-1]
        item = item_path[-1]

        if not self.is_harvestable(name_path, item):
            pass

        elif inspect.ismodule(item):
            for mb_name, member in inspect.getmembers(item):
                # Reset path on modules
                self._harvest((item.__name__, mb_name), (item, member))

        elif callable(item):
            self._collect(name_path, item_path)

            if is_regular_class(name, item):
                if self.include_methods:
                    for mb_name, member in inspect.getmembers(item, predicate=callable):
                        self._harvest(name_path + (mb_name,), item_path + (member,))

    def harvest(self, *baseitems):
        """
        :param baseitems:
            items with ``__name__``, like module, class, functions.
            If nothing is given, `attr:`baseModules` is used instead.
        :return:
            the :attr:`collected`
        """
        if not baseitems:
            baseitems = self.base_modules
        for bi in baseitems:
            self._harvest((bi.__name__,), (bi,))

        return self.collected

    def paths(self):
        """returns the paths only (no callables), sorted"""
        return list(zip(*self.collected))[0]


_unset = object()


def autographed(
    name=_unset,
    needs=_unset,
    provides=_unset,
    inp_sideffects=_unset,
    out_sideffects=_unset,
):
    """
    Decorator to annotate a function with overrides for :class:`Autograph`.
    """
    overrides = {
        k: v
        for k, v in {
            "name": name,
            "needs": needs,
            "provides": provides,
            "inp_sideffects": inp_sideffects,
            "out_sideffects": out_sideffects,
        }.items()
        if v is not _unset
    }

    def decorator(fn):
        fn._autograph = overrides
        return fn

    return decorator


def get_autograph_decors(fn, default=None):
    return getattr(fn, "_autograph", default)


class Autograph(Prefkey):
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
        super().__init__(sep)
        self.out_prefixes = out_prefixes and aslist(out_prefixes, "out_prefixes")
        self.overrides = overrides and asdict(overrides, "overrides")

    def _from_overrides(self, name):
        return self.overrides and self.overrides.get(name) or {}

    def wrap_fn(
        self,
        fn,
        *,
        name=_unset,
        needs=_unset,
        provides=_unset,
        inp_sideffects=_unset,
        out_sideffects=_unset,
    ):
        """
        Overiddes order: my-args, self.overrides, autograpf-decorator, inspection
        """
        args = {k: v for k, v in locals().items() if v is not _unset}
        del args["self"], args["fn"], args["name"]
        decors = get_autograph_decors(fn)

        ## Derive name from my-args, decorator, fn_name
        #  which is used to pick overrides.
        #
        if name is _unset:
            name = decors.get("name", _unset)
            if name is _unset:
                name = fn.__name__

        overrides = self._from_overrides(name)

        op_data = ChainMap(args, overrides)
        if decors:
            op_data.maps.append(decors)
        if op_data:
            log.debug("Autograph overrides for %r: %s", name, op_data)

        op_props = "needs provides inp_sideffects out_sideffects".split()
        needs, provides, inp_sideffects, out_sideffects = (
            op_data.get(a, _unset) for a in op_props
        )

        def is_optional_arg(sig_param):
            return sig_param.default is not inspect._empty

        if needs is _unset:
            sig = inspect.signature(fn)
            needs = [
                optional(name) if is_optional_arg(param) else name
                for name, param in sig.parameters.items()
                if name != "self"
            ]
        needs = aslist(needs, "needs", allowed_types=(list, tuple))

        if provides is _unset:
            if name and self.out_prefixes:
                ## Trim prefix from function-name to derive a singular "provides".
                matched_prefix = first(
                    p for p in self.out_prefixes if name.startswith(p)
                )
                if matched_prefix:
                    provides = [name[len(matched_prefix) :]]
            if provides is _unset:
                provides = ()
        provides = aslist(provides, "provides", allowed_types=(list, tuple))

        if inp_sideffects is not _unset:
            needs.extend(sideffect(i) for i in aslist(inp_sideffects, "inp_sideffects"))

        if out_sideffects is not _unset:
            provides.extend(
                sideffect(i) for i in aslist(out_sideffects, "out_sideffects")
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
