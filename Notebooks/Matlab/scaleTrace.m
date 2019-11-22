function [ ...
  RequiredToRatedPowerRatio ...
, CalculatedDownscalingPercentage ...
, RequiredToRatedPowerRatios ...
, CalculatedDownscalingPercentages ...
, TotalChecksum ...
, PhaseChecksums ...
, MaxVehicleSpeed ...
, TotalDistance ...
, DistanceCompensatedPhaseLengths ...
, OriginalTrace ...
, ApplicableTrace ...
] = scaleTrace ( ...
  ApplyDownscaling ...
, ApplySpeedCap ...
, ApplyDistanceCompensation ...
, UseCalculatedDownscalingPercentage ...
, DownscalingPercentage ...
, ScalingStartTimes ...
, ScalingCorrectionTimes ...
, ScalingEndTimes ...
, ScalingAlgorithms ...
, CappedSpeed ...
, PhaseLengths ...
, Trace ...
, VehicleClass ...
, RatedEnginePower ...
, VehicleTestMass ...
, f0 ...
, f1 ...
, f2 ...
)

% scaleTrace Scales down specified sections of a given trace by the given downscale factor.
%
% 1.  ApplyDownscaling is a logical scalar, specifying if the trace shall
%     be downscaled.
%
% 2.  ApplySpeedCap is a logical scalar, specifying if the trace shall be
%     capped to the given CappedSpeed.
%
% 3.  ApplyDistanceCompensation is a logical scalar, specifying it the 
%     trace shall be compensated for distance due to capped speeds.
%
% 4.  UseCalculatedDownscalingPercentage is a logical scalar, specifying
%     if the calculated downscaling value shall be used instead of the
%     the value given by the input parameter DownscalingPercentage.
%
% 5.  DownscalingPercentage is a double scalar, specifying the degree of
%     downscaling. This value will only be used if the input parameter
%     UseCalculatedDownscalingPercentage is false.
%
% 6.  ScalingStartTimes is a double column vector, containing the start
%     times of the segments to scale in seconds.
%
% 7.  ScalingCorrectionTimes is a double column vector, containing the
%     times to begin the scaling correction at in seconds. The size must 
%     correspond to the size of ScalingStartTimes. Each value must be 
%     between the corresponding start and end times.
% 
% 8.  ScalingEndTimes is a double column vector, containing the end times
%     of the segments to scale in seconds. The size must correspond to the 
%     size of ScalingStartTimes.
% 
% 9.  ScalingAlgorithms is a 2D character matrix, representing a list of 
%     strings, each denoting the algorithm to use for the specific segment.
%     The size must correspond to the size of ScalingStartTimes.
%     If 'Default' or empty, the WLTP algorithm is used.
%
% 10. CappedSpeed in km/h is the maximum speed of vehicles, which are  
%     technically able to follow the speed of the given trace but are not 
%     able to reach the maximum speed of that trace. If ApplySpeedCap is
%     true, the speed values of the given trace are limited to this value.
%
% 11. PhaseLengths is a double column vector, containing the lengths of the
%     phases in seconds. The sum of all lengths must equal the lenght of
%     the given trace.
% 
% 12. Trace is a two column cell array. The first column is a double column
%     vector, containing the trace times in seconds. The second column is a
%     double column vector, containing the vehicle-speed in km/h.
% 
% 13. VehicleClass is a 2D character matrix, reprensting a string with one 
%     of 'CLASS_1', 'CLASS_2', 'CLASS_3A' or 'CLASS_3B' determining the
%     coefficients used to calculate the downscaling factor.
% 
% 14. RatedEnginePower is a double scalar
% 
% 15. VehicleTestMass is a double scalar
% 
% 16. f0 in N is a double scalar, representing the constant road load 
%     coefficient, i.e. independent of velocity, caused by internal
%     frictional resistances.
% 
% 17. f1 in N/(km/h) is a double scalar, representing the linear road load 
%     coefficient, i.e. proportional to velocity, caused by tyres rolling
%     resistances.
% 
% 18. f2 in N/(km/h)^2 is a double scalar, representing the exponential
%     road load coefficient, i.e. quadratical to velocity, caused by 
%     aerodynamic resistances.
%
% Calculated results include:
%
% 1.  RequiredToRatedPowerRatio
%
% 2.  CalculatedDownscalingPercentage
%
% 3.  RequiredToRatedPowerRatios
%
% 4.  CalculatedDownscalingPercentages
%
% 5.  TotalChecksum
%
% 6.  PhaseChecksums 
%
% 7.  MaxVehicleSpeed in km/h of the applicable trace
%
% 8.  TotalDistance in m of the applicable trace
%
% 9.  DistanceCompensatedPhaseLengths in s
%
% 10. OriginalTrace is the original trace interpolated in 1Hz if needed
%
% 11. ApplicableTrace is the scaled, capped and compensated trace
%


