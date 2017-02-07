..    include:: <isonum.txt>

#######
Changes
#######

.. contents::


.. _gtr_ver_matrix:

GTR version matrix
==================
Given a version number ``MAJOR.MINOR.PATCH``, the ``MAJOR`` part tracks the GTR phase implemented.
The following matrix shows these correspondences:

+---------+-----------------------------+
| Release |           GTR ver           |
| train   |                             |
+=========+=============================+
| 0.0.9   | Un-precise GTR phase-1a     |
|         | (diffs explained below)     |
+---------+-----------------------------+
| 0.1.x   | GTR phase-1a                |
|         | (TODO)                      |
+---------+-----------------------------+
| 1.x.x   | GTR phase 1b [TDB]          |
+---------+-----------------------------+


Known deficiencies
==================
* (!) Driveability-rules not ordered as defined in the latest task-force meeting.
* (!) The driveability-rules when speeding down to a halt is broken, and human-drivers should improvise.
* (!) The ``n_min_drive`` is not calculated as defined in the latest task-force meeting,
  along with other recent updates.
* (!) The ``n_max`` is calculated for ALL GEARS, resulting in "clipped" velocity-profiles,
  leading to reduced rpm's for low-powered vehicles.
* Clutching-points and therefore engine-speed are very preliminary
  (ie ``rpm`` when starting from stop might be < ``n_idle``).

.. _todos-list:

TODOs
=====
* Add cmd-line and UI front-ends.
* Use a model-explorer to autocomplete excel-cells.
* Automatically calculate masses from H & L vehicles, and regression-curves from categories.
* wltp_db: Improve test-metrics with group-by classes/phases.
* model: Enhance model-preprocessing by interleaving "octapus" merging stacked-models
  between validation stages.
* model: finalize data-schema (renaming columns and adding ``name`` fields in major blocks).
* model/core: Accept units on all quantities.
* core: Move calculations as class-methods to provide for overriding certain parts of the algorithm.
* core: Support to provide and override arbitrary model-data, and ask for arbitrary output-ones
  by topologically sorting the  graphs of the calculation-dependencies.
* build: Separate wltpdb tests as a separate, optional, plugin of this project (~650Mb size).

.. todolist::


Changelog
=========

v0.0.9-alpha.5 (7-Feb-2017)
----------------------------
- DELETE Wltp-DB files to light-weight wheels.
- Just unpin `xlwings=0.2.3`.


v0.0.9-alpha.4 (5-Oct-2015)
----------------------------
Same algo as `alpha.3` but with corrected engine-speed for idle.
It is used for reports and simulation run by JRC to build the CO\ :sub:`2`\MPAS model,
but still not driveable due to downshifting to 1st-gear when stopping to standstill.

* core, model: Possible to define different `n_min_drive` & `f_safety_margins` per gear.
* core: Add function to identify gear-ratios from experimental engine-runs.
* excel, tests: Add ExcelRunner TCs.
* Updated ``jonschema`` dep 2.5.0.


v0.0.9-alpha.3 (1-Dec-2014)
---------------------------
This is practically the 1st public releases, reworked in many parts, much better documented,
continuously tested and build using TravisCI, with on-the-fly generated diagrams as metrics,
BUT the arithmetic results produced are still identical to v0.0.7, so that the test-cases and
metrics still describe that version, for future comparison.

* Use CONDA for running on TravisCI.
* Improve ExcelRunner.
* docs and metrics improvements.
* ui: Added Excel frontend.
* ui: Added desktop-UI proof-of-concept (:class:`wltp.tkui`).
* metrics: Add diagrams auto-generated from test-metrics into generated site (at "Getting Involved" section).

Noteworthy or *incompatilble* changes
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
* Code:
    * package ``wltc``  --> ``wltp``
    * class ``Experiment``    --> ``Processor``
* Model changes:
    * ``/vehicle/mass`` --> (``test_mass`` and ``unladen_mass``)
    * ``/cycle_run``: If present, (some of) its columns override the calculation.
* Added Excel front-end.
* Added *Metrics* section in documents whith on-the-fly generated diagrams comparing and tracking
  the behavior of the algorithm.
* Now the Eclipse's PyDev-project files are included only as templates; copy them and
  remove the `eclipse` prefix before importing project into Eclipse/Liclipse.



v0.0.9-alpha.1 (1-Oct-2014)
---------------------------
* Backported also to Python-2.7.
* model, core: Discriminate between :term:`Test mass` from :term:`Unladen mass`
  (optionally auto-calced by ``driver_mass`` = 75(kg)).
* model, core: Calculate default resistance-coefficients from a regression-curve (the one found in Heinz-db).
* model, core: Possible to overide WLTP-Class, Target-V & Slope, Gears if present in the ``cycle_run`` table.
* model: Add NEDC cycle data, for facilitating comparisons.
* tests: Include sample-vehicles along with the distribution.
* tests: Speed-up tests by caching files to read and compare.
* docs: Considerable improvements, validate code in comments and docs with *doctest*.
* docs: Provide a http-link to the list of IPython front-ends in the project's wiki.
* build: Use TravisCI as integration server, Coveralls.io as test-coverage service-providers.
* build: Stopped .EXE distribution; need a proper python environment.



