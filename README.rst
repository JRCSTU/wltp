===============================
*wltp* gear-shifts calculator
===============================

|dev-status| |build-status| |cover-status| |docs-status| |pypi-status| |downloads-count| |github-issues|

:Version:       |version|
:Home:          https://github.com/ankostis/wltp
:Documentation: https://wltp.readthedocs.org/
:PyPI:          https://pypi.python.org/pypi/wltp
:Copyright:     2013-2014 European Commission (`JRC-IET <http://iet.jrc.ec.europa.eu/>`_)
:License:       `EUPL 1.1+ <https://joinup.ec.europa.eu/software/page/eupl>`_

Calculates the *gear-shifts* of Light-duty vehicles running the :term:`WLTP`
driving-cycles, according to :term:`UNECE`'s :abbr:`GTR (Global Technical Regulation)` draft.

.. figure:: docs/wltc_class3b.png
    :align: center

    **Figure 1:** *WLTP cycle for class-3b Vehicles*


.. Attention:: This project is still in *alpha* stage.  Its results are not
    considered "correct", and official approval procedures should not rely on them.
    Some of the known deficiencies are described in :doc:`CHANGES`.
    Its result are automatically comparared with those from Heinz-db in each build, and are imprinted
    in the :mod:`~wltp.test.wltp_db_tests` test-case
    (currently, mean rpm differ from Heinz-db < 1.3% and gears diff < 6% for a 1800-step class-3 cycle).



.. _begin-intro:

Introduction
============

The calculator accepts as input the vehicle's technical data, along with parameters for modifying the execution
of the :term:`WLTC` cycle, and it then spits-out the gear-shifts of the vehicle, the attained speed-profile,
and any warnings.  It does not calculate any |CO2| emissions.


An "execution" or a "run" of an experiment is depicted in the following diagram::

         ---------------    ________________         ------------------
        ;  inp-model  ;    |   Experiment   |       ;   out-model    ;
       ;-------------;     |________________|      ;----------------;
      ; +--vehicle  ;  ==> |  ------------- | ==> ; +...           ;
     ;  +--params  ;       | ; WLTC-data ;  |    ;  +--cycle_run  ;
    ;             ;        | ------------   |   ;                ;
    --------------         |________________|   -----------------



.. _wltp_install:

Install
-------
Requires Python 3.3+.

.. Tip:: To install *python*, you can try `WinPython <http://winpython.sourceforge.net/>`_ distribution
    for Windows*, or `Anaconda <http://docs.continuum.io/anaconda/pkg-docs.html>`_
    for *Windows* and *OS X*.

    The most recent version of *WinPython* (python-3.3.5)* has recently
    `change maintainer <http://sourceforge.net/projects/stonebig.u/files/Winpython_3.4/>`_ but it remains
    a higly active project.


You can install (or upgrade) the project directly from the `PyPI <https://pypi.python.org/pypi>`_ repository
with :command:`pip`.
Notice that :option:`--pre` is required, since all realeased packages so far were *pre*-release (``-alpha``) versions:

.. code-block:: console

    $ pip install wltp --pre -U                 ## Use `pip3` if both python-2 & 3 installed.
    $ wltp.py --version                         ## Check which version installed.
    wltp.py 0.0.9-alpha


.. Tip::
    The console-commands that are listed here to begin with ``$`` are for a *POSIX* environment
    (*Linux*, *OS X*). They are simple enough and easy to translate into their *Windows* ``cmd.exe``
    counterparts, but it would be worthwile to install `cygwin <https://www.cygwin.com/>`_ to get
    the same environment on *Windows* machines.

    If you choose to do that, make sure that in the *cygwin*'s installation wizard the following packages
    are also included::

        * git
        * make
        * openssh
        * curl
        * wget


Alternatively you can build the latest version from the sources,
(assuming you have a working installation of `git <http://git-scm.com/>`_)
and install it in `development mode <http://pythonhosted.org/setuptools/setuptools.html#development-mode>`_
with the following series of commands:

.. code-block:: console

    $ git clone "https://github.com/ankostis/wltp.git" wltp.git
    $ cd wltp.git
    $ python setup.py develop                   ## Use `python3` if you have installed both python-2 & 3.


That way you get the complete source-tree of the project, ready for development
(see :doc:`contribute` section, below)::

    +--wltp/            ## (package) The python-code of the calculator
    |   +--cycles/      ## (package) The python-code for the WLTC data
    |   +--test/        ## (package) Test-cases and the wltp_db
    |   +--model        ## (module) Describes the data for the calculation
    |   +--experiment   ## (module) The calculator
    +--docs/            ## Documentation folder
    +--devtools/        ## Scripts for preprocessing WLTC data and the wltp_db
    +--wltp.py          ## (script) The cmd-line entry-point script for the calculator
    +--README.rst
    +--CHANGES.rst
    +--LICENSE.txt




