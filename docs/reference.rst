Implementation
==============
The following module comprise the core of the simulator:

.. autosummary::

    wltp.experiment
    wltp.model
    wltp.cycles.class1
    wltp.cycles.class2
    wltp.cycles.class3

Among the various tests, those involved with data and divergence from existing tool are:

* :mod:`wltp.test.experiment_WholeVehicleTests`
* :mod:`wltp.test.wltp_db_tests`
* :mod:`wltp.test.experiment_SampleVehicleTests`

The following scripts in the sources maybe used to preprocess various wltc data:

* :mod:`util/preprocheinz.py`
* :mod:`util/printwltcclass.py`
* :mod:`util/csvcolumns8to2.py`


Module: :mod:`wltp.experiment`
------------------------------
.. automodule:: wltp.experiment
    :members:


Module: :mod:`wltp.model`
-------------------------
.. automodule:: wltp.model
    :members:




