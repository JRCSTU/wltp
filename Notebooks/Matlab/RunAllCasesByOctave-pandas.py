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
# # Run all matlab cases using pandas to read data
# Execution takes ~5'' for all 125 cases.

# %% [markdown]
# ## Intialization & jupyter setup

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
from typing import Tuple, Union

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
log = logging.getLogger("ipynb.RunMatCases-pandas")
logging.getLogger("blib2to3").propagate = False  # Disable `lab_black` logs.
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s|%(levelname)5.5s|%(name)s:[%(funcName)s]:\n  +--> %(message)s",
    datefmt="%Y-%m-%d,%H:%M:%S",
)
pd.set_option("display.max_columns", 64, "display.max_rows", 130)

NamedTuple = tuple

# %%
from oct2py import Cell
from oct2py import octave as oc

# See https://nbviewer.jupyter.org/github/blink1073/oct2py/blob/master/example/octavemagic_extension.ipynb?create=1
# %load_ext oct2py.ipython
oc.addpath(str(Path("src").absolute()))

# %%
import missingno as msno

# On my linux this lib produces much debug logs about fonts.
l = logging.getLogger("matplotlib.font_manager")
l.propagate = False

# %%
nsamples = 12

# %% [markdown]
# ## Read all input CSV tables (`mat_db`)

# %% [markdown]
# ### `mat_db` *input* files
# The CSV files stored in `Notebooks/Matlab/src`:
#
# - `case.txt`
# - `vehicle.txt`
# - `engine.txt`
# - `gearbox.txt`
# - `phase.txt`
# - `trace.txt`
# - `scale.txt`

# %%
# !ls src/*.txt

# %%
matfile_dtypes = {
    "case": {
        "case": int,
        "class": str,
        **dict.fromkeys(
            "do_dsc do_cap do_cmp calc_dsc supp0 excl1 autom merge".split(), bool
        ),
        "t_start": np.int32,
        "veh": np.int,
        **dict.fromkeys(
            "f_dsc v_cap n_min1 n_min12 n_min2d n_min2 n_min3 n_min3a n_min3d n_min3as"
            " n_min3ds n_lim asm_0 n_asm_s n_asm_e".split(),
            np.float64,
        ),
    },
    "vehicle": {
        "veh": np.int32,
        "#g": np.int32,
        **dict.fromkeys(
            "f_dsc p_rated n_rated n_idle n_max1 m_test m_ro n_lim f0 f1 f2 SM".split(),
            np.float64,
        ),
    },
    "engine": {
        "veh": int,
        **dict.fromkeys(
            "n p ASM".split(),
            np.float64,
        ),
    },
    "gearbox": {
        "veh": int,
        "g": "string",
        "ndv": np.float64,
    },  # "g": Matlab need char-array
    "phase": {
        "class": str,
        "phase": np.float64,
        "length": np.float64,
    },
    "trace": {
        "class": str,
        "t": np.float64,
        "v": np.float64,
    },
    "scale": {
        "class": str,
        "algo": str,
        **dict.fromkeys(
            "t_beg t_max t_end".split(),
            np.float64,
        ),
        **dict.fromkeys(
            "r0 a1 b1".split(),
            np.float64,
        ),
    },
}


def read_mat_csv(fpath: str, **read_csv_kw) -> pd.DataFrame:
    """Matlab data-files have spaces columns and are humanly indented. """
    if fpath in matfile_dtypes:
        basename = fpath
        fpath = f"src/{basename}.txt"
        if "dtype" not in read_csv_kw and basename in dtypes:
            dtype = matfile_dtypes[basename]
    df = pd.read_csv(fpath, sep=" *, *", engine="python", **read_csv_kw)
    df = df.set_index(df.columns[0])

    return df


def read_all_inputs(dtypes=matfile_dtypes) -> Dict[str, pd.DataFrame]:
    files = "case vehicle engine gearbox phase trace scale".split()
    return {name: read_mat_csv(name, dtype=dtypes[name]) for name in files}