%% Define vehicle classes
VEHICLE_CLASS_1 = 'CLASS_1';
VEHICLE_CLASS_2 = 'CLASS_2';
VEHICLE_CLASS_3A = 'CLASS_3A';
VEHICLE_CLASS_3B = 'CLASS_3B';


%% Preprocess inputs

% Check number of inputs and outputs
narginchk(18, 18);
nargoutchk(11, 11);

validateattributes(ApplyDownscaling, ...
	{'logical'}, ...
	{'scalar'}, ...
	mfilename, 'ApplyDownscaling', 1);

validateattributes(ApplySpeedCap, ...
	{'logical'}, ...
	{'scalar'}, ...
	mfilename, 'ApplySpeedCap', 2);

validateattributes(ApplyDistanceCompensation, ...
	{'logical'}, ...
	{'scalar'}, ...
	mfilename, 'ApplyDistanceCompensation', 3);

validateattributes(UseCalculatedDownscalingPercentage, ...
	{'logical'}, ...
	{'scalar'}, ...
	mfilename, 'UseCalculatedDownscalingPercentage', 4);

validateattributes(DownscalingPercentage, ...
	{'double'}, ...
	{'scalar', '>=', 0, '<=', 100}, ...
	mfilename, 'DownscalingPercentage', 5);

validateattributes(ScalingStartTimes, ...
	{'double'}, ...
	{'nonnegative'}, ...
	mfilename, 'ScalingStartTimes', 6);

validateattributes(ScalingCorrectionTimes, ...
	{'double'}, ...
	{'nonnegative', 'size', size(ScalingStartTimes)}, ...
	mfilename, 'ScalingCorrectionTimes', 7);

if ~all(ScalingStartTimes < ScalingCorrectionTimes) || ~all(ScalingCorrectionTimes < ScalingEndTimes)
	error('MATLAB:INVALID_INPUT:ScalingCorrectionTimes', 'ScalingCorrectionTimes must be between ScalingStartTimes and ScalingEndTimes'); 
end

validateattributes(ScalingEndTimes, ...
	{'double'}, ...
	{'nonnegative', 'size', size(ScalingStartTimes)},	...
	mfilename, 'ScalingEndTimes', 8);

validateattributes(ScalingAlgorithms, ...
	{'char'}, ...
	{'2d', 'nrows', length(ScalingStartTimes)}, ...
	mfilename, 'ScalingAlgorithms', 9);

scalingAlgorithms = cellstr(ScalingAlgorithms);
scalingAlgorithms(strcmp(scalingAlgorithms, ''),1) = {'Default'};

validateattributes(CappedSpeed, ...
	{'double'}, ...
	{'scalar'}, ...
	mfilename, 'CappedSpeed', 10);

validateattributes(PhaseLengths, ...
	{'double'}, ...
	{'nonnegative'},	...
	mfilename, 'PhaseLengths', 11);

validateattributes(Trace, ...
	{'cell'}, ...
	{'ncols', 2}, ...
	mfilename, 'Trace', 12);

[givenTraceTimes, givenVehicleSpeeds] = Trace{:};

validateattributes(givenTraceTimes, ...
	{'double'}, ...
	{'nonempty', 'column', 'increasing'}, ...
	mfilename, 'Trace.TraceTimes', 12);

validateattributes(givenVehicleSpeeds, ...
	{'double'},	...
	{'size', size(givenTraceTimes)}, ...
	mfilename, 'Trace.VehicleSpeeds', 12);

validateattributes(VehicleClass, ...
	{'char'}, ...
	{'2d'}, ...
	mfilename, 'VehicleClass', 13);

validateattributes(RatedEnginePower, ...
	{'double'}, ...
	{'scalar', 'positive'}, ...
	mfilename, 'RatedEnginePower', 14);

validateattributes(VehicleTestMass,	...
	{'double'}, ...
	{'scalar', 'positive'}, ...
	mfilename, 'VehicleTestMass', 15);

validateattributes(f0, ...
	{'double'}, ...
	{'scalar'}, ...
	mfilename, 'f0', 16);

validateattributes(f1, ...
	{'double'}, ...
	{'scalar'}, ...
	mfilename, 'f1', 17);

validateattributes(f2,	...
	{'double'}, ...
	{'scalar'}, ...
	mfilename, 'f2', 18);


%% Re-sample the trace in 1Hz
% If the trace was provided with higher sample rate, this may lead to data
% loss.

if givenTraceTimes(1) ~= 0
	error('MATLAB:INVALID_INPUT:Trace', 'Trace time must start at 0'); 
end

originalTraceTimes = (givenTraceTimes(1):1:ceil(givenTraceTimes(end)))';
originalVehicleSpeeds = interp1(givenTraceTimes, givenVehicleSpeeds, originalTraceTimes);
originalTraceTimesCount = length(originalTraceTimes);


%% Identify phases

phaseStarts = cumsum([1; PhaseLengths(1:end-1)]);
phaseEnds = cumsum(PhaseLengths);

if sum(PhaseLengths) ~= originalTraceTimes(end)
	error('MATLAB:INVALID_INPUT:PhaseLengths', 'Sum of phase lengths must equal the trace length');
end


%% Determine the downscaling factor for the entire trace (8.3)

accelerations = CalculateAccelerations(true(originalTraceTimesCount, 1));
requiredPowers = CalculateRequiredPowers(true(originalTraceTimesCount, 1));
requiredToRatedPowerRatio = CalculateRequiredToRatedPowerRatio(true(originalTraceTimesCount, 1));
calculatedDownscalingFactor = CalculateDownscalingFactor(true(originalTraceTimesCount, 1));
if UseCalculatedDownscalingPercentage
	downscalingFactor = calculatedDownscalingFactor;
else
	downscalingFactor = DownscalingPercentage/100;
end

%% Downscale the trace
% Downscaling applies to very low powered class 1 vehicles or vehicles with
% power to mass ratios close to class borderlines, thus causing
% driveability issues.

requiredToRatedPowerRatios = zeros(length(ScalingStartTimes), 1);
calculatedDownscalingFactors = zeros(length(ScalingStartTimes), 1);

downscaledVehicleSpeeds = originalVehicleSpeeds;

for segment = 1:length(ScalingStartTimes)
	if ApplyDownscaling	
		eval(strcat('Algorithm', scalingAlgorithms{segment}, '(ScalingStartTimes(segment), ScalingCorrectionTimes(segment), ScalingEndTimes(segment))'));
	end
	
	indexing = ScalingStartTimes(segment) <= originalTraceTimes & originalTraceTimes <= ScalingEndTimes(segment);
	
	requiredToRatedPowerRatios(segment) = CalculateRequiredToRatedPowerRatio(indexing);
	calculatedDownscalingFactors(segment) = CalculateDownscalingFactor(indexing);
end

downscaled = downscaledVehicleSpeeds ~= originalVehicleSpeeds;


%% Cap the trace (9)
% Speed cap applies to vehicles that are technically able to follow the
% given trace, but whose maximum speed is limited to a value lower than the
% maximum speed of that trace.

cappedVehicleSpeeds = downscaledVehicleSpeeds;

if ApplySpeedCap
	cappedVehicleSpeeds(cappedVehicleSpeeds > CappedSpeed) = CappedSpeed;
end

capped = cappedVehicleSpeeds ~= downscaledVehicleSpeeds;


%% Compensate the trace (9.2)
% A capped trace may need compensations to achieve the same distance as for 
% the original trace.

compensated = false(originalTraceTimesCount, 1);
compensatedTraceTimes = originalTraceTimes;
compensatedVehicleSpeeds = cappedVehicleSpeeds;

additionalSamples = zeros(length(PhaseLengths), 1);

if ApplyDistanceCompensation
	compensationStarts = zeros(length(PhaseLengths), 1);
	compensationEnds = zeros(length(PhaseLengths), 1);
	
	for phase = 1:length(PhaseLengths)
		phaseStart = phaseStarts(phase);
		phaseEnd = phaseEnds(phase);
		
		if phaseStart < phaseEnd
			cappedDistance = sum(cappedVehicleSpeeds(phaseStart:phaseEnd));
			downscaledDistance = sum(downscaledVehicleSpeeds(phaseStart:phaseEnd));
			
			if cappedDistance ~= downscaledDistance
				additionalSamples(phase) = round((downscaledDistance - cappedDistance) / CappedSpeed);
				compensationStarts(phase) = sum(additionalSamples(1:phase-1)) + phaseStart + find(capped(phaseStart:phaseEnd), 1, 'last');
				compensationEnds(phase) = compensationStarts(phase) + additionalSamples(phase);
			end
		end
	end
	
	compensated = zeros(originalTraceTimesCount + sum(additionalSamples), 1);
	compensated(compensationStarts(compensationStarts > 0)) = 1;
	compensated(compensationEnds(compensationEnds > 0)) = -1;
	compensated = logical(cumsum(compensated));

	compensatedTraceTimes = (originalTraceTimes(1):1:ceil(length(compensated) - 1))';
	compensatedVehicleSpeeds = zeros(length(compensated), 1);
	compensatedVehicleSpeeds(compensated) = CappedSpeed;
	compensatedVehicleSpeeds(~compensated) = cappedVehicleSpeeds;	
	
	downscaled = logical(false(length(compensated), 1));
	downscaled(~compensated) = downscaledVehicleSpeeds ~= originalVehicleSpeeds;

	capped = logical(false(length(compensated), 1));
	capped(~compensated) = cappedVehicleSpeeds ~= downscaledVehicleSpeeds;
end


%% Assign outputs

RequiredToRatedPowerRatio = requiredToRatedPowerRatio;

calculatedDownscalingFactor(calculatedDownscalingFactor <= 0.01) = 0;
calculatedDownscalingFactor = round(calculatedDownscalingFactor*1000)/1000;
CalculatedDownscalingPercentage = calculatedDownscalingFactor * 100;

RequiredToRatedPowerRatios = requiredToRatedPowerRatios;

calculatedDownscalingFactors(calculatedDownscalingFactors <= 0.01) = 0;
calculatedDownscalingFactors = round(calculatedDownscalingFactors*1000)/1000;
CalculatedDownscalingPercentages = calculatedDownscalingFactors * 100;

TotalChecksum = round(sum(originalVehicleSpeeds)*10)/10;

PhaseChecksums = zeros(length(PhaseLengths), 1);
for phase = 1:length(PhaseLengths)
	PhaseChecksums(phase) = round(sum(originalVehicleSpeeds(phaseStarts(phase):phaseEnds(phase)))*10)/10;
end

MaxVehicleSpeed = max(compensatedVehicleSpeeds);

TotalDistance = round(sum(compensatedVehicleSpeeds / 3.6)*10)/10;

DistanceCompensatedPhaseLengths = PhaseLengths + additionalSamples;

OriginalTrace = {originalTraceTimes, originalVehicleSpeeds};

