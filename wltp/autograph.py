#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2019-2020 European Commission (JRC);
# Licensed under the EUPL (the 'Licence');
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at: http://ec.europa.eu/idabc/eupl
"""
Harvest functions & annotate their :term:`dependencies <dependency>` to build :term:`pipeline`\\s.
"""
import inspect
import logging
import re
import sys
from collections import ChainMap
from inspect import Parameter
from pathlib import Path
from types import ModuleType
from typing import Any, Callable, Iterable, List, Mapping, Pattern, Set, Tuple, Union

from boltons.iterutils import first
from boltons.setutils import IndexedSet as iset

from graphtik import optional, sfx, sfxed
from graphtik.base import Operation, func_name
from graphtik.modifier import is_sfx
from graphtik.fnop import FnOp, reparse_operation_data

from .utils import Literal, Token, asdict, aslist, astuple

try:
    from re import Pattern as RegexPattern
except ImportError:
    # PY3.6
    from typing import Pattern as RegexPattern


log = logging.getLogger(__name__)

_my_project_dir = Path(__file__).parent

_FnKey = Union[Union[str, Pattern], Iterable[Union[str, Pattern]]]


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
    """Index into dicts with a key or a joined(prefix+key), where prefix: tuple"""

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
    Collect public ops, routines, classes & their methods, partials into :attr:`collected`.

    :param collected:
        a list of 2-tuples::

            (name_path, item_path)

        where the 2 paths correspond to the same items;
        the last path element is always a callable, and
        the previous items may be modules and/or classes,
        in case non-modules are given directly in :meth:`harvest()`::

            [module, [class, ...] callable

        E.g. the path of a class constructor is ``(module_name, class_name)``.

        For :term:`operation`\\s, the name-part is ``None``.
    :param excludes:
        names to exclude;  they can/be/prefixed or not
    :param base_modules:
        skip function/classes not in these modules; if not given, include all items.
        If string, they are searched in :data:`sys.modules`.
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
        >>> len(funcs) > 60
        True
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
        ...     include_methods=True,
        ...     excludes=(excludes),
        ...     base_modules=modules
        ... ).harvest()
        >>> len(funcs) > 30
        True
        >>> sorted(list(zip(*funcs))[0])
        [('wltp.cycler', 'CycleBuilder'),
        ('wltp.cycler', 'CycleBuilder', 'add_columns'),
        ...
        ('wltp.vmax', 'calc_v_max')]

    Use this pattern whe iterating, to account for any :term:`operation` instances:

        >>> funs = [
        ...         (name, fn if isinstance(fn, Operation) else fn)
        ...         for name, fn
        ...         in funcs
        ...        ]
        >>> funs
        [(('wltp.cycler', 'CycleBuilder'),
        ...

    """

    include_methods: bool = True

    def __init__(
        self,
        *,
        excludes: Iterable[_FnKey] = None,
        base_modules: Iterable[Union[ModuleType, str]] = None,
        predicate: Callable[[Any], bool] = None,
        include_methods=False,
        sep=None,
    ):
        super().__init__(sep)
        if include_methods is not None:
            self.include_methods = bool(include_methods)
        self._seen: Set[int] = set()
        self.excludes = set(excludes or ())
        self.base_modules = iset(
            sys.modules[m] if isinstance(m, str) else m for m in (base_modules or ())
        )
        self.predicate = predicate
        self.collected: List[Tuple[str, Callable]] = []

    def is_harvestable(self, name_path, item):
        """Exclude already-seen, private, user-excluded objects(by name or path). """
        name = name_path[-1]
        if (
            name.startswith("_")
            or id(item) in self._seen
            or name in self.excludes
            or self._join_path_names(*name_path) in self.excludes
        ):
            return False

        self._seen.add(id(item))

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
        """Recursively collect modules, routines & classes,."""
        name = name_path[-1]
        item = item_path[-1]

        if not self.is_harvestable(name_path, item):
            pass

        elif isinstance(item, Operation):
            self._collect(None, item_path)

        elif inspect.ismodule(item):
            for mb_name, member in inspect.getmembers(item):
                # Reset path on modules
                self._harvest((item.__name__, mb_name), (item, member))

        elif inspect.isroutine(item):
            self._collect(name_path, item_path)

        elif is_regular_class(name, item):
            self._collect(name_path, item_path)
            if self.include_methods:
                # TIP: scavenge ideas from :class:`doctest.DocTestFinder`
                for mb_name, member in inspect.getmembers(item, predicate=callable):
                    self._harvest(name_path + (mb_name,), item_path + (member,))
        else:
            pass  # partial?

    def harvest(self, *items: Any, base_modules=...) -> List[Tuple[str, Callable]]:
        """
        :param items:
            items with ``__name__``, like module, class, functions,
            or partials (without ``__name__``)
            If nothing is given, `attr:`baseModules` is used instead.

            .. Note::
                This parameter works differently from :attr:`base_modules`, that is,
                harvesting is not limited to those modules only, recursing to
                any imported ones from `items`.

        :return:
            the :attr:`collected`
        """
        old_base_modules = self.base_modules
        try:
            if base_modules is not ...:
                self.base_modules = base_modules

            if not items:
                items = self.base_modules  # type: ignore

            for bi in items:
                name_path = tuple(
                    func_name(bi, mod=0, fqdn=0, human=0, partials=1).split(".")
                )
                self._harvest(name_path, (bi,))

            return self.collected
        finally:
            self.base_modules = old_base_modules

    def paths(self):
        """returns the paths only (no callables), sorted"""
        return list(zip(*self.collected))[0]


_unset = Token("unset")  # TODO: replace `_unset` with ...


def autographed(
    fn=_unset,
    *,
    name=_unset,
    needs=_unset,
    provides=_unset,
    renames=_unset,
    returns_dict=_unset,
    aliases=_unset,
    inp_sideffects=_unset,
    out_sideffects=_unset,
    domain=None,
    **kws,
):
    """
    Decorator adding ``_autograph`` func-attribute with overrides for :class:`Autograph`.

    The rest arguments coming from :class:`graphtik.operation`.

    :param domain:
        if set, overrides are not applied for the "default" domain;
        it allows to reuse the same function to build different operation.
    :param renames:
        mappings to rename both any matching the final `needs` & `provides`
    :param inp_sideffects:
        appended into `needs`; if a tuple, makes it a :class:`.sfxed`
    :param out_sideffects:
        appended into `provides`; if a tuple, makes it a :class:`.sfxed`
    :param kws:
        the rest arguments of :class:`graphtik.operation`, such as::

            endured, parallel, marshalled, node_props

    """
    kws.update(
        {
            k: v
            for k, v in locals().items()
            if v is not _unset and k not in "kws fn domain".split()
        }
    )

    def decorator(fn):
        fn._autograph = {domain: kws}
        return fn

    if fn is _unset:
        return decorator
    return decorator(fn)


def get_autograph_decors(fn, default=None, domain=None) -> dict:
    """Return the dict with :func:`autographed` keywords as keys. """
    if hasattr(fn, "_autograph"):
        return fn._autograph[domain]
    return default


class Autograph(Prefkey):
    """
    Make a graphtik operation by inspecting a function

    The params below (except `full_path_names`) are merged in this order
    (1st takes precendance):

    1. args in :meth:`wrap_fn`
    2. dict from overrides keyed by `name`
    3. decorated with :func:`autographed`
    4. inspected from the callable

    :param out_patterns:
        Autodeduce `provides` by parsing function-names against a collection
        of these items, and decide `provides` by the the 1st one matching
        (unless `provides` are specified in the `overrides`):

        - regex: may contain 1 or 2 groups:

          - 1 group: the name of a single `provides`
          - 2 groups: 2nd is the name of a single :term:`sideffected` dependency,
            the 1st is the sideffect acting upon the former;

        - str: matched as a prefix of the function-name, which is trimmed
          by the first one matching to derrive a single `provides`;

        Note that any `out_sideffects` in overrides, alone, do not block the rule above.
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

    >>> aug = Autograph(out_patterns=['calc_', 'upd_'], renames={"a": "A"})
    >>> aug.wrap_fn(calc_sum_ab)
    FnOp(name='calc_sum_ab',
                        needs=['A', 'b'(?)],
                        provides=['sum_ab'],
                        fn='calc_sum_ab')

    """

    def __init__(
        self,
        out_patterns: _FnKey = None,
        overrides: Mapping[_FnKey, Mapping] = None,
        renames: Mapping = None,
        full_path_names: bool = False,
        sep=None,
    ):
        super().__init__(sep)
        self.out_patterns = out_patterns and aslist(out_patterns, "out_patterns")
        self.overrides = overrides and asdict(overrides, "overrides")
        self.renames = renames and asdict(renames, "renames")
        self.full_path_names = full_path_names

    def _from_overrides(self, key):
        return self.overrides and self._prefkey(self.overrides, key) or {}

    def _match_fn_name_pattern(self, fn_name, pattern) -> Union[str, Tuple[str, str]]:
        """return matched group or groups, callable results or after matched prefix string"""
        if isinstance(pattern, RegexPattern):
            m = pattern.search(fn_name)
            groups = m and m.groups()
            if groups:
                if len(groups) == 1:
                    return groups[0]
                if len(groups) > 2:
                    raise ValueError(
                        f"The `out_pattern` {pattern} matched on '{fn_name}' >2 groups: {groups}"
                    )
                return sfxed(*reversed(groups))
        elif callable(pattern):
            return pattern(fn_name)
        elif fn_name.startswith(pattern):
            return fn_name[len(pattern) :]

    def _deduce_provides_from_fn_name(self, fn_name):
        ## Trim prefix from function-name to derive a singular "provides".
        matches = [self._match_fn_name_pattern(fn_name, p) for p in self.out_patterns]
        provides = first(m for m in matches if m)
        return provides

    def _apply_renames(
        self,
        rename_maps: Iterable[Union[Mapping, Literal[_unset]]],
        word_lists: Iterable,
    ):
        """
        Rename words in all `word_lists` matching keys in `rename_maps`.
        """
        rename_maps = [d for d in rename_maps if d and d is not _unset]
        renames = ChainMap(*rename_maps)
        if renames:
            word_lists = tuple([renames.get(w, w) for w in wl] for wl in word_lists)

        return word_lists

    def _collect_rest_op_args(self, decors: dict):
        """Collect the rest operation arguments from `autographed` decoration."""
        # NOTE: append more arguments as graphtik lib evolves.
        rest_op_args = (
            "returns_dict aliases endured parallel marshalled node_props".split()
        )
        return {k: v for k, v in decors.items() if k in rest_op_args}

    def wrap_fn(
        self,
        fn_path,
        name_path=_unset,
        needs=_unset,
        provides=_unset,
        renames=_unset,
        inp_sideffects=_unset,
        out_sideffects=_unset,
    ) -> FnOp:
        """
        Overriddes order: my-args, self.overrides, autograph-decorator, inspection

        :param fn_path:
            either a callable, or the path to a callable, like::

                [module[, class, ...]] callable

            If none, `fn_path` must be an :term:`operation`.

        :param name_path:
            either a single string, or a tuple-of-strings, corresponding to
            the given `fn_path`
        """
        args = {k: v for k, v in locals().items() if v is not _unset}
        del args["self"], args["fn_path"]
        args.pop("name_path", None)

        fn_path = astuple(fn_path, None)
        fn = fn_path[-1]
        if isinstance(fn, Operation):
            return fn

        decors = get_autograph_decors(fn, {})

        ## Derive `name_path` from: my-args, decorator, fn_name
        #  and then use it to pick overrides.
        #
        if name_path is _unset:
            name_path = decors.get("name", _unset)
            if name_path is _unset:
                name_path = func_name(fn).split(".")

        name_path = astuple(name_path, None)
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

        sig = None
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
        if ... in needs:
            if sig is None:
                sig = inspect.signature(fn)
            needs = [
                arg_name if n is ... else n
                for n, arg_name in zip(needs, sig.parameters)
            ]

        if provides is _unset:
            if is_regular_class(fn_name, fn):
                ## Convert class-name into object variable.
                provides = camel_2_snake_case(fn_name)
            elif self.out_patterns:
                provides = self._deduce_provides_from_fn_name(fn_name) or _unset
            if provides is _unset:
                provides = ()
        provides = aslist(provides, "provides")

        needs, provides = self._apply_renames(
            (renames, override_renames, self.renames), (needs, provides)
        )

        if inp_sideffects is not _unset:
            needs.extend(
                (i if is_sfx(i) else sfxed(*i) if isinstance(i, tuple) else sfx(i))
                for i in aslist(inp_sideffects, "inp_sideffects")
            )

        if out_sideffects is not _unset:
            provides.extend(
                (i if is_sfx(i) else sfxed(*i) if isinstance(i, tuple) else sfx(i))
                for i in aslist(out_sideffects, "out_sideffects")
            )

        if self.full_path_names:
            fn_name = self._join_path_names(*name_path)

        op_kws = self._collect_rest_op_args(decors)

        return FnOp(fn=fn, name=fn_name, needs=needs, provides=provides, **op_kws)


"""
    >>> from graphtik import compose

    >>> aug = Autograph(['calc_', 'upd_'], {
    ...     'calc_p_available':{'provides': 'p_avail'},
    ...     'calc_p_resist': {'provides': 'p_resist'},
    ...     'calc_inertial_power': {'provides': 'p_inert'},
    ...      })
    >>> ops = [aug.wrap_fn(fn, name[-1]) for name, fn in funcs]
    >>> netop = compose('wltp', *(op for op in ops if op.provides))

"""
