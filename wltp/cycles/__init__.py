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
    4. the int16 bytes are then concatanated together, and fed into CRC32;
    5. the lowest 2 bytes of the CRC32 are kept only.

    """
    import binascii
    from ..invariants import v_decimals, vround

    V_ints = vround(V) * 10 ** v_decimals
    return binascii.crc32(V_ints.astype(np.int16).values.tobytes(), crc) & 0xFFFF


def cycle_checksums() -> pd.DataFrame:
    """Return a big table with cummulative and simple SUM & CRC for all class phases."""
    import io

    ## As printed by :func:`tests.test_instances.test_wltc_checksums()``
    return pd.read_csv(
        io.StringIO(
            """
 		V	V	V	V	V_A1	V_A1	V_A1	V_A1	V_A2	V_A2	V_A2	V_A2
		SUM	CRC	cumSUM	cumCRC	SUM	CRC	cumSUM	cumCRC	SUM	CRC	cumSUM	cumCRC
class	part												
class1	part-1	11988.4	54249	11988.4	54249	11988.4	48035	11988.4	48035	11988.399999999998	57724	11988.399999999998	57724
class1	part-2	17162.800000000003	11696	29151.200000000004	48076	17162.800000000003	15201	29151.200000000004	55972	17162.8	32741	29151.199999999997	14379
class1	part-3	11988.4	54249	41139.600000000006	26125	11988.4	54249	41139.600000000006	41693	11988.399999999998	57724	41139.59999999999	39291
class2	part-1	11162.2	19551	11162.2	19551	11162.2	24953	11162.2	24953	11162.2	32458	11162.2	32458
class2	part-2	17054.3	48127	28216.5	36100	17054.3	42503	28216.5	6254	17054.3	59818	28216.5	59921
class2	part-3	24450.6	19878	52667.1	16418	24450.6	13800	52667.1	43190	24450.6	63630	52667.1	38296
class2	part-4	28869.8	61929	81536.9	3690	28869.8	61929	81536.9	33230	28869.799999999996	48973	81536.9	31072
class3a	part-1	11140.3	43537	11140.3	43537	11140.3	57371	11140.3	57371	11140.3	39044	11140.3	39044
class3a	part-2	16995.699999999997	24541	28135.999999999996	62860	16995.699999999997	64679	28135.999999999996	34373	16995.699999999997	3464	28135.999999999996	12691
class3a	part-3	25646.0	8382	53782.0	14621	25646.0	57405	53782.0	34197	25646.0	38294	53782.0	21337
class3a	part-4	29714.9	6991	83496.9	21640	29714.9	6991	83496.9	12084	29714.9	21995	83496.9	36666
class3b	part-1	11140.3	43537	11140.3	43537	11140.3	57371	11140.3	57371	11140.3	39044	11140.3	39044
class3b	part-2	17121.2	11280	28261.5	34369	17121.2	35057	28261.5	61971	17121.199999999997	32325	28261.499999999996	16990
class3b	part-3	25782.2	13901	54043.7	22739	25782.2	46289	54043.7	18236	25782.199999999997	33637	54043.7	32705
class3b	part-4	29714.9	6991	83758.6	27906	29714.9	6991	83758.6	19304	29714.9	21995	83758.6	33489
"""
        ),
        sep="\t",
        header=[0, 1],
        index_col=[0, 1],
    )