mat_db = read_all_inputs()
# Assign tables to  `df_case`, ... variables.
globals().update((f"df_{name}", df) for name, df in mat_db.items())

# %%
display(
    msno.matrix(df_vehicle.replace(0, np.NAN)), msno.matrix(df_case.replace(0, np.NAN))
)

# %%
display("FLAGS:", df_case.select_dtypes(bool).sum())

# %%
# Display all `mat_db` to faciliate inputs-matching & conversions.
#
for name, df in mat_db.items():
    display(name, df.shape, df.head())

# %% [markdown]
# ## SCALE (`scaleTrace()`)

# %%
#######
## Matlab <--> python utils
##


def panda2col(val) -> np.ndarray:
    """Convert any pandas to numpy, and series into a 1xN column-arrays."""

    if isinstance(val, pd.DataFrame):
        val = [panda2col(col_tuple[1]) for col_tuple in val.iteritems()]
    elif isinstance(val, pd.Series):
        # Matlab needs char-array for `Ndv.gears`.
        dtype = str if isinstance(val.dtype, (str, pd.StringDtype)) else None
        val = val.to_numpy(dtype=dtype).reshape(-1, 1)
    elif isinstance(val, bool):
        val = np.bool_(val)  # or Mat's `validateattributes()` screams.
    return val


def columnize_pandas(*args) -> list:
    """Numpy-ize & columnize any pandas args. """
    return [panda2col(v) for v in args]


def mat_ize(ntuple):
    """Columnize all values of a (named) tuple."""
    mat_ized = columnize_pandas(*ntuple)
    return type(ntuple)(*mat_ized)


def cell_columns_to_df(cell: Cell, **df_kw) -> pd.DataFrame:
    """Turn a cell-array of columns into a DataFrame."""
    return pd.DataFrame(np.hstack(tuple(cell)), **df_kw)


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
            # case.txt:f_dsc contains fraction (0-->1), but DownscalingPercentage expects percentage.
            "DownscalingPercentage": 100 * case.f_dsc,
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
    mat_ized = mat_ize(args)
    outputs = oc.scaleTrace(*mat_ized, nout=11)
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

    results = []
    for case_no in mat_db["case"].index:
        try:
            results.append(scale_trace(case_no, mat_db))
        except Exception as ex:
            log.error("Case(%s) failed due to: %s", case_no, ex)
            raise

    return results


# %time scale_results = scale_all_traces(mat_db)

# %% [markdown]
# ### SCALE *output* files
# Conceptually, the results are stored in CSV files inside `Notebooks/Matlab/outs`:
#
# - `trace_interpolated.txt` (not really needed)
# - `trace_scaled.tx`
# - `phase_result.txt`
# - `case_result.txt` (partial)

# %% [markdown]
# ### Process *SCALE* results

# %%
def lene(i):
    try:
        return len(i)
    except:
        pass


def research_mat_results(case_result: NamedTuple):
    """Decide results to coallesce in a single frame, or need further processing into separate frames."""
    fields = pd.DataFrame(
        {
            "is_scalar": [np.isscalar(v) for v in case_result],
            "len": [lene(v) for v in case_result],
            "size": [getattr(v, "size", None) for v in case_result],
            "squeeze": [
                lene(v.squeeze()) if hasattr(v, "squeeze") else None
                for v in case_result
            ],
            "shape": [getattr(v, "shape", None) for v in case_result],
            "squeeze_shape": [
                v.squeeze().shape if hasattr(v, "squeeze") else None
                for v in case_result
            ],
        },
        index=pd.Index(case_result._fields, name="outvar"),
    )
    fields = fields.sort_values(fields.columns.tolist())
    previews = [
        (name, val.shape, val.sample(nsamples).sort_index())
        if isinstance(val, pd.DataFrame)
        else (f"{name} = {val}",)
        for name, val in case_result._asdict().items()
    ]

    return fields, previews


# Pick the case_no=1 results to research.
scale_fields, previews = research_mat_results(scale_results[0])
display(scale_fields)  # , *previews)


