#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2013-2020 European Commission (JRC);
# Licensed under the EUPL (the 'Licence');
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at: http://ec.europa.eu/idabc/eupl
"""
Defines schema, defaults and validations for data consumed/produced by :class:`~.experiment.Experiment`.

The datamodel-instance is managed by :class:`pandel.Pandel`.

>>> from wltp.datamodel import *
>>> __name__ = "wltp.datamodel"
"""

import copy
import functools as fnt
import itertools as itt
import logging
import operator as ops
from collections import abc as cabc
from textwrap import dedent
from typing import Mapping
from typing import Sequence as Seq
from typing import Tuple, Union

import jsonschema
import numpy as np
import pandas as pd
from jsonschema import RefResolver, ValidationError
from numpy import ndarray
from pandas.core.generic import NDFrame

from pandalone.pandata import PandelVisitor

from . import engine
from . import io as wio
from . import nmindrive, utils
from .cycles import class1, class2, class3

try:
    import importlib.resources as pkg_resources
except ImportError:
    # Try backported to PY<37 `importlib_resources`.
    import importlib_resources as pkg_resources  # type: ignore
try:
    from pandas.core.common import PandasError
except ImportError:
    ## Pandas-0.20.1 dropped this class.
    #  See https://github.com/pydata/pandas-datareader/issues/305
    PandasError = ValueError


log = logging.getLogger(__name__)


def get_model_base() -> dict:
    """The base model for running a WLTC experiment.

    It contains some default values for the experiment
    but this model is not valid - you need to override its attributes.

    :return: a tree with the default values for the experiment.
    """

    instance: dict = {
        "unladen_mass": None,
        "test_mass": None,
        "p_rated": None,
        "n_rated": None,
        "n_idle": None,
        "n_min": None,
        "n2v_ratios": [],
        "wltc_data": get_wltc_data(),
    }

    return instance


