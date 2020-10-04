:Organization: UNECE/GS-TF
:Date: 8-Feb-2014
:Version: phase-1b
:URL: https://wiki.unece.org/pages/viewpage.action?pageId=2523179

.. include:: <xhtml1-special.txt>

#######
Annex 2
#######

Gear selection and shift point determination for vehicles equipped with manual transmissions
============================================================================================

.. Attention::
    The document below is very outdated (late 2014)!

    It was an attempt to transcribe the :term:`GTR` in :term:`sphinx`,
    in order to track changes in *git*.

General approach
----------------

1. The shifting procedures described in this Annex shall apply to vehicles equipped
   with manual and automatic shift transmissions.

2. The prescribed gears and shifting points are based on the balance between the power required
   to overcome driving resistance and acceleration, and the power provided by the engine
   in all possible gears at a specific cycle phase.

3. The calculation to determine the gears to use shall be based on engine speeds
   and full load power curves versus speed.

4. For vehicles equipped with a two-range transmission (low and high), only the range
   designed for normal on-road operation shall be considered for gear use determination.

5. This annex shall not apply to vehicles tested according to Annex 8.


Required data
-------------
The following data is required to calculate the gears to be used when driving the cycle
on a chassis dynamometer:

(a) :math:`P_{rated}`, the maximum rated engine power as declared by the manufacturer;

(b) :math:`s`, the rated engine speed at which an engine develops its maximum power.
    If the maximum power is developed over an engine speed range, :math:`s` is determined
    by the minimum of this range;

(c) :math:`n_{idle}`, idling speed;

(d) :math:`ng_{max}`, the number of forward gears;

(e) :math:`n_{min\_drive}`, minimum engine speed when the vehicle is in motion.

    - for :math:`n_{gear} = 1`,

      .. math::
          :label: n_min_drive_1

          n_{min\_drive} = n_{idle}

    - for :math:`n_{gear} = 2`,

      .. math::
          :label: n_min_drive_2

          n_{min\_drive} = 0.9 \times n_{idle}

    - for :math:`n_{gear} > 2`, :math:`n_{min\_drive}` is determined by:

      .. math::
          :label: n_min_drive_3+

          n_{min\_drive} = n_{idle} + 0.125 \times (s - n_{idle})

    Higher values may be used if requested by the manufacturer;

(f) :math:`ndv_i`, the ratio obtained by dividing :math:`n` in :math:`min^{-1}`
    by :math:`v` in :math:`km/h` for each gear :math:`i`, :math:`i=1 \text{ to } ng_{max}`;

(g) :math:`TM`, test mass of the vehicle in :math:`kg`;

(h) :math:`f_0, f_1, f_2`, driving resistance coefficients as defined in Annex 4
    in :math:`N`, :math:`N/(km/h)`, and :math:`N/(km/h)^2` respectively;

(i) :math:`ng_{vmax}`, the gear in which the maximum vehicle speed is reached,
    and is determined as follows:

        .. math::
            :label: ng_vmax_1

            ng_{vmax} = ng_{max}\ if\ v_{max}(ng_{max}) \ge v_{max}(ng_{max}-1),

    otherwise:

        .. math::
            :label: ng_vmax_2

            ng_{vmax} = ng_{max} -1

    where:

    - :math:`v_{max}(ng_{max})` is the vehicle speed at which the required
      road load power equals the available power :math:`P_{wot}` in gear :math:`ng_{max}`;

    - :math:`v_{max}(ng_{max}-1)` is the vehicle speed at which the required
      road load power equals the available power :math:`P_{wot}` in the next lower gear.

    - The required road load power shall be calculated as follows:

      .. math::
          :label: p_req_gv_max

          P_{required} =  \frac{f_0 \times v_j + f_1 \times v_j^2 + f_2 \times v_j^3}{3600}

      where:

      - :math:`v_j` is the vehicle speed at second j of the cycle trace, :math:`km/h`.

(j) :math:`n_{max\_95}`, is the minimum engine speed where 95 per cent of rated power is reached;

(k)
    .. math::
        :label: v_max_cycle

        n_{max}(ng_{vmax}) = ndv(ng_{vmax}) \times v_{max,cycle}

    where:

    - :math:`v_{max,cycle}` is the maximum speed of the vehicle speed trace according to Annex 1;

(l) :math:`P_{wot}(n)` is the full load power curve over the engine speed range from idling speed to :math:`n_{max}`.

(m) :math:`P_{wot}(n)` is the full load power curve over the engine speed range from idling speed to :math:`n_{max}`.



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
For any :math:`v_j \le 1\ km/h`, it shall be assumed that the vehicle is standing still and
the engine speed shall be set to :math:`n_{idle}`.
The gear lever shall be placed in neutral with the clutch engaged except one second before beginning
an acceleration phase from standstill where first gear shall be selected with the clutch disengaged.

For each :math:`v_j \ge 1\ km/h` of the cycle trace and each gear :math:`i, i=1 \text{ to } ng_{max}`,
the engine speed :math:`n_{i,j}` shall be calculated using the following equation:

.. math::
    :label: n_from_v

    n_{i,j} = ndv_i \times v_j


Selection of possible gears with respect to engine speed
--------------------------------------------------------
The following gears may be selected for driving the speed trace at :math:`v_j`:

(a) all gears :math:`i < ng_{vmax}` where :math:`n_{min\_drive} \le n_{i,j} \le n_{max\_95}`, and

(b) all gears :math:`i \ge ng_{vmax}` where :math:`n_{min\_drive} \le n_{i,j} \le n_{max}(ng_{vmax})`

If :math:`aj \le 0` and :math:`n_{i,j}` drops below :math:`n_{idle}`, :math:`n_{i,j}` shall be set
to :math:`n_{idle}` and the clutch shall be disengaged.

If :math:`aj > 0` and :math:`n_{i,j}` drops below :math:`(1.15 \times n_{idle})`, :math:`n_{i,j}` shall be set
to :math:`(1.15 \times n_{idle})` and the clutch shall be disengaged.


Calculation of available power
------------------------------
The available power for each possible gear :math:`i` and each vehicle speed value
of the cycle trace :math:`v_j` shall be calculated using the following equation:

.. math::
    :label: p_avail

    p_{available\_i,j} = P_{wot}(n_{i,j}) \times (1-(SM + ASM))

where:

- :math:`P_{rated}` is the rated power, :math:`kW`;
- :math:`P_{wot}` is the power available at :math:`n_{i,j}` at full load condition
  from the full load power curve;
- :math:`SM` is a safety margin accounting for the difference between the stationary
  full load condition power curve and the power available during transition conditions.
  :math:`SM` is set to :math:`10` per cent;
- :math:`ASM` is an additional exponential power safety margin, which may be applied
  at the request of the manufacturer.
  :math:`ASM` is fully effective between :math:`n_{idle}` and :math:`n_{start}`, and
  exponentially approaching :math:`0` at :math:`n_{end}` as described by the following requirements:

  If :math:`n \le n_{start}`, then

      .. math::
          :label: asm_1

          ASM = ASM_0

  If :math:`n > n_{start}`, then

      .. math::
          :label: asm_2

          ASM = ASM_0 \times exp(ln(\frac{0.005}{ASM_0}) \times \frac {n_{start} - n}{n_{start} - n_{end}})

  :math:`ASM_0, n_{start}` and :math:`n_{end}` shall be defined by the manufacturer but
  must fulfill the following conditions:

  .. math::

      n_{start} \ge n_{idle},

      n_{end} > n_{start}


Determination of possible gears to be used
------------------------------------------
The possible gears to be used shall be determined by the following conditions:

(a) The conditions of paragraph 3.3. are fulfilled, and
(b) :math:`P_{available\_i,j} \ge P_{required,j}`

The initial gear to be used for each second :math:`j` of the cycle trace is
the highest final possible gear :math:`i_{max}`.
When starting from standstill, only the first gear shall be used.



Additional requirements for corrections and/or modifications of gear use
========================================================================
The initial gear selection shall be checked and modified in order to avoid too frequent gearshifts
and to ensure driveability and practicality.

An acceleration phase is a time period of more than 3 seconds with a vehicle speed :math:`\ge 1\ km/h` and
with monotonic increase of the vehicle speed.
A deceleration phase is a time period of more than :math:`3` seconds with a vehicle speed :math:`\ge 1 km/h` and
with monotonic decrease of the vehicle speed.
Corrections and/or modifications shall be made according to the following requirements:

(a) Gears used during accelerations shall be used for a period of at least :math:`2` seconds
    (e.g. a gear sequence :math:`1, 2, 3, 3, 3, 3, 3` shall be replaced by :math:`1, 1, 2, 2, 3, 3, 3, 3, 3`).
    Gears shall not be skipped during acceleration phases.

