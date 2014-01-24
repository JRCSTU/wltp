==========================
WLTC gear-shift calculator
==========================

WLTCG calculates the gear-shifts/real_velocity profile for light-duty-vehicles (cars)
according to UN's draft WLTC testing-cycle.

It accepts as input the car-specifications and a selection of a WLTC-cycle classes
and spits-out the attained speed-profile by the vehicle, along with it gear-shifts used
and any warnings.  It certainly does not calculate any CO2 emissions or other metrics.

To install it, assuming you have download the sources,
do the usual::

    python setup.py install

Or get it directly from the PIP repository::

    pip3 install wltc


For Python 3.3 or later.


Overview:
=========

An "execution" or a "run" of an experiment is depicted in the following diagram::

                       _______________
     .-------.        |               |      .------------------.
    / Model /-.   ==> |   Experiment  | ==> / Model(augmented) /
   '-------'  /   ==> |---------------|    '------------------'
     .-------'        |  .-----------.|
                      | / WLTC-data / |
                      |'-----------'  |
                      |_______________|

Usage:
------

A usage example::

    >> import wltc

    >> model = wltc.Model({
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
    >> experiment.run()
    >> print(model.data['results'])
    >> print(model.driveability_report())



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



CHANGES
=======

v0.0.2, 7-Jan-2014 -- Alpha release
-----------------------------------

* Still unchecked for correctness of results.
* Better README.txt and package-desc.

v0.0.1, 6-Jan-2014 -- Alpha release
-----------------------------------

* Unchecked for correctness.
* Not implemented yet driveability rules.
* Does not output real_velocity yet - inly gears.
* Detecting and applying downscaling.
* Interpreted and implemented the nonsensical specs concerning ``n_min`` engine-revolutions for gear-2
  (Annex 2-3.2, p71).

v0.0.0, 11-Dec-2013 -- Inception stage
--------------------------------------

* Mostly setup.py work, README and help.





Development:
============

The WLTC-profiles for the various classes in the ./util/data/cycles folder were generated from the tables
of the UN word-doc with the specs using the ``./util/csvcolumns8to2`` script, but it still requires
an intermediate manual step involving a spreadsheet to copy the table into ands save them as CSV.

Then use the ``./util/buildwltcclass.py`` to contruct the respective python-vars into the
wltc/Model.py sources.

TODO:
    running the test suite




History
=======

Implemented from scratch based on the UN's specs (document also included in the ./docs dir):
* http://www.unece.org/trans/main/wp29/wp29wgs/wp29grpe/grpedoc_2013.html
* https://www2.unece.org/wiki/pages/viewpage.action?pageId=2523179

But probably a better spec is this one:
* https://www2.unece.org/wiki/display/trans/DHC+draft+technical+report

By ankostis@gmail.com, Dec-2013, (c) AGPLv3 or later



Thanks also to
==============

* Giorgos Fontaras for physics, policy and admin support.
* Steven Heinz for his test-data.