v0.0.8-alpha(04-Aug-2014), v0.0.8.alpha.2(1-Dec-2014)
-----------------------------------------------------
* Documentation fixes.


v0.0.7-alpha, 31-Jul-2014: 1st *internal*
-----------------------------------------
Although it has already been used in various exercises internally in JRC,
it never graduated out of *Alpha* state.

* Rename project to 'wltp'.
* Switch license from AGPL --> EUPL (the same license assumed *retrospectively* for older version)
* Add wltp_db files.
* Unify instances & schemas in ``model.py``.
* Possible to Build as standalone `.exe` using `cx_freeze`.
* Preparations for PyPI/github distribution.
    * Rename project to "wltp".
    * Prepare Sphinx documentation for http://readthedocs.org.
    * Update setup.py
    * Update project-coordinates (authors, etc)



v0.0.6-alpha, 5-Feb-2014
------------------------
* Make it build as standalone `.exe` using `cx_freeze`.
* Possible to transplant base-gears and then apply on them driveability-rules.
* Embed Model --> Experiment to simplify client-code.
* Changes in the data-schema for facilitating conditional runs.
* More reverse-engineered comparisons with heinz's data.


v0.0.5-alpha, 18-Feb-2014
-------------------------
* Many driveability-improvements found by trial-n-error comparing with Heinz's.
* Changes in the data-schema for facilitating storing of tabular-data.
* Use Euro6 polynomial full_load_curve from Fontaras.
* Smooth-away INALID-GEARS.
* Make the plottings of comparisons of sample-vehicle with Heinz'results interactively report driveability-rules.
* Also report GEARS_ORIG, RPM_NORM, P_AVAIL, RPM, GEARS_ORIG, RPM_NORM results.


v0.0.4.alpha, 18-Jan-2014
-------------------------
* Starting to compare with Heinz's data - FOUND DISCREPANCIES IMPLTYING ERROR IN BASE CALCS.
* Test-enhancements and code for comparing with older runs to track algo behavior.
* Calc 'V_real'.
* Also report RPMS, P_REQ, DIRVEABILITY results.
* Make v_max optionally calculated from max_gear /  gear_ratios.
* BUGFIX: in P_AVAIL 100% percents were mixed [0, 1] ratios!
* BUGFIX: make `goodVehicle` a function to avoid mutation side-effects.
* BUGFIX: add forgotten division on p_required Accel/3.6.
* BUGFIX: velocity-profile mistakenly rounded to integers!
* BUGFIX: v_max calculation based on n_rated (not 1.2 * n_rated).
* FIXME: get default_load_curve floats from Heinz-db.
* FIXME: what to to with INVALID-GEARS?


v0.0.3_alpha, 22-Jan-2014
-------------------------
* -Driveability rules not-implemented:
    * missing some conditions for rule-f.
    * no test-cases.
    * No velocity_real.
    * No preparation calculations (eg. vehicle test-mass).
    * Still unchecked for correctness of results.
* -Pending Experiment tasks:
    * FIXME: Apply rule(e) also for any initial/final gear (not just for i-1).
    * FIXME: move V--0 into own gear.
    * FIXME: move V--0 into own gear.
    * FIXME: NOVATIVE rule: "Clutching gear-2 only when Decelerating.".
    * FIXME: What to do if no gear foudn for the combination of Power/Revs??
    * NOTE: "interpratation" of specs for Gear-2
    * NOTE: Rule(A) not needed inside x2 loop.
    * NOTE: rule(b2): Applying it only on non-flats may leave gear for less than 3sec!
    * NOTE: Rule(c) should be the last rule to run, outside x2 loop.
    * NOTE: Rule(f): What if extra conditions unsatisfied? Allow shifting for 1 sec only??
    * TODO: Construct a matrix of n_min_drive for all gears, including exceptions for gears 1 & 2.
    * TODO: Prepend row for idle-gear in N_GEARS
    * TODO: Rule(f) implement further constraints.
    * TODO: Simplify V_real calc by avoiding multiply all.


v0.0.2_alpha, 7-Jan-2014
------------------------
* -Still unchecked for correctness of results.


v0.0.1, 6-Jan-2014: Alpha release
---------------------------------
* -Unchecked for correctness.
* Runs OK.
* Project with python-packages and test-cases.
* Tidied code.
* Selects appropriate classes.
* Detects and applies downscale.
* Interpreted and implemented the nonsensical specs concerning ``n_min`` engine-revolutions for gear-2
  (Annex 2-3.2, p71).
* -Not implemented yet driveability rules.
* -Does not output real_velocity yet - inly gears.


v0.0.0, 11-Dec-2013: Inception stage
------------------------------------
* Mostly setup.py work, README and help.