def upd_default_load_curve(mdl, engine_type="petrol"):
    """Some default 'full-load-curve' for the vehicles """
    import json

    ## Form old accdb, c.2015.
    wots = json.loads(
        """{
    "petrol": [
      0.1, 0.11100069, 0.12200138, 0.13300206, 0.14400275, 0.15500344, 0.16600413, 0.17700482,
      0.1880055, 0.19900619, 0.21000688, 0.22100757, 0.23200826, 0.24300895, 0.25400963,
      0.26501032, 0.27506528, 0.28512023, 0.29517519, 0.30523015, 0.3152851, 0.3231181,
      0.3309511, 0.3387841, 0.3466171, 0.3544501, 0.3622831, 0.37011609, 0.37794909, 0.38578209,
      0.39361509, 0.40268373, 0.41175238, 0.42082102, 0.42988967, 0.43895831, 0.44802696,
      0.4570956, 0.46616424, 0.47523289, 0.48430153, 0.49385337, 0.5034052, 0.51295704,
      0.52250887, 0.53206071, 0.54161255, 0.55116438, 0.56071622, 0.57026805, 0.57981989,
      0.58873474, 0.59764959, 0.60656444, 0.61547929, 0.62439414, 0.633309, 0.64222385, 0.6511387,
      0.66005355, 0.6689684, 0.67815415, 0.6873399, 0.69652565, 0.70571139, 0.71489714,
      0.72408289, 0.73326864, 0.74245439, 0.75164013, 0.76082588, 0.77026954, 0.77971321,
      0.78915687, 0.79860054, 0.8080442, 0.81748786, 0.82693153, 0.83637519, 0.84581885,
      0.85526252, 0.86393898, 0.87261544, 0.8812919, 0.88996837, 0.89864483, 0.90732129,
      0.91599775, 0.92467422, 0.93335068, 0.94202714, 0.94782443, 0.95362171, 0.959419,
      0.96521628, 0.97101357, 0.97681086, 0.98260814, 0.98840543, 0.99420271, 1.0, 0.99556631,
      0.99113261, 0.98669892, 0.98226523, 0.97783154, 0.97339784, 0.96896415, 0.96453046,
      0.96009677, 0.95566307, 0.94509677, 0.93453046, 0.92396415, 0.91339784, 0.90283154,
      0.89226523, 0.88169892, 0.87113261, 0.86056631, 0.85
    ],
    "diesel": [
        0.1, 0.11632768, 0.13265536, 0.14898304, 0.16531072, 0.1816384, 0.19796609, 0.21429377,
        0.23062145, 0.24694913, 0.26327681, 0.27956221, 0.29584762, 0.31213302, 0.32841843,
        0.34470383, 0.36098924, 0.37727464, 0.39356004, 0.40984545, 0.42613085, 0.44289144,
        0.45965203, 0.47641262, 0.49317321, 0.5099338, 0.52669439, 0.54345498, 0.56021557,
        0.57697616, 0.59373675, 0.60775731, 0.62177786, 0.63579841, 0.64981897, 0.66383952,
        0.67786007, 0.69188063, 0.70590118, 0.71992173, 0.73394229, 0.74334518, 0.75274808,
        0.76215098, 0.77155387, 0.78095677, 0.79035967, 0.79976256, 0.80916546, 0.81856836,
        0.82797126, 0.83355082, 0.83913039, 0.84470996, 0.85028953, 0.8558691, 0.86144867,
        0.86702823, 0.8726078, 0.87818737, 0.88376694, 0.88861739, 0.89346785, 0.8983183,
        0.90316876, 0.90801921, 0.91286967, 0.91772013, 0.92257058, 0.92742104, 0.93227149,
        0.93551314, 0.93875479, 0.94199644, 0.94523809, 0.94847974, 0.95172139, 0.95496304,
        0.95820469, 0.96144634, 0.96468798, 0.96645067, 0.96821335, 0.96997604, 0.97173872,
        0.97350141, 0.97526409, 0.97702678, 0.97878946, 0.98055215, 0.98231483, 0.98408335,
        0.98585187, 0.98762038, 0.9893889, 0.99115742, 0.99292593, 0.99469445, 0.99646297,
        0.99823148, 1.0, 0.98871106, 0.97742212, 0.96613319, 0.95484425, 0.94355531, 0.93226637,
        0.92097743, 0.9096885, 0.89839956, 0.88711062, 0.88339956, 0.8796885, 0.87597743,
        0.87226637, 0.86855531, 0.86484425, 0.86113319, 0.85742212, 0.85371106, 0.85
    ]}
    """
    )
    n_norm = np.arange(0.0, 1.21, 0.01)
    #        petrol = np.polyval([-1.0411, 1.3853, -0.5647, 1.1107, 0.0967], n_norm).tolist()
    #        diesel = np.polyval([-0.909, 1.9298, -2.2212, 2.088, 0.095], n_norm).tolist()
    mdl["wot"] = {"n_norm": n_norm, "p_norm": wots[engine_type]}

    return mdl


def upd_resistance_coeffs_regression_curves(mdl):
    mdl["resistance_coeffs_regression_curves"] = [
        [1.40e-01, 7.86e-01],
        [2.75e-05, -3.29e-02],
        [1.11e-05, 2.03e-02],
    ]

    return mdl


def get_wltc_data():
    """The WLTC-data required to run an experiment (the class-cycles and their attributes)..

    Prefer to access wltc-data through :func:`get_class()`, or
    from :samp:`{datamodel}['wltc_data']`,

    :return: a tree
    """

    ## See schemas for explanations.
    ##
    wltc_data = {
        "classes": {
            "class1": class1.class_data(),
            "class2": class2.class_data(),
            "class3a": class3.class_data_a(),
            "class3b": class3.class_data_b(),
        }
    }

    return wltc_data


_model_url = "/data"
_wltc_url = "/wltc"


@fnt.lru_cache()
def _get_model_schema(additional_properties=False) -> dict:
    """
    :param bool additional_properties:
      when False, 4rd-step(validation) will scream on any non-schema property found.
      The json-schema(dict) for input/output of the WLTC experiment.

    .. Warning::
      Do not modify, or they will affect all future operations
    """
    yaml_text = pkg_resources.read_text(__package__, "data-schema.yaml")
    schema: dict = utils.yaml_load(yaml_text)  # type: ignore
    schema["additionalProperties"] = additional_properties
    return schema


@fnt.lru_cache()
def _get_wltc_schema() -> dict:
    """
    The json-schema for the WLTC-data required to run a WLTC experiment.

    .. Warning::
      Do not modify, or they will affect all future operations
    """
    yaml_text = pkg_resources.read_text(__package__, "wltc-schema.yaml")
    return utils.yaml_load(yaml_text)  # type: ignore


######
# Cached Schemas timings:
#
### UNCACHED
# %timeit dm._get_model_schema()
# 43.8 ms ± 334 µs per loop (mean ± std. dev. of 7 runs, 10 loops each)
#
# %timeit dm.get_model_schema()
# 48.9 ms ± 361 µs per loop (mean ± std. dev. of 7 runs, 10 loops each)
#
### LRU CACHED
#
# %timeit dm._get_model_schema()
# 66.8 ns ± 0.404 ns per loop (mean ± std. dev. of 7 runs, 10000000 loops each)
#
# %timeit dm.get_model_schema()
# 4.77 ms ± 20.7 µs per loop (mean ± std. dev. of 7 runs, 100 loops each)
######


def get_model_schema(additional_properties=False):
    """Schema of the input data; you may freely modify them. """
    return copy.deepcopy(_get_model_schema(additional_properties))


def get_wltc_schema():
    """Schema of the wLTC data; you may freely modify them. """
    return copy.deepcopy(_get_wltc_schema())


def get_class_part_names(cls_name=None):
    """
    :param str cls_name: one of 'class1', ..., 'class3b', if missing, returns all 4 part-names
    """
    if cls_name == "class1":
        part_names = ["Low1", "Medium", "Low2"]
    else:
        part_names = ["Low", "Medium", "High", "ExtraHigh"]

    if cls_name:
        wltc_data = get_wltc_data()
        cls = wltc_data["classes"][cls_name]
        part_names = part_names[: len(cls["lengths"]) + 1]

    return part_names


def get_class_names(mdl=None) -> pd.DataFrame:
    wltc_data = get_wltc_data() if mdl is None else mdl["wltc_data"]
    return list(wltc_data["classes"].keys())


def get_class(wltc_class: Union[str, int], mdl=None) -> dict:
    """
    Fetch the wltc-data for a specific class.

    :param wltc_class:
        one of 'class1', ..., 'class3b' or its index 0,1, ... 3

    .. note::
        For pipeline use :func:`.cycles.get_wltc_class_data()`.
    """
    if mdl:
        wltc_data = mdl["wltc_data"]
    else:
        wltc_data = get_wltc_data()

    classes = wltc_data["classes"]
    if isinstance(wltc_class, int):
        class_name = list(classes.keys())[wltc_class]
    else:
        class_name = wltc_class

    return classes[class_name]


def get_class_parts_limits(
    wltc_class: Union[str, int], edges=False
) -> Tuple[Tuple[int, int], ...]:
    """
    Parses the supplied in wltc_data and extracts the part-limits for the specified class-name.

    :param wltc_class:
        one of 'class1', ..., 'class3b' or its index 0,1, ... 3
    :param edges:
        when `True`, internal limits are wrapped within [0, ..., len]

    :return:
        a list of ints with the part-limits, ie for class-3a these are 3 numbers (or 5 if `edge`)

    .. note::
        For pipeline use :func:`.cycles.get_class_phase_boundaries()`.

    Example:

    >>> from wltp import datamodel
    >>> import pandas as pd

    >>> cls = 'class2'
    >>> part_limits = datamodel.get_class_parts_limits(cls)
    >>> part_limits
    (589, 1022, 1477)
    >>> part_limits = datamodel.get_class_parts_limits(cls, edges=True)
    >>> part_limits
    (0,  589, 1022, 1477, 1800)

    And these are the limits for acceleration-dependent items:

    >>> cls_data = datamodel.get_wltc_data()['classes'][cls]
    >>> V = pd.DataFrame(cls_data['V_cycle'])
    >>> V.groupby(pd.cut(V.index, part_limits)).sum()
                  V_cycle
    (0, 589]      11162.2
    (589, 1022]   17054.3
    (1022, 1477]  24450.6
    (1477, 1800]  28869.8

    """
    cls = get_class(wltc_class)
    part_limits = np.cumsum(cls["lengths"])
    if edges:
        part_limits = [0, *part_limits[:-1], part_limits[-1]]
    else:
        part_limits = part_limits[:-1]

    return tuple(part_limits)