Python usage
------------
Here is a quick-start python :abbr:`REPL (Read-Eval-Print Loop)`-example to setup and run
an *experiment*.  First run :command:`python` and try to import the project to check its version:

.. doctest::

    >>> import wltp

    >>> wltp.__version__
    '0.0.9-alpha'

    >>> wltp.__file__               ## To check where it was installed.         # doctest: +SKIP
    /usr/local/lib/site-package/wltp-...


.. Tip::
    You can copy the the python commands starting with ``>>>`` and ``...`` and copy paste them directly
    into the python interpreter; it will remove these prefixes.

If everything works, create the :term:`pandas-model` that will hold the input-data (strings and numbers)
of the experiment.  You can assemble the model-tree by the use of:

* sequences,
* dictionaries,
* :class:`pandas.DataFrame`,
* :class:`pandas.Series`, and
* URI-references to other model-trees.


For instance:

.. doctest::

    >>> from wltp import model
    >>> from wltp.experiment import Experiment
    >>> from collections import OrderedDict as odic         ## It is handy to preserve keys-order.

    >>> mdl = odic(
    ...   vehicle = odic(
    ...     unladen_mass = 1430,
    ...     test_mass    = 1500,
    ...     v_max        = 195,
    ...     p_rated      = 100,
    ...     n_rated      = 5450,
    ...     n_idle       = 950,
    ...     n_min        = None,                            ## Manufacturers my overridde it
    ...     gear_ratios         = [120.5, 75, 50, 43, 37, 32],
    ...     resistance_coeffs   = [100, 0.5, 0.04],
    ...   )
    ... )


For information on the accepted model-data, check its :term:`JSON-schema`:

.. doctest::

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


You then have to feed this model-tree to the :class:`~wltp.experiment.Experiment`
constructor. Internally the :class:`~wltp.pandel.Pandel` resolves URIs, fills-in default values and
validates the data based on the project's pre-defined JSON-schema:

.. doctest::

    >>> processor = Experiment(mdl)         ## Fills-in defaults and Validates model.


Assuming validation passes without errors, you can now inspect the defaulted-model
before running the experiment:

.. doctest::

    >>> mdl = processor.model()             ## Returns the validated model with filled-in defaults.
    >>> sorted(mdl)                         ## The "defaulted" model now includes the `params` branch.
    ['params', 'vehicle']
    >>> 'full_load_curve' in mdl['vehicle'] ## A default wot was also provided in the `vehicle`.
    True


Now you can run the experiment:

.. doctest::

    >>> mdl = processor.run()               ## Runs experiment and augments the model with results.
    >>> sorted(mdl)                         ## Print the top-branches of the "augmented" model.
    ['cycle_run', 'params', 'vehicle']


To access the time-based cycle-results it is better to use a :class:`pandas.DataFrame`:

.. doctest::

    >>> import pandas as pd
    >>> df = pd.DataFrame(mdl['cycle_run']); df.index.name = 't'
    >>> print(df.shape)                 ## ROWS(time-steps) X COLUMNS.
    (1801, 11)
    >>> df.columns
    Index(['v_class', 'v_target', 'clutch', 'gears_orig', 'gears', 'v_real', 'p_available', 'p_required', 'rpm', 'rpm_norm', 'driveability'], dtype='object')
    >>> print('Mean engine_speed: ', df.rpm.mean())
    Mean engine_speed:  1917.0407829
    >>> print(df.describe())
               v_class     v_target     clutch   gears_orig        gears  \
    count  1801.000000  1801.000000       1801  1801.000000  1801.000000
    mean     46.506718    46.506718  0.0660744     3.794003     3.683509
    std      36.119280    36.119280  0.2484811     2.278959     2.278108
    ...
    <BLANKLINE>
                v_real  p_available   p_required          rpm     rpm_norm
    count  1801.000000  1801.000000  1801.000000  1801.000000  1801.000000
    mean     50.356222    28.846639     4.991915  1917.040783     0.214898
    std      32.336908    15.833262    12.139823   878.139758     0.195142
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

.. code-block:: pycon

    >>> df.to_csv('cycle_run.csv')                                                      # doctest: +SKIP


For more examples, download the sources and check the test-cases
found under the :file:`/wltp/test/` folder.



Cmd-line usage
--------------
.. Note:: Not implemented in yet.

The examples presented so far required to execute multiple commands interactively inside
the Python interpreter (REPL).
The comand-line usage below still requires the Python environment to be installed, but provides for
executing an experiment directly from the OS's shell (i.e. :program:`cmd` in windows or :program:`bash` in POSIX),
and in a *single* command.

The entry-point script is called :program:`wltp.py`, and it must have been placed in your :envvar:`PATH`
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





