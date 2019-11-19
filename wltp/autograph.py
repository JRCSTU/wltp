#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2019 European Commission (JRC);
# Licensed under the EUPL (the 'Licence');
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at: http://ec.europa.eu/idabc/eupl
import inspect
import logging
import re
from collections import ChainMap
from inspect import Parameter
from pathlib import Path
from typing import Any, Callable, Iterable, List, Mapping, Set, Tuple, Union

from boltons.iterutils import first

from graphtik import optional, sideffect
from graphtik.op import FunctionalOperation, reparse_operation_data

from .utils import asdict, aslist, astuple

log = logging.getLogger(__name__)

_my_project_dir = Path(__file__).parent

_FnKey = Union[str, Iterable[str]]


def camel_2_snake_case(word):
    """
    >>> camel_2_snake_case("HTTPResponseCodeXYZ")
    'http_response_code_xyz'

    From https://stackoverflow.com/a/1176023/548792
    """
    return re.sub(r"((?<=[a-z0-9])[A-Z]|(?!^)[A-Z](?=[a-z]))", r"_\1", word).lower()


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
    *,
    name=_unset,
    needs=_unset,
    provides=_unset,
    renames=_unset,
    inp_sideffects=_unset,
    out_sideffects=_unset,
):
    """
    Decorator to annotate a function with overrides for :class:`Autograph`.
    """
    kws = locals()
    overrides = {k: v for k, v in kws.items() if v is not _unset}

    def decorator(fn):
        fn._autograph = overrides
        return fn

    return decorator


def get_autograph_decors(fn, default=None):
    return getattr(fn, "_autograph", default)


class Autograph(Prefkey):
    """
    Make a graphtik operation by inspecting a function

    The params below (except `full_path_names`) are merged in this order
    (1st takes precendance):

    1. args in :meth:`wrap_fn`
    2. dict from overrides keyed by `name`
    3. decorated with :func:`autographed`
    4. inspected from the callable

    :param out_prefixes:
        if a function-name start with any of these prefixes, it is trimmed
        and a single `provides` is derrived out of it.
    :param overrides:
        a mapping of ``fn-keys --> dicts`` with keys::

            name, needs, provides, renames, inp_sideffects, out_sideffects

        An `fn-key` may be a string-tuple of names like::

            [module, [class, ...] callable
    :param renames:
        global ``from --> to`` renamings applied both onto `needs` & `provides`.
        They are applied after merging has been completed, so they can rename
        even "inspected" names.
    :param full_path_names:
        whether operation-nodes would be named after the fully qualified name
        (separated with `/` by default)

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
        renames: Mapping = None,
        full_path_names: bool = False,
        sep=None,
    ):
        super().__init__(sep)
        self.out_prefixes = out_prefixes and aslist(out_prefixes, "out_prefixes")
        self.overrides = overrides and asdict(overrides, "overrides")
        self.renames = renames and asdict(renames, "renames")
        self.full_path_names = full_path_names

    def _from_overrides(self, key):
        return self.overrides and self._prefkey(self.overrides, key) or {}

    def _apply_renames(self, arg_renames, override_renames, *word_lists):
        """
        Rename words in all `word_lists` matching `arg_renames`, `override_renames` ...

        and :attr:`renames`, in that order.
        """
        renames_maps = [d for d in (arg_renames, override_renames, self.renames) if d]
        renames = ChainMap(*renames_maps)
        if renames:
            word_lists = tuple([renames.get(w, w) for w in wl] for wl in word_lists)

        return word_lists

    def wrap_fn(
        self,
        *fn_path,
        name_path=_unset,
        needs=_unset,
        provides=_unset,
        renames=None,
        inp_sideffects=_unset,
        out_sideffects=_unset,
    ):
        """
        Overiddes order: my-args, self.overrides, autograpf-decorator, inspection

        :param fn_path:
            the path to a callable, like::

                [module, [class, ...] callable

        :param name_path:
            a single string, ot the corresponding name-path of the `fn` callable
        """
        args = {k: v for k, v in locals().items() if v is not _unset}
        del args["self"], args["fn_path"], args["name_path"]

        fn = fn_path[-1]
        decors = get_autograph_decors(fn)

        ## Derive `name_path` from: my-args, decorator, fn_name
        #  and then use it to pick overrides.
        #
        if name_path is _unset:
            name_path = decors.get("name", _unset)
            if name_path is _unset:
                name = fn.__name__
        name_path = astuple(name_path, "name")
        fn_name = str(name_path[-1])

        overrides = self._from_overrides(name_path)

        op_data = ChainMap(args, overrides)
        if decors:
            op_data.maps.append(decors)
        if op_data:
            log.debug("Autograph overrides for %r: %s", name_path, op_data)

        op_props = "needs provides renames, inp_sideffects out_sideffects".split()
        needs, provides, override_renames, inp_sideffects, out_sideffects = (
            op_data.get(a, _unset) for a in op_props
        )

        def is_optional_arg(sig_param):
            return sig_param.default is not inspect._empty

        if needs is _unset:
            sig = inspect.signature(fn)
            needs = [
                optional(name) if is_optional_arg(param) else name
                for name, param in sig.parameters.items()
                if name != "self" and param.kind is not Parameter.VAR_KEYWORD
            ]
            ## Insert object as 1st need for object-methods.
            #
            if len(fn_path) > 1:
                clazz = fn_path[-2]
                # TODO: respect autograph decorator for object-names.
                class_name = name_path[-2] if len(name_path) > 1 else clazz.__name__
                if is_regular_class(class_name, clazz):
                    log.debug("Object-method %s.%s", class_name, fn_name)
                    needs.insert(0, camel_2_snake_case(class_name))

        needs = aslist(needs, "needs", allowed_types=(list, tuple))

        if provides is _unset:
            if is_regular_class(fn_name, fn):
                ## Convert class-name into object variable.
                provides = camel_2_snake_case(fn_name)
            elif self.out_prefixes:
                ## Trim prefix from function-name to derive a singular "provides".
                matched_prefix = first(
                    p for p in self.out_prefixes if fn_name.startswith(p)
                )
                if matched_prefix:
                    provides = [fn_name[len(matched_prefix) :]]
            if provides is _unset:
                provides = ()
        provides = aslist(provides, "provides", allowed_types=(list, tuple))

        needs, provides = self._apply_renames(
            renames,
            override_renames is not _unset and override_renames,
            needs,
            provides,
        )

        if inp_sideffects is not _unset:
            needs.extend(sideffect(i) for i in aslist(inp_sideffects, "inp_sideffects"))

        if out_sideffects is not _unset:
            provides.extend(
                sideffect(i) for i in aslist(out_sideffects, "out_sideffects")
            )

        if self.full_path_names:
            fn_name = self._join_path_names(*name_path)

        return FunctionalOperation(fn=fn, name=fn_name, needs=needs, provides=provides)


"""
    >>> from graphtik import compose

    >>> aug = Autograph(['calc_', 'upd_'], {
    ...     'calc_p_available':{'provides': 'p_avail'},
    ...     'calc_p_resist': {'provides': 'p_resist'},
    ...     'calc_inertial_power': {'provides': 'p_inert'},
    ...      })
    >>> ops = [aug.wrap_fn(name=name[-1], fn=fn) for name, fn in funcs]
    >>> netop = compose('wltp')(*(op for op in ops if op.provides))
    >>> dot = netop.plot('t.pdf')

"""
