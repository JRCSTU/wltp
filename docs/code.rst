API reference
=============
The core of the simulator is composed from the following modules:

.. currentmodule:: wltp
.. autosummary::

    cycles
    datamodel
    experiment
    cycler
    engine
    vehicle
    vmax
    downscale
    nmindrive
    invariants
    autograph
    io
    utils
    cli
    plots
    idgears


Module: :mod:`wltp.cycles`
-----------------------------
.. automodule:: wltp.cycles
    :members:

Module: :mod:`wltp.datamodel`
-----------------------------
.. automodule:: wltp.datamodel
    :members:

Module: :mod:`wltp.experiment`
------------------------------
.. automodule:: wltp.experiment
    :members:

Module: :mod:`wltp.pipelines`
-----------------------------
.. automodule:: wltp.pipelines
    :members:

Module: :mod:`wltp.cycler`
--------------------------
.. automodule:: wltp.cycler
    :members:

Module: :mod:`wltp.engine`
--------------------------
.. automodule:: wltp.engine
    :members:

Module: :mod:`wltp.vehicle`
---------------------------
.. automodule:: wltp.vehicle
    :members:

Module: :mod:`wltp.vmax`
------------------------
.. automodule:: wltp.vmax
    :members:

Module: :mod:`wltp.downscale`
-----------------------------
.. automodule:: wltp.downscale
    :members:

Module: :mod:`wltp.nmindrive`
-----------------------------
.. automodule:: wltp.nmindrive
    :members:

Module: :mod:`wltp.invariants`
------------------------------
.. automodule:: wltp.invariants
    :members:
    :undoc-members:

Module: :mod:`wltp.autograph`
-----------------------------
.. automodule:: wltp.autograph
    :members:

Module: :mod:`wltp.io`
----------------------
.. automodule:: wltp.io
    :members:

Module: :mod:`wltp.utils`
-------------------------
.. automodule:: wltp.utils
    :members:

Module: :mod:`wltp.cli`
-----------------------
.. automodule:: wltp.cli
    :members:

Module: :mod:`wltp.plots`
-------------------------
.. automodule:: wltp.plots
    :members:

Module: :mod:`wltp.idgears`
---------------------------
.. automodule:: wltp.idgears
    :members:


Validation tests & HDF5 DB
--------------------------
Among the various tests, those running on 'sample' databases for comparing differences
with existing tool are the following:

Module: :mod:`tests.vehdb`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. automodule:: tests.vehdb
    :members:

(abandoned)
~~~~~~~~~~~
.. autosummary::

    tests.test_samples_db
    tests.test_wltp_db

The following scripts in the sources maybe used to preprocess various wltc data:

* :file:`devtools/printwltcclass.py`
* :file:`devtools/csvcolumns8to2.py`

.. automodule:: tests.test_samples_db
    :members:
.. automodule:: tests.test_wltp_db
    :members:
