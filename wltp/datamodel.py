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

.. testsetup::

  from wltp.datamodel import *
"""

import copy
import functools as fnt
import itertools as it
import logging
import operator as ops
from collections.abc import Mapping, Sized
from textwrap import dedent
from typing import Sequence as Seq
from typing import Union

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
        "gear_ratios": [],
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

    .. Note::
      Do not modify, or they will affect all future operations
    """
    return utils.yaml_loads(  # type: ignore
        f"""
$schema: http://json-schema.org/draft-07/schema#
$id: {_model_url}
title: Json-schema describing the input for a WLTC simulator.
type: object
additionalProperties: {additional_properties}
description:
  The vehicle attributes required for generating the WLTC velocity-profile
  downscaling and gear-shifts.
properties:
  id:
    title: Any identifier for the object
    type:
    - integer
    - string
  unladen_mass:
    title: vehicle unladen mass
    type:
    - number
    exclusiveMinimum: 0
    description:
      The mass (kg) of the vehicle without the driver, used to decide its class,
      as defined in Annex-4
  test_mass:
    title: vehicle test mass
    $ref: '#/definitions/positiveNumber'
    description:
      The test mass of the vehicle used in all calculations (kg),
      as defined in Annex 4.2.1.3.1, pg 94.
  v_max:
    title: maximum vehicle velocity
    type:
    - number
    exclusiveMinimum: 0
    description: (OUT) The calculated maximum velocity, as defined in Annex 2-2.i.
  n_vmax:
    title: engine speed for maximum vehicle velocity
    type:
    - number
    exclusiveMinimum: 0
    description: (OUT) The engine speed for `v_max`.
  g_vmax:
    title: gear for maximum vehicle velocity
    type:
    - number
    exclusiveMinimum: 0
    description: (OUT) The gear for achieving `v_max`.
  p_rated:
    title: maximum rated power
    $ref: '#/definitions/positiveNumber'
    description:
      The maximum rated engine power (kW) as declared by the manufacturer.
  n_rated:
    title: rated engine revolutions
    $ref: '#/definitions/positiveNumber'
    description: |2
      The rated engine revolutions at which an engine develops its maximum power.
      If the maximum power is developed over an engine revolutions range,
      it is determined by the mean of this range.
  n_idle:
    title: idling revolutions
    $ref: '#/definitions/positiveNumber'
    description: The idling engine revolutions (Annex 1).
  n_min:
    title: minimum engine revolutions
    type:
    - array
    - number
    description: |2
      Either a number with the minimum engine revolutions for gears > 2 when the vehicle is in motion,
      or an array with the exact `n_min` for each gear (array must have length equal to gears).

      If unspecified, the minimum `n` for gears > 2 is determined by the following equation:

          n_min = n_idle + f_n_min(=0.125) * (n_rated - n_idle)

      Higher values may be used if requested by the manufacturer, by setting this one.
  gear_ratios:
    title: gear ratios
    $ref: '#/definitions/positiveNumbers'
    maxItems: 24
    minItems: 3
    description:
      An array with the gear-ratios obtained by dividing engine-revolutions
      (1/min) by vehicle-velocity (km/h).
  f0:
    title: driving resistance coefficient f0
    type:
    - number
    description: The driving resistance coefficient f0, in N (Annex 4).
  f1:
    title: driving resistance coefficient f1
    type:
    - number
    description: The driving resistance coefficient f1, in N/(km/h) (Annex 4).
  f2:
    title: driving resistance coefficient f2
    type:
    - number
    description: The driving resistance coefficient f2, in N/(km/h)² (Annex 4).
  n_min_drive1:
    description: "[1/min], see Annex 2-2.k, n_min for gear 1"
    type:
    - number
    exclusiveMinimum: 0
  n_min_drive2_up:
    description: "[1/min], Annex 2-2.k"
    type:
    - number
    exclusiveMinimum: 0
  n_min_drive2_stopdecel:
    description: "[1/min], Annex 2-2.k"
    type:
    - number
    exclusiveMinimum: 0
  n_min_drive2:
    description: "[1/min], Annex 2-2.k"
    type:
    - number
    exclusiveMinimum: 0
  n_min_drive_set:
    description: |
      [1/min], Annex 2-2.k,
      calculated minimum engine speed for gears > 2:

        n_min_drive = n_idle + 0.125 (n_rated - n_idle)

      Do not override this, its value will be ignored.
      Set higher values only into parameters n_min_drive_up/down.

      Matlab call this `CalculatedMinDriveEngineSpeedGreater2nd`.
    type:
    - number
    exclusiveMinimum: 0
  n_min_drive_up:
    description: "[1/min], Annex 2-2.k"
    type:
    - number
    exclusiveMinimum: 0
  n_min_drive_up_start:
    description: "[1/min], Annex 2-2.k"
    type:
    - number
    exclusiveMinimum: 0
  n_min_drive_down:
    description: "[1/min], Annex 2-2.k"
    type:
    - number
    exclusiveMinimum: 0
  n_min_drive_down_start:
    description: '[1/min], Annex 2-2.k'
    type:
    - number
    exclusiveMinimum: 0
  t_cold_end:
    description: see Annex 2-2.k about n_mins
    type:
    - number
    minimum: 0
    default: 0
  wot:
    title: wide open throttle curves
    description: |2
      An array/dict/dataframe holding the full load power curves for (at least) 2 columns ('n', 'p')
      or the normalized values ('n_norm', 'p_norm').

      Example:

          np.array([
              [ 600, 1000, ... 7000 ],
              [ 4, 10, ... 30 ]
          ]).T

      * The 1st column or `n` is the engine revolutions in min^-1:
      * The 2nd column or `p` is the full-power load in kW:

      Normalized N/P Example:

          np.array([
              [ 0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120 ],
              [ 6.11, 21.97, 37.43, 51.05, 62.61, 72.49, 81.13, 88.7, 94.92, 98.99, 100., 96.28, 87.66 ]
          ]).T

      * The 1st column or `n_norm` is the normalized engine revolutions, within [0.0, 1.20]:

                  n_norm = (n - n_idle) / (n_rated  - n_idle)

      * The 2nd column or `p_norm` is the normalized values of the full-power load against the p_rated,
        within [0, 1]:

                  p_norm = p / p_rated
    type:
    - object
    - array
  grid_wots:
    description: |2
      A dataframe with 2-level columns (item, gear)
      - `p_avail_stable`: reduced by safety-margin, but not by ASM
      - `p_avail`: reduced by both SM & ASM
      - `p_resist`: road loads power
      - `p_req`: road loads & cycle power
  pmr:
    title: Power to Unladen-Mass
    description: Power/unladen-Mass ratio (W/kg).
    type: number
  wltc_class:
    description:
      The name of the WLTC-class (found within WLTC-data/classes) as
      selected by the experiment.
    type: string
    enum:
    - class1
    - class2
    - class3a
    - class3b
  resistance_coeffs_regression_curves:
    description:
      Regression curve factors for calculating vehicle's `resistance_coeffs`
      when missing.
    type: array
    minItems: 3
    maxItems: 3
    items:
      type: array
      minItems: 2
      maxItems: 2
      items:
        type: number
  f_dsc_threshold:
    title: Downscale-factor threshold
    description:
      The limit for the calculated `f_dsc` below which no downscaling
      happens.
    type:
    - number
    default: 0.01
  f_dsc_decimals:
    title: Downscale-factor rounding decimals
    type:
    - number
    default: 3
  driver_mass:
    title: Driver's mass (kg)
    description: |2
      The mass (kg) of the vehicle's driver (Annex 1-3.2.6, p9), where:

          Unladen_mass = Test_mass - driver_mass
    type:
    - number
    default: 75
  v_stopped_threshold:
    description: Velocity (km/h) under which (<=) to idle gear-shift (Annex 2-3.3, p71).
    type:
    - number
    default: 1
  f_inertial:
    description:
      This is the `kr` inertial-factor used in the 2nd part of the
      formula for calculating required-power (Annex 2-3.1).
    type:
    - number
    default: 1.03
  f_safety_margin:
    description: |2
      Safety-margin(SM) factor for load-curve (Annex 2-3.4).
    type:
    - number
    default: 0.1
  f_n_min:
    description:
      For each gear > 2, N :> n_min = n_idle + f_n_min * n_range (unless
      `n_min` overridden by manufacturer)
    type:
    - number
    default: 0.125
  f_n_min_gear2:
    description: Gear-2 is invalid when N :< f_n_min_gear2 * n_idle.
    type:
    - number
    default: 0.9
  f_n_clutch_gear2:
    description: |2
      A 2-value number-array(f1, f2) controlling when to clutch gear-2:
          N < n_clutch_gear2 := max(f1 * n_idle, f2 * n_range + n_idle),
      unless "clutched"...
    type:
    - array
    default:
    - 1.15
    - 0.03
  f_dsc:
    description: |2
      The downscaling-factor as calculated by the experiment (Annex 1-8.3).

      Set it to 0 to disable downscaling, (or to any other value to force it).
    type: number
  b_no_g0_downshift:
    description: |2
      a flag to suppress shifting to gear-0(idle) during downshifts
    type: boolean
  wltc_data:
    $ref: {_wltc_url}
  cycle:
    description: |2
      An inp/out dataframe matrix with 2-level columns(item, gear),
      and items, in addition to those of `grid_wots`:
      - `v_cycle`: reduced by safety-margin, but not by ASM
      - `v_dsc`: (optional)
      - `v_target`: road loads power
      - `(ok_..., gN)`: rflags denoting the validity of certain conditions for gear-N
      - `g_max0`: does not include corrections for the `g1-->g2 n_min` rule,
        nor points with insufficient power.
definitions:
  positiveInteger:
    type: integer
    exclusiveMinimum: 0
  positiveNumber:
    type: number
    exclusiveMinimum: 0
  positiveIntegers:
    type: array
    items:
      $ref: '#/definitions/positiveInteger'
  positiveNumbers:
    type: array
    items:
      $ref: '#/definitions/positiveNumber'
# Must follow `properties` due to `autoRemoveNull`.
required:
- f0
- f1
- f2
- test_mass
- p_rated
- n_rated
- n_idle
- gear_ratios
- wot
- driver_mass
- v_stopped_threshold
- f_inertial
- f_safety_margin
- f_n_min
- f_n_min_gear2
- f_n_clutch_gear2
- wltc_data
    """
    )


