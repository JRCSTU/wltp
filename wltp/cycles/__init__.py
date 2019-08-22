import numpy as np
import pandas as pd


def crc_velocity(V: pd.Series, crc=0) -> int:
    """
    Compute the CRC32(V * 10) & 0xFFFF of a velocity trace.

    :param V:
        velocity samples, to be rounded according to :data:`wltp.invariants.v_decimals`
    :param crc:
        initial CRC value
    :return:
         the 16 lowest bits of the CRC32 of the trace

    1. The velocity samples are first round to `v_decimals`;
    2. the samples are then multiplied x10 to convert into integers
       (assuming `v_decimals` is 1);
    3. the integer velocity samples are then converted into int16 little-endian bytes
       (eg 0xC0FE --> (0xFE, 0xC0);
    4. the int16 bytes are then concatanated together, and 
    5. fed into ZIP's CRC32;
    6. the lowest 2 bytes of the CRC32 are kept only.

    """
    from binascii import crc32  # it's the same as `zlib.crc32`
    from ..invariants import v_decimals, vround

    V_ints = vround(V) * 10 ** v_decimals
    return crc32(V_ints.astype(np.int16).values.tobytes(), crc) & 0xFFFF


def cycle_checksums() -> pd.DataFrame:
    """Return a big table with cummulative and simple SUM & CRC for all class phases."""
    import io

    ## As printed by :func:`tests.test_instances.test_wltc_checksums()``
    return pd.read_csv(
        io.StringIO(
            """
		V	V	V	V	V_A1	V_A1	V_A2	V_A2
		SUM	CRC	cum_SUM	cum_CRC	CRC	cum_CRC	CRC	cum_CRC
class	part								
class1	part-1	11988.4	54249	11988.4	54249	48035	48035	57724	57724
class1	part-2	17162.8	11696	29151.2	48076	15201	55972	32741	14379
class1	part-3	11988.4	54249	41139.6	26125	54249	41693	57724	39291
class2	part-1	11162.2	19551	11162.2	19551	24953	24953	32458	32458
class2	part-2	17054.3	48127	28216.5	36100	42503	6254	59818	59921
class2	part-3	24450.6	19878	52667.1	16418	13800	43190	63630	38296
class2	part-4	28869.8	61929	81536.9	3690	61929	33230	48973	31072
class3a	part-1	11140.3	43537	11140.3	43537	57371	57371	39044	39044
class3a	part-2	16995.7	24541	28136.0	62860	64679	34373	3464	12691
class3a	part-3	25646.0	8382	53782.0	14621	57405	34197	38294	21337
class3a	part-4	29714.9	6991	83496.9	21640	6991	12084	21995	36666
class3b	part-1	11140.3	43537	11140.3	43537	57371	57371	39044	39044
class3b	part-2	17121.2	11280	28261.5	34369	35057	61971	32325	16990
class3b	part-3	25782.2	13901	54043.7	22739	46289	18236	33637	32705
class3b	part-4	29714.9	6991	83758.6	27906	6991	19304	21995	33489
"""
        ),
        sep="\t",
        header=[0, 1],
        index_col=[0, 1],
    )
