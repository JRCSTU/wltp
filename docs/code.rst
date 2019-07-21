API reference
=============
The core of the simulator is composed from the following modules:

.. currentmodule:: wltp
.. autosummary::

    model
    experiment
    idgears


Module: :mod:`wltp.experiment`
------------------------------
.. automodule:: wltp.experiment
    :members:

Module: :mod:`wltp.model`
-------------------------
.. automodule:: wltp.model
    :members:

Schema
^^^^^^

.. doctest:: model_text

    >>> from wltp import model, utils
    >>> schema = model._get_model_schema()
    >>> print(utils.yaml_dumps(schema))
    $schema: http://json-schema.org/draft-07/schema#
    $id: /model
    title: Json-schema describing the input for a WLTC experiment.
    type: object
    additionalProperties: false
    required:
    - vehicle
    properties:
      vehicle:
        title: vehicle model
        type: object
        additionalProperties: false
        required:
        - test_mass
        - p_rated
        - n_rated
        - n_idle
        - gear_ratios
        - full_load_curve
        description: The vehicle attributes required for generating the WLTC velocity-profile
          downscaling and gear-shifts.
        properties:
          id:
            title: Any identifier for the object
            type:
            - integer
            - string
          unladen_mass:
            title: vehicle unladen mass
            type:
            - number
            - 'null'
            exclusiveMinimum: 0
            description: The mass (kg) of the vehicle without the driver, used to decide
              its class, as defined in Annex-4
          test_mass:
            title: vehicle test mass
            $ref: '#/definitions/positiveNumber'
            description: The test mass of the vehicle used in all calculations (kg), as
              defined in Annex 4.2.1.3.1, pg 94.
          v_max:
            title: maximum vehicle velocity
            type:
            - number
            - 'null'
            exclusiveMinimum: 0
            description: The calculcated maximum velocity, as defined in Annex 2-3.i.
          p_rated:
            title: maximum rated power
            $ref: '#/definitions/positiveNumber'
            description: The maximum rated engine power (kW) as declared by the manufacturer.
          n_rated:
            title: rated engine revolutions
            $ref: '#/definitions/positiveNumber'
            description: |
              The rated engine revolutions at which an engine develops its maximum power.
              If the maximum power is developed over an engine revolutions range,
              it is determined by the mean of this range.
          n_idle:
            title: idling revolutions
            $ref: '#/definitions/positiveNumber'
            description: The idling engine revolutions (Annex 1).
          n_min:
            title: minimum engine revolutions
            type:
            - array
            - integer
            - 'null'
            description: |
              Either a number with the minimum engine revolutions for gears > 2 when the vehicle is in motion,
              or an array with the exact `n_min` for each gear (array must have length equal to gears).
    <BLANKLINE>
              If unspecified, the minimum `n` for gears > 2 is determined by the following equation:
    <BLANKLINE>
                  n_min = n_idle + f_n_min(=0.125) * (n_rated - n_idle)
    <BLANKLINE>
              Higher values may be used if requested by the manufacturer, by setting this one.
          gear_ratios:
            title: gear ratios
            $ref: '#/definitions/positiveNumbers'
            maxItems: 24
            minItems: 3
            description: An array with the gear-ratios obtained by dividing engine-revolutions
              (1/min) by vehicle-velocity (km/h).
          resistance_coeffs:
            title: driving resistance coefficients
            type:
            - 'null'
            - array
            items:
              type: number
            minItems: 3
            maxItems: 3
            description: |
              The 3 driving resistance coefficients f0, f1, f2,
              in N, N/(km/h), and N/(km/h)² respectively (Annex 4).
    <BLANKLINE>
              If not specified, they are determined based on `test_mass` from
              a pre-calculated regression curve:
    <BLANKLINE>
                  f0 = a00 * test_mass + a01,
                  f1 = a10 * test_mass + a11,
                  f2 = a20 * test_mass + a21,
    <BLANKLINE>
              where `a00, ..., a22` specified in `/params`.
          full_load_curve:
            title: full load power curve
            description: |
              An array/dict/dataframe holding the P_wot curve in (at least) 2 columns
              Example:
    <BLANKLINE>
                  np.array([
                      [ 600, 1000, ... 7000 ],
                      [ 4, 10, ... 30 ]
                  ]).T
    <BLANKLINE>
              * The 1st column or `n` is the engine revolutions in min^-1:
              * The 2nd column or `p` is the full-power load in kW:
    <BLANKLINE>
            type:
            - object
            - array
            - 'null'
          norm_full_load_curve:
            title: full load power curve
            description: |
              An array/dict/dataframe holding the full load power curve in (at least) 2 columns
              Example:
    <BLANKLINE>
                  np.array([
                      [ 0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120 ],
                      [ 6.11, 21.97, 37.43, 51.05, 62.61, 72.49, 81.13, 88.7, 94.92, 98.99, 100., 96.28, 87.66 ]
                  ]).T
    <BLANKLINE>
              * The 1st column or `n_norm` is the normalized engine revolutions, within [0.0, 1.20]:
    <BLANKLINE>
                          n_norm = (n - n_idle) / (n_rated  - n_idle)
    <BLANKLINE>
              * The 2nd column or `p_norm` is the normalised values of the full-power load against the p_rated,
                within [0, 1]:
    <BLANKLINE>
                          p_norm = p / p_rated
            type:
            - object
            - array
            - 'null'
          pmr:
            title: Power to Unladen-Mass
            description: Power/unladen-Mass ratio (W/kg).
            type: number
          wltc_class:
            description: The name of the WLTC-class (found within WLTC-data/classes) as
              selected by the experiment.
            type: string
            enum:
            - class1
            - class2
            - class3a
            - class3b
      params:
        title: experiment parameters
        type: object
        additionalProperties: false
        required:
        - resistance_coeffs_regression_curves
        - driver_mass
        - v_stopped_threshold
        - f_inertial
        - f_safety_margin
        - f_n_min
        - f_n_min_gear2
        - f_n_clutch_gear2
        - wltc_data
        properties:
          resistance_coeffs_regression_curves:
            description: Regression curve factors for calculating vehicle's `resistance_coeffs`
              when missing.
            type: array
            minItems: 3
            maxItems: 3
            items:
              type: array
              minItems: 2
              maxItems: 2
              items:
                type: number
          f_downscale_threshold:
            title: Downscale-factor threshold
            description: The limit for the calculated `f_downscale` below which no downscaling
              happens.
            type:
            - number
            - 'null'
            default: 0.01
          f_downscale_decimals:
            title: Downscale-factor rounding decimals
            type:
            - number
            - 'null'
            default: 3
          driver_mass:
            title: Driver's mass (kg)
            description: |
              The mass (kg) of the vehicle's driver (Annex 1-3.2.6, p9), where: 
    <BLANKLINE>
                  Unladen_mass = Test_mass - driver_mass
            type:
            - number
            - 'null'
            default: 75
          v_stopped_threshold:
            description: Velocity (km/h) under which (<=) to idle gear-shift (Annex 2-3.3,
              p71).
            type:
            - number
            - 'null'
            default: 1
          f_inertial:
            description: This is the `kr` inertial-factor used in the 2nd part of the
              formula for calculating required-power (Annex 2-3.1, p71).
            type:
            - number
            - 'null'
            default: 1.03
          f_safety_margin:
            description: |
              Safety-margin factor for load-curve due to transitional effects (Annex 2-3.3, p72).
              If array, its length must match those of the `gear_ratios`.
            type:
            - array
            - number
            - 'null'
            default: 0.9
          f_n_min:
            description: For each gear > 2, N :> n_min = n_idle + f_n_min * n_range (unless
              `n_min` overriden by manufacturer)
            type:
            - number
            - 'null'
            default: 0.125
          f_n_min_gear2:
            description: Gear-2 is invalid when N :< f_n_min_gear2 * n_idle.
            type:
            - number
            - 'null'
            default: 0.9
          f_n_clutch_gear2:
            description: |
              A 2-value number-array(f1, f2) controlling when to clutch gear-2:
                  N < n_clutch_gear2 := max(f1 * n_idle, f2 * n_range + n_idle),
              unless "clutched"...
            type:
            - array
            - 'null'
            default:
            - 1.15
            - 0.03
          f_downscale:
            description: The downscaling-factor as calculated by the experiment (Annex
              1-7.3, p68).
            type: number
          wltc_data:
            $ref: /wltc
      cycle_run: {}
    definitions:
      positiveInteger:
        type: integer
        exclusiveMinimum: 0
      positiveNumber:
        type: number
        exclusiveMinimum: 0
      positiveIntegers:
        type: array
        items:
          $ref: '#/definitions/positiveInteger'
      positiveNumbers:
        type: array
        items:
          $ref: '#/definitions/positiveNumber'


Automatic tests
---------------
Among the various tests, those running on 'sample' databases for comparing differences
with existing tool are the following:

.. currentmodule:: tests
.. autosummary::

    test_samples_db
    test_wltp_db

The following scripts in the sources maybe used to preprocess various wltc data:

* :file:`devtools/preprocheinz.py`
* :file:`devtools/printwltcclass.py`
* :file:`devtools/csvcolumns8to2.py`

Module: :mod:`tests.test_samples_db`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
(abandoned)

.. automodule:: tests.test_samples_db
    :members:

Module: :mod:`tests.test_wltp_db`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
(abandoned)

.. automodule:: tests.test_wltp_db
    :members:

