..    include:: <isonum.txt>

#######
Changes
#######
.. contents::

Known deficiencies
==================
* (!) Driveability-rules not ordered as defined in the latest task-force meeting.
* (!) The ``n_min_drive`` is not calculated as defined in the latest task-force meeting,
  along with other recent updates.
* (!) Does not discriminate between :term:`Unladen mass` and :term:`Test mass`.
* Clutching-points and therefore engine-speed are very preliminary.
* Results are not yet compared with the new wltp_db sample-vehicles.

TODOs
=====
* Add cmd-line front-end.
* Add IPython front-end.
* No automatic calculation of masses and road-load coefficients from H & L vehicles.

.. todolist::

Changelog
=========


v0.0.8-alpha, 04-Aug-2014
---------------------------------------
* Documentation fixes.


v0.0.7-alpha, 31-Jul-2014: 1st *public*
---------------------------------------
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

