:Organization: UNECE/GS-TF
:Date: 14-Sep-2014
:Version: phase-1a
:URL: https://www2.unece.org/wiki/download/attachments/23758909/WLTP-08-04e%20-%20GTR%20Version%2014-09-2014.docx?api=v2

.. include:: <xhtml1-special.txt>

#######
Annex 2
#######


Gear selection and shift point determination for vehicles equipped with manual transmissions
============================================================================================

General approach
----------------

1. The shifting procedures described in this Annex shall apply to vehicles equipped 
   with manual and automatic shift transmissions.

2. The prescribed gears and shifting points are based on the balance between the power required 
   to overcome driving resistance and acceleration, and the power provided by the engine 
   in all possible gears at a specific cycle phase.

3. The calculation to determine the gears to use shall be based on normalised engine speeds 
   (normalised to the span between idling speed and rated engine speed) and 
   normalised full load power curves (normalised to rated power) versus normalised engine speed.

4. This annex shall not apply to vehicles tested according to Annex 8.


Required data 
-------------
The following data is required to calculate the gears to be used when driving the cycle 
on a chassis dynamometer:

(a) :math:`P_{rated}`, the maximum rated engine power as declared by the manufacturer;

(b) :math:`s`, the rated engine speed at which an engine develops its maximum power.
    If the maximum power is developed over an engine speed range, :math:`s` is determined 
    by the mean of this range;

(c) :math:`n_{idle}`, idling speed;

(d) :math:`ng_{max}`, the number of forward gears;

(e) :math:`n_{min\_drive}`, minimum engine speed for gears :math:`i>2` when 
    the vehicle is in motion. The minimum value is determined by the following equation:

    .. math::
        :label: n_min_drive

        n_{min\_drive} = n_{idle} + 0.125 \times (s - n_{idle})

    Higher values may be used if requested by the manufacturer;

(f) :math:`ndv_i`, the ratio obtained by dividing :math:`n` in :math:`min^{-1}` 
    by :math:`v` in :math:`km/h` for each gear :math:`i`, :math:`i=1 \text{ to } ng_{max}`;

(g) :math:`TM`, test mass of the vehicle in :math:`kg`;

(h) :math:`f_0, f_1, f_2`, driving resistance coefficients as defined in Annex 4 
    in :math:`N`, :math:`N/(km/h)`, and :math:`N/(km/h)^2` respectively;   

(i) :math:`P_{norm_{wot}}(n_{norm_i,j})`: is the full load power curve, 
    normalised to rated power over engine speed, normalised to 
    (rated engine speed |mdash| idling speed), where:

    .. math::
        :label: p_wot

        n_{norm} = \frac{n-n_{idle}}{s-n_{idle}}     



Calculations of required power, engine speeds, available power, and possible gear to be used
============================================================================================

Calculation of required power
-----------------------------
For every second :math:`j` of the cycle trace, the power required to overcome driving resistance and 
to accelerate shall be calculated using the following equation:

.. math::
    :label: p_req

    P_{prequired, j} = \frac{f_0 \times v_j + f_1 \times v_j^2 + f_2 \times v_j^3}{3600} + \frac{kr \times a_j \times v_j \times TM}{3600}

where:

- :math:`f0` is the road load coefficient, :math:`N`;
- :math:`f1` is the road load parameter dependent on velocity, :math:`N/(km/h)`;
- :math:`f2` is the road load parameter based on the square of velocity, :math:`N/(km/h)^2`;
- :math:`P_{required,j}` is the required power at second :math:`j`, :math:`kW`;
- :math:`v_j` is the vehicle speed at second :math:`j`, :math:`km/h`;
- :math:`a_j` is the vehicle acceleration at second :math:`j`, :math:`m/s`,

  .. math::
      :label: accel

      a_j = \frac{v_{j+1} - v_j}{3.6 \times (t_{j+1} - t_j)};

- :math:`TM` is the vehicle test mass, :math:`kg`;
- :math:`kr` is a factor taking the inertial resistances of the drivetrain during acceleration 
  into account and is set to :math:`1.1`.


Determination of engine speeds
------------------------------
For each :math:`v_j \le 1\ km/h`, the engine speed shall be set to :math:`n_{idle}` and 
the gear lever shall be placed in neutral with the clutch engaged.

For each :math:`v_j \ge 1\ km/h` of the cycle trace and each gear :math:`i, i=1 \text{ to } ng_{max}`, 
the engine speed :math:`n_{i,j}` shall be calculated using the following equation:

.. math::
    :label: n_from_v

    n_{i,j} = ndv_i \times v_j

All gears :math:`i` for which :math:`n_{min} \le n_{i,j} \le n_{max}` are possible gears 
to be used for driving the cycle trace at :math:`v_j`.

If :math:`i > 2`,

    .. math::
        :label: n_max_g3+

        n_{max} = 1.2 \times (s - n_{idle}) + n_{idle}

    .. math::
        :label: n_min_g3+

        n_{min} = n_{min\_drive}

If :math:`i = 2` and :math:`ndv_2 \times v_j \ge 0.9 \times n_{idle}`,

    .. math::
        :label: n_min_g2

        n_{min} = max(1.15 \times n_{idle}, 0.03 \times (s - n_{idle}) + n_{idle})

If :math:`ndv_2 \times v_j < max(1.15 \times n_{idle}, 0.03 \times (s - n_{idle}) + n_{idle})`, 
the clutch shall be disengaged.

If :math:`i = 1`,

    .. math::
        :label: n_min_g1

        n_{min} = n_{idle}


Calculation of available power
------------------------------
The available power for each possible gear :math:`i` and each vehicle speed value 
of the cycle trace :math:`v_j` shall be calculated using the following equation:

.. math::
    :label: p_avail

    p_{available\_i,j}=P_{norm\_wot}(n_{norm\ i,j}) \times P_{rated} \times SM

where:

- 
  .. math::
        :label: n_norm

        n_{norm_i,j} = \frac{ndv_i \times v_j - n_{idle}}{s - n_{idle}}

and:

- :math:`P_{rated}` is the rated power, :math:`kW`;
- :math:`P_{norm\_wot}` is the percentage of rated power available at :math:`n_{norm\ i,j}`
  at full load condition from the normalised full load power curve;
- :math:`SM` is a safety margin accounting for the difference between the stationary 
  full load condition power curve and the power available during transition conditions. 
  :math:`SM` is set to :math:`0.9`;
- :math:`n_{idle}` is the idling speed, :math:`min^{-1}`;
- :math:`s` is the rated engine speed.


Determination of possible gears to be used
------------------------------------------
The possible gears to be used shall be determined by the following conditions:

(a) :math:`n_{min} \le n_{i,j} \le n_{max}`
(b) :math:`P_{available\_i,j} \ge P_{required,j}`

The initial gear to be used for each second :math:`j` of the cycle trace is 
the highest final possible gear :math:`i_{max}`.
When starting from standstill, only the first gear shall be used.



Additional requirements for corrections and/or modifications of gear use
========================================================================
The initial gear selection shall be checked and modified in order to avoid too frequent gearshifts 
and to ensure driveability and practicality.

Corrections and/or modifications shall be made according to the following requirements:

(a) First gear shall be selected :math:`1` second before beginning an acceleration phase 
    from standstill with the clutch disengaged. Vehicle speeds below :math:`1\ km/h` imply 
    that the vehicle is standing still;

(b) Gears shall not be skipped during acceleration phases. 
    Gears used during accelerations and decelerations must be used for a period 
    of at least :math:`3` seconds 
    (e.g. a gear sequence :math:`1, 1, 2, 2, 3, 3, 3, 3, 3` shall be replaced by 
    :math:`1, 1, 1, 2, 2, 2, 3, 3, 3`);

(c) Gears may be skipped during deceleration phases. 
    For the last phase of a deceleration to a stop, the clutch may be either disengaged or 
    the gear lever placed in neutral and the clutch left engaged;

(d) There shall be no gearshift during transition from an acceleration phase to a deceleration phase. 
    E.g., if :math:`v_j < v_{j+1} > v_{j+2}` and the gear for the time sequence :math:`j` and
    :math:`j+1` is :math:`i`, gear :math:`i` is also kept for the time :math:`j+2`, 
    even if the initial gear for :math:`j+2` would be :math:`i+1`;

(e) If a gear :math:`i` is used for a time sequence of :math:`1 \text{ to } 5` seconds and 
    the gear before this sequence is the same as the gear after this sequence, e.g. :math:`i-1`, 
    the gear use for this sequence shall be corrected to :math:`i-1`.

    Example:

    (A) a gear sequence :math:`i-1, i, i-1`  is replaced by :math:`i-1, i-1, i-1`;
    (B) a gear sequence :math:`i-1, i, i, i-1`  is replaced by :math:`i-1, i-1, i-1, i-1`;
    (C) a gear sequence :math:`i-1, i, i, i, i-1`  is replaced by :math:`i-1, i-1, i-1, i-1, i-1`;
    (D) a gear sequence :math:`i-1, i, i, i, i, i-1` is replaced by :math:`i-1, i-1, i-1, i-1, i-1, i-1`;
    (E) a gear sequence :math:`i-1, i, i, i, i, i, i-1` is replaced by :math:`i-1, i-1, i-1, i-1, i-1, i-1, i-1`.

    For all cases (A) to (E), :math:`g_{min} \le i` must be fulfilled;

(f) A gear sequence :math:`i, i-1, i` shall be replaced by :math:`i, i, i` if the following 
    conditions are fulfilled:

    (i) Engine speed does not drop below :math:`n_{min}`; and
    (ii) The sequence does not occur more often than four times each for the low, medium and high speed cycle phases 
         and not more than three times for the extra high speed phase.

    Requirement (ii) is necessary as the available power will drop below the required power 
    when the gear :math:`i-1`, is replaced by :math:`i`;

(g) If, during an acceleration phase, a lower gear is required at a higher vehicle speed 
    for at least :math:`2` seconds, the higher gears before shall be corrected to the lower gear.

    Example: The originally calculated gear use is :math:`2, 3, 3, 3, 2, 2, 3`. 
    In this case the gear use will be corrected to :math:`2, 2, 2, 2, 2, 2, 2, 3`.

Since the above modifications may create new gear use sequences which are in conflict with these requirements, 
the gear sequences shall be checked twice.