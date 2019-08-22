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

    ## As printed by :func:`tests.test_instances.test_wltc_checksums()``
    table_csv = dedent(
        """
        		V	V	V	V	V_A1	V_A1	V_A2	V_A2
        		SUM	CRC32	cum_SUM	cum_CRC32	CRC32	cum_CRC32	CRC32	cum_CRC32
        class	part								
        class1	part-1	11988.4	9840D3E9	11988.4	9840D3E9	4438BBA3	4438BBA3	155E6130	155E6130
        class1	part-2	17162.8	8C342DB0	29151.2	DCF2D584	8C8D3B61	90BEA9C	A26AA013	27BC6DCC
        class1	part-3	11988.4	9840D3E9	41139.6	6D1D7DF5	9840D3E9	6D1D7DF5	97DBE17C	F523E31C
        class2	part-1	11162.2	85914C5F	11162.2	85914C5F	CDD16179	CDD16179	C771FB0A	C771FB0A
        class2	part-2	17054.3	312DBBFF	28216.5	A0103D21	391AA607	606EFF7B	CCE778B1	5A1D33C8
        class2	part-3	24450.6	81CD4DA6	52667.1	28FBF6C3	E29E35E8	926135F3	57BF4874	EC74F119
        class2	part-4	28869.8	8994F1E9	81536.9	474B3569	8994F1E9	474B3569	2181BF4D	F70F32D3
        class3a	part-1	11140.3	48E5AA11	11140.3	48E5AA11	910CE01B	910CE01B	E0E213B8	E0E213B8
        class3a	part-2	16995.7	14945FDD	28136.0	403DF278	D93BFCA7	24879CA6	CC323D49	3ABFEAD9
        class3a	part-3	25646.0	8B3B20BE	53782.0	D7708FF4	9887E03D	3F6732E0	E6A7C73E	55AA673E
        class3a	part-4	29714.9	F9621B4F	83496.9	9BCE354C	F9621B4F	9BCE354C	517755EB	2B8A32F6
        class3b	part-1	11140.3	48E5AA11	11140.3	48E5AA11	910CE01B	910CE01B	E0E213B8	E0E213B8
        class3b	part-2	17121.2	AF1D2C10	28261.5	FBB481B5	E50188F1	18BDE8F0	7B6A0F45	8DE7D8D5
        class3b	part-3	25782.2	15F6364D	54043.7	43BC555F	A779B4D1	B997EE4D	2DE25EDC	7E5FAD1A
        class3b	part-4	29714.9	F9621B4F	83758.6	639BD037	F9621B4F	639BD037	517755EB	D3DFD78D
        """
    )
    df = pd.read_csv(io.StringIO(table_csv), sep="\t", header=[0, 1], index_col=[0, 1])
    if not full:
        df.update(df.iloc[:, [1, 3, 4, 5, 6, 7]].apply(lambda sr: sr.str[:4]))

    return df


def identify_cycle_v_crc(
    crc: Union[int, str]
) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """see :func:`identify_cycle_v()`"""
    if isinstance(crc, str):
        crc = int(crc, 16)
    crc = hex(crc).upper()
    crc = crc[2:6]

    crcs = cycle_checksums(full=False).iloc[:, [1, 3, 4, 5, 6, 7]]
    matches = crcs == crc
    if matches.any(None):
        ## Fetch 1st from top-left.
        #
        for col, flags in matches.iteritems():
            if flags.any():
                index = np.asscalar(next(iter(np.argwhere(flags))))
                cycle, part = crcs.index[index]
                va_kind, cum_kind = col
                if "cum_" in cum_kind:
                    if index in [2, 6, 10, 14]:  # is it a final part?
                        part = None
                    else:
                        part = part.upper()

                return (cycle, part, va_kind)
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
