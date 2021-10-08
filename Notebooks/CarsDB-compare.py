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
# # Compare results in the DB

# %%
## To autoreload codein python files here.
# %load_ext autoreload
# %autoreload 2

## Auto-format cells to ease diffs.
# %load_ext lab_black

# %%
# %matplotlib ipympl

# %%
from typing import Union, List, Callable, Any, Sequence as Seq
import io, logging, re, sys
from pathlib import Path, PurePosixPath as P


from columnize import columnize
import numpy as np
import pandas as pd
from pandas import HDFStore
from pandas.core.generic import NDFrame
from matplotlib import pyplot as plt
import qgrid
import wltp
from wltp import io as wio, cycler
from wltp.experiment import Experiment

## Add tests/ into `sys.path` to import `vehdb` module.
#
proj_dir = str(Path(wltp.__file__).parents[1] / "tests")
if proj_dir not in sys.path:
    sys.path.insert(0, proj_dir)

import vehdb

idx = pd.IndexSlice
log = logging.getLogger("CarsDB-compare.ipynb")
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

# %%
vehdb.print_nodes(inp_h5fname)
vehdb.print_nodes(out_h5fname)

# %%
from wltp.invariants import vround, nround1


def load_accdb_and_python_datasets(veh_nums=None):
    p1, c1 = vehdb.merge_db_vehicle_subgroups(
        inp_h5fname, "prop", "cycle", veh_nums=veh_nums
    )
    p2, c2 = vehdb.merge_db_vehicle_subgroups(
        out_h5fname, "oprop", "cycle", veh_nums=veh_nums
    )

    ## Originally fetched as 2-levels (veh, item) MultiIndex Series.
    p1 = p1.unstack()
    p2 = p2.unstack()

    ## By the spec, V rounded to 2-digits,
    #  But exporting MSAccess --> Excel outputs garbage decimals!
    #
    v_cols = "v v_orig v_cap v_downscale".split()
    c1[v_cols] = vround(c1[v_cols])

    ## accdb does not offer `n_max`.(?)
    p1["n_max"] = nround1(p1["n_max1 n_max2 n_max3".split()].max(axis=1))

    return p1, c1, p2, c2


p1, c1, p2, c2 = load_accdb_and_python_datasets()

# %%
## EXPORT RESULTS to upload them for the GS-group when releasing.
#
# p2.drop('v116', axis=0).to_excel('pyalgo-props-124cases-1.0.0.dev12.xlsx')
# c2.drop('v116', axis=0).to_excel('pyalgo-cycles-124cases-1.0.0.dev12.xlsx')

# %%
# Available PROPs
print(columnize(list(p1.columns), displaywidth=160))
print(columnize(list(p2.columns), displaywidth=160))

# %%
display(
    vehdb.grid(p1, fitcols=False),
    vehdb.grid(p2, fitcols=False),
    # vehdb.grid(c1, fitcols=0),
)

# %%
sr_cmpr = vehdb.Comparator(lambda d, c: d[:, c], no_styling=True)
dataset_names = "accdb Python".split()  # Must sort with "diff" column.

# %%
## Report PROP differences
#
#     ACCDB,  PYALGO
equivalent_columns = [
    ("Description", None),
    ("test_mass", None),
    ("kerb_mass", None),
    ("vehicle_class", "wltc_class"),
    # ("pmr_km", "pmr"),
    ("f_dsc_req", "f_dsc"),
    ("v_max", "v_max"),
    ("n_max1", "n95_high"),
    # ("???", "is_n_lim_vmax")
]

cdf = sr_cmpr.compare((p1.stack(), p2.stack()), equivalent_columns, dataset_names)
## Workaround qgrid's hate for hierarchical-columns:
#  https://github.com/quantopian/qgrid/issues/18#issuecomment-149321165
cdf.columns = [" ".join(col).strip() for col in cdf.columns.values]

display(vehdb.grid(cdf, fitcols=False, cwidth=100))
# with pd.option_context('max_rows', 130):
#     display(cdf)

# %%
# Available CYCLE columns
print(columnize(list(c1.columns), displaywidth=160))
print(columnize(list(c2.columns), displaywidth=160))

# %%
cmpr = vehdb.Comparator(lambda d, c: d.loc[idx[:, c]])

