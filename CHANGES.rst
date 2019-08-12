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
| 0.1.x   | GTR phase-1a,               |
|         | (roughly valid till ~2016   |
+---------+-----------------------------+
| 1.x.x   | GTR phase 2 [TDB]           |
+---------+-----------------------------+


Known deficiencies
==================
* (!) Driveability-tules are missing - for their implementation,
  the values for calculating "initial-gear" must be trusted first,
  or else no validation is possible.
* Many checks are missing, e.g. not checking if `p_rated` if "close" to `p_wot_max`.
* n_min_drive does not yet accept array of values for G > 2 e.g. for `n_min_drive_up_start`.

.. _todos-list:

TODOs
=====
* Update cmd-line; add UI front-ends.
* Use a model-explorer to autocomplete excel-cells.
* Automatically calculate masses from H & L vehicles.
* datamodel: validate in 2 steps: jsonschema, populate missing values & validate
* datamodel: Enhance model-preprocessing by interleaving "octapus" merging stacked-models
  between validation stages.
* datamodel: finalize data-schema (renaming columns and adding ``name`` fields in major blocks).
* model/core: Accept units on all quantities.
* core: Move calculations as class-methods to provide for overriding certain parts of the algorithm.
* core: execute part of the calculation-graph based on the the data given/asked.


Changelog
=========

v1.0.0.dev8  (7-Aug-2019): PY3.5 only & real work!
--------------------------------------------------
- Drop support for Python 2.7 & <3.6, due to `f"string:`, among others...
  The supported Pythons `covers 84% of 2018 Python-3 installations (71% of Pythons in total)
  <https://www.jetbrains.com/research/python-developers-survey-2018/#python-3-adoption>`_
- FEAT: NOTEBOOKS comparing with latest Heinz db.
  Possible to launch a *live* demo of this repository in *mybinder.org*.
- Revive tests & TravisCI with *pytest* (drop *nosetest*),
  move all TCs out of main-sources.
- Depend on *pandalone* which has updated *jsonschema-v3* validator
  (draft4-->draft7).
- Start grouping functionalities in separate modules
  (e.g. `engine`, `vehicle`, `vmax`, `downscale`, etc).
- datamodel:

  - BREAK: renamed module ``wltp.model --> wltp.datamodel``.
  - FIX: CLASS1 has now +1 PART(low) at the end, as by the recent spec.
  - break: V-traces is renamed from `cycle --> v_cycle`.
  - break: cycle-part limits are plain lists-of-limits (not list-of-pairs).
  - break: flatten model, merging `vehicle` & `params` properties up to root.
  - drop: don't add a sample WOT in base_model if not given.
  - break: Inverse safety margin from 0.9 --> 0.1, and stop supporting ngear array
    (had been left like that since the phase 1a).
  - feat: add helper API funcs to get WLTC class data (e.g. `v_cycle`, limits, etc).

- algo:

  - Drop Slope, cannot work with downscaling.
  - FEAT: VMAX & NMAX calculations:
    - all `v_max` match *accdb*, but 6 cases missmatch `g_vmax` (out of 125 cases).
    - many minor mismatches on `n_max1/2/3`.

  - FEAT: VMAX calculation;  all match *accdb*, but 6 cases missmatch `g_vmax` (out of 125 cases).
  - UPD: DOWNSCALING to recent formulas & constants, and document them.
    Still scaled (not recursive), none can reproduce exactly MsAccess.
  - Start PANDA-izing calculations (from numpy-arrays + rogue indices).
    Much better and shorter code.
  - Rounding according to GTR;  +notebook comparing rounding behavior of
    Python vs Matlab vs C# vs VBA(pre-canned).

- Build & dev-dependencies enhancements.

  - fix: update to pandas-0.25_ (July 2019).

- style: auto-format python files with |black|_  using |pre-commit|_.

.. |black| replace:: *black* opinionated formatter
.. _black: https://black.readthedocs.io/
.. |pre-commit| replace:: *pre-commit* hooks framework
.. _pre-commit: https://pre-commit.com/


v0.1.2a0  (5-Jun-2019): Relax checks
------------------------------------
- Relax some conditions on inputs:
    - Just warn on Pwot-normalized > 1 or > n_idle or < 1.2 x n_rated
      (BUT not extrapolate)
    - allow float as `v_max`.

- build:
    - drop `sphinx_rtd_theme` dependency -  provided by default these days.
    - drop pip-installin of `xlwings` attrocity if missing.


v0.1.1a0  (25-May-2019): UNECE takeover
---------------------------------------
- Fix py36 "nested regex" warning on ``pandel`` module.
- Pin ``jsonschema <3`` to fix validation, was also ``>2.5``, so now maximum ``2.6``.
- Updates to `setup.py` and dependencies.
- Minor documentation fixes.
- VSCode files & dev plugins.


v0.1.0a3 (23-Aug-2018)
----------------------
Quick'n Dirty release to remove ``matplotlib`` from dependencies.

- fix(main): ``--gui``and ``--excelrun`` were preventing cmd-line launches,
  the ``-M`` option did not work due to bad argument type-parsing.
- Dependencies:
    - drop *easygui* dependency.
    - BREAK: move ``matplotlib`` to extras ``[plot]``, so ``co2mpas`` docker-image
      does not load Qt and other heavy graphical stuff.


v0.1.0-alpha.2 (25-May-2017)
----------------------------
- fix(deps): pandas-v0.20.1 dropped PandasError classs -
  See https://github.com/pydata/pandas-datareader/issues/305
- fix(main): regression in `v0.1.0-alpha.0`, main did not import due to
  not fully deleted *tkui* launch code.
- style(pep8): del spaces from python files.
- chore(build): add ``./dib/bumpver.py`` script from post-`co2mpas-1.6.1.dev6`.


v0.1.0-alpha.1 (9-Mar-2017)
----------------------------
- fix(build, #3): Dependency *xlwings* broke builds on Linux in downstream packages.


v0.1.0-alpha.0 (26-Feb-2017)
----------------------------
- feat(core): modify acceleration rule ``3s-->2s`` to assimilate more to *phase-1b*.
- feat(ui): drop tkUI code and *Pillow* dependency.


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


Questions to Heinz
==================
- n_min:

  - GTR 2.g has a conflict between `ng` and  `ng_vmax`: the formula says `ng`
    while the "legend" below speaks only about `ng_vmax`.
    The later makes sense from engineering standpoint and also stacks betters
    against accdb results.

    - So the formula actually must become :math:`(n/v)(ng_{\textbf{vmax}}) \times V_{max,vehicle}`,
      correct?
    - Related to Q on v_max "ties", below, should in those cases consider
      the "from the lower gear achieving v_max", to assume the same logic?

  - What is the meaning of the -0.1389 threshold in Annex 2-2.k?
    Is it used anywhere in the accdb?
  - Regarding the exact boundaries of the "up" phase, is it based on the same logic as
    for accel/decel/cruise phases of Annex 2-4, correct?

    - The "up" phase is also defined for V >= 1kmh, only, correct
      (but not stated in the GTR)?

- VMax in `F new vehicle.form.vbs <https://github.com/JRCSTU/wltp/blob/master/Notebooks/WLTP_GS_AccessDB-sources/F%20new%20vehicle.form.vbs>`_:

  - Is this the `v_max` used for class 3a/b decision?
  - L3358-L3360: is this rounding needed because of
    accumulation of rounding errors?
  - L2835:
  - The GTR reaches only down to `ng-2` while accdb reached `ng-3`.

    - Why?
    - Why some times reach down to ng-3 others ng-2, etc?
    - Why not simply scan from top for max-v?
    - Is it possible a lower gear to have lower v_max and next lower to have v_max high again?
    - Is there a 3-geared car with v_max@gear-1?

  - There are 5 cases where both top gears can reach the same `v_max`/
    Accdb seems to take the lower one, but the GTR suggest the opposite
    
    - Which is the vmax-gear on ties?
    -From which one should derive `n_min_3`?

  - Cannot match accdb `v_max` for vehicles 42, 48, 52, 53?

- Downscale: vehicle-82 has f_dsc 0.010 (=threshold) and still gets downscaled,
  while the GTR write downscale only if that threshold excheeded;  why?
- p_avail: case 48 seems like ASM has been used in the 1st 4 values,
  but all ASM values are 0.  Why?::

         n        Pwot  p_avail_expected       Pavai  ASM     ratio
      1330   33.719761         30.347785   26.975809  0.0  1.125000
      1500   40.840704         36.756634   32.672564  0.0  1.125000
      1800   71.628313         64.465481   57.302650  0.0  1.125000
      1900   75.607663         68.046897   64.266514  0.0  1.058824
      3000  119.380521        107.442469  107.442469  0.0  1.000000
      4000  159.174028        143.256625  143.256625  0.0  1.000000
      5000  198.967535        179.070781  179.070781  0.0  1.000000
      5700  226.822990        204.140691  204.140691  0.0  1.000000
      5800  228.000000        205.200000  205.200000  0.0  1.000000
      6000  228.000000        205.200000  205.200000  0.0  1.000000
      6200  228.000000        205.200000  205.200000  0.0  1.000000
      6400  221.168123        199.051311  199.051311  0.0  1.000000
      6600  213.980159        192.582143  192.582143  0.0  1.000000
      6800  207.931546        187.138391  187.138391  0.0  1.000000

- n_max:

  - veh041 seems to calculate `n_max_cycle` (`n_max2`) based on class2
    and not from class1, where it belongs::

        v_class1_max(64.4) * n2v_4(90.3) = 5815.31
        v_class2_max(123.1) * n2v_4(90.3) = 11115.93  # value in accdb

    How is that possible?

- Driveability rules:

  - Why is `acc`, `dec` & `cruise` calculated on the "japanese" acceleration trace `a2`?
    What is this 0.278 as threshold value they are using?
    (i.e. `A gearshift_table cruise.query.txt#L3
    <https://github.com/ankostis/wltp/blob/master/Notebooks/WLTP_GS_AccessDB-sources/A%20gearshift_table%20cruise.query.txt#L3>`_)?

  - Are the following interpretations for the phases in Annex 2-4 correct?::

             'v': [0,0,3,3,5,8,8,8,6,4,5,6,6]
         'accel': [0,0,0,1,1,1,0,0,0,1,1,1,0]
        'cruise': [0,0,0,0,0,1,1,1,0,0,0,0,0]
         'decel': [0,0,0,0,0,0,0,1,1,1,0,0,0]

    So actually there cannot exist a 2-sample phase, correct?