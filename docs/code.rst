API reference
=============
The core of the simulator is composed from the following modules:

.. currentmodule:: wltp
.. autosummary::

    model
    experiment
    idgears

Among the various tests, those running on 'sample' databases for comparing differences
with existing tool are the following:

.. currentmodule:: tests
.. autosummary::

    test_samples_db
    test_wltp_db

The following scripts in the sources maybe used to preprocess various wltc data:

* :file:`devtools/preprocheinz.py`
* :file:`devtools/printwltcclass.py`
* :file:`devtools/csvcolumns8to2.py`



Module: :mod:`wltp.experiment`
------------------------------
.. automodule:: wltp.experiment
    :members:

Module: :mod:`wltp.model`
-------------------------
.. automodule:: wltp.model
    :members:

Module: :mod:`tests.test_samples_db`
-----------------------------------------
.. automodule:: tests.test_samples_db
    :members:

Module: :mod:`tests.test_wltp_db`
--------------------------------------
.. automodule:: tests.test_wltp_db
    :members:

