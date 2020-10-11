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
# # Parse excel files into a HDF5 file
# It builds an an [HDF5 file](https://pandas.pydata.org/pandas-docs/stable/user_guide/io.html#io-hdf5)
# with the the *vehicle inputs* & *outpus* (`prop`, `wot`, `cycle`) from accdb.
#
# ## To see the full tree
# ...check the `README.py`,
# ## to run this notebook in your own jupyter-server
# ...read instructions on the `README.md`,
# ## to inspect and get help on the HDF5 file
# ...read instructions on the `README.md` and consult the `HDF5-API.ipynb` notebook.

# %% tags=["parameters"]
### Cell tagged as `parameters` for *papermill*.
#
skip_h5_write = False
del_h5_on_start = False  # overridden by `skip_h5_write=True`

# %%
## To autoreload codein python files here.
# %load_ext autoreload
# %autoreload 2

## Auto-format cells to ease diffs.
# %load_ext lab_black

# %%
import functools as ftt
import itertools as itt
import logging
from pathlib import Path
import re
import sys
from typing import Tuple, Dict

from columnize import columnize
import numpy as np
from pandalone import xleash
import qgrid
import pandas as pd
from pandas import HDFStore
import wltp

## Add tests/ into `sys.path` to import `vehdb` module.
#
proj_dir = str(Path(wltp.__file__).parents[1] / "tests")
if proj_dir not in sys.path:
    sys.path.insert(0, proj_dir)

import vehdb

idx = pd.IndexSlice
log = logging.getLogger("CarsDB-inputs.ipynb")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s|%(levelname)4.4s|%(module)s:[%(funcName)s]:\n  +--> %(message)s",
    datefmt="%Y-%m-%d,%H:%M:%S",
)

# %%
## DEFINITIONS
#
h5fname = "VehData/WltpGS-msaccess.h5"
c_vehnum, c_case, c_engno, c_n, c_pwot, c_SM, c_ASM = (
    "vehicle_no",
    "case_no",
    "no_engine",
    "n",
    "Pwot",
    "SM",
    "ASM",
)
c_case_id = c_case

# %%
## UNCOMMENT next command & run to DELETE the db-file, and rebuild it.
if not skip_h5_write and del_h5_on_start:
    # !rm -f {h5fname}

# %%
vehdb.print_nodes(h5fname)

# %%
# a=xleash.lasso('VehData/calculation_parameter_all.15092019_prog_code_dev.xlsx#calculation_parameter_all!::["df"]')
# b=xleash.lasso('VehData/calculation_parameter_all.20092019.xlsx#calculation_parameter_all!::["df"]')
# bad_cols = (a == b).all()
# bad_cols[~bad_cols]

# %%
veh_inputs_excel = (
    Path("VehData/calculation_parameter_all.20092019.xlsx"),
    "calculation_parameter_all",
)
specs = xleash.lasso('%s#%s!::["df"]' % veh_inputs_excel)

wots_excel = (Path("VehData/TB_Pwot.20092019.xlsx"), "TB_Pwot")
pwots = xleash.lasso('%s#%s!::["df"]' % wots_excel)

# %% [markdown]
# ## PRE 20190728 COLUMNS
# ```
# vehicle_no  rated_power     v_max  ndv_6               no_of_gears  v_max_4  v_max_10  n_min_drive_set  n95_high   at_s
# comments    kerb_mass       ndv_1  ndv_7               ng_vmax      v_max_5  v_s_max   n_min_wot        n_max1     above_s
# pmr_km      test_mass       ndv_2  ndv_8               v_max_ext    v_max_6  n_vmax    f_dsc_req        n_max2     vmax_determined_by_n_lim
# pmr_tm      rated_speed     ndv_3  ndv_9               v_max_1      v_max_7  f0        Pres_130         n_max3
# IDclass     idling_speed    ndv_4  ndv_10              v_max_2      v_max_8  f1        Pres_130_Prated  n_max_wot
# class       v_max_declared  ndv_5  v_max_transmission  v_max_3      v_max_9  f2        n95_low          below_s
#
# Index(['no_engine', 'n', 'Pwot', 'Twot', 'Pwot_norm', 'Twot_norm', 'SM', 'ASM',
#        'Pavai'],
#       dtype='object')
# ```

# %%
import qgrid

print(columnize(list(specs.columns), displaywidth=160))
print(pwots.columns)
print(specs[c_vehnum].unique(), specs[c_case].unique())
display(vehdb.grid(specs, fitcols=False), vehdb.grid(pwots))


# %%
def extract_SM_from_pwot(
    pwot, c_n=c_n, c_pwot=c_pwot, c_SM=c_SM, c_ASM=c_ASM
) -> "Tuple(pd.DataFrame, float)":
    """
    Keep just (n, Pwot, ASM) columns & extract SM column as scalar value.

    :param pwot:
        the wot-curve dataframe for a single vehicle, with columns::

            IX	no_engine	n	Pwot	Twot	Pwot_norm	Twot_norm	SM	ASM	Pavai

    :return:
        wot(without SM), SM
        where `wot` is indexed by engine-speed(n)
    """
    SM = vehdb.get_scalar_column(pwot, c_SM)
    pwot = pwot.set_index(c_n).drop(c_SM, axis=1)

    return pwot, SM


# ## TEST
# extract_SM_from_pwot(pwots.loc[pwots[c_engno] == 3])

# %%
veh_results_excel = ("VehData/gearshift_table_all.22102019.xlsx", "gearshift_table_all")
# NOTE: it may take ~5 minute to load ~130 vehicles...
results_df = xleash.lasso('%s#%s!::["df"]' % veh_results_excel)
results_df.shape  # (223_722, 116)

# %%
print(columnize(list(results_df.columns), displaywidth=160))
print(results_df[c_vehnum].unique())
print(results_df[c_case].unique())


# %%
def make_case_overrides():
    """
    Return "manual" changes for AccDB cases above the number of vehicles (116).

    The choices in Gearshift AccDB FORM are not included in the `specs`
    (derived from `Notebooks/VehData/calculation_parameter_all.xlsx`)
    but were communicated separately by Heinz and parsed here
    from this excel file::

        Notebooks/VehData/Differences between ACCESS tool versions 16_ and 20_09_2019.xlsx

    and from `case` Matlab input table.
    """
    overrides = {
        117: {"v_cap_max": 55},
        118: {"v_cap_max": 55},
        119: {"v_cap_max": 80},
        120: {"v_cap_max": 100},
        121: {"v_cap_max": 110},
        122: {"f_dsc": 0, "exclude_crawler_gear": True, "b_no_g0_downshift": True},
        123: {"vehicle_class": "class 3b"},
        124: {
            "nmin_drive_up": 1350,
            "nmin_drive_down": 1300,
            "nmin_drive_start_up": 1450,  # Matlab has this mistakenly 0!
            "nmin_drive_start_down": 1450,
            "t_cold_end": 390,
        },
        125: {
            "nmin_drive_up": 1350,
            "nmin_drive_down": 1350,
            "nmin_drive_start_up": 1400,
            "nmin_drive_start_down": 1350,
            "t_cold_end": 390,
        },
    }

    for case, v_cap in zip(range(117, 122), [55, 55, 80, 100, 110]):
        overrides[case] = {"v_cap": v_cap}

    return overrides


overrides = make_case_overrides()

print("\n".join(f"{k}: {v}" for k, v in sorted(overrides.items())))

# %%
scalar_columns = [
    c_vehnum,
    "Description",
    "case_no",
    "case_no2",
    "vehicle_no",
    "IDclass",
]


def store_results_per_car(
    h5db,
    specs,
    overrides,
    pwots,
    cycles,
    all_cases=None,
    props_group_suffix="prop",
    overrides_group_suffix="override",
    wot_group_suffix="wot",
    cycle_group_suffix="cycle",
    c_vehnum=c_vehnum,
    c_case_id=c_case,
):
    """
    Populate h5db with results collected from a folder full of (`V123.xls`, ...) exchel-files.

    :param cycles:
        if none, also `specs` are not stored!

        vehicles/
            +--v001/
            |   +--props      (series) scalar inputs & outputs generated by AccDB
            |   +--wot        (df) not all vehicles have wot
            |   +--cycle      (df) cycle-run generated by AccDB
            |   +--override   (series) pyalgo must also override these kv-pairs
            +...
    """
    base = vehdb.provenance_info(files=[veh_inputs_excel[0], veh_results_excel[0]])

    if all_cases is None:
        all_cases = set()
        if specs is not None:
            all_cases.update(specs[c_case_id])
        if overrides is not None:
            all_cases.update(overrides.keys())
        if cycles is not None:
            all_cases.update(cycles[c_case_id].unique())
    log.info("Will store %s cases: %s", len(all_cases), all_cases)

    for case in sorted(all_cases):
        vehnum = cycles is not None and int(
            cycles.loc[cycles[c_case_id] == case, c_vehnum].iloc[0]
        )
        log.info(f"+++ Case: %s, Veh: %s (out of %s)...", case, vehnum, len(all_cases))

        ## Store WOT
        #
        if pwots is not None:
            pwot = pwots.loc[pwots[c_engno] == vehnum, :]
            assert pwot.size, (case, vehnum)
            pwot, SM = extract_SM_from_pwot(pwot)
            assert SM and pwot.size, (case, vehnum, SM, pwot)
            pwot_node = vehdb.vehnode(vehnum, wot_group_suffix)
            if not skip_h5_write:
                h5db.put(pwot_node, pwot)
                vehdb.provenir_h5node(
                    h5db,
                    pwot_node,
                    title="Full-load-curve of the test-car, as delivered by Heinz on 13 May 2019",
                    files=[wots_excel[0]],
                    base=base,
                )

        if specs is not None and cycles is not None:
            cyc = cycles.loc[cycles[c_case_id] == case].set_index("tim")
            try:
                cyc, oprops = vehdb.drop_scalar_columns(cyc, scalar_columns)
            except Exception:
                display(case, vehdb.grid(cyc, fitcols=False))
                raise

            ## Store INP/OUT props
            #
            props = specs.loc[specs[c_case_id] == vehnum, :].squeeze()
            assert isinstance(props, pd.Series), props
            props.update(pd.Series(oprops))
            props[c_SM] = SM
            props_group = vehdb.vehnode(case, props_group_suffix)
            if not skip_h5_write:
                h5db.put(props_group, pd.Series(props))
                vehdb.provenir_h5node(
                    h5db,
                    props_group,
                    title="Input specs & scalar results produced by AccDB",
                    base=base,
                )

            ## Store CYCLE
            #
            cycle_group = vehdb.vehnode(case, cycle_group_suffix)
            if not skip_h5_write:
                h5db.put(cycle_group, cyc)
                vehdb.provenir_h5node(
                    h5db, cycle_group, title="Cycle-run produced by AccDB", base=base
                )

        ## Store OVERRIDES
        #
        if overrides is not None and case in overrides:
            overrides_group = vehdb.vehnode(case, overrides_group_suffix)
            if not skip_h5_write:
                h5db.put(overrides_group, pd.Series(overrides[case]))
                vehdb.provenir_h5node(
                    h5db,
                    overrides_group,
                    title="Values to override, as specified manually by Heinz",
                    files=[
                        "VehData/Differences between ACCESS tool versions 16_ and 20_09_2019.xlsx"
                    ],
                    base=base,
                )


##skip_h5_write = True
with vehdb.openh5(h5fname, mode="w") as h5db:
    store_results_per_car(h5db, specs, overrides, pwots, results_df)
    # store_results_per_car(h5db, None, overrides, None, None)

# %%
vehdb.print_nodes(h5fname)

# %%
# %%time
## COMPRESS x4 HDF5: 341Mb --> 72Mb in ~15s.
#
# !ls -lh {h5fname}
if not skip_h5_write:
    # !ptrepack  {h5fname}  --complevel=9 --complib=blosc:lz4hc -o {h5fname}.tmp
    # !mv  {h5fname}.tmp {h5fname}
# !ls -lh {h5fname}

# %%
## SAMPLE: extract data for a specific vehicle.
#
caseno = 14
iosr, cyc = vehdb.load_vehicle_nodes(h5fname, caseno, "prop", "cycle")
display(iosr, cyc.columns, vehdb.grid(cyc, fitcols=False))