# %%
## Report CYCLE-MEAN differences
#
# # Vehicles with DOWNSCALE discrepancies
# veh_nums = [7, 19, 20, 33, 35, 43, 44, 56, 59, 66]
# veh_nums += [82, 88, 91, 99, 100, 101, 112, 113, 114]
# # UNCOMMENT next line to FETCH new vehicles.
p1, c1, p2, c2 = load_accdb_and_python_datasets()
equivalent_series = [
    ("v_orig", "V_cycle"),
    ("v_downscale", "v_target"),
    # ("a", "a_target"),
    ("P_tot_set", "p_req"),
    # ("P_max", "p_available"),
    ("g_max", "g_max0"),
    ("g_min", "g_min"),
    # ("gear", "gears"),
    # ("nc", "n"),
]

c2.columns = wio.flatten_columns(c2.columns)

cols1, cols2 = zip(*equivalent_series)
cols1, cols2 = list(cols1), list(cols2)
## Concat props to col-aggregates & convert prop-cols to numerics
cc1 = pd.concat((p1.infer_objects(), c1[cols1].abs().mean(level=0)), axis=1)
cc2 = pd.concat((p2.infer_objects(), c2[cols2].abs().mean(level=0)), axis=1)

equivalent_props = [
    ("Description", None),
    ("vehicle_class", "wltc_class"),
    ("pmr_km", None),
    ("no_of_gears", None),
    ("f_dsc_req", "f_dsc"),
    ("v_max", "v_max"),
    ("n_vmax", "n_vmax"),
    ("gear_v_max", "g_vmax"),
    ("n_max1", "n_max1"),
    ("n_max2", "n_max2"),
    ("n_max3", "n_max3"),
    ("n_max", "n_max"),
]
display(
    cmpr.compare(
        (cc1, cc2), equivalent_props + equivalent_series, dataset_names, describe=True
    )
)

# %%
## Repeat, to compare while coding.
# display(cmpr.compare((cc1, cc2), equivalent_props + equivalent_series, dataset_names, describe=True))

# %% [markdown]
# AccDB vehicles: 42, 46, 52, 53 & 90 have broken `v_max`, 48 has broken `wot(ASM)`.

# %%
known_bads = set(wio.veh_names([42, 46, 48, 52, 53, 90]))
display(
    cmpr.compare(
        (cc1, cc2), equivalent_props + equivalent_series, dataset_names
    ).set_properties(subset=(known_bads, idx[:]), color="red")
)

# %%
## Repeat, to compare while coding.
# display(cmpr.compare((cc1, cc2), equivalent_props + equivalent_series, dataset_names).set_properties(subset=(known_bads, idx[:]), color='red'))

# %% [markdown]
# ## Compare a vehicle from AccDB <-->PyAlgo *interactively*
# **TODO:** collect and hide all this comparison GUI code below into a python module.

# %%
case_loaded = [None, None]


def _load_interactive_case(
    case_name,
    # increase vertical seperation between flags (but do not exceed max(V))
    flag_mul=2,
):
    accdb_cycle = c1.loc[case_name].copy()
    accdb_gears = [c for c in accdb_cycle.columns if c.startswith("Ind_g")]

    cycle = c2.loc[case_name].dropna(how="all", axis=1).copy()

    ## Scale each flag into a different value, to plot separately, and
    #  to plot in the same axis as V
    #  (bc when plotting flags in `secondary_y`, grid is not working)
    #

    all_flags = [c for c in cycle.columns if c.startswith("ok_")]
    ok_flags = [c for c in all_flags if not c.startswith("ok_gear/")]
    flag_count = len(ok_flags)
    ok_flags = cycle.loc[:, ok_flags].copy()

    ok_gears = [c for c in all_flags if c.startswith("ok_gear/")]
    gear_count = len(ok_gears)
    ok_gears = cycle.loc[:, ok_gears]

    ok_flags[ok_flags < 0] = np.NAN  # Restore NANFLAG --> NAN
    ok_flags = ok_flags * (np.arange(flag_count) + 1) * flag_mul
    ok_gears = ok_gears * (np.arange(gear_count) + flag_count + 1) * flag_mul

    cycle.columns = wio.inflate_columns(cycle.columns)
    ok_flags.columns = wio.inflate_columns(ok_flags.columns)
    ok_gears.columns = wio.inflate_columns(ok_gears.columns)

    return cycle, ok_flags, ok_gears, accdb_cycle, accdb_gears, p1.loc[case_name]


