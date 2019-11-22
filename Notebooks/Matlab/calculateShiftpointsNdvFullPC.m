function [ ...
  CalculatedGearsOutput ...
, AverageGearOutput ...
, AdjustedMax95EngineSpeed ...
, TraceTimesOutput ...
, RequiredVehicleSpeedsOutput ...
, RequiredPowersOutput ...
, RequiredEngineSpeedsOutput ...
, AvailablePowersOutput ...
, PowerCurveOutput ...
, MaxEngineSpeedCycleOutput ...
, MaxEngineSpeedReachableOutput ...
, MaxEngineSpeedOutput ...
, MaxVehicleSpeedCycleOutput ...
, MaxVehicleSpeedReachableOutput ...
, GearMaxVehicleSpeedReachableOutput ...
, MinDriveEngineSpeed1stOutput ...
, MinDriveEngineSpeed1stTo2ndOutput ...
, MinDriveEngineSpeed2ndDecelOutput ...
, MinDriveEngineSpeed2ndOutput ...
, MinDriveEngineSpeedGreater2ndOutput ...
, GearsOutput ...
, ClutchDisengagedOutput ...
, ClutchUndefinedOutput ...
, ClutchHSTOutput ...
, GearCorrectionsOutput ...
, ChecksumVxGearOutput ...
] = calculateShiftpointsNdvFullPC ( ...
  RatedEnginePower ...
, RatedEngineSpeed ...
, IdlingEngineSpeed ...
, Max95EngineSpeed ...
, NoOfGears ...
, VehicleTestMass ...
, f0 ...
, f1 ...
, f2 ...
, Ndv ...
, FullPowerCurve ...
, Trace ...
, SafetyMargin ...
, AdditionalSafetyMargin0 ...
, StartEngineSpeed ...
, EndEngineSpeed ...
, MinDriveEngineSpeed1st ...
, MinDriveEngineSpeed1stTo2nd ...
, MinDriveEngineSpeed2ndDecel ...
, MinDriveEngineSpeed2nd ...
, MinDriveEngineSpeedGreater2nd ...
, EngineSpeedLimitVMax ...
, MaxTorque ...
, ExcludeCrawlerGear ...
, AutomaticClutchOperation ...
, SuppressGear0DuringDownshifts ...
, MinDriveEngineSpeedGreater2ndAccel ...
, MinDriveEngineSpeedGreater2ndDecel ...
, MinDriveEngineSpeedGreater2ndAccelStartPhase ...
, MinDriveEngineSpeedGreater2ndDecelStartPhase ...
, TimeEndOfStartPhase ...
, DoNotMergeClutchIntoGearsOutput ...
)

% calculateShiftpointsNdvFullPC Determines shift-points over trace-time
%
%   1.  RatedEnginePower
%       Annex 2 (2a) P_rated
%       This is a legacy parameter used until regulation GRPE-75-23.
%       The maximum rated engine power as declared by the manufacturer.
%       But the newer regulation GRPE/2018/2 Annex 2 (2g) now requires :
%       The data sets and the values P_rated and n_rated
%       shall be taken from the power curve as declared by the manufacturer.
%       For backward compatibility this parameter may still be used
%       to override the value calculated from FullPowerCurve.
%       Set RatedEnginePower and RatedEngineSpeed to 0
%       to use the calculated values.
%       [kW]
%
%   2.  RatedEngineSpeed
%       Annex 2 (2b) n_rated
%       This is a legacy parameter used until regulation GRPE-75-23.
%       The rated engine speed at which an engine
%       declared by the manufacturer as the engine speed
%       at which the engine develops its maximum power.
%       But the newer regulation GRPE/2018/2 Annex 2 (2g) now requires :
%       The data sets and the values P_rated and n_rated
%       shall be taken from the power curve as declared by the manufacturer.
%       For backward compatibility this parameter may still be used
%       to override the value calculated from FullPowerCurve.
%       Set RatedEnginePower and RatedEngineSpeed to 0
%       to use the calculated values.
%       [1/min]
%
%   3.  IdlingEngineSpeed
%       Annex 2 (2c) n_idle
%       The idling speed.
%       [1/min]
%
%   4.  Max95EngineSpeed
%       Annex 2 (2g) n_max1 = n_95_high
%       The maximum engine speed where 95 per cent of rated power is reached.
%       If the dummy value 0 will be given for this parameter
%       then n_max1 will be calculated from parameter FullPowerCurve P_wot.
%       [1/min]
%
%   5.  NoOfGears
%       Annex 2 (2d) ng
%       The number of forward gears.
%       [integer]
%
%   6.  VehicleTestMass
%       Annex 2 (2l) TM
%       The test mass of the vehicle.
%       [kg]
%
%   7.  f0
%       Annex 2 (2f) f_0
%       The constant road load coefficient,
%       i.e. independent of velocity, caused by internal frictional resistances.
%       [N]
%
%   8.  f1
%       Annex 2 (2f) f_1
%       The linear road load coefficient,
%       i.e. proportional to velocity, caused by tyres rolling resistances.
%       [N/(km/h)]
%
%   9.  f2
%       Annex 2 (2f) f_2
%       The quadratic road load coefficient,
%       i.e. quadratical to velocity, caused by aerodynamic resistances.
%       [N/(km/h)^2]
%
%   10. Ndv
%       Annex 2 (2e) i ==> (n/v)_i
%       The ratio obtained by dividing the engine speed n by the vehicle speed v
%       for each gear i form 1 to ng.
%       [integer] ==> [(1/min)/(km/h)]
%
%   11. FullPowerCurve
%       Annex 2 (2h) and (3.4) n ==> P_wot(n), ASM
%       The full load power curve over the engine speed range.
%       The power curve shall consist of a sufficient number of data sets (n,Pwot)
%       so that the calculation of interim points between consecutive data sets
%       can be performed by linear interpolation.
%       ASM is an additional power safety margin,
%       which may be applied at the request of the manufacturer.
%       It will be defined by an additional column of FullPowerCurve
%       since regulation ECE-TRANS-WP29-GRPE-2017-07.
%       [1/min]  ==> [kW], [%]
%
%   12. Trace
%       Annex 1 (eg 8.3) i ==> v_i
%       The vehicle speed at second i.
%       [s] ==> [km/h]
%
%   13. SafetyMargin
%       Annex 2 (3.4) SM
%       The safety margin is accounting for the difference
%       between the stationary full load condition power curve
%       and the power available during transition conditions.
%       SM is set to 10 per cent.
%       [%]
%
%   14. AdditionalSafetyMargin0
%       This is a legacy parameter used until regulation GRPE-72-10-Rev.2.
%       Later regulations define the additional safety margin values
%       as part of the FullPowerCurve.
%       GRPE-72-10-Rev.2 Annex 2 (3.4) ASM_0 * 100 %
%       The additional exponential power safety margin
%       may be applied at the request of the manufacturer.
%       ASM is fully effective between n_idle and n_start,
%       and approaches zero exponentially at n_end.
%       [%]
%
%   15. StartEngineSpeed
%       This is a legacy parameter used until regulation GRPE-72-10-Rev.2.
%       GRPE-72-10-Rev.2 Annex 2 (3.4) n_start
%       The engine speed at which ASM approching zero starts.
%       [1/min]
%
%   16. EndEngineSpeed
%       This is a legacy parameter used until regulation GRPE-72-10-Rev.2.
%       GRPE-72-10-Rev.2 Annex 2 (3.4) n_end
%       The engine speed at which ASM approching zero ends.
%       [1/min]
%
%   17. MinDriveEngineSpeed1st
%       This is a legacy parameter used until regulation GRPE-75-23.
%       This value may be used to increase the calculated value.
%       Annex 2 (2k) n_min_drive = n_idle for n_gear:1
%       The minimum engine speed when the vehicle is in motion.
%       [1/min]
%
%   18. MinDriveEngineSpeed1stTo2nd
%       This is a legacy parameter used until regulation GRPE-75-23.
%       This value may be used to increase the calculated value.
%       Annex 2 (2ka) n_min_drive = 1.15 x n_idle for n_gear:1->2
%       The minimum engine speed for transitions from first to second gear.
%       [1/min]
%
%   19. MinDriveEngineSpeed2ndDecel
%       This is a legacy parameter used until regulation GRPE-75-23.
%       This value may be used to increase the calculated value.
%       Annex 2 (2kb) n_min_drive = n_idle for n_gear:2
%       The minimum engine speed for decelerations to standstill in second gear.
%       [1/min]
%
%   20. MinDriveEngineSpeed2nd
%       This is a legacy parameter used until regulation GRPE-75-23.
%       This value may be used to increase the calculated value.
%       Annex 2 (2kc) n_min_drive = 0.9 x n_idle for n_gear:2
%       The minimum engine speed for all other driving conditions in second gear.
%       [1/min]
%
%   21. MinDriveEngineSpeedGreater2nd
%       This is a legacy parameter used until regulation GRPE-75-23.
%       This value may be used to increase the calculated value.
%       Annex 2 (2k) n_min_drive = n_idle + 0.125 × ( n_rated - n_idle ) for n_gear:3..
%       This value shall be referred to as n_min_drive_set.
%       The minimum engine speed for all driving conditions in gears greater than 2.
%       [1/min]
%
%   22. EngineSpeedLimitVMax
%       Annex 2, (2i) n_lim
%       The maximum engine speed for the purpose of limiting maximum vehicle speed. 
%       (value 0 means unlimited vehicle speed)
%       [1/min]
%
%   23. MaxTorque
%       This parameter is not used so far.
%       It was intended to be used for the calculation of n_min_drive
%       by earlier regulation proposals.
%       [Nm]
%
%   24. ExcludeCrawlerGear
%       Annex 2 (2j)
%       Gear 1 may be excluded at the request of . the manufacturer if ...
%       [boolean]
%
%   25. AutomaticClutchOperation
%       Annex 2 (1.5)
%       The prescriptions for the clutch operation shall not be applied
%       if the clutch is operated automatically
%       without the need of an engagement or disengagement of the driver.
%       [boolean]
%
%   26. SuppressGear0DuringDownshifts
%       Annex 2 (4f)
%       If a gear is used for only 1 second during a deceleration phase
%       it shall be replaced by gear 0 with clutch disengaged,
%       in order to avoid too high engine speeds.
%       But if this is not an issue, the manufacturer may allow to use
%       the lower gear of the following second directly instead of gear 0
%       for downshifts of up to 3 steps.
%       [boolean]
%
%   27. MinDriveEngineSpeedGreater2ndAccel
%       Annex 2 (2j) n_min_drive_up
%       Values higher than n_min_drive_set may be used for n_gear > 2.
%       The manufacturer may specify a value
%       for acceleration/constant speed phases (n_min_drive_up).
%       [1/min]
%
%   28. MinDriveEngineSpeedGreater2ndDecel
%       Annex 2 (2j) n_min_drive_down
%       Values higher than n_min_drive_set may be used for n_gear > 2.
%       The manufacturer may specify a value
%       for deceleration phases (n_min_drive_down).
%       [1/min]
%
%   29. MinDriveEngineSpeedGreater2ndAccelStartPhase
%       Annex 2 (2j) n_min_drive_up_start
%       Heinz Steven Tool n_min_drive_start_up
%       For an initial period of time (t_start_phase),
%       the manufacturer may specify higher values
%       (n_min_drive_start and/or n_min_drive_up_start)
%       for the values n_min_drive and/or n_min_drive_up
%       for n_gear > 2.
%       This requirement was implemented with other parameters
%       by the reference implementation Heinz Steven Tool.
%       This tool uses the parameter names
%       n_min_drive_start_up and n_min_drive_start_down.
%       The input parameter here correponds with n_min_drive_start_up.
%       [1/min]
%
%   30. MinDriveEngineSpeedGreater2ndDecelStartPhase
%       Annex 2 (2j) n_min_drive_start
%       Heinz Steven Tool n_min_drive_start_down
%       For an initial period of time (t_start_phase),
%       the manufacturer may specify higher values
%       (n_min_drive_start and/or n_min_drive_up_start)
%       for the values n_min_drive and/or n_min_drive_up
%       for n_gear > 2.
%       This requirement was implemented with other parameters
%       by the reference implementation Heinz Steven Tool.
%       This tool uses the parameter names
%       n_min_drive_start_up and n_min_drive_start_down.
%       The input parameter here correponds with n_min_drive_start_down.
%       [1/min]
%
%   31. TimeEndOfStartPhase
%       Annex 2 (2j) t_start_phase
%       For an initial period of time (t_start_phase),
%       the manufacturer may specify higher values
%       (n_min_drive_start and/or n_min_drive_up_start)
%       for the values n_min_drive and/or n_min_drive_up
%       for n_gear > 2.
%       The input parameter here is used in combination with
%       MinDriveEngineSpeedGreater2ndAccelStartPhase and
%       MinDriveEngineSpeedGreater2ndDecelStartPhase.
%       NOTE:
%       if eg TimeEndOfStartPhase = 100
%       then trace times 0..100 will be affected
%       which are stored in TraceTimes(1:101) 
%       Set TimeEndOfStartPhase = -1 to ignore start phase.
%       [s]
%
%   32. DoNotMergeClutchIntoGearsOutput
%       Only if false
%       then ClutchDisengaged will be merge into GearsOutput during deceleration phases
%       an when starting from standstill clutch will be indicated 1 sec before use of 1st gear.                                
%       [boolean]
%   
% Calculated results include:
%
%   1.  CalculatedGearsOutput
%       Annex 2 (3.5) gears to be used
%       This is the main result of the gear shift calculation.
%       The gear to be used will not be indicated for each second of the trace.
%       Only the gear changes will be indicated together with correponding trace second.
%       As a clutch disengagement will be indicated like a gear change,
%       a clutch disengagement and a gear change cannot be indicated at the same time
%       and the clutch disengagement will therefore be indicated one second earlier.
%       [s] ==> [text]
%
%   2.  AverageGearOutput
%       Annex 2 (5) average gear
%       In order to enable the assessment of the correctness of the calculation,
%       the average gear for v >= 1 km/h, rounded to four places of decimal,
%       shall be calculated and recorded.
%       [real]
%
%   3.  AdjustedMax95EngineSpeed
%       Annex 2 (2g) n_max1 = n_95_high adjusted
%       If n_95_high cannot be determined
%       because the engine speed is limited to a lower value n_lim for all gears
%       and the corresponding full load power is higher than 95 per cent of rated power,
%       n_95_high shall be set to n_lim.
%       [1/min]
%
%   4.  TraceTimesOutput
%       Annex 1 (eg 8.3) i interpolated
%       The interpolated trace times (second-by-second).
%       [s]
%
%   5.  RequiredVehicleSpeedsOutput
%       Annex 1 (eg 8.3) v_i interpolated
%       The interpolated vehicle speeds (second-by-second).
%       [km/h]
%
%   6.  RequiredPowersOutput
%       Annex 2 (3.1) P_required,j
%       The power required to overcome driving resistance and to accelerate
%       for each second j of the cycle trace.
%       [kW]
%
%   7.  RequiredEngineSpeedsOutput
%       Annex 2 (3.2) n_i,j
%       The engine speeds required
%       for each gear i from 1 to ng and
%       for each second j of the cycle trace.
%       Note that this are the uncorrected values n_i,j
%       ie without the increments required by Annex 2 (3.3)
%       [1/min]
%
%   8.  AvailablePowersOutput
%       Annex 2 (3.4) P_available_i,j
%       The power available
%       for each gear i from 1 to ng and
%       for each second j of the cycle trace.
%       Note that this power values are determined from uncorrected values n_i,j
%       ie without the engine speed increments required by Annex 2 (3.3)
%       [kW]
%
%   9.  PowerCurveOutput
%       Contains the same data as input parameter FullPowerCurve.
%       But if FullPowerCurve does not contain any ASM values
%       this values will be calculated from the input parameters
%       - AdditionalSafetyMargin0
%       - StartEngineSpeed
%       - EndEngineSpeed
%       and will be used for the shift point calculation
%       and filled in the output parameter PowerCurveOutput.
%       [1/min]  ==> [kW], [%]
%
%   10. MaxEngineSpeedCycleOutput
%       Annex 2 (2g) n_max2
%       n_max2 = (n/v)(ng_vmax) * v_max,cycle
%       ie the engine speed for the maximum vehicle speed of the trace
%       using the gear in which the maximum vehicle speed can be reached.
%       [1/min]
%
%   11. MaxEngineSpeedReachableOutput
%       Annex 2 (2g) n_max3 
%       n_max3 = (n/v)(ng_vmax) * v_max,vehicle
%       ie the engine speed for the maximum vehicle speed reachable
%       using the gear in which the maximum vehicle speed can be reached.
%       [1/min]
%
%   12. MaxEngineSpeedOutput
%       Annex 2 (2g, 2h) n_max 
%       n_max is the maximum of n_max1, n_max2 and n_max3
%       The power curve shall consist of a sufficient number of data sets ...
%       The last data set shall be at n_max or higher engine speed. 
%       [1/min]
%
%   13. MaxVehicleSpeedCycleOutput
%       Annex 2 (2g) v_max,cycle 
%       The maximum vehicle speed of the trace
%       using the gear in which the maximum vehicle speed can be reached.
%       [km/h]
%
%   14. MaxVehicleSpeedReachableOutput
%       Annex 2 (2g, 2i) v_max,vehicle
%       The maximum vehicle speed reachable
%       using the gear in which the maximum vehicle speed can be reached.
%       [km/h]
%
%   15. GearMaxVehicleSpeedReachableOutput
%       Annex 2 (2i) ng_vmax 
%       The gear in which the maximum vehicle speed is reached.  
%       [integer]
%
%   16. MinDriveEngineSpeed1stOutput
%       Annex 2 (2k) n_min_drive = n_idle for n_gear:1
%       The minimum engine speed when the vehicle is in motion.
%       This is the maximum of calculated value and input parameter value.  
%       [1/min]
%
%   17. MinDriveEngineSpeed1stTo2ndOutput
%       Annex 2 (2ka) n_min_drive = 1.15 x n_idle for n_gear:1->2
%       The minimum engine speed for transitions from first to second gear.
%       This is the maximum of calculated value and input parameter value.  
%       [1/min]
%
%   18. MinDriveEngineSpeed2ndDecelOutput
%       Annex 2 (2kb) n_min_drive = n_idle for n_gear:2
%       The minimum engine speed for decelerations to standstill in second gear.
%       This is the maximum of calculated value and input parameter value.  
%       [1/min]
%
%   19. MinDriveEngineSpeed2ndOutput
%       Annex 2 (2kc) n_min_drive = 0.9 x n_idle for n_gear:2
%       The minimum engine speed for all other driving conditions in second gear.
%       This is the maximum of calculated value and input parameter value.  
%       [1/min]
%
%   20. MinDriveEngineSpeedGreater2ndOutput
%       Annex 2 (2k) n_min_drive = n_idle + 0.125 × ( n_rated - n_idle ) for n_gear:3..
%       This value shall be referred to as n_min_drive_set.
%       The minimum engine speed for all driving conditions in gears greater than 2.
%       This is the maximum of calculated value and input parameter value.  
%       [1/min]
%
%   21. GearsOutput
%       Array of gears copied from InitialGears,
%       which are also merged into the parameter GearsOutput.
%       Opposite to CalculatedGearsOutput the gear values are not condensed here.
%       [s] ==> [integer]
%
%   22. ClutchDisengagedOutput
%       Array of booleans copied from ClutchDisengaged,
%       which are also merged into the parameter GearsOutput.
%       Opposite to CalculatedGearsOutput the clutch values are not condensed here.
%       [s] ==> [boolean]
%
%   23. ClutchUndefinedOutput
%       Array of booleans copied from ClutchUndefined,
%       which dicriminates clutch disengaged sub-states. 
%       [s] ==> [boolean]
%
%   24. ClutchHSTOutput
%       CellArray of clutch state names as used by the Heinz Steven Tool (HST).
%       [s] ==> [text]
%
%   25. GearCorrectionsOutput
%       CellArray of gear correction strings for debugging.
%       [s] ==> [text]
%
%   26. ChecksumVxGearOutput
%       Checksum of v * gear for v >= 1 km/h rounded to four places of decimal
%       [1]


