#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2013-2020 European Commission (JRC);
# Licensed under the EUPL (the 'Licence');
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at: http://ec.europa.eu/idabc/eupl
"""
Utils for manipulating h5db with accdb & pyalgo cases.

used by many tests & notebooks.

* load_vehicle_accdb(vehnum=1): load inps & outs for AccDB
* load_vehicle_pyalgo(vehnum=1): load outs for AccDB
"""
import io
import json
import logging
import os
import platform
import re
import shutil
import subprocess as sbp
import sys
import time
from copy import deepcopy
from datetime import datetime
from pathlib import Path, PurePosixPath
from typing import Any, Callable, Dict, List, NamedTuple
from typing import Sequence as Seq
from typing import Tuple, Union

import numpy as np
import pandas as pd
from pandas import HDFStore
from pandas import IndexSlice as idx
from pandas.api.types import is_numeric_dtype
from pandas.core.generic import NDFrame

from pandalone.mappings import Pstep
from wltp import datamodel
from wltp import io as wio
from wltp import utils

log = logging.getLogger(__name__)
EPS = sys.float_info.epsilon


H5DB = Union[str, Path, HDFStore]

notebooks_dir = Path(__file__).parent / ".." / "Notebooks"
AccDbPath = notebooks_dir / "VehData" / "WltpGS-msaccess.h5"
PyAlgoPath = notebooks_dir / "VehData" / "WltpGS-pyalgo.h5"


def oneliner(s) -> str:
    """Collapse any whitespace in stringified `s` into a single space. """
    return re.sub(r"[\n ]+", " ", str(s).strip())


def _human_time(unixtime: int = None) -> str:
    if unixtime is None:
        tm = datetime.now()
    else:
        tm = datetime.utcfromtimestamp(unixtime)
    return tm.strftime("%Y-%m-%d %H:%M:%S")


def _file_hashed(fpath, algo="md5") -> Tuple[str, str]:
    import hashlib
    import io

    digester = hashlib.new(algo)
    with open(fpath, "rb") as f:
        for b in iter(lambda: f.read(io.DEFAULT_BUFFER_SIZE), b""):
            digester.update(b)
    return algo, digester.hexdigest()


# file_hashed(xl_fname)


def _cmd(*args):
    return sbp.check_output(
        args, universal_newlines=True, shell=sys.platform == "win32"
    )


def _git_describe(basedir="."):
    try:
        return _cmd("git", "-C", basedir, "describe", "--always").strip()
    except Exception as ex:
        log.warning("Cannot git-describe due to: %s", ex)
        return "Cannot git-describe due to: %s" % ex


def _python_describe():
    info = {"path": shutil.which("python")}
    conda_env = os.environ.get("CONDA_DEFAULT_ENV")
    log.info("Asking conda-env(%s) or `pip`, might take some time...", conda_env)
    if conda_env:
        info["type"] = "conda"

        try:
            info["env"] = utils.yaml_loads(
                _cmd("conda", "env", "export", "-n", conda_env)
            )
        except Exception as ex:
            log.warning("Cannot conda-env-export due to: %s", ex)
            info["env"] = "Cannot conda-env-export due to: %s" % ex
    else:
        try:
            info["env"] = _cmd(*"pip list --format freeze".split()).strip().split("\n")
        except Exception as ex:
            log.warning("Cannot pip-list due to: %s", ex)
            info["env"] = "Cannot pip-list due to: %s" % ex

    return info


def _provenir_fpath(fpath, algos=("md5", "sha256")) -> Dict[str, str]:
    s = {"path": str(str(Path(fpath).absolute()))}

    fpath = Path(fpath)
    if fpath.exists():
        s["hexsums"] = dict(_file_hashed(fpath, algo) for algo in algos)
        s["ctime"] = _human_time(fpath.stat().st_ctime)
    else:
        log.warning("Provenance file %r does not exist!", fpath)

    return s


#: Lazily instanciated
_root_provenance = None


def provenance_info(*, files=(), repos=(), base=None) -> Dict[str, str]:
    """Build a provenance record, examining environment if no `base` given.

    :param base:
        if given, reused (cloned first), and any fpaths & git-repos appended in it.
    """
    global _root_provenance

    if _root_provenance is None:
        _root_provenance = {
            "uname": dict(platform.uname()._asdict()),
            "python": _python_describe(),
        }
    info = deepcopy(_root_provenance)

    if base:
        info.update(deepcopy(base))

    info["ctime"] = _human_time()

    fps = info.get("files")
    if not isinstance(fps, list):
        fps = info["files"] = []
    fps.extend(_provenir_fpath(f) for f in files)

    gtr = info.get("repos")
    if not isinstance(gtr, list):
        gtr = info["repos"] = []

    if not repos and "." not in gtr:
        repos = ["."]

    log.debug("Git-describing (%s)...", repos)
    gtr.extend(
        {"path": str(Path(g).absolute()), "type": "git", "version": _git_describe(g)}
        for g in repos
    )

    return info


