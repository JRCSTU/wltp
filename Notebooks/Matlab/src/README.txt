This is the MATLAB implementation of the algorithms described by the regulation document:

  WLTP-GS-TF-41 GTR 15 annex 1 and annex 2 08.07.2019_HS rev4_04092019.docx
  i.e. last version of following regulation modified by Heinz Steven
    ECE/TRANS/WP.29/GRPE/2019/2
    Proposal for Amendment 5 to global technical regulation No. 15
    (Worldwide harmonized Light vehicles Test Procedures (WLTP))
      Annex 1
        Worldwide light-duty test cycles (WLTC)
      Annex 2
        Gear selection and shift point determination
        for vehicles equipped with manual transmissions

and by the current reference implementation:

  Gearshift Calculation Tool (by Heinz Steven) 
    "Program version: 08.10.2019
     corresponds to GTR #15, draft for amendment 6,
     program code development subgroup version"
  downloaded from https://www.magentacloud.de/share/i7kq3sjws1

Two MATLAB functions were implemented
- scaleTrace() 
- calculateShiftpointsNdvFullPC()
each one residing in its own MATLAB .m file.

The function scaleTrace() implements the
trace scaling, speed capping and distance compensation
as described by Annex 1, chapter 8. (downscaling) and 
chapter 9 (speed capping and distance compensation).

The function calculateShiftpointsNdvFullPC() implements the 
determination of the gear to be selected and clutch state to be used
for every second of a given trace as described by Annex 2.

Heinz Steven provided a set a 125 test cases
to be used for verification of the implemented algorithms.
The additional MATLAB function calc_all_cases()
may be used to execute all this 125 test cases.

The input data for calc_all_cases() are stored in following CSV files:
- case.txt
- vehicle.txt
- engine.txt
- gearbox.txt
- phase.txt
- trace.txt
- scale.txt

The result data of calc_all_cases() will be stored in following CSV files:
- case_result.txt 
- engine_result.txt
- trace_interpolated.txt
- trace_scaled.txt
- phase_result.txt
- shift_power.txt
- shift.txt 
- shift_condensed.txt

Additionally, calc_all_cases() will also store the reformatted input data
in the following CSV files:
- case_formatted.txt
- vehicle_formatted.txt
- engine_formatted.txt
- gearbox_formatted.txt
- phase_formatted.txt
- trace_formatted.txt
- scale_formatted.txt
Here the column headers will be added (if necessary)
and column values will be aligned,
so that the formatted input data become better readable for humans.
 
Each of this files represents a data table
where each row can be selected by one or two key column values.

The data structure of the input files can be abbreviated like this:
- key columns are marked by "->"
- all column names are explained in the cross reference table
  parameter.xlsx (see below)

  case
  ->case   test case number
    veh    vehicle number
    ...

  vehicle
  ->veh    vehicle number
    class  WLTC cycle class
    ...

  engine
  ->veh     vehicle number
  ->n       engine speed 
    p       power
    ASM     additional safety margin
   
  gearbox
  ->veh     vehicle number
  ->g       gear number
    ndv     ratio engine speed to vehicle speed  

  trace
  ->class   WLTC cycle class
  ->t       time
    v       vehicle speed

  phase
  ->class   WLTC cycle class
  ->phase   phase number within class cycle
    length  length of phase 

  scale
  ->class   WLTC cycle class
    t_beg   time begin of trace scaling
    t_max   time maximum trace scaling
    t_end   time end of trace scaling
    ...

The data structure of the result files can be abbreviated like this:

  case_result
  ->case    test case number
    v_sum   vehicle speed checksum
    ...

  engine_result  
  ->case    test case number
  ->n       engine speed 
    p       power 
    ASM     ASM values calculated from legacy parameters

  trace_interpolated
  ->case    test case number
  ->t       time
    v       vehicle speed
 
  trace_scaled
  ->case    test case number
  ->t       time
    v       vehicle speed
    is_dsc  trace second was downscaled
    is_cap  trace second was capped 
    is_cmp  trace second is compensation 

  phase_result
  ->case         test case number
  ->phase        phase number within class cycle
    ...
    t_dist_comp  length of distance compensated phase

  shift
  ->case         test case number
  ->t            time
    ...
    g            gear number
    clutch       clutch disengaged   
    ...
    
  shift_condensed
  ->case            test case number
  ->t               time point of gear or clutch status change 
    gear_or_clutch  combined gear or clutch status value