%% Preprocess inputs

% Check number of inputs and outputs
narginchk(32, 32);
nargoutchk(26, 26);

validateattributes(RatedEnginePower, ...
	{'double'}, ...
	{'scalar', 'nonnegative'}, ...  % zero if to be calculated
	mfilename, 'RatedEnginePower', 1);

validateattributes(RatedEngineSpeed, ...
	{'double'}, ...
	{'scalar', 'nonnegative'}, ...  % zero if to be calculated
	mfilename, 'RatedEngineSpeed', 2);

validateattributes(IdlingEngineSpeed, ...
	{'double'}, ...
	{'scalar', 'positive'}, ...
	mfilename, 'IdlingEngineSpeed', 3);

% Round the idling speed to the nearest 10 (2c)
IdlingEngineSpeed = round(IdlingEngineSpeed/10)*10;
 
validateattributes(Max95EngineSpeed, ...
	{'double'}, ...
	{'scalar', 'nonnegative'}, ...  % zero if to be calculated
	mfilename, 'Max95EngineSpeed', 4);

validateattributes(NoOfGears, ...
	{'int32'}, ...
	{'scalar', 'integer', 'positive'}, ...
	mfilename, 'NoOfGears', 5);

validateattributes(VehicleTestMass, ...
	{'scalar', 'double'}, ...
	{'positive'}, ...
	mfilename, 'VehicleTestMass', 6);

validateattributes(f0, ...
	{'double'}, ...
	{'scalar'}, ...
	mfilename, 'f0', 7);

validateattributes(f1, ...
	{'double'}, ...
	{'scalar'}, ...
	mfilename, 'f1', 8);

validateattributes(f2, ...
	{'double'}, ...
	{'scalar'}, ...
	mfilename, 'f2', 9);

validateattributes(Ndv, ...
	{'cell'}, ...
	{'ncols', 2}, ...
	mfilename, 'Ndv', 10);

[Gears, NdvRatios] = Ndv{:};

validateattributes(Gears, ...
	{'char'},	...
	{'nrows', NoOfGears}, ...
	mfilename, 'Ndv.Gears', 10);

if ~all(diff(NdvRatios) < 0)
	error('MATLAB:INVALID_INPUT:Ndv', 'Ndv values must decrease monotonically with each gear');
end

% The old method of defining the ASM via the three input parameters
% - AdditionalSafetyMargin0
% - StartEngineSpeed
% - EndEngineSpeed
% is no longer required by the newer regulations.
% But BMW still uses it for comparisons with earlier shiftpoint calculations.
% Addtionally BMW requires to use this parameters in a slightly different way:
% If the ASM values are not defined in the FullPowerCurve
% then the three parameters will be used to calculate ASM values
% for the engine speeds given by the FullPowerCurve
% and this values will be filled into the FullPowerCurve.
% This ASM percentage values additionally shall be rounded
% to one digit after the decimal point ie to 0.1 percent units.
% So afterwards the ASM is always defined by FullPowerCurve.
% This also implies that linear interpolation will be used
% to calculate the ASM values for intermediate engine speeds.
% Previously exponential decaying ASM values were calculated 
% for intermediate engine speeds.

if size( FullPowerCurve, 2 ) == 2
    ASM = [];
    for i = 1 : size( FullPowerCurve{ 1 }, 1 )
        ASM( i ) = ...
          round( ...
            ExponentialDecayingASM( ...
              FullPowerCurve{ 1 }( i ) ...
            , AdditionalSafetyMargin0 ...
            , StartEngineSpeed ...
            , EndEngineSpeed ...
            ) ...
          * 10 ...
          ) ...
        / 10 ...
        ;
    end
    FullPowerCurve{ end + 1 } = ASM';
end

if size( FullPowerCurve, 2 ) == 2
	[ PowerCurveEngineSpeeds, PowerCurvePowers ] = FullPowerCurve{:};
	DefinedPowerCurveAdditionalSafetyMargins = false;
elseif size( FullPowerCurve, 2 ) == 3
 	[ PowerCurveEngineSpeeds, PowerCurvePowers, PowerCurveAdditionalSafetyMargins ] = FullPowerCurve{:};
	DefinedPowerCurveAdditionalSafetyMargins = true;
else
	error('MATLAB:INVALID_INPUT:FullPowerCurve', 'FullPowerCurve must be a cell array with 2 or 3 columns');
end

validateattributes(PowerCurvePowers, ...
	{'double'}, ...
	{'nrows', length(PowerCurveEngineSpeeds)}, ...
	mfilename, 'PowerCurve.PowerCurvePowers', 11);

if DefinedPowerCurveAdditionalSafetyMargins
	validateattributes(PowerCurveAdditionalSafetyMargins, ...
		{'double'}, ...
		{'nrows', length(PowerCurveEngineSpeeds)}, ...
		mfilename, 'PowerCurve.PowerCurveAdditionalSafetyMargins', 11);
end

if ~all(diff(PowerCurveEngineSpeeds) > 0)
	error('MATLAB:INVALID_INPUT:PowerCurveEngineSpeeds', 'Power curve engine speed values must increase strict monotonically');
end

validateattributes(Trace, ...
	{'cell'}, ...
	{'ncols', 2}, ...
	mfilename, 'Trace', 12);

[TraceTimesInput, RequiredVehicleSpeedsInput] = Trace{:};

validateattributes(RequiredVehicleSpeedsInput, ...
	{'double'},	...
	{'nrows', length(TraceTimesInput)}, ...
	mfilename, 'Trace.RequiredVehicleSpeeds', 12);

validateattributes(SafetyMargin, ...
	{'double'}, ...
	{'scalar', '>=', 0, '<=', 100}, ...
	mfilename, 'SafetyMargin', 13);

validateattributes(AdditionalSafetyMargin0, ...
	{'double'}, ...
	{'scalar', '>=', 0, '<=', 100}, ...
	mfilename, 'AdditionalSafetyMargin0', 14);

% additional safety margins defined together with the power curve
% take precedence over the legacy additional safety margins
% exponentially decaying from start to end engine speed
if AdditionalSafetyMargin0 && ~DefinedPowerCurveAdditionalSafetyMargins
	validateattributes(StartEngineSpeed, ...
		{'double'}, ...
		{'scalar', '>=', IdlingEngineSpeed}, ...
		mfilename, 'StartEngineSpeed', 15);
	
	validateattributes(EndEngineSpeed, ...
		{'double'}, ...
		{'scalar', '>', StartEngineSpeed}, ...
		mfilename, 'EndEngineSpeed', 16);
else
	validateattributes(StartEngineSpeed, ...
		{'double'}, ...
		{'scalar'}, ...
		mfilename, 'StartEngineSpeed', 15);

	validateattributes(EndEngineSpeed, ...
		{'double'}, ...
		{'scalar'}, ...
		mfilename, 'EndEngineSpeed', 16);
end

validateattributes(MinDriveEngineSpeed1st, ...
	{'double'}, ...
	{'scalar', 'nonnegative'}, ...
	mfilename, 'MinDriveEngineSpeed1st', 17);

validateattributes(MinDriveEngineSpeed1stTo2nd, ...
	{'double'}, ...
	{'scalar', 'nonnegative'}, ...
	mfilename, 'MinDriveEngineSpeed1stTo2nd', 18);

validateattributes(MinDriveEngineSpeed2ndDecel, ...
	{'double'}, ...
	{'scalar', 'nonnegative'}, ...
	mfilename, 'MinDriveEngineSpeed2ndDecel', 19);

validateattributes(MinDriveEngineSpeed2nd, ...
	{'double'}, ...
	{'scalar', 'nonnegative'}, ...
	mfilename, 'MinDriveEngineSpeed2nd', 20);

validateattributes(MinDriveEngineSpeedGreater2nd, ...
	{'double'}, ...
	{'scalar', 'nonnegative'}, ...
	mfilename, 'MinDriveEngineSpeedGreater2nd', 21);

validateattributes(EngineSpeedLimitVMax, ...
	{'double'}, ...
	{'scalar', 'nonnegative'}, ...
	mfilename, 'EngineSpeedLimitVMax', 22);

validateattributes(MaxTorque, ...
	{'double'}, ...
	{'scalar'}, ...
	mfilename, 'MaxTorque', 23);

validateattributes(ExcludeCrawlerGear, ...
	{'logical'}, ...
	{'scalar'}, ...
	mfilename, 'ExcludeCrawlerGear', 24);

validateattributes(AutomaticClutchOperation, ...
	{'logical'}, ...
	{'scalar'}, ...
	mfilename, 'AutomaticClutchOperation', 25);

% Remove the first gear from the inputs
if ExcludeCrawlerGear
	Gears = Gears(2:end, :); %#ok<NASGU>
	NdvRatios = NdvRatios(2:end);
	NoOfGears = NoOfGears - 1;
end

validateattributes(SuppressGear0DuringDownshifts, ...
	{'logical'}, ...
	{'scalar'}, ...
	mfilename, 'SuppressGear0DuringDownshifts', 26);

validateattributes(MinDriveEngineSpeedGreater2ndAccel, ...
	{'double'}, ...
	{'scalar', 'nonnegative'}, ...
	mfilename, 'MinDriveEngineSpeedGreater2ndAccel', 27);

validateattributes(MinDriveEngineSpeedGreater2ndDecel, ...
	{'double'}, ...
	{'scalar', 'nonnegative'}, ...
	mfilename, 'MinDriveEngineSpeedGreater2ndDecel', 28);

validateattributes(MinDriveEngineSpeedGreater2ndAccelStartPhase, ...
	{'double'}, ...
	{'scalar', 'nonnegative'}, ...
	mfilename, 'MinDriveEngineSpeedGreater2ndAccelStartPhase', 29);

validateattributes(MinDriveEngineSpeedGreater2ndDecelStartPhase, ...
	{'double'}, ...
	{'scalar', 'nonnegative'}, ...
	mfilename, 'MinDriveEngineSpeedGreater2ndDecelStartPhase', 30);

validateattributes(TimeEndOfStartPhase, ...
	{'int32'}, ...
	{'scalar', 'integer', '>=', -1, '<=' max( TraceTimesInput ) }, ...
	mfilename, 'TimeEndOfStartPhase', 31);

validateattributes(DoNotMergeClutchIntoGearsOutput, ...
	{'logical'}, ...
	{'scalar'}, ...
	mfilename, 'DoNotMergeClutchIntoGearsOutput', 32);

%% Re-sample the trace in 1Hz
% If the trace was provided with higher sample rate, this may lead to data
% loss.

if TraceTimesInput(1) ~= 0
	error('MATLAB:INVALID_INPUT:Trace', 'Trace time must start at 0');
end

TraceTimes = (TraceTimesInput(1):1:ceil(TraceTimesInput(end)))';
RequiredVehicleSpeeds = interp1(TraceTimesInput, RequiredVehicleSpeedsInput, TraceTimes);
TraceTimesCount = length(TraceTimes);


%% Identify phases
% TOO_SHORT     time period of 1 or 2 seconds too short for classification
% STANDSTILL	time period with required vehicle speed < 1km/h.
% ACCELERATION	time period of more than 2 seconds with required vehicle
%				speed >= 1km/h and monotonically increasing.
% ACCELERATION_FROM_STANDSTILL
%				ACCELERATION phase following a STANDSTILL phase
% DECELERATION	time period of more than 2 seconds with required vehicle
%				speed >= 1km/h and monotonically decreasing.
% DECELERATION_TO_STANDSTILL
%				DECELERATION phase preceding a STANDSTILL phase
% CONSTANT_SPEED  
%               time period with constant required vehicle speed >= 1km/h

PHASE_TOO_SHORT = 0;
PHASE_STANDSTILL = 1;
PHASE_ACCELERATION = 2;
PHASE_ACCELERATION_FROM_STANDSTILL = 3;
PHASE_DECELERATION = 4;
PHASE_DECELERATION_TO_STANDSTILL = 5;
PHASE_CONSTANT_SPEED = 6;

Phases = zeros(TraceTimesCount, 1);

% As section 4 does not explicitly specify the strictness of acceleration
% monotony, the definition in section 3.3 is used to clearly identify the
% acceleration and deceleration phases respectively.
Phases(RequiredVehicleSpeeds < 1) = PHASE_STANDSTILL;
Phases(RequiredVehicleSpeeds >= 1 & diff([RequiredVehicleSpeeds; 0]) > 0) = PHASE_ACCELERATION;
Phases(RequiredVehicleSpeeds >= 1 & diff([RequiredVehicleSpeeds; 0]) <= 0) = PHASE_DECELERATION;
Phases(RequiredVehicleSpeeds >= 1 & abs(diff([RequiredVehicleSpeeds; 0])) < 0.001) = PHASE_CONSTANT_SPEED;
 
% some gear corrections ignore the duration of acceleration phases
% so save acceleration phases with any duration here
% before phases shorter than or equal to 2 seconds get undefined below
InAccelerationAnyDuration = zeros( TraceTimesCount, 1 );
InAccelerationAnyDuration( Phases == PHASE_ACCELERATION ) = 1;

PhaseEnds = [find(Phases(1:end-1) ~= Phases(2:end)); length(Phases)];
PhaseLengths = diff([0; PhaseEnds]);
PhaseValues = Phases(PhaseEnds);
PreviousPhaseValues = [0; PhaseValues(1:end-1)];
NextPhaseValues = [PhaseValues(2:end); 0];

PhaseValues(PhaseValues == PHASE_ACCELERATION & PreviousPhaseValues == PHASE_STANDSTILL) = PHASE_ACCELERATION_FROM_STANDSTILL;
PhaseValues(PhaseValues == PHASE_DECELERATION & NextPhaseValues == PHASE_STANDSTILL) = PHASE_DECELERATION_TO_STANDSTILL;

% Undefine all phases shorter than or equal to 2 seconds
PhaseValues(PhaseValues ~= PHASE_STANDSTILL & PhaseValues ~= PHASE_CONSTANT_SPEED & PhaseLengths <= 2) = PHASE_TOO_SHORT;

PhaseStarts = cumsum([1; PhaseLengths(1:end-1)]);
PhaseChanges = zeros(TraceTimesCount, 1);
PhaseChanges(PhaseStarts) = 1;
Phases = PhaseValues(cumsum(PhaseChanges));

% Define convenience logic indexing
InStandStill = Phases == PHASE_STANDSTILL;
InAcceleration = Phases == PHASE_ACCELERATION | Phases == PHASE_ACCELERATION_FROM_STANDSTILL;
InAccelerationFromStandstill = Phases == PHASE_ACCELERATION_FROM_STANDSTILL;
InDeceleration = Phases == PHASE_DECELERATION | Phases == PHASE_DECELERATION_TO_STANDSTILL;
InDecelerationToStandstill = Phases == PHASE_DECELERATION_TO_STANDSTILL;
InConstantSpeed = Phases == PHASE_CONSTANT_SPEED;


%% Determine rated engine power and rated engine speed from the full power curve
% NOTE: this will only be done if this values were not set as input parameters

if RatedEnginePower <= 0 || isnan( RatedEnginePower ) ...
&& RatedEngineSpeed <= 0 || isnan( RatedEngineSpeed )
    RatedEnginePower = max( PowerCurvePowers );
    % NOTE: 
    % the following requirement was deleted from the regulation
    % but as there is no new requirement we will stay with the old one :
    % If the maximum power is developed over an engine speed range,
    % n_rated shall be the minimum of this range
    idx = min( find( PowerCurvePowers == RatedEnginePower ) );
    RatedEngineSpeed = PowerCurveEngineSpeeds( idx );
end


%% Determine the maximum engine speed where 95 percent of the rated power is reached from the full power curve
% NOTE: this will only be done if this value was not set as input parameter