# prov_info = nbu.provenance_info(files=[h5fname])
# prov_info = nbu.provenance_info(files=['foo'], base=prov_info)
# prov_info = nbu.provenance_info(files=['ggg'], repos=['../wltp.git'], base=prov_info)
# print(nbu.utils.yaml_dumps(prov_info))


#########################
## HDF5


def openh5(h5: H5DB, mode="r"):
    """Open h5-fpath or reuse existing h5db instance."""

    h5db = None

    if isinstance(h5, HDFStore):
        if h5.is_open:
            h5db = h5
        else:
            h5 = h5.filename

    if h5db is None:
        h5db = HDFStore(
            h5,
            mode=mode,
            encoding="utf-8",
            # Not the strongest one, *repack* it before git-commit.
            complevel=6,
            complib="blosc:blosclz",
        )

    return h5db


def do_h5(h5: H5DB, func: callable, *args, **kw):
    """Open & close if `h5` is fname (string), do nothing if an opened db"""
    if isinstance(h5, HDFStore) and h5.is_open:
        out = func(h5, *args, **kw)
    else:
        with openh5(h5, mode=kw.get("mode", "r")) as h5db:
            out = func(h5db, *args, **kw)

    return out


def print_nodes(h5: H5DB, displaywidth=160):
    from columnize import columnize

    nodes = do_h5(h5, lambda h5db: sorted(h5db.keys()))

    print(columnize(nodes, displaywidth=displaywidth))


def provenir_h5node(h5: H5DB, node, *, title=None, files=(), repos=(), base=None):
    """Add provenance-infos to some existing H5 node.

    For its API, see :func:`provenance_info`.
    """

    def func(h5db):
        h5file = h5db._handle
        if title:
            h5file.set_node_attr(node, "TITLE", title)
        prov_info = provenance_info(files=files, repos=repos, base=base)

        provenance = utils.yaml_dumps(prov_info)
        h5file.set_node_attr(node, "provenance", provenance)

    return do_h5(h5, func)


def provenance_h5node(h5: H5DB, node):
    """Get provenance-infos from some existing H5 node."""

    def func(h5db):
        h5file = h5db._handle
        title = h5file.get_node_attr(node, "TITLE")
        provenance = h5file.get_node_attr(node, "provenance")

        return f"TITLE: {title}\n{provenance}"

    return do_h5(h5, func)


def collect_nodes(h5: H5DB, predicate: Callable[[str], Any], start_in="/") -> List[str]:
    """
    feed all groups into predicate and collect its truthy output
    """

    def func(h5db):
        out = [predicate(g._v_pathname) for g in h5db._handle.walk_groups(start_in)]
        return sorted(set(i for i in out if bool(i)))

    return do_h5(h5, func)


#########################
## Pandas etc


def get_scalar_column(df, column):
    """
    Extract the single scalar value if column contains it.
    """
    col = df[column]
    val = col.iloc[0]

    assert col.isnull().all() or (col == val).all(), (column, val, df[col != val, :])

    return val


def drop_scalar_columns(df, scalar_columns) -> Tuple[pd.DataFrame, dict]:
    values = [get_scalar_column(df, c) for c in scalar_columns]
    scalars = dict(zip(scalar_columns, values))
    return df.drop(scalar_columns, axis=1), scalars


