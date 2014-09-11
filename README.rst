#####################################
wltp: A *wltc* gear-shifts calculator
#####################################
:Version:       |version|
:Home:          https://github.com/ankostis/wltp
:Documentation: https://wltp.readthedocs.org/
:PyPI:          https://pypi.python.org/pypi/wltp
:TravisCI:      https://travis-ci.org/ankostis/wltp
:Copyright:     2013-2014 European Commission (`JRC-IET <http://iet.jrc.ec.europa.eu/>`_)
:License:       `EUPL 1.1+ <https://joinup.ec.europa.eu/software/page/eupl>`_


A calculator of the gear-shifts profile for light-duty-vehicles (cars)
according to :term:`UNECE` draft of the :term:`WLTP`.

.. figure:: docs/wltc_class3b.png
    :align: center

    **Figure 1:** *WLTP cycle for class-3b Vehicles*


.. important:: This project is still in *alpha* stage.  Its results are not
    considered "correct", and no approval procedure should rely on them.
    Some of the known deficiencies are described in :doc:`CHANGES`.



.. @begin-intro

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
with :command:`pip`.
Notice that :option:`--pre` is required, since all realeased packages so far were *pre*-release (``-alpha``) versions:

    $ pip3 install wltp

Or you can build it from the latest sources
(assuming you have a working installation of `git <http://git-scm.com/>`_)::

    $ git clone https://github.com/ankostis/wltp.git wltp
    $ cd wltp
    $ python3 setup.py install .

That way you get the complete source-tree of the project::

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
Here is a quick-start example:

.. code-block:: pycon

    >>> from wltp import model
    >>> from wltp.experiment import Experiment
    >>> import json                  ## Just for pretty-printing model

    >>> mdl = {
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

    >>> processor = Experiment(mdl)
    >>> mdl = processor.run()
    >>> print(json.dumps(mdl['params'], indent=2))
    {
      "f_n_min_gear2": 0.9,
      "v_stopped_threshold": 1,
      "wltc_class": "class3b",
      "f_n_min": 0.125,
      "f_n_max": 1.2,
      "f_downscale": 0,
      "f_inertial": 1.1,
      "f_n_clutch_gear2": [
        1.15,
        0.03
      ],
      "f_safety_margin": 0.9
    }


To access the time-based cycle-results it is better to use a :class:`pandas.DataFrame`:

.. code-block:: pycon

    >>> import pandas as pd
    >>> df = pd.DataFrame(mdl['cycle_run'])
    >>> df.columns
    Index(['clutch', 'driveability', 'gears', 'gears_orig', 'p_available', 'p_required', 'rpm', 'rpm_norm', 'v_class', 'v_real', 'v_target'], dtype='object')
    >>> df.index.name = 't'
    >>> print('Mean engine_speed: ', df.rpm.mean())
    Mean engine_speed:  1917.0407829

    >>> print(df.head())
      clutch driveability  gears  gears_orig  p_available  p_required  rpm  \
    t
    0  False                   0           0            9           0  950
    1  False                   0           0            9           0  950
    2  False                   0           0            9           0  950
    3  False                   0           0            9           0  950
    4  False                   0           0            9           0  950

       rpm_norm  v_class   v_real  v_target
    t
    0         0        0  29.6875         0
    1         0        0  29.6875         0
    2         0        0  29.6875         0
    3         0        0  29.6875         0
    4         0        0  29.6875         0

    [5 rows x 11 columns]

    >>> print(processor.driveability_report())
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


For information on the model-data, check the schema:

.. code-block:: pycon

    >>> print(json.dumps(model.model_schema(), indent=2))
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

To get help::

    $ python wltp --help          ## to get generic help for cmd-line syntax
    $ python wltp -M /vehicle     ## to get help for specific model-paths


and then, assuming ``vehicle.csv`` is a CSV file with the vehicle parameters
for which you want to override the ``n_idle`` only, run the following::

    $ python wltp -v \
        -I vehicle.csv file_frmt=SERIES model_path=/params header@=None \
        -m /vehicle/n_idle:=850 \
        -O cycle.csv model_path=/cycle_run





IPython usage
-------------
.. Note:: Not implemented in yet.




.. @begin-contribute

Getting Involved
================
To provide feedback, use `github's Issue-tracker <https://github.com/ankostis/wltp/issues>`_.


Development
-----------
.. Tip::
    The commands below are given for a *POSIX* environment (*Linux* & *OS X*).  
    They are simple enough and easy to translate into their *Windows* counterparts, 
    but it would be worthwile to install `cygwin <https://www.cygwin.com/>`_ to get 
    the same environment on *Windows*.

To get involved with development, first you need to download the latest sources::

    $ git clone https://github.com/ankostis/wltp.git wltp
    $ cd wltp

It is preferable that you work from within a `virtual-environment <http://docs.python-guide.org/en/latest/dev/virtualenvs/>`_.  Assuming that you have installed ``virtualenv`` you can then type the following::

    $ virtualenv -p <PATH_TO_PYTHON_3> ../wltp.venv
    $ .  ../wltp.venv/bin/activate
    $ python setup.py develop .


Check that the sources are in good shape by running the test-cases and check for errors::

   $ python setup.py test 


You can now modify the sources and rerun the tests to ensure that you didn't break anything.
If there are no problems, commit them with a usefull message.
Split the functionality you want to implement in small well-defined commits, 
and provide test-cases.
If you made a rather important modification, update also the :doc:`CHANGES` file and/or 
other documents.  To see the rendered results of the documents, issue the following command
and check the result html file at ``build/sphinx/html/index.html``::

    $ python setup.py build_sphinx


When you are finished, push the changes upstream to github and make a *merge_request*.
You can check whether your merge-request passed the tests by checking the status of the 
`TravisCI <https://travis-ci.org/ankostis/wltp>`_  integration-server. 

.. Tip:: Skim through the small and excellent IPython developers document:
    `The perfect pull request <https://github.com/ipython/ipython/wiki/Dev:-The-perfect-pull-request>`_




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



.. @begin-glossary

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

.. |CO2| replace:: CO\ :sub:`2`
