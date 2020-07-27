#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2013-2020 European Commission (JRC);
# Licensed under the EUPL (the 'Licence');
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at: http://ec.europa.eu/idabc/eupl
"""
code for generating the cycle

.. Workaround sphinx-doc/sphinx#6590
.. doctest::
    :hide:

    >>> from wltp.cycler import *
    >>> __name__ = "wltp.cycler"
"""
import functools as fnt
from graphtik import compose, keyword, modify, operation, optional, sfxed, vararg
from graphtik.pipeline import Pipeline

from . import autograph as autog
from . import io as wio


@fnt.lru_cache()
def cycler_pipeline(aug: autog.Autograph = None, **pipeline_kw) -> Pipeline:
    """
    Main pipeline to "run" the cycle.

    .. graphtik::
        :height: 600
        :hide:
        :name: cycler_pipeline

        >>> pipe = cycler_pipeline()
    """
    from . import cycler, cycles, vehicle

    aug = aug or wio.make_autograph(domains=("cycle", None))
    funcs = [
        cycles.get_wltc_class_data,
        cycler.get_forced_cycle,
        cycler.init_cycle_velocity,
        cycler.calc_acceleration,
        cycles.get_class_phase_boundaries,
        cycler.attach_class_v_phase_markers,
        cycler.calc_class_va_phase_markers,
        *vehicle.p_req_pipeline(aug).ops,
    ]
    ops = [aug.wrap_fn(fn) for fn in funcs]
    pipe = compose(..., *ops, **pipeline_kw)

    return pipe
