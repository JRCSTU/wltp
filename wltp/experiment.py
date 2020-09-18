#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2013-2020 European Commission (JRC);
# Licensed under the EUPL (the 'Licence');
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at: http://ec.europa.eu/idabc/eupl
"""*(TO BE DEFUNCT)* The core that accepts a vehicle-model and wltc-classes, runs the simulation and updates the model with results.

.. Attention:: The documentation of this core module has several issues and needs work.

Notation
--------
* ALL_CAPITAL variables denote *vectors* over the velocity-profile (the cycle),
* ALL_CAPITAL starting with underscore (`_`) denote *matrices* (gears x time).

For instance, GEARS is like that::

    [0, 0, 1, 1, 1, 2, 2, ... 1, 0, 0]
     <----   cycle time-steps   ---->

and _GEARS is like that::

     t:||: 0  1  2  3
    ---+-------------
    g1:|[[ 1, 1, 1, 1, ... 1, 1
    g2:|   2, 2, 2, 2, ... 2, 2
    g3:|   3, 3, 3, 3, ... 3, 3
    g4:|   4, 4, 4, 4, ... 4, 4 ]]


Major vectors & matrices
------------------------

V:        floats (#cycle_steps)
    The wltp-class velocity profile.

_GEARS:    integers (#gears X #cycle_steps)
    One row for each gear (starting with 1 to #gears).

_N_GEARS:  floats (#gears X #cycle_steps)
    One row per gear with the Engine-revolutions required to follow the V-profile
    (unfeasible revs included),
    produced by multiplying ``V * gear-rations``.

_GEARS_YES:  boolean (#gears X #cycle_steps)
    One row per gear having ``True`` wherever gear is possible for each step.

.. Seealso:: :mod:`~,datamodel` for in/out schemas
.. Workaround sphinx-doc/sphinx#6590
.. doctest::
    :hide:

    >>> from wltp.experiment import *
    >>> __name__ = "wltp.experiment"
"""

import logging
import re

import numpy as np
import pandas as pd

from . import cycler, cycles, datamodel, downscale, engine, invariants
from . import io as wio
from . import nmindrive, pipelines, vehicle, vmax
from .invariants import v_decimals, vround

log = logging.getLogger(__name__)


class Experiment(object):
    """Runs the vehicle and cycle data describing a WLTC experiment.

    See :mod:`wltp.experiment` for documentation.
    """

    def __init__(
        self,
        mdl,
        skip_model_validation=False,
        validate_wltc_data=False,
        additional_properties=True,
    ):
        """
        :param mdl:
            trees (formed by dicts & lists) holding the experiment data.
        :param skip_model_validation:
            when true, does not validate the model.
        :param additional_properties:
            when false; strict checks screams if unknown props in model
        """

        self._set_model(
            mdl, skip_model_validation, validate_wltc_data, additional_properties
        )

        self.wltc = self._model["wltc_data"]

    def run(self):
        """Invokes the main-calculations and extracts/update Model values!

        @see: Annex 2, p 70
        """
        m = wio.pstep_factory.get()
        c = wio.pstep_factory.get().cycle
        w = wio.pstep_factory.get().wot

        mdl = self._model
        orig_mdl = self._model.copy()

        ## Prepare results
        #
        cycle = mdl.get(m.cycle)
        if cycle is None:
            cycle = pd.DataFrame()
        else:
            cycle = pd.DataFrame(cycle)
            log.info(
                "Found forced `cycle-run` table(%ix%i).", cycle.shape[0], cycle.shape[1]
            )
        mdl[c] = cycle

        ## Ensure Time-steps start from 0 (not 1!).
        #
        cycle.reset_index()
        cycle.index.name = c.t

        ## Extract vehicle attributes from model.
        #
        test_mass = mdl[m.test_mass]
        unladen_mass = mdl.get(m.unladen_mass) or test_mass - mdl[m.driver_mass]
        p_rated = mdl[m.p_rated]
        n_rated = mdl[m.n_rated]
        n_idle = mdl[m.n_idle]
        n2v_ratios = mdl[m.n2v_ratios]
        f0 = mdl.get(m.f0)
        f1 = mdl.get(m.f1)
        f2 = mdl.get(m.f2)
        if all(f is not None for f in (f0, f1, f2)):
            pass
        elif (
            all(f is None for f in (f0, f1, f2))
            and m.resistance_coeffs_regression_curves in mdl
        ):
            (f0, f1, f2) = vehicle.calc_default_resistance_coeffs(
                test_mass, mdl[m.resistance_coeffs_regression_curves]
            )
        else:
            raise ValueError("Missing resistance_coeffs!")

        wot = mdl[m.wot]
        n95_low, n95_high = engine.calc_n95(wot, n_rated, p_rated)
        mdl[m.n95_low], mdl[m.n95_high] = n95_low, n95_high

        f_safety_margin = mdl[m.f_safety_margin]

        gwots = engine.interpolate_wot_on_v_grid(wot, n2v_ratios)
        gwots = engine.attach_p_avail_in_gwots(gwots, f_safety_margin=f_safety_margin)
        gwots[w.p_resist] = vehicle.calc_p_resist(gwots.index, f0, f1, f2)

        v_max_rec = vmax.calc_v_max(gwots)
        mdl[m.v_max] = v_max = v_max_rec.v_max
        mdl[m.n_vmax] = v_max_rec.n_vmax
        mdl[m.g_vmax] = v_max_rec.g_vmax
        mdl[m.is_n_lim_vmax] = v_max_rec.is_n_lim
        mdl[m.wots_vmax] = v_max_rec.wot

        p_m_ratio = vehicle.calc_p_m_ratio(p_rated, unladen_mass)
        mdl[m.pmr] = p_m_ratio
        f_inertial = mdl[m.f_inertial]

        forced_v_column = c.v_target
        V = cycle.get(forced_v_column)
        if V is not None:
            log.info(
                "Found forced velocity in %r with %s values.", forced_v_column, len(V)
            )

            V = pd.Series(V, name=c.v_target)
            wltc_class, _part, _kind = cycles.identify_cycle_v(V)
            cb = cycler.CycleBuilder(V)
            mdl[m.f_dsc] = None
        else:
            ## Decide WLTC-class.
            #
            wltc_class = mdl.get(m.wltc_class)
            if wltc_class is None:
                wltc_class = vehicle.decide_wltc_class(
                    self.wltc["classes"], p_m_ratio, v_max
                )
                mdl[m.wltc_class] = wltc_class
            else:
                log.info("Found forced wltc_class(%s).", wltc_class)

            class_data = datamodel.get_class(wltc_class, mdl=self._model)
            V = datamodel.get_class_v_cycle(wltc_class)
            assert isinstance(V, pd.Series), V

            ## Downscale velocity-profile.
            #
            f_dsc = mdl.get(m.f_dsc)
            if not f_dsc:
                f_dsc_threshold = mdl[m.f_dsc_threshold]
                f_dsc_decimals = mdl[m.f_dsc_decimals]
                dsc_data = class_data["downscale"]
                phases = dsc_data["phases"]
                p_max_values = dsc_data["p_max_values"]
                downsc_coeffs = dsc_data["factor_coeffs"]
                f_dsc_raw = downscale.calc_f_dsc_raw(
                    p_max_values,
                    downsc_coeffs,
                    p_rated,
                    test_mass,
                    f0,
                    f1,
                    f2,
                    f_inertial,
                )
                f_dsc = downscale.calc_f_dsc(
                    f_dsc_raw,
                    f_dsc_threshold,
                    f_dsc_decimals,
                )
                mdl[m.f_dsc] = f_dsc
                mdl[m.f_dsc_raw] = f_dsc_raw

            if f_dsc > 0:
                V_dsc_raw = downscale.calc_V_dsc_raw(V, f_dsc, phases)
                V_dsc_raw.name = c.V_dsc_raw

                V_dsc = vround(V_dsc_raw)
                V_dsc.name = c.V_dsc

                ## VALIDATE AGAINST PIPELINE.
                #
                orig_mdl.pop("v_max", None)  # vehdb contains v_max!
                sol = pipelines.scale_trace_pipeline().compute(orig_mdl)
                assert (V_dsc == sol["V_dsc"]).all()
                assert mdl["pmr"] == sol["p_m_ratio"]
                # for i in "v_max g_vmax n_vmax wltc_class n95_high n95_low".split():
                for i in "v_max g_vmax n_vmax wltc_class".split():
                    assert mdl[i] == sol[i]

                # TODO: separate column due to cap/extend.
                V_target = V_dsc.copy()
                V_target.name = c.v_target

                cb = cycler.CycleBuilder(V, V_dsc_raw, V_dsc, V_target)
                V = cb.cycle[c.v_target]
            else:
                V_target = V.copy()
                V_target.name = c.v_target

                cb = cycler.CycleBuilder(V, V_target)
                V = V_target

        assert isinstance(V, pd.Series), V

        pm = cycler.PhaseMarker()

        if wltc_class:
            wltc_parts = datamodel.get_class_parts_limits(wltc_class, edges=True)
            cb.cycle = pm.add_class_phase_markers(cb.cycle, wltc_parts)

        cb.cycle = pm.add_transition_markers(cb.cycle, cb.V, cb.A)

        cb.cycle[c.p_inert] = vehicle.calc_inertial_power(
            cb.V, cb.A, test_mass, f_inertial
        )
        cb.add_wots(gwots)
        cb.cycle[c.p_req] = vehicle.calc_required_power(
            cb.cycle[c.p_resist], cb.cycle[c.p_inert]
        )

        ## VALIDATE AGAINST PIPELINE No1
        #
        inp = {**mdl, "V_compensated": V}
        sol = pipelines.cycler_pipeline().compute(inp.copy())
        graph_cycle = sol["cycle"]
        P_req = graph_cycle["P_req"]
        p_req = cb.cycle[c.p_req]
        idx = ~p_req.isnull()
        assert (p_req[idx] == P_req[idx]).all()

        ## Remaining n_max values
        #
        g_max_n2v = n2v_ratios[mdl[m.g_vmax] - 1]
        #  NOTE: `n95_high` is not rounded based on v, like the rest n_mins.
        mdl[m.n_max1] = mdl[m.n95_high]
        #  NOTE: In Annex 2-2.g, it is confusing g_top with g_vmax;
        #  the later stack betters against accdb results.
        mdl[m.n_max2] = n_max_cycle = g_max_n2v * cb.V.max()
        mdl[m.n_max3] = g_max_n2v * mdl[m.v_max]
        mdl[m.n_max] = engine.calc_n_max(mdl[m.n_max1], mdl[m.n_max2], mdl[m.n_max3])

        # TODO: incorporate `t_cold_end` check in validation framework.
        if wltc_class:
            for err in cb.validate_nims_t_cold_end(mdl[m.t_cold_end], wltc_parts):
                raise err

        initial_gear_flags = cb.calc_initial_gear_flags(
            g_vmax=mdl[m.g_vmax],
            n95_high=n95_high,
            n_max_cycle=n_max_cycle,
            # TODO: expand nmins
            nmins=nmindrive.mdl_2_n_min_drives(**mdl)["n_min_drives"],
        )
        ok_n_flags = cb.combine_ok_n_gear_flags(initial_gear_flags)
        ok_flags = pd.concat((initial_gear_flags, ok_n_flags), axis=1)
        ok_gears = cb.derrive_ok_gears(ok_flags)

        g_min, g_max0, G_scala = cb.make_gmax0(ok_gears)

        cb.add_columns(ok_flags, ok_gears, G_scala, g_min, g_max0)

        mdl[m.cycle] = cb.cycle

        ## VALIDATE AGAINST PIPELINE No2
        #
        assert (g_min == graph_cycle["g_min"]).all()
        assert (g_max0 == graph_cycle["g_max0"]).all()

        return mdl

    #######################
    ##       MODEL       ##
    #######################

    @property
    def model(self):
        return self._model

    def _set_model(
        self, mdl, skip_validation, validate_wltc_data, additional_properties
    ):
        from wltp.datamodel import get_model_base, merge

        merged_model = get_model_base()
        merge(merged_model, mdl)
        if not skip_validation:
            errors = list(
                datamodel.validate_model(
                    merged_model,
                    validate_wltc_data=validate_wltc_data,
                    additional_properties=additional_properties,
                    iter_errors=True,
                )
            )
            if errors:
                err_msg = "\n  ".join(str(e) for e in errors)
                raise ValueError(f"Model validation errors: {err_msg}")
        self._model = merged_model

    def driveability_report(self):
        cycle = self._model.get("cycle")
        if not cycle is None:
            issues = []
            drv = cycle["driveability"]
            pt = -1
            for t in drv.to_numpy().to_numpy().nonzero()[0]:
                if pt + 1 < t:
                    issues += ["..."]
                issues += ["{:>4}: {}".format(t, drv[t])]
                pt = t

            return "\n".join(issues)
        return None


