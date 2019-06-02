from typing import List, Tuple, Dict, Union, Callable, Any
import io, json, time, platform
from datetime import datetime
from ruamel.yaml import YAML
from pathlib import Path, PurePosixPath
from copy import deepcopy
import logging
import subprocess as sbp
import os
import shutil


import pandas as pd
from pandas import HDFStore


log = logging.getLogger(__name__)


def yaml_dumps(o) -> str:
    s = io.StringIO()
    yaml = YAML(typ="safe", pure=True)
    yaml.default_flow_style = False
    # yaml.canonical = True
    yaml.dump(o, s)
    return s.getvalue()


def yaml_loads(y) -> Union[dict, list]:
    s = io.StringIO(y)
    yaml = YAML(typ="safe", pure=True)
    return yaml.load(y)
    return s.getvalue()


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


def _git_describe(basedir="."):
    args = ["git", "-C", basedir, "describe", "--always"]
    try:
        return sbp.check_output(args, universal_newlines=True).strip()
    except Exception as ex:
        return "Cannot git-describe due to: %s" % ex


def _python_describe():
    info = {"path": shutil.which("python")}
    condaenv = os.environ.get("CONDA_DEFAULT_ENV")
    log.info(f"Asking conda-env({condaenv}) or `pip`.")
    if condaenv:
        info["type"] = "conda"

        try:
            info["env"] = yaml_loads(
                sbp.check_output(
                    ["conda", "env", "export", "-n", condaenv], universal_newlines=True
                )
            )
        except Exception as ex:
            raise ex
            info["env"] = "Cannot conde-env-export due to: %s" % ex
    else:
        try:
            info["env"] = (
                sbp.check_output(
                    "pip list --format freeze".split(), universal_newlines=True
                )
                .strip()
                .split("\n")
            )
        except Exception as ex:
            raise ex
            info["env"] = "Cannot pip-list due to: %s" % ex

    return info


def _provenir_fpath(fpath, algos=("md5", "sha256")) -> Dict[str, str]:
    s = {"path": str(str(Path(fpath).absolute()))}

    fpath = Path(fpath)
    if fpath.exists():
        s["hexsums"] = dict(_file_hashed(fpath, algo) for algo in algos)
        s["ctime"] = _human_time(fpath.stat().st_ctime)

    return s


def provenance_info(*, files=(), repos=(), base=None) -> Dict[str, str]:
    """Build a provenance record, examining environment if no `base` given.
    
    :param base:
        if given, reused (cloned first), and any fpaths & git-repos appended in it.
    """
    if base:
        info = deepcopy(base)

    else:
        info = {"uname": dict(platform.uname()._asdict()), "python": _python_describe()}

    info["ctime"] = _human_time()

    fps = info.get("files")
    if not isinstance(fps, list):
        fps = info["files"] = []
    fps.extend(_provenir_fpath(f) for f in files)

    gtr = info.get("repos")
    if not isinstance(gtr, list):
        gtr = info["repos"] = []
    gtr.extend(
        {"path": str(Path(g).absolute()), "type": "git", "version": _git_describe(g)}
        for g in repos
    )

    return info


# prov_info = nbu.provenance_info(fpaths=[h5fname])
# prov_info = nbu.provenance_info(fpaths=['sfdsfd'], base=prov_info)
# prov_info = nbu.provenance_info(fpaths=['ggg'], git_repos=['../wltp.git'], base=prov_info)
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
    if isinstance(h5, HDFStore) and h5.is_open:
        out = func(h5, *args, **kw)
    else:
        with openh5(h5) as h5db:
            out = func(h5db, *args, **kw)

    return out


def print_nodes(h5: Union[str, HDFStore], displaywidth=160):
    from columnize import columnize

    nodes = do_h5(h5, lambda h5db: h5db.keys())

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
        return [i for i in out if bool(i)]
    return do_h5(h5, func)
    

#########################
## Pandas etc
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