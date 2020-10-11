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
# ## Run cycle on a Vehicle
# Quick'n Dirty sample code for running a cycle on user-defined vehicle data.

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
##################################################
## Set PYTHONPATH and import relevant libraries ##
##################################################
from typing import Union, List, Callable, Any, Sequence as Seq
import io
import itertools as itt
import logging
from pathlib import Path, PurePosixPath as P
from pprint import pprint
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
from wltp.experiment import Experiment
from wltp import datamodel, io as wio, engine, vmax, vehicle, cycler, utils

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

# %% [markdown]
# ## Run a vehicle with user-specified data

# %%
## For more input data, see https://wltp.readthedocs.io/en/latest/code.html#schema
#
mdl = datamodel.get_model_base()
mdl["f0"] = 395.78
mdl["f1"] = 0.0
mdl["f2"] = 0.15
mdl["unladen_mass"] = 2527.0
mdl["test_mass"] = 2827.0
mdl["p_rated"] = 95.3000030517578
mdl["n_rated"] = 3500
mdl["n_idle"] = 750
mdl["v_max"] = 119.8
# mdl["n_min_drive"] =
# mdl["n_min_drive_up"] = ...
# mdl["n_min_drive_down"] = ...
# mdl["n_min_drive_up_start"] = ...
# mdl["n_min_drive_down_start"] = ...
# mdl["t_cold_end"] = ...
mdl["n2v_ratios"] = [122.88, 75.12, 50.06, 38.26, 33.63]

mdl["wot"] = pd.read_csv(
    io.StringIO(
        """
n	p
1000	18.80
1250	34.00
1500	51.80
1750	62.30
2000	71.20
2250	78.80
2500	86.40
2750	89.70
3000	93.00
3250	94.15
3500	95.30
3750	95.00
4000	94.70
4250	92.15
4500	89.60
4750	86.95
5000	84.30
"""
    ),
    sep="\t",
    header=0,
)

datamodel.validate_model(mdl, additional_properties=True)
exp = Experiment(mdl, skip_model_validation=True)

mdl = exp.run()

oprops = {
    "pmr": mdl["pmr"],
    "n95_low": mdl["n95_low"],
    "n95_high": mdl["n95_high"],
    "v_max": mdl["v_max"],
    "n_vmax": mdl["n_vmax"],
    "g_vmax": mdl["g_vmax"],
    "n_max1": mdl["n_max1"],
    "n_max2": mdl["n_max2"],
    "n_max3": mdl["n_max3"],
    "n_max": mdl["n_max"],
    "wltc_class": mdl["wltc_class"],
    "f_dsc_raw": mdl["f_dsc_raw"],
    "f_dsc": mdl["f_dsc"],
}

pprint(oprops)
display(mdl["cycle"])

# %% [markdown]
# ## Run a case from AccDb
# The same vehicle data as above, read from h5db.

# %%
h5 = "VehData/WltpGS-msaccess.h5"
prop, wot, n2vs = vehdb.load_vehicle_accdb(h5, 1)
acc_cycle = vehdb.load_vehicle_nodes(h5, 1, "cycle")

# %%
case_no = 88
props, wot, n2vs = vehdb.load_vehicle_accdb(h5, case_no)
mdl = vehdb.mdl_from_accdb(props, wot, n2vs)

datamodel.validate_model(mdl, additional_properties=True)
exp = Experiment(mdl, skip_model_validation=True)

# %time mdl = exp.run()

oprops = {
    "pmr": mdl["pmr"],
    "n95_low": mdl["n95_low"],
    "n95_high": mdl["n95_high"],
    "v_max": mdl["v_max"],
    "n_vmax": mdl["n_vmax"],
    "g_vmax": mdl["g_vmax"],
    "n_max1": mdl["n_max1"],
    "n_max2": mdl["n_max2"],
    "n_max3": mdl["n_max3"],
    "n_max": mdl["n_max"],
    "wltc_class": mdl["wltc_class"],
    "f_dsc_raw": mdl["f_dsc_raw"],
    "f_dsc": mdl["f_dsc"],
}

pprint(oprops)
display(mdl["cycle"])

# %%
print(sorted(mdl.keys()))

# %%
ax = mdl["cycle"][["V_cycle", "v_target"]].plot()
ax = mdl["cycle"][["p_req", "p_avail"]].plot(ax=ax, secondary_y=True)

# %% [markdown]
# ## Even simpler case

# %%
import pandas as pd
from wltp import datamodel
from wltp.experiment import Experiment

inp_mdl = datamodel.get_model_base()
inp_mdl.update(
    {
        "unladen_mass": None,
        "test_mass": 1100,  # in kg
        "p_rated": 95.3,  # in kW
        "n_rated": 3000,  # in RPM
        "n_idle": 600,
        "n2v_ratios": [122.88, 75.12, 50.06, 38.26, 33.63],
        ## For giving absolute P numbers,
        #  rename `p_norm` column to `p`.
        #
        "wot": pd.DataFrame(
            [[600, 0.1], [2500, 1], [3500, 1], [5000, 0.7]], columns=["n", "p_norm"]
        ),
        "f0": 395.78,
        "f1": 0,
        "f2": 0.15,
    }
)
datamodel.validate_model(inp_mdl, additional_properties=True)
exp = Experiment(inp_mdl, skip_model_validation=True)

# exp = Experiment(inp_mdl)
out_mdl = exp.run()
print(f"Available values: \n{list(out_mdl.keys())}")
print(f"Cycle: ")
display(out_mdl["cycle"])