ApplicableTrace = {compensatedTraceTimes, compensatedVehicleSpeeds, downscaled, capped, compensated};


	%% Calculate accelerations
	
	function accelerations = CalculateAccelerations(indexing)
		accelerations = [diff(originalVehicleSpeeds(indexing)) ./ (3.6 * diff(originalTraceTimes(indexing))); 0];
	end


	%% Calculate required powers
	
	function requiredPowers = CalculateRequiredPowers(indexing)
		requiredPowers = (f0 * originalVehicleSpeeds(indexing) + f1 * (originalVehicleSpeeds(indexing).^2) + f2 * (originalVehicleSpeeds(indexing).^3) + 1.03 * accelerations(indexing) .* originalVehicleSpeeds(indexing) * VehicleTestMass) / 3600;
	end


	%% Calculate required to rated power ratio
	
	function requiredToRatedPowerRatio = CalculateRequiredToRatedPowerRatio(indexing)
		requiredToRatedPowerRatio = max(requiredPowers(indexing))/RatedEnginePower;
	end


	%% Calculate downscaling factor
	
	function calculatedDownscalingFactor = CalculateDownscalingFactor(indexing)
		switch VehicleClass
			case VEHICLE_CLASS_1
				r0 = 0.978;
				a1 = 0.680;
				b1 = -0.665;
			case VEHICLE_CLASS_2
				r0 = 0.866;
				a1 = 0.606;
				b1 = -0.525;
			case VEHICLE_CLASS_3A
				r0 = 0.867;
				a1 = 0.588;
				b1 = -0.510;		
			case VEHICLE_CLASS_3B
				r0 = 0.867;
				a1 = 0.588;
				b1 = -0.510;			
			otherwise				
				calculatedDownscalingFactor = 0;
				
				return
		end

		localRequiredToRatedPowerRatio = CalculateRequiredToRatedPowerRatio(indexing);
		
		if localRequiredToRatedPowerRatio >= r0
			calculatedDownscalingFactor = a1 * localRequiredToRatedPowerRatio + b1;
		else
			calculatedDownscalingFactor = 0;
		end
	end


	%% Algorithm WLTP
	
	function AlgorithmWLTP(scalingStart, correctionStart, scalingEnd)
		
		scalingStartIndex = find(originalTraceTimes >= scalingStart, 1, 'first');
		correctionStartIndex = find(originalTraceTimes >= correctionStart, 1, 'first');
		scalingEndIndex = find(originalTraceTimes >= scalingEnd, 1, 'first');
		
		for i = scalingStartIndex:correctionStartIndex-1;
			downscaledVehicleSpeeds(i+1) = downscaledVehicleSpeeds(i) + accelerations(i)*(1 - downscalingFactor)*3.6;
		end
		
		if scalingEndIndex < originalTraceTimesCount
			subsequentVehicleSpeed = originalVehicleSpeeds(scalingEndIndex + 1);
		else
			subsequentVehicleSpeed = originalVehicleSpeeds(end);
		end
				
		if (originalVehicleSpeeds(correctionStartIndex) - subsequentVehicleSpeed == 0)
			% This would result in division by zero.
			% The correction factor is explicitly set to 0.
			correctionFactor = 0;
		else
			correctionFactor = (downscaledVehicleSpeeds(correctionStartIndex) - subsequentVehicleSpeed)/(originalVehicleSpeeds(correctionStartIndex) - subsequentVehicleSpeed);
		end
		
		for i = correctionStartIndex+1:scalingEndIndex;
			downscaledVehicleSpeeds(i) = downscaledVehicleSpeeds(i-1) + accelerations(i-1)*correctionFactor*3.6;
        end
        
        % ECE/TRANS/WP.29/GRPE/2019/2
        % The modified vehicle speed values ... shall be rounded
        % according to paragraph 7. of this UN GTR to 1 place of decimal
        downscaledVehicleSpeeds = round( downscaledVehicleSpeeds * 10 ) / 10;
        
	end


	%% Default algorithm
	
	function AlgorithmDefault(scalingStart, correctionStart, scalingEnd) %#ok<DEFNU>
		AlgorithmWLTP(scalingStart, correctionStart, scalingEnd);
	end

	
end
