#################################################################################
WLTP: WLTC gear-shift calculator
#################################################################################
:Copyright:   2013-2014 European Commission (JRC)
:License:     EUPL


A calculator of the gear-shifts profile for light-duty-vehicles (cars)
according to UN's draft on the Worldwide harmonized Light vehicles Test Procedures.


Overview:
=========

It accepts as input the car-specifications and a selection of a WLTC-cycle classes
and spits-out the attained speed-profile by the vehicle, along with it gear-shifts used
and any warnings.  It certainly does not calculate any CO2 emissions or other metrics.

An "execution" or a "run" of an experiment is depicted in the following diagram::


         .-------------------.    ______________        .-------------------.
        /        Model      /    | Experiment   |       / Model(augmented)  /
       /-------------------/     |--------------|      /-------------------/
      / +--vehicle        /  ==> |  .----------.| ==> / +...              /
     /  +--params        /       | / WLTC-data/ |    /  +--cycle_run     /
    /                   /        |'----------'  |   /                   /
    '------------------'         |______________|  '-------------------'



Install:
========

Requires Python-3.

To install it, assuming you have download the sources,
do the usual::

    python setup.py install

Or get it directly from the PyPI repository::

    pip3 install wltc


Tested on::

     Python 3.3.5 (v3.3.5:62cf4e77f785, Mar  9 2014, 10:35:05) (AMD64)] on win32,

.. Seealso::

    WinPython <http://winpython.sourceforge.net/>




Cmd-line usage:
===============

To get help::

    $ python wltc --help          ## to get generic help for cmd-line syntax

    $ python wltc -M /vehicle     ## to get help for specific model-paths


and then, as an example::

    python wltc -v \
        -I vehicle.csv file_frmt=SERIES model_path=/params header@=None \
        -m /vehicle/n_idle:=850 \
        -O cycle.csv model_path=/cycle_run


Python Usage:
=============

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

    print(wltc.instances.model_schema())


Development:
============

See :doc:`INSTALL.txt`



History
=======

Implemented from scratch based on the UN's specs (document also included in the ./docs dir):
* http://www.unece.org/trans/main/wp29/wp29wgs/wp29grpe/grpedoc_2013.html
* https://www2.unece.org/wiki/pages/viewpage.action?pageId=2523179

But probably a better spec is this one:
* https://www2.unece.org/wiki/display/trans/DHC+draft+technical+report

.. Seealso:: :doc:`INSTALL.txt`


Contributors
============

* Kostis Anagnostopoulos, author.
* Steven Heinz for his test-data and the cooperation on the tricky parts of the specification.
* Giorgos Fontaras for physics, policy and admin support.