#######################
## PURE CALCULATIONS ##
##  Separate for     ##
##     testability!  ##
#######################


def addDriveabilityMessage(time_step, msg, driveability_issues):
    old = driveability_issues[time_step]
    driveability_issues[time_step] = old + msg


def addDriveabilityProblems(_GEARS_BAD, reason, driveability_issues):
    failed_steps = _GEARS_BAD.to_numpy().nonzero()[0]
    if failed_steps.size != 0:
        log.info("%i %s: %s", failed_steps.size, reason, failed_steps)
        for step in failed_steps:
            addDriveabilityMessage(step, reason, driveability_issues)


_escape_char = 128

_regex_gears2regex = re.compile(br"\\g(\d+)")


def dec_byte_repl(m):
    return bytes([_escape_char + int(m.group(1))])


def gearsregex(gearspattern):
    r"""
    :param gearspattern: regular-expression or substitution that escapes decimal-bytes written as: ``\g\d+``
                        with adding +128, eg::

                            \g124|\g7 --> unicode(128+124=252)|unicode(128+7=135)
    """

    assert isinstance(gearspattern, bytes), (
        "Not bytes: %s" % gearspattern
    )  # For python-2 to work with __future__.unicode_literals.

    regex = _regex_gears2regex.sub(dec_byte_repl, gearspattern)
    return re.compile(regex)


