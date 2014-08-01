#####################################
wltp: A *wltc* gear-shifts calculator
#####################################
:Home:          https://github.com/ankostis/wltp
:Documentation: https://wltp.readthedocs.org/
:PyPI:          https://pypi.python.org/pypi/wltp
:Copyright:     2013-2014 European Commission (JRC)
:License:       `EUPL 1.1+ <https://joinup.ec.europa.eu/software/page/eupl>`_


A calculator of the gear-shifts profile for light-duty-vehicles (cars)
according to UNECE's draft of the
`Worldwide harmonized Light vehicles Test Procedures <https://en.wikipedia.org/wiki/Worldwide_harmonized_Light_vehicles_Test_Procedures>`_.

.. important:: This simulator is still in *alpha* stage.
    Known limitations are described in the :doc:`CHANGES`.


Introduction
============

The calculator accepts as input the vehicle-specifications and parameters for modifying the execution
of the WLTC-cycle and spits-out the it gear-shifts of the vehicle, the attained speed-profile,
and any warnings.  It certainly does not calculate any CO2 emissions or other metrics.


An "execution" or a "run" of an experiment is depicted in the following diagram::


         .-------------------.    ______________        .-------------------.
        /        Model      /    | Experiment   |       / Model(augmented)  /
       /-------------------/     |--------------|      /-------------------/
      / +--vehicle        /  ==> |  .----------.| ==> / +...              /
     /  +--params        /       | / WLTC-data/ |    /  +--cycle_run     /
    /                   /        |'----------'  |   /                   /
    '------------------'         |______________|  '-------------------'


Install
-------
Requires Python 3.3+.
Install it directly from the `PyPI <https://pypi.python.org/pypi>`_ repository with the usual::

    $ pip3 install wltc

Or assuming you have download the sources::

    $ python setup.py install


.. Seealso:: `WinPython <http://winpython.sourceforge.net/>`_



Python usage
------------
A usage example::

    >> import wltc

    >> model = {
        "vehicle": {
            "mass":     1500,
            "v_max":    195,
            "p_rated":  100,
            "n_rated":  5450,
            "n_idle":   950,
            "n_min":    None, # Can be overriden by manufacturer.
            "gear_ratios":      [120.5, 75, 50, 43, 37, 32],
            "resistance_coeffs":[100, 0.5, 0.04],
        }
    }

    >> experiment = wltc.Experiment(model)

    >> model = experiment.run()

    >> print(model['params'])
    >> print(model['cycle_run'])
    >> print(Experiment.driveability_report())



    >> {
        'wltc_class':   'class3b'
        'v_class':      [ 0.,  0.,  0., ...,  0.,  0.,  0.],
        'f_downscale':  0,
        'v_target':     [ 0.,  0.,  0., ...,  0.,  0.,  0.],
        'gears':        [0, 0, 0, ..., 0, 0, 0],
        'clutch':       array([ True,  True,  True, ...,  True,  True,  True], dtype=bool),
        'v_real':       [ 0.,  0.,  0., ...,  0.,  0.,  0.],
        'driveability': {...},
    }


For information on the model-data, check the schema::

    >> print(wltc.model.model_schema())


For more examples, download the sources and check the test-cases
found at ``/wltp/test``.



Cmd-line usage
--------------
.. Note:: Not implemented in this vesion

To get help::

    $ python wltc --help          ## to get generic help for cmd-line syntax
    $ python wltc -M /vehicle     ## to get help for specific model-paths


and then, assuming ``vehicle.csv`` is a CSV file with the vehicle parameters
for which you want to override the ``n_idle`` only, run the following::

    $ python wltc -v \
        -I vehicle.csv file_frmt=SERIES model_path=/params header@=None \
        -m /vehicle/n_idle:=850 \
        -O cycle.csv model_path=/cycle_run




Contribute
==========
:Issue Tracker: https://github.com/ankostis/wltp/issues
:Source Code: https://github.com/ankostis/wltp

.. Seealso:: :doc:`INSTALL`



Contributors
------------
* Steven Heinz for his test-data and the cooperation on the tricky parts of the specification.
* Giorgos Fontaras for physics, policy and admin support.
* Kostis Anagnostopoulos, author.



History
-------
Implemented from scratch based on the UN's specs (document also included in the `docs` dir):

* http://www.unece.org/trans/main/wp29/wp29wgs/wp29grpe/grpedoc_2013.html
* https://www2.unece.org/wiki/pages/viewpage.action?pageId=2523179
* But probably a better spec is this one:
  https://www2.unece.org/wiki/display/trans/DHC+draft+technical+report

.. Seealso:: :doc:`CHANGES`