def get_class_pmr_limits(edges=False) -> list:
    """
    Parses the supplied in wltc_data and extracts the part-limits for the specified class-name.

    :param edges:
        when `True`, embeds internal limits into (0, len)

    :return:
        a list with the pmr-limits (2 numbers)

    .. note::
        For pipeline use :term:`jsonp` dependencies into ``wltc_class_data``.
    """
    wltc_data = get_wltc_data()

    pmr_limits_pairs = [cls["pmr_limits"] for cls in wltc_data["classes"].values()]
    pmr_limits = sorted(set(itt.chain(*pmr_limits_pairs)))
    if not edges:
        pmr_limits = pmr_limits[1:-1]  ## Exclude 0 and inf

    return pmr_limits


def get_class_v_cycle(wltc_class: Union[str, int]) -> pd.Series:
    """
    Fetch the `v-cycle` for a class with the proper `t` in index.

    :param wltc_class:
        one of 'class1', ..., 'class3b' or its index 0,1, ... 3
    :return:
        a series containing :math:`length + 1` samples, numbered from 0 to `length`,
        where `length` is the duration of the cycle in seconds.
    """
    cls = get_class(wltc_class)
    V = cls["V_cycle"]
    assert isinstance(V, pd.Series)

    return V


def merge(a, b, path=[]):
    """'merges b into a"""

    for key in b.keys():
        bv = b[key]
        if key in a:
            av = a[key]
            if isinstance(av, cabc.Mapping) != isinstance(bv, cabc.Mapping):
                log.debug(
                    "Dict-values conflict at '%s'! a(%s) != b(%s)",
                    "/".join(path + [str(key)]),
                    type(av),
                    type(bv),
                )
                pass
            elif av is bv:
                continue  # same leaf value
            elif isinstance(av, cabc.Mapping):
                merge(av, bv, path + [str(key)])
                continue
        a[key] = bv
    return a


# works
# print(merge({1:{"a":"A"},2:{"b":"B"}}, {2:{"c":"C"},3:{"d":"D"}}))
# # has conflict
# merge({1:{"a":"A"},2:{"b":"B"}}, {1:{"a":"A"},2:{"b":"C"}})


@fnt.lru_cache()
def model_validator(
    additional_properties=False, validate_wltc_data=False, validate_schema=False
) -> PandelVisitor:
    ## NOTE: Using non-copied (mode, wltc)-schemas,
    #  since we are certain they will not be modified here.
    #
    schema = _get_model_schema(additional_properties)
    wltc_schema = (
        _get_wltc_schema() if validate_wltc_data else {}
    )  ## Do not supply wltc schema, for speedup.
    resolver = RefResolver(_model_url, schema, store={_wltc_url: wltc_schema})

    validator = PandelVisitor(
        schema,
        resolver=resolver,
        auto_default=True,
        auto_default_nulls=True,
        auto_remove_nulls=True,
    )
    if validate_schema:
        ## Patch jsonschema-schema for extra fields & forbid miss-spells.
        #  See https://github.com/Julian/jsonschema/issues/268
        #
        stricter_metaschema = {
            **validator.META_SCHEMA,
            "additionalProperties": False,
            "properties": {
                **validator.META_SCHEMA["properties"],
                "tags": {
                    "description": "Data item extra label e.g. input/output or use/purpose.",
                    "type": "array",
                    "items": {"type": "string"},
                    "uniqueItems": True,
                },
                "units": {
                    "description": "Default units of the quantity, by `pint` library.",
                    "type": "string",
                },
                # For extension https://sphinx-jsonschema.readthedocs.io/en/latest/schemakeywords.html
                "$$target": {"type": ["string", "array"]},
            },
        }
        strictValidator = jsonschema.validators.validator_for(stricter_metaschema)
        strictValidator(stricter_metaschema).validate(schema)

    return validator