def np2bytes(NUMS):
    if (NUMS < 0).any() or (NUMS >= (256 - _escape_char)).any():
        assert all(NUMS >= 0) and all(NUMS < (256 - _escape_char)), (
            "Outside byte-range: %s" % NUMS[(NUMS < 0) | (NUMS >= (256 - _escape_char))]
        )

    return (NUMS + _escape_char).astype("uint8").tostring()


def bytes2np(bytesarr):
    assert isinstance(bytesarr, bytes), "Not bytes: %s" % bytesarr

    return np.frombuffer(bytesarr, dtype="uint8") - _escape_char


def assert_regexp_unmatched(regex, string, msg):
    assert not re.findall(regex, string), "%s: %s" % (
        msg,
        [(m.start(), m.group()) for m in re.finditer(regex, string)],
    )


# =====================
# Driveability rules #
# =====================


def rule_checkSingletons(bV, GEARS, CLUTCH, driveability_issues, re_zeros):
    re_singletons = gearsregex(b"(\\g0)")


def rule_a(bV, GEARS, CLUTCH, driveability_issues, re_zeros):
    """Rule (a): Clutch & set to 1st-gear before accelerating from standstill.

     Implemented with a regex, outside rules-loop:
     Also ensures gear-0 always followed by gear-1.

     NOTE: Rule(A) not inside x2 loop, and last to run.
    """

    for m in re_zeros.finditer(bV):
        t_accel = m.end()
        # Exclude zeros at the end.
        if t_accel == len(bV):
            break
        GEARS[t_accel - 1 : t_accel] = 1
        CLUTCH[t_accel - 1 : t_accel - 2] = True
        addDriveabilityMessage(t_accel - 1, "(a: X-->0)", driveability_issues)
    assert_regexp_unmatched(
        b"\x00[^\x00\x01]",
        GEARS.astype("uint8").tostring(),
        "Jumped gears from standstill",
    )