if Max95EngineSpeed <= 0 || isnan( Max95EngineSpeed )
    PowerCurvePowerMax95 = 0.95 * max( PowerCurvePowers );
    if PowerCurvePowers( end ) >= PowerCurvePowerMax95
        Max95EngineSpeed = PowerCurveEngineSpeeds( end );
    else
        idx = max( find( diff ( PowerCurvePowers >= PowerCurvePowerMax95 ) ) );
        if isempty( idx )
            error( 'MATLAB:INVALID_INPUT:FullPowerCurve', ...
                   'Max95EngineSpeed can not be calculated from FullPowerCurve' );
        end
        Max95EngineSpeed = ...
          PowerCurveEngineSpeeds( idx ) ... 
          + ( PowerCurvePowerMax95              - PowerCurvePowers      ( idx ) ) ...
          / ( PowerCurvePowers      ( idx + 1 ) - PowerCurvePowers      ( idx ) ) ...
          * ( PowerCurveEngineSpeeds( idx + 1 ) - PowerCurveEngineSpeeds( idx ) ) ...
        ;
        % NOTE:
        % idx + 1 is never out of range
        % because diff() returns a one element shorter vector 
        % division by zero is impossible
        % because PowerCurveEngineSpeeds increases strict monotonically
    end
end


%% Define minimum engine speeds when vehicle is in motion (2k)
% NOTE: The calculation of minimum engine speeds for the second gear does
% not fully confirm to the latest legislation text, but rather reflects
% the previous revision of it until (2ka) is clarified.

% Calculate
CalculatedMinDriveEngineSpeed1st = IdlingEngineSpeed;
CalculatedMinDriveEngineSpeed1stTo2nd = 1.15 * IdlingEngineSpeed;
CalculatedMinDriveEngineSpeed2ndDecel = IdlingEngineSpeed;
CalculatedMinDriveEngineSpeed2nd = 0.9 * IdlingEngineSpeed;
CalculatedMinDriveEngineSpeedGreater2nd = IdlingEngineSpeed + 0.125 * ( RatedEngineSpeed - IdlingEngineSpeed );  % min_drive_set

% Choose higher values and round to nearest integer
MinDrive1st = round( max( CalculatedMinDriveEngineSpeed1st, MinDriveEngineSpeed1st ) );
MinDrive1stTo2nd = round( max( CalculatedMinDriveEngineSpeed1stTo2nd, MinDriveEngineSpeed1stTo2nd ) );
MinDrive2ndDecel = round( max(CalculatedMinDriveEngineSpeed2ndDecel, MinDriveEngineSpeed2ndDecel ) );
MinDrive2nd = round( max( CalculatedMinDriveEngineSpeed2nd, MinDriveEngineSpeed2nd ) );
MinDriveGreater2nd = round( max( CalculatedMinDriveEngineSpeedGreater2nd, MinDriveEngineSpeedGreater2nd ) );

MinDrives = zeros( TraceTimesCount, NoOfGears );
MinDrives( :, 1 ) = MinDrive1st;
MinDrives( :, 2 ) = MinDrive2nd;
MinDrives( :, 3:NoOfGears ) = MinDriveGreater2nd;
MinDrives( InDecelerationToStandstill, 2 ) = MinDrive2ndDecel;

% Changed requirement:
% MinDrive1stTo2nd no longer limited to acceleration phase
% this now will be handled below after InitialGears were determined.
%
% MinDrives(InAccelerationFromStandstill, 2) = MinDrive1stTo2nd;

% Annex 2, (k) n_min_drive_set
% Values higher than n_min_drive_set may be used for n_gear > 2
% if requested by the manufacturer.
% All individually chosen n_min_drive values
% shall be equal to or higher than n_min_drive_set
% but shall not exceed 2 * n_min_drive_set.
% NOTE:
% values smaller than n_min_drive_set will have no effect
% because the max() function will be used below
if MinDriveEngineSpeedGreater2ndAccel > 2 * CalculatedMinDriveEngineSpeedGreater2nd
    error( ...
      'MATLAB:INVALID_INPUT:MinDriveEngineSpeedGreater2ndAccel' ...
    , 'MinDriveEngineSpeedGreater2ndAccel value %g must be less or equal 2 * m_min_drive_set = %g' ...
    , MinDriveEngineSpeedGreater2ndAccel ...
    , 2 * CalculatedMinDriveEngineSpeedGreater2nd ...
    );
end
if MinDriveEngineSpeedGreater2ndDecel > 2 * CalculatedMinDriveEngineSpeedGreater2nd
    error( ...
      'MATLAB:INVALID_INPUT:MinDriveEngineSpeedGreater2ndDecel' ...
    , 'MinDriveEngineSpeedGreater2ndDecel value %g must be less or equal 2 * m_min_drive_set = %g' ...
    , MinDriveEngineSpeedGreater2ndDecel ...
    , 2 * CalculatedMinDriveEngineSpeedGreater2nd ...
    );
end
if MinDriveEngineSpeedGreater2ndAccelStartPhase > 2 * CalculatedMinDriveEngineSpeedGreater2nd
    error( ...
      'MATLAB:INVALID_INPUT:MinDriveEngineSpeedGreater2ndAccelStartPhase' ...
    , 'MinDriveEngineSpeedGreater2ndAccelStartPhase value %g must be less or equal 2 * m_min_drive_set = %g' ...
    , MinDriveEngineSpeedGreater2ndAccelStartPhase ...
    , 2 * CalculatedMinDriveEngineSpeedGreater2nd ...
    );
end
if MinDriveEngineSpeedGreater2ndDecelStartPhase > 2 * CalculatedMinDriveEngineSpeedGreater2nd
    error( ...
      'MATLAB:INVALID_INPUT:MinDriveEngineSpeedGreater2ndDecelStartPhase' ...
    , 'MinDriveEngineSpeedGreater2ndDecelStartPhase value %g must be less or equal 2 * m_min_drive_set = %g' ...
    , MinDriveEngineSpeedGreater2ndDecelStartPhase ...
    , 2 * CalculatedMinDriveEngineSpeedGreater2nd ...
    );
end

% Annex 2, (k) n_min_drive_set
% For an initial period of time (t_start_phase),
% the manufacturer may specify higher values. 
% The initial time period shall be specified by the manufacturer
% but shall not exceed the low speed phase of the cycle
% and shall end in a stop phase
% so that there is no change of n_min_drive within a short trip.
InStandstillMinDrive = RequiredVehicleSpeeds == 0;
if TimeEndOfStartPhase >= 0 ...
&& ~ InStandstillMinDrive( TimeEndOfStartPhase + 1 )
    error( ...
      'MATLAB:INVALID_INPUT:TimeEndOfStartPhase' ...
    , 'Vehicle speed at end of start phase must be zero' ...
    );
end
% can not check for unknown end of low speed phase here

% Annex 2, 2(k) n_min_drive_set
% Samples which have acceleration values >= -0.1389 m/s² ( = 0.5 (km/h)/s )
% shall belong to the acceleration/constant speed phases.
Accelerations = [diff(RequiredVehicleSpeeds) ./ (3.6 * diff(TraceTimes)); 0];
InAccelerationMinDrive = Accelerations >= - 0.1389;
InDecelerationMinDrive = ~ InAccelerationMinDrive;

MinDrives( InAccelerationMinDrive, 3:NoOfGears ) = ...
  max( ... 
    MinDrives( InAccelerationMinDrive, 3:NoOfGears ) ...
  , MinDriveEngineSpeedGreater2ndAccel ...
  ) ...
;
MinDrives( InDecelerationMinDrive, 3:NoOfGears ) = ...
  max( ...
    MinDrives( InDecelerationMinDrive, 3:NoOfGears ) ...
  , MinDriveEngineSpeedGreater2ndDecel ...
  ) ...
;
InAccelerationMinDriveStartPhase = ( InAccelerationMinDrive & TraceTimes <= TimeEndOfStartPhase );
MinDrives( InAccelerationMinDriveStartPhase, 3:NoOfGears ) = ...
  max( ...
    MinDrives( InAccelerationMinDriveStartPhase, 3:NoOfGears ) ...
  , MinDriveEngineSpeedGreater2ndAccelStartPhase ...
  ) ...
;
InDecelerationMinDriveStartPhase = ( InDecelerationMinDrive & TraceTimes <= TimeEndOfStartPhase );
MinDrives( InDecelerationMinDriveStartPhase, 3:NoOfGears ) = ...
  max( ...
    MinDrives( InDecelerationMinDriveStartPhase, 3:NoOfGears ) ...
  , MinDriveEngineSpeedGreater2ndDecelStartPhase ...
  ) ...
;

% Round to the nearest integer
MinDrives = round(MinDrives);

%% Determine the gear, in which the maximum vehicle speed is reached (2i)
% The maximum vehicle speed is defined as the vehicle speed, at which the
% available power equals the road load power caused by friction and
% aerodynamics, and is usually not covered by typical traces. That is why
% the calculation is based on sufficient fictive road load speeds.

% Vehicle speed values rounded to one place of decimal
% shall be used for the determination of v_max and ng_vmax.
RoadLoadSpeeds = 0.1:0.1:500;
RoadLoadPowers = (f0 .* RoadLoadSpeeds + f1 .* (RoadLoadSpeeds.^2) + f2 .* (RoadLoadSpeeds.^3))/3600;

