#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2019 European Commission (JRC);
# Licensed under the EUPL (the 'Licence');
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at: http://ec.europa.eu/idabc/eupl
import contextvars
from typing import List

import pandas as pd

from pandalone import mappings


#: Contains all path/column names used, after code has run code.
#: Don't use it directly, but either
#: - through context-vars to allow for redefinitions, or
#: - call :func:`paths_collected()` at the end of a code run.
_root_pstep = mappings.Pstep()

#: The root-path wrapped in a context-var so that cloent code
#: canm redfine paths & column names momentarily with::
#:
#:     with wio.pstep_factory.redined(<this_module>.cols):
#:         ...
pstep_factory = contextvars.ContextVar("root", default=_root_pstep)


def paths_collected(with_orig=False, tag=None) -> List[str]:
    """
    Return path/column names used, after code has run code.
    
    See :meth:`mappings.Pstep._paths`.
    """
    return _root_pstep._paths(with_orig, tag)


def veh_name(g):
    return "v%0.3d" % int(g)


def veh_names(vlist):
    return [veh_name(v) for v in vlist]


def gear_name(g):
    return f"g{g}"


def gear_names(glist):
    return [gear_name(g) for g in glist]