def step_rule_b1(t, pg, g, V, A, GEARS, driveability_issues):
    """Rule (b1): Do not skip gears while accelerating."""

    if (pg + 1) < g and A[t - 1] > 0:
        pg = pg + 1
        GEARS[t] = pg
        addDriveabilityMessage(t, "(b1: %i-->%i)" % (g, pg), driveability_issues)
        return True
    return False


def step_rule_b2(t, pg, g, V, A, GEARS, driveability_issues):
    """Rule (b2): Hold gears for at least 2sec when accelerating."""

    if (
        pg != GEARS[t - 2]
    ):  # A[t-1] > 0):  NOTE: Not checking Accel on the final step A[t-1]!
        # assert g > pg, 'Rule e & g missed downshift(%i: %i-->%i) in acceleration!'%(t, pg, g)
        if g < pg:
            addDriveabilityMessage(
                t,
                "Rule e or g missed downshift(%i: %i-->%i) in acceleration?"
                % (t, pg, g),
                driveability_issues,
            )
        if A[t - 2] > 0:
            addDriveabilityMessage(t, "(b2: %i-->%i)" % (g, pg), driveability_issues)

            return True
    return False


def step_rule_c1(t, pg, g, V, A, GEARS, driveability_issues):
    """Rule (c1): Skip gears <3sec when decelerating. """

    if (pg != GEARS[t - 3 : t - 1]).any() and (A[t - 2 : t] < 0).all():
        pt = t - 2
        while pt >= t - 3 and GEARS[pt] == pg:
            pt -= 1

        ## Skip even further...
        #
        if GEARS[t + 1] < g:
            t += 1
            g = GEARS[t]

        GEARS[pt + 1 : t] = g
        for tt in range(pt + 1, t):
            addDriveabilityMessage(tt, "(c1: %i-->%i)" % (pg, g), driveability_issues)
        return True
    return False


def rule_c2(bV, A, GEARS, CLUTCH, driveability_issues, re_zeros):
    """Rule (c2): Skip 1st-gear while decelerating to standstill.

     Implemented with a regex, outside rules-loop:
     Search for zeros in _reversed_ V & GEAR profiles,
     for as long Accel is negative.
     NOTE: Rule(c2) is the last rule to run.
    """

    nV = len(bV)
    for m in re_zeros.finditer(bV[::-1]):
        t_stop = m.end()
        # Exclude zeros at the end.
        if t_stop == nV:
            break
        t = nV - t_stop - 1
        while A[t] < 0 and GEARS[t] == 1:
            addDriveabilityMessage(t, "(c2: %i-->0)" % GEARS[t], driveability_issues)
            GEARS[t] = 0
            CLUTCH[t] = False
            t -= 1


def step_rule_d(t, pg, g, V, A, GEARS, driveability_issues):
    """Rule (d): Cancel shifts after peak velocity."""

    if A[t - 2] > 0 and A[t - 1] < 0 and GEARS[t - 2] == pg:
        GEARS[t] = pg
        addDriveabilityMessage(t, "(d: %i-->%i)" % (g, pg), driveability_issues)
        return True
    return False


def step_rule_e(t, pg, g, V, A, GEARS, driveability_issues):
    """Rule (e): Cancel shifts lasting 5secs or less."""

    if pg > g:
        ## Travel back in time for 5secs.
        #
        pt = t - 2
        while pt >= t - 5 and GEARS[pt] == pg:
            pt -= 1

        if (
            GEARS[pt] < pg
        ):  # NOTE: Apply rule(e) also for any LOWER initial/final gears (not just for i-1).
            GEARS[pt + 1 : t] = g
            for tt in range(pt + 1, t):
                addDriveabilityMessage(
                    tt, "(e: %i-->%i)" % (pg, g), driveability_issues
                )
            return True
    return False


def step_rule_f(t, pg, g, V, A, GEARS, driveability_issues):
    """Rule(f): Cancel 1sec downshifts (under certain circumstances)."""

    if pg < g and GEARS[t - 2] >= g:
        # NOTE: Nowhere to apply it since rule(b2) would have eliminated 1-sec shifts.  Moved before rule(b)!
        # NOTE: Applying rule(f) also for i-2, i-3, ... singular-downshifts.
        # FIXME: Rule(f) implement further constraints.
        # NOTE: Rule(f): What if extra conditions unsatisfied? Allow shifting for 1 sec only??
        GEARS[t - 1] = min(g, GEARS[t - 2])
        addDriveabilityMessage(t - 1, "(f: %i-->%i)" % (pg, g), driveability_issues)
        return True

    return False


def step_rule_g(t, pg, g, V, A, GEARS, driveability_issues):
    """Rule(g): Cancel upshift during acceleration if later downshifted for at least 2sec."""

    if pg > g and (GEARS[t : t + 2] == g).all() and (A[t - 1 : t + 2] > 0).all():
        ## Travel back in time for as long accelerating and same gear.
        #
        pt = t - 2
        while GEARS[pt] == pg and A[pt] > 0:
            pt -= 1

        GEARS[pt + 1 : t] = g
        for tt in range(pt + 1, t):
            addDriveabilityMessage(tt, "(g: %i-->%i)" % (pg, g), driveability_issues)
        return True

    return False


def applyDriveabilityRules(V, A, GEARS, CLUTCH, driveability_issues):
    """
    @note: Modifies GEARS & CLUTCH.
    @see: Annex 2-4, p 72
    """
    return  ## FIXME: BREAK RULES oin advance of UPDATING them 2019

    def apply_step_rules(rules, isStopOnFirstApplied):
        for t in t_range:
            if GEARS[t - 1] != GEARS[t]:  ## All rules triggered by a gear-shift.
                for rule in rules:
                    if rule(
                        t, GEARS[t - 1], GEARS[t], V, A, GEARS, driveability_issues
                    ) and (isStopOnFirstApplied or GEARS[t - 1] == GEARS[t]):
                        break

    ## V --> byte-array to search by regex.
    #
    V = V.copy()
    V[V > (255 - _escape_char)] = 255 - _escape_char
    bV = np2bytes(V)
    re_zeros = gearsregex(br"\g0+")

    ## NOTE: Extra_rule(1): Smooth-away INVALID-GEARS.
    #
    for t in range(
        2, len(GEARS)
    ):  # Start from 2nd element to accommodate rule(e)'s backtracking.
        if GEARS[t] < 0:
            GEARS[t] = GEARS[t - 1]

    ## Loop X 2 driveability-rules.
    #
    t_range = range(
        5, len(GEARS)
    )  # Start from 5th element to accommodate rule(e)'s backtracking.
    for _ in [0, 1]:
        apply_step_rules(
            [step_rule_g, step_rule_f], False
        )  # NOTE: Rule-order and first-to-apply flag unimportant.
        apply_step_rules(
            [step_rule_e, step_rule_b1, step_rule_b2], False
        )  # NOTE: Rule-order for b1 &b2 unimportant.
        apply_step_rules([step_rule_c1], False)

        rule_c2(bV, A, GEARS, CLUTCH, driveability_issues, re_zeros)

    rule_a(bV, GEARS, CLUTCH, driveability_issues, re_zeros)


def run_cycle(
    V, A, P_REQ, n2v_ratios, n_idle, n_min_drive, n_rated, p_rated, load_curve, mdl
):
    """Calculates gears, clutch and actual-velocity for the cycle (V).
    Initial calculations happen on engine_revs for all gears, for all time-steps of the cycle (_N_GEARS array).
    Driveability-rules are applied afterwards on the selected gear-sequence, for all steps.

    :param V: the cycle, the velocity profile
    :param A: acceleration of the cycle (diff over V) in m/sec^2
    :return: CLUTCH:    a (1 X #velocity) bool-array, eg. [3, 150] --> gear(3), time(150)

    :rtype: array
    """

    ## A multimap to collect problems.
    #
    driveability_issues = np.empty_like(V, dtype="object")
    driveability_issues[:] = ""

    ## Read and calc model parameters.
    #
    n_range = n_rated - n_idle

    f_n_max = mdl["f_n_max"]
    n_max = n_idle + f_n_max * n_range

    if n_min_drive is None:
        f_n_min = mdl["f_n_min"]
        n_min_drive = n_idle + f_n_min * n_range

    f_n_min_gear2 = mdl["f_n_min_gear2"]
    n_min_gear2 = f_n_min_gear2 * n_idle

    f_n_clutch_gear2 = mdl["f_n_clutch_gear2"]
    n_clutch_gear2 = max(
        f_n_clutch_gear2[0] * n_idle, f_n_clutch_gear2[1] * n_range + n_idle
    )

    p_safety_margin = mdl["f_safety_margin"]
    v_stopped_threshold = mdl["v_stopped_threshold"]

    (_N_GEARS, _GEARS, _GEAR_RATIOS) = calcEngineRevs_required(
        V, n2v_ratios, n_idle, v_stopped_threshold
    )

    (_G_BY_N, CLUTCH) = possibleGears_byEngineRevs(
        V,
        A,
        _N_GEARS,
        len(n2v_ratios),
        n_idle,
        n_min_drive,
        n_min_gear2,
        n_max,
        v_stopped_threshold,
        driveability_issues,
    )

    (_G_BY_P, _P_AVAILS, _N_NORMS) = possibleGears_byPower(
        _N_GEARS,
        P_REQ,
        n_idle,
        n_rated,
        p_rated,
        load_curve,
        p_safety_margin,
        driveability_issues,
    )

    assert (
        _GEAR_RATIOS.shape == _N_GEARS.shape == _P_AVAILS.shape == _N_NORMS.shape
    ), _shapes(_GEAR_RATIOS, _N_GEARS, _P_AVAILS, _N_NORMS)

    GEARS = selectGears(_GEARS, _G_BY_N, _G_BY_P, driveability_issues)
    CLUTCH[(GEARS == 2) & (_N_GEARS[1, :] < n_clutch_gear2)] = True

    assert V.shape == GEARS.shape, _shapes(V, GEARS)
    assert GEARS.shape == CLUTCH.shape == driveability_issues.shape, _shapes(
        GEARS, CLUTCH.shape, driveability_issues
    )
    assert "i" == GEARS.dtype.kind, GEARS.dtype
    assert ((GEARS >= -1) & (GEARS <= len(n2v_ratios))).all(), (min(GEARS), max(GEARS))

    return (
        GEARS,
        CLUTCH,
        _GEAR_RATIOS,
        _N_GEARS,
        _P_AVAILS,
        _N_NORMS,
        driveability_issues,
    )


if __name__ == "__main__":
    pass