# %%
def merge_scalar_results(results, scalar_fields):
    """ Collect all scalar results in a (hierarchical) dataframe. """
    return pd.DataFrame(
        [[getattr(res, k) for k in scalar_fields] for res in results],
        columns=scalar_fields,
    ).set_index("case")


# Pick the case_no=1 results to research.
df_scaled_scalars = mat_db["scaled_scalars"] = merge_scalar_results(
    scale_results, scale_fields.query("is_scalar").index
)

display(
    df_scaled_scalars.sample(nsamples).sort_index(),
    df_scaled_scalars.describe(),
    msno.matrix(df_scaled_scalars.replace(0, np.NAN)),
)


# %%
def merge_scale_phases(scale_results, res_name):
    """Special-purpose hierarchical-concat for `scaleTrace()` results. """
    res = pd.concat(
        [pd.Series(getattr(r, res_name).ravel(), name=r.case) for r in scale_results],
        axis=1,
    )
    res.columns.name = "case"
    res.index.name = "phase"
    return res.T


phase_sums = {
    "checksums": merge_scale_phases(scale_results, "PhaseChecksums"),
    "lengths": merge_scale_phases(scale_results, "DistanceCompensatedPhaseLengths"),
}
phase_sums = pd.concat(phase_sums.values(), axis=1, keys=phase_sums.keys())

df_scaled_checksums = mat_db["scaled_checksums"] = phase_sums

display(phase_sums.sample(nsamples).sort_index())


# %%
def merge_scale_traces(scale_results):
    """Special-purpose pandas-concat for `scaleTrace()` results. """
    traces = {i.case: i.ApplicableTrace for i in scale_results}
    traces = pd.concat(traces.values(), keys=traces.keys(), names=["case", "t"])
    return traces


df_scaled_traces = mat_db["scaled_traces"] = merge_scale_traces(scale_results)

df_scaled_traces.sample(nsamples).sort_index()

# %%
list(mat_db)

# %% [markdown]
# ## SHIFT (`calculateShiftpointsNdvFullPC()`)
# Re-display inputs & produced SCALE outputs to select inputs for SHIFT.

# %%
## Display all `mat_db` to faciliate inputs-matching & conversions.
#
# for name, df in mat_db.items():
#     display(name, df.shape, df.head())

# %%
ShitPointsInps = namedtuple(
    "ShitPointsInps",
    ## Order is important when callling mat-functions!
    """
    RatedEnginePower  RatedEngineSpeed  IdlingEngineSpeed  Max95EngineSpeed  NoOfGears  VehicleTestMass f0  f1  f2
    Ndv  FullPowerCurve  Trace  SafetyMargin  AdditionalSafetyMargin0  StartEngineSpeed  EndEngineSpeed
    MinDriveEngineSpeed1st  MinDriveEngineSpeed1stTo2nd  MinDriveEngineSpeed2ndDecel  MinDriveEngineSpeed2nd
    MinDriveEngineSpeedGreater2nd  EngineSpeedLimitVMax  MaxTorque  ExcludeCrawlerGear  AutomaticClutchOperation
    SuppressGear0DuringDownshifts  MinDriveEngineSpeedGreater2ndAccel  MinDriveEngineSpeedGreater2ndDecel
    MinDriveEngineSpeedGreater2ndAccelStartPhase  MinDriveEngineSpeedGreater2ndDecelStartPhase  TimeEndOfStartPhase
    DoNotMergeClutchIntoGearsOutput  LimitVehicleSpeedByAvailablePower  ReturnAdjustedEngSpeedsAndAvlPowers
    AllowSlippingClutchFor1stAnd2ndGear
    """.split(),
)