def load_interactive_case(
    case_name,
    # increase vertical seperation between flags (but do not exceed max(V))
    flag_mul=2,
):
    if case_loaded[0] == case_name:
        cycle_data = case_loaded[1]
    else:
        cycle_data = _load_interactive_case(case_name)
        case_loaded[0] = case_name
        case_loaded[1] = cycle_data
    return cycle_data


# cycle, ok_flags, ok_gears, accdb_cycle, accdb_gears, accdb_props = load_interactive_case('v001')
# ok_flags.columns, ok_gears.columns

# %%
def decide_signal_axis(colnames):
    def is_velocity(col):
        return is_velocity(col[0]) if isinstance(col, tuple) else col.startswith("v_")

    l1 = [i for i in colnames if is_velocity(i)]
    l2 = [i for i in colnames if not is_velocity(i)]
    return l1, l2


def define_schemes():
    """Predfined case/pan/zooms of the compraison diagram below."""
    return [
        ## (label, caseno, zoom, pan, *other-UNUSED)
        ("dive(t=764): 1->2 gear too early", "v001", 45.0, 30.40),
        ("dive(t=903): 1st gear not reached", "v001", 45.0, 36.4),
        ("lowPower(t=724)", "v001", 43.0, 69.6),
        ("Py:LowP AccDB:DnShift(t=1571-8)", "v019", 69, 63.4),
        ("p_max from lower g(t=1571-8)", "v020", 69, 63.4),
        ("sameCar?", "v023", 1, 0),
        ("noPowerDives(t=1540-80)", "v024", 26, 63.60),
        ("noPowerDive(t=1574)", "v024", 26, 66.4),
        ("noPowerDive(t=1574)", "v025", 69, 63.4),
        (
            "decelToStop(t=1591)",
            "v025",
            69,
            72.0,
            "AccDB not respecting n_min=0.9 x n_idle (Annex 2-3.k.3)",
        ),
        ("lowPowerDive", "v033", 5, 72),
        ("low -1 gears?", "v035", 65, 63, "Diffs in gears above 2"),
        ("noPowerDive(t=1574)", "v024", 26, 66.4),
        ("g5Ok?(1542)", "v075", 55, 62.4, "Vehicle has too many insufficient powers"),
        ("lowP, lowG betterPAvail(t=1574)", "v087", 65, 63.40),
        ("lowPower(t=1574)", "v088", 65, 63.40),
        ("lowPower", "v101", 1, 0),
        ("lowPower", "v111", 1, 0),
        ("extention", "v117", 13, 72),
        ("extention", "v118", 13, 72),
        ("extention", "v119", 13, 72),
        ("extention", "v120", 13, 72),
        ("extention", "v121", 13, 72),
        ("lowPower", "v124", 1, 0),
        ("lowPower", "v125", 1, 0),
    ]


def grid(df):
    """Display a dynamic grid if given `df` too long. """
    display(vehdb.grid(df, fitcols=len(df.shape) < 2 or df.shape[1] < 12))


def merge_pyalgo_accdb(pyalgo, accdb):
    pyalgo = pyalgo.copy()
    pyalgo.columns = wio.flatten_columns(pyalgo.columns)
    merged = pd.concat((pyalgo, accdb), axis=1, keys=("pyalgo", "accdb"))
    merged.columns = wio.flatten_columns(merged.columns)

    return merged


def display_diff_gears(pyalgo, accdb, props):
    merged = merge_pyalgo_accdb(pyalgo, accdb)
    diffgears_idx = merged["pyalgo/g_max0"] != merged["accdb/g_max"]
    display(merged.loc[diffgears_idx, ["pyalgo/g_max0", "accdb/g_max"]])


def display_diff_cycle(pyalgo, accdb, props):
    merged = merge_pyalgo_accdb(pyalgo, accdb)
    diffgears_idx = merged["pyalgo/g_max0"] != merged["accdb/g_max"]
    grid(merged[diffgears_idx])


def display_pyalgo(pyalgo, accdb, props):
    pyalgo.columns = wio.flatten_columns(pyalgo.columns)
    grid(pyalgo.drop("t", axis=1))


