#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2013-2020 European Commission (JRC);
# Licensed under the EUPL (the 'Licence');
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at: http://ec.europa.eu/idabc/eupl
"""
data for all cycles and utilities to identify them

.. Workaround sphinx-doc/sphinx#6590
.. doctest::
    :hide:

    >>> from wltp.cycles import *
    >>> __name__ = "wltp.cycles"
"""
import functools as fnt
from typing import Iterable, Mapping, Optional, Sequence, Tuple, Union

import numpy as np
import pandas as pd
from toolz import itertoolz as itz

from graphtik import compose, operation
from graphtik.pipeline import Pipeline

from .. import autograph as autog

try:
    import importlib.resources as pkg_resources
except ImportError:
    # Try backported to PY<37 `importlib_resources`.
    import importlib_resources as pkg_resources  # type: ignore


@fnt.lru_cache()
def read_V_file(fname) -> Tuple[float, ...]:
    """Parse textual files with cycle velocities."""
    return tuple(float(n) for n in pkg_resources.read_text(__package__, fname).split())


def crc_velocity(V: Iterable, crc: Union[int, str] = 0, full=False) -> str:
    """
    Compute the CRC32(V) of a 1Hz velocity trace, to be compared with :ref:`checksums`.

    :param V:
        velocity samples, to be rounded according to :data:`wltp.invariants.v_decimals`
    :param crc:
        initial CRC value (might be a hex-string)
    :param full:
        print full 32bit number (x8 hex digits), or else,
        just the highest half (the 1st x4 hex digits)
    :return:
         the 16 lowest bits of the CRC32 of the trace, as hex-string

    1. The velocity samples are first round to `v_decimals`;
    2. the samples are then multiplied x10 to convert into integers
       (assuming `v_decimals` is 1);
    3. the integer velocity samples are then converted into int16 little-endian bytes
       (eg 0xC0FE --> (0xFE, 0xC0);
    4. the int16 bytes are then concatanated together, and
    5. fed into ZIP's CRC32;
    6. formated as 0-padded, 8-digit, HEXes;
    7. keeping (usually) the highest 2 bytes of the CRC32
       (4 leftmost hex-digits).

    See also :func:`.identify_cycle_v_crc()` & :func:`.cycle_checksums()`.
    """
    from binascii import crc32  # it's the same as `zlib.crc32`
    from ..invariants import v_decimals, vround

    if not isinstance(V, pd.Series):
        V = pd.Series(V)
    if isinstance(crc, str):
        crc = int(crc, 16)

    V_ints = vround(V) * 10 ** v_decimals
    vbytes = V_ints.astype(np.int16).values.tobytes()
    # crc = hex(crc32(vbytes, crc)).upper()
    crc = crc32(vbytes, crc)
    crc = f"{crc:08X}"

    if not full:
        crc = crc[:4]

    return crc


@fnt.lru_cache()
def cycle_checksums(full=False) -> pd.DataFrame:
    """
    Return a big table with by-phase/cumulative :ref:`CRC/SUM <phasings>` for all class phases.

    :param full:
        CRCs contain the full 32bit number (x8 hex digits)

    """
    import io
    from textwrap import dedent
    from pandas import IndexSlice as idx

    ## As printed by :func:`tests.test_instances.test_wltc_checksums()``
    table_csv = dedent(  # NOTE: literal [Tab] character in the string below.
        """
        checksum		CRC32	CRC32	CRC32	CRC32	CRC32	CRC32	SUM	SUM
        accumulation		by_phase	by_phase	by_phase	cumulative	cumulative	cumulative	by_phase	cumulative
        phasing		V	VA0	VA1	V	VA0	VA1	V	V
        class	phase
        class1	phase-1	9840D3E9	4438BBA3	97DBE17C	9840D3E9	4438BBA3	97DBE17C	11988.4	11988.4
        class1	phase-2	8C342DB0	8C8D3B61	D9E87FE5	DCF2D584	090BEA9C	4295031D	17162.8	29151.2
        class1	phase-3	9840D3E9	4438BBA3	97DBE17C	6D1D7DF5	4691DA10	F523E31C	11988.4	41139.6
        class2	phase-1	85914C5F	CDD16179	8A0A7ECA	85914C5F	CDD16179	8A0A7ECA	11162.2	11162.2
        class2	phase-2	312DBBFF	391AA607	64F1E9AA	A0103D21	606EFF7B	3E77EBB8	17054.3	28216.5
        class2	phase-3	81CD4DA6	E29E35E8	9560F88E	28FBF6C3	926135F3	D162E0F1	24450.6	52667.1
        class2	phase-4	8994F1E9	0D258481	2181BF4D	474B3569	262AE3F3	F70F32D3	28869.8	81536.9
        class3a	phase-1	48E5AA11	910CE01B	477E9884	48E5AA11	910CE01B	477E9884	11140.3	11140.3
        class3a	phase-2	14945FDD	D93BFCA7	41480D88	403DF278	24879CA6	DE5A24E1	16995.7	28136.0
        class3a	phase-3	8B3B20BE	9887E03D	9F969596	D7708FF4	3F6732E0	2EE999C6	25646.0	53782.0
        class3a	phase-4	F9621B4F	1A0A2845	517755EB	9BCE354C	9853FD01	2B8A32F6	29714.9	83496.9
        class3b	phase-1	48E5AA11	910CE01B	477E9884	48E5AA11	910CE01B	477E9884	11140.3	11140.3
        class3b	phase-2	AF1D2C10	E50188F1	FAC17E45	FBB481B5	18BDE8F0	65D3572C	17121.2	28261.5
        class3b	phase-3	15F6364D	A779B4D1	015B8365	43BC555F	B997EE4D	BA25436D	25782.2	54043.7
        class3b	phase-4	F9621B4F	1A0A2845	517755EB	639BD037	0B7AD0EA	D3DFD78D	29714.9	83758.6
        """
    )
    df = pd.read_csv(
        io.StringIO(table_csv), sep="\t", header=[0, 1, 2], index_col=[0, 1]
    )
    if not full:

        def clip_crc(sr):
            try:
                sr = sr.str[:4]
            except AttributeError:
                # AttributeError('Can only use .str accessor with string values...
                pass
            return sr

        df = df.groupby(level="checksum", axis=1).transform(clip_crc)

    return df


@fnt.lru_cache()
def cycle_phases() -> pd.DataFrame:
    """
    Return a textual table with the boundaries of all cycle :ref:`phasings`.
    """
    import io
    from textwrap import dedent
    from pandas import IndexSlice as idx

    ## As printed by :func:`tests.test_instances.def test_cycle_phases_df()``
    table_csv = dedent(  # NOTE: literal [Tab] character in the string below.
        """
        class	phasing	phase-1	phase-2	phase-3	phase-4
        class1	V	[0, 589]	[589, 1022]	[1022, 1611]
        class1	VA0	[0, 588]	[589, 1021]	[1022, 1610]
        class1	VA1	[1, 589]	[590, 1022]	[1023, 1611]
        class2	V	[0, 589]	[589, 1022]	[1022, 1477]	[1477, 1800]
        class2	VA0	[0, 588]	[589, 1021]	[1022, 1476]	[1477, 1799]
        class2	VA1	[1, 589]	[590, 1022]	[1023, 1477]	[1478, 1800]
        class3a	V	[0, 589]	[589, 1022]	[1022, 1477]	[1477, 1800]
        class3a	VA0	[0, 588]	[589, 1021]	[1022, 1476]	[1477, 1799]
        class3a	VA1	[1, 589]	[590, 1022]	[1023, 1477]	[1478, 1800]
        class3b	V	[0, 589]	[589, 1022]	[1022, 1477]	[1477, 1800]
        class3b	VA0	[0, 588]	[589, 1021]	[1022, 1476]	[1477, 1799]
        class3b	VA1	[1, 589]	[590, 1022]	[1023, 1477]	[1478, 1800]
        """
    )
    return pd.read_csv(
        io.StringIO(table_csv), sep="\t", header=0, index_col=[0, 1]
    ).fillna("")


def identify_cycle_v_crc(
    crc: Union[int, str]
) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """The opposite of :func:`identify_cycle_v()`"""
    if isinstance(crc, str):
        crc = int(crc, 16)
    crc = hex(crc).upper()
    crc = crc[2:6]

    crcs = cycle_checksums(full=False)["CRC32"]
    matches = crcs == crc
    if matches.any(None):
        ## Find the 1st match from left-top.
        #
        rows, cols = np.nonzero(matches.to_numpy())
        row, col = rows[0], cols[0]
        cycle, phase = crcs.index[row]
        accum, phasing = crcs.columns[col]

        if accum == "cumulative":
            if row in [2, 6, 10, 14]:  # is it a final cycle-phase?
                phase = None
            else:
                phase = phase.upper()

        return (cycle, phase, phasing)

    return (None, None, None)


def identify_cycle_v(V: Iterable):
    """
    Finds the first left-top :ref:`CRC <checksums>` matching the given Velocity-trace.

    :param V:
        Any cycle or phases of it (one of Low/Medium/High/Extra High phases),
        or concatenated subset of the above phases, but in that order.
    :return:
        a 3tuple (class, phase, kind), like this:

        - ``(None,     None,   None)``: if no match
        - ``(<class>,  None,  <phasing>)``: if it matches a full-cycle
        - ``(<class>, <phase>, <phasing>)``: if it matches a phase
        - ``(<class>, <PHASE>, <phasing>)``: (CAPITAL phase) if it matches a phase, cumulatively

        where `<phasing>` is one of

        - ``V``
        - ``A0`` (offset: 0, length: -1, lissing -last sample)
        - ``A1`` (offset: 1, length: -1, missing first sample)
   """
    crc = crc_velocity(V)
    return identify_cycle_v_crc(crc)


@autog.autographed(needs=["wltc_data/classes", ...])
def get_wltc_class_data(wltc_classes: Mapping, wltc_class: Union[str, int]) -> dict:
    """
    Fetch the wltc-data for a specific class.

    :param wltc_data:
        same-named item in :term:`datamodel`
    :param wltc_class:
        one of 'class1', ..., 'class3b' or its index 0,1, ... 3

    Like :func:`.datamodel.get_class` suited for pipelines.
    """
    if isinstance(wltc_class, int):
        class_name = list(wltc_classes.keys())[wltc_class]
    else:
        class_name = wltc_class

    return wltc_classes[class_name]


@autog.autographed(needs=["wltc_class_data/lengths", "wltc_class_data/V_cycle"])
def get_class_phase_boundaries(
    part_lengths: tuple, V_cycle
) -> Tuple[Tuple[int, int], ...]:
    """
    Serve ``[low, high)`` boundaries from class-data, as `Dijkstra demands it`__.

    :return:
        a tuple of tuple-pairs of *time indices* (low/hight) part-boundaries
        (ie for class-3a these are 5 pairs of numbers, see example below),
        that may be used as ``Series.loc[slice(*pair)]``.

    Like :func:`.datamodel.get_class_parts_limits` with ``edges=true``,
    suited for pipelines.

    __  https://www.cs.utexas.edu/users/EWD/transcriptions/EWD08xx/EWD831.html

    **Example:**

        >>> from wltp import datamodel, cycles
        >>> wcd = datamodel.get_wltc_data()
        >>> cd = cycles.get_wltc_class_data(wcd["classes"], "class3b")
        >>> cycles.get_class_phase_boundaries(cd["lengths"], cd["V_cycle"])
        ((0, 589), (589, 1022), (1022, 1477), (1477, 1800))


    """
    part_breaks = np.cumsum(part_lengths)
    return tuple(itz.sliding_window(2, (0, *part_breaks)))


@autog.autographed()
@autog.autographed(
    name="make_compensated_phases_grouper", needs="compensated_phase_boundaries",
)
def make_class_phases_grouper(
    class_phase_boundaries: Sequence[tuple],
) -> pd.Categorical:
    """
    Return a pandas group-BY for the given `boundaries` as `VA1` phasing.

    :param class_phase_boundaries:
        a list of ``[low, high]`` boundary pairs
        (from :func:`.get_class_phase_boundaries()`)

    Onbviously, it cannot produce overlapping split-times belonging to 2 phases.
    """
    part_intervals = pd.IntervalIndex.from_tuples(class_phase_boundaries, closed="left")
    t_max = class_phase_boundaries[-1][-1]
    return pd.cut(range(t_max + 1), part_intervals)


@autog.autographed(needs=["wltc_class_data/V_cycle", ...])
@autog.autographed(name="calc_dsc_distances", needs=["V_dsc", ...])
@autog.autographed(name="calc_capped_distances", needs=["V_capped", ...])
@autog.autographed(
    name="calc_compensated_distances",
    needs=["V_compensated", "compensated_phases_grouper"],
)
def calc_wltc_distances(V: pd.Series, class_phases_grouper) -> pd.DataFrame:
    """
    Return a *(phase x (sum, cumsum))* matrix for the v-phasing `boundaries` of `V`.

    :param V:
        a velocity profile with the standard WLTC length
    :param class_phases_grouper:
        an object to break up a velocity in parts
        (from :func:`make_grouper()`)
    """
    sums = V.groupby(class_phases_grouper).sum()
    sums = pd.concat([sums, sums.cumsum()], axis=1, keys=["sum", "cumsum"])
    sums.name = f"{V.name}_sums"

    return sums