@fnt.lru_cache()
def _get_wltc_schema() -> dict:
    """
    The json-schema for the WLTC-data required to run a WLTC experiment.

    .. Note::
      Do not modify, or they will affect all future operations
    """
    return utils.yaml_loads(  # type: ignore
        f"""
$schema: http://json-schema.org/draft-07/schema#
$id: {_wltc_url}
title: WLTC data
type: object
additionalProperties: false
required:
- classes
properties:
  classes:
    type: object
    additionalProperties: false
    required:
    - class1
    - class2
    - class3a
    - class3b
    properties:
      class1:
        $ref: '#definitions/class'
      class2:
        $ref: '#definitions/class'
      class3a:
        $ref: '#definitions/class'
      class3b:
        $ref: '#definitions/class'
definitions:
  class:
    title: WLTC class data
    type: object
    additionalProperties: false
    properties:
      pmr_limits:
        title: PMR (low, high]
        description:
          Power_To_unladen-Mass ratio-limits ((low, high], W/kg) used to
          select classes (Annex 1, p19).
        type: array
        items:
          type: number
        minItems: 2
        maxItems: 2
      velocity_limits:
        description:
          Velocity-limits ([low, high), km/h) within which (<) version-a/b
          from class3 is selected (Annex 1, p19).
        type: array
        items:
          type: number
        minItems: 2
        maxItems: 2
      parts:
        type: array
        items:
          type: integer
      downscale:
        type: object
        additionalProperties: false
        properties:
          phases:
            type: array
            description: triplet (start, tip, end); start & end remain unchanged
            items:
              $ref: data#definitions/positiveInteger
            maxItems: 3
            minItems: 3
            additionalItems: false
          decel_phase:
            type: array
            additionalItems: false
            items:
              type: integer
            maxItems: 2
            minItems: 2
          p_max_values:
            type: object
            properties:
              time:
                type: number
              v:
                type: number
              a:
                type: number
            additionalProperties: false
            required:
            - time
            - v
            - a
          factor_coeffs:
            type: array
        required:
        - phases
        - p_max_values
        - factor_coeffs
      checksum:
        type: number
      part_checksums:
        type: array
        items:
          type: number
      v_cycle:
        type: array
        items:
          type: number
        minItems: 906
    required:
    - pmr_limits
    - parts
    - downscale
    - v_cycle
    """
    )


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
        part_names = part_names[: len(cls["parts"]) + 1]

    return part_names


def get_class_names(mdl=None) -> pd.DataFrame:
    wltc_data = get_wltc_data() if mdl is None else mdl["wltc_data"]
    return list(wltc_data["classes"].keys())


def get_class(class_id: Union[str, int], mdl=None) -> dict:
    """
    Fetch the wltc-data for a specific class.

    :param class_id:
        one of 'class1', ..., 'class3b' or its index 0,1, ... 3
    """
    if mdl:
        wltc_data = mdl["wltc_data"]
    else:
        wltc_data = get_wltc_data()

    classes = wltc_data["classes"]
    if isinstance(class_id, int):
        class_name = list(classes.keys())[class_id]
    else:
        class_name = class_id

    return classes[class_name]


def get_class_parts_limits(class_id: Union[str, int], mdl=None, edges=False):
    """
    Parses the supplied in wltc_data and extracts the part-limits for the specified class-name.

    :param class_id:
        one of 'class1', ..., 'class3b' or its index 0,1, ... 3
    :param mdl: the mdl to parse wltc_data from, if omitted, parses the results of :func:`get_wltc_data()`
    :param edges: when `True`, embeds internal limits inside [0, ..., len]
    :return: a list of ints with the part-limits, ie for class-3a these are 3 numbers (or 5 if `edge`)

    Example:

    >>> from wltp import datamodel
    >>> import pandas as pd

    >>> cls = 'class2'
    >>> part_limits = datamodel.get_class_parts_limits(cls)
    >>> part_limits
    [589, 1022, 1477]
    >>> part_limits = datamodel.get_class_parts_limits(cls, edges=True)
    >>> part_limits
    [0,  589, 1022, 1477, 1801]

    And these are the limits for acceleration-dependent items:

    >>> cls_data = datamodel.get_wltc_data()['classes'][cls]
    >>> V = pd.DataFrame(cls_data['v_cycle'])
    >>> V.groupby(pd.cut(V.index, part_limits)).sum()
                  v_cycle
    (0, 589]      11162.2
    (589, 1022]   17054.3
    (1022, 1477]  24450.6
    (1477, 1801]  28869.8

    """
    cls = get_class(class_id)
    part_limits = cls["parts"]
    if edges:
        part_limits.insert(0, 0)
        part_limits.append(len(cls["v_cycle"]))

    return part_limits


def get_class_pmr_limits(mdl=None, edges=False):
    """
    Parses the supplied in wltc_data and extracts the part-limits for the specified class-name.

    :param mdl: the mdl to parse wltc_data from, if omitted, parses the results of :func:`get_wltc_data()`
    :param edges: when `True`, embeds internal limits into (0, len)
    :return: a list with the pmr-limits (2 numbers)
    """
    if mdl:
        wltc_data = mdl["wltc_data"]
    else:
        wltc_data = get_wltc_data()

    pmr_limits_pairs = [cls["pmr_limits"] for cls in wltc_data["classes"].values()]
    pmr_limits = sorted(set(it.chain(*pmr_limits_pairs)))
    if not edges:
        pmr_limits = pmr_limits[1:-1]  ## Exclude 0 and inf

    return pmr_limits


def get_class_v_cycle(class_id: Union[int, str], mdl=None) -> pd.Series:
    """
    Fetch the `v-cycle` for a class with the proper `t` in index.

    :param class_id:
        one of 'class1', ..., 'class3b' or its index 0,1, ... 3
    :return:
        a series containing :math:`length + 1` samples, numbered from 0 to `length`,
        where `length` is the duration of the cycle in seconds.
    """
    cls = get_class(class_id)
    V = cls["v_cycle"]
    assert isinstance(V, pd.Series)

    return V


def merge(a, b, path=[]):
    """'merges b into a"""

    for key in b.keys():
        bv = b[key]
        if key in a:
            av = a[key]
            if isinstance(av, Mapping) != isinstance(bv, Mapping):
                #                 log.debug("Dict-values conflict at '%s'! a(%s) != b(%s)",
                #                                 '/'.join(path + [str(key)]), type(av), type(bv))
                pass
            elif av is bv:
                continue  # same leaf value
            elif isinstance(av, Mapping):
                merge(av, bv, path + [str(key)])
                continue
        a[key] = bv
    return a


# works
# print(merge({1:{"a":"A"},2:{"b":"B"}}, {2:{"c":"C"},3:{"d":"D"}}))
# # has conflict
# merge({1:{"a":"A"},2:{"b":"B"}}, {1:{"a":"A"},2:{"b":"C"}})


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
        # See https://github.com/Julian/jsonschema/issues/268
        stricter_metaschema = dict(validator.META_SCHEMA, additionalProperties=False)
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
    ...     "gear_ratios":[120.5, 75, 50, 43, 33, 28],
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
        yield_forced_cycle_errors(mdl, additional_properties),
    ]
    errors = it.chain(*[v for v in validators if not v is None])

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


def yield_forced_cycle_errors(mdl, additional_properties):
    forced_cycle = mdl.get("forced_cycle")
    if not forced_cycle is None:
        try:
            if not isinstance(forced_cycle, pd.DataFrame):
                forced_cycle = pd.DataFrame(forced_cycle)
                if forced_cycle.shape[0] == forced_cycle.shape[1]:
                    yield ValidationError(
                        "The force_cycle is a square matrix(%s), cannot decide orientation!"
                        % (forced_cycle.shape,)
                    )
            if forced_cycle.shape[0] < forced_cycle.shape[1]:
                forced_cycle = forced_cycle.T
            cols = forced_cycle.columns

            # if not additional_properties and not set(cols) <= set(['v','slide']):
            #     yield ValidationError('Unexpected columns!')

            if forced_cycle.shape[1] == 1:
                if cols[0] == 1:
                    log.warning(
                        "Assuming the unamed single-column to be the velocity_profile(%s).",
                        cols[0],
                    )
                    forced_cycle.columns = ["v"]

            mdl["forced_cycle"] = forced_cycle
        except PandasError as ex:
            yield ValidationError("Invalid forced_cycle, due to: %s" % ex, cause=ex)


if __name__ == "__main__":
    ## Using private schemas below, we're certain it's not modified.
    #
    print(f"WLTC: \n{utils.yaml_dumps(_get_model_schema())}")
    print(f"INPUT: \n{utils.yaml_dumps(_get_wltc_schema())}")
    print(f"MODEL: \n{utils.yaml_dumps(get_model_base())}")