def display_pyalgo_flags(pyalgo, accdb, props):
    flags = pyalgo.select_dtypes("int8").copy()
    flags.columns = wio.flatten_columns(flags.columns)
    pyalgo = pyalgo[["p_req", "p_avail"]].copy()
    pyalgo.columns = wio.flatten_columns(pyalgo.columns)
    grid(pd.concat((pyalgo, flags), axis=1))


def display_accdb_cycle(pyalgo, accdb, props):
    grid(accdb)


def display_accdb_props(pyalgo, accdb, props):
    grid(props)


## What to display in the Tabs beneath the plot
#
out_specs = [
    (display_diff_gears, "DiffGears"),
    (display_diff_cycle, "DiffGear cycles"),
    (display_pyalgo_flags, "PyAlgo flags"),
    (display_pyalgo, "PyAlgo"),
    (display_accdb_cycle, "AccDb cycle"),
    (display_accdb_props, "AccDb props"),
]

# %%
## TODO: CLASSify code in these cells.
from ipywidgets import (
    interact,
    interactive,
    interactive_output,
    fixed,
    interact_manual,
    widgets,
)
from IPython.display import clear_output


init_zoom = 55.0
init_pan = 30.40
max_zoom = 72.0

Case = widgets.SelectionSlider(options=list(c2.index.levels[0]), description="Case")
Gear = widgets.SelectionSlider(options=["g1"], description="Gear")
Zoom = widgets.FloatSlider(
    init_zoom, min=1.0, max=max_zoom, step=4.0, description="Zoom"
)
Pan = widgets.FloatSlider(init_pan, min=0.0, max=max_zoom, step=0.4, description="Pan")
IsPyAlgoGears = widgets.Checkbox(False, description="Plot PyAlgo Gear flags?")
IsAccdbGears = widgets.Checkbox(False, description="Plot AccDB Gear flags?")
PyAlgoSignals = widgets.SelectMultiple(rows=7, description="Pyalgo signals")
AccDBSignals = widgets.SelectMultiple(rows=7, description="AccDB signals")
AxisScenes = widgets.Select(options=[], description="Scenes")
AxisScenes.layout.width = "auto"
Desc = widgets.Textarea(disabled=True)  # DEFUNCT
Desc.layout.width = "24"
Desc.layout.height = "7em"
Selections = widgets.HBox(
    [
        Case,
        Zoom,
        Pan,
        AxisScenes,
        IsPyAlgoGears,
        PyAlgoSignals,
        IsAccdbGears,
        AccDBSignals,
        Gear,
    ]
)
Selections.layout.width = "95%"
Selections.layout.flex_flow = "row wrap"
# Selections.layout.justify_content = "flex-start"


#: Updated by *interact* function, for display functions to read them
#: pyalgo, accdb, accdb_props
results = [None, None, None]

Tab = widgets.Tab()


def refresh_tabs():
    global out_specs

    AxisScenes.options = [
        (f"{caseno}: {label}", (caseno, zoom, pan, *other))
        for label, caseno, zoom, pan, *other in define_schemes()
    ]
    needs_retabbing = False
    if out_specs and len(out_specs[0]) < 3:
        out_specs = [(widgets.Output(), *i) for i in out_specs]
        needs_retabbing = True
    if needs_retabbing or not Tab.children:
        Tab.children = [out for out, _, _ in out_specs]
        for i, (_, _, title) in enumerate(out_specs):
            Tab.set_title(i, title)

    return out_specs


refresh_tabs()


def update_tab_contents(change):
    if change.new is None:
        return
    out, func, _ = out_specs[change.new]
    has_content = bool(out.get_state()["outputs"])
    if not has_content:
        with out:
            func(*(i.copy() for i in results))


Tab.observe(update_tab_contents, names="selected_index")


Gui = widgets.VBox([Selections, Tab])


def update_valid_signals(change):
    case_name = Case.value
    pyalgo, _, ok_gears, accdb, _, _ = load_interactive_case(case_name)

    Gear.options = ok_gears.columns.levels[1]

    pyalgo_columns = [
        ("/".join(cc for cc in c if cc), c)
        for c in pyalgo.select_dtypes(exclude=[np.object])
        if not c[0].startswith("ok_gear") and not c[0] == "t"
    ]
    PyAlgoSignals.options = pyalgo_columns

    accdb_columns = [
        c for c in accdb.select_dtypes(exclude=[np.object]) if not c.startswith("Ind_g")
    ]
    AccDBSignals.options = accdb_columns