IPython notebook usage
----------------------
The list of *IPython notebooks* for wltp is maintained at the `wiki <https://github.com/ankostis/wltp/wiki>`_
of the project.

Requirements
^^^^^^^^^^^^
In order to run them interactively, ensure that the following requirements are satisfied:

a. A `ipython-notebook server <http://ipython.org/notebook.html>`_ >= v2.x.x is installed, up and running.
b. The *wltp* is installed on your *python-3* of your system (see `wltp_install`_ above).

Instructions
^^^^^^^^^^^^
* Visit each *notebook* from the wiki-list that you wish to run and **download** it as :file:`ipynb` file
  from the menu (:menuselection:`File|Download as...|IPython Notebook(.ipynb)`).
* Locate the downloaded file with your *file-browser* and **drag n' drop** it on the landing page
  of your notebook's server (the one with the folder-list).


Enjoy!


.. _begin-contribute:

Getting Involved
================
This project is hosted in **github**.
To provide feedback about bugs and errors or questions and requests for enhancements,
use `github's Issue-tracker <https://github.com/ankostis/wltp/issues>`_.



Sources & Dependencies
----------------------
To get involved with development, first you need to download the latest sources:

.. code-block:: console

    $ git clone https://github.com/ankostis/wltp.git wltp.git
    $ cd wltp.git


