#####################################
wltp: A *wltc* gear-shifts calculator
#####################################
|dev-status| |build-status| |cover-status| |docs-status| |pypi-status| |downloads_count|

:Version:       |version|
:Home:          https://github.com/ankostis/wltp
:Documentation: https://wltp.readthedocs.org/
:Copyright:     2013-2014 European Commission (`JRC-IET <http://iet.jrc.ec.europa.eu/>`_)
:License:       `EUPL 1.1+ <https://joinup.ec.europa.eu/software/page/eupl>`_

Calculates the *gear-shifts* of Light-duty vehicles running the :term:`WLTP`
driving-cycles, according to the specifications of the :term:`UNECE` draft.

.. figure:: docs/wltc_class3b.png
    :align: center

    **Figure 1:** *WLTP cycle for class-3b Vehicles*


.. important:: This project is still in *alpha* stage.  Its results are not
    considered "correct", and no approval procedure should rely on them.
    Some of the known deficiencies are described in :doc:`CHANGES`.
    Comparison of result with those from Heinz-db are imprinted in the :mod:`~wltp.test.wltp_db_tests` test-case.



.. _begin_intro:

Introduction
============

The calculator accepts as input the vehicle-specifications and parameters for modifying the execution
of the :term:`WLTC` cycle and spits-out the it gear-shifts of the vehicle, the attained speed-profile,
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

.. Tip:: `WinPython <http://winpython.sourceforge.net/>`_ and
    `Anaconda <http://docs.continuum.io/anaconda/pkg-docs.html>`_ python distributions
    for *Windows* and *OS X*, respectively.

You can install the project directly from the `PyPI <https://pypi.python.org/pypi>`_ repository
with the usual command (note the ``--pre`` option, since it is still in *Alpha* version):

.. code-block:: console

    $ pip3 install wltp --pre
    $ wltp.py --help
    usage: wltp.py -I ARG [ARG ...] [-c COLUMN_SPEC [COLUMN_SPEC ...]]
              [-r [COLUMN_SPEC [COLUMN_SPEC ...]]]
              [-m MODEL_PATH=VALUE [MODEL_PATH=VALUE ...]]
              [--strict [TRUE | FALSE]] [-M [MODEL_PATH [MODEL_PATH ...]]]
              [-O ARG [ARG ...]] [-d] [-v] [--version] [--help]

    Calculates the *gear-shifts* of Light-duty vehicles running the :term:`WLTP`
    driving-cycles, according to the specifications of the :term:`UNECE` draft.
    ...


Or you can build it from the latest sources
(assuming you have a working installation of `git <http://git-scm.com/>`_):

.. code-block:: console

    $ git clone "https://github.com/ankostis/wltp.git" wltp
    $ cd wltp
    $ python3 setup.py install .


That way you get the complete source-tree of the project, ready for development
(see :doc:`contribute`)::

    +--wltp/            ## (package) The python-code of the calculator
    |   +--cycles/      ## (package) The python-code for the WLTC data
    |   +--test/        ## (package) Test-cases and the wltp_db
    |   +--model        ## (module) Describes the data for the calculation
    |   +--experiment   ## (module) The calculator
    +--docs/            ## Documentation folder
    +--util/            ## Scripts for preprocessing WLTC data and the wltp_db
    +--wltp.py          ## (script) The cmd-line entry-point script for the calculator
    +--README.rst
    +--CHANGES.rst
    +--LICENSE.txt




Python usage
------------
Here is a quick-start python :abbr:`REPL (Read–Eval–Print Loop)` examples to create and validate a *model*
with the input-data for runing a single experiment:

.. doctest::
    :options: +ELLIPSIS, +NORMALIZE_WHITESPACE

    >>> from wltp import model
    >>> from wltp.experiment import Experiment

    >>> mdl = {
    ...   "vehicle": {
    ...     "unladen_mass": 1430,
    ...     "test_mass":    1500,
    ...     "v_max":    195,
    ...     "p_rated":  100,
    ...     "n_rated":  5450,
    ...     "n_idle":   950,
    ...     "n_min":    None, # Can be overriden by manufacturer.
    ...     "gear_ratios":      [120.5, 75, 50, 43, 37, 32],
    ...     "resistance_coeffs":[100, 0.5, 0.04],
    ...   }
    ... }
    >>> processor = Experiment(mdl)         ## Validates model

If model validated without any errors, you can then run the experiment:

.. doctest::
    :options: +ELLIPSIS, +NORMALIZE_WHITESPACE

    >>> mdl = processor.run()               ## Runs experiment and augments model with results.
    >>> model.json_dumps(mdl)               ## Would print the complete augmented model (long!).            # doctest: +SKIP
    ...
    >>> print(model.json_dumps(mdl['params'], indent=2))     ## The ``params`` augmented with the WLTC-class & downscaling.  # doctest: +SKIP
    {
      "wltc_class": "class3b",
      "f_downscale": 0,
      "f_inertial": 1.1,
      "f_n_min_gear2": 0.9,
      "f_n_max": 1.2,
      "f_n_clutch_gear2": [
        1.15,
        0.03
      ],
      "v_stopped_threshold": 1,
      "f_n_min": 0.125,
      "f_safety_margin": 0.9
    }


To access the time-based cycle-results it is better to use a :class:`pandas.DataFrame`:

.. doctest::
    :options: +ELLIPSIS, +NORMALIZE_WHITESPACE

    >>> import pandas as pd
    >>> df = pd.DataFrame(mdl['cycle_run'])
    >>> df.columns
    Index(['v_class', 'v_target', 'clutch', 'gears_orig', 'gears', 'v_real', 'p_available', 'p_required', 'rpm', 'rpm_norm', 'driveability'], dtype='object')
    >>> df.index.name = 't'
    >>> print('Mean engine_speed: ', df.rpm.mean())
    Mean engine_speed:  1917.0407829

    >>> print(df.head())                                                            # doctest: +SKIP
      clutch driveability  gears  gears_orig  p_available  p_required  rpm  \
    t
    0  False                   0           0            9           0  950
    1  False                   0           0            9           0  950
    2  False                   0           0            9           0  950
    3  False                   0           0            9           0  950
    4  False                   0           0            9           0  950
    ...
    >>> print(processor.driveability_report())                                      # doctest: +SKIP
    ...
      12: (a: X-->0)
      13: g1: Revolutions too low!
      14: g1: Revolutions too low!
    ...
      30: (b2(2): 5-->4)
    ...
      38: (c1: 4-->3)
      39: (c1: 4-->3)
      40: Rule e or g missed downshift(40: 4-->3) in acceleration?
    ...
      42: Rule e or g missed downshift(42: 3-->2) in acceleration?
    ...

You can export the cycle-run results in a CSV-file with the following pandas command:

.. doctest::

    >>> df.to_csv('cycle_run.csv')

For information on the model-data, check the schema:

.. doctest::
    :options: +SKIP

    >>> print(model.json_dumps(model.model_schema(), indent=2))                         # doctest: +SKIP
    {
      "properties": {
        "params": {
          "properties": {
            "f_n_min_gear2": {
              "description": "Gear-2 is invalid when N :< f_n_min_gear2 * n_idle.",
              "type": [
                "number",
                "null"
              ],
              "default": 0.9
            },
            "v_stopped_threshold": {
              "description": "Velocity (Km/h) under which (<=) to idle gear-shift (Annex 2-3.3, p71).",
              "type": [
    ...


For more examples, download the sources and check the test-cases
found at ``/wltp/test``.



Cmd-line usage
--------------
.. Note:: Not implemented in yet.

The examples presented so far required to execute multiple commands interactively inside
the Python interpreter (REPL).
The comand-line usage below still requires the Python environment to be installed, but provides for
executing an experiment directly from the OS's shell (i.e. ``cmd.exe`` in windows or ``bash`` in POSIX),
and in a *single* command.

The entry-point script is called ``wltp.py``, and it must have been placed in your ``PATH``
during installation.  This script can construct a *model* by reading input-data
from multiple files and/or overriding specific single-value items. Conversely,
it can output multiple parts of the resulting-model into files.

To get help for this script, use the following commands:

.. code-block:: console

    $ wltp.py --help          ## to get generic help for cmd-line syntax
    $ wltp.py -M /vehicle     ## to get help for specific model-paths


and then, assuming ``vehicle.csv`` is a CSV file with the vehicle parameters
for which you want to override the ``n_idle`` only, run the following:

.. code-block:: console

    $ wltp.py -v \
        -I vehicle.csv file_frmt=SERIES model_path=/params header@=None \
        -m /vehicle/n_idle:=850 \
        -O cycle.csv model_path=/cycle_run





IPython usage
-------------
.. Note:: Not implemented in yet.




.. _begin_contribute:

Getting Involved
================
To provide feedback, use `github's Issue-tracker <https://github.com/ankostis/wltp/issues>`_.

.. Tip::
    The console-commands listed in the following sections are for a *POSIX* environments
    (*Linux* & *OS X*). They are simple enough and easy to translate into their *Windows* counterparts,
    but it would be worthwile to install `cygwin <https://www.cygwin.com/>`_ to get
    the same environment on *Windows* machines.

    In the cygwin's installation wizard, make sure that the following packages are also included::

        * git
        * make
        * openssh
        * curl
        * wget



Sources & Dependent libraries
-----------------------------
To get involved with development, first you need to download the latest sources:

.. code-block:: console

    $ git clone https://github.com/ankostis/wltp.git wltp.git
    $ cd wltp.git


Then you can install all project's dependencies using the ``setup.py`` script:

.. code-block:: console

    $ python3 setup.py --help                           ## Get help for this script.
    Common commands: (see '--help-commands' for more)

      setup.py build      will build the package underneath 'build/'
      setup.py install    will install the package

    Global options:
    ...

    $ python3 setup.py develop                          ## Install dependencies into project's folder.


The dependencies installed with the last command, above, will only be available when running
build-commands through the ``setup.py`` script or the ``pip`` command.  If you need to install
the project's dependencies for all python sessions and IDEs such as `LiClipse <https://brainwy.github.io/liclipse/>`_,
it is preferable that you install them
in a `virtual-environment <http://docs.python-guide.org/en/latest/dev/virtualenvs/>`_:

.. code-block:: console

    $ pip3 install virtualenv                           ## Ensure `virtualenv` is installed.
    $ virtualenv --system-site-packages ../wltp.venv    ## If both python-2 & 3 installed, use:  -p <PATH_TO_PYTHON_3>
    $ .  ../wltp.venv/bin/activate                      ## To deactivate virtual-environment type: deactivate
    $ python setup.py install                           ## Install dependencies into the virtual-environment.


You should now run the test-cases (see :ref:`begin_test_cases`, below) to check that the sources are in good shape:

.. code-block:: console

   $ python setup.py test                               ## or: python setup.py nosetests



Development procedure
---------------------
The typical development procedure is like this:

1. Modify the sources in small, isolated and well-defined changes, i.e.
   adding a single feature, or fixing a specific bug.
2. Add test-cases "proving" your code.
3. Rerun all test-cases to ensure that you didn't break anything,
   and check their *coverage* remain above 80%:

.. code-block:: console

    $ python setup.py nosetests --with-coverage --cover-package wltp.model,wltp.experiment --cover-min-percentage=80


4. If you made a rather important modification, update also the :doc:`CHANGES` file and/or
   other documents (i.e. README.rst).  To see the rendered results of the documents,
   issue the following commands and read the result html-file at ``build/sphinx/html/index.html``:

.. code-block:: console

    $ python setup.py build_sphinx                  # Builds html docs
    $ python setup.py build_sphinx -b doctest       # Checks if python-code embeded in comments runs ok.


5. If there are no problems, commit your changes with a descriptive message.

6. Repeat this cycle for other bugs/enhancements.
7. When you are finished, push the changes upstream to *github* and make a *merge_request*.
   You can check whether your merge-request indeed passed the tests by checking
   its build-status |build-status| on the integration-server's site (TravisCI).

    .. Tip:: Skim through the small IPython developer'ss documentantion on the matter:
        `The perfect pull request <https://github.com/ipython/ipython/wiki/Dev:-The-perfect-pull-request>`_



.. _begin_test_cases:

Tests & Metrics
---------------
In order to maintain the algorithm stable, a lot of effort has been put
to setup a series of test-case and metrics to check the sanity of the results
and to compare them with the Heinz-db tool or other datasets.
These tests can be found in the ``wltp/test`` folders.
Code for generating diagrams for the metrics below are located
in the ``docs/pyplot/`` folder.

.. plot:: pyplots/avg_p__pmr.py
   :include-source:




Specs & Algorithm
-----------------
This program was implemented from scratch based on
this :download:`GTR specification <23.10.2013 ECE-TRANS-WP29-GRPE-2013-13 0930.docx>`
(included in the ``docs/`` dir).  The latest version of this :term:`GTR`, along
with other related documents can be found at UNECE's site:

* http://www.unece.org/trans/main/wp29/wp29wgs/wp29grpe/grpedoc_2013.html
* https://www2.unece.org/wiki/pages/viewpage.action?pageId=2523179
* Probably a more comprehensible but older spec is this one:
  https://www2.unece.org/wiki/display/trans/DHC+draft+technical+report

The WLTC-profiles for the various classes in the ``./util/data/cycles`` folder were generated from the tables
of the specs above using the ``./util/csvcolumns8to2`` script, but it still requires
an intermediate manual step involving a spreadsheet to copy the table into ands save them as CSV.

Then use the :mod:`./util/buildwltcclass.py` to contruct the respective python-vars into the
:mod:`wltp/model.py` sources.


Data-files generated from Steven Heinz's ms-access ``vehicle info`` db-table can be processed
with the  ``/util/preprocheinz.py`` script.


Cycles
^^^^^^

.. figure:: docs/wltc_class1.png
    :align: center
.. figure:: docs/wltc_class2.png
    :align: center
.. figure:: docs/wltc_class3a.png
    :align: center
.. figure:: docs/wltc_class3b.png
    :align: center

.. Seealso:: :doc:`CHANGES`



Development team
----------------

* Author:
    * Kostis Anagnostopoulos
* Contributing Authors:
    * Heinz Steven (test-data, validation and review)
    * Georgios Fontaras (simulation, physics & engineering support)
    * Alessandro Marotta (policy support)



.. _begin_glossary:

Glossary
========
.. glossary::

    WLTP
        The `Worldwide harmonised Light duty vehicles Test Procedure <https://www2.unece.org/wiki/pages/viewpage.action?pageId=2523179>`_,
        a :term:`GRPE` informal working group

    UNECE
        The United Nations Economic Commission for Europe, which has assumed the steering role
        on the :term:`WLTP`.

    GRPE
        UNECE Working party on Pollution and Energy – Transport Programme

    GTR
        Global Technical Regulation

    WLTC
        The family of the 3 pre-defined *driving-cycles* to use for each vehicle depending on its
        :term:`PMR`. Classes 1,2 & 3 are split in 2, 4 and 4 *parts* respectively.

    PMR
        The ``rated_power / unladen_mass`` of the vehicle

    Unladen mass
        *UM* or *Curb weight*, the weight of the vehicle in running order minus
        the mass of the driver.

    Test mass
        *TM*, the representative weight of the vehicle used as input for the calculations of the simulation,
        derived by interpolating between high and low values for the |CO2|-family of the vehicle.

    Downscaling
        Reduction of the top-velocity of the original drive trace to be followed, to ensure that the vehicle
        is not driven in an unduly high proportion of "full throttle".


.. _begin_replacements:

.. |CO2| replace:: CO\ :sub:`2`

.. |build-status| image:: https://travis-ci.org/ankostis/wltp.svg?branch=master
    :alt: Integration-build status
    :scale: 100%
    :target: https://travis-ci.org/ankostis/wltp/builds

.. |cover-status| image:: https://coveralls.io/repos/ankostis/wltp/badge.png?branch=master
        :target: https://coveralls.io/r/ankostis/wltp?branch=master

.. |docs-status| image:: https://readthedocs.org/projects/wltp/badge/
    :alt: Documentation status
    :scale: 100%
    :target: https://readthedocs.org/builds/wltp/

.. |pypi-status| image::  https://pypip.in/v/wltp/badge.png
    :target: https://pypi.python.org/pypi/wltp/
    :alt: Latest Version in PyPI

.. |python-ver| image:: https://pypip.in/py_versions/wltp/badge.svg
    :target: https://pypi.python.org/pypi/wltp/
    :alt: Supported Python versions

.. |dev-status| image:: https://pypip.in/status/wltp/badge.svg
    :target: https://pypi.python.org/pypi/wltp/
    :alt: Development Status

.. |downloads_count| image:: https://pypip.in/download/wltp/badge.svg?period=week
    :target: https://pypi.python.org/pypi/wltp/
    :alt: Downloads
