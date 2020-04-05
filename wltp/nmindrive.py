#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2013-2020 European Commission (JRC);
# Licensed under the EUPL (the 'Licence');
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at: http://ec.europa.eu/idabc/eupl
"""
Calculate/Validate *n_min_drive* parameters, defined mostly in Annex 2-2.k.

.. testsetup::

  from wltp.nmindrive import *
"""

from collections import namedtuple
from typing import Union

from jsonschema import ValidationError

from graphtik import arg, compose, sideffect

from . import io as wio
from .autograph import Autograph, FnHarvester, autographed
from .invariants import nround1, nround10

m = wio.pstep_factory.get()


# calc_n_idle_R = autographed(needs="n_idle", provides="n_idle_R")(fn=nround10)
def calc_n_idle_R(n_idle: float) -> int:
    return nround10(n_idle)


def calc_n_rated_R(n_rated: float) -> int:
    return nround1(n_rated)


@autographed(out_sideffects=["valid: n_rated", "valid: n_idle"])
def validate_n_rated_above_n_idle(n_idle_R, n_rated_R):
    if n_rated_R <= n_idle_R:
        raise ValidationError(
            f"{m.n_rated}({n_rated_R}) must be higher than {m.n_idle}({n_idle_R}!"
        )


def calc_n_min_drive_set(n_idle_R: int, n_rated_R: float) -> float:
    return n_idle_R + 0.125 * (n_rated_R - n_idle_R)


def calc_n_min_drive_set_R(n_min_drive_set: float) -> int:
    return nround1(n_min_drive_set)


def calc_n_min_drive1(n_idle_R: int) -> int:
    return n_idle_R


def calc_n_min_drive1_R(n_min_drive1: float) -> int:
    return nround1(n_min_drive1)


def calc_n_min_drive2(n_idle_R: int) -> float:
    return 0.9 * n_idle_R


def calc_n_min_drive2_R(n_min_drive2: float) -> int:
    return nround1(n_min_drive2)


def calc_n_min_drive2_up(n_idle_R: int) -> float:
    return 1.15 * n_idle_R


def calc_n_min_drive2_up_R(n_min_drive2_up: float) -> int:
    return nround1(n_min_drive2_up)


def calc_n_min_drive2_stopdecel(n_idle_R: int) -> int:
    return n_idle_R


def calc_n_min_drive2_stopdecel_R(n_min_drive2_stopdecel: float) -> int:
    return nround1(n_min_drive2_stopdecel)


def _check_higher_from_n_min_drive_set(n, n_min_drive_set):
    if n < n_min_drive_set:
        raise ValidationError(
            f"Must be higher than `{m.n_min_drive_set}`({n_min_drive_set})!"
        )


def _check_lower_than_2x_n_min_drive_set(n, n_min_drive_set):
    if n > 2 * n_min_drive_set:
        raise ValidationError(
            f"Must be lower than 2 x `{m.n_min_drive_set}`({n_min_drive_set})!"
        )


def calc_n_min_drive_up(n_min_drive_set: int) -> int:
    return n_min_drive_set


def calc_n_min_drive_up_R(n_min_drive_up: float) -> int:
    return nround1(n_min_drive_up)


def calc_n_min_drive_up_start(n_min_drive_up: int) -> int:
    return n_min_drive_up


def calc_n_min_drive_up_start_R(n_min_drive_up_start: float) -> int:
    return nround1(n_min_drive_up_start)


def calc_n_min_drive_down(n_min_drive_set: int) -> int:
    return n_min_drive_set


def calc_n_min_drive_down_R(n_min_drive_down: float) -> int:
    return nround1(n_min_drive_down)


def calc_n_min_drive_down_start(n_min_drive_down: int) -> int:
    return n_min_drive_down


def calc_n_min_drive_down_start_R(n_min_drive_down_start: float) -> int:
    return nround1(n_min_drive_down_start)


@autographed(out_sideffects=["valid: n_min_drive_up"])
def validate_n_min_drive_up_V1(n_min_drive_up_R: int, n_min_drive_set_R: int):
    _check_higher_from_n_min_drive_set(n_min_drive_up_R, n_min_drive_set_R)


@autographed(out_sideffects=["valid: n_min_drive_up"])
def validate_n_min_drive_up_V2(n_min_drive_up_R: int, n_min_drive_set_R: int):
    _check_lower_than_2x_n_min_drive_set(n_min_drive_up_R, n_min_drive_set_R)


@autographed(out_sideffects=["valid: n_min_drive_down"])
def validate_n_min_drive_down_V1(n_min_drive_down_R: int, n_min_drive_set_R: int):
    _check_higher_from_n_min_drive_set(n_min_drive_down_R, n_min_drive_set_R)


@autographed(out_sideffects=["valid: n_min_drive_down"])
def validate_n_min_drive_down_V2(n_min_drive_down_R: int, n_min_drive_set_R: int):
    _check_lower_than_2x_n_min_drive_set(n_min_drive_down_R, n_min_drive_set_R)


@autographed(out_sideffects=["valid: n_min_drive_up_start"])
def validate_n_min_drive_up_start_V1(
    n_min_drive_up_start_R: int, n_min_drive_set_R: int
):
    _check_higher_from_n_min_drive_set(n_min_drive_up_start_R, n_min_drive_set_R)


@autographed(out_sideffects=["valid: n_min_drive_up_start"])
def validate_n_min_drive_up_start_V2(
    n_min_drive_up_start_R: int, n_min_drive_set_R: int
):
    _check_lower_than_2x_n_min_drive_set(n_min_drive_up_start_R, n_min_drive_set_R)


@autographed(out_sideffects=["valid: n_min_drive_down_start"])
def validate_n_min_drive_down_start_V1(
    n_min_drive_down_start_R: int, n_min_drive_set_R: int
):
    _check_higher_from_n_min_drive_set(n_min_drive_down_start_R, n_min_drive_set_R)


@autographed(out_sideffects=["valid: n_min_drive_down_start"])
def validate_n_min_drive_down_start_V2(
    n_min_drive_down_start_R: int, n_min_drive_set_R: int
):
    _check_lower_than_2x_n_min_drive_set(n_min_drive_down_start_R, n_min_drive_set_R)


validate_n_min_drives = autographed(
    lambda: None,
    inp_sideffects=[
        "valid: n_idle",
        "valid: n_rated",
        "valid: n_min_drive_up",
        "valid: n_min_drive_down",
        "valid: n_min_drive_up_start",
        "valid: n_min_drive_down_start",
    ],
    out_sideffects="valid: n_min_drives",
)
"""Ensure all no-sideffect validations run."""

_NMinDrives = namedtuple(
    "NMinDrives",
    (
        "n_min_drive1",
        "n_min_drive2_up",
        "n_min_drive2_stopdecel",
        "n_min_drive2",
        "n_min_drive_set",
        "n_min_drive_up",
        "n_min_drive_up_start",
        "n_min_drive_down",
        "n_min_drive_down_start",
        "t_cold_end",
    ),
)


#: Consume (R)ounded values to construct a :class:`_NMinDrives` instance.
NMinDrives = autographed(
    _NMinDrives,
    needs=[arg(n if n == "t_cold_end" else f"{n}_R", n) for n in _NMinDrives._fields],
    inp_sideffects="valid: n_min_drives",
    provides="n_min_drives",
)


# TODO: lazily create nmins pipeline with a function.
_funcs = FnHarvester(base_modules=[__name__]).harvest()
_aug = Autograph(["calc_", "upd_"])
_ops = [_aug.wrap_fn(fn, name) for name, fn in _funcs]
mdl_2_n_min_drives = compose("mdl_2_n_min_drives", *_ops, endured=True)
"""
A pipeline to pre-process *n_min_drives* values.

.. graphtik::
    :width: 150%
    :hide:

    >>> mdl_2_n_min_drives
    NetworkOperation('mdl_2_n_min_drives',
    ...

**Example:**

>>> from wltp.nmindrive import mdl_2_n_min_drives

>>> mdl = {"n_idle": 500, "n_rated": 3000, "p_rated": 80, "t_cold_end": 470}
>>> n_min_drives = mdl_2_n_min_drives.compute(mdl, "n_min_drives")
>>> n_min_drives
{'n_min_drives': NMinDrives(n_min_drive1=500, n_min_drive2_up=575, n_min_drive2_stopdecel=500,
 n_min_drive2=450, n_min_drive_set=813, n_min_drive_up=813, n_min_drive_up_start=813,
 n_min_drive_down=813, n_min_drive_down_start=813, t_cold_end=470)}
"""