Note that this MATLAB code also generates some data which may be ignore here.

The output table "trace_interpolated" contains the interpolated second-by-second trace data.
But as the input table "trace" in case of WLTC cycles already contains data for every second,
the interpolation does not generate any new information.
So the table "trace_interpolated" may be ignored here.

The output table "engine_result" contains the power curve data of the input table "engine"
but with ASM values computed from the legacy parameters asm_0, n_asm_start and n_asm_end
which were used in previous versions of the regulation.
So the table "engine_result" may be ignored here.

The output table "shift_condensed" contains combined gear or clutch status values,
where either another gear must be selected or the clutch must be disengaged.
So it contains only the timepoints where any such changes occurs.
This special condensed data format is only required for HORIBA internal handling.
So the table "shift_condensed" may be ignored here.
  
The MATLAB functions described here may be executed
either by the commercial software MATLAB from MathWorks
or by the free software GNU Octave from Free Software Foundation.
(GNU Octave may be downloaded by link: https://www.gnu.org/software/octave/)

I verified that the MATLAB functions work at least with following versions:
- MATLAB R2013b
- GNU Octave 5.1
but probably even older versions will do.

To execute all test cases simply load the all three MATLAB .m file
and all seven input .txt files into the same directory.
Open this directory as working directory in MATLAB or GNU Octave 
and run the calc_all_cases.m file.
All eight output .txt files will be written in the same directory. 

Because GNU Octave does not support the MATLAB table structures
the input and output tables are stored in MATLAB cell-arrays.
This increases the required execution time of the test code
but it is still fast enough to calculate all 125 test cases
in about 10 minutes by MATLAB and 20 minutes by GNU Octave.

But most of this execution time is consumed
by the reading and writing of the test data tables.
The execution times of the real calculation functions are reasonable small.
For MATLAB:
- scaleTrace()                      0.1 .. 0.2 seconds
- calculateShiftpointsNdvFullPC()   1.0 .. 2.0 seconds
For GNU Octave this times are about twice as long.   

Additionally, I created an Excel cross reference table parameter.xlsx
which shows the correlation between
- MATLAB test case input and output values i.e. table columns
- MATLAB function parameters 
- Gearshift Calculation Tool (by Heinz Steven) dialog parameters and table columns
- Regulation chapters and parameter descriptions

New test cases for already defined vehicles
may simply be added to the input table case.txt.
If such a new test case requires a new vehicle
then also the input tables vehicle.txt, engine.txt and gearbox.txt must be extended.
The input tables trace.txt, phase.txt and scale.txt must not be changed
as long as WLTC test cycles are used.


All files mentioned in this e-mail can be downloaded by the following links:
(The password is always the same: gearshift)

Description of the MATLAB Implementation (i.e. this document here)
- file: description.txt
- link: https://hcloud.horiba.de/index.php/s/9LMG8a0d59B2ajM

Regulation:
- file: WLTP-GS-TF-41 GTR 15 annex 1 and annex 2 08.07.2019_HS rev4_04092019.docx
- link: https://hcloud.horiba.de/index.php/s/S24zyQsn7HRV4tE

Gearshift Calculation Tool (by Heinz Steven):
- file: WLTP_GS_calculation_22102019_PCD-SG.accdb
- link: https://hcloud.horiba.de/index.php/s/MmOLoQtpEuH5hIo

Cross Reference of Calculation Parameters:
- file: parameter.xlsx
- link: https://hcloud.horiba.de/index.php/s/v2nc5Anhgvu9N4s

MATLAB Code with 125 Test Cases and Test Results
- file: calc_all_cases.zip
- link: https://hcloud.horiba.de/index.php/s/T6k0DBZRoxlVIKq

  this .zip file contains the following files:  
  - calc_all_cases.m
  - scaleTrace.m
  - calculateShiftpointsNdvFullPC.m
  - case.txt
  - vehicle.txt
  - engine.txt
  - gearbox.txt
  - phase.txt
  - trace.txt
  - scale.txt
  - case_result.txt 
  - engine_result.txt
  - trace_interpolated.txt
  - trace_scaled.txt
  - phase_result.txt
  - shift_power.txt
  - shift.txt 
  - shift_condensed.txt
