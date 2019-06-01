from typing import Tuple, Dict, Union
import io, json, time, platform
from datetime import datetime
from ruamel.yaml import YAML
from pathlib import Path, PurePosixPath
from copy import deepcopy
import logging 

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


def _git_describe():
    import subprocess as sbp

    try:
        return sbp.check_output("git describe --always".split()).trim()
    except Exception as ex:
        log.info("Cannot git-describe due to: %s", ex)


def _provenir_fpath(fpath, algos=("md5", "sha256")) -> Dict[str, str]:
    s = {"fpath": str(fpath)}

    fpath = Path(fpath)
    if fpath.exists():
        s["hexsums"] = dict(_file_hashed(fpath, algo) for algo in algos)
        s["ctime"] = _human_time(fpath.stat().st_ctime)

    return s


def provenance_info(*fpaths, prov_info=None) -> Dict[str, str]:
    """
    :param prov_info:
        if given, reused (cloned first), and any fpaths appended in it.
    """
    if prov_info:
        info = deepcopy(prov_info)

        fps = info.get("fpaths")
        if not isinstance(fpaths, list):
            fps = info["fpaths"] = []
        fps.extend(_provenir_fpath(f) for f in fpaths)
    else:
        info = {"ctime": _human_time(), "uname": dict(platform.uname()._asdict())}

        gitver = _git_describe()
        if gitver:
            info["gitver"] = gitver

        if fpaths:
            info["fpaths"] = [_provenir_fpath(f) for f in fpaths]

    return info


# prov_info = _provenance_info(xlfname)
# prov_info = provenance_info('sfdsfd', prov_info=prov_info)
# provenance_info('ggg', prov_info=prov_info)



#########################
## HDF5 

def openh5(h5: Union[str, HDFStore]):
    "open h5-fpath or reuse existing h5db instance"
    
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


def print_nodes(h5: Union[str, HDFStore], displaywidth=160):
    from columnize import columnize

    with openh5(h5) as h5db:
        nodes = h5db.keys()
    
    print(columnize(nodes, displaywidth=displaywidth))


def provenir_h5node(h5db, node, *fpaths, title=None, prov_info=None):
    h5file = h5db._handle
    if title:
        h5file.set_node_attr(node, "TITLE", title)
    if prov_info is None:
        prov_info = provenance_info(*fpaths)

    provenance = yaml_dumps(prov_info)
    h5file.set_node_attr(node, "provenance", provenance)


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

vehs_root = PurePosixPath('/vehicles')

def vehnode(vehnum=None, *suffix):
    p = vehs_root
    if vehnum is not None:
        p = vehs_root / ("v%0.3d" % int(vehnum))
    return str(p.joinpath(*suffix))
# assert vehnode(13) ==  '/vehicles/v013'
# assert vehnode(3, 'props') ==  '/vehicles/v003/props'
# assert vehnode(None, 'props') ==  '/vehicles/props'
# assert vehnode() ==  '/vehicles'

def load_vehicle(h5, vehnum, *subnodes) -> list:
    with openh5(h5) as h5db:
        return [h5db.get(vehnode(vehnum, sn)) for sn in subnodes]

