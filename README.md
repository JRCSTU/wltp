# WLTP
UNECE's WLTP reference implementation in Python

## Contents
- Python code implementing the WLTP algorithm.
- Notebooks to process the vehicle data, launch the algo, etc.
- The original files of the algo (document & MSAccess db).


## HDF5
Heinz Steven has implemented the original reference algorithm in the [`WLTP_GS_calculation_15032019_for_prog_code_subgroup.accdb`](./WLTP_GS_calculation_15032019_for_prog_code_subgroup.accdb) *MSAccess* database.
That database facilitated the development & execution of the algorithm 
by storing any and all data needed during those phases.

To substitute those facilities i used the *pandas* + *HDF5* file-format to store all data, 
peristently, across code runs.

- Help on `pandas` HDF5 python library: https://pandas.pydata.org/pandas-docs/stable/user_guide/io.html#io-hdf5
- Help on the underlying `tables` library: https://www.pytables.org/
- Use `vitables` GUI to inspect the file (`conda install vitables`). 
- All major API methods of those libraries are listed  at the top 
  of the `CarsDB.ipynb` notebook.


## Recreate this Jupyter server
This server runs on a *conda* environment.  
All installed dependencies are kept in the `./environment.yaml` file,

> **Tip:**
> 
> Maintain the env-file by running this terminal command after any programm (un)install::
>     
>     conda env export -n jupyter > environment.yaml 

To reproduce this server:

1. recreate the conda-env::

  ```bash
  $ conda env create -f environment.yaml
  ```

2. then ensure `qgrid` is properly installed for *jupyter lab*,
  by following [the instructions](https://github.com/quantopian/qgrid#installation)
  
  Optionally [install `jupytext`](https://github.com/mwouts/jupytext) if you want 
  to commit changes into this project's git-repo.

3. Finally launch it with:

  ```bash
  $ jupyter lab
  ```


## Code to extract data from MSAccess

in case it is needed in the future
...but cannot run in this server bc `pyodbc` lib cannot runs on *Linux* :-( 

```python
## Can run only on WINDOWS only!!
#
import pyodbc

def mdb_connect(db_file, user='admin', password = '', old_driver=False):
    """
    :param db_file:
        must be an absolute path
    """
    driver_ver = '*.mdb'
    if not old_driver:
        driver_ver += ', *.accdb'

    odbc_conn_str = ('DRIVER={Microsoft Access Driver (%s)}'
                     ';DBQ=%s;UID=%s;PWD=%s' %
                     (driver_ver, db_file, user, password))

    return pyodbc.connect(odbc_conn_str)

fname='WLTP_GS_calculation_15032019_for_prog_code_subgroup.accdb'
conn = mdb_connect(fname)
crsr = conn.cursor()

print([i.table_name for i in crsr.tables(tableType='TABLE')]
print([i.column_name for i in crsr.columns('gearshift_table_all')]
```