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
# # VMAX experiments

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
import logging
from pathlib import Path, PurePosixPath as P
import sys

from columnize import columnize
import numpy as np
import pandas as pd
from pandas import HDFStore, IndexSlice as idx
from pandas.core.generic import NDFrame
from matplotlib import pyplot as plt
import qgrid
import wltp
from wltp import io as wio, vmax, engine, vehicle, vmax, cycler
from wltp.experiment import Experiment

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

pd.set_option("display.max_columns", 32)

# %%
## DEFINITIONS
#
inp_h5fname = "VehData/WltpGS-msaccess.h5"
out_h5fname = "VehData/WltpGS-pyalgo.h5"
c_n, c_p, c_n_norm, c_p_norm = "n", "Pwot", "n_norm", "p_norm"

# vehdb.print_nodes(inp_h5fname)
# vehdb.print_nodes(out_h5fname)

# %%
vehnum = 35
ac_props, wot, _ = vehdb.load_vehicle_accdb(inp_h5fname, vehnum)
wot


# %% [markdown]
# ## Good case from h5db

# %%
def read_veh(vehnum, silent=False):
    ac_props, wot, _ = vehdb.load_vehicle_accdb(inp_h5fname, vehnum)
    py_props, _, gwots = vehdb.load_vehicle_pyalgo(out_h5fname, vehnum)

    if not silent:
        display(ac_props[["no_of_gears", "gear_v_max", "v_max"]], "", py_props)
        ax = None
        ax = gwots.loc[:, ("g6 g5 g4".split(), "p_avail")].plot(ax=ax)
        gwots.loc[:, ("g6 g5 g4".split(), "p_resist")].plot(ax=ax)

    return ac_props, py_props, wot, gwots


caseno = 21
ac_props, py_props, wot, gwots = read_veh(caseno)

# %%
display(wot)


# %%
def plot_gwots(ac_props, py_props, gwots, g, bottom_g, *, offset=2):
    """
    :param gwots:
        a df V x (gear, item)
    """
    gwots = gwots.copy()
    gwots.index.name = "V [kmh]"

    v_max = py_props["v_max"]
    g_max = py_props["g_vmax"]

    v_max_ac = ac_props["v_max"]
    g_max_acc = ac_props["gear_v_max"]
    g_top = ac_props["no_of_gears"]

    v_range = idx[v_max - offset : v_max + offset]
    g_range = [f"g{i}" for i in range(g_top, bottom_g)]

    ax = gwots.loc[v_range, (f"g{g}", "p_resist")].plot(linewidth=3)
    ax = gwots.loc[v_range, (slice(f"g{g_top}", f"g{bottom_g}"), "p_avail")].plot(ax=ax)
    ax.axvline(v_max, color="orange", label=f"v_max_python(g{g_max})")
    ax.axvline(v_max_ac, color="green", label=f"v_max_accdb(g{g_max_acc})")
    ax.legend()
    ax.grid(axis="x", which="both")


plot_gwots(ac_props, py_props, gwots, 6, 5)


# %%
def disp_gwots(ac_props, py_props, gwots, g, offset=0.5):
    gwots.index.name = "V [kmh]"
    v_max_ac = ac_props["v_max"]
    v_max = py_props["v_max"]
    # display(gwots['g5'].dropna())
    display(gwots.loc[v_max - offset : v_max + offset, f"g{g}"])


disp_gwots(ac_props, py_props, gwots, 6)

# %%
disp_gwots(ac_props, py_props, gwots, 5)


# %% [markdown]
# ## Good MAXWOT case from h5db

# %%
def read_veh(vehnum, silent=False):
    ac_props, wot, n2vs = vehdb.load_vehicle_accdb(inp_h5fname, vehnum)
    py_props, _, gwots = vehdb.load_vehicle_pyalgo(out_h5fname, vehnum)

    if not silent:
        display(ac_props[["no_of_gears", "gear_v_max", "v_max"]], "", py_props)
        ax = None
        ax = gwots.loc[:, ("g6 g5 g4".split(), "p_avail")].plot(ax=ax)
        gwots.loc[:, ("g6 g5 g4".split(), "p_resist")].plot(ax=ax)

    return ac_props, py_props, wot, gwots, n2vs


caseno = 48
ac_props, py_props, wot, gwots, n2vs = read_veh(caseno)

# %%
display(wot)


# %%
def plot_gwots(ac_props, py_props, gwots, g, bottom_g, *, offset=2):
    gwots.index.name = "V [kmh]"
    v_max_ac = ac_props["v_max"]
    v_max = py_props["v_max"]
    g_top = ac_props["no_of_gears"]
    g_max = py_props["g_vmax"]
    g_max_acc = ac_props["gear_v_max"]
    v_range = idx[v_max - offset : v_max + offset]
    ax = gwots.loc[v_range, (f"g{g}", "p_resist")].plot(linewidth=3)
    ax = gwots.loc[v_range, (slice(f"g{g_top}", f"g{bottom_g}"), "p_avail")].plot(ax=ax)
    ax.axvline(v_max, color="orange", label=f"v_max_python(g{g_max})")
    ax.axvline(v_max_ac, color="green", label=f"v_max_accdb(g{g_max_acc})")
    ax.legend()
    ax.grid(axis="x", which="both")


plot_gwots(ac_props, py_props, gwots, 6, 4)


# %%
def disp_gwots(ac_props, py_props, gwots, g, offset=0.5):
    gwots.index.name = "V [kmh]"
    v_max_ac = ac_props["v_max"]
    v_max = py_props["v_max"]
    # display(gwots['g5'].dropna())
    display(gwots.loc[v_max - offset : v_max + offset, f"g{g}"])


disp_gwots(ac_props, py_props, gwots, 6)

# %% [markdown]
# ## BAD case from h5db
#
# ```
#          v_max  g_vmax
# accdb:   141.1       6
# pyalgo:  141.1       5
# ```
# Strangely, accdb finds the correct `v_max`, but `g6` does not seem to cross `p_resist` at that point...

# %%
caseno = 25
ac_props, py_props, wot, gwots, n2vs = read_veh(caseno)

# %%
plot_gwots(ac_props, py_props, gwots, 6, 5)

# %%
disp_gwots(ac_props, py_props, gwots, 6)
disp_gwots(ac_props, py_props, gwots, 5)

# %% [markdown]
# ## Manual run

# %%
caseno = 64
# caseno = 48  # maxWOT
# caseno = 20  # maxWOT last gear
ac_props, wot, n2vs = vehdb.load_vehicle_accdb(inp_h5fname, caseno)
wot = wot.rename(vehdb.accdb_renames(), axis=1)
wot["n"] = wot.index
ac_props = ac_props.rename(vehdb.accdb_renames())
gwots = engine.interpolate_wot_on_v_grid(wot, n2vs)
gwots = engine.attach_p_avail_in_gwots(gwots, f_safety_margin=0.1)
gwots["p_resist"] = vehicle.calc_p_resist(
    gwots.index, ac_props.f0, ac_props.f1, ac_props.f2
)

# %%
w = wio.pstep_factory.get()
gidx = wio.GearMultiIndexer.from_df(gwots)

rec = vmax.calc_v_max(gwots)
print(f"VMAX: {rec.v_max}, G_VMAX: {rec.g_vmax}, maxWOT? {rec.is_n_lim}")
display(rec.wot[f"g{rec.g_vmax}"])

# %% [markdown]
# # Museum

# %%
## Test V_GRID construction always inside WOT_N
engine._make_v_grid(1.201, 1.4999)