PowerCurveVehicleSpeedsPerGear = PowerCurveEngineSpeeds * ( 1 ./ NdvRatios' );

% Reduce the values of the power curve by 10%
for gear = 1 : NoOfGears
    AvailablePowersPerGear( gear, : ) = 0.9 * interp1( PowerCurveVehicleSpeedsPerGear( :, gear ) , PowerCurvePowers, RoadLoadSpeeds );
end

NextRoadLoadPowers = [ RoadLoadPowers( 2:end ) 0 ];
NextAvailablePowersPerGear = [ AvailablePowersPerGear( :, 2:end ) zeros( NoOfGears, 1 ) ];

for gear = 1 : NoOfGears
    VehicleSpeedsPerGear( gear, : ) = RoadLoadSpeeds( ...
      xor( ...
            RoadLoadPowers <     AvailablePowersPerGear( gear, : ) ...
      , NextRoadLoadPowers < NextAvailablePowersPerGear( gear, : ) ...
      ) ...
    );
end

GearAtMaxVehicleSpeed = 0;
for gear = NoOfGears : -1 : 2
    if ~ isempty( VehicleSpeedsPerGear( gear  , : ) ) ...
    && ~ isempty( VehicleSpeedsPerGear( gear-1, : ) ) ...
    &&       max( VehicleSpeedsPerGear( gear  , : ) ) ...
         >=  max( VehicleSpeedsPerGear( gear-1, : ) ) 
  	    GearAtMaxVehicleSpeed = gear;
  	    MaxVehicleSpeed = max( VehicleSpeedsPerGear( gear, : ) );
        break;
    end
end
if GearAtMaxVehicleSpeed == 0
    error( 'MATLAB:INVALID_INPUT:Ndv', 'Gear to be used at maximum vehicle speed could not be determined' );
end

%% Determine maximum engine speed (2g)

% n_max1 = n_95_high
% If n_95_high cannot be determined
% because the engine speed is limited to a lower value n_lim for all gears
% and the corresponding full load power is higher than 95 per cent of rated power,
% n_95_high shall be set to n_lim. 
if EngineSpeedLimitVMax > 0 && EngineSpeedLimitVMax < Max95EngineSpeed
    PowerAtEngineSpeedLimitVMax = interp1(PowerCurveEngineSpeeds, PowerCurvePowers, EngineSpeedLimitVMax);
    if PowerAtEngineSpeedLimitVMax > 0.95 * RatedEnginePower
        Max95EngineSpeed = EngineSpeedLimitVMax;
    end
end

% n_max2
EngineSpeedAtGearAtMaxRequiredSpeed = NdvRatios(GearAtMaxVehicleSpeed) * max(RequiredVehicleSpeeds);
% Annex 2, 2 (i)
% if, for the purpose of limiting maximum vehicle speed, the maximum engine speed is limited to n_lim ...
if EngineSpeedLimitVMax > 0 && EngineSpeedLimitVMax < EngineSpeedAtGearAtMaxRequiredSpeed
	EngineSpeedAtGearAtMaxRequiredSpeed = EngineSpeedLimitVMax;
end

% n_max3
EngineSpeedAtGearAtMaxVehicleSpeed = NdvRatios(GearAtMaxVehicleSpeed) * MaxVehicleSpeed;
% Annex 2, 2 (i)
% if, for the purpose of limiting maximum vehicle speed, the maximum engine speed is limited to n_lim ...
if EngineSpeedLimitVMax > 0 && EngineSpeedLimitVMax < EngineSpeedAtGearAtMaxVehicleSpeed
	EngineSpeedAtGearAtMaxVehicleSpeed = EngineSpeedLimitVMax;
    GearAtMaxVehicleSpeed = NoOfGears;
    MaxVehicleSpeed = EngineSpeedLimitVMax / NdvRatios(NoOfGears);
end

% n_max = max( n_max1, n_max2, n_max3 )
MaxEngineSpeed = max( [ ...
  Max95EngineSpeed ...
  EngineSpeedAtGearAtMaxRequiredSpeed ...
  EngineSpeedAtGearAtMaxVehicleSpeed ...
] );

%% Check power curve quality (2h)
% The first data set shall be at n_min_drive_set or lower.
% The last data set shall be at n_max or higher engine speed.
if PowerCurveEngineSpeeds(1) > CalculatedMinDriveEngineSpeedGreater2nd || PowerCurveEngineSpeeds(end) < MaxEngineSpeed;
    % NOTE: according to (2k) MinDriveEngineSpeedGreater2nd shall be ignored for power curve lower limit check
    error('MATLAB:INVALID_INPUT:PowerCurveEngineSpeeds', 'Power curve engine speed range shall be [%g, %g], found [%g, %g]', CalculatedMinDriveEngineSpeedGreater2nd, MaxEngineSpeed, PowerCurveEngineSpeeds(1), PowerCurveEngineSpeeds(end));
end


%% Calculate required powers (3.1)

RequiredPowers = (f0 * RequiredVehicleSpeeds + f1 * (RequiredVehicleSpeeds.^2) + f2 * (RequiredVehicleSpeeds.^3) + 1.03 * Accelerations .* RequiredVehicleSpeeds * VehicleTestMass) / 3600;


%% Calculate required engine speeds (3.2)

RequiredEngineSpeeds = RequiredVehicleSpeeds * NdvRatios';
InitialRequiredEngineSpeeds = RequiredEngineSpeeds;

PossibleGearsByEngineSpeed = NaN(TraceTimesCount, NoOfGears);
ClutchDisengaged = zeros(TraceTimesCount, 1);
% FOR TESTING PURPOSES WE NOW INTRODUCED AS EXTRA INDICATION FOR SUB-STATE "UNDEFINED"
ClutchUndefined  = zeros(TraceTimesCount, 1);

% For ANY v < 1km/h the vehicle is considered standing still with the
% engine idling and neutral gear engaged...
RequiredEngineSpeeds(InStandStill, :) = IdlingEngineSpeed;
PossibleGearsByEngineSpeed(InStandStill, :) = 0;

% ...except 1 second before acceleration phase, where the 1st gear shall be
% engaged. Consequently subsequent calculations shall NOT by applied to the
% stillstand phase.
AccelerationFromStandstillStarts = PhaseStarts(PhaseValues == PHASE_ACCELERATION_FROM_STANDSTILL);

BeforeAccelerationStarts = AccelerationFromStandstillStarts-1;
for i = 1:length(BeforeAccelerationStarts)
	while BeforeAccelerationStarts(i) >= 3 && Accelerations(BeforeAccelerationStarts(i)) > 0
        % avoid trace time index stored BeforeAccelerationStarts(i) becoming smaller than 2
        % so there will always be smaller trace time index to indicate clutch disenganged  
        BeforeAccelerationStarts(i) = BeforeAccelerationStarts(i) - 1;
    end     
end    
AdvancedFirstGearEngage = arrayfun(@colon, BeforeAccelerationStarts, AccelerationFromStandstillStarts-1, 'Uniform', false);
AdvancedClutchDisengage = arrayfun(@colon, BeforeAccelerationStarts-1, BeforeAccelerationStarts-1, 'Uniform', false);    
if ~DoNotMergeClutchIntoGearsOutput
    ClutchDisengaged([AdvancedClutchDisengage{:}]) = 1;
end
PossibleGearsByEngineSpeed([AdvancedFirstGearEngage{:}], 1) = 1;
ClutchDisengaged([AdvancedFirstGearEngage{:}]) = 1;


%% Determine possible gears based on required engine speeds (3.3)

for gear = 1:NoOfGears
	if gear < GearAtMaxVehicleSpeed
		PossibleGearsByEngineSpeed(~InStandStill & MinDrives(:, gear) <= RequiredEngineSpeeds(:, gear) & RequiredEngineSpeeds(:, gear) <= Max95EngineSpeed, gear) = 1; % (3.3a)
	else
		% NOTE:
		% if GearAtMaxVehicleSpeed < NoOfGears and gear == NoOfGears then EngineSpeedAtGearAtMaxRequiredSpeed is irrelevant
		% but as the engine speed for a higher gear is always lower than for a lower gear
		% the check for <= EngineSpeedAtGearAtMaxRequiredSpeed does not hurt
		PossibleGearsByEngineSpeed(~InStandStill & MinDrives(:, gear) <= RequiredEngineSpeeds(:, gear) & RequiredEngineSpeeds(:, gear) <= EngineSpeedAtGearAtMaxRequiredSpeed, gear) = 1; % (3.3b)
	end
end

PossibleGearsByEngineSpeed(~InStandStill & RequiredEngineSpeeds(:, 1) < MinDrives(:, 1), 1) = 1; % (3.3c)

ClutchDisengagedByGear = zeros(TraceTimesCount, NoOfGears);
ClutchUndefinedByGear  = zeros(TraceTimesCount, NoOfGears);

InAnyStandstill    = RequiredVehicleSpeeds < 1;
InAnyDeceleration  = diff( [ RequiredVehicleSpeeds; 0 ] ) <= -0.001 & not( InAnyStandstill );
InAnyAcceleration  = diff( [ RequiredVehicleSpeeds; 0 ] ) >= +0.001 & not( InAnyStandstill );
InAnyConstantSpeed = not( InAnyStandstill | InAnyDeceleration | InAnyAcceleration );

InAnyDecelerationWithLowEngineSpeed = ...
  repmat(InAnyDeceleration, 1, NoOfGears) & ...
  RequiredEngineSpeeds < IdlingEngineSpeed;
  % Regulation requires :
  % 3.3 Selection of possible gears with respect to engine speed
  %   If a_j < 0 and n_i,j <= n_idle,
  %   n_i,j shall be set to n_idle and the clutch shall be disengaged.
  % But the Heinz Steven Tool (HST) does this only if n_i,j < n_idle.
  % MATLAB will do it like HST to avoid following differences :
  %  vehicle_no =  78, time 345 and 1367 with n_2 = 1000 = n_idle
  %  vehicle_no = 115, time 64           with n_2 =  700 = n_idle.
ClutchDisengagedByGear(InAnyDecelerationWithLowEngineSpeed) = 1;
RequiredEngineSpeeds(InAnyDecelerationWithLowEngineSpeed) = IdlingEngineSpeed;

InAnyAccelOrConstSpeedWithLowEngineSpeed = ...
  repmat(InAnyAcceleration | InAnyConstantSpeed, 1, NoOfGears) & ...
  RequiredEngineSpeeds < max( 1.15 * IdlingEngineSpeed, PowerCurveEngineSpeeds(1) );
ClutchDisengagedByGear(InAnyAccelOrConstSpeedWithLowEngineSpeed) = 1;
ClutchUndefinedByGear (InAnyAccelOrConstSpeedWithLowEngineSpeed) = 1;
% "Undefined" covers any status of the clutch between "disengaged" and "engaged",
% depending on the individual engine and transmission design.
% In such a case, the real engine speed may deviate from the calculated engine speed.
RequiredEngineSpeeds(InAnyAccelOrConstSpeedWithLowEngineSpeed) = ...
  max( 1.15 * IdlingEngineSpeed, RequiredEngineSpeeds(InAnyAccelOrConstSpeedWithLowEngineSpeed) );

% HST 2019-10-08 sets clutch to "undefined" for gear 1
% if the used engine speed is greater than ndv_1 * v
% but only if v >= 1 km/h and not during a deceleration to standstill  
Gear1WithIncrEngineSpeed = ...
  ( InitialRequiredEngineSpeeds( :, 1 ) < RequiredEngineSpeeds( : , 1 ) ) & ...
  not( InStandStill ) & not( InDecelerationToStandstill );
ClutchDisengagedByGear( Gear1WithIncrEngineSpeed ) = 1; 
ClutchUndefinedByGear( Gear1WithIncrEngineSpeed ) = 1; 

%% Calculate available powers (3.4)

% additional safety margins defined together with the power curve
% take precedence over the legacy additional safety margins
% exponentially decaying from start to end engine speed

if DefinedPowerCurveAdditionalSafetyMargins

    RequiredEngineSpeeds( :, 2 ) = max( RequiredEngineSpeeds( :, 2 ), IdlingEngineSpeed );
    AvailablePowers( :, 1:2 ) = ...
      interp1( ...
        PowerCurveEngineSpeeds ...
      , PowerCurvePowers .* ( 1 - ( SafetyMargin + PowerCurveAdditionalSafetyMargins ) / 100 ) ...
      , max( RequiredEngineSpeeds( :, 1:2 ), PowerCurveEngineSpeeds( 1 ) ) ...
      ) ...
    ;
    AvailablePowers( :, 3:size(RequiredEngineSpeeds,2) ) = ...
      interp1( ...
        PowerCurveEngineSpeeds ...
      , PowerCurvePowers .* ( 1 - ( SafetyMargin + PowerCurveAdditionalSafetyMargins ) / 100 ) ...
      , RequiredEngineSpeeds( :, 3:end ) ...
      , 'linear' ...
      , 'extrap' ...
      ) ...
    ;
    InitialAvailablePowers = interp1(PowerCurveEngineSpeeds, PowerCurvePowers .* (1 - (SafetyMargin + PowerCurveAdditionalSafetyMargins)/100), InitialRequiredEngineSpeeds);
    
else

	AdditionalSafetyMargin = zeros(TraceTimesCount, NoOfGears);

	if AdditionalSafetyMargin0 ~= 0
		AdditionalSafetyMargin = AdditionalSafetyMargin0 * exp(log(0.5/AdditionalSafetyMargin0) * (StartEngineSpeed - RequiredEngineSpeeds) / (StartEngineSpeed - EndEngineSpeed));
        % In MATLAB the ASM values have the unit "percent" with a range 0 to 100
        % while in the regulation the assumed unit is "fraction" with a range 0 to 1.
        % Therefore the value of the constant 0.005 used in the regulation formula
        % ASM = ASM_0 × exp( ln( 0.005 / ASM_0 ) × ( n_start – n ) / ( n_start – n_end ) )
        % must be replaced by the value 0.5 in the MATLAB formula.
	end

	AdditionalSafetyMargin(RequiredEngineSpeeds<=StartEngineSpeed)=AdditionalSafetyMargin0;

	AvailablePowers = interp1(PowerCurveEngineSpeeds, PowerCurvePowers, RequiredEngineSpeeds) .* (1 - (SafetyMargin + AdditionalSafetyMargin)/100);
	InitialAvailablePowers = interp1(PowerCurveEngineSpeeds, PowerCurvePowers, InitialRequiredEngineSpeeds) .* (1 - (SafetyMargin + AdditionalSafetyMargin)/100);

end

% Explicitly allow slipping clutch for the first gear.
InAcceleration1stLowAvailablePower = InAcceleration & PossibleGearsByEngineSpeed(:, 1) == 1 & PossibleGearsByEngineSpeed(:, 2) ~= 1 & AvailablePowers(:, 1) < RequiredPowers;
while any(InAcceleration1stLowAvailablePower)
	RequiredEngineSpeeds(InAcceleration1stLowAvailablePower, 1) = RequiredEngineSpeeds(InAcceleration1stLowAvailablePower, 1) + 1;
	% additional safety margins defined together with the power curve
	% take precedence over the legacy additional safety margins
	% exponentially decaying from start to end engine speed
	if DefinedPowerCurveAdditionalSafetyMargins
		AvailablePowers(InAcceleration1stLowAvailablePower, 1) = interp1(PowerCurveEngineSpeeds, PowerCurvePowers .* (1 - (SafetyMargin + PowerCurveAdditionalSafetyMargins)/100), RequiredEngineSpeeds(InAcceleration1stLowAvailablePower, 1));
	else
		AvailablePowers(InAcceleration1stLowAvailablePower, 1) = interp1(PowerCurveEngineSpeeds, PowerCurvePowers, RequiredEngineSpeeds(InAcceleration1stLowAvailablePower, 1)) .* (1 - (SafetyMargin + AdditionalSafetyMargin(InAcceleration1stLowAvailablePower, 1))/100);
	end
	InAcceleration1stLowAvailablePower = InAcceleration & PossibleGearsByEngineSpeed(:, 1) == 1 & PossibleGearsByEngineSpeed(:, 2) ~= 1 & AvailablePowers(:, 1) < RequiredPowers;
end

% Explicitly allow slipping clutch for the second gear.
InAcceleration2ndLowAvailablePower = InAcceleration & PossibleGearsByEngineSpeed(:, 2) == 1 & PossibleGearsByEngineSpeed(:, 3) ~= 1 & AvailablePowers(:, 2) < RequiredPowers;
while any(InAcceleration2ndLowAvailablePower)
	RequiredEngineSpeeds(InAcceleration2ndLowAvailablePower, 2) = RequiredEngineSpeeds(InAcceleration2ndLowAvailablePower, 2) + 1;
	% additional safety margins defined together with the power curve
	% take precedence over the legacy additional safety margins
	% exponentially decaying from start to end engine speed
	if DefinedPowerCurveAdditionalSafetyMargins
		AvailablePowers(InAcceleration2ndLowAvailablePower, 2) = interp1(PowerCurveEngineSpeeds, PowerCurvePowers .* (1 - (SafetyMargin + PowerCurveAdditionalSafetyMargins)/100), RequiredEngineSpeeds(InAcceleration2ndLowAvailablePower, 2));
	else
		AvailablePowers(InAcceleration2ndLowAvailablePower, 2) = interp1(PowerCurveEngineSpeeds, PowerCurvePowers, RequiredEngineSpeeds(InAcceleration2ndLowAvailablePower, 2)) .* (1 - (SafetyMargin + AdditionalSafetyMargin(InAcceleration2ndLowAvailablePower, 2))/100);
	end
	InAcceleration2ndLowAvailablePower = InAcceleration & PossibleGearsByEngineSpeed(:, 2) == 1 & PossibleGearsByEngineSpeed(:, 3) ~= 1 & AvailablePowers(:, 2) < RequiredPowers;
end


%% Determine possible gears based on available powers (3.5)

PossibleGearsByAvailablePowersWithTotalSafetyMargin = NaN(TraceTimesCount, NoOfGears);

% ECE-TRANS-WP29-GPRE-2018-02
% 3.5 Determination of possible gears to be used
% (b) For n_gear > 2, if P_available_i,j >= P_required,j
%
% CHANGES:
% - the check for minimum engine speed was removed
% - the check for available power was restricted to gear numbers > 2

PossibleGearsByAvailablePowersWithTotalSafetyMargin(:, 1:2) = 1;

for gear = 3:NoOfGears

    PossibleGearsByAvailablePowersWithTotalSafetyMargin( AvailablePowers(:, gear) >= RequiredPowers, gear ) = 1;
    
	% ECE-TRANS-WP29-GPRE-2017-07
	% 3.5 Determination of possible gears to be used
	% (b) If n_i,j >= n_min_drive of n_gear > 2,
	%     P_available_i,j >= P_required_j
	%
	% The if-clause was addded,
	% so the power no longer must be checked if engine speed is not high enough

	% PossibleGearsByAvailablePowersWithTotalSafetyMargin( RequiredEngineSpeeds(:, gear) < MinDriveEngineSpeed1stTo2nd, gear ) = 1;

	% GSTF Note 2016-12-16
	% Annex 2, 3.5 (b) if-clause modified and explained:
	%   (b) If n_i,j >= minimum drive speed
	%                   DEFINED IN THE P_wot CURVE
	%                   (see paragraph 2 (h) of this annex)
	%       P_available_i,j >= P_required_j
	%   JUSTIFICATION:
	%   If P_wot is provided at lower speed than n_min_drive,
	%   the available power check should start at this speed.

	% PossibleGearsByAvailablePowersWithTotalSafetyMargin( RequiredEngineSpeeds(:, gear) < PowerCurveEngineSpeeds(1), gear ) = 1;

end

% the gear with highest power is always allowed by the Heinz Steven Tool
% even if the available power is less then the required power
% but only the gears which are possible by engine speed will be considered
[ ~, I ] = max( fliplr( AvailablePowers .* PossibleGearsByEngineSpeed ), [], 2 );
I = size( AvailablePowers, 2 ) - I + 1;  % I is a column vector of gear indices with max power for each trace second
% NOTE:
% if the maximum value occurs more than once,
% then max() returns the index corresponding to the first occurrence
% but as we need the index of the last occurence (ie of the highest gear)
% we flip the matrix horizontally before and invert the indices afterwards
[ m, n ] = size( AvailablePowers );
linearInd = sub2ind( [ m n ], 1:m, I' );  % convert trace time indices and gear indices to linear indices
PossibleGearsByAvailablePowersWithTotalSafetyMargin( linearInd ) = 1;
 
%% Determine initial gears

InStandStillReps = repmat(InStandStill, 1, NoOfGears);

PossibleGears = PossibleGearsByEngineSpeed;
PossibleGears(~InStandStillReps) = PossibleGears(~InStandStillReps) .* PossibleGearsByAvailablePowersWithTotalSafetyMargin(~InStandStillReps);

for gear = 1:NoOfGears
	PossibleGears(:,gear) = double(gear) * PossibleGears(:,gear);
end

% Select the highest final possible gear as initial gear at a given time
InitialGears = max(PossibleGears, [], 2);
InitialGears(AccelerationFromStandstillStarts) = 1;
		
AccelerationFromStandstillEnds = PhaseEnds(PhaseValues == PHASE_ACCELERATION_FROM_STANDSTILL);

AccelerationsFromStandstill = arrayfun(@colon, AccelerationFromStandstillStarts, AccelerationFromStandstillEnds, 'Uniform', false);

for phase = AccelerationsFromStandstill' %#ok<FXUP>
	gears = InitialGears(phase{:});

	secondGearEngaged = find(gears == 2, 1, 'first' ) - 1;

	gears(1:secondGearEngaged) = 1;

	InitialGears(phase{:}) = gears;
end


% Changed requirement:
% MinDrive1stTo2nd no longer limited to acceleration phase.

for i = 1 : length( InitialGears )
	switch InitialGears( i )
	case 1
		FromGear1 = true;
	case 2
		if FromGear1 ...
		&& InitialRequiredEngineSpeeds( i, 2 ) < MinDrive1stTo2nd ...
		&& PossibleGears( i, 1 ) == 1 ...
			InitialGears( i ) = 1;
		else
			FromGear1 = false;
		end
	otherwise
		FromGear1 = false;
	end
end


%% Apply corrections (4)

% create a cell array of gear corrections just for debugging
CorrectionsCells = cell( size( InitialGears ) );
[ CorrectionsCells, InitialGearsPrev ] = appendCorrectionCells( CorrectionsCells, InitialGears, InitialGears, '', 0 );

% The application of gear correction 4.(d) is unclear.
% As other gear corrections it shall be applied multiple times.
% If during the first application there is a 2-step upshift
% this will be corrected to a 1-step upshift.
% But then during the second application there still is a 1-step upshift 
% which shall be suppressed by correction 4.(d). 
% We assume here that such repeated corrections must be avoided.
% This will be realized by using correction 4.(d)
% for every second of the driving trace only once.

% vector of flags indicating where gear correction 4.(d) was applied before 
% so far gear correction 4.(d) was not applied for any trace second
corr_4d_applied_before = false( size( InitialGears ) );

%-----------------------------------------------------------------------
% Regulation Annex 2, 5.(a)
%------------------------------------------------------------------------------
% Paragraphs 4.(a) to 4.(f) inclusive of this annex
% shall be applied sequentially,
% scanning the complete cycle trace in each case.
% Since modifications to paragraphs 4.(a) to 4.(f) inclusive of this annex
% may create new gear use sequences, these new gear sequences shall be checked
% twice and modified if necessary.
%------------------------------------------------------------------------------
for correction = 1 : 2

    Corr4bToBeDoneAfterCorr4a = false( size( InitialGears, 1 ), 1 );
    Corr4bToBeDoneAfterCorr4d = false( size( InitialGears, 1 ), 1 );
    [InitialGears, Corr4bToBeDoneAfterCorr4a, Corr4bToBeDoneAfterCorr4d] = ...
      applyCorrection4b( InitialGears, Corr4bToBeDoneAfterCorr4a, Corr4bToBeDoneAfterCorr4d);
    [ CorrectionsCells, InitialGearsPrev ] = appendCorrectionCells( CorrectionsCells, InitialGears, InitialGearsPrev, '4b', correction );

    [InitialGears] = applyCorrection4a(InitialGears, Corr4bToBeDoneAfterCorr4a, PhaseStarts, PhaseEnds, PhaseValues);
    [ CorrectionsCells, InitialGearsPrev ] = appendCorrectionCells( CorrectionsCells, InitialGears, InitialGearsPrev, '4a', correction );
    
    % Do an extra delayed gear correction "4s" ( s : short downshift )
    % which was determined during gear correction 4b
    % but shall be done after gear correction 4a.
    % This delayed correction must be suppressed at positions
    % where there is no such short downshift anymore
    % (and at positions where correction 4c will extend such short downshifts)
    Corr4bToBeDoneAfterCorr4a = ...
      Corr4bToBeDoneAfterCorr4a ...
    & diff( [ NaN; InitialGears ] ) < 0 ...
    & diff( [ InitialGears; NaN ] ) > 0 ...
    ;
    Corr4bToBeDoneAfterCorr4a = ...
      Corr4bToBeDoneAfterCorr4a ...
    & next_n_gears_are_higher( 6, InitialGears ) ...
    ;
    InitialGears( Corr4bToBeDoneAfterCorr4a ) = InitialGears( find( Corr4bToBeDoneAfterCorr4a ) - 1 );
    % The Heinz Steven Tool does not check if clutch is "disengaged" or "undefined" for a corrected gear.
    % As each correction lasts only one second it might be resonable to do so.
    % So MATLAB will reset the clutch state "disengaged" or "undefined" for each corrected gear.
    ClutchDisengagedByGear( Corr4bToBeDoneAfterCorr4a, InitialGears( Corr4bToBeDoneAfterCorr4a ) ) = 0;
    ClutchUndefinedByGear ( Corr4bToBeDoneAfterCorr4a, InitialGears( Corr4bToBeDoneAfterCorr4a ) ) = 0;    
    [ CorrectionsCells, InitialGearsPrev ] = appendCorrectionCells( CorrectionsCells, InitialGears, InitialGearsPrev, '4s', correction );

    %-----------------------------------------------------------------------
    % Regulation Annex 2, 4.(c) preface
    %-----------------------------------------------------------------------
    % The modification check described in paragraph 4.(c) of this annex
    % shall be applied to the complete cycle trace twice
    % prior to the application of paragraphs 4.(d) to 4.(f) of this annex.
    %-----------------------------------------------------------------------
    for correction_4c = 1:2
        [ InitialGears ] = applyCorrection4c( InitialGears );
        [ CorrectionsCells, InitialGearsPrev ] = appendCorrectionCells( CorrectionsCells, InitialGears, InitialGearsPrev, '4c', correction );
    end

    [InitialGears] = applyCorrection4d(InitialGears, PhaseStarts, PhaseEnds, PhaseValues);
    [ CorrectionsCells, InitialGearsPrev ] = appendCorrectionCells( CorrectionsCells, InitialGears, InitialGearsPrev, '4d', correction );

    % Do an extra delayed gear correction "4t" ( t : two step downshift )
    % which was determined during gear correction 4b
    % but shall be done after gear correction 4d (according Heinz Steven).
    % This delayed correction must be suppressed at positions
    % where there is no downshift by more than one gear anymore.
    Corr4bToBeDoneAfterCorr4d = Corr4bToBeDoneAfterCorr4d & diff( [ InitialGears; NaN ] ) < -1; 
    if SuppressGear0DuringDownshifts
        nextCorr4bToBeDoneAfterCorr4d = [ false; Corr4bToBeDoneAfterCorr4d( 1:end-1 ) ];
        InitialGears( Corr4bToBeDoneAfterCorr4d ) = InitialGears( nextCorr4bToBeDoneAfterCorr4d ); 
    else
        InitialGears( Corr4bToBeDoneAfterCorr4d ) = 0;
        ClutchDisengaged( Corr4bToBeDoneAfterCorr4d ) = 1;
    end
    
    [ CorrectionsCells, InitialGearsPrev ] = appendCorrectionCells( CorrectionsCells, InitialGears, InitialGearsPrev, '4t', correction );

    % But also such delayed gear corrections "4t" must be undone
    % when an even later 2nd gear correction 4d 
    % reduces such downshifts to downshift by only one gear.
    prevInitialGears = [ 0; InitialGears( 1:end-1 ) ];
    nextInitialGears = [ InitialGears( 2:end ); 0 ];
    idx = find( ...
      InitialGears == 0 ...
    & prevInitialGears - 1 == nextInitialGears ...
    & nextInitialGears > 0 ...
    );
    InitialGears( idx ) = InitialGears( idx - 1 );
    ClutchDisengaged( idx ) = 0;    
    
    [InitialGears, ClutchDisengaged] = applyCorrection4e(InitialGears, PhaseStarts, PhaseEnds, PhaseValues, ClutchDisengaged, InitialRequiredEngineSpeeds, IdlingEngineSpeed);
    [ CorrectionsCells, InitialGearsPrev ] = appendCorrectionCells( CorrectionsCells, InitialGears, InitialGearsPrev, '4e', correction );

    [InitialGears, ClutchDisengaged] = applyCorrection4f(InitialGears, ClutchDisengaged, SuppressGear0DuringDownshifts );
    [ CorrectionsCells, InitialGearsPrev ] = appendCorrectionCells( CorrectionsCells, InitialGears, InitialGearsPrev, '4f', correction );

end


%-----------------------------------------------------------------------
% Regulation Annex 2, 5.(c)
%-----------------------------------------------------------------------
% In order to enable the assessment of the correctness of the calculation,
% the average gear for v >= 1 km/h,
% rounded according to paragraph 7. of this UN GTR to four places of decimal,
% shall be calculated and recorded.
%-----------------------------------------------------------------------
% proposed improvement
%-----------------------------------------------------------------------
% In order to enable the assessment of the correctness of the calculation,
% the checksum of v * gear for v >= 1 km/h,
% rounded according to paragraph 7. of this UN GTR to four places of decimal,
% shall be calculated and recorded.
%-----------------------------------------------------------------------

%% Calculate average gear
PhasesSum = ( Phases ~= PHASE_STANDSTILL & ~isnan( InitialGears ) );
AverageGear = ...
  sum( InitialGears( PhasesSum ) ) ...
/ sum(               PhasesSum   ) ...
;

%% Calculate checksum of v * gear for v >= 1 km/h
ChecksumVxGear = ...
  sum(    InitialGears         ( PhasesSum ) ...
       .* RequiredVehicleSpeeds( PhasesSum ) ...
  ) ...
;

%% Interleave the clutch

for t = 1:TraceTimesCount
	if InitialGears(t) >= 1
		if ClutchDisengagedByGear(t, InitialGears(t)) == 1
			ClutchDisengaged(t) = 1;
		end
		if ClutchUndefinedByGear(t, InitialGears(t)) == 1
			ClutchUndefined(t) = 1;
		end
	end
end

% Annex 2
% 1.5. The prescriptions for the clutch operation
% shall not be applied if the clutch is operated automatically
% without the need of an engagement or disengagement of the driver.
if ~AutomaticClutchOperation ...
&& ~DoNotMergeClutchIntoGearsOutput ...
	% previously it was decided to indicate clutch only during deceleration ...
	InitialGears(InDeceleration & ClutchDisengaged) = -1;
	% ... but now it was decided to indicate the clutch also
	% one second before the 1st gear is used for acceleration from standstill
    InitialGears([AdvancedClutchDisengage{:}]) = -1; 
end

%% Remove duplicate gears

GearSequenceStarts = [1; find(~(isnan(InitialGears(1:end-1)) & isnan(InitialGears(2:end))) & diff(InitialGears) ~= 0) + 1];

GearNames = strcat('MANUAL-', num2str(InitialGears(GearSequenceStarts), '%-d'));	% Convert gear numbers to strings with no space padding by "%-d"
GearNames = cellstr(GearNames);												% Convert to cell array of strings
GearNames = regexprep(GearNames, 'MANUAL-0', 'MANUAL-NEUTRAL');				% Replace "MANUAL-0" by "MANUAL-NEUTRAL"
GearNames = regexprep(GearNames, 'MANUAL--1', 'MANUAL-CLUTCH');				% Replace "MANUAL--1" by "MANUAL-CLUTCH"
GearNames = char(GearNames);												% Convert to character array

% generate clutch state strings as done by Heinz Steven Tool (HST)

ClutchHST = {};
for i = 1:length(ClutchDisengaged)
    if ClutchUndefined(i)
        ClutchHST{i} = 'undefined';
    elseif ClutchDisengaged(i)
        ClutchHST{i} = 'disengaged';
    elseif InitialGears(i) == 0
        % NOTE:
        % HST uses comma ',' after 'engaged'
        % but MATLAB will use semicolon ';' there 
        % for export in comma seperated values file (.csv).
        ClutchHST{i} = 'engaged; gear lever in neutral';
    else
        ClutchHST{i} = 'engaged';
    end
end

%% Assign outputs

CalculatedGearsOutput = {TraceTimes(GearSequenceStarts), GearNames};
AverageGearOutput = round(AverageGear*10000)/10000;
AdjustedMax95EngineSpeed = Max95EngineSpeed;
TraceTimesOutput = TraceTimes;
RequiredVehicleSpeedsOutput = RequiredVehicleSpeeds;
RequiredPowersOutput = RequiredPowers;
RequiredEngineSpeedsOutput = num2cell(InitialRequiredEngineSpeeds, 1);
AvailablePowersOutput = num2cell(InitialAvailablePowers, 1);
PowerCurveOutput = FullPowerCurve;
MaxEngineSpeedCycleOutput = EngineSpeedAtGearAtMaxRequiredSpeed;
MaxEngineSpeedReachableOutput = EngineSpeedAtGearAtMaxVehicleSpeed;
MaxEngineSpeedOutput = MaxEngineSpeed;
MaxVehicleSpeedCycleOutput = max( RequiredVehicleSpeeds );
MaxVehicleSpeedReachableOutput = MaxVehicleSpeed;
GearMaxVehicleSpeedReachableOutput = GearAtMaxVehicleSpeed;
MinDriveEngineSpeed1stOutput = MinDrive1st;
MinDriveEngineSpeed1stTo2ndOutput = MinDrive1stTo2nd;
MinDriveEngineSpeed2ndDecelOutput = MinDrive2ndDecel;
MinDriveEngineSpeed2ndOutput = MinDrive2nd;
MinDriveEngineSpeedGreater2ndOutput = MinDriveGreater2nd;
GearsOutput = InitialGears;
ClutchDisengagedOutput = ClutchDisengaged;
ClutchUndefinedOutput = ClutchUndefined;
ClutchHSTOutput = ClutchHST;
GearCorrectionsOutput = CorrectionsCells;
ChecksumVxGearOutput = round(ChecksumVxGear*10000)/10000;

%% Corrections

	function [ InitialGears ] = applyCorrection4a( InitialGears, Corr4bToBeDoneAfterCorr4a, PhaseStarts, PhaseEnds, PhaseValues)

    PreviousInitialGears = NaN( size( InitialGears ) );
    for i = 1 : 2 * size( InitialGears )
        % The gear at the first gear position to be corrected
        % will be finally corrected after at most two iterations.
        % So the maximum number of iteration required to correct all gears
        % will be at most two times the size of the vector of gears.
        if PreviousInitialGears == InitialGears;
            break
        else
            PreviousInitialGears = InitialGears;
        end

        minPossibleGears = min( PossibleGears, [], 2 );

        %-----------------------------------------------------------------------
        % Regulation Annex 2, 4.(a) :
        %-----------------------------------------------------------------------
        % If a one step higher gear (n+1) is required for only 1 second
        % and the gears before and after are the same (n),
        % or one of them is one step lower (n-1),
        % gear (n+1) shall be corrected to gear n.
        %-----------------------------------------------------------------------

        nextInitialGears = [ InitialGears( 2 : end ); NaN ];
        upshiftsOneOrTwoGearsOneSec = ...
          find( ...
            diff( InitialGears ) == +1 & diff( nextInitialGears ) == -1 ... 
          | diff( InitialGears ) == +1 & diff( nextInitialGears ) == -2 ...
          | diff( InitialGears ) == +2 & diff( nextInitialGears ) == -1 ...
          ) ...
        + 1 ...
        ;
        for shift = upshiftsOneOrTwoGearsOneSec'
            % reduce upshift only if possible for complete duration
            if all( InitialGears( shift ) - 1 >= minPossibleGears( shift ) ) ...
            && all( InitialGears( shift ) - 1 >= 1 )  % avoid neutral gear
                InitialGears( shift ) = InitialGears( shift ) - 1;
            end           
        end
        
        %-----------------------------------------------------------------------
        % 4.(a) continued :
        %-----------------------------------------------------------------------
        % If, during acceleration or constant speed phases
        % or transitions from constant speed to acceleration
        % or acceleration to constant speed phases
        % where these phases only contain upshifts,
        % a gear is used for only one second,
        % the gear in the following second shall be corrected to the gear before,
        % so that a gear is used for at least 2 seconds.
        %
        % This requirement shall not be applied to downshifts during an acceleration phase
        % or if the use of a gear for just one second
        % follows immediately after such a downshift
        % or if the downshift occurs right at the beginning of an acceleration phase.
        % In these cases, the downshifts shall be first corrected
        % according to paragraph 4.(b) of this annex.
        %
        % However, if the gear at the beginning of an acceleration phase
        % is one step lower than the gear in the previous second
        % and the gears in the following (up to five) seconds
        % are the same as the gear in the previous second but followed by a downshift,
        % so that the application of 4.(c) would correct them
        % to the same gear as at the beginning of the acceleration phase,
        % the application of 4.(c) should be performed instead.
        %-----------------------------------------------------------------------

        % if a gear is used for a single second but the next gear is lower
        % then extend this next gear backwards instead of extending the single gear forwards
        % and so avoid that a higher gear with to less power will used after the single second
        % eg RRT vehicle 15, trace seconds 909..918 :
        %   909      918
        %    v        v 
        %    4345545555    InitialGears  
        %      *>            single extended FORWARD  
        %    4344545555    InitialGears 
        %        <*          single extended BACKWARD 
        %    4344445555    InitialGears
        % But such a backward extension of the next gear is not allowed
        % according Heinz Steven (Workshop 2019-02-05)

        InAccelOrConst = InAcceleration | InConstantSpeed; 
 
        singlesInAccelOrConstNextHigher = ...
          InAccelOrConst ...
        & ~ isnan( InitialGears ) ...
        & ( InitialGears >  [ NaN; InitialGears( 1:end-1 ) ] ...   % upshifts only
          | InitialGears == [ NaN; InitialGears( 1:end-1 ) ] & ... % but also unchanged gears
            diff( [ false; InAcceleration ]  ) == 1 ...            % at begin of acceleration phase
          ) ...
        & InitialGears <  [ InitialGears( 2:end ); NaN ] ...  %  gear used for a single second and next gear is HIGHER
        & InitialGears >= [ minPossibleGears( 2:end ); NaN ] ...  % single gear may be extended FORWARD to next second
        ;
            
        % exclude singles immediately after singles
        % as later singles will be adjusted to earlier singles
        singlesInAccelOrConstNextHigher = ...
          singlesInAccelOrConstNextHigher ... 
        & not( [ false; singlesInAccelOrConstNextHigher( 1:end-1 ) ] );

        % exclude singles immediately after downshifts
        singlesInAccelOrConstNextHigher = ...
          singlesInAccelOrConstNextHigher ...
        & ( [ NaN; InitialGears( 1:end-1 ) ] >= [ NaN; NaN; InitialGears( 1:end-2 ) ] ...
          ) ...
        ;
        if any( singlesInAccelOrConstNextHigher )
            InitialGears( [ false; singlesInAccelOrConstNextHigher( 1:end-1 ) ] ) = InitialGears( singlesInAccelOrConstNextHigher );
        end
            
        singlesInAccelOrConstNextLower = ...
          InAccelOrConst ...
        & ~ isnan( InitialGears ) ...
        & ( InitialGears >  [ NaN; InitialGears( 1:end-1 ) ] ...   % upshifts only
          | InitialGears == [ NaN; InitialGears( 1:end-1 ) ] & ... % but also unchanged gears
            diff( [ false; InAcceleration ]  ) == 1 ...            % at begin of acceleration phase
          ) ...
        & InitialGears >  [ InitialGears( 2:end ); NaN ] ...  %  gear used for a single second and next gear is LOWER
        & [ InitialGears( 2:end ); NaN ] >= minPossibleGears ...  % next gear may be extended BACKWARD to single second
        ;
            
        % exclude singles immediately after downshifts
        singlesInAccelOrConstNextLower = ...
          singlesInAccelOrConstNextLower ...
        & ( [ NaN; InitialGears( 1:end-1 ) ] >= [ NaN; NaN; InitialGears( 1:end-2 ) ] ) ...
        ;
        if any( singlesInAccelOrConstNextLower )
            % do a forward extension ignoring possible problems with too less available power
            % exclude singles immediately after singles
            % as later singles will be adjusted to earlier singles
            singlesInAccelOrConstNextLower = ...
              singlesInAccelOrConstNextLower ... 
            & not( [ false; singlesInAccelOrConstNextLower( 1:end-1 ) ] );
            InitialGears( [ false; singlesInAccelOrConstNextLower( 1:end-1 ) ] ) = InitialGears( singlesInAccelOrConstNextLower );
        end

        %-----------------------------------------------------------------------
        % 4.(a) continued :
        %-----------------------------------------------------------------------
        % Furthermore, if the gear in the first second of an acceleration phase
        % is the same as the gear in the previous second
        % and the gear in the following seconds is one step higher,
        % the gear in the second second of the acceleration phase
        % shall be replaced by the gear used in the first second of the acceleration phase
        %-----------------------------------------------------------------------
        % The Heinz Steven Tool ignores the length of the acceleration phases here.
        % So we use InAccelerationAnyDuration instead of InAcceleration here.
        % HST corrects the gear for eg vehicle_no: 109 time: 1088
        % where acceleration phase lasts only for time 1087..1088.
        %-----------------------------------------------------------------------
 
        % but this will only be done
		% if the gear in the first second of the acceleration phase
        % may not be increased by correction 4b to done after correction 4a 

        prevInAccelAnyDur        = [ false; InAccelerationAnyDuration( 1:end-1 ) ];   
        prevPrevNotInAccelAnyDur = [ false; not( prevInAccelAnyDur( 1:end-1 ) ) ];
        prevGears          = [ 0; InitialGears( 1:end-1 ) ];
        prevPrevGears      = [ 0; prevGears( 1:end-1 ) ];
        prev_Corr4bToBeDoneAfterCorr4a = [ false; Corr4bToBeDoneAfterCorr4a( 1:end-1 ) ];

        idx = ...
        ( prevPrevNotInAccelAnyDur ... 
        & prevInAccelAnyDur ...
        & InAccelerationAnyDuration ...
        & prevPrevGears >= prevGears ... 
        & prevGears + 1 == InitialGears ...
        & InitialGears - 1 >= minPossibleGears ...
        & not( prev_Corr4bToBeDoneAfterCorr4a ) ... 
        );
        InitialGears( idx ) = InitialGears( idx ) - 1 ;
        
        %-----------------------------------------------------------------------
        % 4.(a) continued :
        %-----------------------------------------------------------------------
        % Gears shall not be skipped during acceleration phases.
        %-----------------------------------------------------------------------

        % In an acceleration phase :
    	% Decrease a gear, if it differs from the previous non-neutral gear by more than 1 step
        % and the previous gear may not be increased by correction 4b done after correction 4a.  
       
        prev_gear = [ NaN; InitialGears( 1:end-1 ) ];
        upshift = diff( [ InitialGears( 1 ); InitialGears( 1:end ) ] );
        gear_decr_possible = InitialGears - 1 >= minPossibleGears;
        prev_Corr4bToBeDoneAfterCorr4a = [ false; Corr4bToBeDoneAfterCorr4a( 1:end-1 ) ];
        twoStepUpshiftInAcceleration = ...
          prev_gear > 0 ...
        & InAcceleration ...
        & upshift > 1 ...
        & gear_decr_possible ...
        & not( prev_Corr4bToBeDoneAfterCorr4a ) ... 
        ;
        if( any( twoStepUpshiftInAcceleration ) )
            InitialGears( twoStepUpshiftInAcceleration ) = InitialGears( twoStepUpshiftInAcceleration ) - 1;
        end

        %-----------------------------------------------------------------------
        % 4.(a) continued :
        %-----------------------------------------------------------------------
        % However an upshift by two gears is permitted
        % at the transition from an acceleration phase to a constant speed phase
        % if the duration of the constant speed phase exceeds 5 seconds.
        %-----------------------------------------------------------------------

        % At a transition from acceleration phase to a constant speed phase longer than 5 seconds :
    	% Decrease a gear, if it differs from the previous non-neutral gear by more than 2 steps.
    	% But assume that this rule must also be applied at other transitions. 
        % At a transition from acceleration phase to a constant speed phase of up to 5 seconds :
    	% Decrease a gear, if it differs from the previous non-neutral gear by more than 1 step.
		prevInAcceleration   = [ false; InAcceleration( 1:end-1 ) ];
        next1stInConstantSpeed = [        InConstantSpeed( 2:end ); false ];
        next2ndInConstantSpeed = [ next1stInConstantSpeed( 2:end ); false ];
        next3rdInConstantSpeed = [ next2ndInConstantSpeed( 2:end ); false ];
        next4thInConstantSpeed = [ next3rdInConstantSpeed( 2:end ); false ];
        next5thInConstantSpeed = [ next4thInConstantSpeed( 2:end ); false ];
        inConstantSpeedMoreThan5Sec = ...
                 InConstantSpeed ...
        & next1stInConstantSpeed ...
        & next2ndInConstantSpeed ...
        & next3rdInConstantSpeed ...
        & next4thInConstantSpeed ...
        & next5thInConstantSpeed ...
        ;

        prev_gear = [ NaN; InitialGears( 1:end-1 ) ];
        upshift = diff( [ InitialGears( 1 ); InitialGears( 1:end ) ] );
        gear_decr_possible = InitialGears - 1 >= minPossibleGears;
        tooBigUpshiftAtTransition = ... 
          prev_gear > 0 ...
        & prevInAcceleration ...
        & InConstantSpeed ...
        & ( upshift > 1 & ~ inConstantSpeedMoreThan5Sec ...
          | upshift > 2 &   inConstantSpeedMoreThan5Sec ...
          ) ...
        & gear_decr_possible ...
        ; 
        if( any( tooBigUpshiftAtTransition ) )
            InitialGears( tooBigUpshiftAtTransition ) = InitialGears( tooBigUpshiftAtTransition ) - 1;
        end
        
    end  % for-loop
        
    end

        
    function [ InitialGears, Corr4bToBeDoneAfterCorr4a, Corr4bToBeDoneAfterCorr4d ] = ...
      applyCorrection4b( InitialGears, Corr4bToBeDoneAfterCorr4a, Corr4bToBeDoneAfterCorr4d )

        %-----------------------------------------------------------------------
        % Annex 2, 4.(b) :
        %-----------------------------------------------------------------------
        % If a downshift is required during an acceleration phase
        % or at the beginning of the acceleration phase
        % the gear required during this downshift shall be noted (i_DS).
        %
        % The starting point of a correction procedure is defined by either
        % the last previous second when i_DS was identified
        % or by the starting point of the acceleration phase,
        % if all time samples before have gears > i_DS.
        %
        % The highest gear of the time samples before the downshift
        % determines the reference gear i_ref for the downshift.
        % A downshift where i_DS = i_ref - 1
        % is referred to as a one step downshift,
        % a downshift where i_DS = i_ref - 2
        % is referred to as a two step downshift,
        % a downshift where i_DS = i_ref – 3
        % is referred to as a three step downshift. 
        %
        % The following check shall then be applied.
        %
        % (i) One step downshifts
        %
        % Working forward from the starting point of the correction procedure
        % to the end of the acceleration phase,
        % the latest occurrence of a 10 second window
        % containing i_DS for either 2 or more consecutive seconds,
        % or 2 or more individual seconds, shall be identified.
        %
        % The last usage of i_DS in this window
        % defines the end point of the correction procedure.
        % Between the start and end of the correction period,
        % all requirements for gears greater than i_DS
        % shall be corrected to a requirement of i_DS.
        %
        % From the end of the correction period
        % ( in case of 10 second windows containing i_DS
        %   for either 2 or more consecutive seconds,
        %   or 2 or more individual seconds )
        % or from the starting point of the correction procedure
        % ( in case all 10 second windows contain i_DS only for one second
        %   or some 10 second windows contain no i_DS at all ) 
        % to the end of the acceleration phase,
        % all downshifts with a duration of only one second shall be removed.
        %
        % (ii) Two or three step downshifts
        %
        % Working forward from the starting point of the correction procedure
        % to the end of the acceleration phase,
        % the latest occurrence of i_DS shall be identified.
        % From the starting point of the correction procedure
        % all requirements for gears greater than or equal to i_DS
        % up to the latest occurrence of i_DS shall be corrected to (i_DS + 1).
        %
        % (iii)
        % If one step downshifts as well as two step and/or three step downshifts
        % occur during an acceleration phase,
        % three step downshifts shall be corrected
        % before two or one step downshifts are corrected
        % and two step downshifts shall be corrected
        % before one step downshifts are corrected.
        %
        % In such cases, the starting point of the correction procedure
        % for the two or one step downshifts is the second immediately following
        % the end of the correction period for the three step downshifts
        % and the starting point of the correction procedure
        % for the one step downshifts is the second immediately following
        % the end of the correction period for the two step downshifts.
        % 
        % If a three step downshift occurs after a one or two step downshift,
        % it shall overrule this downshifts
        % in the time period before the three step downshift.
        % 
        % If a two step downshift occurs after a one step downshift,
        % it shall overrule the one step downshift
        % in the time period before the two step downshift.
        %
        % This correction shall not be performed for gear 1.
        %-----------------------------------------------------------------------

        %-----------------------------------------------------------------------
        % This will be realized by implementing following simpler rules :
        %-----------------------------------------------------------------------
        % Each downshift by more than one step
        % will limit the maximum usable gears to the gear
        % one step higher than the downshifted gear
        % backwards until the beginning of the acceleration phase 
        %
        % Each downshifted gear used more than once during the last 10 seconds
        % will limit the maximum usable gears to this downshifted gear
        % backwards until the beginning of the acceleration phase 
        %
        % Each isolated downshift lasting only 1 second
        % will be replaced by the previous gear
        %-----------------------------------------------------------------------
        % visualization of rules implemented :
        %-----------------------------------------------------------------------
        % initial gear sequence
        %                                                        o-o-.
        %                                                        |   |
        %                o-o-.           o-o-.   o-o-o-o-o-o-o-o-.   | o-o-o-
        %                |   |           | v |   |                   | |
        %            o-o-.   o-o-.   o-o-.   o-o-.                   o-.
        %            |           |   |
        %        o-o-.           o-o-.
        %        |
        %   -o-o-.
        %
        %-----------------------------------------------------------------------
        %
        %                                          <-----------------> 10 second window
        %                                                            v isolated 2-step downshift
        %    <-------------------------------------------------------> limit earlier gears to 1 step higher level
        %
        %                                                        o-o-.
        %    v v v v v v v v v v v v v v v v v v v v v v v v v v v v |
        %                o-o-.           o-o-.   o-o-o-o-o-o-o-o-*-*-| o-o-o-
        %                |   |           | v |   |                   | |
        %            o-o-.   o-o-.   o-o-.   o-o-.                   o-.
        %            |           |   |
        %        o-o-.           o-o-.
        %        |
        %   -o-o-.
        %
        %-----------------------------------------------------------------------
        %
        %    <-----------------> 10 second window
        %                    <-> lasting 1-step downshift
        %    <-----------------> limit earlier gears to same level
        %
        %                o-o-.           o-o-.   o-o-o-o-o-o-o-o-o-o-. o-o-o-
        %    v v v v v v v v v v         |   |   |                   | |
        %            o-o-*-*-o-o-.   o-o-.   o-o-.                   o-.
        %            |           |   |
        %        o-o-.           o-o-.
        %        |
        %   -o-o-.
        %
        %-----------------------------------------------------------------------
        %
        %        <-----------------> 10 second window
        %                        <-> lasting 1-step downshift
        %    <---------------------> limit earlier gears to same level
        %
        %                                o-o-.   o-o-o-o-o-o-o-o-o-o-. o-o-o-
        %                                |   |   |                   | |
        %            o-o-o-o-o-o-.   o-o-.   o-o-.                   o-.
        %    v v v v v v v v v v v v |
        %        o-o-*-*-*-*-*-*-o-o-.
        %        |
        %   -o-o-.
        %
        %-----------------------------------------------------------------------
        %
        %                    <-----------------> 10 second window
        %                                    <-> lasting 1-step downshift
        %    <---------------------------------> limit earlier gears to same level 
        %
        %                                o-o-.   o-o-o-o-o-o-o-o-o-o-. o-o-o-
        %    v v v v v v v v v v v v v v v v v v |                   | |
        %                            o-o-*-*-o-o-.                   o-.
        %                            |
        %        o-o-o-o-o-o-o-o-o-o-.
        %        |
        %   -o-o-.
        %
        %-----------------------------------------------------------------------
        %
        %                                          <-----------------> 10 second window
        %                                                            * isolated 1-step downshift
        %                                                          *   use previous gear
        %
        %                                        o-o-o-o-o-o-o-o-o-o-*-o-o-o-
        %                                        |                   ^ |
        %                            o-o-o-o-o-o-.                   o-.
        %                            |
        %        o-o-o-o-o-o-o-o-o-o-.
        %        |
        %   -o-o-.
        %
        %-----------------------------------------------------------------------
        % final gear sequence
        %
        %                            o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-
        %                            |
        %        o-o-o-o-o-o-o-o-o-o-.
        %        |
        %   -o-o-.
        %
        %-----------------------------------------------------------------------

        % corrections to be done for all acceleration phases
        AnyAccelerationStarts = PhaseStarts( PhaseValues == PHASE_ACCELERATION | PhaseValues == PHASE_ACCELERATION_FROM_STANDSTILL );
		AnyAccelerationEnds   = PhaseEnds(   PhaseValues == PHASE_ACCELERATION | PhaseValues == PHASE_ACCELERATION_FROM_STANDSTILL );
        AnyAccelerations = arrayfun( @colon, AnyAccelerationStarts, AnyAccelerationEnds, 'Uniform', false );

        for phase = AnyAccelerations' %#ok<FXUP>
            gears = InitialGears( phase{:} )';
            gears_orig = gears;
            
            % do gear corrections in 3 steps :
            % 1. reduce 2-step downshifts backwards
            % 2. extend repeated usages of same downshift gear backwards
            % 3. remove isolated downshifts 
             
            % 1. reduce 2-step downshifts backwards

            gears_greater_one = gears;            
            gears_greater_one( gears <= 1 ) = NaN;  % exclude gear 1

            % limit gears used earlier to at most on step higher than gear used later on
            % cummin() restricts in forward direction
            % but we must restrict gears in backward direction here
            % so reverse gears by fliplr() before and after using cummin()
            gears_max_allowed = fliplr( my_cummin( fliplr( gears_greater_one ) ) + 1 );
            % NOTE: NaN values will be ignored by cummin()

            % gears_max_allowed must not get bigger than NoOfGears
            gears_max_allowed = min( gears_max_allowed, double( NoOfGears ) );
            % NOTE: NaN values will be removed from gears_max_allowed

            gears = min( gears, gears_max_allowed );
            % NOTE: NaN values of will not be removed from gears

            % 2. extend repeated usages of same downshift gear backwards

            % the accumulated number of gear usages per gear
            % will be incremented by each usage of that gear
            use_per_gear = bsxfun( @eq, gears, ( 1 : NoOfGears )' );
            cumulated_use_per_gear = cumsum( use_per_gear, 2 );

            % but after the window size (ie 10 sec) the number of expired gears usages must be subtracted
            % the accumulated decrements have the same size as accumulated increments 
            % calculated a window size earlier
            size_of_window = 10;
            outdated_use_per_gear  = [ zeros( NoOfGears, size_of_window ), cumulated_use_per_gear ];
            outdated_use_per_gear( :, ( end - size_of_window + 1 ) : end ) = []; 

            %   222333444343444444444  gears
            %
            % + 000123333445555555555  cumulated_use_per_gear (eg gear 3)
            %      <-------->          size_of_window (ie 10 sec)           
            % - 000000000000012333344  outdated_use_per_gear (eg gear 3)
            % -----------------------
            %   000123333445543222211  nbr_of_use_per_gear (eg gear 3)
            nbr_of_use_per_gear = cumulated_use_per_gear - outdated_use_per_gear;

            % compress the matrix of number of gear usages per gear
            % to a vector of number of current gear usages
            % NOTE:
            % "gears" may contain NaN if eg no gear offers the required power
            % this NaN values shall be ignored here
            gears_without_nan = gears;
            gears_without_nan( isnan( gears ) ) = 1;  % use dummy gear 1 so that indexing by sub2ind() will not fail ...
            nbr_of_use_gears = nbr_of_use_per_gear( sub2ind( size( nbr_of_use_per_gear ), gears_without_nan, 1 : length( gears ) ) );
            nbr_of_use_gears( isnan( gears ) ) = 0;  % ... but discard number of usages of dummy gear
            
            gears_used_twice = gears;
            gears_used_twice( gears <= 1 ) = NaN;  % exclude gear 1
            gears_used_twice( nbr_of_use_gears < 2 ) = NaN;

            % limit gears used earlier to at most same gear used twice later on
            % cummin() restricts in forward direction
            % but we must restrict gears in backward direction here
            % so reverse gears by fliplr() before and after using cummin()
            gears_max_allowed = fliplr( my_cummin( fliplr( gears_used_twice ) ) );
            gears = min( gears, gears_max_allowed );

            % 3. remove isolated downshifts 

            % downshift is required during an acceleration phase ...
            gears_prev = [ gears( 1 ), gears( 1:end-1 ) ];
            gears_next = [ gears( 2:end ), gears( end ) ];
            % ... or at the beginning of the acceleration phase
            if phase{ 1 }( 1 ) > 1
                gears_prev( 1 ) = InitialGears( phase{ 1 }( 1 ) - 1 );
            end
            gears_greater_one = gears;            
            gears_greater_one( gears <= 1 ) = NaN;  % exclude gear 1
            Corr4bToBeDoneAfterCorr4a( phase{:} ) = ...
              Corr4bToBeDoneAfterCorr4a( phase{:} ) ...
            | gears_prev' > gears_greater_one' & gears_greater_one' < gears_next' ...
            ;

            % NaN values in "gears" may get overwritten by above gear corrections
            % but this values shall be kept to indicate to low power
            gears( isnan( gears_orig ) ) = NaN;    
            InitialGears( phase{:} ) = gears';

            %-----------------------------------------------------------------------
            % Annex 2, 5.(b)
            % (same as previous Annex 2, 4.(b) continued)
            %-----------------------------------------------------------------------
            % After the application of paragraph 4.(b) of this annex,
            % a downshift by more than one gear could occur
            % at the transition from a deceleration or constant speed phase to an acceleration phase. 
            % In this case, the gear for the last sample of the deceleration or constant speed phase
            % shall be replaced by gear 0 and the clutch shall be disengaged.
            % If the "suppress gear 0 during downshifts" option
            % according to paragraph 4.(f) of this annex is chosen,
            % the following lower gear shall be used instead of gear 0.
            %-----------------------------------------------------------------------
            idx_begin = phase{1}(1);
            if idx_begin > 1
                if InitialGears( idx_begin ) - InitialGears( idx_begin - 1 ) < -1
                    % this additional corrections by regulation 4b
                    % shall be done after gear corrections by 4d
                    % (according to Heinz Steven workshop 2018-02-06)
                    Corr4bToBeDoneAfterCorr4d( idx_begin - 1 ) = true;
                end
            end

        end
            
    end


    function [ InitialGears ] = applyCorrection4c( InitialGears )

        %-----------------------------------------------------------------------
        % Regulation Annex 2, 4.(c) :
        %-----------------------------------------------------------------------
        % If gear i is used for a time sequence of 1 to 5 seconds
        % and the gear prior to this sequence is one step lower
        % and the gear after this sequence is one or two steps lower than within this sequence
        % or the gear prior to this sequence is two steps lower
        % and the gear after this sequence is one step lower than within the sequence,
        % the gear for the sequence shall be corrected to 
        % the maximum of the gears before and after the sequence.
        % In all cases i-1 >= i_min shall be fulfilled.
        % NOTE:
        % The corrected gear will be i-1 in all cases.
        % 3.5. Determination of possible gears to be used.
        % The lowest final possible gear is i_min.
        %-----------------------------------------------------------------------

        minPossibleGears = min( PossibleGears, [], 2 );
        for b = 1 : length( InitialGears ) - 2
            if     InitialGears( b   ) >  0 ...
            &&     InitialGears( b+1 ) == InitialGears( b   ) + 1 ...
            &&     InitialGears( b+2 ) == InitialGears( b+1 )
                d = b+2;
                i = 0;
                while d+i <= length( InitialGears ) ...
                &&    InitialGears( d+i ) > InitialGears( b )
                    i = i + 1;
                end
                if i <= 4
                    r = b+1 : d+i-1;  
                    InitialGears( r ) = InitialGears( b );
                    InitialGears( r ) = max( InitialGears( r ), minPossibleGears( r ) );
                end
            elseif InitialGears( b   ) >  0 ...
            &&     InitialGears( b+1 ) == InitialGears( b   ) + 2 ...
            &&     InitialGears( b+2 ) == InitialGears( b+1 )
                d = b+2;
                i = 0;
                while d+i <= length( InitialGears ) ...
                &&    InitialGears( d+i ) ~= InitialGears( b ) + 1
                    i = i + 1;
                end
                if i <= 4
                    r = b+1 : d+i-1;  
                    InitialGears( r ) = InitialGears( b ) + 1;
                    InitialGears( r ) = max( InitialGears( r ), minPossibleGears( r ) );
                end
            end 
        end
    end


    function [InitialGears] = applyExtraCorrection4d(InitialGears, PhaseStarts, PhaseEnds, PhaseValues )

        % the reference implemention from Heinz Steven 
        % does gear correction 4d for RRT vehicle 20 trace seconds 1726:1776
        % ignoring the intermediate constant speed phase at second 1744
        % so we will also include constand speed phases
        % in their surrounding deceleration phases

        % define extra phase values for this gear correction
        ExtraPhaseValues = PhaseValues;

        % undo from/to stillstand discrimination to simplify case discrimination
        ExtraPhaseValues( ExtraPhaseValues == PHASE_ACCELERATION_FROM_STANDSTILL ) = PHASE_ACCELERATION;
        ExtraPhaseValues( ExtraPhaseValues == PHASE_DECELERATION_TO_STANDSTILL ) = PHASE_DECELERATION;

        % include constant speed phases into deceleration phases
        ExtraPreviousPhaseValues = [0; ExtraPhaseValues(1:end-1)];
        ExtraNextPhaseValues = [ExtraPhaseValues(2:end); 0];
        ExtraPhaseValues( ...
          ExtraPreviousPhaseValues == PHASE_DECELERATION ...
        & ExtraPhaseValues         == PHASE_CONSTANT_SPEED ...
        & ExtraNextPhaseValues     == PHASE_DECELERATION ...
        ) = PHASE_DECELERATION;
            
        % redetermine ExtraPhaseValues as multiple phases may have been combined into a single phase

        % expand ExtraPhaseValues to ExtraPhases ...
        ExtraPhaseStarts = cumsum([1; PhaseLengths(1:end-1)]);
        ExtraPhaseChanges = zeros(TraceTimesCount, 1);
        ExtraPhaseChanges(ExtraPhaseStarts) = 1;
        ExtraPhases = ExtraPhaseValues(cumsum(ExtraPhaseChanges));

        % ... and contract ExtraPhases to ExtraPhaseValues again
        ExtraPhaseEnds = [find(ExtraPhases(1:end-1) ~= ExtraPhases(2:end)); length(ExtraPhases)];
        ExtraPhaseLengths = diff([0; ExtraPhaseEnds]);
        ExtraPhaseValues = ExtraPhases(ExtraPhaseEnds);
        ExtraPreviousPhaseValues = [0; ExtraPhaseValues(1:end-1)];
        ExtraNextPhaseValues = [ExtraPhaseValues(2:end); 0];

        % redo from/to stillstand discrimination
        ExtraPhaseValues(ExtraPhaseValues == PHASE_ACCELERATION & ExtraPreviousPhaseValues == PHASE_STANDSTILL) = PHASE_ACCELERATION_FROM_STANDSTILL;
        ExtraPhaseValues(ExtraPhaseValues == PHASE_DECELERATION & ExtraNextPhaseValues == PHASE_STANDSTILL) = PHASE_DECELERATION_TO_STANDSTILL;

        % undefine all phases shorter than or equal to 2 seconds
        ExtraPhaseValues(ExtraPhaseValues ~= PHASE_STANDSTILL & ExtraPhaseValues ~= PHASE_CONSTANT_SPEED & ExtraPhaseLengths <= 2) = 0;

        % expand modified ExtraPhaseValues to ExtraPhases
        ExtraPhaseStarts = cumsum([1; ExtraPhaseLengths(1:end-1)]);
        ExtraPhaseChanges = zeros(TraceTimesCount, 1);
        ExtraPhaseChanges(ExtraPhaseStarts) = 1;
        ExtraPhases = ExtraPhaseValues(cumsum(ExtraPhaseChanges));

        [InitialGears] = applyCorrection4d(InitialGears, ExtraPhaseStarts, ExtraPhaseEnds, ExtraPhaseValues);

    end
   

	function [InitialGears] = applyCorrection4d(InitialGears, PhaseStarts, PhaseEnds, PhaseValues)

        %-----------------------------------------------------------------------
        % Regulation Annex 2, 4.(d) :
        %-----------------------------------------------------------------------
        % No upshift to a higher gear shall be performed within a deceleration phase.
        %-----------------------------------------------------------------------
        % NOTE:
        % The newest regulation ECE/TRANS/WP.29/GRPE/2019/2
        % moved the text part below to paragraph Annex 2, 4.(e).
        % But we keep it here as it does not matter
        % whether it will be executed at the end of 4.(d) or at the begin of 4.(e). 
        %-----------------------------------------------------------------------
        % No upshift to a higher gear at the transition
        % from an acceleration or constant speed phase
        % to a deceleration phase shall be performed
        % if one of the gears in the first two seconds
        % following the end of the deceleration phase         
        % is lower than the upshifted gear or is gear 0.              
	    % If there is an upshift during the transition
        % and the initial deceleration phase by 2 gears,
        % an upshift by 1 gear shall be performed instead.
        % In this case, no further modifications shall be perfomed
        % in the following gear use checks.
        %-----------------------------------------------------------------------

        AnyDecelerationStarts = PhaseStarts(PhaseValues == PHASE_DECELERATION | PhaseValues == PHASE_DECELERATION_TO_STANDSTILL);
		AnyDecelerationEnds = PhaseEnds(PhaseValues == PHASE_DECELERATION | PhaseValues == PHASE_DECELERATION_TO_STANDSTILL);
        AnyDecelerations = arrayfun(@colon, AnyDecelerationStarts, AnyDecelerationEnds, 'Uniform', false);
        for phase = AnyDecelerations' %#ok<FXUP>
            
            % apply correction to each phase only once
            if any( corr_4d_applied_before( phase{ : } ) )
                continue
            end
            
            % NOTE:
            % the phase before a deceleration phase
            % is guaranteed to be either a acceleration phase or a constant speed phase
            % because it can neither be a stillstand phase nor another deceleration phase

            % correction 4a requires that each gear must be used for at least 2 sec during acceleration
            % this may lead to a delayed usage of higher gears even in the subsequent deceleration phase
            % so an upshift at the transition from acceleration to deceleration phase
            % may occur not immediately at the first second of the transition but some seconds later
            % therefore we will regard any upshift occuring during the first 3 seconds of the deceleration phase
            % as being related to the transition            
            % eg RRT vehicle 23, trace seconds 605..616 :
            %   605        616 
            %    v          v 
            %    AAAAAAAAADDD  A:acceleration D:deceleration
            %    223456677777  g_max
            %    223344556677  gear corr 4a : use each gear for at least 2 sec
            %              ^   delayed usage of higher gear after transition A->D
            
            g_max_at_transition = max( InitialGears( phase{ 1 }( 1 : min( 3, length( phase{ 1 } ) ) ) ) );
           
            if phase{ 1 }( 1 ) - 1 >= 1 ...                                     % avoid indexing before trace
            && g_max_at_transition > InitialGears( phase{ 1 }( 1 ) - 1 ) ...    % upshift at begin of deceleration phase
            && InitialGears( phase{ 1 }( 1 ) - 1 ) > 0 ...                      % exclude neutral gear
            && phase{ 1 }( end ) + 2 <= TraceTimesCount ...                     % avoid indexing after trace
            && (  g_max_at_transition > InitialGears( phase{ 1 }( end ) + 1 ) ...  % 1st gear after deceleration phase is lower
               || g_max_at_transition > InitialGears( phase{ 1 }( end ) + 2 ) ...  % 2nd gear after deceleration phase is lower
               || InitialGears( phase{ 1 }( end ) + 1 ) == 0 ...                   % 1st gear after deceleration phase is zero
               || InitialGears( phase{ 1 }( end ) + 2 ) == 0 ...                   % 2nd gear after deceleration phase is zero
               )
          % && InitialGears( phase{ 1 }( end ) + 1 ) > 0 ...                    % exclude neutral gear
                switch( g_max_at_transition - InitialGears( phase{ 1 }( 1 ) - 1 ) )
                case 1
                    % single step upshift 
                    % disable upshifts to gears higher than used before decelaration phase
                    InitialGears( phase{ : } ) = min( InitialGears( phase{ : } ), InitialGears( phase{ 1 }( 1 ) - 1 ) );
                    corr_4d_applied_before( phase{ : } ) = true;          
                case num2cell( 2 : NoOfGears )
                    % multiple step upshift
                    % limit upshifts to gears at most one step higher than used before deceleration phase 
                    InitialGears( phase{ : } ) = min( InitialGears( phase{ : } ), InitialGears( phase{ 1 }( 1 ) - 1 ) + 1 );
                    % correction was applied to current phase
                    corr_4d_applied_before( phase{ : } ) = true;          
                end
            end
            
            % no upshift to a higher gear shall be performed within a deceleration phase

            % but Heinz Steven Tool extends a deceleration phase by a following constant speed second
            % when handling gear correction "no upshift during decel"
            % eg for RRT vehicle 20 time 1744
            % 2019-02-26 found that HST extends a deceleration phase also by a following acceleration second 
            % eg for RRT vehicle 20 time 670 when using n_min_drive_down = 1500 
            phase_ext = phase{ : };
            if length( RequiredVehicleSpeeds ) >= phase_ext( end ) + 2 
                if RequiredVehicleSpeeds( phase_ext( end ) + 1 ) >= 1 ...
                && (    abs( diff( RequiredVehicleSpeeds( phase_ext( end ) + 1 : phase_ext( end ) + 2 ) ) ) < 0.001 ...
                     ||      diff( RequiredVehicleSpeeds( phase_ext( end ) + 1 : phase_ext( end ) + 2 ) )   > 0     )
                    phase_ext = [ phase_ext, phase_ext( end ) + 1 ];
                end
            end
            gears = InitialGears( phase_ext );
            idx_neutral = find( gears == 0 );  % gear 0 must be ignored
            gears( idx_neutral ) = NoOfGears;  % replace gear 0 by gear max so that it will not affect cummin()
            gears = my_cummin( gears );        % disable any upshifts by cummin()
            gears( idx_neutral ) = 0;          % re-establish gear 0                
            InitialGears( phase_ext ) = gears;

        end
     
    end


    function [InitialGears, ClutchDisengaged] = applyCorrection4e(InitialGears, PhaseStarts, PhaseEnds, PhaseValues, ClutchDisengaged, InitialRequiredEngineSpeeds, IdlingEngineSpeed)
 
        %-----------------------------------------------------------------------
        % Regulation Annex 2, 4.(e) :
        %-----------------------------------------------------------------------
        % NOTE:
        % The newest regulation ECE/TRANS/WP.29/GRPE/2019/2
        % moved this gear correction to paragraph
        % 3.3. Selection of possible gears with respect to engine speed.
        % But we keep it here to check also additional usages of gear 2,
        % which may result from other gear corrections done before. 
        %-----------------------------------------------------------------------
        % During a deceleration phase,
        % gears with n_gear > 2 shall be used
        % as long as the engine speed does not drop below n_min_drive. 
        % Gear 2 shall be used during a deceleration phase
        % within a short trip of the cycle (not at the end of a short trip)
        % as long as the engine speed does not drop below (0.9 × n_idle). 
        % If the engine speed drops below n_idle,
        % the clutch shall be disengaged.
        % If the deceleration phase is the last part of a short trip
        % shortly before a stop phase,
        % the second gear shall be used 
        % as long as the engine speed does not drop below n_idle.
        %-----------------------------------------------------------------------

        AnyDecelerationStarts = ...
          PhaseStarts( ...
            PhaseValues == PHASE_DECELERATION ...
          | PhaseValues == PHASE_DECELERATION_TO_STANDSTILL ...
          ) ...
        ;
        AnyDecelerationEnds = ...
          PhaseEnds( ...
            PhaseValues == PHASE_DECELERATION ...
          | PhaseValues == PHASE_DECELERATION_TO_STANDSTILL ...
          ) ...
        ;
        AnyDecelerations = arrayfun( @colon, AnyDecelerationStarts, AnyDecelerationEnds, 'Uniform', false );

        secondGearsWithLowEngineSpeeds = find( ...
          InitialGears == 2 ...
        & ( ( Phases == PHASE_DECELERATION ...
            & InitialRequiredEngineSpeeds(:, 2) < 0.9 * IdlingEngineSpeed ...
            ) ...
          | ( Phases == PHASE_DECELERATION_TO_STANDSTILL ...
            & InitialRequiredEngineSpeeds(:, 2) < IdlingEngineSpeed ...
            ) ...
          ) ...  
        );

        for phase = AnyDecelerations' %#ok<FXUP>
            secondGearsWithLowEngineSpeedsInPhase = ... 
              secondGearsWithLowEngineSpeeds( ...
                secondGearsWithLowEngineSpeeds >= phase{:}(1) ...
              & secondGearsWithLowEngineSpeeds <= phase{:}(end) ...
              ) ...
            ;
            ClutchDisengaged( secondGearsWithLowEngineSpeedsInPhase ) = 1;
            
            % Additional correction get the same results as the Heinz Steven Tool
            % (eg for RRT vehicle 8, trace seconds 94:95, 440, 525, 1449, 1792:1793).
            % HST seems to do gear correction 4f (eg 33322111 -> 33301111)
            % while Matlab substitutes gear 1 by gear 2 before (eg 33322111 -> 33322222).
            % To compensate this an additional correction will be done here:
            % If gear 2 would only be used for 1 or 2 seconds before becomming disengaged
            % then disengage gear 2 also during this initial seconds.
            if ~ isempty( secondGearsWithLowEngineSpeedsInPhase )
                t_clutch = min( secondGearsWithLowEngineSpeedsInPhase );
                if InitialGears( t_clutch - 1 ) == 2 ...
                && InitialGears( t_clutch - 2 ) ~= 2
                    ClutchDisengaged( t_clutch - 1 ) = 1;
                end
                if InitialGears( t_clutch - 1 ) == 2 ... 
                && InitialGears( t_clutch - 2 ) == 2 ...
                && InitialGears( t_clutch - 3 ) ~= 2  
                    ClutchDisengaged( t_clutch - 1 ) = 1;
                    ClutchDisengaged( t_clutch - 2 ) = 1;
                end
            end            
        end

    end


    function [ InitialGears, ClutchDisengaged ] = applyCorrection4f( InitialGears, ClutchDisengaged, SuppressGear0DuringDownshifts )

        gear = InitialGears;
        i_max = length( gear );
        gear_max = max( PossibleGears, [], 2 );
        % The "i_max" mentioned in the regulation text
        % is the maximum possible gear NUMBER usable at a certain time.
        % In this code this is defined by gear_max(i). 

        % determine extended phases of standstill
        % including leading phases of gear 0 usage
        InStandStillExtended = InStandStill;
        for i = i_max-1 : -1: 1
            if gear( i ) == 0 && InStandStillExtended( i+1 )
                InStandStillExtended( i ) = true;
            end
        end
 
        for i = 1 : i_max
            % NOTE:
            % In the gear sequence examples shown by the regulation text
            % eg "j, 0, i, i, i-1, k"
            % the letters "i", "j" and "k" denote gear NUMBERS.
            % But in this for-loop the letter "i" is the time INDEX of the gear
            % which possibly will be replaced by gear 0.
            % So the time indices for the regulation example above are i-1:i+4
            % and the related gear numbers are defined by gear(i-1:i+4).

            replaced = false; 

            % Heinz Steven Tool 2019-10-08 corrects the gear sequence
            % for vehicle 114 time 434..443
            % from 5 5 5 4 4 3 2 0 0 0
            % to   5 5 5 0 0 0 0 0 0 0
            % while it should have been corrected
            % to   5 5 5 0 2 2 2 0 0 0
            % So we correct such exceptional gear sequences like Heinz Steven.
            if i-1  >= 1     ...
            && i+5  <= i_max ...
            && all( InDecelerationToStandstill( i-1 : i+5 ) ) ...
            && gear(i-1) >  gear(i  ) ...
            && gear(i  ) == gear(i+1) ...
            && gear(i+1) >  gear(i+2) ...
            && gear(i+2) >  gear(i+3) ...
            && gear(i+3) >  1 ...
            && gear(i+4) <= 1 ...
            && gear(i+5) <= 1
              gear(i  ) = 0;
              gear(i+1) = 0;
              gear(i+2) = 0;
              gear(i+3) = 0;
            end

            %-------------------------------------------------------------------
            % Regulation Annex 2, 4.(f) :
            %-------------------------------------------------------------------
            % If during a deceleration phase the duration of a gear sequence
            % (a time sequence with constant gear)
            % between two gear sequences of 3 seconds or more
            % is only 1 second,
            % it shall be replaced by gear 0 and "the clutch shall be disengaged.
            %-------------------------------------------------------------------
            % NOTE: Another text later was moved to the begin of regulation 4.(f).
            %-------------------------------------------------------------------
            if      i-3  >= 1         ...
            &&      i+3  <= i_max     ...
            && all( InDeceleration( i-3 : i+3 ) ) ...
            && gear(i-3) == gear(i-2) ...
            && gear(i-2) == gear(i-1) ...
            && gear(i-1) ~= gear(i  ) ...
            && gear(i  ) ~= gear(i+1) ...
            && gear(i+1) == gear(i+2) ...
            && gear(i+2) == gear(i+3)

                gear(i) = 0;
                ClutchDisengaged(i) = 1;
                replaced = true;

            %-------------------------------------------------------------------
            % If during a deceleration phase the duration of a gear period
            % (a time sequence with constant gear)
            % between two gear sequences of 3 seconds or more
            % is 2 seconds,
            % it shall be replaced by gear 0 for the 1st second
            % and for the 2nd second with the gear
            % that follows after the 2 second period.
            % The clutch shall be disengaged for the 1st second.
            % This requirement shall only be applied
            % if the gear that follows after the 2 second period is > 0.
            %-------------------------------------------------------------------        
            elseif  i-3  >= 1         ...
            &&      i+4  <= i_max     ...
            && all( InDeceleration( i-3 : i+4 ) ) ...
            && gear(i-3) == gear(i-2) ...
            && gear(i-2) == gear(i-1) ...
            && gear(i-1) ~= gear(i  ) ...
            && gear(i  ) == gear(i+1) ...
            && gear(i+1) ~= gear(i+2) ...
            && gear(i+2) >  0         ...
            && gear(i+2) == gear(i+3) ...
            && gear(i+3) == gear(i+4)

                gear(i) = 0;
                ClutchDisengaged(i) = 1;
                gear(i+1) = gear(i+2);
                replaced = true;

            %-------------------------------------------------------------------
            % If several gear sequences with durations of 1 or 2 seconds
            % follow one another, corrections shall be performed as follows:
            %-------------------------------------------------------------------

            %-------------------------------------------------------------------
            % A gear sequence 
            %       i, i, i, i-1, i-1, i-2  or
            %       i, i, i, i-1, i-2, i-2 
            % shall be changed to
            %   ==> i, i, i,   0, i-2, i-2
            % with i-2 > 0
            %-------------------------------------------------------------------
            elseif  i-3     >= 1         ...
            &&      i+2     <= i_max     ...
            && all( InDeceleration( i-1 : i ) ) ...  
            && gear(i-3)    == gear(i-2) ...
            && gear(i-2)    == gear(i-1) ...
            && gear(i-1) -1 == gear(i  ) ...
            && (     gear(i  )    == gear(i+1) ...
                  && gear(i+1) -1 == gear(i+2) ...
               ||    gear(i  ) -1 == gear(i+1) ...
                  && gear(i+1)    == gear(i+2) ...
               )                               ...
            && gear(i+2)    >  0

                gear(i) = 0;
                ClutchDisengaged(i) = 1;
                gear(i+1) = gear(i+2);
                replaced = true;

            %-------------------------------------------------------------------
            % A gear sequence such as
            %       i, i, i, i-1, i-2, i-3  or
            %       i, i, i, i-2, i-2, i-3  or 
            %       other possible combinations
            % shall be changed to
            %   ==> i, i, i,   0, i-3, i-3
            % with i-3 > 0
            %-------------------------------------------------------------------
            % what are "other possible combinations" ?
            % found that HST for RRT vehicle 32 time 1529:1534 replaces also
            % 6 6 6 5 2 2 -> 6 6 6 0 2 2 2
            % so also following correction must also be done :
            %       i, i, i, i-1, i-4, i-4
            % shall be changed to
            %   ==> i, i, i,   0, i-4, i-4
            % assume following generalization :
            % - the last three gears must not be increasing
            % - the last gear must be three or more steps below first gear (i)
            %-------------------------------------------------------------------
            elseif  i-3     >= 1         ...
            &&      i+2     <= i_max     ...
            && all( InDeceleration( i-1 : i ) ) ...  
            && gear(i-3)    == gear(i-2) ...
            && gear(i-2)    == gear(i-1) ...
            && (  gear(i-1) -1 ==  gear(i  ) ...
               || gear(i-1) -2 ==  gear(i  ) ...
               )                             ...
            && gear(i  )    >= gear(i+1) ...
            && gear(i+1)    >= gear(i+2) ...
            && gear(i+2) +3 <= gear(i-1) ...
            && gear(i+2)    >  0

                gear(i) = 0;
                ClutchDisengaged(i) = 1;
                gear(i+1) = gear(i+2);
                replaced = true;

            end
            %-------------------------------------------------------------------
            % This change shall also be applied to gear sequences
            % where the acceleration is >= 0 for the first 2 seconds
            % and < 0 for the 3rd second
            % or where the acceleration is >= 0 for the last 2 seconds.
            %-------------------------------------------------------------------
            % IMPLEMENTED ABOVE AS: all( InDeceleration( i-1 : i ) )
            %-------------------------------------------------------------------
  
            %-------------------------------------------------------------------
            % In all cases specified above in this sub-paragraph,
            % the clutch disengagement (gear 0) for 1 second is used
            % in order to avoid too high engine speeds for this second.
            % If this is not an issue and, if requested by the manufacturer,
            % it is allowed to use the lower gear of the following second
            % directly instead of gear 0 for downshifts of up to 3 steps.
            % The use of this option shall be recorded.
            %-------------------------------------------------------------------
            % NOTE: This text is a later part of the regulation text. 
            %-------------------------------------------------------------------
            if replaced                      ... 
            && SuppressGear0DuringDownshifts ...
            && i-1 >= 1                      ...
            && i+1 <= i_max                  ...
            && gear(i-1) -3 <= gear(i+1)
                gear(i) = gear(i+1);
                ClutchDisengaged(i) = 0;
                replaced = false;
            end 

            %-------------------------------------------------------------------
            % For extreme transmission designs, it is possible
            % that gear sequences with durations of 1 or 2 seconds
            % following one another may last up to 7 seconds.
            % In such cases, the correction above shall be complemented 
            % by the following correction requirements in a second step:
            %-------------------------------------------------------------------
            % NOTE: This text is a earlier part of the regulation text. 
            %-------------------------------------------------------------------
            if replaced
            
                %---------------------------------------------------------------
                % If gear i-1 is one or two steps below i_max
                % for second 3 of this sequence (one after gear 0). 
                % A gear sequence shall be changed :
                %       j, 0, i  , i  , i-1, k   
                %   ==> j, 0, i-1, i-1, i-1, k
                %       with j > i+1 and 0 < k <= i-1
                %---------------------------------------------------------------
                if      i-1     >= 1             ...
                &&      i+4     <= i_max         ...
                && gear(i-1)    >  gear(i+1) + 1 ...
                && gear(i  )    == 0             ...
                && gear(i+1)    == gear(i+2)     ...
                && gear(i+2) -1 == gear(i+3)     ...
                && gear(i+3)    >= gear(i+4)     ...
                && gear(i+3) +2 >= gear_max(i+1) ...
                && gear(i+4)    >  0

                    gear(i+1) = gear(i+3);
                    gear(i+2) = gear(i+3);
     
                %---------------------------------------------------------------
                % If gear i-1 is more than two steps below i_max
                % for second 3 of this sequence
                % A gear sequence shall be changed :
                %       j, 0, i  , i  , i-1, k 
                %   ==> j, 0, 0  , k  , k  , k 
                %       with j > i+1 and 0 < k <= i-1
                %---------------------------------------------------------------
                elseif  i-1     >= 1             ...
                &&      i+4     <= i_max         ...
                && gear(i-1)    >  gear(i+1) + 1 ...
                && gear(i  )    == 0             ...
                && gear(i+1)    == gear(i+2)     ...
                && gear(i+2) -1 == gear(i+3)     ...
                && gear(i+3)    >= gear(i+4)     ...
                && gear(i+3) +2 <  gear_max(i+1) ...
                && gear(i+4)    >  0

                    gear(i+1) = 0;
                    ClutchDisengaged(i+1) = 1;
                    gear(i+2) = gear(i+4);
                    gear(i+3) = gear(i+4);

                %---------------------------------------------------------------
                % If gear i-2 is one or two steps below i_max
                % for second 3 of this sequence (one after gear 0). 
                % A gear sequence shall be changed :
                %       j, 0, i  , i  , i-2, k 
                %   ==> j, 0, i-2, i-2, i-2, k 
                %       with j > i+1 and 0 < k <= i-2 
                %---------------------------------------------------------------
                elseif  i-1     >= 1             ...
                &&      i+4     <= i_max         ...
                && gear(i-1)    >  gear(i+1) + 1 ...
                && gear(i  )    == 0             ...
                && gear(i+1)    == gear(i+2)     ...
                && gear(i+2) -2 == gear(i+3)     ...
                && gear(i+3)    >= gear(i+4)     ...
                && gear(i+3) +2 >= gear_max(i+1) ...
                && gear(i+4)    >  0

                    gear(i+1) = gear(i+3);
                    gear(i+2) = gear(i+3);

                %---------------------------------------------------------------
                % If gear i-2 is more than two steps below i_max
                % for second 3 of this sequence,
                %       j, 0, i  , i  , i-2, k 
                %   ==> j, 0, 0  , k  , k  , k
                %       with j > i+1 and 0 < k <= i-2
                %---------------------------------------------------------------
                elseif  i-1     >= 1             ...
                &&      i+4     <= i_max         ...
                && gear(i-1)    >  gear(i+1) + 1 ...
                && gear(i  )    == 0             ...
                && gear(i+1)    == gear(i+2)     ...
                && gear(i+2) -2 == gear(i+3)     ...
                && gear(i+3)    >= gear(i+4)     ...
                && gear(i+3) +2 <  gear_max(i+1) ...
                && gear(i+4)    >  0

                    gear(i+1) = 0;
                    ClutchDisengaged(i+1) = 1;
                    gear(i+2) = gear(i+4);
                    gear(i+3) = gear(i+4);

                end

            end  % if replaced

            %-------------------------------------------------------------------
            % If the deceleration phase is the last part of a short trip
            % shortly before a stop phase
            % and the last gear > 0 before the stop phase
            % is used only for a period of up to 2 seconds,
            % gear 0 shall be used instead
            % and the gear lever shall be placed in neutral
            % and the clutch shall be engaged.
            %-------------------------------------------------------------------
            % NOTE: This text later was moved to the begin of regulation 4.(f).
            %-------------------------------------------------------------------

            if      i-1  >  1         ...
            &&      i+1  <= i_max     ...
            && all( InDecelerationToStandstill( i-1 : i ) ) ...
            && InStandStillExtended( i+1 ) ...
            && gear(i  ) >  0         ...
            && gear(i-1) ~= gear(i  ) ...
            && gear(i  ) ~= gear(i+1)

                % decelaration to standstill with last non-zero gear used for 1 second
                gear(i) = 0;
                ClutchDisengaged(i  ) = 0;

            elseif  i-1  >  1         ...
            &&      i+2  <= i_max     ...
            && all( InDecelerationToStandstill( i-1 : i+1 ) ) ...
            && InStandStillExtended( i+2 ) ...
            && gear(i  ) >  0         ...
            && gear(i-1) ~= gear(i  ) ...
            && gear(i  ) == gear(i+1) ...
            && gear(i+1) ~= gear(i+2)

                % decelaration to standstill with last non-zero gear used for 2 seconds
                gear(i) = 0;
                ClutchDisengaged(i) = 0;
                gear(i+1) = 0;
                ClutchDisengaged(i+1) = 0;

            end 

        end  % for i

        %-----------------------------------------------------------------------
        % A downshift to first gear is not permitted
        % during those deceleration phases.
        % If such a downshift would be necessary
        % in the last part of a short trip just before a stop phase,
        % since the engine speed would drop below n_idle in 2nd gear,
        % gear 0 shall be used instead
        % and the gear lever shall be placed in neutral
        % and the clutch shall be engaged.
        %
        % If the first gear is required in a time oeriod of the least 2 seconds
        % imemdiately before of a deceleration to stop,
        % this gear should be used until the first sample of the deceleration phase.
        % For the rest of the deceleration phase,
        % gear 0 shall be used and the gear lever shall be placed in neutral
        % and the clutch shall be engaged.       
        %-----------------------------------------------------------------------
        % NOTE: This text later was moved to an earlier position of regulation 4.(f).
        %-----------------------------------------------------------------------

        InDecelerationToStandstillPrev = [ false; InDecelerationToStandstill( 1:end-1 ) ];
        gear( ...
          InDecelerationToStandstillPrev ...
        & InDecelerationToStandstill ...
        & gear == 1 ...
        ) = 0;
        gearPrev = [ 0; gear( 1:end-1 ) ];

        % additional correction required for eg :
        % - HST vehicle_no: 109 time: 1446
        % - HST vehicle_no: 111 time: 1446
        BeginDecelerationToStandstillGear1Engaged = ...                     
          ~InDecelerationToStandstillPrev ...
        &  gearPrev ~= 1 ...
        &  InDecelerationToStandstill ...
        &  gear == 1 ...
        & ~ClutchDisengaged ...
        ;
        gear            ( BeginDecelerationToStandstillGear1Engaged ) = 0;
        ClutchDisengaged( BeginDecelerationToStandstillGear1Engaged ) = 1;       
        
        % If gear 0 with disengaged clutch was inserted by above gear corrections
        % then futher gear corrections may have lead to an immediately
        % following gear 0 with engaged clutch.
        % In this cases the clutch shall already be engaged for the inserted gear 0.
        % But this shall not be done for the additional correction above for eg :
        % - HST vehicle_no: 109 time: 1446
        % - HST vehicle_no: 111 time: 1446
        % ie it shall not be done at the begin of deceleration to standstill.
        InDecelerationToStandstillPrev = [ false; InDecelerationToStandstill( 1:end-1 ) ];
        InDecelerationToStandstillNext = [ InDecelerationToStandstill( 2:end ); false ];
        gearNext = [ gear( 2:end ); 0 ]; 
        ClutchDisengagedNext = [ ClutchDisengaged( 2:end ); false ];
        ClutchDisengaged( ...
           InDecelerationToStandstillPrev ...
        &  InDecelerationToStandstill ...
        &  InDecelerationToStandstillNext ...
        &  gear     == 0 ...
        &  gearNext == 0 ...
        &  ClutchDisengaged ...
        & ~ClutchDisengagedNext ...
        ) = false;

        InitialGears = gear;

    end


    function [ CorrectionsCells, InitialGearsPrev ] = appendCorrectionCells( CorrectionsCells, InitialGears, InitialGearsPrev, correctionType, correctionNbr );
        % This function is just for debugging of gear corrections.
        % It extends a cell array of gear correction strings
        % by the current corrections and the resulting corrected gears.
        % Each gear correction is indicated by a string combining correction type and number.
        % If eg gear 2 is corrected to gear 3 by correction '4a' during the first iteration  
        % then the gear correction string will be extended by ' 4a1 3'.
        % If eg gear 2 is not corrected
        % then the gear correction string will be extended by ' --- 2'. 
        % If the iteration number is 0 then gear correction string will just be inited with the initial gears.
        % Clutch will be indicated by single char 'C' (not by '-1').
        % Gear 10 will be indicated by single char 'X' (not by '10').
        % Non-existing gears will be indicated by single char '?' (not by 'NaN').
        %
        % Output parameters :
        %   CorrectionsCells
        %     A cell array of gear correction strings AFTER the current correction
        %     eg
        %       ...
        %       '4 --- 4 4b1 2 --- 2 --- 2 --- 2 --- 2 --- 2 --- 2 --- 2 --- 2 --- 2 --- 2 --- 2 --- 2 --- 2 --- 2 --- 2 --- 2 --- 2 --- 2 --- 2'
        %       '4 --- 4 4b1 3 --- 3 --- 3 --- 3 --- 3 --- 3 --- 3 --- 3 --- 3 --- 3 --- 3 --- 3 --- 3 --- 3 --- 3 --- 3 --- 3 --- 3 --- 3 --- 3'
        %       '5 --- 5 4b1 4 --- 4 --- 4 --- 4 --- 4 --- 4 --- 4 4b2 3 --- 3 --- 3 --- 3 --- 3 --- 3 --- 3 --- 3 --- 3 --- 3 --- 3 --- 3 --- 3'
        %       '5 --- 5 --- 5 4c1 4 --- 4 --- 4 --- 4 --- 4 --- 4 --- 4 --- 4 --- 4 --- 4 --- 4 4g2 3 --- 3 --- 3 --- 3 --- 3 --- 3 --- 3 --- 3'
        %       '5 --- 5 --- 5 4c1 4 --- 4 --- 4 --- 4 --- 4 --- 4 --- 4 --- 4 --- 4 --- 4 --- 4 4g2 3 --- 3 --- 3 --- 3 --- 3 --- 3 --- 3 --- 3'
        %       ...
        %   InitialGearsPrev
        %     A cell array of gear numbers AFTER current correction ie before next correction
        %
        % Input parameters :
        %   CorrectionsCells
        %     A cell array of gear correction strings BEFORE the current correction
        %   InitialGears
        %     A cell array of gear numbers AFTER the current correction
        %   InitialGearsPrev
        %     A cell array of gear numbers BEFORE the current correction
        %   correctionType
        %     A string indicating the type of the current correction
        %     eg '4c'
        %   correctionNbr
        %     A number indicating the iteration of the current correction
        
        InitialGearsCells = cellstr( num2str( InitialGears, '%d' ) );
        InitialGearsCells = regexprep( InitialGearsCells, '-1', 'C' );
        InitialGearsCells = regexprep( InitialGearsCells, '10', 'X' );
        InitialGearsCells = regexprep( InitialGearsCells, 'NaN', '?' );
        InitialGearsCells = regexprep( InitialGearsCells, ' *', '' );
        if correctionNbr == 0
            CorrectionsCells = InitialGearsCells;
        else
            BlankCells = regexprep( InitialGearsCells, '.*', ' ' );
            ChangedGearsCells = regexprep( InitialGearsCells, '.*', '---' );
            ChangedGearsCells( InitialGears ~= InitialGearsPrev ) = cellstr( strcat( correctionType, num2str( correctionNbr ) ) );
            ChangedGearsCells( isnan( InitialGears ) & isnan( InitialGearsPrev ) ) = cellstr( '---' );
            CorrectionsCells = strcat( CorrectionsCells, BlankCells, ChangedGearsCells, BlankCells, InitialGearsCells );
        end
        InitialGearsPrev = InitialGears;
    end


    % Matlab function "cummin" was introduced in Matlab R2014b
    % define a substitute for earlier versions
    function [ M ] = my_cummin( A )
        min_val = NaN;
        for i = 1 : length(A)
            if isnan( min_val )
                min_val = A(i);
            elseif isnan( A(i) )
                % ignored
            elseif A(i) < min_val
                min_val = A(i);
            end
            M(i) = min_val;
        end
    end


    function [ ...
      ASM ...
    ] = ExponentialDecayingASM ( ...
      EngineSpeed ...
    , AdditionalSafetyMargin0 ...
    , StartEngineSpeed ...
    , EndEngineSpeed ...
    )
        if AdditionalSafetyMargin0 == 0
            ASM = 0;
        elseif EngineSpeed <= StartEngineSpeed
            ASM = AdditionalSafetyMargin0;
        else
            ASM = ...
              AdditionalSafetyMargin0 ...
            * exp( ...
                log( 0.5 / AdditionalSafetyMargin0 ) ...
                * (    EngineSpeed - StartEngineSpeed ) ...
                / ( EndEngineSpeed - StartEngineSpeed ) ...
              ) ...
            ;
            % In MATLAB the ASM values have the unit "percent" with a range 0 to 100
            % while in the regulation the assumed unit is "fraction" with a range 0 to 1.
            % Therefore the value of the constant 0.005 used in the regulation formula
            % ASM = ASM_0 × exp( ln( 0.005 / ASM_0 ) × ( n_start – n ) / ( n_start – n_end ) )
            % must be replaced by the value 0.5 in the MATLAB formula.
        end
    end


    function enabled = next_n_gears_are_higher( n, gears ) 
        enabled = true( size( gears ) );
        for i = 1 : length( gears )
            for k = 1 : n
                if i + k < length( gears )
                    if gears( i + k ) <= gears( i )
                        enabled( i ) = false;
                    end
                end
            end
        end
    end


end
