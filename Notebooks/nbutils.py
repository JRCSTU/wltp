from typing import List, Tuple, Dict, Union, Callable, Any, Sequence as Seq
import io, json, time, platform
from datetime import datetime
from pathlib import Path, PurePosixPath
from copy import deepcopy
import logging
import subprocess as sbp
import os
import qgrid
import shutil
import sys


import pandas as pd
from pandas import HDFStore

from wltp.utils import yaml_loads, yaml_dumps


log = logging.getLogger(__name__)


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


# file_hashed(xlfname)


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
    condaenv = os.environ.get("CONDA_DEFAULT_ENV")
    log.info("Asking conda-env(%s) or `pip`, might take some time...", condaenv)
    if condaenv:
        info["type"] = "conda"

        try:
            info["env"] = yaml_loads(_cmd("conda", "env", "export", "-n", condaenv))
        except Exception as ex:
            log.warning("Cannot conda-env-export due to: %s", ex)
            info["env"] = "Cannot conde-env-export due to: %s" % ex
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
        info.update(base)

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
# prov_info = nbu.provenance_info(files=['sfdsfd'], base=prov_info)
# prov_info = nbu.provenance_info(files=['ggg'], repos=['../wltp.git'], base=prov_info)
# print(nbu.yaml_dumps(prov_info))


#########################
## HDF5


def openh5(h5: Union[str, HDFStore]):
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
            encoding="utf-8",
            # Not the strongest one, *repack* it before git-commit.
            complevel=6,
            complib="blosc:blosclz",
        )

    return h5db


def do_h5(h5: Union[str, HDFStore], func: callable, *args, **kw):
    """Open & close if `h5` is fname (string), do nothing if an opened db"""
    if isinstance(h5, HDFStore) and h5.is_open:
        out = func(h5, *args, **kw)
    else:
        with openh5(h5) as h5db:
            out = func(h5db, *args, **kw)

    return out


def print_nodes(h5: Union[str, HDFStore], displaywidth=160):
    from columnize import columnize

    nodes = do_h5(h5, lambda h5db: sorted(h5db.keys()))

    print(columnize(nodes, displaywidth=displaywidth))


def provenir_h5node(
    h5: Union[str, HDFStore], node, *, title=None, files=(), repos=(), base=None
):
    """Add provenance-infos to some existing H5 node.
    
    For its API, see :func:`provenance_info`. 
    """

    def func(h5db):
        h5file = h5db._handle
        if title:
            h5file.set_node_attr(node, "TITLE", title)
        prov_info = provenance_info(files=files, repos=repos, base=base)

        provenance = yaml_dumps(prov_info)
        h5file.set_node_attr(node, "provenance", provenance)

    return do_h5(h5, func)


def collect_nodes(
    h5: Union[str, HDFStore], predicate: Callable[[str], Any], start_in="/"
) -> List[str]:
    """
    feed all groups into predicate and collect its truthy output
    """

    def func(h5db):
        out = [predicate(g._v_pathname) for g in h5db._handle.walk_groups(start_in)]
        return sorted(set(i for i in out if bool(i)))

    return do_h5(h5, func)


#########################
## Pandas etc

from pandas.core.generic import NDFrame
from pandas.api.types import is_numeric_dtype


def get_scalar_column(df, column):
    """
    Extract the single scalar value if column contains it.
    """
    col = df[column]
    val = col.iloc[0]

    assert col.isnull().all() or (col == val).all(), (column, df)

    return val


def drop_scalar_columns(df, scalar_columns) -> Tuple[pd.DataFrame, dict]:
    values = [get_scalar_column(df, c) for c in scalar_columns]
    scalars = dict(zip(scalar_columns, values))
    return df.drop(scalar_columns, axis=1), scalars


class Comparator:
    """Pick and concat side-by-side differently-named columns from multiple dataframe."""

    def __init__(
        self,
        col_accesor: Callable[[NDFrame, str], NDFrame],
        no_diff_prcnt=False,
        diff_colname="diffs",
        diff_bar_kw={"align": "mid", "color": ["#d65f5f", "#5fba7d"]},
        no_styling=False,
    ):
        """
        :param col_accessor:
            how to pick a column from an ndframe
        :param no_diff_prcnt:
            if this is falsy, and all equivalent columns are numerics,
            result dataframe contains an extra *diff* column.
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
            when access by ``self.col_accesor( df[i], col_name[i] )`` ∀ i ∈ [0, N).
        :param col_names:
            a list o N x column-names; Nones omit the respective dataset
        :return: 
        """
        picked_cols = [self.col_accesor(d, c) for d, c in zip(datasets, col_names) if c]
        dataset_names = list(dataset_names)

        if not self.no_diff_prcnt and all(is_numeric_dtype(d) for d in picked_cols):
            d0, *drest = picked_cols

            picked_cols = [d0]
            for d in drest:
                picked_cols.extend((d, 100 * (d0 - d) / d0))

            dataset_names = dataset_names + ["diffs[%]"]

        return pd.concat(picked_cols, axis=1, keys=dataset_names)

    def compare(
        self,
        datasets: Seq,
        equiv_colnames: Seq[Seq[str]],
        dataset_names: Seq[str],
        no_styling=None,
    ):
        """
        List side-by-side same-kind columns (with different names) from many datasets,

        optionally diffing them against the 1st dataset.

        :param datasets:
            a list of N x ndframes, each one containing the respective columns in `equiv_colnames`.
        :param equiv_colnames:
            a matrix of M x N column-names, like:
            
                [("p_downscale", "f_downscale"), ("cycle", "wltc_class"), ...]
                
            All columns in the N dimension must exist in the respective dataframe in `datasets` list.
            The 1st columns in the M-dimension are used a axis-1, level-0 labels 
            on the concatanated ndframe.
        :param dataset_names:
            used as hierarchical labels to distinuish from which dataset each column comes from
        """
        if no_styling is None:
            no_styling = self.no_styling

        col_level_0 = list(zip(*equiv_colnames))[0]
        df = pd.concat(
            (
                self._pick_n_diff_columns(datasets, cols, dataset_names)
                for cols in equiv_colnames
            ),
            axis=1,
            keys=col_level_0,
        )

        if self.diff_bar_kw and not no_styling:
            df = self._styled_with_diff_bars(df, col_level_0)
        return df

    def _styled_with_diff_bars(self, df, col_level_0):
        style = df.style
        for c in col_level_0:
            diff_idx = (c, "diffs[%]")
            try:
                df[diff_idx]
            except Exception:
                "Ok, `diff[%]` column missing"
            else:
                style = style.bar(subset=[diff_idx], **self.diff_bar_kw)

        return style


## Fix too-small columns when too many,
# from: https://github.com/quantopian/qgrid/issues/171#issuecomment-365489567
def grid(df, fitcols=True, cwidth=None):
    grid_opts = {"forceFitColumns": fitcols}
    if not fitcols and cwidth is None:
        cwith = 86
    if cwidth is not None:
        grid_opts["defaultColumnWidth"] = cwidth

    return qgrid.show_grid(df, grid_options=grid_opts)


#########################
## Vehicle-DB-specific

vehs_root = PurePosixPath("/vehicles")


def vehnode(vehnum=None, *suffix):
    p = vehs_root
    if vehnum is not None:
        p = vehs_root / ("v%0.3d" % int(vehnum))
    return str(p.joinpath(*suffix))


# assert vehnode(13) ==  '/vehicles/v013'
# assert vehnode(3, 'props') ==  '/vehicles/v003/props'
# assert vehnode(None, 'props') ==  '/vehicles/props'
# assert vehnode() ==  '/vehicles'


def load_vehicle(h5: Union[str, HDFStore], vehnum, *subnodes) -> list:
    "return vehicle's groups listed in `subnodes`"

    def func(h5db):
        return [h5db.get(vehnode(vehnum, sn)) for sn in subnodes]

    return do_h5(h5, func)


# props, pwot = load_vehicle(h5fname, vehnum, "props", "pwot")


def all_vehnums(h5) -> List[int]:
    def func(h5db):
        vehnums = [int(g._v_name[1:]) for g in h5db._handle.iter_nodes(vehnode())]
        return sorted(vehnums)

    return do_h5(h5, func)


def normalize_pwot(
    pwot,
    n_idle,
    n_rated,
    p_rated,
    c_n="n",
    c_p="Pwot",
    c_n_norm="n_norm",
    c_p_norm="p_norm",
):
    pwot = pwot.copy()
    pwot[c_n] = pwot.index

    pwot[c_n_norm] = (pwot[c_n] - n_idle) / (n_rated - n_idle)
    pwot[c_p_norm] = pwot[c_p] / p_rated

    return pwot[[c_n_norm, c_p_norm]]


def run_pyalgo_on_Heinz_vehicle(
    h5, vehnum, props_group_suffix="iprop", pwot_group_suffix="pwot"
) -> Tuple[dict, pd.DataFrame]:
    """
    Quick'n dirty way to invoke python-algo (bc model will change).
     
    :param h5:
        the `WltpGs-msaccess.h5` file (path or h5db) to read input from 
    :return:
        the *out-props* key-values, and the *cycle_run* data-frame
    """
    from wltp.experiment import Experiment

    props, pwot = load_vehicle(h5, vehnum, props_group_suffix, pwot_group_suffix)

    ndvs = [props["ndv_%i" % g] for g in range(1, props["no_of_gears"] + 1)]
    norm_pwot = normalize_pwot(
        pwot, props.idling_speed, props.rated_speed, props.rated_power
    )
    inverse_SM = 1.0 - props.SM

    input_model = yaml_loads(
        f"""
        vehicle:
          gear_ratios:  {ndvs}
          resistance_coeffs:
            - {props.f0} 
            - {props.f1}
            - {props.f2}
          p_rated:      {props.rated_power}
          unladen_mass: {props.kerb_mass}
          test_mass:    {props.test_mass}
          n_rated:      {props.rated_speed}
          n_idle:       {props.idling_speed}
          v_max:        {props.v_max_declared}
        params:
          f_safety_margin: {inverse_SM}
        """
    )
    input_model["vehicle"]["full_load_curve"] = norm_pwot

    exp = Experiment(input_model)
    output_model = exp.run()

    ## Keep only *output* key-values, not to burden HDF data-model
    #  (excluding `driveability`, which is a list, and f0,f1,f2, addume were input).
    #
    veh = output_model["vehicle"]
    oprops = {
        "f_downscale": output_model["params"]["f_downscale"],
        "pmr": veh["pmr"],
        "wltc_class": veh["wltc_class"],
        "v_max": veh["v_max"],
    }

    cycle_run = output_model["cycle_run"]
    # Drop `driveability` arrays, not to burden HDF data-model.
    cycle_run = cycle_run.drop("driveability", axis=1)
    ## Gears are `int8`, and h5 pickles them.
    #
    for badtype_col in "gears gears_orig".split():
        cycle_run[badtype_col] = cycle_run[badtype_col].astype("int64")

    return oprops, cycle_run


# oprops, cycle = nbu.run_pyalgo_on_Heinz_vehicle(inp_h5fname, 14)
# display(oprops, cycle)


def merge_db_vehicle_subgroups(
    h5: Union[str, HDFStore], vehicle_subgroups, veh_nums=None
) -> List[NDFrame]:
    """
    Merge HDF-subgroup(s) from all vehicles into an Indexed-DataFrame(s)

    :param h5:
        any `WltpGs-*.h5` file (path or h5db) containing `vehicles/v001/{subgroups}` groups 
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

    return index_dfs
