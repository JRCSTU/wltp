# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.6.0
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %% [markdown]
# ## Run all matlab cases using pandas to read data
# Execution takes ~5'' for all 125 cases.

# %%
## To autoreload codein python files here.
# %load_ext autoreload
# %autoreload 2

## Auto-format cells to ease diffs.
# %load_ext lab_black

# %%
## If you change that, restart kernel and clear all outpouts before running it
# #%matplotlib widget
# %matplotlib inline

# %%
import io
import itertools as itt
import logging
import os
import re
import sys
from collections import namedtuple
from pathlib import Path
from pathlib import PurePosixPath as P
from typing import Any, Callable, Dict, Mapping, List
from typing import Sequence as Seq
from typing import Union

import numpy as np
import pandas as pd
import qgrid
from columnize import columnize
from matplotlib import pyplot as plt
from pandas import HDFStore
from pandas import IndexSlice as idx
from pandas.core.generic import NDFrame

import wltp
from graphtik import compose, operation, optional
from pandalone.mappings import Pstep
from wltp import cycler, datamodel, engine
from wltp import io as wio
from wltp import vehicle, vmax
from wltp.experiment import Experiment
from wltp.utils import pwd_changed, yaml_loads

## Add tests/ into `sys.path` to import `vehdb` module.
#
proj_dir = str(Path(wltp.__file__).parents[1] / "tests")
if proj_dir not in sys.path:
    sys.path.insert(0, proj_dir)

import vehdb

idx = pd.IndexSlice
log = logging.getLogger("VMax.ipynb")
logging.getLogger("blib2to3").propagate = False  # Disable `lab_black` logs.
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s|%(levelname)5.5s|%(name)s:[%(funcName)s]:\n  +--> %(message)s",
    datefmt="%Y-%m-%d,%H:%M:%S",
)
pd.set_option("display.max_columns", 64, "display.max_rows", 130)

# %%
from oct2py import Cell
from oct2py import octave as oc

# See https://nbviewer.jupyter.org/github/blink1073/oct2py/blob/master/example/octavemagic_extension.ipynb?create=1
# %load_ext oct2py.ipython
oc.addpath(str(Path("src").absolute()))

# %%
nsamples = 12

# %% [markdown]
# ## *Input* data for calc_all_cases()
# The data stored in the following CSV files:
#
# 1. `case.txt`
# 2. `vehicle.txt`
# 3. `engine.txt`
# 4. `gearbox.txt`
# 5. `phase.txt`
# 6. `trace.txt`
# 7. `scale.txt`

# %%
# !ls src/*.txt

# %% [markdown]
# ### Read all input CSV tables (`mat_db`)

# %%
dtypes = {
    "case": {
        "case": int,
        "class": str,
        **dict.fromkeys(
            "do_dsc do_cap do_cmp calc_dsc supp0 excl1 autom merge".split(), bool
        ),
        "veh": np.int,
        **dict.fromkeys(
            "f_dsc v_cap n_min1 n_min12 n_min2d n_min2 n_min3 n_min3a n_min3d n_min3as"
            " n_min3ds t_start n_lim asm_0 n_asm_s n_asm_e".split(),
            np.float64,
        ),
    },
    "vehicle": {
        "veh": np.int,
        "#g": np.float64,
        **dict.fromkeys(
            "f_dsc p_rated n_rated n_idle n_max1 m_test m_ro n_lim f0 f1 f2 SM".split(),
            np.float16,
        ),
    },
    "engine": {"veh": int, **dict.fromkeys("n p ASM".split(), np.float16,)},
    "gearbox": {"veh": int, "g": np.float64, "ndv": np.float16},
    "phase": {"class": str, "phase": np.float64, "length": np.float64,},
    "trace": {"class": str, "t": np.float64, "v": np.float64,},
    "scale": {
        "class": str,
        "algo": str,
        **dict.fromkeys("t_beg t_max t_end".split(), np.float64,),
        **dict.fromkeys("r0 a1 b1".split(), np.float16,),
    },
}


def read_csv(basename: str) -> pd.DataFrame:
    """Matlab data-files have spaces columns and are humanly idented. """
    fpath = f"src/{basename}.txt"
    df = pd.read_csv(fpath, sep=" *, *", engine="python", dtype=dtypes[basename])
    df = df.set_index(df.columns[0])

    return df


def read_all_inputs() -> Dict[str, pd.DataFrame]:
    files = re.split("[, ]+", "case, vehicle, engine, gearbox, phase, trace, scale")
    return {name: read_csv(name) for name in files}


mat_db = read_all_inputs()
# Assign tables to  `df_case`, ... variables.
globals().update((f"df_{name}", df) for name, df in mat_db.items())

# %%
for name, df in mat_db.items():
    display(f"{name}:", df.head())

# %%
df_case.at[1, "veh"]

# %%
TraceScaledInps = namedtuple(
    "TraceScaledInps",
    ## Order is important when callling mat-functions!
    """
    ApplyDownscaling ApplySpeedCap ApplyDistanceCompensation UseCalculatedDownscalingPercentage
    DownscalingPercentage ScalingStartTimes ScalingCorrectionTimes ScalingEndTimes
    ScalingAlgorithms CappedSpeed PhaseLengths Trace VehicleClass RatedEnginePower
    VehicleTestMass f0 f1 f2
     """.split(),
)

TraceScaledOuts = namedtuple(
    "TraceScaledOuts",
    "case veh"  # Not outs, added for reference
    ## Order is important when callling mat-functions!
    """
    RequiredToRatedPowerRatio CalculatedDownscalingPercentage RequiredToRatedPowerRatios
    CalculatedDownscalingPercentages TotalChecksum PhaseChecksums MaxVehicleSpeed
    TotalDistance DistanceCompensatedPhaseLengths OriginalTrace ApplicableTrace
    """.split(),
)


def extract_scale_trace_inputs(
    case_no: int, mat_db: Dict[str, pd.DataFrame], **overrides
) -> dict:
    """
    Return an ordered dictionary with (pandas) values for mat-function `scaleTrace.m`.

    :return:
        data are regular pandas
        (apply :func:`columnize_pandas()` before calling matlab)
    """

    case = mat_db["case"].loc[case_no]
    case_class = case["class"]

    veh_no = case.veh
    veh = mat_db["vehicle"].loc[veh_no]
    veh_class = veh["class"]

    scale = mat_db["scale"].loc[veh_class]
    phase = mat_db["phase"].loc[veh_class]
    trace = mat_db["trace"].loc[case_class]
    trace = trace.loc[:, ["t", "v"]]

    args = TraceScaledInps(
        **{
            # CASE
            "VehicleClass": case_class,
            "ApplyDownscaling": case.do_dsc,
            "ApplySpeedCap": case.do_cap,
            "ApplyDistanceCompensation": case.do_cmp,
            "UseCalculatedDownscalingPercentage": case.calc_dsc,
            "DownscalingPercentage": case.f_dsc,
            "CappedSpeed": case.v_cap,
            # VEHICLE
            "RatedEnginePower": veh.p_rated,
            "VehicleTestMass": veh.m_test,
            "f0": veh.f0,
            "f1": veh.f1,
            "f2": veh.f2,
            # SCALE, PHASE & TRACE
            "ScalingStartTimes": scale.t_beg,
            "ScalingCorrectionTimes": scale.t_max,
            "ScalingEndTimes": scale.t_end,
            "ScalingAlgorithms": scale.algo,
            "PhaseLengths": phase.length,
            "Trace": trace,
        }
    )

    args = args._replace(**overrides)

    return args


def panda2col(val) -> np.ndarray:
    """Convert any pandas to numpy, and series into a 1xN column-arrays."""

    if isinstance(val, pd.DataFrame):
        val = [panda2col(col_tuple[1]) for col_tuple in val.iteritems()]
    elif isinstance(val, pd.Series):
        val = val.to_numpy().reshape(-1, 1)
    return val


def columnize_pandas(*args) -> list:
    """Numpy-ize & columnize any pandas args. """
    return [panda2col(v) for v in args]


def cell_columns_to_df(cell: Cell, **df_kw) -> pd.DataFrame:
    """Turn a cell-array of columns into a DataFrame."""
    return pd.DataFrame(np.hstack(tuple(cell)), **df_kw)


def scale_trace(
    case_no: int, mat_db: Dict[str, pd.DataFrame], **overrides
) -> TraceScaledOuts:
    """
    Run `scaleTrace.m` for the given `case_no` in `mat_db`.

    :return:
        results as builtins or numpy-arrays
    """

    df_case = mat_db["case"]
    veh_no = df_case.at[case_no, "veh"]

    args = extract_scale_trace_inputs(case_no, mat_db, **overrides)
    mat_ized = columnize_pandas(*args)
    args = TraceScaledInps(**dict(zip(TraceScaledInps._fields, mat_ized)))
    outputs = oc.scaleTrace(*args, nout=11)
    outputs = TraceScaledOuts(case_no, veh_no, *outputs)

    outputs = outputs._replace(
        ApplicableTrace=cell_columns_to_df(
            outputs.ApplicableTrace[0], columns="t v is_dsc is_cap is_cmp".split()
        )
        .astype({"t": int, "is_dsc": bool, "is_cap": bool, "is_cmp": bool})
        .set_index("t"),
        OriginalTrace=cell_columns_to_df(outputs.OriginalTrace[0], columns=["t", "v"])
        .astype({"t": int})
        .set_index("t"),
    )
    return outputs


def scale_all_traces(
    mat_db: Mapping[int, Union[TraceScaledInps, Exception]]
) -> Mapping[int, Union[TraceScaledOuts, Exception]]:
    """Run `scaleTrace.m` for all cases in in `mat_db`."""

    all_scaled = []
    for case_no in mat_db["case"].index:
        try:
            all_scaled.append(scale_trace(case_no, mat_db))
        except Exception as ex:
            log.error("Case(%s) failed due to: %s", case_no, ex)
            all_scaled[case_no] = ex
            raise

    return all_scaled


# %time scale_results = scale_all_traces(mat_db)

# %% [markdown]
# ## *Output* data for calc_all_cases()
# The data stored in the following CSV files:
#
# 1. `case_result.txt`
# 2. `engine_result.txt`
# 3. `trace_interpolated.txt`
# 4. `trace_scaled.txt`
# 5. `phase_result.txt`
# 6. `shift_power.txt`
# 7. `shift.txt`
# 8. `shift_condensed.txt`
#
# But here we get those in the one `TraceScaledOuts` instance for each case.

# %%
# Pick the case_no=1 results
case_result = scale_results[0]
for name, val in case_result._asdict().items():
    if isinstance(val, pd.DataFrame):
        display(f"{name}:", val.head())
    else:
        display(f"{name} = {val}")

# %% [markdown]
# Let's collect scalars in a (possibly hierarchical) dataframes:

# %%
non_scalar_scale_fields = set(
    "PhaseChecksums DistanceCompensatedPhaseLengths OriginalTrace ApplicableTrace".split()
)
scalar_scale_fields = [
    f for f in scale_results[0]._fields if f not in non_scalar_scale_fields
]
scale_scalars = pd.DataFrame(
    [[getattr(res, k) for k in scalar_scale_fields] for res in scale_results],
    columns=scalar_scale_fields,
).set_index("case")


display(scale_scalars.sample(nsamples).sort_index())


# %%
def merge_phase_numbers(scale_results, res_name):
    res = pd.concat(
        [pd.Series(getattr(r, res_name).ravel(), name=r.case) for r in scale_results],
        axis=1,
    )
    res.columns.name = "case"
    res.index.name = "phase"
    return res.T


phase_sums = {
    "checksums": merge_phase_numbers(scale_results, "PhaseChecksums"),
    "lengths": merge_phase_numbers(scale_results, "DistanceCompensatedPhaseLengths"),
}
phase_sums = pd.concat(phase_sums.values(), axis=1, keys=phase_sums.keys())
display(phase_sums.sample(nsamples).sort_index())

# %%
case_traces = {i.case: i.ApplicableTrace for i in scale_results}
case_traces = pd.concat(
    case_traces.values(), keys=case_traces.keys(), names=["case", "t"]
)
case_traces.sample(nsamples).sort_index()

# %% [markdown]
# ## Result items (so far)
# ```
# - scale_scalars
# - phase_sums
# - case_traces
# ```
# (all `pd.DataFrames`)

# %%
# !ls ../VehData

# %%
py_h5 = "../VehData/WltpGS-pyalgo.h5"
acc_h5 = "../VehData/WltpGS-msaccess.h5"
case_no = 1
acc_db = vehdb.load_vehicle_accdb(acc_h5, case_no)
py_db = vehdb.load_vehicle_pyalgo(py_h5, case_no)

# %%
display("PY: ", py_db.df.v_target.sum())
display(case_traces.loc[1, 1].sum())

# %%
scale_results

# %%
