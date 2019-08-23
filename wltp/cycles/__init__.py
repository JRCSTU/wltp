import functools as fnt
from typing import Iterable, Union, Tuple, Optional

import numpy as np
import pandas as pd


def crc_velocity(V: Iterable, crc: Union[int, str] = 0, full=False) -> str:
    """
    Compute the CRC32(V * 10) of a 1Hz velocity trace.

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
    6. the highest 2 bytes of the CRC32 are (usually) kept, formated in hex 
       (x4 leftmost hex-digits).

    """
    from binascii import crc32  # it's the same as `zlib.crc32`
    from ..invariants import v_decimals, vround

    if not isinstance(V, pd.Series):
        V = pd.Series(V)
    if isinstance(crc, str):
        crc = int(crc, 16)

    V_ints = vround(V) * 10 ** v_decimals
    vbytes = V_ints.astype(np.int16).values.tobytes()
    crc = hex(crc32(vbytes, crc)).upper()

    crc = crc[2:] if full else crc[2:6]
    return crc


@fnt.lru_cache()
def cycle_checksums(full=False) -> pd.DataFrame:
    """
    Return a big table with cummulative and simple SUM & CRC for all class phases.
    
    :param full:
        CRCs contain the full 32bit number (x8 hex digits)

    """
    import io
    from textwrap import dedent
    from pandas import IndexSlice as idx

    ## As printed by :func:`tests.test_instances.test_wltc_checksums()``
    table_csv = dedent(
        """
        checksum		CRC32	CRC32	CRC32	CRC32	CRC32	CRC32	SUM	SUM
        accumulation		by_phase	by_phase	by_phase	cummulative	cummulative	cummulative	by_phase	cummulative
        phasing		V	V_A1	V_A2	V	V_A1	V_A2	V	V
        class	part								
        class1	part-1	9840D3E9	4438BBA3	155E6130	9840D3E9	4438BBA3	155E6130	11988.4	11988.4
        class1	part-2	8C342DB0	8C8D3B61	A26AA013	DCF2D584	90BEA9C	27BC6DCC	17162.8	29151.2
        class1	part-3	9840D3E9	9840D3E9	97DBE17C	6D1D7DF5	6D1D7DF5	F523E31C	11988.4	41139.6
        class2	part-1	85914C5F	CDD16179	C771FB0A	85914C5F	CDD16179	C771FB0A	11162.2	11162.2
        class2	part-2	312DBBFF	391AA607	CCE778B1	A0103D21	606EFF7B	5A1D33C8	17054.3	28216.5
        class2	part-3	81CD4DA6	E29E35E8	57BF4874	28FBF6C3	926135F3	EC74F119	24450.6	52667.1
        class2	part-4	8994F1E9	8994F1E9	2181BF4D	474B3569	474B3569	F70F32D3	28869.8	81536.9
        class3a	part-1	48E5AA11	910CE01B	E0E213B8	48E5AA11	910CE01B	E0E213B8	11140.3	11140.3
        class3a	part-2	14945FDD	D93BFCA7	CC323D49	403DF278	24879CA6	3ABFEAD9	16995.7	28136.0
        class3a	part-3	8B3B20BE	9887E03D	E6A7C73E	D7708FF4	3F6732E0	55AA673E	25646.0	53782.0
        class3a	part-4	F9621B4F	F9621B4F	517755EB	9BCE354C	9BCE354C	2B8A32F6	29714.9	83496.9
        class3b	part-1	48E5AA11	910CE01B	E0E213B8	48E5AA11	910CE01B	E0E213B8	11140.3	11140.3
        class3b	part-2	AF1D2C10	E50188F1	7B6A0F45	FBB481B5	18BDE8F0	8DE7D8D5	17121.2	28261.5
        class3b	part-3	15F6364D	A779B4D1	2DE25EDC	43BC555F	B997EE4D	7E5FAD1A	25782.2	54043.7
        class3b	part-4	F9621B4F	F9621B4F	517755EB	639BD037	639BD037	D3DFD78D	29714.9	83758.6
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


def identify_cycle_v_crc(
    crc: Union[int, str]
) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """see :func:`identify_cycle_v()`"""
    if isinstance(crc, str):
        crc = int(crc, 16)
    crc = hex(crc).upper()
    crc = crc[2:6]

    crcs = cycle_checksums(full=False)["CRC32"]
    matches = crcs == crc
    if matches.any(None):
        ## Fetch 1st from top-left.
        #
        for col, flags in matches.iteritems():
            if flags.any():
                index = np.asscalar(next(iter(np.argwhere(flags))))
                cycle, part = crcs.index[index]
                accum, phasing = col
                if accum == "cummulative":
                    if index in [2, 6, 10, 14]:  # is it a final cycle-part?
                        part = None
                    else:
                        part = part.upper()

                return (cycle, part, phasing)
        else:
            assert False, ("Impossible find:", crc, crcs)
    return (None, None, None)


def identify_cycle_v(V: Iterable):
    """
    Finds which cycle/part/kind matches a CRC.

    :param V:
        Any cycle or parts of it (one of Low/Medium/High/Extra Kigh phases), 
        or concatenated subset of the above phases, but in that order.
    :return:
        a 3 tuple (class, part, kind), like this:

        - ``(None,     None,   None)``: if no match
        - ``(<class>,  None,  <kind>)``: if it matches a full-cycle
        - ``(<class>, <part>, <kind>)``: if it matches a part
        - ``(<class>, <PART>, <kind>)``: (CAPITAL part) if it matches a part cummulatively

        where `<kind>` is one of ``'V', 'V_A1', 'V_A2'``.
   """
    crc = crc_velocity(V)
    return identify_cycle_v_crc(crc)
