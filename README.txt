==========================
WLTC gear-shift calculator
==========================

WLTCG calculates the gear-shifts/real_velocity profile for light-duty-vehicles (cars)
according to the WLTC testing-cycle.

It accepts as input the car-specifications and a selection of a WLTC-cycle classes
and spits-out the attained speed-profile by the vehicle, along with it gear-shifts used
and any warnings.  It certainly does not calculate any CO2 emissions or other metrics.

To install it, assuming you have download the sources,
do the usual::

	python setup.py install

Or get it directly from the PIP repository::

	pip3 install wltc


For Python 3.3 or later.


Usage:
======

An "execution" or a "run" of an experiment is depicted in the following diagram::

                       _______________
     .-------.        |               |      .------------------.
    / Model /-.   ==> |   Experiment  | ==> / Model(augmented) /
   '-------'  /   ==> |---------------|    '------------------'
     .-------'        |  .-----------.|
                      | / WLTC-data / |
                      |'-----------'  |
                      |_______________|


A typical usage would look like this::

	import wltc

    model = wltc.Model({
	    "vehicle": {
	        "mass":     1500,
	        "v_max":    195,
	        "p_rated":  100,
	        "n_rated":  5450,
	        "n_idle":   950,
	        "n_min":    500,
	        "gear_ratios":      [120.5, 75, 50, 43, 37, 32],
	        "resistance_coeffs":[100, 0.5, 0.04],
	    }
	}

    experiment = wltc.Experiment(model)
    experiment.run()
    print(model['results'])


For information on the model-data, check the schema::

	print(wltc.instances.model_schema())



Installation
============

The first step is to expand the .tgz archive in a temporary directory (not directly in Python's site-packages).
It contains a distutils setup file "setup.py". OS-specific installation instructions follow.

GNU/Linux, BSDs, Unix, Mac OS X, etc.
-------------------------------------

# Open a shell.

# Go to the directory created by expanding the archive::

 ``cd <archive_directory_path>``

# Install the package (you may need root permissions to complete this step)::

	su
	(enter admin password)
	python setup.py install

If the python executable isn't on your path, you'll have to specify the complete path, such as /usr/local/bin/python.

To install for a specific Python version, use this version in the setup call, e.g.::

	python3.1 setup.py install

To install for different Python versions, repeat step 3 for every required version. The last installed
version will be used in the `shebang line<http://en.wikipedia.org/wiki/Shebang_%28Unix%29>` of the ``rst2*.py`` wrapper scripts.


Windows
-------

Just double-click ``install.py``. If this doesn't work, try the following:

# Open a DOS Box (Command Shell, MS-DOS Prompt, or whatever they're calling it these days).

# Go to the directory created by expanding the archive::

	cd <archive_directory_path>

# Install the package::

	<path_to_python.exe>\python setup.py install

To install for a specific python version, specify the Python executable for this version.

To install for different Python versions, repeat step 3 for every required version.


Development:
------------

The WLTC-profiles for the various classes in the ./util/data/cycles folder were generated from the tables
of the UN word-doc with the specs using the ``./util/csvcolumns8to2`` script, but it still requires
an intermediate manual step involving a spreadsheet to copy the table into ands save them as CSV.

Then use the ``./util/buildwltcclass.py`` to contruct the respective python-vars into the
wltc/Model.py sources.

TODO:
	running the test suite




History
=======

Implemented from the UN's specs (document also included in the docs):
  https://www2.unece.org/wiki/pages/viewpage.action?pageId=2523179

By ankostis@gmail.com, Dec-2013, JRC, (c) AGPLv3 or later



Thanks also to
==============

* Giorgos Fontaras for physics, policy and admin support.
* Steven Heinz for his test-data.
