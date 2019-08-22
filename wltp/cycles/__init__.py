from typing import Union

import numpy as np
import pandas as pd


def crc_velocity(V: pd.Series, crc: Union[str, int] = 0) -> str:
    """
    Compute the CRC32(V * 10) & 0xFFFF of a velocity trace.

    :param V:
        velocity samples, to be rounded according to :data:`wltp.invariants.v_decimals`
    :param crc:
        initial CRC value (might be a HEX-string)
    :return:
         the 16 lowest bits of the CRC32 of the trace, as hex-string

    1. The velocity samples are first round to `v_decimals`;
    2. the samples are then multiplied x10 to convert into integers
       (assuming `v_decimals` is 1);
    3. the integer velocity samples are then converted into int16 little-endian bytes
       (eg 0xC0FE --> (0xFE, 0xC0);
    4. the int16 bytes are then concatanated together, and 
    5. fed into ZIP's CRC32;
    6. the lowest 2 bytes of the CRC32 are kept, formated in hex.

    """
    from binascii import crc32  # it's the same as `zlib.crc32`
    from ..invariants import v_decimals, vround

    if isinstance(crc, str):
        crc = int(crc, 16)
    V_ints = vround(V) * 10 ** v_decimals
    vbytes = V_ints.astype(np.int16).values.tobytes()
    return "%04X" % (crc32(vbytes, crc) & 0xFFFF)


def cycle_checksums() -> pd.DataFrame:
    """Return a big table with cummulative and simple SUM & CRC for all class phases."""
    import io

    ## As printed by :func:`tests.test_instances.test_wltc_checksums()``
    return pd.read_csv(
        io.StringIO(
            """
		V	V	V	V	V_A1	V_A1	V_A2	V_A2
		SUM	CRC32	cum_SUM	cum_CRC32	CRC32	cum_CRC32	CRC32	cum_CRC32
class	part								
class1	part-1	11988.4	D3E9	11988.4	D3E9	BBA3	BBA3	E17C	E17C
class1	part-2	17162.8	2DB0	29151.2	BBCC	3B61	DAA4	7FE5	382B
class1	part-3	11988.4	D3E9	41139.6	660D	D3E9	A2DD	E17C	997B
class2	part-1	11162.2	4C5F	11162.2	4C5F	6179	6179	7ECA	7ECA
class2	part-2	17054.3	BBFF	28216.5	8D04	A607	186E	E9AA	EA11
class2	part-3	24450.6	4DA6	52667.1	4022	35E8	A8B6	F88E	9598
class2	part-4	28869.8	F1E9	81536.9	0E6A	F1E9	81CE	BF4D	7960
class3a	part-1	11140.3	AA11	11140.3	AA11	E01B	E01B	9884	9884
class3a	part-2	16995.7	5FDD	28136.0	F58C	FCA7	8645	0D88	3193
class3a	part-3	25646.0	20BE	53782.0	391D	E03D	8595	9596	5359
class3a	part-4	29714.9	1B4F	83496.9	5488	1B4F	2F34	55EB	8F3A
class3b	part-1	11140.3	AA11	11140.3	AA11	E01B	E01B	9884	9884
class3b	part-2	17121.2	2C10	28261.5	8641	88F1	F213	7E45	425E
class3b	part-3	25782.2	364D	54043.7	58D3	B4D1	473C	8365	7FC1
class3b	part-4	29714.9	1B4F	83758.6	6D02	1B4F	4B68	55EB	82D1
"""
        ),
        sep="\t",
        header=[0, 1],
        index_col=[0, 1],
    )