Case.observe(update_valid_signals, names="value")
update_valid_signals(None)


def apply_axis_scene(change):
    Case.value, Zoom.value, Pan.value, *other = AxisScenes.value
    Desc.value = other[0] if other else ""


AxisScenes.observe(apply_axis_scene, names="value")


def _count_series_diffs(a, b):
    na, nb = len(a), len(b)
    if na != nb:
        na = min(na, nb)
        return (a.iloc[:na] != b.iloc[:na]).sum() + (nb - na)
    return (a != b).sum()


def _distribute_signals_in_axes(columns, df):
    cols1, cols2 = decide_signal_axis(columns)
    df1 = df.loc[:, cols1]
    df2 = df.loc[:, cols2]
    return df1, df2


def recreate_fig():
    """
     Recreate the same figure-number, or else they leak.

    Hack, or else, shown double figure the 1st time this cell runs,
    or figure hidden, or stability/performance problems.
    """
    for i in range(3):
        fig_nums = plt.get_fignums()
        fig = plt.figure(
            num='Compare AccDB <--> PyAlgo "Initial Gear"', figsize=(10, 8)
        )
        if fig.number in set(fig_nums):
            fig.clear()
            plt.close(fig)
        else:
            return fig
    else:
        raise Exception(f"Exhausted new-fig tries({i}) with figs({plt.get_fignums()})")


fig = recreate_fig()


def plot_gear_flags(
    case,
    gear,
    zoom,
    pan,
    pyalgo_signals,
    accdb_signals,
    is_pyalgo_gears,
    is_accdb_gears,
):
    fig.clear()

    ax = plt.subplot()
    ax2 = ax3 = None

    out_specs = refresh_tabs()

    (
        cycle,
        ok_flags,
        ok_gears,
        accdb_cycle,
        accdb_gears,
        accdb_props,
    ) = load_interactive_case(case)

    clen = max(len(cycle), len(accdb_cycle))
    viewlen = int(clen / zoom)
    offset = int(pan * (clen - viewlen) / max_zoom)
    scale = idx[offset : offset + viewlen]

    diffgears_total = _count_series_diffs(cycle["g_max0"], accdb_cycle["g_max"])

    pyalgo = cycle.loc[scale]
    accdb = accdb_cycle.loc[scale]
    diffgears_view = _count_series_diffs(pyalgo["g_max0"], accdb["g_max"])
    merged = merge_pyalgo_accdb(pyalgo, accdb)

    ## Clean tabs if caseno/pan/zoom have changed.
    #
    if not pyalgo.equals(results[0]):
        Tab.selected_index = None
        for out, _, _ in out_specs:
            with out:
                clear_output()

    results[0] = pyalgo
    results[1] = accdb
    results[2] = accdb_props

    ax.set_title(
        f"Case_no: {case}, # of diff gears, in_view: {diffgears_view}, TOTAL: {diffgears_total}"
    )

    ok_flags = ok_flags.loc[:, idx[:, gear]].iloc[scale]
    ok_gears = ok_gears.loc[scale]

    if not pyalgo["V_cycle"].empty:
        pyalgo["V_cycle"].plot.line(ax=ax, color="0.70", linewidth=4.5)

    if is_pyalgo_gears:
        if not ok_flags.empty:
            ok_flags.plot.line(ax=ax, linewidth=2)
        ok_gears.plot.line(ax=ax, linewidth=3)

    ax2 = merged[["pyalgo/g_max0", "accdb/g_max"]].plot.line(
        ax=ax, linewidth=3, style=["b-", "c:"], secondary_y=True
    )

    if is_accdb_gears:
        accdb_gears = accdb.loc[:, accdb_gears] * (np.arange(len(accdb_gears)) + 1)
        accdb_gears[accdb_gears == 0] = np.NAN
        accdb_gears = accdb_gears.dropna(how="all", axis=1).fillna(0)
        ax2 = accdb_gears.plot.line(
            ax=ax, linewidth=2, linestyle="--", secondary_y=True
        )

    ax3 = ax.twinx()
    show_signals = pyalgo_signals or accdb_signals
    ax3.set_visible(show_signals)
    if show_signals:
        pyalgo1, pyalgo2 = _distribute_signals_in_axes(pyalgo_signals, pyalgo)
        accdb1, accdb2 = _distribute_signals_in_axes(accdb_signals, accdb)

        merged1 = merge_pyalgo_accdb(pyalgo1, accdb1)
        merged2 = merge_pyalgo_accdb(pyalgo2, accdb2)

        if not merged1.empty:
            merged1.astype(np.float64).plot.line(ax=ax, linewidth=2, linestyle="--")
        if not merged2.empty:
            merged2.astype(np.float64).plot.line(ax=ax3, linewidth=2, linestyle=":")
            ax3.legend(loc=4)
    ax.legend(loc=1)
    ax2.legend(loc=3)

    #     if ax2:
    #         ax2.grid(True, axis="both", which="both")
    ax.grid(True, axis="both", which="both")

    # Re-tighten if ax3 has (dis)appeared.
    # Had to use `rect` or axis-title half-hidden the first time fig is created!
    fig.tight_layout(rect=[0, 0, 1, 0.985])


