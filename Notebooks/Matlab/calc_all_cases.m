function calc_all_cases

  %-----------------------------------------------------------------------------
  fprintf( 'read input files : \n' );

  fprintf( '- case.txt\n'    );
  tab_case    = read_tab( 'case.txt'    );
  fprintf( '- vehicle.txt\n' );
  tab_vehicle = read_tab( 'vehicle.txt' );
  fprintf( '- engine.txt\n'  );
  tab_engine  = read_tab( 'engine.txt'  );
  fprintf( '- gearbox.txt\n' );
  tab_gearbox = read_tab( 'gearbox.txt' );
  fprintf( '- phase.txt\n'   );
  tab_phase   = read_tab( 'phase.txt'   );
  fprintf( '- trace.txt\n'   );
  tab_trace   = read_tab( 'trace.txt'   );
  fprintf( '- scale.txt\n'   );
  tab_scale   = read_tab( 'scale.txt'   );

  % size_c = size( tab_case, 1 );
  % size_n = size( tab_engine, 1 );
  % size_g = size( tab_gearbox, 1 );
  % size_t = size( tab_trace, 1 );

  % init output tables
  % tab_case_result        = { size_c, 20 };
  % tab_engine_result      = { size_c * size_n, 3  };
  % tab_trace_interpolated = { size_c * size_t, 3  };
  % tab_trace_scaled       = { size_c * size_t, 6  };
  % tab_phase_result       = { size_c * 4, 4 };
  % tab_shift_power        = { size_c * size_t * size_g, 5 };
  % tab_shift              = { size_c * size_t, 9 };
  % tab_shift_condensed    = { size_c * size_t, 3 };

  % column numbers for input table 'case'
  col_case_case                =  1;
  col_case_vehicle             =  2;
  col_case_do_down_scale       =  3;
  col_case_do_speed_cap        =  4;
  col_case_do_dist_comp        =  5;
  col_case_use_f_dsc_calc      =  6;
  col_case_f_dsc               =  7;
  col_case_v_cap               =  8;
  col_case_class               =  9;
  col_case_n_min_1             = 10;
  col_case_n_min_1_to_2        = 11;
  col_case_n_min_2_decel       = 12;
  col_case_n_min_2             = 13;
  col_case_n_min_3             = 14;
  col_case_n_min_3_accel       = 15;
  col_case_n_min_3_decel       = 16;
  col_case_n_min_3_accel_start = 17;
  col_case_n_min_3_decel_start = 18;
  col_case_t_start_phase       = 19;
  col_case_suppress_0          = 20;
  col_case_exclude_1           = 21;
  col_case_clutch_automatic    = 22;
  col_case_n_lim               = 23;
  col_case_asm_0               = 24;
  col_case_n_asm_start         = 25;
  col_case_n_asm_end           = 26;
  col_case_clutch_merged       = 27;

  % column numbers for input table 'vehicle'
  col_vehicle_vehicle  = 1;
  col_vehicle_class    = 2;
  col_vehicle_f_dsc    = 3;
  col_vehicle_p_rated  = 4;
  col_vehicle_n_rated  = 5;
  col_vehicle_n_idle   = 6;
  col_vehicle_n_max1   = 7;
  col_vehicle_nbr_of_g = 8;
  col_vehicle_m_test   = 9;
  col_vehicle_m_ro     = 10;
  col_vehicle_n_lim    = 11;
  col_vehicle_f0       = 12;
  col_vehicle_f1       = 13;
  col_vehicle_f2       = 14;
  col_vehicle_SM       = 15;

  % column numbers for input table 'engine'
  col_engine_vehicle   = 1;
  col_engine_n         = 2;
  col_engine_p         = 3;
  col_engine_ASM       = 4;

  % column numbers for input table 'gearbox'
  col_gearbox_vehicle  = 1;
  col_gearbox_g        = 2;
  col_gearbox_ndv      = 3;

  % column numbers for input table 'trace'
  col_trace_class      = 1;
  col_trace_t          = 2;
  col_trace_v          = 3;

  % column numbers for input table 'phase'
  col_phase_class      = 1;
  col_phase_phase      = 2;
  col_phase_length     = 3;

  % column numbers for input table 'scale'
  col_scale_class       = 1;
  col_scale_algorithm   = 2;
  col_scale_t_start_dsc = 3;
  col_scale_t_max_dsc   = 4;
  col_scale_t_end_dsc   = 5;
  col_scale_r0          = 6;
  col_scale_a1          = 7;
  col_scale_b1          = 8;

  % column numbers for output table 'case_result'
  col_case_result_case                = 1;
  col_case_result_r_max               = 2;
  col_case_result_f_dsc               = 3;
  col_case_result_v_checksum          = 4;
  col_case_result_v_max               = 5;
  col_case_result_d_cycle             = 6;
  col_case_result_g_average           = 7;
  col_case_result_v_x_g_checksum      = 8;
  col_case_result_n_max1              = 9;
  col_case_result_n_max2              = 10;
  col_case_result_n_max3              = 11;
  col_case_result_n_max               = 12;
  col_case_result_v_max_cycle         = 13;
  col_case_result_v_max_vehicle       = 14;
  col_case_result_g_v_max_vehicle     = 15;
  col_case_result_n_min_drive_1       = 16;
  col_case_result_n_min_drive_1_to_2  = 17;
  col_case_result_n_min_drive_2_decel = 18;
  col_case_result_n_min_drive_2       = 19;
  col_case_result_n_min_drive_3       = 20;

  % column numbers for output table 'engine_result'
  col_engine_result_case              = 1;
  col_engine_result_n                 = 2;
  col_engine_result_p                 = 3;
  col_engine_result_ASM               = 4;

  % column numbers for output table 'trace_interpolated'
  col_trace_interpolated_case         = 1;
  col_trace_interpolated_t            = 2;
  col_trace_interpolated_v            = 3;

  % column numbers for output table 'trace_scaled'
  col_trace_scaled_case               = 1;
  col_trace_scaled_t                  = 2;
  col_trace_scaled_v                  = 3;
  col_trace_scaled_downscaled         = 4;
  col_trace_scaled_capped             = 5;
  col_trace_scaled_compensated        = 6;

  % column numbers for output table 'phase_result'
  col_phase_result_case               = 1;
  col_phase_result_phase              = 2;
  col_phase_result_v_checksum         = 3;
  col_phase_result_t_dist_comp        = 4;

  % column numbers for output table 'shift_power'
  col_shift_power_case                = 1;
  col_shift_power_t                   = 2;
  col_shift_power_g                   = 3;
  col_shift_power_n                   = 4;
  col_shift_power_p                   = 5;

  % column numbers for output table 'shift'
  col_shift_case                      = 1;
  col_shift_t                         = 2;
  col_shift_v                         = 3;
  col_shift_p                         = 4;
  col_shift_g                         = 5;
  col_shift_clutch_disengaged         = 6;
  col_shift_clutch_undefined          = 7;
  col_shift_clutch_HST                = 8;
  col_shift_g_corrections             = 9;

  % column numbers for output table 'shift_condensed'
  col_shift_condensed_case            = 1;
  col_shift_condensed_t               = 2;
  col_shift_condensed_gear_or_clutch  = 3;

  %-----------------------------------------------------------------------------
  fprintf( 'write formatted input files :\n' );

  fprintf( '- case_formatted.txt\n' );
  fileID = fopen( 'case_formatted.txt', 'w' );
  fprintf( fileID, '%4s'  , 'case' );
  fprintf( fileID, ', %4s', 'veh' );
  fprintf( fileID, ', %6s', 'do_dsc' );
  fprintf( fileID, ', %6s', 'do_cap' );
  fprintf( fileID, ', %6s', 'do_cmp' );
  fprintf( fileID, ', %8s', 'calc_dsc' );
  fprintf( fileID, ', %5s', 'f_dsc' );
  fprintf( fileID, ', %5s', 'v_cap' );
  fprintf( fileID, ', %8s', 'class' );
  fprintf( fileID, ', %7s', 'n_min1' );
  fprintf( fileID, ', %7s', 'n_min12' );
  fprintf( fileID, ', %7s', 'n_min2d' );
  fprintf( fileID, ', %7s', 'n_min2' );
  fprintf( fileID, ', %7s', 'n_min3' );
  fprintf( fileID, ', %7s', 'n_min3a' );
  fprintf( fileID, ', %7s', 'n_min3d' );
  fprintf( fileID, ', %8s', 'n_min3as' );
  fprintf( fileID, ', %8s', 'n_min3ds' );
  fprintf( fileID, ', %3s', 't_start' );
  fprintf( fileID, ', %5s', 'supp0' );
  fprintf( fileID, ', %5s', 'excl1' );
  fprintf( fileID, ', %3s', 'autom' );
  fprintf( fileID, ', %7s', 'n_lim' );
  fprintf( fileID, ', %5s', 'asm_0' );
  fprintf( fileID, ', %7s', 'n_asm_s' );
  fprintf( fileID, ', %7s', 'n_asm_e' );
  fprintf( fileID, ', %3s', 'merge' );
  fprintf( fileID, '\n' );
  for k = 1 : size( tab_case, 1 )
    fprintf( fileID, '%4d'    , tab_case{ k, col_case_case } );
    fprintf( fileID, ', %4d'  , tab_case{ k, col_case_vehicle } );
    fprintf( fileID, ', %6d'  , tab_case{ k, col_case_do_down_scale } );
    fprintf( fileID, ', %6d'  , tab_case{ k, col_case_do_speed_cap } );
    fprintf( fileID, ', %6d'  , tab_case{ k, col_case_do_dist_comp } );
    fprintf( fileID, ', %8d'  , tab_case{ k, col_case_use_f_dsc_calc } );
    fprintf( fileID, ', %5.3f', tab_case{ k, col_case_f_dsc } );
    fprintf( fileID, ', %5.1f', tab_case{ k, col_case_v_cap } );
    fprintf( fileID, ', %8s'  , tab_case{ k, col_case_class } );
    fprintf( fileID, ', %7.2f', tab_case{ k, col_case_n_min_1 } );
    fprintf( fileID, ', %7.2f', tab_case{ k, col_case_n_min_1_to_2 } );
    fprintf( fileID, ', %7.2f', tab_case{ k, col_case_n_min_2_decel } );
    fprintf( fileID, ', %7.2f', tab_case{ k, col_case_n_min_2 } );
    fprintf( fileID, ', %7.2f', tab_case{ k, col_case_n_min_3 } );
    fprintf( fileID, ', %7.2f', tab_case{ k, col_case_n_min_3_accel } );
    fprintf( fileID, ', %7.2f', tab_case{ k, col_case_n_min_3_decel } );
    fprintf( fileID, ', %8.2f', tab_case{ k, col_case_n_min_3_accel_start } );
    fprintf( fileID, ', %8.2f', tab_case{ k, col_case_n_min_3_decel_start } );
    fprintf( fileID, ', %7d'  , tab_case{ k, col_case_t_start_phase } );
    fprintf( fileID, ', %5d'  , tab_case{ k, col_case_suppress_0 } );
    fprintf( fileID, ', %5d'  , tab_case{ k, col_case_exclude_1 } );
    fprintf( fileID, ', %5d'  , tab_case{ k, col_case_clutch_automatic } );
    fprintf( fileID, ', %7.2f', tab_case{ k, col_case_n_lim } );
    fprintf( fileID, ', %5.3f', tab_case{ k, col_case_asm_0 } );
    fprintf( fileID, ', %7.2f', tab_case{ k, col_case_n_asm_start } );
    fprintf( fileID, ', %7.2f', tab_case{ k, col_case_n_asm_end } );
    fprintf( fileID, ', %5d'  , tab_case{ k, col_case_clutch_merged } );
    fprintf( fileID, '\n' );
  end
  fclose( fileID );

  fprintf( '- vehicle_formatted.txt\n' );
  fileID = fopen( 'vehicle_formatted.txt', 'w' );
  fprintf( fileID, '%4s'  , 'veh' );
  fprintf( fileID, ', %8s', 'class' );
  fprintf( fileID, ', %5s', 'f_dsc' );
  fprintf( fileID, ', %7s', 'p_rated' );
  fprintf( fileID, ', %7s', 'n_rated' );
  fprintf( fileID, ', %7s', 'n_idle' );
  fprintf( fileID, ', %7s', 'n_max1' );
  fprintf( fileID, ', %2s', '#g' );
  fprintf( fileID, ', %6s', 'm_test' );
  fprintf( fileID, ', %6s', 'm_ro' );
  fprintf( fileID, ', %7s', 'n_lim' );
  fprintf( fileID, ', %7s', 'f0' );
  fprintf( fileID, ', %7s', 'f1' );
  fprintf( fileID, ', %7s', 'f2' );
  fprintf( fileID, ', %5s', 'SM' );
  fprintf( fileID, '\n' );
  for k = 1 : size( tab_vehicle, 1 )
    fprintf( fileID, '%4d'    , tab_vehicle{ k, col_vehicle_vehicle } );
    fprintf( fileID, ', %8s'  , tab_vehicle{ k, col_vehicle_class } );
    fprintf( fileID, ', %5.3f', tab_vehicle{ k, col_vehicle_f_dsc } );
    fprintf( fileID, ', %7.1f', tab_vehicle{ k, col_vehicle_p_rated } );
    fprintf( fileID, ', %7.2f', tab_vehicle{ k, col_vehicle_n_rated } );
    fprintf( fileID, ', %7.2f', tab_vehicle{ k, col_vehicle_n_idle } );
    fprintf( fileID, ', %7.2f', tab_vehicle{ k, col_vehicle_n_max1 } );
    fprintf( fileID, ', %2d'  , tab_vehicle{ k, col_vehicle_nbr_of_g } );
    fprintf( fileID, ', %6.1f', tab_vehicle{ k, col_vehicle_m_test } );
    fprintf( fileID, ', %6.1f', tab_vehicle{ k, col_vehicle_m_ro } );
    fprintf( fileID, ', %7.2f', tab_vehicle{ k, col_vehicle_n_lim } );
    fprintf( fileID, ', %7.2f', tab_vehicle{ k, col_vehicle_f0 } );
    fprintf( fileID, ', %7.5f', tab_vehicle{ k, col_vehicle_f1 } );
    fprintf( fileID, ', %7.5f', tab_vehicle{ k, col_vehicle_f2 } );
    fprintf( fileID, ', %5.3f', tab_vehicle{ k, col_vehicle_SM } );
    fprintf( fileID, '\n' );
  end
  fclose( fileID );

  fprintf( '- engine_formatted.txt\n' );
  fileID = fopen( 'engine_formatted.txt', 'w' );
  fprintf( fileID, '%4s'  , 'veh' );
  fprintf( fileID, ', %7s', 'n' );
  fprintf( fileID, ', %7s', 'p' );
  fprintf( fileID, ', %5s', 'ASM' );
  fprintf( fileID, '\n' );
  for k = 1 : size( tab_engine, 1 )
    fprintf( fileID, '%4d'    , tab_engine{ k, col_engine_vehicle } );
    fprintf( fileID, ', %7.2f', tab_engine{ k, col_engine_n } );
    fprintf( fileID, ', %7.3f', tab_engine{ k, col_engine_p } );
    fprintf( fileID, ', %5.3f', tab_engine{ k, col_engine_ASM } );
    fprintf( fileID, '\n' );
  end
  fclose( fileID );

  fprintf( '- gearbox_formatted.txt\n' );
  fileID = fopen( 'gearbox_formatted.txt', 'w' );
  fprintf( fileID, '%4s'  , 'veh' );
  fprintf( fileID, ', %2s', 'g' );
  fprintf( fileID, ', %7s', 'ndv' );
  fprintf( fileID, '\n' );
  for k = 1 : size( tab_gearbox, 1 )
    fprintf( fileID, '%4d'    , tab_gearbox{ k, col_gearbox_vehicle } );
    fprintf( fileID, ', %2d'  , tab_gearbox{ k, col_gearbox_g } );
    fprintf( fileID, ', %7.3f', tab_gearbox{ k, col_gearbox_ndv } );
    fprintf( fileID, '\n' );
  end
  fclose( fileID );

  fprintf( '- trace_formatted.txt\n' );
  fileID = fopen( 'trace_formatted.txt', 'w' );
  fprintf( fileID, '%8s'  , 'class' );
  fprintf( fileID, ', %4s', 't' );
  fprintf( fileID, ', %5s', 'v' );
  fprintf( fileID, '\n' );
  for k = 1 : size( tab_trace, 1 )
    fprintf( fileID, '%8s'    , tab_trace{ k, col_trace_class } );
    fprintf( fileID, ', %4d'  , tab_trace{ k, col_trace_t } );
    fprintf( fileID, ', %5.1f', tab_trace{ k, col_trace_v } );
    fprintf( fileID, '\n' );
  end
  fclose( fileID );

  fprintf( '- phase_formatted.txt\n' );
  fileID = fopen( 'phase_formatted.txt', 'w' );
  fprintf( fileID, '%8s'  , 'class' );
  fprintf( fileID, ', %5s', 'phase' );
  fprintf( fileID, ', %6s', 'length' );
  fprintf( fileID, '\n' );
  for k = 1 : size( tab_phase, 1 )
    fprintf( fileID, '%8s'  , tab_phase{ k, col_phase_class } );
    fprintf( fileID, ', %5d', tab_phase{ k, col_phase_phase } );
    fprintf( fileID, ', %6d', tab_phase{ k, col_phase_length } );
    fprintf( fileID, '\n' );
  end
  fclose( fileID );

  fprintf( '- scale_formatted.txt\n' );
  fileID = fopen( 'scale_formatted.txt', 'w' );
  fprintf( fileID, '%8s'  , 'class' );
  fprintf( fileID, ', %4s', 'algo' );
  fprintf( fileID, ', %5s', 't_beg' );
  fprintf( fileID, ', %5s', 't_max' );
  fprintf( fileID, ', %5s', 't_end' );
  fprintf( fileID, ', %6s', 'r0' );
  fprintf( fileID, ', %6s', 'a1' );
  fprintf( fileID, ', %6s', 'b1' );
  fprintf( fileID, '\n' );
  for k = 1 : size( tab_scale, 1 )
    fprintf( fileID, '%8s'    , tab_scale{ k, col_scale_class } );
    fprintf( fileID, ', %4s'  , tab_scale{ k, col_scale_algorithm } );
    fprintf( fileID, ', %5d'  , tab_scale{ k, col_scale_t_start_dsc } );
    fprintf( fileID, ', %5d'  , tab_scale{ k, col_scale_t_max_dsc } );
    fprintf( fileID, ', %5d'  , tab_scale{ k, col_scale_t_end_dsc } );
    fprintf( fileID, ', %6.3f', tab_scale{ k, col_scale_r0 } );
    fprintf( fileID, ', %6.3f', tab_scale{ k, col_scale_a1 } );
    fprintf( fileID, ', %6.3f', tab_scale{ k, col_scale_b1 } );
    fprintf( fileID, '\n' );
  end
  fclose( fileID );

  %-----------------------------------------------------------------------------
  % calculate trace scaling and gear shifting for all vehicles
  for i = 1 : size( tab_case, 1 )

    fprintf( 'handle case %d\n', i );
    
    % init output tables
    tab_case_result        = { };
    tab_engine_result      = { };
    tab_trace_interpolated = { };
    tab_trace_scaled       = { };
    tab_phase_result       = { };
    tab_shift_power        = { };
    tab_shift              = { };
    tab_shift_condensed    = { };

    row_case = tab_case( i, : );
    v = row_case{ col_case_vehicle };
    row_vehicle  = get_tab_row( tab_vehicle, col_vehicle_vehicle, v );
    rows_engine  = get_tab_row( tab_engine , col_engine_vehicle , v );
    rows_gearbox = get_tab_row( tab_gearbox, col_gearbox_vehicle, v );
    cc = row_case{ col_case_class };
    cv = row_vehicle{ col_vehicle_class };
    rows_phase   = get_tab_row( tab_phase  , col_phase_class, cc );
    row_scale    = get_tab_row( tab_scale  , col_scale_class, cv );
    rows_trace   = get_tab_row( tab_trace  , col_trace_class, cc );

    ApplyDownscaling = logical( ...
      row_case{ col_case_do_down_scale } ...
    );
    ApplySpeedCap = logical( ...
      row_case{ col_case_do_speed_cap } ...
    );
    ApplyDistanceCompensation = logical( ...
      row_case{ col_case_do_dist_comp } ...
    );
    UseCalculatedDownscalingPercentage = logical( ...
      row_case{ col_case_use_f_dsc_calc } ...
    );
    DownscalingPercentage = ...
      100 * row_case{ col_case_f_dsc };
      % case.f_dsc contains fraction value 0.0 .. 1.0
      % DownscalingPercentage expects percentage value 0.0 .. 100.0
    if DownscalingPercentage <= 1
      % downscaling shall only be applied if it exeeds 1 percent
      ApplyDownscaling = false;
    end
    ScalingStartTimes = ...
      row_scale{ col_scale_t_start_dsc };
    ScalingCorrectionTimes = ...
      row_scale{ col_scale_t_max_dsc };
    ScalingEndTimes = ...
      row_scale{ col_scale_t_end_dsc };
    ScalingAlgorithms = ...
      [ row_scale{ col_scale_algorithm } ];
    CappedSpeed = ...
      row_case{ col_case_v_cap };
    PhaseLengths = cell2mat( ...
      rows_phase( :, col_phase_length ) ...
    );
    Trace = { ...
      cell2mat( rows_trace( :, col_trace_t ) ) ...
    , cell2mat( rows_trace( :, col_trace_v ) ) ...
    };
    VehicleClass = ...
      row_case{ col_case_class };
    RatedEnginePower = ...
      row_vehicle{ col_vehicle_p_rated };
    VehicleTestMass = ...
      row_vehicle{ col_vehicle_m_test };
    f0 = ...
      row_vehicle{ col_vehicle_f0 };
    f1 = ...
      row_vehicle{ col_vehicle_f1 };
    f2 = ...
      row_vehicle{ col_vehicle_f2 };
    
    %---------------------------------------------------------------------------
    fprintf( '- scale trace\n' );

    [ RequiredToRatedPowerRatio ...
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
    );

    s = size( tab_case_result, 1 );
    tab_case_result( s + 1, col_case_result_case ) = ...
      { i };
    tab_case_result( s + 1, col_case_result_r_max ) = ...
      { RequiredToRatedPowerRatio };
    tab_case_result( s + 1, col_case_result_f_dsc ) = ...
      { CalculatedDownscalingPercentage };
    tab_case_result( s + 1, col_case_result_v_checksum ) = ...
      { TotalChecksum };
    tab_case_result( s + 1, col_case_result_v_max ) = ...
      { MaxVehicleSpeed };
    tab_case_result( s + 1, col_case_result_d_cycle ) = ...
      { TotalDistance };

    s = size( tab_phase_result, 1 );
    for p = 1 : size( PhaseChecksums, 1 )
      tab_phase_result( s + p, col_phase_result_case ) = ...
        { i };
      tab_phase_result( s + p, col_phase_result_phase ) = ...
        { p };
      tab_phase_result( s + p, col_phase_result_v_checksum ) = ...
        { PhaseChecksums( p ) };
      tab_phase_result( s + p, col_phase_result_t_dist_comp ) = ...
        { DistanceCompensatedPhaseLengths( p ) };
    end

    s = size( tab_trace_interpolated, 1 );
    for p = 1 : size( OriginalTrace{ 1 } )
      tab_trace_interpolated( s + p, col_trace_interpolated_case ) = ...
        { i };
      tab_trace_interpolated( s + p, col_trace_interpolated_t ) = ...
        { OriginalTrace{ 1 }( p ) };
      tab_trace_interpolated( s + p, col_trace_interpolated_v ) = ...
        { OriginalTrace{ 2 }( p ) };
    end
    
    s = size( tab_trace_scaled, 1 );
    for p = 1 : size( ApplicableTrace{ 1 } )
      tab_trace_scaled( s + p, col_trace_scaled_case ) = ...
        { i };
      tab_trace_scaled( s + p, col_trace_scaled_t ) = ...
        { ApplicableTrace{ 1 }( p ) };
      tab_trace_scaled( s + p, col_trace_scaled_v ) = ...
        { ApplicableTrace{ 2 }( p ) };
      tab_trace_scaled( s + p, col_trace_scaled_downscaled ) = ...
        { ApplicableTrace{ 3 }( p ) };
      tab_trace_scaled( s + p, col_trace_scaled_capped ) = ...
        { ApplicableTrace{ 4 }( p ) };
      tab_trace_scaled( s + p, col_trace_scaled_compensated ) = ...
        { ApplicableTrace{ 5 }( p ) };
    end
    
    % RatedEnginePower
      % already set above
    RatedEngineSpeed = ...
      row_vehicle{ col_vehicle_n_rated };
    IdlingEngineSpeed = ...
      row_vehicle{ col_vehicle_n_idle };
    Max95EngineSpeed = ...
      row_vehicle{ col_vehicle_n_max1 };
    NoOfGears = int32( ...
      row_vehicle{ col_vehicle_nbr_of_g } ...
    );
    % VehicleTestMass
      % already set above
    % f0
      % already set above
    % f1
      % already set above
    % f2
      % already set above
    gear_nbrs = cell2mat( rows_gearbox( :, col_gearbox_g ) );
    gear_chars = [ '  ' ];
    for g = 1 : size( gear_nbrs )
      gear_chars( g, : ) = sprintf( '%2d', gear_nbrs( g ) );
    end
    Ndv = ...
      { gear_chars ...
      , cell2mat( rows_gearbox( :, col_gearbox_ndv ) ) ...
      };
    FullPowerCurve = ...
      { cell2mat( rows_engine( :, col_engine_n ) ) ...
      , cell2mat( rows_engine( :, col_engine_p ) ) ...
      , 100 * cell2mat( rows_engine( :, col_engine_ASM ) ) ...
      };
      % engine.ASM contains fraction values 0.0 .. 1.0
      % FullPowerCurve.ASM expects percentage values 0.0 .. 100.0
    Trace = ...
      [ ApplicableTrace( :, 1 ) ...
      , ApplicableTrace( :, 2 ) ...
      ];
    SafetyMargin = ...
      100 * row_vehicle{ col_vehicle_SM };
      % vehicle.SM contains fraction value 0.0 .. 1.0
      % SafetyMargin expects a percentage value 0.0 .. 100.0
    AdditionalSafetyMargin0 = ...
      row_case{ col_case_asm_0 };  % legacy parameter
    StartEngineSpeed = ...
      row_case{ col_case_n_asm_start };  % legacy parameter
    EndEngineSpeed = ...
      row_case{ col_case_n_asm_end };  % legacy parameter
    MinDriveEngineSpeed1st = ...
      row_case{ col_case_n_min_1 };
    MinDriveEngineSpeed1stTo2nd = ...
      row_case{ col_case_n_min_1_to_2 };
    MinDriveEngineSpeed2ndDecel = ...
      row_case{ col_case_n_min_2_decel };
    MinDriveEngineSpeed2nd = ...
      row_case{ col_case_n_min_2 };
    MinDriveEngineSpeedGreater2nd = ...
      row_case{ col_case_n_min_3 };
    EngineSpeedLimitVMax = ...
      row_case{ col_case_n_lim };
    MaxTorque = ...
      0;  % legacy parameter
    ExcludeCrawlerGear = logical( ...
      row_case{ col_case_exclude_1 } ...
    );
    AutomaticClutchOperation = logical( ...
      row_case{ col_case_clutch_automatic } ...
    );
    SuppressGear0DuringDownshifts = logical( ...
      row_case{ col_case_suppress_0 } ...
    );
    MinDriveEngineSpeedGreater2ndAccel = ...
      row_case{ col_case_n_min_3_accel };
    MinDriveEngineSpeedGreater2ndDecel = ...
      row_case{ col_case_n_min_3_decel };
    MinDriveEngineSpeedGreater2ndAccelStartPhase = ...
      row_case{ col_case_n_min_3_accel_start };
    MinDriveEngineSpeedGreater2ndDecelStartPhase = ...
      row_case{ col_case_n_min_3_decel_start };
    TimeEndOfStartPhase = int32( ...
      row_case{ col_case_t_start_phase } ...
    );
    DoNotMergeClutchIntoGearsOutput = logical( ...
      1 ...  % test parameter
    );

    %---------------------------------------------------------------------------
    fprintf( '- calculate gear shifts\n' );

    [ CalculatedGearsOutput ...
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
    ] = calculateShiftpointsNdvFullPC (  ...
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
    );

    s = size( tab_case_result, 1 );
    tab_case_result( s, col_case_result_g_average ) = ...
      { AverageGearOutput };
    tab_case_result( s, col_case_result_v_x_g_checksum ) = ...
      { ChecksumVxGearOutput };
    tab_case_result( s, col_case_result_n_max1 ) = ...
      { AdjustedMax95EngineSpeed };
    tab_case_result( s, col_case_result_n_max2 ) = ...
      { MaxEngineSpeedCycleOutput };
    tab_case_result( s, col_case_result_n_max3 ) = ...
      { MaxEngineSpeedReachableOutput };
    tab_case_result( s, col_case_result_n_max ) = ...
      { MaxEngineSpeedOutput };
    tab_case_result( s, col_case_result_v_max_cycle ) = ...
      { MaxVehicleSpeedCycleOutput };
    tab_case_result( s, col_case_result_v_max_vehicle ) = ...
      { MaxVehicleSpeedReachableOutput };
    tab_case_result( s, col_case_result_g_v_max_vehicle ) = ...
      { GearMaxVehicleSpeedReachableOutput };
    tab_case_result( s, col_case_result_n_min_drive_1 ) = ...
      { MinDriveEngineSpeed1stOutput };
    tab_case_result( s, col_case_result_n_min_drive_1_to_2 ) = ...
      { MinDriveEngineSpeed1stTo2ndOutput };
    tab_case_result( s, col_case_result_n_min_drive_2_decel ) = ...
      { MinDriveEngineSpeed2ndDecelOutput };
    tab_case_result( s, col_case_result_n_min_drive_2 ) = ...
      { MinDriveEngineSpeed2ndOutput };
    tab_case_result( s, col_case_result_n_min_drive_3 ) = ...
      { MinDriveEngineSpeedGreater2ndOutput };
    
    s = size( tab_engine_result, 1 );
    for p = 1 : size( PowerCurveOutput{ 1 }, 1 )
       tab_engine_result( s + p, col_engine_result_case ) = ...
         { i };
       tab_engine_result( s + p, col_engine_result_n ) = ...
         { PowerCurveOutput{ 1 }( p ) };
       tab_engine_result( s + p, col_engine_result_p ) = ...
         { PowerCurveOutput{ 2 }( p ) };
       tab_engine_result( s + p, col_engine_result_ASM ) = ...
         { PowerCurveOutput{ 3 }( p ) };
    end
    
    s = size( tab_shift_power, 1 );
    t_nbr = size( RequiredEngineSpeedsOutput{ 1 }, 1 );
    g_nbr = size( RequiredEngineSpeedsOutput, 2 );
    for t = 0 : t_nbr - 1
      for g = 1 : g_nbr
        p = t * g_nbr + g;
        tab_shift_power( s + p, col_shift_power_case ) = ...
          { i };
        tab_shift_power( s + p, col_shift_power_t ) = ...
          { t };
        tab_shift_power( s + p, col_shift_power_g ) = ...
          { g };
        tab_shift_power( s + p, col_shift_power_n ) = ...
          { RequiredEngineSpeedsOutput{ g }( t + 1) };
        tab_shift_power( s + p, col_shift_power_p ) = ...
          { AvailablePowersOutput{ g }( t + 1 ) };
      end
    end

    s = size( tab_shift, 1 );
    for p = 1 : size( TraceTimesOutput )
      tab_shift( s + p, col_shift_case ) = ...
        { i };
      tab_shift( s + p, col_shift_t ) = ...
        { TraceTimesOutput( p ) };   
      tab_shift( s + p, col_shift_v ) = ...
        { RequiredVehicleSpeedsOutput( p ) };
      tab_shift( s + p, col_shift_p ) = ...
        { RequiredPowersOutput( p ) }; 
      tab_shift( s + p, col_shift_g ) = ...
        { GearsOutput( p ) };
      tab_shift( s + p, col_shift_clutch_disengaged ) = ...
        { ClutchDisengagedOutput( p ) };
      tab_shift( s + p, col_shift_clutch_undefined ) = ...
        { ClutchUndefinedOutput( p ) };
      tab_shift( s + p, col_shift_clutch_HST ) = ...
        { ClutchHSTOutput( p ) };
      tab_shift( s + p, col_shift_g_corrections ) = ...
        { GearCorrectionsOutput( p ) };
    end
    
    s = size( tab_shift_condensed, 1 );
    for p = 1 : size( CalculatedGearsOutput{ 1 }, 1 )
       tab_shift_condensed( s + p, col_shift_condensed_case ) = ...
         { i };
       tab_shift_condensed( s + p, col_shift_condensed_t ) = ...
         { CalculatedGearsOutput{ 1 }( p ) };
       tab_shift_condensed( s + p, col_shift_condensed_gear_or_clutch ) = ...
         { strtrim( CalculatedGearsOutput{ 2 }( p, : ) ) };
    end
    
    %---------------------------------------------------------------------------
    fprintf( '- write output files :\n' );

    fprintf( '  - case_result.txt\n' );
    if i > 1
      fileID = fopen( 'case_result.txt', 'a' );
    else
      fileID = fopen( 'case_result.txt', 'w' );
      fprintf( fileID, '%4s'  , 'case' );
      fprintf( fileID, ', %5s', 'r_max' );
      fprintf( fileID, ', %5s', 'f_dsc' );
      fprintf( fileID, ', %7s', 'v_sum' );
      fprintf( fileID, ', %5s', 'v_max' );
      fprintf( fileID, ', %8s', 'd_cycle' );
      fprintf( fileID, ', %6s', 'g_avg' );
      fprintf( fileID, ', %9s', 'v_x_g_sum' );
      fprintf( fileID, ', %7s', 'n_max1' );
      fprintf( fileID, ', %7s', 'n_max2' );
      fprintf( fileID, ', %7s', 'n_max3' );
      fprintf( fileID, ', %7s', 'n_max' );
      fprintf( fileID, ', %7s', 'v_max_c' );
      fprintf( fileID, ', %7s', 'v_max_v' );
      fprintf( fileID, ', %7s', 'g_v_max' );
      fprintf( fileID, ', %7s', 'n_min1' );
      fprintf( fileID, ', %7s', 'n_min12' );
      fprintf( fileID, ', %7s', 'n_min2d' );
      fprintf( fileID, ', %7s', 'n_min2' );
      fprintf( fileID, ', %7s', 'n_min3' );
      fprintf( fileID, '\n' );
    end
    for k = 1 : size( tab_case_result, 1 )
      fprintf( fileID, '%4d'    , tab_case_result{ k, col_case_result_case } );
      fprintf( fileID, ', %5.3f', tab_case_result{ k, col_case_result_r_max } );
      fprintf( fileID, ', %5.3f', tab_case_result{ k, col_case_result_f_dsc } );
      fprintf( fileID, ', %7.1f', tab_case_result{ k, col_case_result_v_checksum } );
      fprintf( fileID, ', %5.1f', tab_case_result{ k, col_case_result_v_max } );
      fprintf( fileID, ', %8.1f', tab_case_result{ k, col_case_result_d_cycle } );
      fprintf( fileID, ', %6.4f', tab_case_result{ k, col_case_result_g_average } );
      fprintf( fileID, ', %9.1f', tab_case_result{ k, col_case_result_v_x_g_checksum } );
      fprintf( fileID, ', %7.2f', tab_case_result{ k, col_case_result_n_max1 } );
      fprintf( fileID, ', %7.2f', tab_case_result{ k, col_case_result_n_max2 } );
      fprintf( fileID, ', %7.2f', tab_case_result{ k, col_case_result_n_max3 } );
      fprintf( fileID, ', %7.2f', tab_case_result{ k, col_case_result_n_max } );
      fprintf( fileID, ', %7.1f', tab_case_result{ k, col_case_result_v_max_cycle } );
      fprintf( fileID, ', %7.1f', tab_case_result{ k, col_case_result_v_max_vehicle } );
      fprintf( fileID, ', %7d'  , tab_case_result{ k, col_case_result_g_v_max_vehicle } );
      fprintf( fileID, ', %7.2f', tab_case_result{ k, col_case_result_n_min_drive_1 } );
      fprintf( fileID, ', %7.2f', tab_case_result{ k, col_case_result_n_min_drive_1_to_2 } );
      fprintf( fileID, ', %7.2f', tab_case_result{ k, col_case_result_n_min_drive_2_decel } );
      fprintf( fileID, ', %7.2f', tab_case_result{ k, col_case_result_n_min_drive_2 } );
      fprintf( fileID, ', %7.2f', tab_case_result{ k, col_case_result_n_min_drive_3 } );
      fprintf( fileID, '\n' );
    end
    fclose( fileID );

    fprintf( '  - engine_result.txt\n' );
    if i > 1
      fileID = fopen( 'engine_result.txt', 'a' );
    else
      fileID = fopen( 'engine_result.txt', 'w' );
      fprintf( fileID, '%4s'  , 'case' );
      fprintf( fileID, ', %7s', 'n' );
      fprintf( fileID, ', %5s', 'p' );
      fprintf( fileID, ', %5s', 'ASM' );
      fprintf( fileID, '\n' );
    end
    for k = 1 : size( tab_engine_result, 1 )
      fprintf( fileID,  '%4d'    , tab_engine_result{ k, col_engine_result_case } );
      fprintf( fileID,  ', %7.2f', tab_engine_result{ k, col_engine_result_n } );
      fprintf( fileID,  ', %5.1f', tab_engine_result{ k, col_engine_result_p } );
      fprintf( fileID,  ', %5.3f', tab_engine_result{ k, col_engine_result_ASM } );
      fprintf( fileID, '\n' );
    end
    fclose( fileID );

    fprintf( '  - trace_interpolated.txt\n' );
    if i > 1
      fileID = fopen( 'trace_interpolated.txt', 'a' );
    else
      fileID = fopen( 'trace_interpolated.txt', 'w' );
      fprintf( fileID, '%4s'  , 'case' );
      fprintf( fileID, ', %4s', 't' );
      fprintf( fileID, ', %5s', 'v' );
      fprintf( fileID, '\n' );
    end
    for k = 1 : size( tab_trace_interpolated, 1 )
      fprintf( fileID, '%4d'    , tab_trace_interpolated{ k, col_trace_interpolated_case } );
      fprintf( fileID, ', %4d'  , tab_trace_interpolated{ k, col_trace_interpolated_t } );
      fprintf( fileID, ', %5.1f', tab_trace_interpolated{ k, col_trace_interpolated_v } );
      fprintf( fileID, '\n' );
    end
    fclose( fileID );

    fprintf( '  - trace_scaled.txt\n' );
    if i > 1
      fileID = fopen( 'trace_scaled.txt', 'a' );
    else
      fileID = fopen( 'trace_scaled.txt', 'w' );
      fprintf( fileID, '%4s'  , 'case' );
      fprintf( fileID, ', %4s', 't' );
      fprintf( fileID, ', %5s', 'v' );
      fprintf( fileID, ', %6s', 'is_dsc' );
      fprintf( fileID, ', %6s', 'is_cap' );
      fprintf( fileID, ', %6s', 'is_cmp' );
      fprintf( fileID, '\n' );
    end
    for k = 1 : size( tab_trace_scaled, 1 )
      fprintf( fileID, '%4d'    , tab_trace_scaled{ k, col_trace_scaled_case } );
      fprintf( fileID, ', %4d'  , tab_trace_scaled{ k, col_trace_scaled_t } );
      fprintf( fileID, ', %5.1f', tab_trace_scaled{ k, col_trace_scaled_v } );
      fprintf( fileID, ', %6d'  , tab_trace_scaled{ k, col_trace_scaled_downscaled } );
      fprintf( fileID, ', %6d'  , tab_trace_scaled{ k, col_trace_scaled_capped } );
      fprintf( fileID, ', %6d'  , tab_trace_scaled{ k, col_trace_scaled_compensated } );
      fprintf( fileID, '\n' );
    end
    fclose( fileID );

    fprintf( '  - phase_result.txt\n' );
    if i > 1
      fileID = fopen( 'phase_result.txt', 'a' );
    else
      fileID = fopen( 'phase_result.txt', 'w' );
      fprintf( fileID, '%4s'  , 'case' );
      fprintf( fileID, ', %5s', 'phase' );
      fprintf( fileID, ', %8s', 'v_sum' );
      fprintf( fileID, ', %5s', 't_cmp' );
      fprintf( fileID, '\n' );
    end
    for k = 1 : size( tab_phase_result, 1 )
      fprintf( fileID, '%4d'    , tab_phase_result{ k, col_phase_result_case } );
      fprintf( fileID, ', %5d'  , tab_phase_result{ k, col_phase_result_phase } );
      fprintf( fileID, ', %8.1f', tab_phase_result{ k, col_phase_result_v_checksum } );
      fprintf( fileID, ', %5d'  , tab_phase_result{ k, col_phase_result_t_dist_comp } );
      fprintf( fileID, '\n' );
    end
    fclose( fileID );

    fprintf( '  - shift_power.txt\n' );
    if i > 1
      fileID = fopen( 'shift_power.txt', 'a' );
    else
      fileID = fopen( 'shift_power.txt', 'w' );
      fprintf( fileID, '%4s'  , 'case' );
      fprintf( fileID, ', %4s', 't' );
      fprintf( fileID, ', %2s', 'g' );
      fprintf( fileID, ', %7s', 'n' );
      fprintf( fileID, ', %6s', 'p_avail' );
      fprintf( fileID, '\n' );
    end
    for k = 1 : size( tab_shift_power, 1 )
      fprintf( fileID,  '%4d'    , tab_shift_power{ k, col_shift_power_case } );
      fprintf( fileID,  ', %4d'  , tab_shift_power{ k, col_shift_power_t } );
      fprintf( fileID,  ', %2d'  , tab_shift_power{ k, col_shift_power_g } );
      fprintf( fileID,  ', %7.2f', tab_shift_power{ k, col_shift_power_n } );
      fprintf( fileID,  ', %6.1f', tab_shift_power{ k, col_shift_power_p } );
      fprintf( fileID, '\n' );
    end
    fclose( fileID );

    fprintf( '  - shift.txt\n' );
    if i > 1
      fileID = fopen( 'shift.txt', 'a' );
    else
      fileID = fopen( 'shift.txt', 'w' );
      fprintf( fileID, '%4s'    , 'case' );
      fprintf( fileID, ', %4s'  , 't' );
      fprintf( fileID, ', %5s'  , 'v' );
      fprintf( fileID, ', %5s'  , 'p_req' );
      fprintf( fileID, ', %2s'  , 'g' );
      fprintf( fileID, ', %6s'  , 'clutch' );
      fprintf( fileID, ', %6s'  , 'undef' );
      fprintf( fileID, ', %30s' , 'clutch_HST' );
      fprintf( fileID, ', %109s', 'g_corrections' );
      fprintf( fileID, '\n' );
    end
    for k = 1 : size( tab_shift, 1 )
      fprintf( fileID, '%4d'    , tab_shift{ k, col_shift_case } );
      fprintf( fileID, ', %4d'  , tab_shift{ k, col_shift_t } );
      fprintf( fileID, ', %5.1f', tab_shift{ k, col_shift_v } );
      fprintf( fileID, ', %5.1f', tab_shift{ k, col_shift_p } );
      fprintf( fileID, ', %2d'  , tab_shift{ k, col_shift_g } );
      fprintf( fileID, ', %6d'  , tab_shift{ k, col_shift_clutch_disengaged } );
      fprintf( fileID, ', %6d'  , tab_shift{ k, col_shift_clutch_undefined } );
      fprintf( fileID, ', %30s' , tab_shift{ k, col_shift_clutch_HST }{ 1 } );
      fprintf( fileID, ', %109s', tab_shift{ k, col_shift_g_corrections }{ 1 } );
      fprintf( fileID, '\n' );
    end
    fclose( fileID );

    fprintf( '  - shift_condensed.txt\n' );
    if i > 1
      fileID = fopen( 'shift_condensed.txt', 'a' );
    else
      fileID = fopen( 'shift_condensed.txt', 'w' );
      fprintf( fileID, '%4s'  , 'case' );
      fprintf( fileID, ', %4s', 't' );
      fprintf( fileID, ', %15s', 'gear_or_clutch' );
      fprintf( fileID, '\n' );
    end
    for k = 1 : size( tab_shift_condensed, 1 )
      fprintf( fileID,  '%4d'   , tab_shift_condensed{ k, col_shift_condensed_case } );
      fprintf( fileID,  ', %4d' , tab_shift_condensed{ k, col_shift_condensed_t } );
      fprintf( fileID,  ', %15s', tab_shift_condensed{ k, col_shift_condensed_gear_or_clutch } );
      fprintf( fileID, '\n' );
    end
    fclose( fileID );

  end

  %-----------------------------------------------------------------------------
  function[ ...
    tab ...
  ] = read_tab ( ...
    file ...
  )
    progress_delay = 7;  %sec
    tprev = tstart = cputime() * 10;  % x10 to make it seconds
    str = fileread( file );
    str = regexprep(  str, '\n$', '' );
    str = regexprep(  str, '"', '' );
    semicolons = not( isempty( regexp( str, ';' ) ) );
    if semicolons
      str = regexprep(  str, ',', '.' );
      str = regexprep(  str, ';', ',' );
    end
    arr_str = strsplit( str, '\n' );
    % assume line without numeric value is headline
    arr_idx = regexp( arr_str( 1 ), ',[0-9. ]*,' );
    headline = isempty( arr_idx{ 1 } );
    if headline
      arr_str = arr_str( 2 : end );
    end
    tab = {};
    for i = 1 : length( arr_str )
      tab( i, : ) = strtrim( strsplit( arr_str{ i }, ',' ) );
    end
    for i = 1 : size( tab, 1 )

      %% Progres indicator
      %
      tnow = cputime() * 10;
      if (tnow - tprev) > progress_delay
        elapsed = (tnow - tstart);
        fprintf( 2, '  ...reading %i out of %i in %.1f sec\n', i, size( tab, 1 ), elapsed )
        fflush(stderr);
        tprev = tnow;
      end

      for k = 1 : size( tab, 2 )
        tab{ i, k } = str_to_num_or_str( tab{ i, k } );
      end
    end
  end

  %-----------------------------------------------------------------------------
  function[ ...
    row ...
  ] = get_tab_row ( ...
    tab_cell_array ...
  , col_nbr ...
  , val ...
  )
    idx = get_tab_idx( tab_cell_array, col_nbr, val );
    idx = find( idx );
    row = tab_cell_array( idx, : );
  end

  %-----------------------------------------------------------------------------
  function[ ...
    idx ...
  ] = get_tab_idx ( ...
    tab_cell_array ...
  , col_nbr ...
  , val ...
  )
    % find value 'val'
    % in column number 'col_nbr'
    % of table cell array 'tab_cell_array'
    col_cell_array = { tab_cell_array{ 1:end, col_nbr } };
    if strcmp( class( val ), 'char' )
      idx = strfind( col_cell_array, val );
      idx = not( cellfun( 'isempty', idx ) );
    else
      idx = ( [ col_cell_array{:} ] == val );     
    end
  end

  %-----------------------------------------------------------------------------
  function[ ...
    str_or_num ...
  ] = str_to_num_or_str ( ...
    str ...
  )
    [ num, valid ] = str2num( str );
    if valid
      str_or_num = num;
    else
      str_or_num = str;
    end
  end

end