ShiftPointsOuts = namedtuple(
    "ShiftPointsOuts",
    "case veh"  # Not outs, added for reference
    ## Order is important when callling mat-functions!
    """
    CalculatedGearsOutput AverageGearOutput AdjustedMax95EngineSpeed TraceTimesOutput RequiredVehicleSpeedsOutput
    RequiredPowersOutput RequiredEngineSpeedsOutput AvailablePowersOutput PowerCurveOutput MaxEngineSpeedCycleOutput
    MaxEngineSpeedReachableOutput MaxEngineSpeedOutput MaxVehicleSpeedCycleOutput MaxVehicleSpeedReachableOutput
    GearMaxVehicleSpeedReachableOutput MinDriveEngineSpeed1stOutput MinDriveEngineSpeed1stTo2ndOutput
    MinDriveEngineSpeed2ndDecelOutput MinDriveEngineSpeed2ndOutput MinDriveEngineSpeedGreater2ndOutput GearsOutput
    ClutchDisengagedOutput ClutchUndefinedOutput ClutchHSTOutput GearCorrectionsOutput ChecksumVxGearOutput
    """.split(),
)


def extract_run_shift_points_inputs(
    case_no: int, mat_db: Dict[str, pd.DataFrame], **overrides
) -> dict:
    """
    Return an ordered dictionary with (pandas) values for mat-function `scaleTrace.m`.

    :return:
        data are regular pandas
        (apply :func:`columnize_pandas()` before calling matlab)
    """

    case = mat_db["case"].loc[case_no]

    veh_no = case.veh
    veh = mat_db["vehicle"].loc[veh_no]

    ## Careful selection of ndv.g.dtype := "string" (Panda's extension-type)
    #  to do the following::
    #      ndv = (ndv.g.to_numpy(str), ndv.ndv)
    ndv = mat_db["gearbox"].loc[veh_no, :].copy()
    ndv["g"] = ndv["g"].str.slice_replace(0, 0, "g")

    wot = mat_db["engine"].loc[veh_no, :].copy()
    # engine.txt:ASM contains fractions [0-->1] but FullPowerCurve.ASM expects percentages.
    wot["ASM"] = wot.ASM * 100

    trace = mat_db["scaled_traces"].loc[case_no, ["v"]].reset_index(level="t")

    args = ShitPointsInps(
        **{
            # VEHICLE
            "RatedEnginePower": veh.p_rated,  # legacy, derrived from Wot if 0
            "RatedEngineSpeed": veh.n_rated,  # legacy, derrived from Wot if 0
            "IdlingEngineSpeed": veh.n_idle,
            "Max95EngineSpeed": veh.n_max1,
            "NoOfGears": veh["#g"],
            "VehicleTestMass": veh.m_test,
            "f0": veh.f0,
            "f1": veh.f1,
            "f2": veh.f2,
            "SafetyMargin": 100 * veh.SM,  # x100, see note on `wot`, above.
            "Ndv": ndv,
            "FullPowerCurve": wot,
            "Trace": trace,
            # CASE
            "AdditionalSafetyMargin0": case.asm_0,
            "StartEngineSpeed": case.n_asm_s,
            "EndEngineSpeed": case.n_asm_e,
            "MinDriveEngineSpeed1st": case.n_min1,
            "MinDriveEngineSpeed1stTo2nd": case.n_min12,
            "MinDriveEngineSpeed2ndDecel": case.n_min2d,
            "MinDriveEngineSpeed2nd": case.n_min2,
            "MinDriveEngineSpeedGreater2nd": case.n_min3,
            "EngineSpeedLimitVMax": case.n_lim,
            "MaxTorque": 0,  # DEFUNCT
            "ExcludeCrawlerGear": case.excl1,
            "AutomaticClutchOperation": case.autom,
            "SuppressGear0DuringDownshifts": case.supp0,
            "MinDriveEngineSpeedGreater2ndAccel": case.n_min3a,
            "MinDriveEngineSpeedGreater2ndDecel": case.n_min3d,
            "MinDriveEngineSpeedGreater2ndAccelStartPhase": case.n_min3as,
            "MinDriveEngineSpeedGreater2ndDecelStartPhase": case.n_min3ds,
            "TimeEndOfStartPhase": case.t_start,
            "DoNotMergeClutchIntoGearsOutput": True,  # hard-coded in `calc_all_cases.m` (NOT `case.merge` all false)
            "LimitVehicleSpeedByAvailablePower": True,  # hard-coded in `calc_all_cases.m`
            "ReturnAdjustedEngSpeedsAndAvlPowers": True,  # hard-coded in `calc_all_cases.m`
            "AllowSlippingClutchFor1stAnd2ndGear": False,  # hard-coded in `calc_all_cases.m`
        }
    )

    args = args._replace(**overrides)

    return args


def run_shift_points_RAW(
    case_no: int, mat_db: Dict[str, pd.DataFrame], **overrides
) -> TraceScaledOuts:
    """
    Run `calculateShiftpointsNdvFullPC.m` for the given `case_no` in `mat_db`.

    "param mat_db:
        must include results of `scale_trace()`, `scaled_scalars` & `scaled_traces`

    :return:
        results as builtins or numpy-arrays
    """

    df_case = mat_db["case"]
    veh_no = df_case.at[case_no, "veh"]

    args = extract_run_shift_points_inputs(case_no, mat_db, **overrides)
    mat_ized = mat_ize(args)
    outputs = oc.calculateShiftpointsNdvFullPC(*mat_ized, nout=26)
    outputs = ShiftPointsOuts(case_no, veh_no, *outputs)

    return outputs


def run_all_shift_points(
    mat_db: Mapping[int, Union[TraceScaledInps, Exception]],
    results_varname="shift_results",
) -> Mapping[int, Union[TraceScaledOuts, Exception]]:
    """Run `scaleTrace.m` for all cases in in `mat_db`."""

    globs = globals()
    results = globs.get(results_varname, [])
    globs[results_varname] = results

    for case_no in mat_db["case"].index:
        if len(results) >= case_no:  # cases start from 1
            log.info("Case(%s) SKIPPED, already in results.", case_no)
            continue
        try:
            log.info("Case(%s) ...", case_no)
            results.append(run_shift_points_RAW(case_no, mat_db))
        except Exception as ex:
            log.error("Case(%s) failed due to: %s", case_no, ex)
            raise

    return results


# shift_results = [run_shift_points_RAW(1, mat_db)]  # TEST-CASE
# del shift_results  # UNCOMMENT to recalc all vehicles.
# del shift_results[-1]
# %time shift_results = run_all_shift_points(mat_db);

# %% [markdown]
# ### SHIFT *output* files
# Conceptually, the results are stored in CSV files inside `Notebooks/Matlab/outs`:
#
# - `shift.txt`  (the "cycle")
# - `shift_condensed.txt`  (merged in "cycle")
# - `shift_power.txt`  (not realy needed)
# - `case_result.txt` (partial)

# %% [markdown]
# ### Process SHIFT results

# %%
# Pick the case_no=1 results to research.
shift_fields, previews = research_mat_results(shift_results[0])
display(
    shift_fields,
)  # *previews)

# %%
df_shift_scalars = mat_db["shift_scalars"] = merge_scalar_results(
    shift_results, shift_fields.query("is_scalar").index
)

display(
    #     df_shift_scalars.sample(nsamples).sort_index(),
    df_shift_scalars,
    df_shift_scalars.describe(),
    msno.matrix(df_shift_scalars.replace(0, np.NAN)),
    list(mat_db),
)


# %%
def convert_booleans(df: pd.DataFrame):
    """Convert to booleans columns with just [0, 1]. """
    nums = df.select_dtypes(np.number)
    booleans = ((nums == 0) | (nums == 1)).all()
    booleans = booleans[booleans].index.tolist()

    return df.astype(dict.fromkeys(booleans, bool))


def merge_shift_cycle(
    case_result: NamedTuple,
    fields: pd.DataFrame,
    field_sizing_column="size",
    time_column="TraceTimesOutput",
):
    """
    Merge all outvars in `case_result` having the same "sizing" as `field_column_match` in `fields`

    and convert any integer/boolean columns."""
    t = getattr(case_result, time_column)
    sizing_value = fields.at[time_column, field_sizing_column]
    query = f"{field_sizing_column} == {sizing_value}"
    columns = [col for col in fields.query(query).index.tolist()]

    res = pd.DataFrame({col: getattr(case_result, col).ravel() for col in columns})

    res = res.convert_dtypes()
    res = convert_booleans(res)

    res.set_index(time_column)
    res.index.name = "t"

    return res