## TODO: drop yield-error method, locality of errors is lost on debug.
def validate_model(
    mdl,
    additional_properties=False,
    iter_errors=False,
    validate_wltc_data=False,
    validate_schema=False,
):
    """
    :param bool iter_errors: does not fail, but returns a generator of ValidationErrors

    >>> validate_model(None)
    Traceback (most recent call last):
    jsonschema.exceptions.ValidationError: None is not of type 'object'
    ...

    >>> mdl = get_model_base()
    >>> err_generator = validate_model(mdl, iter_errors=True)
    >>> sorted(err_generator, key=hash)
    [<ValidationError:
    ...

    >>> mdl = get_model_base()
    >>> mdl.update({
    ...     "unladen_mass":1230,
    ...     "test_mass":   1300,
    ...     "p_rated": 110.625,
    ...     "n_rated": 5450,
    ...     "n_idle":  950,
    ...     "n_min":   500,
    ...     "n2v_ratios":[120.5, 75, 50, 43, 33, 28],
    ...     "f0": 100,
    ...     "f1": 0.5,
    ...     "f2": 0.04,
    ... })
    >>> mdl = upd_default_load_curve(mdl);
    >>> err_generator = validate_model(mdl, iter_errors=True)
    >>> list(err_generator)
    []
    """

    validator = model_validator(
        additional_properties=additional_properties,
        validate_wltc_data=validate_wltc_data,
    )
    validators = [
        validator.iter_errors(mdl),
        yield_n_min_errors(mdl),
        yield_load_curve_errors(mdl),
    ]
    errors = itt.chain(*[v for v in validators if not v is None])

    if iter_errors:
        return errors
    else:
        for error in errors:
            raise error


def yield_load_curve_errors(mdl):
    d = wio.pstep_factory.get()

    wot = mdl.get("wot")
    if wot is None or mdl is None:
        # Bail out, jsonschema errors already reported.
        return

    try:
        mdl["wot"] = wot = engine.parse_wot(wot)
    except Exception as ex:
        yield ValidationError("Failed parsing wot due to: %s" % ex, cause=ex)

    try:
        n_idle = mdl[d.n_idle]
        n_rated = mdl[d.n_rated]
        p_rated = mdl[d.p_rated]

        wot = engine.denorm_wot(wot, n_idle, n_rated, p_rated)
        wot = engine.norm_wot(wot, n_idle, n_rated, p_rated)
    except KeyError as ex:
        ## Jsonschema checked them already.
        yield ValidationError(
            f"Cannot validate further wot, missing rated values from inputs! {ex}"
        )
        return
    except Exception as ex:
        yield ValidationError(f"Failed (de)normalizing wot due to: {ex}")
        return

    n_min_drive_set = mdl.get(d.n_min_drive_set)
    for err in engine.validate_wot(wot, n_idle, n_rated, p_rated, n_min_drive_set):
        raise err


def yield_n_min_errors(mdl):
    """
    .. TODO:
      Validate min(Nwot) <= n_min_drive_set.
    """
    d = wio.pstep_factory.get()
    # g = wio.pstep_factory.get().gears

    if not mdl.get(d.n_rated) or not mdl.get(d.n_rated):
        # Bail out, jsonschema errors already reported.
        return

    # sol = mdl_2_n_min_drives.compute(mdl2, "n_min_drives")
    sol = nmindrive.mdl_2_n_min_drives.compute(mdl)
    err = sol.check_if_incomplete()
    if err:
        yield err
    nmins = sol["n_min_drives"]

    for k, v in nmins._asdict().items():
        mdl[k] = v


if __name__ == "__main__":
    ## Using private schemas below, we're certain it's not modified.
    #
    print(f"WLTC: \n{utils.yaml_dumps(_get_model_schema())}")
    print(f"INPUT: \n{utils.yaml_dumps(_get_wltc_schema())}")
    print(f"MODEL: \n{utils.yaml_dumps(get_model_base())}")