class Comparator:
    """Pick and concat side-by-side differently-named columns from multiple dataframe."""

    def __init__(
        self,
        col_accessor: Callable[[NDFrame, str], NDFrame],
        *,
        no_diff_percent=False,
        diff_colname="diff",
        diff_bar_kw={"align": "mid", "color": ["#d65f5f", "#5fba7d"]},
        no_styling=False,
    ):
        """
        :param col_accessor:
            how to pick a column from an NDFrame
        :param no_diff_percent:
            if this is falsy, the result dataframe contains an extra *diff percent* column
            if the respective equivalent-columns are numerics.
        :param diff_colname`:
            how to name the extra *diff* column (does nothing for when not generated)
        :param diff_bar_kw:
            if given, apply styling bars at the `diff[%]` columns,
            with these as extra styling
            (see https://pandas.pydata.org/pandas-docs/stable/user_guide/style.html#Bar-charts)
        """
        for _k, _v in locals().items():
            if not _k.startswith("_") or _k == "self":
                vars(self)[_k] = _v

    def _pick_n_diff_columns(
        self, datasets: Seq[NDFrame], col_names: Seq[str], dataset_names: Seq[str]
    ) -> NDFrame:
        """
        Pick and concatenate the respective `col_names` from each dataframe in `datasets`,

        and (optionally) diff against the 1st dataset.

        :param datasets:
            a list of N x dataframes.
            Each one must contain the respective column from `col_names`,
            when access by ``self.col_accessor( df[i], col_name[i] )`` ∀ i ∈ [0, N).
        :param col_names:
            a list o N x column-names; Nones omit the respective dataset
        :return:
        """
        picked_cols = [
            self.col_accessor(d, c) for d, c in zip(datasets, col_names) if c
        ]
        dataset_names = list(dataset_names)

        if not self.no_diff_percent and all(is_numeric_dtype(d) for d in picked_cols):
            d0, *drest = picked_cols
            picked_cols = [d0]
            for d in drest:
                picked_cols.extend((d, d0 - d))

            dataset_names = dataset_names + [self.diff_colname]

        return pd.concat(picked_cols, axis=1, keys=dataset_names, sort=True)

    def _col_0(self, equiv_colnames):
        return next(iter(zip(*equiv_colnames)))

    def _concat_datasets(
        self,
        datasets,
        equiv_colnames: Seq[Seq[str]],
        dataset_names: Seq[str],
        keys: Seq[str],
    ):
        return pd.concat(
            (
                self._pick_n_diff_columns(datasets, cols, dataset_names)
                for cols in equiv_colnames
            ),
            axis=1,
            keys=keys,
        )

    def compare(
        self,
        datasets: Seq,
        equiv_colnames: Seq[Seq[str]],
        dataset_names: Seq[str],
        *,
        no_styling=None,
        describe=False,
    ):
        """
        List side-by-side same-kind columns (with different names) from many datasets,

        optionally diffing them against the 1st dataset.

        :param datasets:
            a list of N x NDFrames, each one containing the respective columns in `equiv_colnames`.
        :param equiv_colnames:
            a matrix of M x N column-names, like:

                [("p_downscale", "f_dsc"), ("cycle", "wltc_class"), ...]

            All columns in the N dimension must exist in the respective dataframe in `datasets` list.
            The 1st columns in the M-dimension are used a axis-1, level-0 labels
            on the concatanated NDFrame.
        :param dataset_names:
            used as hierarchical labels to distinguish from which dataset each column comes from
        """
        if no_styling is None:
            no_styling = self.no_styling

        col_0 = self._col_0(equiv_colnames)
        df = self._concat_datasets(datasets, equiv_colnames, dataset_names, keys=col_0)
        if describe:
            nonzeros = (df != 0).sum().to_frame().T
            nonzeros.index = ["nonzero"]
            ## Aggregate on absolute-diffs.
            df.loc[:, idx[:, self.diff_colname]] = df.loc[
                :, idx[:, self.diff_colname]
            ].abs()
            df = pd.concat((df.describe(), nonzeros), axis=0)
            df = df.drop("count", axis=0)

            if self.diff_bar_kw and not no_styling:
                df = self._styled_with_diff_bars(df, col_0)
        else:
            if self.diff_bar_kw and not no_styling:
                df = self._styled_with_diff_bars(df, col_0)
        return df

    def _styled_with_diff_bars(self, df, col_level_0):
        style = df.style
        for c in col_level_0:
            if "nonzero" in df.index:
                diff_idx = idx[:"max", idx[c, self.diff_colname]]
            else:
                diff_idx = idx[:, idx[c, self.diff_colname]]
            try:
                df.loc[diff_idx]
            except Exception:
                "Ok, `diff` column missing"
            else:
                style = style.bar(subset=diff_idx, **self.diff_bar_kw)

        return style


## Fix too-small columns when too many,
# from: https://github.com/quantopian/qgrid/issues/171#issuecomment-365489567
def grid(df, fitcols=True, cwidth=None):
    import qgrid

    grid_opts = {"forceFitColumns": fitcols}
    if not fitcols and cwidth is None:
        cwidth = 86
    if cwidth is not None:
        grid_opts["defaultColumnWidth"] = cwidth

    return qgrid.show_grid(df, grid_options=grid_opts)


#########################
## Vehicle-DB-specific

vehs_root = PurePosixPath("/vehicles")


def vehnode(vehnum=None, *suffix):
    p = vehs_root
    if vehnum is not None:
        p = vehs_root / (wio.veh_name(vehnum))
    return str(p.joinpath(*suffix))


# assert vehnode(13) ==  '/vehicles/v013'
# assert vehnode(3, 'props') ==  '/vehicles/v003/props'
# assert vehnode(None, 'props') ==  '/vehicles/props'
# assert vehnode() ==  '/vehicles'

# TODO: rename load_vehicle_nodes --> load_h5_nodes()
# TODO: rename load_vehicle_XXX move make `vehnum` 1st compulsory argument.
def load_vehicle_nodes(h5: H5DB, vehnum, *subnodes) -> list:
    "return vehicle's groups listed in `subnodes`"

    def func(h5db):
        res = [h5db.get(vehnode(vehnum, sn)) for sn in subnodes]
        return res[0] if len(subnodes) == 1 else res

    res = do_h5(h5, func)
    return res


# props, wot = load_vehicle_nodes(h5fname, vehnum, "prop", "wot")


class CaseData(NamedTuple):
    """Typical case data stored in vehicle DBs. """

    props: pd.Series
    df: pd.DataFrame
    items: list


def load_vehicle_accdb(h5: H5DB = AccDbPath, vehnum=None) -> CaseData:
    """return the typical inputs data  (not outs) for a vehicle in accdc: props, wot, n2vs"""

    def func(h5db):
        props = load_vehicle_nodes(h5db, vehnum, "prop")
        wot_vehnum = props["vehicle_no"]
        wot = load_vehicle_nodes(h5db, wot_vehnum, "wot")
        n2vs = load_n2v_gear_ratios(props)
        return CaseData(props, wot, n2vs)

    res = do_h5(h5, func)
    return res


def load_vehicle_pyalgo(
    h5: H5DB = PyAlgoPath, vehnum=None, nodes=("oprop", "cycle", "wots_vmax")
) -> CaseData:
    """return the typical output data for a vehicle in pyalgo (see `node` defaults). """

    def func(h5db):
        return CaseData(*load_vehicle_nodes(h5db, vehnum, *nodes))

    res = do_h5(h5, func)
    return res


def all_vehnums(h5) -> List[int]:  # TODO: rename to all_cases()
    def func(h5db):
        vehnums = [int(g._v_name[1:]) for g in h5db._handle.iter_nodes(vehnode())]
        return sorted(vehnums)

    return do_h5(h5, func)


def load_n2v_gear_ratios(vehicle_iprops: Union[dict, pd.Series]):
    """Reads all valid `ndv_X` values from AccDB input-properties in HD5"""
    ng = vehicle_iprops["no_of_gears"]
    return [vehicle_iprops[f"ndv_{g}"] for g in range(1, ng + 1)]


def accdb_renames():
    """
    Renames to use accdb inputs (props, wots) into pyalgo to be used like::

        props.unstack().rename(accdb_prop_renames())
    """
    return {
        "idling_speed": "n_idle",
        "rated_speed": "n_rated",
        "rated_power": "p_rated",
        "kerb_mass": "unladen_mass",
        "vehicle_class": "wltc_class",
        "Pwot": "p",
    }


def mdl_from_accdb(props, wot, n2vs: List[float]) -> dict:
    """
    :param props:
        may have been renamed with :func:`accdb_renames()`
    """
    assert isinstance(n2vs, list)

    mdl: dict = datamodel.get_model_base()
    mdl["f0"] = props.f0
    mdl["f1"] = props.f1
    mdl["f2"] = props.f2
    mdl["unladen_mass"] = props.get("unladen_mass", props.kerb_mass)
    mdl["test_mass"] = props.test_mass
    mdl["p_rated"] = props.get("p_rated", props.rated_power)
    mdl["n_rated"] = props.get("n_rated", props.rated_speed)
    mdl["n_idle"] = props.get("n_idle", props.idling_speed)
    mdl["v_max"] = props.get("", props.v_max)
    # mdl['n_min_drive']=           props.n_min_drive
    # mdl['n_min_drive_set']=       props.n_min_drive_set
    mdl["n_min_drive_up"] = props.n_min_drive_up
    mdl["n_min_drive_down"] = props.n_min_drive_down
    mdl["n_min_drive_up_start"] = props.n_min_drive_start_up  # inversed@acdb!
    mdl["n_min_drive_down_start"] = props.n_min_drive_start_down  # inversed@acdb!
    mdl["t_cold_end"] = props.t_end_start_phase
    mdl["f_safety_margin"] = props.SM

    renames = accdb_renames()
    wot = wot.rename(renames, axis=1)
    wot["n"] = wot.index
    mdl["wot"] = wot

    mdl["n2v_ratios"] = n2vs

    return mdl


def run_pyalgo_on_accdb_vehicle(
    h5,
    vehnum,
    additional_properties=False,
    props_group_suffix="prop",
    pwot_group_suffix="wot",
) -> Tuple[dict, pd.DataFrame, pd.DataFrame]:
    """
    Quick 'n dirty way to invoke python-algo (bc model will change).

    :param h5:
        the `WltpGs-msaccess.h5` file (path or h5db) to read input from
    :return:
        the *out-props* key-values, the *cycle* data-frame,
        and the grid-wots constructed to solve v_max.
    """
    from wltp import io as wio, engine, utils
    from wltp.experiment import Experiment

    props, wot, n2vs = load_vehicle_accdb(h5, vehnum)

    mdl = mdl_from_accdb(props, wot, n2vs)
    datamodel.validate_model(mdl, additional_properties=additional_properties)
    exp = Experiment(mdl, skip_model_validation=True)
    mdl = exp.run()

    ## Keep only *output* key-values, not to burden HDF data-model
    #  (excluding `driveability`, which is a list, and f0,f1,f2, addume were input).
    #
    # oprops = {k: v for k, v in veh if np.isscalar(v)}
    out_mdl = {
        "pmr": mdl["pmr"],
        "n95_low": mdl["n95_low"],
        "n95_high": mdl["n95_high"],
        "v_max": mdl["v_max"],
        "n_vmax": mdl["n_vmax"],
        "g_vmax": mdl["g_vmax"],
        "is_n_lim_vmax": mdl["is_n_lim_vmax"],
        "n_max1": mdl["n_max1"],
        "n_max2": mdl["n_max2"],
        "n_max3": mdl["n_max3"],
        "n_max": mdl["n_max"],
        "wltc_class": mdl["wltc_class"],
        "f_dsc_raw": mdl["f_dsc_raw"],
        "f_dsc": mdl["f_dsc"],
    }

    cycle = mdl["cycle"]

    return out_mdl, cycle, mdl["wots_vmax"]


# oprops, cycle, wots_vmax = nbu.run_pyalgo_on_accdb_vehicle(inp_h5fname, 14)
# display(oprops, cycle, wots_vmax)


def merge_db_vehicle_subgroups(
    h5: H5DB, *vehicle_subgroups: str, veh_nums=None
) -> Union[NDFrame, List[NDFrame]]:
    """
    Merge HDF-subgroup(s) from all vehicles into an Indexed-DataFrame(s)

    :param h5:
        any `WltpGs-*.h5` file (path or h5db) containing `vehicles/v001/{subgroups}` groups
    :param vehicle_subgroups:
        the name of a sub-group in the h5 file (or a list of such names).
        If a list given, returns a list
    :return:
        as many vertically concatenated dataframes as `vehicle_subgroups` given
    """

    def func(h5db):
        veh_nums_ = all_vehnums(h5db) if veh_nums is None else veh_nums
        data_collected = list(
            zip(
                *(
                    tuple(
                        # key: vehnum, value: subgroup-dfs
                        ("v%0.3i" % vehnum, h5db.get(vehnode(vehnum, datag)))
                        for datag in vehicle_subgroups
                    )
                    for vehnum in veh_nums_
                )
            )
        )

        return data_collected

    data_collected = do_h5(h5, func)

    dicts_to_merge = [dict(d) for d in data_collected]
    index_dfs = [
        pd.concat(d.values(), keys=d.keys()).sort_index() for d in dicts_to_merge
    ]

    return index_dfs[0] if len(index_dfs) == 1 else index_dfs


def read_matlab_csv(fpath, **csv_kw):
    """Matlab data-files have spaces columns and are humanly indented. """

    df = pd.read_csv(fpath, sep=" *, *", engine="python", **csv_kw).convert_dtypes()
    return df

def setup_octave():
    """Setup `oct2py` library to execute wltp's MATLAB sources. """
    from oct2py import octave as oc

    # See https://nbviewer.jupyter.org/github/blink1073/oct2py/blob/master/example/octavemagic_extension.ipynb?create=1
    # %load_ext oct2py.ipython

    wltp_mat_sources_path = str(Path("src").absolute())
    mat_path = set(oc.path().split(osp.pathsep))
    if wltp_mat_sources_path not in mat_path:
        oc.addpath(wltp_mat_sources_path)