(b) If a lower gear is required at a higher vehicle speed for at least :math:`2` seconds during
    an acceleration phase, the higher gears before shall be corrected to the lower gear.

(c) During a deceleration phase, gears with :math:`n_{gear} > 2` shall be used as long as
    the engine speed does not drop below :math:`n_{min\_drive}`.
    If a gear sequence lasts between :math:`1` and :math:`2` seconds, it shall be replaced by
    gear :math:`0` for the first second and the next lower gear for the second second.
    The clutch shall be disengaged for the first second.
    Gear :math:`0` is where the clutch is disengeged.

(d) The second gear shall be used during a deceleration phase within a short trip of the cycle as long as
    the engine speed does not drop below :math:`0.9 \times n_{idle}`.
    If the engine speed drops below :math:`n_{idle}`, the clutch shall be disengaged.

(e) If the deceleration phase is the last part of a short trip shortly before a stop phase and
    the second gear would only be used for up to two seconds, the gear shall be set to :math:`0` and
    the clutch may be either disengaged or the gear lever placed in neutral and the clutch left engaged.
    A downshift to first gear is not permitted during those deceleration phases.

(f) If gear :math:`i` is used for a time sequence of :math:`1 \text{ to } 5` seconds and
    the gear before this sequence is the same as the gear after this sequence, e.g. :math:`i-1`,
    the gear to be used for this sequence shall be corrected to :math:`i-1`.

    Example:

    (A) gear sequence :math:`i-1, i, i-1` shall be replaced by :math:`i-1, i-1, i-1`;
    (B) gear sequence :math:`i-1, i, i, i-1` shall be replaced by :math:`i-1, i-1, i-1, i-1`;
    (C) gear sequence :math:`i-1, i, i, i, i-1` shall be replaced by :math:`i-1, i-1, i-1, i-1, i-1`;
    (D) gear sequence :math:`i-1, i, i, i, i, i-1` shall be replaced by :math:`i-1, i-1, i-1, i-1, i-1, i-1`;
    (E) gear sequence :math:`i-1, i, i, i, i, i, i-1` shall be replaced by :math:`i-1, i-1, i-1, i-1, i-1, i-1, i-1`.

    In all example cases above, :math:`g_{min} \le i` must be fulfilled;

(g) Any gear sequence :math:`i, i-1, i` shall be replaced by :math:`i, i, i` if the following
    conditions are fulfilled:

    (i) engine speed does not drop below :math:`n_{min}`; and
    (ii) the sequence does not occur more often than four times for each of the low, medium and high speed cycle phases
         and not more than three times for the extra high speed phase.

    Requirement (ii) is necessary as the available power will drop below the required power
    when the gear :math:`i-1`, is replaced by :math:`i`;

(h) If, during an acceleration phase, a lower gear is required at a higher vehicle speed
    for at least :math:`2` seconds, the higher gears before shall be corrected to the lower gear.

    Example: The originally calculated gear use is :math:`2, 3, 3, 3, 2, 2, 3`.
    In this case the gear use will be corrected to :math:`2, 2, 2, 2, 2, 2, 2, 3`.

Since the above modifications may create new gear use sequences which are in conflict with these requirements,
the gear sequences shall be checked twice.
Paragraphs 4.(a) to 4.(g) shall be applied in in succession and only after each has completely finished scanning the gear-profile.


Discussion
----------
.. raw:: html

    <div id="disqus_thread"></div>
    <script type="text/javascript">
        /* * * CONFIGURATION VARIABLES: EDIT BEFORE PASTING INTO YOUR WEBPAGE * * */
        var disqus_shortname = 'wltp';
        var disqus_identifier = 'site.annex2';
        var disqus_title = 'wltp: Annex 2';

        /* * * DON'T EDIT BELOW THIS LINE * * */
        (function() {
            var dsq = document.createElement('script'); dsq.type = 'text/javascript'; dsq.async = true;
            dsq.src = '//' + disqus_shortname + '.disqus.com/embed.js';
            (document.getElementsByTagName('head')[0] || document.getElementsByTagName('body')[0]).appendChild(dsq);
        })();
    </script>
    <noscript>Please enable JavaScript to view the <a href="http://disqus.com/?ref_noscript">comments powered by Disqus.</a></noscript>

.. include:: ../README.rst
    :start-after: _begin-replacements:
