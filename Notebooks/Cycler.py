# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.3.4
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %% [markdown]
# ## Develop `wltp/cycler.py`
# (WIP) run a vehicle from the h5db, step-by-step.

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
from typing import Union, List, Callable, Any, Sequence as Seq
import io
import itertools as itt
import logging
from pathlib import Path, PurePosixPath as P
import sys

from columnize import columnize
import numpy as np
import pandas as pd
from pandas import HDFStore, IndexSlice as idx
from pandas.core.generic import NDFrame
from matplotlib import pyplot as plt
from pandalone.mappings import Pstep
import qgrid

import wltp
from wltp import engine
from wltp.experiment import Experiment
from wltp import datamodel, io as wio, engine, nmindrive, vmax, vehicle, cycler

## Add tests/ into `sys.path` to import `vehdb` module.
#
proj_dir = str(Path(wltp.__file__).parents[1] / "tests")
if proj_dir not in sys.path:
    sys.path.insert(0, proj_dir)

import vehdb

idx = pd.IndexSlice
log = logging.getLogger("VMax.ipynb")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s|%(levelname)4.4s|%(module)s:[%(funcName)s]:\n  +--> %(message)s",
    datefmt="%Y-%m-%d,%H:%M:%S",
)

pd.set_option("display.max_columns", 64)

# %%
h5 = "VehData/WltpGS-msaccess.h5"
caseno = 1
prop, wot, n2vs = vehdb.load_vehicle_accdb(h5, caseno)
acc_cycle = vehdb.load_vehicle_nodes(h5, 1, "cycle")

# %%
print(list(prop.index))

# %%
# renames = vehdb.accdb_renames()
# prop = prop.rename(renames)
mdl = vehdb.mdl_from_accdb(prop, wot, n2vs)
datamodel.validate_model(mdl, additional_properties="true")
wot = mdl["wot"]

# %%
print(list(acc_cycle.columns))
print(list(mdl.keys()))

# %%
gwots = engine.interpolate_wot_on_v_grid(wot, n2vs)
gwots = engine.attach_p_avail_in_gwots(gwots, f_safety_margin=0.1)
gwots["p_resist"] = vehicle.calc_p_resist(gwots.index, mdl["f0"], mdl["f1"], mdl["f2"])

# %%
V = datamodel.get_class_v_cycle(3)

# %%
cb = cycler.CycleBuilder(V)
pm = cycler.PhaseMarker()

# %%
wltc_parts = datamodel.get_class_parts_limits(3, edges=True)
cb.cycle = pm.add_class_phase_markers(cb.cycle, wltc_parts)

# %%
cb.cycle = pm.add_transition_markers(cb.cycle, cb.V, cb.A)
cb.cycle.select_dtypes(bool).sum()

# %%
t_cold_end = 470  # gap for all classes
for err in cb.validate_nims_t_cold_end(t_cold_end, wltc_parts):
    raise err

# %%
acc_cycle = vehdb.load_vehicle_nodes(h5, caseno, "cycle")
print(list(acc_cycle.columns))

# %%
## INPUTS testing ok_flags2 selection
#
c = wio.pstep_factory.get().cycle

ng = 6
n95_high = engine.calc_n95(wot, mdl["n_rated"], mdl["p_rated"])[0]
v_max_cycle = cb.V.max()
vmax_rec = vmax.calc_v_max(gwots)
g_vmax = vmax_rec.g_vmax
n2v_vmax = n2vs[g_vmax - 1]
n_max_cycle = v_max_cycle * n2v_vmax
n_max_cycle = v_max_cycle * n2v_vmax
nmins = nmindrive.mdl_2_n_min_drives(*mdl)

# %%
cb.add_wots(gwots)

# %%
kr = 1.03
SM = 0.1
cb.cycle["p_inert"] = vehicle.calc_inertial_power(cb.V, cb.A, prop.test_mass, kr)
cb.cycle["p_req"] = vehicle.calc_required_power(
    cb.cycle["p_inert"], cb.cycle["p_resist"]
)
p_remain = cycler.calc_p_remain(cb.cycle["p_req"], cb.cycle["p_avail"])


# %%
def flag_aggregates(ok_flags):
    trues = ok_flags[ok_flags >= 0].sum()
    df = pd.concat((trues, ok_flags.sum() - trues), axis=1)  # negatives are NANs
    df.columns = ("trues", "NANs")
    return df


ok_flags = cb.calc_initial_gear_flags(
    g_vmax=g_vmax, n95_high=n95_high, n_max_cycle=n_max_cycle, nmins=nmins
)
flag_aggregates(ok_flags)

# %%
ok_flags = cb.calc_initial_gear_flags(
    g_vmax=g_vmax, n95_high=n95_high, n_max_cycle=n_max_cycle, nmins=nmins
)
flag_aggregates(ok_flags)

# %%
ok_n = cb.combine_ok_n_gear_flags(ok_flags)
ok_flags1 = pd.concat((ok_flags, ok_n), axis=1)
ok_gears = cb.derrive_ok_gears(ok_flags1)
ok_gears.sum()

# %%
ok_n = cb.combine_ok_n_gear_flags(ok_flags)
ok_flags1 = pd.concat((ok_flags, ok_n), axis=1)
ok_gears = cb.derrive_ok_gears(ok_flags1)
ok_gears.sum()

# %%
g_min, g_max0, _ = cb.make_gmax0(ok_gears)
cycle = pd.concat((cb.cycle, ok_flags1, ok_gears, g_min, g_max0), axis=1)

# %%
g_max0.plot()
acc_cycle.g_max.plot()
g_max0_diff = (g_max0 - acc_cycle.g_max).abs()
g_max0_diff[g_max0_diff == 0] = np.NAN
display(
    pd.concat(
        (g_max0.describe(), acc_cycle.g_max.describe(), g_max0_diff.describe()), axis=1
    )
)

# %%
## Most differences are in G1-->G2 shifts
# (which is not implemented in `g_vmax0`).
display(cycle.loc[~g_max0_diff.isnull() & (g_max0_diff != 0)])

# %%
ok_p = cycler.calc_ok_p_rule(pd.concat((cycle, p_remain), axis=1), cb.gidx)
ok_p

# %%
cb.add_columns(p_remain, ok_flags1, ok_gears, g_min, g_max0)

# %%
cycler.fill_insufficient_power(cb.cycle)

# %%
################################
## MOVED to compare-notebook! ##
################################
from ipywidgets import interact, interactive, fixed, interact_manual, widgets

max_zoom = 48.0

## Scale each flag into a different value, to plot separately, and
#  to plot in the same axis as V
#  (bc when plotting flags in `secondary_y`, grid is not working)
#
mul = 2
flag_count = ok_flags.shape[1]
gear_count = ok_gears.shape[1]
ok_flags2 = ok_flags.copy()
ok_flags2[ok_flags2 < 0] = np.NAN  # Restore NANFLAG --> NAN
ok_flags2 = ok_flags2 * (np.arange(flag_count) + 1) * mul
ok_gear2 = ok_gears * (np.arange(gear_count) + flag_count + 1) * mul


@interact(
    gear=wio.GearMultiIndexer.from_df(ok_flags)[:],
    zoom=(1.0, max_zoom, 1.0),
    pan=(0, max_zoom, 1),
    display_id="plot",
)
def plot_gear(gear="g2", zoom=48, pan=13.8):
    ax = None

    clen = len(cb.cycle)
    viewlen = int(clen / zoom)
    offset = int(pan * (clen - viewlen) / max_zoom)
    scale = idx[offset : offset + viewlen]

    cycle = cb.cycle.loc[scale]
    ok_flags = ok_flags2.loc[:, idx[:, gear]].iloc[scale]
    ok_gear = ok_gear2.loc[scale]

    ax = cycle["V_cycle"].plot.line(ax=ax, linewidth=4, figsize=(20, 8))
    ax = ok_flags.plot.line(ax=ax)
    ax = ok_gear.plot.line(ax=ax, linewidth=3)

    ax.grid(True, axis="both", which="both")

    ## IF only i could find quickly how to display the df BELOW the plot...
    # display(cycle, display_id='grid')


# %% [markdown]
# ## Museum

# %%
from wltp.cycles import cycle_checksums

cycle_checksums()

# %%
from wltp.cycles import cycle_phases

cycle_phases()

# %%
## Is clutch-undefined only used for gear 1?
acc_cycle.loc[
    cycler.timelens(acc_cycle.clutch == "undefined"), ["v", "a", "gear", "clutch"]
]

# %%
## AccDB: note that acc/dec/cruise are "gradients", with threshold 0.278.
acc_cycle.loc[:100, ["a2", "acc", "cruise", "dec"]].astype(int).plot()
acc_cycle.loc[:100, "v"].plot(secondary_y=True)

# %%
cycle = pd.DataFrame(
    {
        "v": [0, 0, 3, 3, 5, 8, 8, 8, 6, 4, 5, 6, 6],
        "accel": [0, 0, 0, 1, 1, 1, 0, 0, 0, 1, 1, 1, 0],
        "cruise": [0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0],
        "decel": [0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0],
        "up": [0, 0, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1],
        "init": [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    }
)
pm = cycler.PhaseMarker()


def phase(cond):
    return pm._identify_consecutive_truths((cycle.v > 1) & cond, True).astype(int)


A = (-cycle.v.astype(int)).diff(-1)  # GTR's acceleration definition
assert (phase(A > 0) == cycle.accel).all()
assert (phase(A == 0) == cycle.cruise).all()
assert (phase(A < 0) == cycle.decel).all()