display(Gui)

interactive_output(
    plot_gear_flags,
    {
        "case": Case,
        "gear": Gear,
        "zoom": Zoom,
        "pan": Pan,
        "pyalgo_signals": PyAlgoSignals,
        "accdb_signals": AccDBSignals,
        "is_pyalgo_gears": IsPyAlgoGears,
        "is_accdb_gears": IsAccdbGears,
    },
)

# %% [markdown]
# # Museum

# %%
## Is clutch-undefined only used for gear 1?  NO< also for g2.
display(c1.loc[c1.clutch == "undefined", "gear"].value_counts())
# display(c1.loc[c1.clutch=='undefined', ['v', 'a', 'g_max', 'clutch']])

# %%
# c2 = c2.loc[c2.index != 'v116']
# p2 = p2.loc[p2.index != 'v116']
# p2.to_excel('pyalgo_props-1.0.0.dev10.xlsx')
# c2.to_excel('pyalgo_cycles-1.0.0.dev10.xlsx')

# %% [markdown]
# ### AccDB not respecting n_min=0.9 x n_idle (Annex 2-3.k.3):

# %%
def is_bad_g2_in_decel_to_stop(accdb, cyc, prop):
    cyc = cyc.reset_index(level=0)
    # bad_rows = (accdb.g_max == 2) & cyc.stopdecel & (cyc['n/g2'] < 0.9 * prop['idling_speed'])
    bad_rows = (accdb.g_max == 2) & (cyc.g_max0 == 1) & cyc.stopdecel
    if bad_rows.any():
        return pd.concat(
            (
                accdb.loc[bad_rows, ["g_max", "n_2"]],
                cyc.loc[bad_rows, ["n/g2", "ok_gear/g1", "ok_gear/g2", "stopdecel"]],
            ),
            axis=1,
        )


for case, cyc in c2.groupby(level=0):
    accdb = c1.loc[case]
    prop = p1.loc[case]
    res = is_bad_g2_in_decel_to_stop(accdb, cyc, prop)
    if res is not None:
        display(
            prop[["idling_speed", "vehicle_class"]],
            f"0.9 x n_idle: {prop['idling_speed'] * 0.9}",
        )
        if isinstance(res, tuple):
            display(*res)
        else:
            display(res)


# %% [markdown]
# ### Insufficient power where more than one gears are N-valid:

# %%
def is_more_low_powered_gears(cyc):
    cyc2 = cyc.copy()
    cyc2.columns = wio.inflate_columns(cyc2.columns)
    c22 = cyc2.iloc[1571:1579][["ok_p", "ok_max_n"]].dropna(axis=1, how="all")
    try:
        ## is there any row with all-low-p AND 2-or-more n-max-ok?
        bad_rows = (~c22["ok_p"].replace(-1, 0).astype("bool")).all(axis=1) & (
            c22["ok_max_n"].replace(-1, 0).astype("bool").sum(axis=1) > 1
        )
        if bad_rows.any():
            c22.columns = wio.flatten_columns(c22.columns)
            return (
                list(bad_rows[bad_rows].index),
                pd.concat(
                    (c22, cyc.iloc[1571:1579].loc[:, ["g_min", "g_max"]]), axis=1
                ),
            )
    except Exception as ex:
        print(ex)


for case, cyc in c2.groupby(level=0):
    res = is_more_low_powered_gears(cyc)
    if res is not None:
        display(p2.loc[case, ["wltc_class", "g_vmax"]])
        if isinstance(res, tuple):
            display(*res)
        else:
            display(res)