.. Admonition:: Virtualenv & Liclipse IDE
    :class: note

    You may choose to work in a `virtual-environment <http://docs.python-guide.org/en/latest/dev/virtualenvs/>`_,
    to install dependency libraries isolated from system's ones, and/or without *admin-rights*
    (recommended for *Linux*/*Mac OS*).

    .. Attention::
        If you decide to reuse stystem-installed packages using  :option:`--system-site-packages`
        with ``virtualenv <= 1.11.6``
        (to avoid, for instance, having to reinstall *numpy* and *pandas* that require native-libraries)
        you may be bitten by `bug #461 <https://github.com/pypa/virtualenv/issues/461>`_ which
        prevents you from upgrading any of the pre-installed packages with :command:`pip`.

    Within the sources it is included a :file:`.project` file for the comprehensive
    `LiClipse <https://brainwy.github.io/liclipse/>`_, an **eclipse** IDE pre-configured with the
    excellent **PyDev** environment.  If you also choose to use it, you have to add a new PyDev python-intepreter
    under :menuselection:`&Windows --> &Preferences --> PyDev --> Interpreters --> Python Interpreter`
    named ``wltp.venv``, since this is the name already specified in the :file:`.project`.
    You may change this name by :guilabel:`Right-clicking` on the Project and navigating
    to :menuselection:`Properties --> PyDev - Interpreter/Grammar --> Interpreter`,
    but you have to remember not commit this change in :file:`.project`.


Then you can install all project's dependencies in *`development mode* using the :file:`setup.py` script:

.. code-block:: console

    $ python setup.py --help                           ## Get help for this script.
    Common commands: (see '--help-commands' for more)

      setup.py build      will build the package underneath 'build/'
      setup.py install    will install the package

    Global options:
      --verbose (-v)      run verbosely (default)
      --quiet (-q)        run quietly (turns verbosity off)
      --dry-run (-n)      don't actually do anything
    ...

    $ python setup.py develop                           ## Also installs dependencies into project's folder.
    $ python setup.py build                             ## Check that the project indeed builds ok.


You should now run the test-cases (see `Tests & Metrics`_, below) to check
that the sources are in good shape:

.. code-block:: console

   $ python setup.py test


.. Note:: The above commands installed the dependencies inside the project folder and
    for the *virtual-environment*.  That is why all build and testing actions have to go through
    :samp:`python setup.py {some_cmd}`.

    If you are dealing with installation problems and/or you want to permantly install dependant packages,
    you have to *deactivate* the virtual-environment and start installing them into your *base*
    python environment:

    .. code-block:: console

       $ deactivate
       $ python setup.py develop

    or even try the more *permanent* installation-mode:

    .. code-block:: console

       $ python setup.py install                # May require admin-rights



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


    .. Tip:: You can enter just: ``python setup.py test_all`` instead of the above cmd-line
        since it has been *aliased* in the :file:`setup.cfg` file.
        Check this file for more example commands to use during development.


4. If you made a rather important modification, update also the :doc:`CHANGES` file and/or
   other documents (i.e. README.rst).  To see the rendered results of the documents,
   issue the following commands and read the result html at :file:`build/sphinx/html/index.html`:

    .. code-block:: console

        $ python setup.py build_sphinx                  # Builds html docs
        $ python setup.py build_sphinx -b doctest       # Checks if python-code embeded in comments runs ok.


5. If there are no problems, commit your changes with a descriptive message.

6. Repeat this cycle for other bugs/enhancements.
7. When you are finished, push the changes upstream to *github* and make a *merge_request*.
   You can check whether your merge-request indeed passed the tests by checking
   its build-status |build-status| on the integration-server's site (TravisCI).

    .. Hint:: Skim through the small IPython developer's documentantion on the matter:
        `The perfect pull request <https://github.com/ipython/ipython/wiki/Dev:-The-perfect-pull-request>`_



Tests & Metrics
---------------
In order to maintain the algorithm stable, a lot of effort has been put
to setup a series of test-case and metrics to check the sanity of the results
and to compare them with the Heinz-db tool or other datasets.
These tests can be found in the :file:`wltp/test/` folders.
Code for generating diagrams for the metrics below are located
in the :file:`docs/pyplot/` folder.

.. plot:: pyplots/avg_p__pmr.py
   :include-source:




Specs & Algorithm
-----------------
This program was implemented from scratch based on
this :download:`GTR specification <23.10.2013 ECE-TRANS-WP29-GRPE-2013-13 0930.docx>`
(included in the :file:`docs/` folder).  The latest version of this GTR, along
with other related documents can be found at UNECE's site:

* http://www.unece.org/trans/main/wp29/wp29wgs/wp29grpe/grpedoc_2013.html
* https://www2.unece.org/wiki/pages/viewpage.action?pageId=2523179
* Probably a more comprehensible but older spec is this one:
  https://www2.unece.org/wiki/display/trans/DHC+draft+technical+report

The WLTC-profiles for the various classes in the :file:`devtools/data/cycles/` folder were generated from the tables
of the specs above using the :file:`devtools/csvcolumns8to2.py` script, but it still requires
an intermediate manual step involving a spreadsheet to copy the table into ands save them as CSV.

Then use the :file:`devtools/buildwltcclass.py` to contruct the respective python-vars into the
:mod:`wltp/model.py` sources.


Data-files generated from Steven Heinz's ms-access ``vehicle info`` db-table can be processed
with the  :file:`devtools/preprocheinz.py` script.


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


.. _dev-team:

Development team
----------------

* Author:
    * Kostis Anagnostopoulos
* Contributing Authors:
    * Heinz Steven (test-data, validation and review)
    * Georgios Fontaras (simulation, physics & engineering support)
    * Alessandro Marotta (policy support)



.. _begin-glossary:

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
        :term:`UNECE` Working party on Pollution and Energy - Transport Programme

    GS Task-Force
        The Gear-shift Task-force of the :term:`GRPE`. It is the team of automotive experts drafting
        the gear-shifting strategy for vehicles running the :term:`WLTP` cycles.

    WLTC
        The family of pre-defined *driving-cycles* corresponding to vehicles with different
        :abbr:`PMR (Power to Mass Ratio)`. Classes 1,2, 3a & 3b are split in 2, 4, 4 and 4 *parts* respectively.

    Unladen mass
        *UM* or *Curb weight*, the weight of the vehicle in running order minus
        the mass of the driver.

    Test mass
        *TM*, the representative weight of the vehicle used as input for the calculations of the simulation,
        derived by interpolating between high and low values for the |CO2|-family of the vehicle.

    Downscaling
        Reduction of the top-velocity of the original drive trace to be followed, to ensure that the vehicle
        is not driven in an unduly high proportion of "full throttle".

    pandas-model
        The *container* of data that the gear-shift calculator consumes and produces.
        It is implemented by :class:`wltp.pandel.Pandel` as a mergeable stack of :term:`JSON-schema` abiding trees of
        strings and numbers, formed with sequences, dictionaries, :mod:`pandas`-instances and URI-references.

    JSON-schema
        The `JSON schema <http://json-schema.org/>`_ is an `IETF draft <http://tools.ietf.org/html/draft-zyp-json-schema-03>`_
        that provides a *contract* for what JSON-data is required for a given application and how to interact
        with it.  JSON Schema is intended to define validation, documentation, hyperlink navigation, and
        interaction control of JSON data.
        You can learn more about it from this `excellent guide <http://spacetelescope.github.io/understanding-json-schema/>`_,
        and experiment with this `on-line validator <http://www.jsonschema.net/>`_.

    JSON-pointer
        JSON Pointer(:rfc:`6901`) defines a string syntax for identifying a specific value within
        a JavaScript Object Notation (JSON) document. It aims to serve the same purpose as *XPath* from the XML world,
        but it is much simpler.



.. _begin-replacements:

.. |CO2| replace:: CO\ :sub:`2`

.. |build-status| image:: https://travis-ci.org/ankostis/wltp.svg
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

.. |downloads-count| image:: https://pypip.in/download/wltp/badge.svg?period=week
    :target: https://pypi.python.org/pypi/wltp/
    :alt: Downloads

.. |github-issues| image:: http://img.shields.io/github/issues/ankostis/wltp.svg
    :target: https://github.com/ankostis/wltp/issues
    :alt: Issues count