# merge_shift_cycle(shift_results[0], shift_fields)[5:100] ## TEST_CASE


def concat_cycles(results):
    dfs = {r.case: merge_shift_cycle(r, shift_fields) for r in results}
    cycles = pd.concat(dfs.values(), keys=dfs.keys(), axis=0, names=["case", "t"])

    return cycles


shift_cycles = concat_cycles(shift_results)
shift_cycles

# %%
## Check what other NON-SCALAR fields remain to be converted?
shift_fields.query("not is_scalar and squeeze < 18")


# %% [markdown]
# NOTE: From those above, only `PowerCurveOutput` will not be stored anywhere in `mat_db`,
# which corresponds to `engine_result.txt` file.
#
# The rest will be tansformed into frames, below, and the concatenate with the big CYCLE, further below.

# %%
def conv_CalculatedGearsOutput(cell):
    """This output corresponds to `shift_condensed.txt` file contents."""
    res = pd.DataFrame(
        pd.Series(cell[0][1]).str.strip(),
        index=pd.Index(cell[0][0].ravel(), name="t", dtype=int),
        columns=["shift"],
    )

    return res


# conv_CalculatedGearsOutput(shift_results[0].CalculatedGearsOutput)  # TEST_CASE


def cell_to_df(cell):
    """This output corresponds to `engine_result.txt` file contents."""
    res = pd.DataFrame(np.hstack(cell.squeeze()))

    return res


# shift_results[0].PowerCurveOutput  # TEST_CASE


conv_specs = [
    # FIELD, CONVERSION_FUNC, ARGS
    # Corresponds to `shift_condensed.txt`
    ("CalculatedGearsOutput", conv_CalculatedGearsOutput, ()),
    # corresponds to `engine_result.txt`
    ("PowerCurveOutput", cell_to_df, ()),
    ("RequiredEngineSpeedsOutput", cell_to_df, ()),
    ("AvailablePowersOutput", cell_to_df, ()),
]


## Apply specs on results of all cases,
#  and concat in hierarchical sub-frames.
def convert_by_specs(results, conv_specs):
    def apply_spec(field, fun, args):
        dfs = {r.case: fun(getattr(r, field), *args) for r in results}
        out = pd.concat(dfs.values(), keys=dfs.keys(), axis=0, names=["case", "t"])

        return out

    return {field: apply_spec(field, *spec) for field, *spec in conv_specs}


shift_dfs = convert_by_specs(shift_results, conv_specs)
for name, df in shift_dfs.items():
    display(name, df.loc[pd.IndexSlice[:, 10:22], :])


# %%
## make a single (hierarchical by vehicle & time) CYCLES frame with all items.
#
def concat_cycle(shift_cycles, shift_dfs):
    cycles = shift_cycles.set_axis(
        pd.MultiIndex.from_product([shift_cycles.columns, [""]]), axis=1
    )

    shifts_condensed = shift_dfs["CalculatedGearsOutput"]
    shifts_condensed = shifts_condensed.set_axis(
        pd.MultiIndex.from_product([shifts_condensed.columns, [""]]), axis=1
    )

    return pd.concat(
        (
            cycles,
            shifts_condensed,
            *(
                shift_dfs[k].set_axis(
                    pd.MultiIndex.from_product(
                        # +1 so gears start from 1st
                        [[k], shift_dfs[k].columns + 1],
                    ),
                    axis=1,
                )
                for k in ["RequiredEngineSpeedsOutput", "AvailablePowersOutput"]
            ),
        ),
        axis=1,
    ).rename_axis(["item", "gear"], axis=1)


df_shift_cycles = mat_db["shift_cycles"] = concat_cycle(shift_cycles, shift_dfs)
df_shift_cycles.sample(nsamples).sort_index()

# %%
list(mat_db)
