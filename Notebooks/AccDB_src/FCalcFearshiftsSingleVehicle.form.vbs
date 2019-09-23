Option Compare Database

Private Sub B2_Click()
	DoCmd.Close

End Sub



Private Sub Befehl107_Click()
	Dim wrkWS1
	Dim dbsDB1
	Dim rstce, rstbe
	Dim rstde, rstae
	Dim rstee, rstfe, rstge, rsthe
	Dim aa As Double, bb As Double, cc As Double, dd As Double, ee As Double, dt As Single, t As Single, n As Integer, m As Integer, m0 As Integer
	Dim g_acc As Byte, g_cruise As Byte, g_dec As Byte, n_norm_max As Double, P_res As Double
	Dim n_norm_1 As Double, n_norm_2 As Double, n_norm_3 As Double, n_norm_4 As Double, n_norm_5 As Double, n_norm_6 As Double, n_norm As Double
	Dim P_norm_1 As Double, P_norm_2 As Double, P_norm_3 As Double, P_norm_4 As Double, P_norm_5 As Double, P_norm_6 As Double
	Dim P_1 As Double, P_2 As Double, P_3 As Double, P_4 As Double, P_5 As Double, P_6 As Double, P_a As Double
	Dim a_1 As Double, a_2 As Double, a_3 As Double, a_4 As Double, a_5 As Double, a_6 As Double, n_min_drive_fact As Double, n_min_2_fact As Double
	Dim rated_speed As Integer, idling_speed As Integer, n_min_drive As Integer, n_min_2 As Integer, n_min_drive_set As Integer
	Dim fact_v_min_g2 As Double, f_dsc As Double


	m = 0
	n = 0
	m0 = 0
	t = 0

	Be92.Visible = True
	Be93.Visible = True
	Be110.Visible = True
	Text91.Visible = True
	Text92.Visible = True
	Text109.Visible = True


	Set wrkWS1 = DBEngine.Workspaces(0)
	Set dbsDB1 = wrkWS1.Databases(0)

	Set rsthe = dbsDB1.OpenRecordset("TB_vehicle_info", DB_OPEN_DYNASET)
	rsthe.MoveLast

	m0 = rsthe.RecordCount


	rsthe.MoveFirst


	Do Until rsthe.EOF

		m = m + 1


		Text91 = m
		Text92 = m0

		Me.Repaint


		Set rstae = dbsDB1.OpenRecordset("ST_eng", DB_OPEN_DYNASET)
		rstae.MoveFirst
		rstae.edit
		rstae!eng_no = rsthe!vehicle_no
		rstae.Update
		rstae.Close




		Set rstae = dbsDB1.OpenRecordset("ST_veh", DB_OPEN_DYNASET)
		rstae.MoveFirst
		rstae.edit
		rstae!veh_no = rsthe!vehicle_no
		rstae!description = rsthe!comments
		rstae.Update
		rstae.Close





		DoCmd.OpenQuery "A ST_vehicle_info del"
		DoCmd.OpenQuery "A ST_vehicle_info"
		DoCmd.OpenQuery "A ST_vehicle_info IDclass"
		DoCmd.OpenQuery "A TA_Pwot del"
		DoCmd.OpenQuery "A TA_Pwot"

		DoCmd.OpenQuery "A ST_vehicle_info dates"
		gearshift_calculation1
'Stop
		gearshift_calculation2
'Stop
		gearshift_calculation3

		numbering_g0
		numbering_g1
		numbering_g2
		numbering_g3
		numbering_g4
		numbering_g5
		numbering_g6
		numbering_g7
		numbering_g8
		numbering_g9
		numbering_g10
		numbering_ST

		DoCmd.OpenQuery "A gearshift_table stop"
		DoCmd.OpenQuery "A gearshift_table acc"
		DoCmd.OpenQuery "A gearshift_table cruise"
		DoCmd.OpenQuery "A gearshift_table dec"

		If Rahmen36 = 1 Then

			DoCmd.OpenQuery "A gearshift_table final_dec"

		End If

		calculation_of_tolerances



		GoTo weiter

'check_gear_use_calculation
'#########################################################################
'gear 0 and v >= 1 km/h

		n = 0

		Set rstbe = dbsDB1.OpenRecordset("A gearshift_table n_g0", DB_OPEN_DYNASET)

		If Not rstbe.EOF Then

			rstbe.MoveFirst

			Do Until rstbe.EOF

				If rstbe![duration in s] > 2 Then

					n = n + 1

				End If

				rstbe.MoveNext

			Loop

			If n > 0 Then

				DoCmd.OpenQuery "A gearshift_table n_g0"

			End If
		End If

		rstbe.Close

'#########################################################################
'gear 1

		n = 0

		Set rstbe = dbsDB1.OpenRecordset("A gearshift_table n_g1", DB_OPEN_DYNASET)

		If Not rstbe.EOF Then

			rstbe.MoveFirst

			Do Until rstbe.EOF

				If rstbe![duration in s] < 2 Then

					n = n + 1

				End If

				rstbe.MoveNext

			Loop

			If n > 0 Then

				DoCmd.OpenQuery "A gearshift_table n_g1"

			End If
		End If

		rstbe.Close

'#########################################################################
'gear 2

		n = 0

		Set rstbe = dbsDB1.OpenRecordset("A gearshift_table n_g2", DB_OPEN_DYNASET)

		If Not rstbe.EOF Then

			rstbe.MoveFirst

			Do Until rstbe.EOF

				If rstbe![duration in s] < 2 Then

					n = n + 1

				End If

				rstbe.MoveNext

			Loop

			If n > 0 Then

				DoCmd.OpenQuery "A gearshift_table n_g2"

			End If
		End If

		rstbe.Close

'#########################################################################
'gear 3

		n = 0

		Set rstbe = dbsDB1.OpenRecordset("A gearshift_table n_g3", DB_OPEN_DYNASET)

		If Not rstbe.EOF Then

			rstbe.MoveFirst

			Do Until rstbe.EOF

				If rstbe![duration in s] < 2 Then

					n = n + 1

				End If

				rstbe.MoveNext

			Loop

			If n > 0 Then

				DoCmd.OpenQuery "A gearshift_table n_g3"

			End If
		End If

		rstbe.Close

'#########################################################################
'gear 4

		n = 0

		Set rstbe = dbsDB1.OpenRecordset("A gearshift_table n_g4", DB_OPEN_DYNASET)

		If Not rstbe.EOF Then

			rstbe.MoveFirst

			Do Until rstbe.EOF

				If rstbe![duration in s] < 2 Then

					n = n + 1

				End If

				rstbe.MoveNext

			Loop

			If n > 0 Then

				DoCmd.OpenQuery "A gearshift_table n_g4"

			End If
		End If

		rstbe.Close

'#########################################################################
'gear 5

		n = 0

		Set rstbe = dbsDB1.OpenRecordset("A gearshift_table n_g5", DB_OPEN_DYNASET)

		If Not rstbe.EOF Then

			rstbe.MoveFirst

			Do Until rstbe.EOF

				If rstbe![duration in s] < 2 Then

					n = n + 1

				End If

				rstbe.MoveNext

			Loop

			If n > 0 Then

				DoCmd.OpenQuery "A gearshift_table n_g5"

			End If
		End If

		rstbe.Close

'#########################################################################
'gear 6

		n = 0

		Set rstbe = dbsDB1.OpenRecordset("A gearshift_table n_g6", DB_OPEN_DYNASET)

		If Not rstbe.EOF Then

			rstbe.MoveFirst

			Do Until rstbe.EOF

				If rstbe![duration in s] < 2 Then

					n = n + 1

				End If

				rstbe.MoveNext

			Loop

			If n > 0 Then

				DoCmd.OpenQuery "A gearshift_table n_g6"

			End If
		End If

		rstbe.Close

'#########################################################################
'gear 7

		n = 0

		Set rstbe = dbsDB1.OpenRecordset("A gearshift_table n_g7", DB_OPEN_DYNASET)

		If Not rstbe.EOF Then

			rstbe.MoveFirst

			Do Until rstbe.EOF

				If rstbe![duration in s] < 2 Then

					n = n + 1

				End If

				rstbe.MoveNext

			Loop

			If n > 0 Then

				DoCmd.OpenQuery "A gearshift_table n_g7"

			End If
		End If

		rstbe.Close

		weiter:

		Set rstbe = dbsDB1.OpenRecordset("A gearshift_table average_gear", DB_OPEN_DYNASET)
		rstbe.MoveFirst

		Set rstae = dbsDB1.OpenRecordset("ST_vehicle_info", DB_OPEN_DYNASET)

		rstae.MoveFirst
		rstae.edit

		rstae!average_gear = Int(rstbe!gear * 10000 + 0.5) / 10000

		rstae.Update

		rstbe.Close
		rstae.Close


		DoCmd.OpenQuery "A gearshift_table add_gearshift_table_all"
		DoCmd.OpenQuery "A ST_vehicle_info add_calculation_parameter_all"



		weiter_01:

		GoTo weiter02

		Set rstbe = dbsDB1.OpenRecordset("A gearshift_table tolerance violations2", DB_OPEN_DYNASET)

		If Not rstbe.EOF Then

			rstbe.MoveFirst

			Do Until rstbe.EOF

				MsgBox "Driveability problems can be expected in cycle part " & rstbe!part & ", time for tolerance violations: " & rstbe!n & " s"

				rstbe.MoveNext

			Loop

			rstbe.Close

		Else

			rstbe.Close

		End If


		weiter02:

		weiterhe:

		rsthe.MoveNext

	Loop

	MsgBox "gearshift calculation completed"
End Sub








Private Sub Befehl163_Click()

	Dim wrkWS1
	Dim dbsDB1
	Dim rstce, rstbe

	Set wrkWS1 = DBEngine.Workspaces(0)
	Set dbsDB1 = wrkWS1.Databases(0)

	Set rstbe = dbsDB1.OpenRecordset("A gearshift_table tolerance violations", DB_OPEN_DYNASET)

	If Not rstbe.EOF Then

		rstbe.Close

		DoCmd.OpenQuery "A gearshift_table tolerance violations", , acReadOnly

	Else

		rstbe.Close

		MsgBox "No datasets with speed tolerance violations found!"

	End If





End Sub

Private Sub Befehl166_Click()

	DoCmd.OpenQuery "A gearshift_table n_downshift", , acReadOnly

End Sub

Private Sub Befehl167_Click()

	DoCmd.OpenQuery "A gearshift_table n_upshift", , acReadOnly

End Sub






Private Sub Befehl204_Click()
	Dim wrkWS1
	Dim dbsDB1
	Dim rstce, rstbe
	Dim rstde, rstae
	Dim rstee, rstfe, rstge, rsthe
	Dim aa As Double, bb As Double, cc As Double, dd As Double, ee As Double, dt As Single, t As Single, n As Integer, m As Integer, m0 As Integer
	Dim g_acc As Byte, g_cruise As Byte, g_dec As Byte, n_norm_max As Double, P_res As Double
	Dim n_norm_1 As Double, n_norm_2 As Double, n_norm_3 As Double, n_norm_4 As Double, n_norm_5 As Double, n_norm_6 As Double, n_norm As Double
	Dim P_norm_1 As Double, P_norm_2 As Double, P_norm_3 As Double, P_norm_4 As Double, P_norm_5 As Double, P_norm_6 As Double
	Dim P_1 As Double, P_2 As Double, P_3 As Double, P_4 As Double, P_5 As Double, P_6 As Double, P_a As Double
	Dim a_1 As Double, a_2 As Double, a_3 As Double, a_4 As Double, a_5 As Double, a_6 As Double, n_min_drive_fact As Double, n_min_2_fact As Double
	Dim rated_speed As Integer, idling_speed As Integer, n_min_drive As Integer, n_min_2 As Integer, n_min_drive_set As Integer
	Dim fact_v_min_g2 As Double, f_dsc As Double, n_max As Double


	m = 0
	n = 0
	m0 = 0
	t = 0

	Be92.Visible = True
	Be93.Visible = True
	Be110.Visible = True
	Text91.Visible = True
	Text92.Visible = True
	Text109.Visible = True


	Set wrkWS1 = DBEngine.Workspaces(0)
	Set dbsDB1 = wrkWS1.Databases(0)

	Set rsthe = dbsDB1.OpenRecordset("vehicle_info", DB_OPEN_DYNASET)

	rsthe.MoveFirst



	Set rstbe = dbsDB1.OpenRecordset("n95_low_high", DB_OPEN_DYNASET)




	Do Until rsthe.EOF

		m = m + 1

		Text91 = m
		Me.Repaint

		Set rstce = dbsDB1.OpenRecordset("A TB_Pwot_ST_veh", DB_OPEN_DYNASET)
		Set rstde = dbsDB1.OpenRecordset("A TB_Pwot_ST_veh", DB_OPEN_DYNASET)







		Set rstae = dbsDB1.OpenRecordset("ST_veh", DB_OPEN_DYNASET)
		rstae.MoveFirst
		rstae.edit
		rstae!veh_no = rsthe!vehicle_no
		rstae.Update
		rstae.Close

		rstce.MoveLast

		n_max = rstce!n

		rstce.MoveFirst



		rstde.MoveFirst
		rstde.MoveNext

		i = 0

		rstbe.AddNew

		If rstce!Pwot_norm > 0.5 Then

			GoTo tn95_low

		ElseIf rstce!Pwot_norm = 0.5 Then


			rstbe!n_50 = rstce!n

			GoTo tn95_low

		ElseIf rstde!Pwot_norm = 0.5 Then

			rstbe!n_50 = rstde!n

			GoTo tn95_low

		ElseIf rstce!Pwot_norm < 0.5 And rstde!Pwot_norm > 0.5 Then

			rstbe!n_50 = rstce!n + (rstde!n - rstce!n) / (rstde!Pwot_norm - rstce!Pwot_norm) * (0.5 - rstce!Pwot_norm)

			GoTo tn95_low

		ElseIf rstce!Pwot_norm < 0.5 And rstde!Pwot_norm < 0.5 Then

			Do Until rstce!Pwot_norm <= 0.5 And rstde!Pwot_norm > 0.5

				rstce.MoveNext
				rstde.MoveNext

			Loop

			rstbe!n_50 = rstce!n + (rstde!n - rstce!n) / (rstde!Pwot_norm - rstce!Pwot_norm) * (0.5 - rstce!Pwot_norm)


		End If

		tn95_low:

		If rstce!Pwot_norm < 0.95 And rstde!Pwot_norm < 0.95 Then

			Do Until rstce!Pwot_norm <= 0.95 And rstde!Pwot_norm > 0.95

				rstce.MoveNext
				rstde.MoveNext

			Loop

		End If



		If rstce!Pwot_norm = 0.95 Then


			rstbe!vehicle_no = rstce!no_engine
			rstbe!n_95_low = rstce!n

'MsgBox "low n1 = " & rstce!n & "Pwot_norm1 = " & rstce!Pwot_norm

			Do Until rstce!Pwot_norm > 0.95 And rstde!Pwot_norm <= 0.95

				rstce.MoveNext
				rstde.MoveNext

			Loop

			If rstde!Pwot_norm < 0.95 Then

				rstbe!n_95_high = rstce!n + (rstde!n - rstce!n) / (rstde!Pwot_norm - rstce!Pwot_norm) * (0.95 - rstce!Pwot_norm)

'MsgBox "high n1 = " & rstce!n & ", n2 = " & rstde!n & ", Pwot_norm1 = " & rstce!Pwot_norm & ", Pwot_norm2 = " & rstde!Pwot_norm


			Else

				rstbe!n_95_high = rstde!n

'MsgBox "high n1 = " & rstce!n & "Pwot_norm1 = " & rstce!Pwot_norm

			End If

			GoTo endloop

		Else

			rstbe!vehicle_no = rstce!no_engine
			rstbe!n_95_low = rstce!n + (rstde!n - rstce!n) / (rstde!Pwot_norm - rstce!Pwot_norm) * (0.95 - rstce!Pwot_norm)

'MsgBox "low n1 = " & rstce!n & ", n2 = " & rstde!n & ", Pwot_norm1 = " & rstce!Pwot_norm & ", Pwot_norm2 = " & rstde!Pwot_norm


			Do Until rstce!Pwot_norm > 0.95 And rstde!Pwot_norm <= 0.95 Or rstde!n = n_max

				rstce.MoveNext
				rstde.MoveNext

			Loop

			If rstde!Pwot_norm < 0.95 Then

				rstbe!n_95_high = rstce!n + (rstde!n - rstce!n) / (rstde!Pwot_norm - rstce!Pwot_norm) * (0.95 - rstce!Pwot_norm)

'MsgBox "high n1 = " & rstce!n & ", n2 = " & rstde!n & ", Pwot_norm1 = " & rstce!Pwot_norm & ", Pwot_norm2 = " & rstde!Pwot_norm

			Else

				rstbe!n_95_high = rstde!n

'MsgBox "high n1 = " & rstce!n & "Pwot_norm1 = " & rstce!Pwot_norm

			End If

			GoTo endloop


		End If


		endloop:
		On Error Resume Next

		rstbe.Update
		rstce.Close
		rstde.Close

		endloop2:

		rsthe.MoveNext

	Loop

	rsthe.Close
	rstbe.Close

	MsgBox "Done!"

End Sub

Private Sub Befehl21_Click()



	DoCmd.OpenQuery "A gearshift_table check_results_final", , acReadOnly



End Sub

Private Sub Befehl22_Click()

	Dim wrkWS1
	Dim dbsDB1
	Dim rstce, rstbe

	Set wrkWS1 = DBEngine.Workspaces(0)
	Set dbsDB1 = wrkWS1.Databases(0)

	Set rstbe = dbsDB1.OpenRecordset("A gearshift_table check_results_Ptot_above_P_max", DB_OPEN_DYNASET)

	If Not rstbe.EOF Then

		rstbe.Close

		DoCmd.OpenQuery "A gearshift_table check_results_Ptot_above_P_max", , acReadOnly

	Else

		rstbe.Close

		MsgBox "No datasets with P_available < P_required found!"

	End If

End Sub

Private Sub Befehl24_Click()

	DoCmd.OpenForm "F export results"

End Sub

Private Sub Befehl28_Click()


	Dim wrkWS1
	Dim dbsDB1
	Dim rstce, rstbe
	Dim rstde, rstae
	Dim rstee, rstfe, rstge, rsthe
	Dim aa As Double, bb As Double, cc As Double, dd As Double, ee As Double, dt As Single, t As Single, n As Integer, m As Integer
	Dim g_acc As Byte, g_cruise As Byte, g_dec As Byte, n_norm_max As Double, P_res As Double
	Dim n_norm_1 As Double, n_norm_2 As Double, n_norm_3 As Double, n_norm_4 As Double, n_norm_5 As Double, n_norm_6 As Double, n_norm As Double
	Dim P_norm_1 As Double, P_norm_2 As Double, P_norm_3 As Double, P_norm_4 As Double, P_norm_5 As Double, P_norm_6 As Double
	Dim P_1 As Double, P_2 As Double, P_3 As Double, P_4 As Double, P_5 As Double, P_6 As Double, P_a As Double
	Dim a_1 As Double, a_2 As Double, a_3 As Double, a_4 As Double, a_5 As Double, a_6 As Double, n_min_drive_fact As Double, n_min_2_fact As Double
	Dim rated_speed As Integer, idling_speed As Integer, n_min_drive As Integer, n_min_2 As Integer, n_min_drive_set As Integer
	Dim fact_v_min_g2 As Double, fact_g2_min As Double


	m = 0
	n = 0

	t = 0




	Set wrkWS1 = DBEngine.Workspaces(0)
	Set dbsDB1 = wrkWS1.Databases(0)



	Set rstae = dbsDB1.OpenRecordset("A gearshift_table_all case_max_last", DB_OPEN_DYNASET)

	If Not rstae.EOF Then

		rstae.MoveFirst

	End If

	Set rstbe = dbsDB1.OpenRecordset("ST_vehicle_info", DB_OPEN_DYNASET)
	rstbe.MoveFirst
	rstbe.edit
	If IsNull(rstae!case_max_last) Then
		rstbe!case_no = 1

	Else
		rstbe!case_no = rstae!case_max_last + 1
	End If
	rstbe.Update

	rstae.Close

	Set rstae = dbsDB1.OpenRecordset("A vehicle_info ST_vehicle_info", DB_OPEN_DYNASET)

	rstae.MoveFirst

	If s104 = True And s106 = False And rstbe!test_mass_modified = False Then

		MsgBox "You did not save the test mass modification!"

		Exit Sub

	ElseIf s106 = True And s104 = False And rstbe!road_load_modified = False Then

		MsgBox "You did not save the road load modifications!"

		Exit Sub

	ElseIf s104 = True And s106 = True And rstbe!test_mass_modified = False Then

		MsgBox "You did not save the test mass and road load modifications!"

		Exit Sub

	End If

	If Ko195 = True And (rstbe!v_cap = "" Or rstbe!v_cap = 0) Then

		MsgBox "You did not insert a speed cap value!"

		Exit Sub

	End If

	If rstbe!n_min_drive_up < rstbe!n_min_drive_set Then


		MsgBox "You chose a n_min_drive_up value lower than the default value, that is not allowed!"

		Exit Sub

	ElseIf rstbe!n_min_drive_down < rstbe!n_min_drive_set Then

		MsgBox "You chose a n_min_drive_down value lower than the default value, that is not allowed!"

		Exit Sub


	End If







	If (Ko195.Visible = False Or Ko195 = False) And rstbe!v_cap > 0 Then

		rstbe.edit
		rstbe!v_cap = Null
		rstbe.Update

	End If


	If (Ko179.Visible = False Or Ko179 = False) And rstbe!n_min_drive_set <> rstae!n_min_drive_set Then

		rstbe.edit
		rstbe!n_min_drive_set = rstae!n_min_drive_set
		rstbe.Update

	End If


	If Ko228 = True And (IsNull(Text230) Or IsNull(Text234) Or IsNull(Text242)) Then

		MsgBox "You have to specify n_min_drive_start_up and/or n_min_drive_start_down and/or t_end of the start phase!"

		Exit Sub

	End If

	If IsNull(Kombinationsfeld12) Then

		MsgBox "You have to chose a vehicle in order to start the calculations!"

		Exit Sub

	End If

	rstae.Close
	rstbe.Close

	DoCmd.OpenQuery "A ST_vehicle_info dates"
	gearshift_calculation1
'Stop
	gearshift_calculation2
'Stop
	gearshift_calculation3

	DoCmd.OpenQuery "A gearshift_table stop"
	DoCmd.OpenQuery "A gearshift_table acc"
	DoCmd.OpenQuery "A gearshift_table cruise"
	DoCmd.OpenQuery "A gearshift_table dec"

	numbering_g0
	numbering_g1
	numbering_g2
	numbering_g3
	numbering_g4
	numbering_g5
	numbering_g6
	numbering_g7
	numbering_g8
	numbering_g9
	numbering_g10
	numbering_ST





	calculation_of_tolerances



	n = 0

	Set rstbe = dbsDB1.OpenRecordset("A gearshift_table n_g0", DB_OPEN_DYNASET)

	If Not rstbe.EOF Then

		rstbe.MoveFirst

		Do Until rstbe.EOF

			If rstbe![duration in s] > 2 Then

				n = n + 1

			End If

			rstbe.MoveNext

		Loop

		If n > 0 Then

			DoCmd.OpenQuery "A gearshift_table n_g0"

		End If
	End If

	rstbe.Close

'#########################################################################
'gear 1

	n = 0

	Set rstbe = dbsDB1.OpenRecordset("A gearshift_table n_g1", DB_OPEN_DYNASET)

	If Not rstbe.EOF Then

		rstbe.MoveFirst

		Do Until rstbe.EOF

			If rstbe![duration in s] < 2 Then

				n = n + 1

			End If

			rstbe.MoveNext

		Loop

		If n > 0 Then

			DoCmd.OpenQuery "A gearshift_table n_g1"

		End If
	End If

	rstbe.Close

'#########################################################################
'gear 2

	n = 0

	Set rstbe = dbsDB1.OpenRecordset("A gearshift_table n_g2", DB_OPEN_DYNASET)

	If Not rstbe.EOF Then

		rstbe.MoveFirst

		Do Until rstbe.EOF

			If rstbe![duration in s] < 2 Then

				n = n + 1

			End If

			rstbe.MoveNext

		Loop

		If n > 0 Then

			DoCmd.OpenQuery "A gearshift_table n_g2"

		End If
	End If

	rstbe.Close

'#########################################################################
'gear 3

	n = 0

	Set rstbe = dbsDB1.OpenRecordset("A gearshift_table n_g3", DB_OPEN_DYNASET)

	If Not rstbe.EOF Then

		rstbe.MoveFirst

		Do Until rstbe.EOF

			If rstbe![duration in s] < 2 Then

				n = n + 1

			End If

			rstbe.MoveNext

		Loop

		If n > 0 Then

			DoCmd.OpenQuery "A gearshift_table n_g3"

		End If
	End If

	rstbe.Close

'#########################################################################
'gear 4

	n = 0

	Set rstbe = dbsDB1.OpenRecordset("A gearshift_table n_g4", DB_OPEN_DYNASET)

	If Not rstbe.EOF Then

		rstbe.MoveFirst

		Do Until rstbe.EOF

			If rstbe![duration in s] < 2 Then

				n = n + 1

			End If

			rstbe.MoveNext

		Loop

		If n > 0 Then

			DoCmd.OpenQuery "A gearshift_table n_g4"

		End If
	End If

	rstbe.Close

'#########################################################################
'gear 5

	n = 0

	Set rstbe = dbsDB1.OpenRecordset("A gearshift_table n_g5", DB_OPEN_DYNASET)

	If Not rstbe.EOF Then

		rstbe.MoveFirst

		Do Until rstbe.EOF

			If rstbe![duration in s] < 2 Then

				n = n + 1

			End If

			rstbe.MoveNext

		Loop

		If n > 0 Then

			DoCmd.OpenQuery "A gearshift_table n_g5"

		End If
	End If

	rstbe.Close

'#########################################################################
'gear 6

	n = 0

	Set rstbe = dbsDB1.OpenRecordset("A gearshift_table n_g6", DB_OPEN_DYNASET)

	If Not rstbe.EOF Then

		rstbe.MoveFirst

		Do Until rstbe.EOF

			If rstbe![duration in s] < 2 Then

				n = n + 1

			End If

			rstbe.MoveNext

		Loop

		If n > 0 Then

			DoCmd.OpenQuery "A gearshift_table n_g6"

		End If
	End If

	rstbe.Close

'#########################################################################
'gear 7

	n = 0

	Set rstbe = dbsDB1.OpenRecordset("A gearshift_table n_g7", DB_OPEN_DYNASET)

	If Not rstbe.EOF Then

		rstbe.MoveFirst

		Do Until rstbe.EOF

			If rstbe![duration in s] < 2 Then

				n = n + 1

			End If

			rstbe.MoveNext

		Loop

		If n > 0 Then

			DoCmd.OpenQuery "A gearshift_table n_g7"

		End If
	End If

	rstbe.Close

'#########################################################################
'gear 8

	n = 0

	Set rstbe = dbsDB1.OpenRecordset("A gearshift_table n_g8", DB_OPEN_DYNASET)

	If Not rstbe.EOF Then

		rstbe.MoveFirst

		Do Until rstbe.EOF

			If rstbe![duration in s] < 2 Then

				n = n + 1

			End If

			rstbe.MoveNext

		Loop

		If n > 0 Then

			DoCmd.OpenQuery "A gearshift_table n_g8"

		End If
	End If

	rstbe.Close


'#########################################################################
'gear 9

	n = 0

	Set rstbe = dbsDB1.OpenRecordset("A gearshift_table n_g9", DB_OPEN_DYNASET)

	If Not rstbe.EOF Then

		rstbe.MoveFirst

		Do Until rstbe.EOF

			If rstbe![duration in s] < 2 Then

				n = n + 1

			End If

			rstbe.MoveNext

		Loop

		If n > 0 Then

			DoCmd.OpenQuery "A gearshift_table n_g9"

		End If
	End If

	rstbe.Close


'#########################################################################
'gear 10

	n = 0

	Set rstbe = dbsDB1.OpenRecordset("A gearshift_table n_g10", DB_OPEN_DYNASET)

	If Not rstbe.EOF Then

		rstbe.MoveFirst

		Do Until rstbe.EOF

			If rstbe![duration in s] < 2 Then

				n = n + 1

			End If

			rstbe.MoveNext

		Loop

		If n > 0 Then

			DoCmd.OpenQuery "A gearshift_table n_g10"

		End If
	End If

	rstbe.Close


	weiter:

	Set rstbe = dbsDB1.OpenRecordset("A gearshift_table average_gear", DB_OPEN_DYNASET)
	rstbe.MoveFirst

	Set rstae = dbsDB1.OpenRecordset("ST_vehicle_info", DB_OPEN_DYNASET)

	rstae.MoveFirst
	rstae.edit

	rstae!average_gear = Int(rstbe!gear * 10000 + 0.5) / 10000

	rstae.Update

	rstbe.Close
	rstae.Close

	If Kontroll164 = False Then

		GoTo weiter_01

	Else

		DoCmd.OpenQuery "A gearshift_table add_gearshift_table_all"
		DoCmd.OpenQuery "A ST_vehicle_info add_calculation_parameter_all"

	End If




	weiter_01:



	Set rstbe = dbsDB1.OpenRecordset("A gearshift_table tolerance violations2", DB_OPEN_DYNASET)

	If Not rstbe.EOF Then

		rstbe.MoveFirst

		Do Until rstbe.EOF

			MsgBox "Driveability problems can be expected in cycle part " & rstbe!part & ", time for tolerance violations: " & rstbe!n & " s"

			rstbe.MoveNext

		Loop

		rstbe.Close

	Else

		rstbe.Close

	End If


	weiter02:



	DoCmd.OpenQuery "A TB_export act"


	MsgBox "gearshift calculation completed"

	Ko179.Visible = False
	Ko219.Visible = False
	Ko228.Visible = False
	Ko236.Visible = False
	Be180.Visible = False
	Text181.Visible = False
	Text221.Visible = False
	Text230.Visible = False
	Text234.Visible = False
	Be182.Visible = False
	Be222.Visible = False
	Be231.Visible = False
	Be235.Visible = False
	Ko195.Visible = False
	Be196.Visible = False
	Text174.Visible = False
	Text155.Visible = False
	Text238.Visible = False
	Text151.Visible = False
	Text157.Visible = False
	Text152.Visible = False
	Text71.Visible = False
	Text168.Visible = False
	Text170.Visible = False
	Text161.Visible = False
	Text159.Visible = False
	Text224.Visible = False
	Be103.Visible = False
	Be175.Visible = False
	Be156.Visible = False
	Be239.Visible = False
	Be153.Visible = False
	Be158.Visible = False
	Be154.Visible = False
	Be72.Visible = False
	Be171.Visible = False
	Be169.Visible = False
	Be162.Visible = False
	Be160.Visible = False
	Be225.Visible = False
	s108.Visible = False
	Be243.Visible = False
	Text242.Visible = False
	Be198.Visible = False
	Text197.Visible = False
	Ko195 = False
	Kombinationsfeld12 = Null
	Ko244.Visible = False
	Ko246.Visible = False
	Ko248.Visible = False
	Ko250.Visible = False
	Be251.Visible = False

End Sub

Private Sub Befehl51_Click()
	DoCmd.OpenQuery "A gearshift_table n_ave parts", , acReadOnly
	DoCmd.OpenQuery "A gearshift_table n_ave", , acReadOnly

End Sub

Private Sub Befehl56_Click()





End Sub

Private Sub Befehl58_Click()




End Sub

Private Sub Befehl59_Click()

	Dim wrkWS1
	Dim dbsDB1
	Dim rstce, rstbe

	Set wrkWS1 = DBEngine.Workspaces(0)
	Set dbsDB1 = wrkWS1.Databases(0)

	Set rstbe = dbsDB1.OpenRecordset("A gearshift_table check p_wot", DB_OPEN_DYNASET)

	If Not rstbe.EOF Then

		rstbe.Close

		DoCmd.OpenQuery "A gearshift_table check p_wot", , acReadOnly

	Else

		rstbe.Close
		MsgBox "No wot operation datasets found!"

	End If

End Sub

Private Sub Befehl61_Click()



End Sub

Private Sub Befehl62_Click()



End Sub

Private Sub Befehl63_Click()

	DoCmd.OpenQuery "A gearshift_table W_res parts", , acReadOnly
	DoCmd.OpenQuery "A gearshift_table W_res", , acReadOnly


End Sub





Private Sub Form_Open(Cancel As Integer)

	DoCmd.Maximize

	Dim wrkWS1
	Dim dbsDB1
	Dim rstce, rstbe
	Dim rstde, rstae
	Dim rstee
	Dim aa As Double, bb As Double, cc As Double, dd As Double, ee As Double, dt As Single, t As Single, n As Integer, m As Integer
	Dim n_min_drive_fact As Double, n_min_2_fact As Double
	Dim rated_speed As Integer, idling_speed As Integer, n_min_drive As Integer, n_min_2 As Integer, n_min_drive_set As Integer
	m = 0
	n = 0

	t = 0

	Set wrkWS1 = DBEngine.Workspaces(0)
	Set dbsDB1 = wrkWS1.Databases(0)

	Kontrollk130 = False
	Kontr217 = False
	Kontr205 = False
	Kontroll202 = False
	Kontr217 = False

	Kontr226 = True
	Kontr226.Visible = False
	Text238.Visible = False
	Be239.Visible = False
	Ko244.Visible = False
	Ko246.Visible = False
	Ko248.Visible = False
	Ko250.Visible = False
	Be251.Visible = False



	Text7 = ""
	Text15 = ""

'Be92.Visible = False
'Be93.Visible = False
'Be110.Visible = False
'Text91.Visible = False
'Text92.Visible = False
'Text109.Visible = False

	Be198.Visible = False
	Text197 = ""
	Text197.Visible = False

	Rahmen183.Visible = False





	Be182.Visible = False
	Text181.Visible = False
	Be222.Visible = False
	Text221.Visible = False
	Ko219 = False
	Ko219.Visible = False
	Be225.Visible = False
	Text224.Visible = False




	Text20 = Null
	Text221 = Null
	Text221.Visible = False
	Ko219 = False
	Ko219.Visible = False
	Be222.Visible = False
	Ko228 = False
	Ko228.Visible = False
	Ko236 = False
	Ko236.Visible = False
	Text230.Visible = False
	Text234.Visible = False
	Be231.Visible = False
	Be235.Visible = False


	Kombinationsfeld13 = DLookup("[eng_no]", "ST_eng")
	Kombinationsfeld12 = ""
	Text100 = ""
	Kombinationsfeld19 = n_min_drive_set



	Kombinationsfeld52 = DLookup("[class]", "ST_WLTC_version")
	Kombinationsfeld43.Visible = False


	Kontrollk126 = False
	Kontrollk124 = True
	Kontrollk111 = False
	Kontrollk114 = False

	Kontroll164 = False
	Bezeichnungsfeld165.Visible = False
	Text71 = ""
	Text155 = ""
	Text151 = ""
	Text157 = ""
	Text159 = ""
	Text152 = ""
	Text161 = ""
	Text174 = ""
	Text170 = ""
	Text168 = ""


	Text76 = n_min_drive_set
	Text77 = n_min_2
	Text85 = ""


	Rahmen36 = 1
	Rahmen207 = 3



	s104 = False
	s106 = False
	s108 = False
	Ko195 = False
	Ko179 = False



	s108.Visible = False
	Ko195.Visible = False
	Ko179.Visible = False

	Be175.Visible = False
	Be156.Visible = False
	Be153.Visible = False
	Be158.Visible = False
	Be154.Visible = False
	Be180.Visible = False

	Be196.Visible = False
	Be72.Visible = False
	Be171.Visible = False
	Be169.Visible = False
	Be160.Visible = False
	Be162.Visible = False
	Be103.Visible = False

	Text174.Visible = False
	Text155.Visible = False
	Text151.Visible = False
	Text157.Visible = False
	Text152.Visible = False

	Text71.Visible = False
	Text170.Visible = False
	Text168.Visible = False
	Text159.Visible = False
	Text161.Visible = False

	Be92.Visible = False
	Be93.Visible = False
	Be110.Visible = False
	Text91.Visible = False
	Text92.Visible = False
	Text109.Visible = False
	Befehl107.Visible = False
	Be243.Visible = False
	Text242.Visible = False

	m = 0
	n = 0

	t = 0

	Befehl28.Enabled = False






End Sub

Private Sub K0_AfterUpdate()


End Sub

Private Sub Ko179_AfterUpdate()
'If (Kontr217 = False And n_min_drive_up <= rstce!n_min_drive_set) Or (Kontr217 = True And n_min_drive_up <= rstce!n_min_drive_new) Then
	Dim n_min_drive As Integer
	Dim wrkWS1
	Dim dbsDB1
	Dim rstce
	Dim n_min_drive_up As Integer


	Set wrkWS1 = DBEngine.Workspaces(0)
	Set dbsDB1 = wrkWS1.Databases(0)
'...

	Set rstce = dbsDB1.OpenRecordset("ST_vehicle_info", DB_OPEN_DYNASET)

	rstce.MoveFirst

	If Kontr217 = False Then

		n_min_drive = rstce!n_min_drive_set

	Else

		n_min_drive = rstce!n_min_drive_new

	End If


	If Ko179 = True Then

		Be182.Visible = True
		Text181.Visible = True

		Text181 = n_min_drive
	Else

		Be182.Visible = False
		Text181.Visible = False

		rstce.edit

		If Kontr217 = False Then

			rstce!n_min_drive_up = rstce!n_min_drive_set

		Else

			rstce!n_min_drive_up = rstce!n_min_drive_new

		End If

		rstce!n_min_drive_up_modified = False


		rstce.Update

		Text152 = n_min_drive
		Text152.Requery

	End If

	rstce.Close

End Sub

Private Sub Ko195_AfterUpdate()

	If Ko195 = False Then

		Be198.Visible = False
		Text197.Visible = False

	Else

		Be198.Visible = True
		Text197.Visible = True

	End If



End Sub

Private Sub Kombinationsfeld104_AfterUpdate()

	Dim wrkWS1
	Dim dbsDB1
	Dim rstce, rstbe
	Dim rstde, rstae
	Dim rstee



	Set wrkWS1 = DBEngine.Workspaces(0)
	Set dbsDB1 = wrkWS1.Databases(0)
'...


	Set rstae = dbsDB1.OpenRecordset("ST_default_RL_values", DB_OPEN_DYNASET)
	rstae.MoveFirst
	rstae.edit
	rstae!Number = Kombinationsfeld104
	rstae.Update
	rstae.Close





End Sub

Private Sub Ko219_AfterUpdate()
'If (Kontr217 = False And n_min_drive_up <= rstce!n_min_drive_set) Or (Kontr217 = True And n_min_drive_up <= rstce!n_min_drive_new) Then

	Dim n_min_drive As Integer
	Dim wrkWS1
	Dim dbsDB1
	Dim rstce
	Dim n_min_drive_up As Integer


	Set wrkWS1 = DBEngine.Workspaces(0)
	Set dbsDB1 = wrkWS1.Databases(0)
'...

	Set rstce = dbsDB1.OpenRecordset("ST_vehicle_info", DB_OPEN_DYNASET)

	rstce.MoveFirst

	If Kontr217 = False Then

		n_min_drive = rstce!n_min_drive_set
	Else

		n_min_drive = rstce!n_min_drive_new

	End If

	If Ko219 = True Then

		Be222.Visible = True
		Text221.Visible = True

		Text221 = n_min_drive

	Else

		Be222.Visible = False
		Text221.Visible = False

		rstce.edit

		If Kontr217 = False Then

			rstce!n_min_drive_down = rstce!n_min_drive_set

		Else

			rstce!n_min_drive_down = rstce!n_min_drive_new

		End If

		rstce!n_min_drive_down_modified = False

		rstce.Update

		Text224 = n_min_drive
		Text224.Requery

	End If

	rstce.Close

End Sub

Private Sub Ko228_AfterUpdate()

	If Ko228 = True Then


		Text230.Visible = True
		Text234.Visible = True
		Text242.Visible = True
		Text230 = Null
		Text234 = Null
		Text242 = Null

		Be231.Visible = True
		Be235.Visible = True
		Be243.Visible = True
		Ko236.Visible = True
		Be237.Visible = True

		Befehl28.Enabled = False

	Else

		Text230 = Null
		Text234 = Null
		Text242 = Null
		Ko236.Visible = False
		Text230.Visible = False
		Text234.Visible = False
		Text242.Visible = False
		Be231.Visible = False
		Be235.Visible = False
		Be243.Visible = False
		Befehl28.Enabled = True

		Dim wrkWS1
		Dim dbsDB1
		Dim rstae
		Dim IDclass As Byte

		Set wrkWS1 = DBEngine.Workspaces(0)
		Set dbsDB1 = wrkWS1.Databases(0)

		Set rstae = dbsDB1.OpenRecordset("ST_vehicle_info", DB_OPEN_DYNASET)
		rstae.MoveFirst

		rstae.edit
		rstae!n_min_drive_start_up = Null
		rstae!n_min_drive_start_down = Null
		rstae!t_end_start_phase = Null
		rstae.Update
		rstae.Close


	End If


End Sub

Private Sub Ko236_AfterUpdate()

	Ko236 = False




	If Rahmen36 = 1 Then

		DoCmd.OpenQuery "A possible_tend_cold_WLTC", , acReadOnly


	ElseIf Rahmen36 = 2 Then

		DoCmd.OpenQuery "A possible_tend_cold_purge", , acReadOnly

	ElseIf Rahmen36 = 4 Then

		DoCmd.OpenQuery "A possible_tend_cold_random", , acReadOnly

	End If

End Sub

Private Sub Ko244_AfterUpdate()

	Dim wrkWS1
	Dim dbsDB1
	Dim rstae

	Set wrkWS1 = DBEngine.Workspaces(0)
	Set dbsDB1 = wrkWS1.Databases(0)

	Set rstae = dbsDB1.OpenRecordset("ST_vehicle_info", DB_OPEN_DYNASET)
	rstae.MoveFirst
	rstae.edit

	If Ko244 = True Then
		rstae![suppress gear 0 during downshifts] = True
	Else
		rstae![suppress gear 0 during downshifts] = False
	End If

	rstae.Update
	rstae.Close

End Sub

Private Sub Ko246_AfterUpdate()
	Dim wrkWS1
	Dim dbsDB1
	Dim rstae

	Set wrkWS1 = DBEngine.Workspaces(0)
	Set dbsDB1 = wrkWS1.Databases(0)

	Set rstae = dbsDB1.OpenRecordset("ST_vehicle_info", DB_OPEN_DYNASET)
	rstae.MoveFirst
	rstae.edit

	If Ko246 = True Then
		rstae![skip_downscaling] = True
	Else
		rstae![skip_downscaling] = False
	End If

	rstae.Update
	rstae.Close
End Sub

Private Sub Ko248_AfterUpdate()

	If Ko248 = True Then

		Ko250.Visible = True
		Be251.Visible = True
		Ko250 = ""

	Else

		Ko250.Visible = False
		Be251.Visible = False
		Ko179.Visible = False
		Ko219.Visible = False
		Ko228.Visible = False
		Ko236.Visible = False
		Be180.Visible = False
		Text181.Visible = False
		Text221.Visible = False
		Text230.Visible = False
		Text234.Visible = False
		Be182.Visible = False
		Be222.Visible = False
		Be231.Visible = False
		Be235.Visible = False
		Ko195.Visible = False
		Be196.Visible = False
		Text174.Visible = False
		Text155.Visible = False
		Text238.Visible = False
		Text151.Visible = False
		Text157.Visible = False
		Text152.Visible = False
		Text71.Visible = False
		Text168.Visible = False
		Text170.Visible = False
		Text161.Visible = False
		Text159.Visible = False
		Text224.Visible = False
		Be103.Visible = False
		Be175.Visible = False
		Be156.Visible = False
		Be239.Visible = False
		Be153.Visible = False
		Be158.Visible = False
		Be154.Visible = False
		Be72.Visible = False
		Be171.Visible = False
		Be169.Visible = False
		Be162.Visible = False
		Be160.Visible = False
		Be225.Visible = False
		s108.Visible = False
		Be243.Visible = False
		Text242.Visible = False
		Be198.Visible = False
		Text197.Visible = False
		Ko195 = False
		Kombinationsfeld12 = Null
		Ko244.Visible = False
		Ko246.Visible = False
'Ko248.Visible = False
		Ko250.Visible = False
		Be251.Visible = False


	End If

End Sub

Private Sub Ko250_AfterUpdate()
	Dim wrkWS1
	Dim dbsDB1
	Dim rstce, rstbe
	Dim rstde, rstae
	Dim r0 As Double, a1 As Double, b1 As Double, rmax As Double, p_req As Double, f_dsc_req As Double

	Set wrkWS1 = DBEngine.Workspaces(0)
	Set dbsDB1 = wrkWS1.Databases(0)
'...


	Set rstce = dbsDB1.OpenRecordset("ST_vehicle_info", DB_OPEN_DYNASET)
	rstce.MoveFirst

	rstce.edit
	rstce!IDclass_cycle = Ko250
	rstce!higher_vehicle_class_cycle_used = True
	rstce.Update

'rstce.Close

'##############################################################
'calculate dsc_req


	If rstce!IDclass_cycle = 1 Then

		r0 = 0.978
		a1 = 0.68
		b1 = -0.665

		p_req = (rstce!f0 * 61.4 + rstce!f1 * 61.4 ^ 2 + rstce!f2 * 61.4 ^ 3 + 1.03 * rstce!test_mass * 61.4 * 0.22) / 3600

		rmax = p_req / rstce!rated_power

		If rmax < r0 Then

			f_dsc_req = 0

		Else

			f_dsc_req = Int((a1 * rmax + b1) * 1000 + 0.5) / 1000

			If f_dsc_req < 0.01 Then

				f_dsc_req = 0

			End If

		End If

	ElseIf rstce!IDclass_cycle = 2 Then

		r0 = 0.866
		a1 = 0.606
		b1 = -0.525

		p_req = (rstce!f0 * 109.9 + rstce!f1 * 109.9 ^ 2 + rstce!f2 * 109.9 ^ 3 + 1.03 * rstce!test_mass * 109.9 * 0.36) / 3600

		rmax = p_req / rstce!rated_power

		If rmax < r0 Then

			f_dsc_req = 0

		Else

			f_dsc_req = Int((a1 * rmax + b1) * 1000 + 0.5) / 1000

			If f_dsc_req < 0.01 Then

				f_dsc_req = 0

			End If

		End If

	ElseIf rstce!IDclass_cycle > 2 Then

		r0 = 0.867
		a1 = 0.588
		b1 = -0.51

		p_req = (rstce!f0 * 111.9 + rstce!f1 * 111.9 ^ 2 + rstce!f2 * 111.9 ^ 3 + 1.03 * rstce!test_mass * 111.9 * 0.5) / 3600

		rmax = p_req / rstce!rated_power

		If rmax < r0 Then

			f_dsc_req = 0

		Else

			f_dsc_req = Int((a1 * rmax + b1) * 1000 + 0.5) / 1000

			If f_dsc_req < 0.01 Then

				f_dsc_req = 0

			End If

		End If

	End If

	rstce.edit


	rstce!Pres_130 = p_req
	rstce!Pres_130_Prated = rmax
	rstce!f_dsc_req = f_dsc_req

	rstce.Update
	rstce.Close

	Text161 = f_dsc_req

	Me.Requery

End Sub

Private Sub Kombinationsfeld12_AfterUpdate()
	Dim wrkWS1
	Dim dbsDB1
	Dim rstce, rstbe
	Dim rstde, rstae
	Dim rstee
	Dim aa As Double, bb As Double, cc As Double, dd As Double, ee As Double, dt As Single, t As Single, n As Integer, m As Integer
	Dim n_min_drive_fact As Double, n_min_2_fact As Double
	Dim rated_speed As Integer, idling_speed As Integer, n_min_drive As Integer, n_min_2 As Integer, n_min_drive_set As Integer
	m = 0
	n = 0

	t = 0

	Set wrkWS1 = DBEngine.Workspaces(0)
	Set dbsDB1 = wrkWS1.Databases(0)
'...

	If Rahmen36 = 1 Or Rahmen36 = 2 Then

		Ko244.Visible = True
		Ko244 = False
		Ko246.Visible = True
		Ko246 = False
		Ko248.Visible = True
		Ko248 = False

		Ko236.Visible = False
		Be237.Visible = False

		Ko195.Visible = True
		Be196.Visible = True

		Be222.Visible = False
		Text221.Visible = False
		Ko219.Visible = True
		Ko219 = False
		Be225.Visible = True
		Text224.Visible = True
		Text238.Visible = True
		Be239.Visible = True
'End If

		Ko179.Visible = True
		Ko179 = False

		If Ko195 = False Then
			Be198.Visible = False
			Text197 = ""
			Text197.Visible = False
		End If

		Ko219.Visible = True
		Be180.Visible = True
		Ko228.Visible = True

		Ko219 = False
		Ko228 = False

	ElseIf Rahmen36 = 4 Then

		If Kontr226 = True Then

			Ko244.Visible = True
			Ko244 = False

		Else

			Ko244 = False
			Ko244.Visible = False

		End If

		Ko236.Visible = False
		Be237.Visible = False


		Be222.Visible = False
		Text221.Visible = False
		Ko219.Visible = True
		Ko219 = False
		Be225.Visible = True
		Text224.Visible = True
		Text238.Visible = True
		Be239.Visible = True
'End If

		Ko179.Visible = True
		Ko179 = False

		If Ko195 = False Then
			Be198.Visible = False
			Text197 = ""
			Text197.Visible = False
		End If

		Ko219.Visible = True
		Be180.Visible = True
		Ko228.Visible = True

		Ko219 = False
		Ko228 = False


	ElseIf Rahmen36 = 3 Then

		Ko179.Visible = False
		Ko219.Visible = False
		Be180.Visible = False
		Ko195.Visible = False


	End If



	Be182.Visible = False

	Text181.Visible = False


	s108.Visible = True


	s104 = False
	s106 = False
	s108 = False

'Be178.Visible = True
	Be175.Visible = True
	Be156.Visible = True
	Be153.Visible = True
	Be158.Visible = True
	Be154.Visible = True
	Be180.Visible = True

	Be72.Visible = True
	Be171.Visible = True
	Be169.Visible = True
	Be160.Visible = True
	Be162.Visible = True
	Be103.Visible = True

	Text174.Visible = True
	Text155.Visible = True
	Text151.Visible = True
	Text157.Visible = True
	Text152.Visible = True

	Text71.Visible = True
	Text170.Visible = True
	Text168.Visible = True
	Text159.Visible = True
	Text161.Visible = True

	Text230.Visible = False
	Text234.Visible = False
	Be231.Visible = False
	Be235.Visible = False
	Text242.Visible = False
	Be243.Visible = False
	Be198.Visible = False
	Text197.Visible = False
	Ko195 = False

	Set rstae = dbsDB1.OpenRecordset("ST_veh", DB_OPEN_DYNASET)
	rstae.MoveFirst
	rstae.edit
	rstae!veh_no = Kombinationsfeld12
	rstae.Update
	rstae.Close

	Set rstae = dbsDB1.OpenRecordset("ST_eng", DB_OPEN_DYNASET)
	rstae.MoveFirst
	rstae.edit
	rstae!eng_no = Kombinationsfeld12
	rstae.Update
	rstae.Close

	Text10 = Kombinationsfeld12
	Me.Repaint

	DoCmd.OpenQuery "A ST_vehicle_info del"

	DoCmd.OpenQuery "A ST_vehicle_info"

	DoCmd.OpenQuery "A ST_vehicle_info IDclass"
	DoCmd.OpenQuery "A TA_Pwot del"
	DoCmd.OpenQuery "A TA_Pwot"

	Set rstae = dbsDB1.OpenRecordset("ST_vehicle_info", DB_OPEN_DYNASET)
	rstae.MoveFirst

	rstae.edit




	If Rahmen36 = 1 Then
		rstae!Cycle = "WLTC"
	ElseIf Rahmen36 = 2 Then
		rstae!Cycle = "EVAP purge"
	ElseIf Rahmen36 = 3 Then
		rstae!Cycle = "NEDC"
	ElseIf Rahmen36 = 4 Then
		rstae!Cycle = "other cycle"
	End If

	rstae!n_min_drive_start_up = Null
	rstae!n_min_drive_start_down = Null
	rstae!t_end_start_phase = Null

	rstae.Update

	rated_speed = rstae!rated_speed
	idling_speed = rstae!idling_speed
	n_min_drive = rstae![n_min_drive]
	n_min_2 = 0.9 * idling_speed
	n_min_drive_set = rstae![n_min_drive_set]

	Text100 = rstae![description]
	Text98 = rstae![test_mass]
	Text43 = rstae![f0]
	Text45 = rstae![f1]
	Text47 = rstae![f2]
	Text174 = rstae!test_mass


	Befehl28.Enabled = True

	Text76 = n_min_drive_set


	Text71 = rstae![rated_speed]
	Text155 = rstae![idling_speed]
	Text151 = rstae![v_max]

	Text157 = rstae![n_max1]
	Text238 = rstae![n_min_drive_set]
	Text159 = rstae![n_max2]
	Text152 = rstae![n_min_drive_up]
	Text224 = rstae![n_min_drive_down]
	Text161 = rstae![f_dsc_req]

	Text170 = rstae!no_of_gears
	Text168 = rstae!gear_v_max


	Me.Repaint

	rstae.Close


End Sub

Private Sub Kombinationsfeld13_AfterUpdate()
	Dim wrkWS1
	Dim dbsDB1
	Dim rstce, rstbe
	Dim rstde, rstae
	Dim rstee
	Dim aa As Double, bb As Double, cc As Double, dd As Double, ee As Double, dt As Single, t As Single, n As Integer, m As Integer

	m = 0
	n = 0

	t = 0



	Set wrkWS1 = DBEngine.Workspaces(0)
	Set dbsDB1 = wrkWS1.Databases(0)
'...


	Set rstae = dbsDB1.OpenRecordset("ST_eng", DB_OPEN_DYNASET)
	rstae.MoveFirst
	rstae.edit
	rstae!eng_no = Kombinationsfeld13
	rstae.Update
	rstae.Close
	Kombinationsfeld12.Enabled = True

	DoCmd.OpenQuery "A TB_Pwot_norm del"
	DoCmd.OpenQuery "A TB_Pwot_norm"
	DoCmd.OpenQuery "A ST_vehicle_info del"
	DoCmd.OpenQuery "A ST_vehicle_info"

End Sub



Public Sub gearshift_calculation2()

	Dim wrkWS1
	Dim dbsDB1
	Dim rstce, rstbe
	Dim rstde, rstae
	Dim rstee, rstfe, rstge, rsthe, rstie, rstke
	Dim aa As Double, bb As Double, cc As Double, dd As Double, ee As Double, dt As Double, t As Double, n As Double, m As Integer, k As Integer, h As Integer
	Dim g_acc As Byte, g_cruise As Byte, g_dec As Byte, n_norm_max As Double, P_res As Double, j As Integer, i As Integer, l As Integer, o As Integer, P As Integer
	Dim n_norm_1 As Double, n_norm_2 As Double, n_norm_3 As Double, n_norm_4 As Double, n_norm_5 As Double, n_norm_6 As Double, n_norm As Double
	Dim P_norm_1 As Double, P_norm_2 As Double, P_norm_3 As Double, P_norm_4 As Double, P_norm_5 As Double, P_norm_6 As Double, j1 As Byte, j2 As Byte
	Dim v_1 As Double, v_2 As Double, P_1 As Double, P_2 As Double, g_0 As Byte, g_1 As Byte, g_2 As Byte, P_a As Double, P_tot As Double
	Dim a_1 As Double, a_2 As Double, a_3 As Double, a_4 As Double, a_5 As Double, a_6 As Double, g_ref As Byte, t1 As Long, t2 As Long, t_ref As Long
	Dim g_2s As Byte, g_2e As Byte, g_2b As Byte, v As Double, P_max As Double, z As Double, IDn_norm As Integer
	Dim n_orig As Double, v_orig As Double, a As Double, v_de As Double, flag As Byte, flag2 As Byte, flag3 As Byte
	Dim a_de As Double, n_de As Double, n_norm_de As Double, IDn_norm_de As Integer, P_a_de As Double, P_tot_de As Double, P_res_de As Double, P_max_de As Double
	Dim downscale_factor As Double, n_max_wot As Double, n_min_wot As Double, Pwot As Double, Pavai As Double, ASM As Double, t_end_i As Integer, t_end_j As Integer, t_end_k As Integer
	Dim SM0 As Double, kr As Double, t_start As Integer, m_old As Integer, highidle As Double, Pavai_hidle As Double, g_2s_i As Byte, g_2s_j As Byte, g_2s_k As Byte
	Dim t_l As Integer, t_j As Integer, t_old_i As Integer, t_old_j As Integer, t_old_k As Integer, i_old As Integer, j_old As Integer, k_old As Integer
	Dim ti(300) As Long, g_start As Byte, flag_g As Byte, n_4c As Byte, flag_text7 As Byte

	m_old = 0
	m = 0
	n = 0
	j = 0
	t = 0



	P = 0

	Set wrkWS1 = DBEngine.Workspaces(0)
	Set dbsDB1 = wrkWS1.Databases(0)
	Text85 = ""

	Text20 = "calculate gear use"
	Me.Repaint




	Set rstae = dbsDB1.OpenRecordset("A ST_vehicle_info open", DB_OPEN_DYNASET)
	rstae.MoveFirst

	SM0 = rstae!SM0
	kr = rstae!kr



	flag = 0

	If Rahmen36 = 3 Then

		GoTo weiter_NEDC_2


	End If



	Set rstie = dbsDB1.OpenRecordset("A TA_Pwot sort", DB_OPEN_DYNASET)
	rstie.MoveLast
	n_max_wot = rstie.n

	Set rstke = dbsDB1.OpenRecordset("A TA_Pwot sort", DB_OPEN_DYNASET)

	Set rstbe = dbsDB1.OpenRecordset("A gearshift_table sort", DB_OPEN_DYNASET)

	rstie.MoveFirst
	rstke.MoveFirst
	rstke.MoveNext

	P = 1

	n = 0
	m = 0
	k = 0
	j = 0
	m_old = 0




	Set rstce = dbsDB1.OpenRecordset("A gearshift_table sort", DB_OPEN_DYNASET)
	Set rstde = dbsDB1.OpenRecordset("A gearshift_table sort", DB_OPEN_DYNASET)
	Set rstee = dbsDB1.OpenRecordset("A gearshift_table sort", DB_OPEN_DYNASET)
	Set rstfe = dbsDB1.OpenRecordset("A gearshift_table sort", DB_OPEN_DYNASET)
	Set rstge = dbsDB1.OpenRecordset("A gearshift_table sort", DB_OPEN_DYNASET)
	Set rsthe = dbsDB1.OpenRecordset("A gearshift_table sort", DB_OPEN_DYNASET)


'######################################################################################################################

	weiter3:

	m_old = m_old + 1
	n = 0
	m = 0
	flag_text7 = 0

	lap_4ab:

'####################################################################################################################
' Annex 2, paragraph 4(a)
' If a one step higher gear (n+1) is required for only 1 second and the gears before and after are the same (n), gear n+1 shall be corrected to gear n.

'####################################################################################################################


'1) ########################################################################################################################
'1) 343 -> 333, 342 -> 332, 243 -> 233, 4(a) of annex 2

	rstbe.MoveFirst
	rstce.MoveFirst
	rstce.MoveNext
	rstde.MoveFirst
	rstde.MoveNext
	rstde.MoveNext

	Do Until rstde.EOF

		If rstce!gear > rstbe!gear And rstde!gear <= rstbe!gear And rstde!gear > 0 Then

			rstce.edit
			If rstce!g_min <= rstbe!gear Then
				rstce!gear = rstbe!gear
				rstce!gear_modification = rstce!gear_modification & "1) 343 -> 333, 342 -> 332, "
				m = m + 1
			Else
				rstce!gear_modification = rstce!gear_modification & "1) Necessary gear modification not possible, "
				n = n + 1
			End If
			rstce.Update

		ElseIf rstce!gear = rstbe!gear + 2 And rstde!gear = rstbe!gear + 1 And rstce!gear > 0 Then

			rstce.edit
			If rstce!g_min <= rstde!gear Then
				rstce!gear = rstde!gear
				rstce!gear_modification = rstce!gear_modification & "1) 243 -> 233, "
				m = m + 1
			Else
				rstce!gear_modification = rstce!gear_modification & "1) Necessary gear modification not possible, "
				n = n + 1
			End If
			rstce.Update

		End If

		rstbe.MoveNext
		rstce.MoveNext
		rstde.MoveNext

	Loop


'#################################################################################################


'####################################################################################################################
' Annex 2, paragraph 4(a)
' Gears used during accelerations at vehicle speeds >= 1 km/h shall be used for a period of at least 2 seconds
' (e.g. a gear sequence 1, 2, 3, 3, 3, 3, 3 shall be replaced by 1, 1, 2, 2, 3, 3, 3).
' Gears shall not be skipped during acceleration phases.

'####################################################################################################################


' 4(a) ##########################################################################################################################


	rstbe.MoveFirst

	rstce.MoveFirst
	rstce.MoveNext

	rstde.MoveFirst
	rstde.MoveNext
	rstde.MoveNext

	rstee.MoveFirst
	rstee.MoveNext
	rstee.MoveNext
	rstee.MoveNext



	Do Until rstee.EOF

'2a) 1123 -> 1112, starting from standstill paragraph 4(a) of annex 2

		If (rstbe!gear = 1 Or rstbe!gear = 0) And rstce!gear = 1 And rstde!gear > 1 And rstee!gear > 1 And rstee!v > rstde!v And rstde!v > rstce!v And rstce!v > rstbe!v And rstbe!v < 1 And rstee!a > 0 Then

			rstde.edit
			If rstde!g_min = 1 Then
				rstde!gear = 1
				rstde!gear_modification = rstde!gear_modification & "2a) 1123 -> 1112, "
				m = m + 1
			Else
				rstde!gear_modification = rstde!gear_modification & "2a) Necessary gear modification not possible, "
				n = n + 1
			End If
			rstde.Update

			If rstee!gear > 2 Then

				rstee.edit
				If rstee!g_min <= 2 Then
					rstee!gear = 2
					rstee!gear_modification = rstee!gear_modification & "2a) 1113 -> 1112, "
					m = m + 1
				Else
					rstee!gear_modification = rstee!gear_modification & "2a) Necessary gear modification not possible, "
					n = n + 1
				End If
				rstee.Update

			End If


'2b1) & 2b2) g1>=g2, g2>=g3, g4=g3-1, g5=g3,g6=g5, g7>=g6, g4->g3, last sub-paragraph of 4(a) of annex 2

		ElseIf rstbe!v >= rstce!v And rstce!v >= rstde!v And rstee!v > rstde!v And rstde!v >= 1 And rstbe!gear >= rstce!gear And rstce!gear = rstde!gear + 1 And rstee!gear = rstce!gear Then

'2b1a and 2b1b check for 10 second window for downshifts ################################################

			g_ref = rstde!gear
			t_ref = rstde!Tim
			j1 = 0
			j2 = 0
			i = 0

			Do Until rstde!a <= 0 Or i = 9 Or rstde!v < 1

				rstde.MoveNext

				i = i + 1

				If rstde!gear <= g_ref Then

					j1 = j1 + 1
					t1 = rstde!Tim

				End If


			Loop

			For k = 1 To i

				rstde.MovePrevious

			Next k

			If rstce!Tim <> rstde!Tim - 1 Then
				MsgBox "Error2b1a " & rstce!Tim & ", " & rstde!Tim
				Exit Sub
			End If

			i = 0

			Do Until i = 6 Or rstde!v < 1

				rstde.MoveNext

				i = i + 1

				If rstde!gear <= g_ref Then

					j2 = j2 + 1
					t2 = rstde!Tim

				End If


			Loop

			For k = 1 To i

				rstde.MovePrevious

			Next k

			If rstce!Tim <> rstde!Tim - 1 Then
				MsgBox "Error2b1b " & rstce!Tim & ", " & rstde!Tim
				Exit Sub
			End If

			If j1 = 0 And j2 = 0 Then

'2b1a) g1>=g2, g2=g3+1, g4=g2, g3->g2 #######################################################

				rstde.edit

				rstde!gear = rstce!gear
				rstde!gear_modification = rstde!gear_modification & "2b1a) g1>=g2, g2=g3+1, g4=g2, g3->g2, "
				m = m + 1

				rstde.Update

			ElseIf j1 > 0 And j2 = 0 Then

'2b1b) lower gear ahead within a 10 s window, g4->g3 ##########################################

				rstee.edit
				If rstee!g_min <= rstde!gear Then
					rstee!gear = rstde!gear
					rstee!gear_modification = rstee!gear_modification & "2b1b) lower gear ahead within a 10 s window, g4->g3, "
					m = m + 1
				Else
					rstee!gear_modification = rstee!gear_modification & "2b1b) Necessary gear modification not possible, "
					n = n + 1
				End If
				rstee.Update

			ElseIf j1 = 0 And j2 > 0 Then


'2b2) application of 4(c), gi->g_ref #############################################################

				Do Until rstde!Tim = t2 - 1

					rstde.MoveNext

					If rstde!gear > g_ref Then

						rstde.edit
						If rstde!g_min <= g_ref Then
							rstde!gear = g_ref
							rstde!gear_modification = rstde!gear_modification & "2b2) application of 4(c), gi->g_ref, "
							m = m + 1
						Else
							rstde!gear_modification = rstde!gear_modification & "2b2) Necessary gear modification not possible, "
							n = n + 1
						End If
						rstde.Update

					End If

				Loop

				Do Until rstde!Tim = t_ref

					rstde.MovePrevious

				Loop

				If rstce!Tim <> rstde!Tim - 1 Then
					MsgBox "Error2b2 " & rstce!Tim & ", " & rstde!Tim
					Exit Sub
				End If

			End If


'2b3) g1>=g2, g2>=g3, g4>=g3, g5>=g4, g6=g5, g7>=g6, g5->g4, last sub-paragraph of 4(a) of annex 2

		ElseIf rstbe!v >= rstce!v And rstce!v < rstde!v And rstee!v > rstde!v And rstce!v >= 1 And rstbe!gear >= rstce!gear And rstce!gear = rstde!gear - 1 Then


			rstde.edit
			If rstde!g_min <= rstce!gear Then
				rstde!gear = rstce!gear
				rstde!gear_modification = rstde!gear_modification & "2b3) g1>=g2, g2<g3, g4>=g3, g3->g2, "
				m = m + 1
			Else
				rstde!gear_modification = rstde!gear_modification & "2b3) Necessary gear modification not possible, "
				n = n + 1
			End If
			rstde.Update

'2c) ##############################################################################################
'2c) 2234 -> 2233, 4(a) of annex 2


		ElseIf rstce!gear = rstbe!gear And rstde!gear = rstce!gear + 1 And rstee!gear > rstde!gear And rstee!v >= rstde!v And rstde!v > rstce!v And rstce!v > rstbe!v And rstbe!v >= 1 Then

			rstee.edit
			If rstee!g_min <= rstce!gear + 1 Then
				rstee!gear = rstce!gear + 1
				rstee!gear_modification = rstee!gear_modification & "2c) 2234 -> 2233, "
				m = m + 1
			Else
				rstee!gear_modification = rstee!gear_modification & "2c) Necessary gear modification not possible, "
				n = n + 1
			End If
			rstee.Update

'2d) ##################################################################################################
'2d) 2244 or 2243 -> 2233, 4(a) of annex 2

		ElseIf rstce!gear >= rstbe!gear And rstde!gear > rstce!gear + 1 And rstee!gear > rstce!gear + 1 And rstee!v >= rstde!v And rstde!v > rstce!v And rstce!v > rstbe!v And rstbe!v >= 1 Then

			If rstde!v = rstee!v And rstde!gear = rstee!gear And rstde!gear = rstce!gear + 2 Then

				i = 0

				For k = 1 To 4

					rstee.MoveNext

					If rstee!v = rstde!v Then

						i = i + 1

					End If

				Next k

				For k = 1 To 4

					rstee.MovePrevious

				Next k

				If rstee!Tim <> rstde!Tim + 1 Then
					MsgBox "Error3a " & rstde!Tim & ", " & rstee!Tim
					Exit Sub
				End If

				If i = 4 Then

'3) #################################################################################################
' Paragraph 4(a) But an upshift by two gears is allowed at the transition from an acceleration phase to a constant speed phase,
' if the duration of constant speed phase exceeds 5 seconds.

					rstde.edit
					rstde!gear_modification = rstde!gear_modification & "3a) upshift by two gears is permitted, "

					rstde.Update

				Else

					GoTo weiter_2d

				End If

			Else

				weiter_2d:

				rstde.edit
				If rstde!g_min <= rstce!gear + 1 Then
					rstde!gear = rstce!gear + 1
					rstde!gear_modification = rstde!gear_modification & "2d) 2244 -> 2234, "
					m = m + 1
				Else
					rstde!gear_modification = rstde!gear_modification & "2d) Necessary gear modification not possible, "
					n = n + 1
				End If
				rstde.Update


				rstee.edit
				If rstee!g_min <= rstce!gear + 1 Then
					rstee!gear = rstce!gear + 1
					rstee!gear_modification = rstee!gear_modification & "2d) 2234 -> 2233, "
					m = m + 1
				Else
					rstee!gear_modification = rstee!gear_modification & "2d) Necessary gear modification not possible, "
					n = n + 1
				End If
				rstee.Update

			End If



		End If



		rstbe.MoveNext
		rstce.MoveNext
		rstde.MoveNext
		rstee.MoveNext


	Loop


'#######################################################################################################

	If flag_text7 = 0 Then

		flag_text7 = 1

		GoTo lap_4ab

	End If



'##################################################################################################
' If a lower gear is required at a higher vehicle speed during an acceleration phase for more than 1 second within a moving window of 10 seconds,
' the higher gears before shall be corrected to the lower gear. This correction shall not be performed for gear 1.

'4) check for lower gear ahead during acc 4(b) of annex 2
' gear i-3 #########################################################################


	rstbe.MoveFirst
	rstce.MoveFirst
	rstce.MoveNext
	rstde.MoveFirst
	rstde.MoveNext
	rstde.MoveNext

	Do Until rstde.EOF



		If rstde!v > rstce!v And rstce!v >= 1 Then



			l = 0
			k = 0
			i = 0
			j = 0
			t_old_i = 0
			t_old_j = 0
			t_old_k = 0
			flag_g = 0

			For h = 0 To 300

				ti(h) = 0

			Next h

			g_1 = rstce!gear

			If g_1 <= 2 Then

				GoTo weiter_k32

			Else

				t_start = rstce!Tim

				l = 0

				Do Until rstde!v <= rstce!v Or rstce!g_min > g_1

					If rstce!gear > g_1 Then

						flag_g = flag_g + rstce!gear - g_1

						g_1 = rstce!gear

						t_start = rstce!Tim

					End If

					t_end_j = rstce!Tim

					If rstce!gear = g_1 - 3 And rstce!gear > 0 Then

						i = i + 1

						If i > 300 Then
							MsgBox "i = " & i & " at t = " & rstce!Tim
							Stop
						End If

						ti(i) = rstce!Tim
						g_2s_i = rstce!gear
						t_end_i = rstce!Tim
						t_end_j = rstce!Tim


					End If

					l = l + 1

					rstbe.MoveNext
					rstce.MoveNext
					rstde.MoveNext

				Loop

				For h = 1 To l

					rstbe.MovePrevious
					rstce.MovePrevious
					rstde.MovePrevious

				Next h


				l = 0



				If i > 0 Then

					If rstce!Tim < ti(1) Then

						Do Until rstce!Tim = ti(1)

							rstbe.MoveNext
							rstce.MoveNext
							rstde.MoveNext

						Loop

					ElseIf rstce!Tim > ti(1) Then

						Do Until rstce!Tim = ti(1)

							rstbe.MovePrevious
							rstce.MovePrevious
							rstde.MovePrevious

						Loop

					End If

					rstbe.MovePrevious
					rstce.MovePrevious
					rstde.MovePrevious

					Do Until rstce!gear = g_2s_i Or rstbe!v >= rstce!v

						rstbe.MovePrevious
						rstce.MovePrevious
						rstde.MovePrevious


					Loop

					ti(0) = rstce!Tim
					g_start = rstce!gear

					If rstce!Tim < t_start Then

						t_start = rstce!Tim


					End If



				Else

					GoTo weiter_k32

				End If



				j = 0

				For h = 1 To i

					If ti(i - h + 1) - ti(i - h) <= 9 Then

						j = i - h + 1
						GoTo weiter_i32

					Else


						t_end_i = ti(i - h)

					End If

				Next h



				If i = 1 Then

					GoTo weiter_i33

				End If


				weiter_i32:


				If j = 1 And i = 1 And g_start > g_2s_i Then

					l = 0

					Do Until rstce!Tim = ti(i) + 1

						If rstce!gear > g_2s_i + 1 Then

							rstce.edit

							rstce!gear = g_2s_i + 1
							rstce!gear_modification = rstce!gear_modification & "4_k23) check for lower gear ahead during acc, "

							rstce.Update
							m = m + 1

						End If

						l = l + 1

						rstbe.MoveNext
						rstce.MoveNext
						rstde.MoveNext

					Loop

					For h = 1 To l

						rstbe.MovePrevious
						rstce.MovePrevious
						rstde.MovePrevious

					Next h

					If rstce!Tim <> t_start Then

						MsgBox "check for lower gear ahead during acc 4(b1) of annex 2, gear i-3, error at t = " & rstce!Tim

						Stop

					End If

					GoTo weiter_k32

				End If


				If j <= 1 Then

					l = 0

					Do Until rstce!Tim = ti(i) + 1

						If rstce!gear = g_2s_i And rstce!Tim > t_end_i Then

							rstce.edit

							rstce!gear = g_2s_i + 1
							rstce!gear_modification = rstce!gear_modification & "4_k2a3) check for lower gear ahead during acc, "

							rstce.Update
							m = m + 1

						ElseIf rstce!gear > g_2s_i + 1 And rstce!Tim > t_end_i Then

							rstce.edit

							rstce!gear = g_2s_i + 1
							rstce!gear_modification = rstce!gear_modification & "4_k2b3) check for lower gear ahead during acc, "

							rstce.Update
							m = m + 1

						End If

						l = l + 1

						rstbe.MoveNext
						rstce.MoveNext
						rstde.MoveNext

					Loop

					For h = 1 To l

						rstbe.MovePrevious
						rstce.MovePrevious
						rstde.MovePrevious

					Next h



					If j = 1 Then

						l = 0

						Do Until rstce!Tim = t_end_i + 1

							If rstce!Tim >= ti(0) Then

								rstce.edit


								If rstce!gear > g_2s_i And rstce!g_min <= g_2s_i Then
									rstce!gear = g_2s_i
									rstce!gear_modification = rstce!gear_modification & "4_k13) check for lower gear ahead during acc, "
								ElseIf rstce!gear = g_2s_i Then
									rstce!gear_modification = rstce!gear_modification & "4_k13) gear modification not necessary, "
								End If

								rstce.Update
								m = m + 1

							End If

							l = l + 1

							rstbe.MoveNext
							rstce.MoveNext
							rstde.MoveNext

						Loop

					End If

					GoTo weiter_k32

				Else

					l = 0



					Do Until rstce!Tim = t_end_i + 1


						If rstce!Tim >= ti(0) Then

							rstce.edit


							If rstce!gear > g_2s_i And rstce!g_min <= g_2s_i Then
								rstce!gear = g_2s_i
								rstce!gear_modification = rstce!gear_modification & "4_k13) check for lower gear ahead during acc, "
							ElseIf rstce!gear = g_2s_i Then
								rstce!gear_modification = rstce!gear_modification & "4_k13) gear modification not necessary, "
							End If

							rstce.Update
							m = m + 1

						End If

						l = l + 1

						rstbe.MoveNext
						rstce.MoveNext
						rstde.MoveNext

					Loop

					GoTo weiter_j32

				End If

				weiter_i33:


				l = 0

				Do Until rstce!Tim = ti(1) + 1

					If rstce!gear = g_2s_i And rstce!Tim > ti(0) Then

						rstce.edit

						rstce!gear = g_2s_i + 1
						rstce!gear_modification = rstce!gear_modification & "4_k2a3) check for lower gear ahead during acc, "

						rstce.Update
						m = m + 1

					ElseIf rstce!gear > g_2s_i + 1 And rstce!Tim > t_end_i Then

						rstce.edit

						rstce!gear = g_2s_i + 1
						rstce!gear_modification = rstce!gear_modification & "4_k2b3) check for lower gear ahead during acc, "

						rstce.Update
						m = m + 1

					End If

					l = l + 1

					rstbe.MoveNext
					rstce.MoveNext
					rstde.MoveNext

				Loop

				GoTo weiter_k32


				weiter_j32:

				If rstce!Tim < t_end_i Then

					Do Until rstce!Tim = t_end_i

						rstbe.MoveNext
						rstce.MoveNext
						rstde.MoveNext

					Loop

				End If

			End If
		End If

		weiter_k32:

		rstbe.MoveNext
		rstce.MoveNext
		rstde.MoveNext


	Loop




'ßßßßßßßßßßßßßßßßßßßßßßßßßßßßßßßßßßßßßßßßßßßßßßßßßßßßßßßßßßßßßßßßßßßßßßßßßßßßßßßßßßßßßßßßß
'4) check for lower gear ahead during acc 4(b) of annex 2
' gear i-2 #########################################################################


	rstbe.MoveFirst
	rstce.MoveFirst
	rstce.MoveNext
	rstde.MoveFirst
	rstde.MoveNext
	rstde.MoveNext

	Do Until rstde.EOF



		If rstde!v > rstce!v And rstce!v >= 1 Then



			l = 0
			k = 0
			i = 0
			j = 0
			t_old_i = 0
			t_old_j = 0
			t_old_k = 0
			flag_g = 0

			For h = 0 To 300

				ti(h) = 0

			Next h

			g_1 = rstce!gear

			If g_1 <= 2 Then

				GoTo weiter_k2

			Else

				t_start = rstce!Tim

				l = 0

				Do Until rstde!v <= rstce!v Or rstce!g_min > g_1

					If rstce!gear > g_1 Then

						flag_g = flag_g + rstce!gear - g_1

						g_1 = rstce!gear

						t_start = rstce!Tim

					End If

					t_end_j = rstce!Tim

					If rstce!gear = g_1 - 2 And rstce!gear > 0 Then

						i = i + 1

						If i > 300 Then
							MsgBox "i = " & i & " at t = " & rstce!Tim
							Stop
						End If

						ti(i) = rstce!Tim
						g_2s_i = rstce!gear
						t_end_i = rstce!Tim
						t_end_j = rstce!Tim


					End If

					l = l + 1

					rstbe.MoveNext
					rstce.MoveNext
					rstde.MoveNext

				Loop

				For h = 1 To l

					rstbe.MovePrevious
					rstce.MovePrevious
					rstde.MovePrevious

				Next h


				l = 0



				If i > 0 Then

					If rstce!Tim < ti(1) Then

						Do Until rstce!Tim = ti(1)

							rstbe.MoveNext
							rstce.MoveNext
							rstde.MoveNext

						Loop

					ElseIf rstce!Tim > ti(1) Then

						Do Until rstce!Tim = ti(1)

							rstbe.MovePrevious
							rstce.MovePrevious
							rstde.MovePrevious

						Loop

					End If

					rstbe.MovePrevious
					rstce.MovePrevious
					rstde.MovePrevious

					Do Until rstce!gear = g_2s_i Or rstbe!v >= rstce!v

						rstbe.MovePrevious
						rstce.MovePrevious
						rstde.MovePrevious


					Loop

					ti(0) = rstce!Tim
					g_start = rstce!gear

					If rstce!Tim < t_start Then

						t_start = rstce!Tim


					End If



				Else

					GoTo weiter_k2

				End If



				j = 0

				For h = 1 To i

					If ti(i - h + 1) - ti(i - h) <= 9 Then

						j = i - h + 1
						GoTo weiter_i2

					Else


						t_end_i = ti(i - h)

					End If

				Next h



				If i = 1 Then

					GoTo weiter_i3

				End If


				weiter_i2:


				If j = 1 And i = 1 And g_start > g_2s_i Then

					l = 0

					Do Until rstce!Tim = ti(i) + 1

						If rstce!gear > g_2s_i + 1 Then

							rstce.edit

							rstce!gear = g_2s_i + 1
							rstce!gear_modification = rstce!gear_modification & "4_k2) check for lower gear ahead during acc, "

							rstce.Update
							m = m + 1

						End If

						l = l + 1

						rstbe.MoveNext
						rstce.MoveNext
						rstde.MoveNext

					Loop

					For h = 1 To l

						rstbe.MovePrevious
						rstce.MovePrevious
						rstde.MovePrevious

					Next h

					If rstce!Tim <> t_start Then

						MsgBox "check for lower gear ahead during acc 4(b1) of annex 2, gear i-2, error at t = " & rstce!Tim

						Stop

					End If

					GoTo weiter_k2

				End If


				If j <= 1 Then

					l = 0

					Do Until rstce!Tim = ti(i) + 1

						If rstce!gear = g_2s_i And rstce!Tim > t_end_i Then

							rstce.edit

							rstce!gear = g_2s_i + 1
							rstce!gear_modification = rstce!gear_modification & "4_k2a) check for lower gear ahead during acc, "

							rstce.Update
							m = m + 1

						ElseIf rstce!gear > g_2s_i + 1 And rstce!Tim > t_end_i Then

							rstce.edit

							rstce!gear = g_2s_i + 1
							rstce!gear_modification = rstce!gear_modification & "4_k2b) check for lower gear ahead during acc, "

							rstce.Update
							m = m + 1

						End If

						l = l + 1

						rstbe.MoveNext
						rstce.MoveNext
						rstde.MoveNext

					Loop

					For h = 1 To l

						rstbe.MovePrevious
						rstce.MovePrevious
						rstde.MovePrevious

					Next h



					If j = 1 Then

						l = 0

						Do Until rstce!Tim = t_end_i + 1

							If rstce!Tim >= ti(0) Then

								rstce.edit


								If rstce!gear > g_2s_i And rstce!g_min <= g_2s_i Then
									rstce!gear = g_2s_i
									rstce!gear_modification = rstce!gear_modification & "4_k1) check for lower gear ahead during acc, "
								ElseIf rstce!gear = g_2s_i Then
									rstce!gear_modification = rstce!gear_modification & "4_k1) gear modification not necessary, "
								End If

								rstce.Update
								m = m + 1

							End If

							l = l + 1

							rstbe.MoveNext
							rstce.MoveNext
							rstde.MoveNext

						Loop

					End If

					GoTo weiter_k2

				Else

					l = 0



					Do Until rstce!Tim = t_end_i + 1


						If rstce!Tim >= ti(0) Then

							rstce.edit


							If rstce!gear > g_2s_i And rstce!g_min <= g_2s_i Then
								rstce!gear = g_2s_i
								rstce!gear_modification = rstce!gear_modification & "4_k1) check for lower gear ahead during acc, "
							ElseIf rstce!gear = g_2s_i Then
								rstce!gear_modification = rstce!gear_modification & "4_k1) gear modification not necessary, "
							End If

							rstce.Update
							m = m + 1

						End If

						l = l + 1

						rstbe.MoveNext
						rstce.MoveNext
						rstde.MoveNext

					Loop

					GoTo weiter_j2

				End If

				weiter_i3:


				l = 0

				Do Until rstce!Tim = ti(1) + 1

					If rstce!gear = g_2s_i And rstce!Tim > ti(0) Then

						rstce.edit

						rstce!gear = g_2s_i + 1
						rstce!gear_modification = rstce!gear_modification & "4_k2a) check for lower gear ahead during acc, "

						rstce.Update
						m = m + 1

					ElseIf rstce!gear > g_2s_i + 1 And rstce!Tim > t_end_i Then

						rstce.edit

						rstce!gear = g_2s_i + 1
						rstce!gear_modification = rstce!gear_modification & "4_k2b) check for lower gear ahead during acc, "

						rstce.Update
						m = m + 1

					End If

					l = l + 1

					rstbe.MoveNext
					rstce.MoveNext
					rstde.MoveNext

				Loop

				GoTo weiter_k2


				weiter_j2:

				If rstce!Tim < t_end_i Then

					Do Until rstce!Tim = t_end_i

						rstbe.MoveNext
						rstce.MoveNext
						rstde.MoveNext

					Loop

				End If

			End If
		End If

		weiter_k2:

		rstbe.MoveNext
		rstce.MoveNext
		rstde.MoveNext


	Loop


'##################################################################################################
' If a one step lower gear is required at a higher vehicle speed during an acceleration phase for more than 1 second within a moving window of 10 seconds,
' the higher gears before shall be corrected to the lower gear. This correction shall not be performed for gear 1.
'4) check for lower gear ahead during acc 4(b) of annex 2
' gear i-1 #########################################################################

	rstbe.MoveFirst
	rstce.MoveFirst
	rstce.MoveNext
	rstde.MoveFirst
	rstde.MoveNext
	rstde.MoveNext

	Do Until rstde.EOF




		If rstde!v > rstce!v And rstce!v >= 1 Then



			l = 0
			k = 0
			i = 0
			j = 0
			t_old_i = 0
			t_old_j = 0
			t_old_k = 0

			For h = 0 To 300

				ti(h) = 0

			Next h

			g_1 = rstce!gear

			If g_1 <= 2 Then

				GoTo weiter_k1

			Else

				t_start = rstce!Tim


				Do Until rstde!v <= rstce!v Or rstce!g_min > g_1

					t_end_j = rstce!Tim

					If rstce!gear = g_1 - 1 And rstce!gear > 0 Then

						i = i + 1

						If i > 300 Then
							MsgBox "i = " & i & " at t = " & rstce!Tim
							Stop
						End If

						ti(i) = rstce!Tim
						g_2s_i = rstce!gear
						t_end_i = rstce!Tim
						t_end_j = rstce!Tim


					End If

					l = l + 1

					rstbe.MoveNext
					rstce.MoveNext
					rstde.MoveNext

				Loop

				For h = 1 To l

					rstbe.MovePrevious
					rstce.MovePrevious
					rstde.MovePrevious

				Next h

				If rstce!Tim <> t_start Then

					MsgBox "check for lower gear ahead during acc 4(b1) of annex 2, gear i-1, error at t = " & rstce!Tim

					Stop

				End If

				l = 0


				If i > 0 Then

					If rstce!Tim < ti(1) Then

						Do Until rstce!Tim = ti(1)

							rstbe.MoveNext
							rstce.MoveNext
							rstde.MoveNext

						Loop

					ElseIf rstce!Tim > ti(1) Then

						Do Until rstce!Tim = ti(1)

							rstbe.MovePrevious
							rstce.MovePrevious
							rstde.MovePrevious

						Loop

					End If

					rstbe.MovePrevious
					rstce.MovePrevious
					rstde.MovePrevious

					If rstbe!v < rstce!v Then

						Do Until rstce!gear = g_2s_i Or rstbe!v >= rstce!v

							rstbe.MovePrevious
							rstce.MovePrevious
							rstde.MovePrevious

						Loop


					End If

					ti(0) = rstce!Tim
					g_start = rstce!gear

					If rstce!Tim < t_start Then

						t_start = rstce!Tim

					End If



				Else

					GoTo weiter_k1

				End If



				j = 0

				For h = 1 To i

					If ti(i - h + 1) - ti(i - h) <= 9 Then

						j = i - h + 1
						GoTo weiter_i1

					Else


						t_end_i = ti(i - h)

					End If

				Next h



				weiter_i1:


				If j = 1 And i = 1 Then


					If g_start > g_2s_i Then

						l = 0



						Do Until rstce!Tim = ti(i) + 1

							If rstce!gear = g_2s_i Then

								rstce.edit

								rstce!gear = g_2s_i + 1
								rstce!gear_modification = rstce!gear_modification & "4_i2) check for lower gear ahead during acc, "

								rstce.Update
								m = m + 1

							End If

							l = l + 1

							rstbe.MoveNext
							rstce.MoveNext
							rstde.MoveNext

						Loop


						GoTo weiter_k1

					Else

						l = 0

						Do Until rstce!Tim = ti(i) + 1



							rstce.edit

							If rstce!gear > g_2s_i And rstce!g_min <= g_2s_i Then
								rstce!gear = g_2s_i
								rstce!gear_modification = rstce!gear_modification & "4_i3) check for lower gear ahead during acc, "
							ElseIf rstce!gear = g_2s_i Then
								rstce!gear_modification = rstce!gear_modification & "4_i3) gear modification not necessary, "
							End If


							rstce.Update
							m = m + 1


							l = l + 1

							rstbe.MoveNext
							rstce.MoveNext
							rstde.MoveNext

						Loop

						GoTo weiter_k1

					End If

				ElseIf j = 0 Then


					l = 0


					Do Until rstce!Tim = ti(i) + 1


						If rstce!gear = g_2s_i And rstce!Tim > ti(0) Then

							rstce.edit

							rstce!gear = g_2s_i + 1
							rstce!gear_modification = rstce!gear_modification & "4_i2) check for lower gear ahead during acc, "

							rstce.Update
							m = m + 1

						End If

						l = l + 1

						rstbe.MoveNext
						rstce.MoveNext
						rstde.MoveNext

					Loop

					GoTo weiter_k1


				Else

					l = 0

					Do Until rstce!Tim = ti(i) + 1

						If rstce!gear = g_2s_i And rstce!Tim > t_end_i Then

							rstce.edit

							rstce!gear = g_2s_i + 1
							rstce!gear_modification = rstce!gear_modification & "4_i2) check for lower gear ahead during acc, "

							rstce.Update
							m = m + 1

						End If

						l = l + 1

						rstbe.MoveNext
						rstce.MoveNext
						rstde.MoveNext

					Loop

					For h = 1 To l

						rstbe.MovePrevious
						rstce.MovePrevious
						rstde.MovePrevious

					Next h


					l = 0

					Do Until rstce!Tim = t_end_i + 1



						rstce.edit


						If rstce!gear > g_2s_i And rstce!g_min <= g_2s_i Then
							rstce!gear = g_2s_i
							rstce!gear_modification = rstce!gear_modification & "4_i1) check for lower gear ahead during acc, "
						ElseIf rstce!gear = g_2s_i Then
							rstce!gear_modification = rstce!gear_modification & "4_i1) gear modification not necessary, "
						End If

						rstce.Update
						m = m + 1

						l = l + 1

						rstbe.MoveNext
						rstce.MoveNext
						rstde.MoveNext

					Loop


					GoTo weiter_j1

				End If


				weiter_j1:

				If rstce!Tim < ti(i) Then

					Do Until rstce!Tim = ti(i)

						rstbe.MoveNext
						rstce.MoveNext
						rstde.MoveNext

					Loop

				End If

			End If
		End If

		weiter_k1:

		rstbe.MoveNext
		rstce.MoveNext
		rstde.MoveNext


	Loop




	Text253 = m

	gearshift_calculation2_4c

'Stop

	gearshift_calculation2_4df
'Stop

	gearshift_calculation2b


'##################################################################################################################



	If Forms![F calc gearshifts single vehicle].[Kontroll164] = False And m > 0 Then

		MsgBox "Modification Lap " & P & ", number of modifications = " & Text253

	End If

	If m > 0 Then

		P = P + 1

'Stop

		If m_old < 2 Then

			GoTo weiter3

		End If

	End If

'Stop




'################################################################################################################################
' Corrections according to annex 2, paragraph 5(b) ##############################################################################
' 4b2) corr 6644 -> 6044 at transitions from dec to acc


	rstbe.MoveFirst
	rstce.MoveFirst
	rstce.MoveNext
	rstde.MoveFirst
	rstde.MoveNext
	rstde.MoveNext
	rstee.MoveFirst
	rstee.MoveNext
	rstee.MoveNext
	rstee.MoveNext


	Do Until rstee.EOF

		If rstbe!v >= rstce!v And rstce!v >= rstde!v And rstee!v > rstde!v And rstbe!gear = rstce!gear And rstde!gear = rstee!gear And rstce!gear >= rstde!gear + 2 Then

			rstce.edit

			rstce!gear = 0
			rstce!clutch = "disengaged"
			rstce!gear_modification = rstce!gear_modification & "4b2) corr 6644 -> 6044 at transitions from dec to acc, "

			rstce.Update
			m = m + 1



		End If

		rstbe.MoveNext
		rstce.MoveNext
		rstde.MoveNext
		rstee.MoveNext

	Loop


'#############################################################################################################################
' 7c) suppress gear 0 during deceleration according to annex 2, paragraph 4(f)

	If Ko244 = True Then

		rstbe.MoveFirst

		rstce.MoveFirst
		rstce.MoveNext

		rstde.MoveFirst
		rstde.MoveNext
		rstde.MoveNext

		Do Until rstde.EOF

			If rstbe!gear >= rstde!gear + 2 And rstde!gear > 0 And rstce!gear = 0 And rstbe!gear <= rstde!gear + 3 Then

				rstce.edit
				If rstce!g_min <= rstde!gear Then
					rstce!gear = rstde!gear
					rstce!clutch = "engaged"
					rstce!nc = rstde!nc * rstce!v / rstde!v
					rstce!gear_modification = rstce!gear_modification & "7c) suppress gear 0 during downshifts, "
					m = m + 1
				Else
					rstce!gear_modification = rstce!gear_modification & "7c) Necessary gear modification not possible, "
					n = n + 1
				End If
				rstce.Update

			End If

			rstbe.MoveNext
			rstce.MoveNext
			rstde.MoveNext

		Loop

	End If







	rstie.Close
	rstke.Close
	rstae.Close
	rstbe.Close
	rstce.Close
	rstde.Close
	rstee.Close
	rstfe.Close
	rstge.Close
	rsthe.Close

	weiter_NEDC_2:




End Sub



Private Sub Kombinationsfeld17_AfterUpdate()

	Dim wrkWS1
	Dim dbsDB1
	Dim rstce, rstbe
	Dim rstde, rstae
	Dim rstee
	Dim aa As Double, bb As Double, cc As Double, dd As Double, ee As Double, dt As Single, t As Single, n As Integer, m As Integer

	m = 0
	n = 0

	t = 0



	Set wrkWS1 = DBEngine.Workspaces(0)
	Set dbsDB1 = wrkWS1.Databases(0)
'...


	Set rstae = dbsDB1.OpenRecordset("ST_safety_margin_Pwot", DB_OPEN_DYNASET)
	rstae.MoveFirst
	rstae.edit
	rstae!safety_margin_Pwot = Kombinationsfeld17
	rstae.Update
	rstae.Close

	Kombinationsfeld33.Enabled = True


End Sub




Private Sub Kombinationsfeld33_AfterUpdate()

	Dim wrkWS1
	Dim dbsDB1
	Dim rstce, rstbe
	Dim rstde, rstae
	Dim rstee
	Dim aa As Double, bb As Double, cc As Double, dd As Double, ee As Double, dt As Single, t As Single, n As Integer, m As Integer

	m = 0
	n = 0

	t = 0



	Set wrkWS1 = DBEngine.Workspaces(0)
	Set dbsDB1 = wrkWS1.Databases(0)
'...


	Set rstae = dbsDB1.OpenRecordset("ST_n_norm_max", DB_OPEN_DYNASET)
	rstae.MoveFirst
	rstae.edit
	rstae!n_norm_max = Kombinationsfeld33
	rstae.Update
	rstae.Close


	Befehl28.Enabled = True


End Sub

Private Sub Kombinationsfeld43_AfterUpdate()

	Dim wrkWS1
	Dim dbsDB1
	Dim rstce, rstbe
	Dim rstde, rstae
	Dim rstee
	Dim aa As Double, bb As Double, cc As Double, dd As Double, ee As Double, dt As Single, t As Single, n As Integer, m As Integer

	m = 0
	n = 0

	t = 0



	Set wrkWS1 = DBEngine.Workspaces(0)
	Set dbsDB1 = wrkWS1.Databases(0)
'...


	Set rstae = dbsDB1.OpenRecordset("ST_cycle_no", DB_OPEN_DYNASET)
	rstae.MoveFirst
	rstae.edit
	rstae!cycle_no = Kombinationsfeld43
	rstae.Update
	rstae.Close

	Kombinationsfeld12.Enabled = True
	Kombinationsfeld12 = ""

	Me.Requery



End Sub

Private Sub Kombinationsfeld52_AfterUpdate()

	Dim wrkWS1
	Dim dbsDB1
	Dim rstce, rstbe
	Dim rstde, rstae
	Dim rstee
	Dim aa As Double, bb As Double, cc As Double, dd As Double, ee As Double, dt As Single, t As Single, n As Integer, m As Integer

	m = 0
	n = 0

	t = 0



	Set wrkWS1 = DBEngine.Workspaces(0)
	Set dbsDB1 = wrkWS1.Databases(0)
'...


	Set rstae = dbsDB1.OpenRecordset("ST_WLTC_version", DB_OPEN_DYNASET)
	rstae.MoveFirst
	rstae.edit
	rstae!class = Kombinationsfeld52
	rstae.Update
	rstae.Close



'If Abs(DLookup("[class]", "vehicle_info", "[vehicle_no] = " & Kombinationsfeld12) - Kombinationsfeld52) > 1 Then

'MsgBox "The chosen vehicle class is 2 classes away from the appropriate class for the chosen vehicle_no!"

'End If


	Kombinationsfeld64.Visible = True
	Bezeichnungsfeld66.Visible = True




End Sub

Private Sub Kombinationsfeld64_AfterUpdate()
	Dim wrkWS1
	Dim dbsDB1
	Dim rstce, rstbe
	Dim rstde, rstae
	Dim rstee
	Dim aa As Double, bb As Double, cc As Double, dd As Double, ee As Double, dt As Single, t As Single, n As Integer, m As Integer
	Dim n_min_drive_fact As Double, n_min_2_fact As Double
	Dim rated_speed As Integer, idling_speed As Integer, n_min_drive As Integer
	Dim n_min_2 As Integer, n_min_drive_set As Integer

	m = 0
	n = 0

	t = 0






	Set wrkWS1 = DBEngine.Workspaces(0)
	Set dbsDB1 = wrkWS1.Databases(0)
'...



	Set rstae = dbsDB1.OpenRecordset("ST_downscaling", DB_OPEN_DYNASET)
	rstae.MoveFirst
	rstae.edit
	rstae!downscale_factor_acc = Kombinationsfeld64
	rstae.Update
	rstae.Close





End Sub

Private Sub Kombinationsfeld82_AfterUpdate()
	Dim wrkWS1
	Dim dbsDB1
	Dim rstce, rstbe
	Dim rstde, rstae
	Dim rstee
	Dim aa As Double, bb As Double, cc As Double, dd As Double, ee As Double, dt As Single, t As Single, n As Integer, m As Integer

	m = 0
	n = 0

	t = 0



	Set wrkWS1 = DBEngine.Workspaces(0)
	Set dbsDB1 = wrkWS1.Databases(0)
'...


	Set rstae = dbsDB1.OpenRecordset("ST_safety_margin_Pwot", DB_OPEN_DYNASET)
	rstae.MoveFirst
	rstae.edit
	rstae!y_1 = Kombinationsfeld82
	rstae.Update
	rstae.Close


	DoCmd.OpenQuery "A TB_Pwot_norm del"
	DoCmd.OpenQuery "A TB_Pwot_norm"

End Sub

Private Sub Kombinationsfeld87_AfterUpdate()
	Set wrkWS1 = DBEngine.Workspaces(0)
	Set dbsDB1 = wrkWS1.Databases(0)
'...


	Set rstae = dbsDB1.OpenRecordset("ST_v_max_safety_margin", DB_OPEN_DYNASET)
	rstae.MoveFirst
	rstae.edit
	rstae!safety_margin = Kombinationsfeld87
	rstae.Update
	rstae.Close

	Set rstae = dbsDB1.OpenRecordset("ST_cap", DB_OPEN_DYNASET)
	rstae.MoveFirst
	rstae.edit
	rstae!v_cap = (1 - DLookup("[safety_margin]", "ST_v_max_safety_margin")) * DLookup("[v_max]", "ST_vehicle_info")
	rstae.Update
	rstae.Close

End Sub

Private Sub Kontrollk130_AfterUpdate()
	If Kontrollk130 = False Then

		Text132.Visible = False
		Text128.Visible = False
		Bezeichnungsfeld129.Visible = False
		Bezeichnungsfeld133.Visible = False
		Bezeichnungsfeld134.Visible = False

	Else

		Text132.Visible = True
		Text128.Visible = True
		Bezeichnungsfeld129.Visible = True
		Bezeichnungsfeld133.Visible = True
		Bezeichnungsfeld134.Visible = True
		Text132 = ""
		Text128 = ""

	End If



End Sub



Private Sub Kontr205_AfterUpdate()

	Kontr205 = False

	DoCmd.OpenQuery "A vehicle_info check", ReadOnly



End Sub



Private Sub Kontr226_AfterUpdate()

	Kombinationsfeld12 = Null

End Sub

Private Sub Kontroll137_AfterUpdate()

	If Kontroll137 = False Then

		Text140.Visible = False
		Text146.Visible = False
		Text148.Visible = False

		Be141.Visible = False
		Be147.Visible = False
		Be149.Visible = False

		Befehl177.Visible = False

	Else

		Text140.Visible = True
		Text146.Visible = True
		Text148.Visible = True

		Be141.Visible = True
		Be147.Visible = True
		Be149.Visible = True

		Befehl177.Visible = True

	End If

End Sub

Private Sub Kontroll164_AfterUpdate()

	If Kontroll164 = False Then

		Bezeichnungsfeld165.Visible = False
		Befehl107.Visible = False
		Be92.Visible = False
		Be93.Visible = False
		Be110.Visible = False
		Text91.Visible = False
		Text92.Visible = False
		Text109.Visible = False

	Else

		Bezeichnungsfeld165.Visible = True
		Befehl107.Visible = True
		Be92.Visible = True
		Be93.Visible = True
		Be110.Visible = True
		Text91.Visible = True
		Text92.Visible = True
		Text109.Visible = True

	End If

End Sub

Private Sub Option184_GotFocus()

End Sub




Private Sub Rahmen36_AfterUpdate()

	Dim wrkWS1
	Dim dbsDB1
	Dim rstae



	Set wrkWS1 = DBEngine.Workspaces(0)
	Set dbsDB1 = wrkWS1.Databases(0)

	Ko244.Visible = False
	Ko246.Visible = False
	Ko248.Visible = False
	Ko250.Visible = False
	Be251.Visible = False

	Ko179.Visible = False
	Ko219.Visible = False
	Ko228.Visible = False
	Ko236.Visible = False
	Be180.Visible = False
	Text181.Visible = False
	Text221.Visible = False
	Text230.Visible = False
	Text234.Visible = False
	Be182.Visible = False
	Be222.Visible = False
	Be231.Visible = False
	Be235.Visible = False
	Ko195.Visible = False
	Be196.Visible = False
	Text174.Visible = False
	Text155.Visible = False
	Text238.Visible = False
	Text151.Visible = False
	Text157.Visible = False
	Text152.Visible = False
	Text71.Visible = False
	Text168.Visible = False
	Text170.Visible = False
	Text161.Visible = False
	Text159.Visible = False
	Text224.Visible = False
	Be103.Visible = False
	Be175.Visible = False
	Be156.Visible = False
	Be239.Visible = False
	Be153.Visible = False
	Be158.Visible = False
	Be154.Visible = False
	Be72.Visible = False
	Be171.Visible = False
	Be169.Visible = False
	Be162.Visible = False
	Be160.Visible = False
	Be225.Visible = False
	s108.Visible = False
	Be243.Visible = False
	Text242.Visible = False
	Be198.Visible = False
	Text197.Visible = False
	Ko195 = False

	If Rahmen36 = 1 Then

		Rahmen183.Visible = False
		Kombinationsfeld12.Enabled = True
		Kombinationsfeld43.Visible = False
		Bezeichnungsfeld44.Visible = False
		Kontr226 = True
		Kontr226.Visible = False

		Be198.Visible = False
		Text197 = ""
		Text197.Visible = False

	ElseIf Rahmen36 = 2 Then

		Kombinationsfeld12.Enabled = True

		Rahmen183.Visible = False
		Kombinationsfeld43.Visible = False
		Bezeichnungsfeld44.Visible = False
		Kontr226 = True
		Kontr226.Visible = False
		Be198.Visible = False
		Text197 = ""
		Text197.Visible = False

	ElseIf Rahmen36 = 4 Then

		Kombinationsfeld12.Enabled = False

		Rahmen183.Visible = False
		Kombinationsfeld43.Visible = True
		Kombinationsfeld43 = Null
		Bezeichnungsfeld44.Visible = True
		Kontr226.Visible = True
		Kontr226 = False
		Be198.Visible = False
		Text197 = ""
		Text197.Visible = False

	ElseIf Rahmen36 = 3 Then

		Kombinationsfeld12.Enabled = True


		Be198.Visible = False
		Text197 = ""
		Text197.Visible = False
		Kontr226 = False
		Kontr226.Visible = False
		Rahmen183.Visible = True
		Rahmen183 = False

		Kombinationsfeld43.Visible = False
		Bezeichnungsfeld44.Visible = False



'...


		Set rstae = dbsDB1.OpenRecordset("ST_cycle_no", DB_OPEN_DYNASET)
		rstae.MoveFirst
		rstae.edit
		rstae!cycle_no = 1
		rstae.Update
		rstae.Close




	Else

	End If

	Set rstae = dbsDB1.OpenRecordset("ST_vehicle_info", DB_OPEN_DYNASET)
	rstae.MoveFirst
	rstae.edit

	If Rahmen36 = 1 Then
		rstae!Cycle = "WLTC"
	ElseIf Rahmen36 = 2 Then
		rstae!Cycle = "EVAP purge"
	ElseIf Rahmen36 = 3 Then
		rstae!Cycle = "NEDC"
	ElseIf Rahmen36 = 4 Then
		rstae!Cycle = "other cycle"
	End If
	rstae.Update
	rstae.Close

	Kombinationsfeld12 = ""

	Me.Requery

End Sub




Public Sub check_gear_use_calculation()
	Dim wrkWS1
	Dim dbsDB1
	Dim rstce, rstbe
	Dim rstde, rstae
	Dim rstee, rstfe, rstge, rsthe, rstie
	Dim aa As Double, bb As Double, cc As Double, dd As Double, ee As Double, dt As Single, t As Single, n As Integer, m As Integer, k As Integer
	Dim g_acc As Byte, g_cruise As Byte, g_dec As Byte, n_norm_max As Double, P_res As Double, j As Integer, i As Integer
	Dim n_norm_1 As Double, n_norm_2 As Double, n_norm_3 As Double, n_norm_4 As Double, n_norm_5 As Double, n_norm_6 As Double, n_norm As Double
	Dim P_norm_1 As Double, P_norm_2 As Double, P_norm_3 As Double, P_norm_4 As Double, P_norm_5 As Double, P_norm_6 As Double
	Dim v_1 As Double, v_2 As Double, P_1 As Double, P_2 As Double, g_1 As Byte, g_2 As Byte, P_a As Double
	Dim a_1 As Double, a_2 As Double, a_3 As Double, a_4 As Double, a_5 As Double, a_6 As Double



	Set wrkWS1 = DBEngine.Workspaces(0)
	Set dbsDB1 = wrkWS1.Databases(0)
'...

	Text20 = "check gear use calculation"
	Me.Repaint


'DoCmd.OpenQuery "A ST_vehicle_info del"
'DoCmd.OpenQuery "A ST_vehicle_info"

	DoCmd.OpenQuery "A gearshift_table gearshift_not_ok_Ste false"

	n = 0
	m = 0
	k = 0
	j = 0

	Set rstbe = dbsDB1.OpenRecordset("A gearshift_table sort", DB_OPEN_DYNASET)
	Set rstce = dbsDB1.OpenRecordset("A gearshift_table sort", DB_OPEN_DYNASET)
	Set rstde = dbsDB1.OpenRecordset("A gearshift_table sort", DB_OPEN_DYNASET)
	Set rstee = dbsDB1.OpenRecordset("A gearshift_table sort", DB_OPEN_DYNASET)
	Set rstfe = dbsDB1.OpenRecordset("A gearshift_table sort", DB_OPEN_DYNASET)
	Set rstge = dbsDB1.OpenRecordset("A gearshift_table sort", DB_OPEN_DYNASET)
	Set rsthe = dbsDB1.OpenRecordset("A gearshift_table sort", DB_OPEN_DYNASET)


	weiter3:

	rstbe.MoveFirst

	rstce.MoveFirst
	rstce.MoveNext

	rstde.MoveFirst
	rstde.MoveNext
	rstde.MoveNext


	Do Until rstde.EOF

'Text7 = rstbe!part
'Text15 = rstbe!tim
'Me.Repaint


'1) ########################################################################################################################
'1) 232 -> 222, 323 -> 333

		If (rstce!gear = rstbe!gear + 1 And rstde!gear = rstbe!gear) Or (rstce!gear = rstbe!gear - 1 And rstde!gear = rstbe!gear) Then

			rstce.edit
			rstce!error_description = rstce!error_description & "1) 232 -> 222, 323 -> 333, "
			rstce.Update

		End If



		rstbe.MoveNext
		rstce.MoveNext
		rstde.MoveNext

	Loop

'#######################################################################################################


	rstbe.MoveFirst

	rstce.MoveFirst
	rstce.MoveNext

	rstde.MoveFirst
	rstde.MoveNext
	rstde.MoveNext

	rstee.MoveFirst
	rstee.MoveNext
	rstee.MoveNext
	rstee.MoveNext


	Do Until rstee.EOF

'Text7 = rstbe!part
'Text15 = rstbe!tim
'Me.Repaint

'2) #############################################################################################
'2) 6546 -> 6556

		If rstce!gear = rstbe!gear - 1 And rstde!gear = rstce!gear - 1 And rstee!gear = rstbe!gear Then

			rstde.edit
			rstde!error_description = rstde!error_description & "2) 6546 -> 6556, "
			rstde.Update

		End If



		rstbe.MoveNext
		rstce.MoveNext
		rstde.MoveNext
		rstee.MoveNext


	Loop



'######################################################################################################



	rstbe.MoveFirst

	rstce.MoveFirst
	rstce.MoveNext

	rstde.MoveFirst
	rstde.MoveNext
	rstde.MoveNext


	Do Until rstde.EOF

'Text7 = rstbe!part
'Text15 = rstbe!tim
'Me.Repaint

'4) ##############################################################################################
'4) 133 -> 122

		If rstce!gear > rstbe!gear + 1 And rstde!gear = rstce!gear And rstce!v > rstbe!v Then

			rstce.edit
			rstce!error_description = rstce!error_description & "4) 133 -> 122, "
			rstce.Update

			rstde.edit
			rstde!error_description = rstde!error_description & "4) 133 -> 122, "
			rstde.Update


		End If

'5) ###############################################################################################

'5) 123 -> 122

		If rstce!gear = rstbe!gear + 1 And rstde!gear = rstce!gear + 1 Then



			rstde.edit
			rstde!error_description = rstde!error_description & "5) 123 -> 122, "
			rstde.Update


		End If


'6) ####################################################################################################

'6) 232 -> 222, 323 -> 333

		If (rstce!gear = rstbe!gear + 1 And rstde!gear <= rstbe!gear) Or (rstce!gear = rstbe!gear - 1 And rstde!gear = rstbe!gear) Then

			rstce.edit
			rstce!error_description = rstce!error_description & "6) 232 -> 222, 323 -> 333, "
			rstce.Update

		End If

'7) ####################################################################################################

'7) 321 -> 311

		If rstce!gear = rstbe!gear - 1 And rstde!gear = rstce!gear - 1 Then

			rstce.edit
			rstce!error_description = rstce!error_description & "7) 321 -> 311, "
			rstce.Update

		End If


		rstbe.MoveNext
		rstce.MoveNext
		rstde.MoveNext

	Loop

'GoTo weiter

'################################################################################################################

	weiter4:

	rstbe.MoveFirst

	rstce.MoveFirst
	rstce.MoveNext

	rstde.MoveFirst
	rstde.MoveNext
	rstde.MoveNext

	rstee.MoveFirst
	rstee.MoveNext
	rstee.MoveNext
	rstee.MoveNext


	Do Until rstee.EOF

'Text7 = rstbe!part
'Text15 = rstbe!tim
'Me.Repaint

'8) ############################################################################################################

'8) 1223 -> 1222

		If rstce!gear = rstbe!gear + 1 And rstde!gear = rstce!gear And rstee!gear > rstde!gear And rstce!v > rstbe!v Then

			rstee.edit
			rstee!error_description = rstee!error_description & "8) 1223 -> 1222, "
			rstee.Update

		End If

'9) #############################################################################################################

'9) 3223 -> 3222

		If rstce!gear = rstbe!gear - 1 And rstde!gear = rstce!gear And rstee!gear = rstbe!gear Then

			rstee.edit
			rstee!error_description = rstee!error_description & "9) 3223 -> 3222, "
			rstee.Update

		End If

'10) ############################################################################################################

'10) 3443 -> 3333

		If rstce!gear = rstbe!gear + 1 And rstde!gear = rstce!gear And rstee!gear <= rstbe!gear Then

			rstce.edit
			rstce!error_description = rstce!error_description & "10) 3443 -> 3333, "
			rstce.Update

			rstde.edit
			rstde!error_description = rstde!error_description & "10) 3443 -> 3333, "
			rstde.Update

		End If

'11) ##############################################################################################################

'11) 2244 -> 2233

		If rstce!gear = rstbe!gear And rstde!gear = rstce!gear + 2 And rstee!gear = rstde!gear And rstde!v > rstce!v Then

			rstee.edit
			rstee!error_description = rstee!error_description & "11) 2244 -> 2233, "
			rstee.Update

			rstde.edit
			rstde!error_description = rstde!error_description & "11) 2244 -> 2233, "
			rstde.Update

		End If


		rstbe.MoveNext
		rstce.MoveNext
		rstde.MoveNext
		rstee.MoveNext


	Loop

'###################################################################################################################

	weiter5:

	rstbe.MoveFirst

	rstce.MoveFirst
	rstce.MoveNext

	rstde.MoveFirst
	rstde.MoveNext
	rstde.MoveNext

	rstee.MoveFirst
	rstee.MoveNext
	rstee.MoveNext
	rstee.MoveNext

	rstfe.MoveFirst
	rstfe.MoveNext
	rstfe.MoveNext
	rstfe.MoveNext
	rstfe.MoveNext

	Do Until rstfe.EOF

'Text7 = rstbe!part
'Text15 = rstbe!tim
'Me.Repaint

'12) ######################################################################################################

'12) 43300 -> 40000

		If rstce!gear < rstbe!gear - 1 And rstce!gear > 0 And rstde!gear < rstbe!gear And rstee!gear = 0 And rstee!gear = rstfe!gear Then

			rstce.edit
			rstce!error_description = rstce!error_description & "12) 43300 -> 40000 or 43200 -> 40000, "
			rstce.Update

			rstde.edit
			rstde!error_description = rstde!error_description & "12) 43300 -> 40000 or 43200 -> 40000, "
			rstde.Update

		End If

'13) ############################################################################################################

'13) 33110 -> 33000, 33220 -> 33000

		If rstce!gear = rstbe!gear And rstde!gear < rstce!gear And rstee!gear = rstde!gear And rstde!gear > 0 And rstfe!gear = 0 And rstfe!v < 1 Then

			rstee.edit
			rstee!error_description = rstee!error_description & "13) 33110 -> 33000, 33220 -> 33000, "
			rstee.Update

			rstde.edit
			rstde!error_description = rstde!error_description & "13) 33110 -> 33000, 33220 -> 33000, "
			rstde.Update

		End If

'14) #############################################################################################################

'14) 34443 -> 33333

		If rstbe!gear > 0 And rstce!gear > rstbe!gear And rstde!gear > rstbe!gear And rstee!gear > rstbe!gear And rstfe!gear <= rstbe!gear Then

			rstce.edit
			rstce!error_description = rstce!error_description & "14) 34443 -> 33333, "
			rstce.Update

			rstde.edit
			rstde!error_description = rstde!error_description & "14) 34443 -> 33333, "
			rstde.Update

			rstee.edit
			rstee!error_description = rstee!error_description & "14) 34443 -> 33333, "
			rstee.Update

		End If



		rstbe.MoveNext
		rstce.MoveNext
		rstde.MoveNext
		rstee.MoveNext
		rstfe.MoveNext

	Loop

'##########################################################################################################

	weiter6:

	rstbe.MoveFirst

	rstce.MoveFirst
	rstce.MoveNext

	rstde.MoveFirst
	rstde.MoveNext
	rstde.MoveNext

	rstee.MoveFirst
	rstee.MoveNext
	rstee.MoveNext
	rstee.MoveNext

	rstfe.MoveFirst
	rstfe.MoveNext
	rstfe.MoveNext
	rstfe.MoveNext
	rstfe.MoveNext

	rstge.MoveFirst
	rstge.MoveNext
	rstge.MoveNext
	rstge.MoveNext
	rstge.MoveNext
	rstge.MoveNext


	Do Until rstge.EOF

'Text7 = rstbe!part
'Text15 = rstbe!tim
'Me.Repaint

'15) #####################################################################################################################

'15) 344443 -> 333333

		If rstbe!gear > 0 And rstce!gear > rstbe!gear And rstde!gear > rstbe!gear And rstee!gear > rstbe!gear And rstfe!gear > rstbe!gear And rstge!gear <= rstbe!gear Then

			rstce.edit
			rstce!error_description = rstce!error_description & "15) 344443 -> 333333, "
			rstce.Update

			rstde.edit
			rstde!error_description = rstde!error_description & "15) 344443 -> 333333, "
			rstde.Update

			rstee.edit
			rstee!error_description = rstee!error_description & "15) 344443 -> 333333, "
			rstee.Update

			rstfe.edit
			rstfe!error_description = rstfe!error_description & "15) 344443 -> 333333, "
			rstfe.Update


		End If

'16) ####################################################################################################################

'16) 553322 -> 550022 or 550222

		If rstce!gear = rstbe!gear And rstde!gear < rstbe!gear And rstee!gear = rstde!gear And rstfe!gear < rstde!gear And rstge!gear = rstfe!gear Then

			rstde.edit
			rstde!error_description = rstde!error_description & "16) 553322 -> 550022 or 550222, "
			rstde.Update

			rstee.edit
			rstee!error_description = rstee!error_description & "16) 553322 -> 550022 or 550222, "
			rstee.Update


		End If

'17) #####################################################################################################################

'17) 554332 -> 550332 or 553332

		If rstce!gear = rstbe!gear And rstde!gear < rstbe!gear And rstee!gear < rstde!gear And rstfe!gear < rstde!gear And rstge!gear < rstde!gear And rstge!gear > 0 Then

			rstde.edit
			rstde!error_description = rstde!error_description & "17) 554332 -> 550332 or 553332, "
			rstde.Update


		End If


'18) ####################################################################################################################

'18) 000123 -> 000111

		If rstce!gear = rstbe!gear And rstde!gear = rstbe!gear And rstee!gear > rstde!gear And rstfe!gear > rstde!gear And rstge!gear > rstde!gear And rstge!gear > rstfe!gear Then

			rstee.edit
			rstee!error_description = rstee!error_description & "18) 000123 -> 000111, "
			rstee.Update

			rstfe.edit
			rstfe!error_description = rstfe!error_description & "18) 000123 -> 000111, "
			rstfe.Update

			rstge.edit
			rstge!error_description = rstge!error_description & "18) 000123 -> 000111, "
			rstge.Update

		End If

'19) #####################################################################################################################

'19) 112224 -> 112223

		If rstce!gear = rstbe!gear And rstde!gear = rstbe!gear + 1 And rstee!gear = rstde!gear And rstfe!gear = rstde!gear And rstge!gear > rstde!gear + 1 And rstbe!gear > 0 Then


			rstge.edit
			rstge!error_description = rstge!error_description & "19) 112224 -> 112223, "
			rstge.Update

		End If

'20) #######################################################################################################################

'20) 122234 -> 122233

		If rstce!gear = rstbe!gear + 1 And rstde!gear = rstbe!gear + 1 And rstee!gear = rstce!gear And rstfe!gear = rstce!gear + 1 And rstge!gear > rstfe!gear And rstbe!gear > 0 Then


			rstge.edit
			rstge!error_description = rstge!error_description & "20) 122234 -> 122233, "
			rstge.Update

		End If

'21) #########################################################################################################################

'21) 001113 -> 001112

		If rstce!gear = rstbe!gear And rstde!gear = rstbe!gear + 1 And rstee!gear = rstde!gear And rstfe!gear = rstde!gear And rstge!gear > rstde!gear And rstbe!gear = 0 And rstbe!v < 1 Then


			rstge.edit
			rstge!error_description = rstge!error_description & "21) 001113 -> 001112, "
			rstge.Update

		End If

'22) ##########################################################################################################################

'22) 011123 -> 011122

		If rstce!gear = rstbe!gear + 1 And rstde!gear = rstbe!gear + 1 And rstee!gear = rstce!gear And rstfe!gear = rstce!gear + 1 And rstge!gear > rstfe!gear And rstbe!gear = 0 And rstbe!v < 1 Then


			rstge.edit
			rstge!error_description = rstge!error_description & "22) 011123 -> 011122, "
			rstge.Update

		End If

'23) ###########################################################################################################################

'23) 333556 -> 333444

		If rstce!gear = rstbe!gear And rstde!gear = rstbe!gear And rstee!gear > rstce!gear + 1 And rstfe!gear > rstce!gear + 1 And rstge!gear > rstce!gear + 1 And rstce!v > rstbe!v And rstde!v > rstce!v And rstee!v <= rstde!v And rstfe!v <= rstee!v And rstge!v <= rstfe!v Then

			rstee.edit
			rstee!error_description = rstee!error_description & "23) 333556 -> 333444, "
			rstee.Update

			rstfe.edit
			rstfe!error_description = rstfe!error_description & "23) 333556 -> 333444, "
			rstfe.Update

			rstge.edit
			rstge!error_description = rstge!error_description & "23) 333556 -> 333444, "
			rstge.Update

		End If





		rstbe.MoveNext
		rstce.MoveNext
		rstde.MoveNext
		rstee.MoveNext
		rstfe.MoveNext
		rstge.MoveNext

	Loop

'##################################################################################################################


	weiter7:

	rstbe.MoveFirst

	rstce.MoveFirst
	rstce.MoveNext

	rstde.MoveFirst
	rstde.MoveNext
	rstde.MoveNext

	rstee.MoveFirst
	rstee.MoveNext
	rstee.MoveNext
	rstee.MoveNext

	rstfe.MoveFirst
	rstfe.MoveNext
	rstfe.MoveNext
	rstfe.MoveNext
	rstfe.MoveNext

	rstge.MoveFirst
	rstge.MoveNext
	rstge.MoveNext
	rstge.MoveNext
	rstge.MoveNext
	rstge.MoveNext

	rsthe.MoveFirst
	rsthe.MoveNext
	rsthe.MoveNext
	rsthe.MoveNext
	rsthe.MoveNext
	rsthe.MoveNext
	rsthe.MoveNext

	Do Until rsthe.EOF

'Text7 = rstbe!part
'Text15 = rstbe!tim
'Me.Repaint

'24) ##################################################################################################################

'24) 344443 -> 333333

		If rstbe!gear > 0 And rstce!gear > rstbe!gear And rstde!gear > rstbe!gear And rstee!gear > rstbe!gear And rstfe!gear > rstbe!gear And rstge!gear <= rstbe!gear Then

			rstce.edit
			rstce!error_description = rstce!error_description & "24) 344443 -> 333333, "
			rstce.Update

			rstde.edit
			rstde!error_description = rstde!error_description & "24) 344443 -> 333333, "
			rstde.Update

			rstee.edit
			rstee!error_description = rstee!error_description & "24) 344443 -> 333333, "
			rstee.Update

			rstfe.edit
			rstfe!error_description = rstfe!error_description & "24) 344443 -> 333333, "
			rstfe.Update

		End If

'25) #######################################################################################################

'25) 503322 -> 533322

		If rstbe!gear > 0 And rstce!gear = 0 And rstde!gear >= rstce!g_min And rstge!gear > 0 And rstge!gear = rstfe!gear And rstde!gear = rstee!gear And rstee!gear > rstfe!gear And rstfe!gear > 0 Then

			rstce.edit
			rstce!error_description = rstce!error_description & "25) 503322 -> 533322, "
			rstce.Update

		End If

'26) ########################################################################################################

'26) 503320 -> 533300 or 500000

		If rstbe!gear > 0 And rstce!gear = 0 And rstge!gear > 0 And rstge!gear = 0 And rstde!gear = rstee!gear And rstee!gear > rstfe!gear And rstfe!gear > 0 Then

			If rstde!gear >= rstce!g_min Then

				rstce.edit
				rstce!error_description = rstce!error_description & "26) 503320 -> 533300, "
				rstce.Update

				rstfe.edit
				rstfe!error_description = rstfe!error_description & "26) 503320 -> 533300, "
				rstfe.Update

			Else

				rstde.edit
				rstde!error_description = rstde!error_description & "26) 503320 -> 500000, "
				rstde.Update

				rstee.edit
				rstee!error_description = rstee!error_description & "26) 503320 -> 500000, "
				rstee.Update

				rstfe.edit
				rstfe!error_description = rstfe!error_description & "26) 503320 -> 500000, "
				rstfe.Update

			End If

		End If

'27) #########################################################################################################

'27) 3444443 -> 3333333

		If rstbe!gear > 0 And rstce!gear > rstbe!gear And rstde!gear > rstbe!gear And rstee!gear > rstbe!gear And rstfe!gear > rstbe!gear And rstge!gear > rstbe!gear And rsthe!gear <= rstbe!gear Then

			rstce.edit
			rstce!error_description = rstce!error_description & "27) 3444443 -> 3333333, "
			rstce.Update

			rstde.edit
			rstde!error_description = rstde!error_description & "27) 3444443 -> 3333333, "
			rstde.Update

			rstee.edit
			rstee!error_description = rstee!error_description & "27) 3444443 -> 3333333, "
			rstee.Update

			rstfe.edit
			rstfe!error_description = rstfe!error_description & "27) 3444443 -> 3333333, "
			rstfe.Update

			rstge.edit
			rstge!error_description = rstge!error_description & "27) 3444443 -> 3333333, "
			rstge.Update

		End If

'28) ###########################################################################################################

'28) 5000001 -> 5222221, if v >=1

		If rstbe!gear > rsthe!gear And rsthe!gear > 0 And rstde!gear = 0 And rstde!v >= 1 And rstce!gear = 0 And rstce!v >= 1 And rstee!gear = 0 And rstee!v >= 1 And rstfe!gear = 0 And rstfe!v >= 1 And rstge!gear = 0 And rstge!v >= 1 Then

			g_1 = rstce!g_max

			If rstde!g_max < g_1 Then

				g_1 = rstde!g_max

			End If

			If rstee!g_max < g_1 Then

				g_1 = rstee!g_max

			End If

			If rstfe!g_max < g_1 Then

				g_1 = rstfe!g_max

			End If

			If rstge!g_max < g_1 Then

				g_1 = rstge!g_max

			End If



			rstce.edit
			rstce!error_description = rstce!error_description & "28) 5000001 -> 5222221, if v>=1, "
			rstce.Update

			rstde.edit
			rstde!error_description = rstde!error_description & "28) 5000001 -> 5222221, if v>=1, "
			rstde.Update

			rstee.edit
			rstee!error_description = rstee!error_description & "28) 5000001 -> 5222221, if v>=1, "
			rstee.Update

			rstfe.edit
			rstfe!error_description = rstfe!error_description & "28) 5000001 -> 5222221, if v>=1, "
			rstfe.Update

			rstge.edit
			rstge!error_description = rstge!error_description & "28) 5000001 -> 5222221, if v>=1, "
			rstge.Update

		End If


'29) ############################################################################################################

'29) 3334555 -> 3334445

		If rstce!gear = rstbe!gear And rstde!gear = rstbe!gear And rstee!gear = rstbe!gear + 1 And rstfe!gear = rstbe!gear + 2 And rstge!gear = rstfe!gear And rsthe!gear = rstfe!gear Then

			rstfe.edit
			rstfe!error_description = rstfe!error_description & "29) 3334555 -> 3334445, "
			rstfe.Update

			rstge.edit
			rstge!error_description = rstge!error_description & "29) 3334555 -> 3334445, "
			rstge.Update

		End If

'30) #############################################################################################################

'30) 3334455 -> 3334445

		If rstce!gear = rstbe!gear And rstde!gear = rstbe!gear And rstee!gear = rstbe!gear + 1 And rstfe!gear = rstbe!gear + 1 And rstge!gear = rstbe!gear + 2 And rsthe!gear = rstge!gear Then


			rstge.edit
			rstge!error_description = rstge!error_description & "30) 3334455 -> 3334445, "
			rstge.Update

		End If

'31) ###################################################################################################################

'31) 5443221 -> 5002221, '5443222 -> 5002222

		If rstce!gear = rstbe!gear - 1 And rstde!gear = rstce!gear And rstee!gear = rstde!gear - 1 And rstfe!gear = rstee!gear - 1 And rstge!gear = rstfe!gear And (rsthe!gear = rstge!gear - 1 Or rsthe!gear = rstge!gear) And rsthe!gear > 0 Then

			rstce.edit
			rstce!error_description = rstce!error_description & "31) 5443221 -> 5002221, '5443222 -> 5002222, "
			rstce.Update

			rstde.edit
			rstde!error_description = rstde!error_description & "31) 5443221 -> 5002221, '5443222 -> 5002222, "
			rstde.Update

			rstee.edit
			rstee!error_description = rstee!error_description & "31) 5443221 -> 5002221, '5443222 -> 5002222, "
			rstee.Update

		End If

'32 #############################################################################################################################

'32) 3222000 -> 3000000

		If rstge!gear = 0 And rstfe!gear = 0 And rsthe!gear = 0 And rsthe!v < 1 And rstce!gear = rstde!gear And rstde!gear = rstee!gear And rstbe!gear > rstce!gear And rstce!gear > 0 Then

			rstce.edit
			rstce!error_description = rstce!error_description & "32) 3222000 -> 3000000, "
			rstce.Update

			rstde.edit
			rstde!error_description = rstde!error_description & "32) 3222000 -> 3000000, "
			rstde.Update

			rstee.edit
			rstee!error_description = rstee!error_description & "32) 3222000 -> 3000000, "
			rstee.Update

		End If




		rstbe.MoveNext
		rstce.MoveNext
		rstde.MoveNext
		rstee.MoveNext
		rstfe.MoveNext
		rstge.MoveNext
		rsthe.MoveNext

	Loop


'34 ######################################################################################################

	rstbe.MoveFirst

	rstce.MoveFirst
	rstce.MoveNext


	Do Until rstce.EOF

'Text7 = rstbe!part
'Text15 = rstbe!tim
'Me.Repaint




'34) check for gear 1 before stop


		If rstbe!v >= 1 And rstce!v < 1 Then

			k = 0
			v_1 = rstbe!v
			v_2 = v_1 + 1

			If rstbe!gear > 0 Then

				rstbe.edit
				rstbe!error_description = rstbe!error_description & "34) check for gear 1 before stop, "
				rstbe.Update

			End If


			weiter_stop_loop:

			If rstbe!gear > 1 Or v_2 <= v_1 Then

				If k > 0 Then

					For i = 1 To k

						rstbe.MoveNext

						If i = 1 And v_2 <= v_1 Then

							rstbe.edit
							rstbe!error_description = Null
							rstbe.Update

						End If

					Next i

				End If

				GoTo weiter_stop

			Else



				v_1 = rstbe!v

				k = k + 1

				rstbe.MovePrevious

				v_2 = rstbe!v

				If rstbe!gear = 1 And v_2 > v_1 Then

					rstbe.edit
					rstbe!error_description = rstbe!error_description & "34) check for gear 1 before stop, "
					rstbe.Update

				End If

				GoTo weiter_stop_loop

			End If

			GoTo weiter_stop

		Else

			GoTo weiter_stop

		End If


		weiter_stop:



		rstbe.MoveNext
		rstce.MoveNext


	Loop

'35  ######################################################################################################

	rstbe.MoveFirst



	Do Until rstbe.EOF

'Text7 = rstbe!part
'Text15 = rstbe!tim
'Me.Repaint




'35) check for gear below gear_min


		If rstbe!gear < rstbe!g_min And rstbe!gear > 0 Then


			rstbe.edit
			rstbe!error_description = rstbe!error_description & "35) check for gear below gear_min, "
			rstbe.Update

		End If


		rstbe.MoveNext

	Loop


	rstbe.Close
	rstce.Close
	rstde.Close
	rstee.Close
	rstfe.Close
	rstge.Close
	rsthe.Close


End Sub

Public Sub perform_downscaling()

	Dim wrkWS1
	Dim dbsDB1
	Dim rstce, rstbe
	Dim rstde, rstae
	Dim rstee
	Dim aa As Double, bb As Double, cc As Double, dd As Double, ee As Double, dt As Single, t As Single, n As Integer, m As Integer
	Dim n_min_drive_fact As Double, n_min_2_fact As Double
	Dim rated_speed As Integer, idling_speed As Integer, n_min_drive As Integer, n_min_2 As Integer, n_min_drive_set As Integer
	Dim downscale_factor As Double, a_neg_ave As Double, t_end As Integer
	m = 0
	n = 0

	t = 0

	Set wrkWS1 = DBEngine.Workspaces(0)
	Set dbsDB1 = wrkWS1.Databases(0)
'...

	Set rstae = dbsDB1.OpenRecordset("ST_vehicle_info", DB_OPEN_DYNASET)
	rstae.MoveFirst


	Set rstbe = dbsDB1.OpenRecordset("A gearshift_table sort", DB_OPEN_DYNASET)
	rstbe.MoveLast
	t_end = rstbe!Tim
	rstbe.MoveFirst

	Set rstce = dbsDB1.OpenRecordset("A gearshift_table sort", DB_OPEN_DYNASET)
	rstce.MoveFirst
	rstce.MoveNext




	downscale_factor = 1 - rstae!f_dsc_req


	If rstae!IDclass > 2 Then


		Do Until rstbe!Tim = 1533

			rstbe.MoveNext
			rstce.MoveNext

		Loop

		Do Until rstbe!Tim = 1724

			rstce.edit

			rstce!v_downscale = rstbe!v_downscale + (rstce!v_orig - rstbe!v_orig) * downscale_factor

			rstce.Update

			rstbe.MoveNext
			rstce.MoveNext

		Loop

		a_neg_ave = (rstbe!v_downscale - 82.6) / (rstbe!v_orig - 82.6)

		Do Until rstbe!Tim = 1762

			rstce.edit

			rstce!v_downscale = rstbe!v_downscale + (rstce!v_orig - rstbe!v_orig) * a_neg_ave

			rstce.Update

			rstbe.MoveNext
			rstce.MoveNext

		Loop

		rstbe.MoveFirst

		Do Until rstbe.EOF

			rstbe.edit

			rstbe!v = rstbe!v_downscale
			rstbe!v_cap = rstbe!v_downscale

			rstbe.Update

			rstbe.MoveNext

		Loop



	ElseIf rstae!IDclass = 2 Then


		Do Until rstbe!Tim = 1520

			rstbe.MoveNext
			rstce.MoveNext

		Loop

		Do Until rstbe!Tim = 1725

			rstce.edit

			rstce!v_downscale = rstbe!v_downscale + (rstce!v_orig - rstbe!v_orig) * downscale_factor

			rstce.Update

			rstbe.MoveNext
			rstce.MoveNext

		Loop

		a_neg_ave = (rstbe!v_downscale - 90.4) / (rstbe!v_orig - 90.4)

		Do Until rstbe!Tim = 1742

			rstce.edit

			rstce!v_downscale = rstbe!v_downscale + (rstce!v_orig - rstbe!v_orig) * a_neg_ave

			rstce.Update

			rstbe.MoveNext
			rstce.MoveNext

		Loop

		rstbe.MoveFirst

		Do Until rstbe.EOF

			rstbe.edit

			rstbe!v = rstbe!v_downscale
			rstbe!v_cap = rstbe!v_downscale

			rstbe.Update

			rstbe.MoveNext

		Loop


	ElseIf rstae!IDclass = 1 Then


		Do Until rstbe!Tim = 651
			rstbe.MoveNext
			rstce.MoveNext

		Loop

		Do Until rstbe!Tim = 848

			rstce.edit

			rstce!v_downscale = rstbe!v_downscale + (rstce!v_orig - rstbe!v_orig) * downscale_factor

			rstce.Update

			rstbe.MoveNext
			rstce.MoveNext

		Loop

		a_neg_ave = (rstbe!v_downscale - 36.7) / (rstbe!v_orig - 36.7)

		Do Until rstbe!Tim = 906

			rstce.edit

			rstce!v_downscale = rstbe!v_downscale + (rstce!v_orig - rstbe!v_orig) * a_neg_ave

			rstce.Update

			rstbe.MoveNext
			rstce.MoveNext

		Loop


		If t_end > 1700 Then

			Do Until rstbe!Tim = 2262
				rstbe.MoveNext
				rstce.MoveNext

			Loop

			Do Until rstbe!Tim = 2459

				rstce.edit

				rstce!v_downscale = rstbe!v_downscale + (rstce!v_orig - rstbe!v_orig) * downscale_factor

				rstce.Update

				rstbe.MoveNext
				rstce.MoveNext

			Loop

			a_neg_ave = (rstbe!v_downscale - 36.7) / (rstbe!v_orig - 36.7)

			Do Until rstbe!Tim = 2517

				rstce.edit

				rstce!v_downscale = rstbe!v_downscale + (rstce!v_orig - rstbe!v_orig) * a_neg_ave

				rstce.Update

				rstbe.MoveNext
				rstce.MoveNext

			Loop

		End If

	End If

	rstbe.MoveFirst

	Do Until rstbe.EOF

		rstbe.edit

		rstbe!v_downscale = Int(rstbe!v_downscale * 10 + 0.5) / 10
		rstbe!v = Int(rstbe!v_downscale * 10 + 0.5) / 10
		rstbe!v_cap = Int(rstbe!v_downscale * 10 + 0.5) / 10

		rstbe.Update

		rstbe.MoveNext

	Loop




	rstbe.Close
	rstce.Close

	rstae.Close



End Sub





Private Sub s108_AfterUpdate()



	If s108 = True Then

		DoCmd.OpenQuery "A TB_Pwot check", , acReadOnly

	End If

	s108 = False

End Sub

Private Sub Text100_AfterUpdate()

	Dim wrkWS1
	Dim dbsDB1

	Dim rstde, rstae

	Set wrkWS1 = DBEngine.Workspaces(0)
	Set dbsDB1 = wrkWS1.Databases(0)
'...


	dv_base = 2










	Set rstae = dbsDB1.OpenRecordset("ST_vehicle_info", DB_OPEN_DYNASET)

	rstae.MoveFirst
	rstae.edit

	rstae!description = Text100

	rstae.Update
	rstae.Close


	Befehl28.Enabled = True


End Sub

Public Sub calculation_of_tolerances()
	Dim wrkWS1
	Dim dbsDB1
	Dim rstce, rstbe
	Dim rstde, rstae
	Dim rstee, rstfe, rstge
	Dim aa As Double, bb As Double, cc As Double, dd As Double, ee As Double, dt As Single, t As Single, n As Integer, m As Integer
	Dim tol_min As Double, tol_max As Double, dv_base As Double, t_max As Double


	Set wrkWS1 = DBEngine.Workspaces(0)
	Set dbsDB1 = wrkWS1.Databases(0)
'...


	dv_base = 2










	Set rstae = dbsDB1.OpenRecordset("A gearshift_table sort", DB_OPEN_DYNASET)
	rstae.MoveFirst
	rstae.MoveLast


	t_max = rstae.RecordCount - 1


	rstae.MoveFirst

'MsgBox ("t_max = " & t_max)
'Stop

'################### calculation of tolerances first 10 s ##############################



	rstae.edit
	rstae!tol_max = dv_base
	rstae!tol_min = 0
	rstae.Update

	rstae.MoveNext



	Do Until rstae!Tim = t_max

		tol_min = rstae!v_cap - dv_base

		If tol_min < 0 Then

			tol_min = 0

		End If


		tol_max = rstae!v_cap + dv_base



		rstae.MovePrevious

		If rstae!v_cap - dv_base < tol_min Then

			tol_min = rstae!v_cap - dv_base

			If tol_min < 0 Then

				tol_min = 0

			End If


		End If

		If rstae!v_cap + dv_base > tol_max Then

			tol_max = rstae!v_cap + dv_base

		End If


		rstae.MoveNext


		rstae.MoveNext

		If rstae!v_cap - dv_base < tol_min Then

			tol_min = rstae!v_cap - dv_base

			If tol_min < 0 Then

				tol_min = 0

			End If


		End If

		If rstae!v_cap + dv_base > tol_max Then

			tol_max = rstae!v_cap + dv_base

		End If


		rstae.MovePrevious


		rstae.edit

		rstae!tol_min = tol_min
		rstae!tol_max = tol_max

		rstae.Update

		rstae.MoveNext

	Loop

	rstae.edit
	rstae!tol_max = dv_base
	rstae!tol_min = 0
	rstae.Update

	rstae.MoveNext


'################### end of calculation ##############################

	rstae.Close

'start of indication of shifts ####################################################################################################################

	Set rstbe = dbsDB1.OpenRecordset("A gearshift_table sort", DB_OPEN_DYNASET)
	Set rstce = dbsDB1.OpenRecordset("A gearshift_table sort", DB_OPEN_DYNASET)
	Set rstde = dbsDB1.OpenRecordset("A gearshift_table sort", DB_OPEN_DYNASET)


	rstbe.MoveFirst

	rstce.MoveFirst
	rstce.MoveNext

	rstde.MoveFirst
	rstde.MoveNext
	rstde.MoveNext

'MsgBox "start of gearshift indication!"


	Do Until rstde.EOF

		If rstbe!v > 1 And rstce!v > 1 And rstde!v > 1 And rstce!gear = rstde!gear And rstbe!gear = rstce!gear - 1 And rstbe!gear > 0 Then

			rstce.edit
			rstce!gearshift = 1
			rstce!upshift = True
			rstce.Update

		ElseIf rstbe!v > 1 And rstce!v > 1 And rstde!v > 1 And rstce!gear = rstde!gear And rstbe!gear > rstce!gear And rstde!gear > 0 Then

			rstce.edit
			rstce!gearshift = 1
			rstce!downshift = True
			rstce.Update

		ElseIf rstbe!v > 1 And rstce!v > 1 And rstde!v > 1 And rstce!gear = 0 And rstbe!gear > rstde!gear And rstde!gear > 0 Then

			rstce.edit
			rstce!gearshift = 1
			rstce!downshift = True
			rstce.Update

		End If

		rstbe.MoveNext
		rstce.MoveNext
		rstde.MoveNext

	Loop

	rstbe.Close
	rstce.Close
	rstde.Close

'end of indication of shifts####################################################################################################################

End Sub

Public Sub noise_calculation()
	Dim wrkWS1
	Dim dbsDB1
	Dim rstce, rstbe
	Dim rstde, rstae
	Dim rstee, rstfe, rstge, rsthe, rstie
	Dim aa As Double, bb As Double, cc As Double, dd As Double, ee As Double, dt As Single, t As Single, n As Integer, m As Integer, k As Integer, h As Integer
	Dim g_acc As Byte, g_cruise As Byte, g_dec As Byte, n_norm_max As Double, P_res As Double, j As Integer, i As Integer, l As Integer, o As Integer, P As Integer
	Dim n_norm_1 As Double, n_norm_2 As Double, n_norm_3 As Double, n_norm_4 As Double, n_norm_5 As Double, n_norm_6 As Double, n_norm As Double
	Dim P_norm_1 As Double, P_norm_2 As Double, P_norm_3 As Double, P_norm_4 As Double, P_norm_5 As Double, P_norm_6 As Double
	Dim v_1 As Double, v_2 As Double, P_1 As Double, P_2 As Double, g_1 As Byte, g_2 As Byte, P_a As Double, P_tot As Double
	Dim a_1 As Double, a_2 As Double, a_3 As Double, a_4 As Double, a_5 As Double, a_6 As Double
	Dim g_2s As Byte, g_2e As Byte, g_2b As Byte, v As Double, P_max As Double, z As Double, IDn_norm As Integer
	Dim n_orig As Integer, v_orig As Double, a As Double, v_de As Double, flag As Byte, flag2 As Byte
	Dim a_de As Double, n_de As Integer, n_norm_de As Double, IDn_norm_de As Integer, P_a_de As Double, P_tot_de As Double, P_res_de As Double, P_max_de As Double
	Dim downscale_factor As Double, Lroll As Double, Lprop_crs As Double, Lprop_wot As Double, Lprop As Double, Ltot As Double
	Dim P_rel As Double, i_prop As Double, i_roll As Double

	m = 0
	n = 0
	j = 0
	t = 0
'Forms![F check results]!Text7.Visible = False
'Forms![F check results]!Text15.Visible = False
'Forms![F check results]!B17.Visible = False
'Forms![F check results]!B16.Visible = False

	P = 0

	Set wrkWS1 = DBEngine.Workspaces(0)
	Set dbsDB1 = wrkWS1.Databases(0)
	Text85 = ""

	Text20 = "calculate noise"
	Me.Repaint

'...
	Set rstie = dbsDB1.OpenRecordset("A TB_noise", DB_OPEN_DYNASET)
	rstie.MoveFirst


	Set rstae = dbsDB1.OpenRecordset("A ST_vehicle_info2", DB_OPEN_DYNASET)
	rstae.MoveFirst


	Set rstbe = dbsDB1.OpenRecordset("A gearshift_table sort", DB_OPEN_DYNASET)
	rstbe.MoveFirst

	Do Until rstbe.EOF


		Lprop_crs = rstie!Lcrs_idle + (rstie!Lcrs_s - rstie!Lcrs_idle) / (rstae!rated_speed - rstae!idling_speed) * (rstbe!nc - rstae!idling_speed)

		Lprop_wot = rstie!Lwot_idle + (rstie!Lwot_s - rstie!Lwot_idle) / (rstae!rated_speed - rstae!idling_speed) * (rstbe!nc - rstae!idling_speed)

		If Lprop_wot < Lprop_crs Then

			Lprop_wot = Lprop_crs

		End If

		If rstbe!P_rel < 0 Then

			P_rel = 0

		Else

			P_rel = rstbe!P_rel

		End If

		Lprop = Lprop_crs + (Lprop_wot - Lprop_crs) * P_rel

		If rstbe!v >= 1 Then

			i_prop = Lprop - 10 * Log((25 ^ 2 + 4 ^ 2) * 19.23 / (7.5 ^ 2 + 1.2 ^ 2)) / Log(10) - 10 * Log(rstbe!v) / Log(10)

		Else

			i_prop = Lprop - 10 * Log((25 ^ 2 + 4 ^ 2) * 19.23 / (7.5 ^ 2 + 1.2 ^ 2)) / Log(10)

		End If

		If rstbe!v >= 5 Then

			Lroll = rstie!Lr_50 + rstie!Br * Log(rstbe!v / 50) / Log(10)

			Ltot = 10 * Log(10 ^ (0.1 * Lroll) + 10 ^ (0.1 * Lprop)) / Log(10)

			i_roll = Lroll - 10 * Log((25 ^ 2 + 4 ^ 2) * 19.23 / (7.5 ^ 2 + 1.2 ^ 2)) / Log(10) - 10 * Log(rstbe!v) / Log(10)

		Else

			Ltot = Lprop

			i_roll = 0

		End If

		i_tot = 10 * Log(10 ^ (0.1 * i_prop) + 10 ^ (0.1 * i_roll)) / Log(10)


		rstbe.edit

		rstbe!Lprop_crs = Lprop_crs
		rstbe!Lprop_wot = Lprop_wot
		rstbe!Lprop = Lprop
		rstbe!Ltot = Ltot
		rstbe!i_prop = 10 ^ (0.1 * i_prop)
		rstbe!i_tot = 10 ^ (0.1 * i_tot)


		If rstbe!v >= 5 Then

			rstbe!Lroll = Lroll
			rstbe!i_roll = 10 ^ (0.1 * i_roll)


		Else

			rstbe!i_roll = 0

		End If

		rstbe.Update

		rstbe.MoveNext

	Loop

	rstie.Close
	rstae.Close
	rstbe.Close


End Sub

Public Sub numbering_g1()
	Dim wrkWS1
	Dim dbsDB1
	Dim rstde
	Dim rstce



	Dim n As Integer
	Dim cc As Double, cc_old As Double, m As Integer


	Set wrkWS1 = DBEngine.Workspaces(0)
	Set dbsDB1 = wrkWS1.Databases(0)

'GoTo restart


	DoCmd.OpenQuery "A gearshift_table Ind_g1"


	Set rstce = dbsDB1.OpenRecordset("A gearshift_table sort", DB_OPEN_DYNASET)
	rstce.MoveFirst


	cc = 0
	cc_old = 0
	m = 0
	n = 0


	Do Until rstce.EOF



		If rstce![Ind_g1] = True Then


			If m = 0 Then

				rstce.edit

				n = n + 1
				rstce![n_g1] = n
				m = 1
				rstce.Update
't1 = rstce![n_acc]
'Me.Repaint


			Else

				rstce.edit

				rstce![n_g1] = n

				rstce.Update
't1 = rstce![n_acc]
'Me.Repaint


			End If



		Else

			m = 0

			GoTo next_dataset


		End If



		next_dataset:






		rstce.MoveNext




	Loop

	rstce.Close





End Sub

Public Sub numbering_g2()
	Dim wrkWS1
	Dim dbsDB1
	Dim rstde
	Dim rstce



	Dim n As Integer
	Dim cc As Double, cc_old As Double, m As Integer


	Set wrkWS1 = DBEngine.Workspaces(0)
	Set dbsDB1 = wrkWS1.Databases(0)

'GoTo restart


	DoCmd.OpenQuery "A gearshift_table Ind_g2"


	Set rstce = dbsDB1.OpenRecordset("A gearshift_table sort", DB_OPEN_DYNASET)
	rstce.MoveFirst


	cc = 0
	cc_old = 0
	m = 0
	n = 0


	Do Until rstce.EOF



		If rstce![Ind_g2] = True Then


			If m = 0 Then

				rstce.edit

				n = n + 1
				rstce![n_g2] = n
				m = 1
				rstce.Update
't1 = rstce![n_acc]
'Me.Repaint


			Else

				rstce.edit

				rstce![n_g2] = n

				rstce.Update
't1 = rstce![n_acc]
'Me.Repaint


			End If



		Else

			m = 0

			GoTo next_dataset


		End If



		next_dataset:






		rstce.MoveNext




	Loop

	rstce.Close





End Sub

Public Sub numbering_g3()
	Dim wrkWS1
	Dim dbsDB1
	Dim rstde
	Dim rstce



	Dim n As Integer
	Dim cc As Double, cc_old As Double, m As Integer


	Set wrkWS1 = DBEngine.Workspaces(0)
	Set dbsDB1 = wrkWS1.Databases(0)

'GoTo restart


	DoCmd.OpenQuery "A gearshift_table Ind_g3"


	Set rstce = dbsDB1.OpenRecordset("A gearshift_table sort", DB_OPEN_DYNASET)
	rstce.MoveFirst


	cc = 0
	cc_old = 0
	m = 0
	n = 0


	Do Until rstce.EOF



		If rstce![Ind_g3] = True Then


			If m = 0 Then

				rstce.edit

				n = n + 1
				rstce![n_g3] = n
				m = 1
				rstce.Update
't1 = rstce![n_acc]
'Me.Repaint


			Else

				rstce.edit

				rstce![n_g3] = n

				rstce.Update
't1 = rstce![n_acc]
'Me.Repaint


			End If



		Else

			m = 0

			GoTo next_dataset


		End If



		next_dataset:






		rstce.MoveNext




	Loop

	rstce.Close





End Sub

Public Sub numbering_g4()
	Dim wrkWS1
	Dim dbsDB1
	Dim rstde
	Dim rstce



	Dim n As Integer
	Dim cc As Double, cc_old As Double, m As Integer


	Set wrkWS1 = DBEngine.Workspaces(0)
	Set dbsDB1 = wrkWS1.Databases(0)

'GoTo restart


	DoCmd.OpenQuery "A gearshift_table Ind_g4"


	Set rstce = dbsDB1.OpenRecordset("A gearshift_table sort", DB_OPEN_DYNASET)
	rstce.MoveFirst


	cc = 0
	cc_old = 0
	m = 0
	n = 0


	Do Until rstce.EOF



		If rstce![Ind_g4] = True Then


			If m = 0 Then

				rstce.edit

				n = n + 1
				rstce![n_g4] = n
				m = 1
				rstce.Update
't1 = rstce![n_acc]
'Me.Repaint


			Else

				rstce.edit

				rstce![n_g4] = n

				rstce.Update
't1 = rstce![n_acc]
'Me.Repaint


			End If



		Else

			m = 0

			GoTo next_dataset


		End If



		next_dataset:






		rstce.MoveNext




	Loop

	rstce.Close





End Sub

Public Sub numbering_g5()
	Dim wrkWS1
	Dim dbsDB1
	Dim rstde
	Dim rstce



	Dim n As Integer
	Dim cc As Double, cc_old As Double, m As Integer


	Set wrkWS1 = DBEngine.Workspaces(0)
	Set dbsDB1 = wrkWS1.Databases(0)

'GoTo restart


	DoCmd.OpenQuery "A gearshift_table Ind_g5"


	Set rstce = dbsDB1.OpenRecordset("A gearshift_table sort", DB_OPEN_DYNASET)
	rstce.MoveFirst


	cc = 0
	cc_old = 0
	m = 0
	n = 0


	Do Until rstce.EOF



		If rstce![Ind_g5] = True Then


			If m = 0 Then

				rstce.edit

				n = n + 1
				rstce![n_g5] = n
				m = 1
				rstce.Update
't1 = rstce![n_acc]
'Me.Repaint


			Else

				rstce.edit

				rstce![n_g5] = n

				rstce.Update
't1 = rstce![n_acc]
'Me.Repaint


			End If



		Else

			m = 0

			GoTo next_dataset


		End If



		next_dataset:






		rstce.MoveNext




	Loop

	rstce.Close





End Sub

Public Sub numbering_g6()
	Dim wrkWS1
	Dim dbsDB1
	Dim rstde
	Dim rstce



	Dim n As Integer
	Dim cc As Double, cc_old As Double, m As Integer


	Set wrkWS1 = DBEngine.Workspaces(0)
	Set dbsDB1 = wrkWS1.Databases(0)

'GoTo restart


	DoCmd.OpenQuery "A gearshift_table Ind_g6"


	Set rstce = dbsDB1.OpenRecordset("A gearshift_table sort", DB_OPEN_DYNASET)
	rstce.MoveFirst


	cc = 0
	cc_old = 0
	m = 0
	n = 0


	Do Until rstce.EOF



		If rstce![Ind_g6] = True Then


			If m = 0 Then

				rstce.edit

				n = n + 1
				rstce![n_g6] = n
				m = 1
				rstce.Update
't1 = rstce![n_acc]
'Me.Repaint


			Else

				rstce.edit

				rstce![n_g6] = n

				rstce.Update
't1 = rstce![n_acc]
'Me.Repaint


			End If



		Else

			m = 0

			GoTo next_dataset


		End If



		next_dataset:






		rstce.MoveNext




	Loop

	rstce.Close





End Sub

Public Sub numbering_g7()
	Dim wrkWS1
	Dim dbsDB1
	Dim rstde
	Dim rstce



	Dim n As Integer
	Dim cc As Double, cc_old As Double, m As Integer


	Set wrkWS1 = DBEngine.Workspaces(0)
	Set dbsDB1 = wrkWS1.Databases(0)

'GoTo restart


	DoCmd.OpenQuery "A gearshift_table Ind_g7"


	Set rstce = dbsDB1.OpenRecordset("A gearshift_table sort", DB_OPEN_DYNASET)
	rstce.MoveFirst


	cc = 0
	cc_old = 0
	m = 0
	n = 0


	Do Until rstce.EOF



		If rstce![Ind_g7] = True Then


			If m = 0 Then

				rstce.edit

				n = n + 1
				rstce![n_g7] = n
				m = 1
				rstce.Update
't1 = rstce![n_acc]
'Me.Repaint


			Else

				rstce.edit

				rstce![n_g7] = n

				rstce.Update
't1 = rstce![n_acc]
'Me.Repaint


			End If



		Else

			m = 0

			GoTo next_dataset


		End If



		next_dataset:






		rstce.MoveNext




	Loop

	rstce.Close





End Sub

Private Sub Text128_AfterUpdate()

	If Kontrollk130 = False Then

		Exit Sub

	Else



		Dim wrkWS1
		Dim dbsDB1
		Dim rstde, rstae
		Dim rstce

		Dim n As Integer
		Dim cc As Double, cc_old As Double, m As Integer
		Dim x As Double, y As Double, yl As Double, yh As Double, xl As Double
		Dim n_min_drive_fact As Double, n_min_2_fact As Double
		Dim rated_speed As Integer, idling_speed As Integer, n_min_drive As Integer, n_min_2 As Integer, n_min_drive_set As Integer
		Dim nx As Integer

		Set wrkWS1 = DBEngine.Workspaces(0)
		Set dbsDB1 = wrkWS1.Databases(0)


		Set rstce = dbsDB1.OpenRecordset("A choose wot curve sort", DB_OPEN_DYNASET)
		rstce.MoveFirst

		Set rstde = dbsDB1.OpenRecordset("A choose wot curve sort", DB_OPEN_DYNASET)
		rstde.MoveFirst
		rstde.MoveNext

		y = Text128

		Do Until rstde!Pwot_norm >= y

			rstce.MoveNext
			rstde.MoveNext

		Loop

		xl = rstce!n_norm

		yl = rstce!Pwot_norm
		yh = rstde!Pwot_norm

		x = xl + (y - yl) / (yh - yl) * 0.01

		rstce.Close
		rstde.Close


		n_min_drive_fact = DLookup("[n_min_drive_fact]", "TB_side_conditions")
		n_min_2_fact = DLookup("[n_min_2_fact]", "TB_side_conditions")
		rated_speed = DLookup("[rated_speed]", "ST_vehicle_info")
		idling_speed = DLookup("[idling_speed]", "ST_vehicle_info")
		n_min_drive = DLookup("[n_min_drive]", "ST_n_min_drive")
		n_min_2 = DLookup("[n_min_2]", "ST_n_min_drive")
		n_min_drive_set = Int((n_min_drive_fact * (rated_speed - idling_speed) + idling_speed) + 0.5)

		nx = x * (rated_speed - idling_speed) + idling_speed

		Text132 = nx

		Kombinationsfeld19 = nx


		Set rstae = dbsDB1.OpenRecordset("ST_n_min_drive", DB_OPEN_DYNASET)
		rstae.MoveFirst
		rstae.edit
		rstae!n_min_drive = Text132
		rstae.Update
		rstae.Close


		Kombinationsfeld14.Enabled = True

	End If

End Sub

Public Sub numbering_g0()
	Dim wrkWS1
	Dim dbsDB1
	Dim rstde, rstae, rstbe, rstee, rstfe, rstge, rsthe
	Dim rstce



	Dim n As Integer
	Dim cc As Double, cc_old As Double, m As Integer


	Set wrkWS1 = DBEngine.Workspaces(0)
	Set dbsDB1 = wrkWS1.Databases(0)

'GoTo restart


	DoCmd.OpenQuery "A gearshift_table Ind_g0"


	Set rstbe = dbsDB1.OpenRecordset("A gearshift_table sort", DB_OPEN_DYNASET)
	Set rstce = dbsDB1.OpenRecordset("A gearshift_table sort", DB_OPEN_DYNASET)
	Set rstde = dbsDB1.OpenRecordset("A gearshift_table sort", DB_OPEN_DYNASET)
	Set rstee = dbsDB1.OpenRecordset("A gearshift_table sort", DB_OPEN_DYNASET)
	Set rstfe = dbsDB1.OpenRecordset("A gearshift_table sort", DB_OPEN_DYNASET)
	Set rstge = dbsDB1.OpenRecordset("A gearshift_table sort", DB_OPEN_DYNASET)
	Set rsthe = dbsDB1.OpenRecordset("A gearshift_table sort", DB_OPEN_DYNASET)

	rstbe.MoveFirst
	rstce.MoveFirst
	rstce.MoveNext
	rstde.MoveFirst
	rstde.MoveNext
	rstde.MoveNext
	rstee.MoveFirst
	rstee.MoveNext
	rstee.MoveNext
	rstee.MoveNext
	rstfe.MoveFirst
	rstfe.MoveNext
	rstfe.MoveNext
	rstfe.MoveNext
	rstfe.MoveNext
	rstge.MoveFirst
	rstge.MoveNext
	rstge.MoveNext
	rstge.MoveNext
	rstge.MoveNext
	rstge.MoveNext
	rsthe.MoveFirst
	rsthe.MoveNext
	rsthe.MoveNext
	rsthe.MoveNext
	rsthe.MoveNext
	rsthe.MoveNext
	rsthe.MoveNext

	Do Until rsthe.EOF

'Text7 = rstbe!part
'Text15 = rstbe!tim
'Me.Repaint

		If rsthe!v < 1 And rstbe!v < 20 Then

			If rstge!ind_g0 = True Then

				rstge.edit
				rstge!ind_g0 = False
				rstge.Update

			End If

			If rstfe!ind_g0 = True Then

				rstfe.edit
				rstfe!ind_g0 = False
				rstfe.Update

			End If

			If rstee!ind_g0 = True Then

				rstee.edit
				rstee!ind_g0 = False
				rstee.Update

			End If

			If rstde!ind_g0 = True Then

				rstde.edit
				rstde!ind_g0 = False
				rstde.Update

			End If

			If rstce!ind_g0 = True Then

				rstce.edit
				rstce!ind_g0 = False
				rstce.Update

			End If

			If rstbe!ind_g0 = True Then

				rstbe.edit
				rstbe!ind_g0 = False
				rstbe.Update

			End If

		End If

		rstbe.MoveNext
		rstce.MoveNext
		rstde.MoveNext
		rstee.MoveNext
		rstfe.MoveNext
		rstge.MoveNext
		rsthe.MoveNext

	Loop

	rstbe.Close
	rstde.Close
	rstee.Close
	rstfe.Close
	rstge.Close
	rsthe.Close

'######################################################################################


	cc = 0
	cc_old = 0
	m = 0
	n = 0

	rstce.MoveFirst

	Do Until rstce.EOF



		If rstce![ind_g0] = True Then


			If m = 0 Then

				rstce.edit

				n = n + 1
				rstce![n_g0] = n
				m = 1
				rstce.Update
't1 = rstce![n_acc]
'Me.Repaint


			Else

				rstce.edit

				rstce![n_g0] = n

				rstce.Update
't1 = rstce![n_acc]
'Me.Repaint


			End If



		Else

			m = 0

			GoTo next_dataset


		End If



		next_dataset:






		rstce.MoveNext




	Loop

	rstce.Close





End Sub

Public Sub gearshift_calculation1()
	Dim wrkWS1
	Dim dbsDB1
	Dim rstce, rstbe
	Dim rstde, rstae
	Dim rstee, rstfe, rstge, rsthe, rstie, rstke
	Dim aa As Double, bb As Double, cc As Double, dd As Double, ee As Double, dt As Single, t As Single, n As Double, m As Integer, k As Integer, h As Integer
	Dim g_acc As Byte, g_cruise As Byte, g_dec As Byte, n_norm_max As Double, P_res As Double, j As Integer, i As Integer, l As Integer, o As Integer, P As Integer
	Dim n_norm_1 As Double, n_norm_2 As Double, n_norm_3 As Double, n_norm_4 As Double, n_norm_5 As Double, n_norm_6 As Double, n_norm As Double
	Dim P_norm_1 As Double, P_norm_2 As Double, P_norm_3 As Double, P_norm_4 As Double, P_norm_5 As Double, P_norm_6 As Double
	Dim v_1 As Double, v_2 As Double, P_1 As Double, P_2 As Double, g_1 As Byte, g_2 As Byte, P_a As Double, P_tot As Double
	Dim a_1 As Double, a_2 As Double, a_3 As Double, a_4 As Double, a_5 As Double, a_6 As Double
	Dim g_2s As Byte, g_2e As Byte, g_2b As Byte, v As Double, P_max As Double, z As Double, IDn_norm As Integer
	Dim n_orig As Integer, v_orig As Double, a As Double, v_de As Double, flag As Byte, flag2 As Byte, flag3 As Byte
	Dim a_de As Double, n_de As Double, n_norm_de As Double, IDn_norm_de As Integer, P_a_de As Double, P_tot_de As Double, P_res_de As Double, P_max_de As Double
	Dim downscale_factor As Double, n_max_wot As Double, Pwot As Double, Pavai As Double, ASM As Double, n_min_wot As Double
	Dim SM0 As Double, kr As Double, v_cap As Double, Pwot_n_min As Double, Pwot_n_max As Double, a_thr As Double, fact As Double
	Dim n_ref As Double, idling_speed As Integer

	m = 0
	n = 0
	j = 0
	t = 0


	P = 0

	Set wrkWS1 = DBEngine.Workspaces(0)
	Set dbsDB1 = wrkWS1.Databases(0)
	Text85 = ""

	Text20 = "calculate gear use"
	Me.Repaint




	Set rstae = dbsDB1.OpenRecordset("A ST_vehicle_info open", DB_OPEN_DYNASET)
	rstae.MoveFirst

	SM0 = rstae!SM0
	kr = rstae!kr
	a_thr = rstae!a_thr
	idling_speed = rstae!idling_speed
	n_ref = 1.15 * idling_speed
	n_min_wot = rstae!n_min_wot
	n_max_wot = rstae!n_max_wot

	DoCmd.OpenQuery "A gearshift_table del"

' calculation for WLTC #######################################################################################################

	If Rahmen36 = 1 Then

		DoCmd.OpenQuery "A gearshift_table"

		downscale_factor = rstae!f_dsc_req

		If downscale_factor > 0.01 And rstae!skip_downscaling = False Then

' if required, downscaling will be performed according to annex 1, paragraph 8 ################################################

			perform_downscaling

		End If

		DoCmd.OpenQuery "A gearshift_table v_cap"

		If rstae!v_cap > 0 Then

' if reqired, capped speed cycle will be calculated according to annex 1, paragraph 9 ##########################################

			Calculate_speed_capped_cycle

		End If

' calculation for EVAP purge cycle ##############################################################################################

	ElseIf Rahmen36 = 2 Then

		DoCmd.OpenQuery "A gearshift_table purge"

		If rstae!IDclass = 1 Then

			downscale_factor = rstae!f_dsc_req

			If downscale_factor > 0.01 And rstae!skip_downscaling = False Then

				perform_downscaling

			End If

		End If

		DoCmd.OpenQuery "A gearshift_table v_cap"

		If rstae!v_cap > 0 Then

			Calculate_speed_capped_cycle

		End If


' calculation for NEDC ###############################################################################

	ElseIf Rahmen36 = 3 Then

		DoCmd.OpenQuery "A gearshift_table NEDC"

		GoTo weiter_NEDC_1:

' calculation for other cycles ########################################################################

	ElseIf Rahmen36 = 4 Then

		DoCmd.OpenQuery "A gearshift_table random1"


	End If


	weiter_NEDC_1:

	If Rahmen36 = 3 Then

		DoCmd.OpenQuery "A gearshift_table corr_g_max_NEDC"
		DoCmd.OpenQuery "A gearshift_table corr_g_max_NEDC2"

		If Rahmen183 = True Then

			DoCmd.OpenQuery "A gearshift_table corr_g_2_1_NEDC"

		End If


	End If

' v is set to v_max, if v > v_max #####################################################################

	DoCmd.OpenQuery "A gearshift_table v_corr_v_max"


	Set rstbe = dbsDB1.OpenRecordset("A gearshift_table sort", DB_OPEN_DYNASET)
	Set rstce = dbsDB1.OpenRecordset("A gearshift_table sort", DB_OPEN_DYNASET)
	Set rstde = dbsDB1.OpenRecordset("A gearshift_table sort", DB_OPEN_DYNASET)



	rstbe.MoveFirst
	rstce.MoveFirst
	rstce.MoveNext
	rstde.MoveFirst
	rstde.MoveNext
	rstde.MoveNext

	rstbe.edit

	rstbe!a = (rstce!v - rstbe!v) / 3.6
	rstbe!vma = (rstce!v - rstbe!v) / 3.6 * rstbe!v / 3.6
	rstbe!a_cap = (rstce!v_cap - rstbe!v_cap) / 3.6
	rstbe!vma_cap = (rstce!v_cap - rstbe!v_cap) / 3.6 * rstbe!v_cap / 3.6
	rstbe!a_downscale = (rstce!v_downscale - rstbe!v_downscale) / 3.6
	rstbe!vma_downscale = (rstce!v_downscale - rstbe!v_downscale) / 3.6 * rstbe!v_downscale / 3.6
	rstbe!a_orig = (rstce!v_orig - rstbe!v_orig) / 3.6
	rstbe!vma_orig = (rstce!v_orig - rstbe!v_orig) / 3.6 * rstbe!v_orig / 3.6

	rstbe!a2 = (rstce!v - 0) / 3.6 / 2
	rstbe!vma2 = (rstce!v - 0) / 3.6 / 2 * rstbe!v / 3.6
	rstbe!a2_orig = (rstce!v_orig - 0) / 3.6 / 2
	rstbe!vma2_orig = (rstce!v_orig - 0) / 3.6 / 2 * rstbe!v_orig / 3.6

	rstbe.Update



	Do Until rstde.EOF

		rstce.edit

		rstce!a = (rstde!v - rstce!v) / 3.6
		rstce!vma = (rstde!v - rstce!v) / 3.6 * rstce!v / 3.6
		rstce!a_cap = (rstde!v_cap - rstce!v_cap) / 3.6
		rstce!vma_cap = (rstde!v_cap - rstce!v_cap) / 3.6 * rstce!v_cap / 3.6
		rstce!a_downscale = (rstde!v_downscale - rstce!v_downscale) / 3.6
		rstce!vma_downscale = (rstde!v_downscale - rstce!v_downscale) / 3.6 * rstce!v_downscale / 3.6
		rstce!a_orig = (rstde!v_orig - rstce!v_orig) / 3.6
		rstce!vma_orig = (rstde!v_orig - rstce!v_orig) / 3.6 * rstce!v_orig / 3.6

		rstce!a2 = (rstde!v - rstbe!v) / 3.6 / 2
		rstce!vma2 = (rstde!v - rstbe!v) / 3.6 / 2 * rstce!v / 3.6
		rstce!a2_orig = (rstde!v_orig - rstbe!v_orig) / 3.6 / 2
		rstce!vma2_orig = (rstde!v_orig - rstbe!v_orig) / 3.6 / 2 * rstce!v_orig / 3.6


		rstce.Update


		rstbe.MoveNext
		rstce.MoveNext
		rstde.MoveNext

	Loop

	rstce.edit


	rstce!a = 0
	rstce!vma = 0
	rstce!a_cap = 0
	rstce!vma_cap = 0
	rstce!a_downscale = 0
	rstce!vma_downscale = 0
	rstce!a_orig = 0
	rstce!vma_orig = 0

	rstce!a2 = (0 - rstbe!v) / 3.6 / 2
	rstce!vma2 = (0 - rstbe!v) / 3.6 / 2 * rstce!v / 3.6
	rstce!a2_orig = (0 - rstbe!v_orig) / 3.6 / 2
	rstce!vma2_orig = (0 - rstbe!v_orig) / 3.6 / 2 * rstce!v_orig / 3.6

	rstce.Update



	flag = 0



'DoCmd.OpenQuery "A gearshift_table corr v_n_max3"

' Determination of engine speeds for NEDC cycle #####################################################################

	DoCmd.OpenQuery "A gearshift_table n_01"
	DoCmd.OpenQuery "A gearshift_table n_1"
	DoCmd.OpenQuery "A gearshift_table n_2"

	If Rahmen36 = 3 Then

		DoCmd.OpenQuery "A gearshift_table n_3 NEDC"
		DoCmd.OpenQuery "A gearshift_table n_4 NEDC"
		DoCmd.OpenQuery "A gearshift_table n_5 NEDC"
		DoCmd.OpenQuery "A gearshift_table n_6 NEDC"
		DoCmd.OpenQuery "A gearshift_table n_7 NEDC"
		DoCmd.OpenQuery "A gearshift_table n_8 NEDC"
		DoCmd.OpenQuery "A gearshift_table n_9 NEDC"
		DoCmd.OpenQuery "A gearshift_table n_10 NEDC"

		GoTo weiter_NEDC


	End If



	Set rstie = dbsDB1.OpenRecordset("A TA_Pwot sort", DB_OPEN_DYNASET)
	rstie.MoveFirst
	n_min_wot = rstie!n
	Pwot_n_min = rstie!Pavai
	rstie.MoveLast
	n_max_wot = rstie.n
	Pwot_n_max = rstie!Pavai

' Calculation of accelerations (a and a2), accelerations*vehicle speed (vma and vma2), required acceleration power (based on a), driving resistance power ###############
' Calculations according to annex 2, paragraph 3.1

	Set rstke = dbsDB1.OpenRecordset("A TA_Pwot sort", DB_OPEN_DYNASET)



	rstbe.MoveFirst

	rstce.MoveFirst
	rstce.MoveNext

	Do Until rstce.EOF

		rstbe.edit


		rstbe!P_a = (rstbe!v * (rstce!v - rstbe!v) / 3.6 * kr * rstae!test_mass) / 3600
		rstbe!P_res = (rstae!f0 * rstbe!v + rstae!f1 * rstbe!v ^ 2 + rstae!f2 * rstbe!v ^ 3) / 3600

		rstbe!P_tot = (rstbe!v * (rstce!v - rstbe!v) / 3.6 * kr * rstae!test_mass) / 3600 + (rstae!f0 * rstbe!v + rstae!f1 * rstbe!v ^ 2 + rstae!f2 * rstbe!v ^ 3) / 3600


		rstbe.Update


		rstbe.MoveNext
		rstce.MoveNext


	Loop

	rstbe.edit


	rstbe!P_a = 0
	rstbe!P_res = (rstae!f0 * rstbe!v + rstae!f1 * rstbe!v ^ 2 + rstae!f2 * rstbe!v ^ 3) / 3600

	rstbe!P_tot = (rstae!f0 * rstbe!v + rstae!f1 * rstbe!v ^ 2 + rstae!f2 * rstbe!v ^ 3) / 3600


	rstbe.Update


'Stop

' Calculation of engine speeds and available power per gear according to annex 2, paragraphs 3.2 and 3.4  and the lowest possible gear according to annex 2, paragraphs 3.3 and 3.5 ###


' v < 1, gear 0 ############################################################################

	rstbe.MoveFirst

	Do Until rstbe.EOF

		If rstbe!v < 1 Then

			rstbe.edit
			rstbe!gear = 0
			rstbe!g_max = 0
			rstbe!g_min = 0
			rstbe!nc = idling_speed
			rstbe!clutch = "engaged, gear lever in neutral"
			rstbe.Update

		End If

		rstbe.MoveNext

	Loop


' gear 1 ############################################################################

	rstbe.MoveFirst

	Do Until rstbe.EOF

		n = rstae!ndv_1 * rstbe!v

		If rstbe!v < 1 Then

			rstbe.edit

			rstbe!g_min = 0
			rstbe!g_max = 0
			rstbe!clutch = "disengaged"
			rstbe.Update

		End If

		If rstbe!v >= 1 And n < idling_speed Then

			rstbe.edit
			rstbe!g_max = 1
			rstbe!g_min = 1

			If rstbe!a > 0 Then

				n = n_ref

			Else

				n = idling_speed

			End If

			rstbe!n_1 = n
			rstbe.Update

		End If

		If n >= idling_speed And rstbe!v >= 1 And rstbe!v * rstae!ndv_1 <= rstae!n_max1 Then

			rstbe.edit
			rstbe!g_min = 1

			rstbe!n_1 = n

			If rstbe!a >= 0 And n < n_ref Then

				n = n_ref

				rstbe!n_1 = n


			End If


			If rstbe!v * rstae!ndv_2 < n_ref And rstbe!a >= 0 Then

				rstbe!g_max = 1

			ElseIf rstbe!v * rstae!ndv_2 < 0.9 * idling_speed And rstbe!a < 0 Then

				rstbe!g_max = 1

			End If



			If n >= n_min_wot And n <= n_max_wot Then


				rstie.MoveFirst
				rstke.MoveFirst
				rstke.MoveNext

				If n > rstke!n Then



					Do Until rstie!n < n And n <= rstke!n

						rstie.MoveNext
						rstke.MoveNext

					Loop

				End If


				If n <= rstie!n Then

					Pwot = rstie!Pwot
					Pavai = rstie!Pavai

				Else

					Pwot = rstie!Pwot + (rstke!Pwot - rstie!Pwot) / (rstke!n - rstie!n) * (n - rstie!n)


					Pavai = rstie!Pavai + (rstke!Pavai - rstie!Pavai) / (rstke!n - rstie!n) * (n - rstie!n)

				End If


				rstbe!P_1 = Pavai

			End If

			rstbe.Update

		End If


		rstbe.MoveNext

	Loop

' gear 2 ############################################################################

	rstbe.MoveFirst

	Do Until rstbe.EOF

		n = rstae!ndv_2 * rstbe!v

		If rstbe!v < 1 Or n < 0.9 * idling_speed Or n > n_max_wot Or rstbe!a > 0 And n < n_ref Then


			GoTo endloop_n2

		Else

			If rstbe!a > 0 And (n_min_wot >= n_ref And n < n_min_wot Or n_min_wot < n_ref And n < idling_speed) Then

				If rstae!ndv_2 * rstbe!v >= n_ref Then

					n = rstae!ndv_2 * rstbe!v

				Else

					n = n_ref

				End If


			ElseIf n < idling_speed Then

				n = idling_speed

			End If

			rstbe.edit
			rstbe!n_2 = n
			If n <= rstae!n_max1 And rstae!ndv_1 * rstbe!v > rstae!n_max1 Then
				rstbe!g_min = 2
				rstbe!g_max = 2
			End If

			rstbe.Update




			rstie.MoveFirst
			rstke.MoveFirst
			rstke.MoveNext

			If rstbe!n_2 > rstke!n Then



				Do Until rstie!n < rstbe!n_2 And rstbe!n_2 <= rstke!n

					rstie.MoveNext
					rstke.MoveNext

				Loop

			End If

			If rstbe!n_2 <= rstie!n Then

				Pwot = rstie!Pwot
				Pavai = rstie!Pavai

			Else


				Pwot = rstie!Pwot + (rstke!Pwot - rstie!Pwot) / (rstke!n - rstie!n) * (rstbe!n_2 - rstie!n)

				Pavai = rstie!Pavai + (rstke!Pavai - rstie!Pavai) / (rstke!n - rstie!n) * (rstbe!n_2 - rstie!n)

			End If

			rstbe.edit
			rstbe!P_2 = Pavai
			rstbe.Update

		End If

		endloop_n2:

		rstbe.MoveNext

	Loop

' gear 3 ############################################################################

	rstbe.MoveFirst

	Do Until rstbe.EOF


		n = rstae!ndv_3 * rstbe!v

		If rstbe!v < 1 Or n < idling_speed Or n > n_max_wot Then


			GoTo endloop_n3

		Else


			rstbe.edit
			rstbe!n_3 = n
			If IsNull(rstbe!g_min) Then
				If n <= rstae!n_max1 Or (rstae!gear_v_max = 3 And n <= n_max_wot) Then
					rstbe!g_min = 3
				End If
			End If

			rstbe.Update


			rstie.MoveFirst
			rstke.MoveFirst
			rstke.MoveNext

			If rstbe!n_3 > rstke!n Then



				Do Until rstie!n < rstbe!n_3 And rstbe!n_3 <= rstke!n

					rstie.MoveNext
					rstke.MoveNext

				Loop

			End If

			Pwot = rstie!Pwot + (rstke!Pwot - rstie!Pwot) / (rstke!n - rstie!n) * (rstbe!n_3 - rstie!n)

			Pavai = rstie!Pavai + (rstke!Pavai - rstie!Pavai) / (rstke!n - rstie!n) * (rstbe!n_3 - rstie!n)


			rstbe.edit
			rstbe!P_3 = Pavai
			rstbe.Update


		End If

		endloop_n3:

		rstbe.MoveNext

	Loop

' gear 4 ############################################################################

	If rstae!no_of_gears < 4 Then

		GoTo endloop_end

	Else
		rstbe.MoveFirst

		Do Until rstbe.EOF

			n = rstae!ndv_4 * rstbe!v

			If rstbe!v < 1 Or n < idling_speed Or n > n_max_wot Then


				GoTo endloop_n4

			Else


				rstbe.edit
				rstbe!n_4 = n
				If IsNull(rstbe!g_min) Then

					If n <= rstae!n_max1 Or (rstae!gear_v_max = 4 And n <= n_max_wot) Then
						rstbe!g_min = 4
					End If
				End If
				rstbe.Update

				rstie.MoveFirst
				rstke.MoveFirst
				rstke.MoveNext

				If rstbe!n_4 > rstke!n Then



					Do Until rstie!n < rstbe!n_4 And rstbe!n_4 <= rstke!n

						rstie.MoveNext
						rstke.MoveNext

					Loop

				End If

				Pwot = rstie!Pwot + (rstke!Pwot - rstie!Pwot) / (rstke!n - rstie!n) * (rstbe!n_4 - rstie!n)

				Pavai = rstie!Pavai + (rstke!Pavai - rstie!Pavai) / (rstke!n - rstie!n) * (rstbe!n_4 - rstie!n)

				rstbe.edit
				rstbe!P_4 = Pavai
				rstbe.Update


			End If

			endloop_n4:

			rstbe.MoveNext

		Loop

	End If

' gear 5 ############################################################################

	If rstae!no_of_gears < 5 Then

		GoTo endloop_end

	Else

		rstbe.MoveFirst

		Do Until rstbe.EOF

			n = rstae!ndv_5 * rstbe!v

			If rstbe!v < 1 Or n < idling_speed Or n > n_max_wot Then


				GoTo endloop_n5

			Else


				rstbe.edit
				rstbe!n_5 = n
				If IsNull(rstbe!g_min) Then
					If n <= rstae!n_max1 Or (rstae!gear_v_max = 5 And n <= n_max_wot) Then
						rstbe!g_min = 5
					End If
				End If
				rstbe.Update

				rstie.MoveFirst
				rstke.MoveFirst
				rstke.MoveNext

				If rstbe!n_5 > rstke!n Then



					Do Until rstie!n < rstbe!n_5 And rstbe!n_5 <= rstke!n

						rstie.MoveNext
						rstke.MoveNext

					Loop

				End If

				Pwot = rstie!Pwot + (rstke!Pwot - rstie!Pwot) / (rstke!n - rstie!n) * (rstbe!n_5 - rstie!n)

				Pavai = rstie!Pavai + (rstke!Pavai - rstie!Pavai) / (rstke!n - rstie!n) * (rstbe!n_5 - rstie!n)

				rstbe.edit
				rstbe!P_5 = Pavai
				rstbe.Update

			End If

			endloop_n5:

			rstbe.MoveNext

		Loop

	End If


' gear 6 ############################################################################

	If rstae!no_of_gears < 6 Then

		GoTo endloop_end

	Else

		rstbe.MoveFirst

		Do Until rstbe.EOF

			n = rstae!ndv_6 * rstbe!v

			If rstbe!v < 1 Or n < idling_speed Or n > n_max_wot Then


				GoTo endloop_n6

			Else


				rstbe.edit
				rstbe!n_6 = n
				If IsNull(rstbe!g_min) Then
					If n <= rstae!n_max1 Or (rstae!gear_v_max = 6 And n <= n_max_wot) Then
						rstbe!g_min = 6
					End If
				End If
				rstbe.Update

				rstie.MoveFirst
				rstke.MoveFirst
				rstke.MoveNext

				If rstbe!n_6 > rstke!n Then



					Do Until rstie!n < rstbe!n_6 And rstbe!n_6 <= rstke!n

						rstie.MoveNext
						rstke.MoveNext

					Loop

				End If

				Pwot = rstie!Pwot + (rstke!Pwot - rstie!Pwot) / (rstke!n - rstie!n) * (rstbe!n_6 - rstie!n)

				Pavai = rstie!Pavai + (rstke!Pavai - rstie!Pavai) / (rstke!n - rstie!n) * (rstbe!n_6 - rstie!n)

				rstbe.edit
				rstbe!P_6 = Pavai
				rstbe.Update


			End If

			endloop_n6:

			rstbe.MoveNext

		Loop

	End If



' gear 7 ############################################################################

	If rstae!no_of_gears < 7 Then

		GoTo endloop_end

	Else


		rstbe.MoveFirst

		Do Until rstbe.EOF

			n = rstae!ndv_7 * rstbe!v

			If rstbe!v < 1 Or n < idling_speed Or n > n_max_wot Then


				GoTo endloop_n7

			Else


				rstbe.edit
				rstbe!n_7 = n
				If IsNull(rstbe!g_min) Then
					If n <= rstae!n_max1 Or (rstae!gear_v_max = 7 And n <= n_max_wot) Then
						rstbe!g_min = 7
					End If
				End If
				rstbe.Update

				rstie.MoveFirst
				rstke.MoveFirst
				rstke.MoveNext

				If rstbe!n_7 > rstke!n Then



					Do Until rstie!n < rstbe!n_7 And rstbe!n_7 <= rstke!n

						rstie.MoveNext
						rstke.MoveNext

					Loop

				End If

				Pwot = rstie!Pwot + (rstke!Pwot - rstie!Pwot) / (rstke!n - rstie!n) * (rstbe!n_7 - rstie!n)

				Pavai = rstie!Pavai + (rstke!Pavai - rstie!Pavai) / (rstke!n - rstie!n) * (rstbe!n_7 - rstie!n)

				rstbe.edit
				rstbe!P_7 = Pavai
				rstbe.Update


			End If

			endloop_n7:

			rstbe.MoveNext

		Loop

	End If


' gear 8 ############################################################################

	If rstae!no_of_gears < 8 Then

		GoTo endloop_end

	Else


		rstbe.MoveFirst

		Do Until rstbe.EOF

			n = rstae!ndv_8 * rstbe!v

			If rstbe!v < 1 Or n < idling_speed Or n > n_max_wot Then


				GoTo endloop_n8

			Else


				rstbe.edit
				rstbe!n_8 = n
				If IsNull(rstbe!g_min) Then
					If n <= rstae!n_max1 Or (rstae!gear_v_max = 8 And n <= n_max_wot) Then
						rstbe!g_min = 8
					End If
				End If
				rstbe.Update

				rstie.MoveFirst
				rstke.MoveFirst
				rstke.MoveNext

				If rstbe!n_8 > rstke!n Then



					Do Until rstie!n < rstbe!n_8 And rstbe!n_8 <= rstke!n

						rstie.MoveNext
						rstke.MoveNext

					Loop

				End If

				Pwot = rstie!Pwot + (rstke!Pwot - rstie!Pwot) / (rstke!n - rstie!n) * (rstbe!n_8 - rstie!n)

				Pavai = rstie!Pavai + (rstke!Pavai - rstie!Pavai) / (rstke!n - rstie!n) * (rstbe!n_8 - rstie!n)

				rstbe.edit
				rstbe!P_8 = Pavai
				rstbe.Update


			End If

			endloop_n8:

			rstbe.MoveNext

		Loop


	End If


' gear 9 ############################################################################

	If rstae!no_of_gears < 9 Then

		GoTo endloop_end

	Else


		rstbe.MoveFirst

		Do Until rstbe.EOF

			n = rstae!ndv_9 * rstbe!v

			If rstbe!v < 1 Or n < idling_speed Or n > n_max_wot Then


				GoTo endloop_n9

			Else


				rstbe.edit
				rstbe!n_9 = n
				If IsNull(rstbe!g_min) Then
					If n <= rstae!n_max1 Or (rstae!gear_v_max = 9 And n <= n_max_wot) Then
						rstbe!g_min = 9
					End If
				End If
				rstbe.Update

				rstie.MoveFirst
				rstke.MoveFirst
				rstke.MoveNext

				If rstbe!n_9 > rstke!n Then



					Do Until rstie!n < rstbe!n_9 And rstbe!n_9 <= rstke!n

						rstie.MoveNext
						rstke.MoveNext

					Loop

				End If

				Pwot = rstie!Pwot + (rstke!Pwot - rstie!Pwot) / (rstke!n - rstie!n) * (rstbe!n_9 - rstie!n)

				Pavai = rstie!Pavai + (rstke!Pavai - rstie!Pavai) / (rstke!n - rstie!n) * (rstbe!n_9 - rstie!n)

				rstbe.edit
				rstbe!P_9 = Pavai
				rstbe.Update


			End If

			endloop_n9:

			rstbe.MoveNext

		Loop


	End If



' gear 10 ############################################################################

	If rstae!no_of_gears < 10 Then

		GoTo endloop_end

	Else


		rstbe.MoveFirst

		Do Until rstbe.EOF

			n = rstae!ndv_10 * rstbe!v

			If rstbe!v < 1 Or n < idling_speed Or n > n_max_wot Then


				GoTo endloop_n10

			Else


				rstbe.edit
				rstbe!n_10 = n
				If IsNull(rstbe!g_min) Then
					If n <= rstae!n_max1 Or (rstae!gear_v_max = 10 And n <= n_max_wot) Then
						rstbe!g_min = 10
					End If
				End If
				rstbe.Update

				rstie.MoveFirst
				rstke.MoveFirst
				rstke.MoveNext

				If rstbe!n_10 > rstke!n Then



					Do Until rstie!n < rstbe!n_10 And rstbe!n_10 <= rstke!n

						rstie.MoveNext
						rstke.MoveNext

					Loop

				End If

				Pwot = rstie!Pwot + (rstke!Pwot - rstie!Pwot) / (rstke!n - rstie!n) * (rstbe!n_10 - rstie!n)

				Pavai = rstie!Pavai + (rstke!Pavai - rstie!Pavai) / (rstke!n - rstie!n) * (rstbe!n_10 - rstie!n)
				rstbe.edit
				rstbe!P_10 = Pavai
				rstbe.Update


			End If

			endloop_n10:

			rstbe.MoveNext

		Loop

	End If



'#######################################################################################################

	endloop_end:

'Stop

	DoCmd.OpenQuery "A gearshift_table P_res"
	DoCmd.OpenQuery "A gearshift_table P_a"
	DoCmd.OpenQuery "A gearshift_table P_tot"

' Calculation of maximum possible acceleration per gear #######################################################

	DoCmd.OpenQuery "A gearshift_table a_1"
	DoCmd.OpenQuery "A gearshift_table a_2"
	DoCmd.OpenQuery "A gearshift_table a_3"
	DoCmd.OpenQuery "A gearshift_table a_4"
	DoCmd.OpenQuery "A gearshift_table a_5"
	DoCmd.OpenQuery "A gearshift_table a_6"
	DoCmd.OpenQuery "A gearshift_table a_7"
	DoCmd.OpenQuery "A gearshift_table a_8"
	DoCmd.OpenQuery "A gearshift_table a_9"
	DoCmd.OpenQuery "A gearshift_table a_10"

	If Rahmen36 = 3 Then

		DoCmd.OpenQuery "A gearshift_table n_NEDC"
'Stop
		DoCmd.OpenQuery "A gearshift_table n_NEDC2"
		DoCmd.OpenQuery "A gearshift_table n_kl_NEDC"



		GoTo weiter


	End If

' Determination of the highest possible gear according to annex 2, paragraphs 3.3 and 3.5 ############################################################################

	rstbe.MoveFirst


	Do Until rstbe.EOF


		If Not IsNull(rstbe!n_10) And (IsNull(rstae!n_min_drive_start_up) Or (Not IsNull(rstae!n_min_drive_start_up) And rstbe!Tim > rstae!t_end_start_phase)) And ((rstbe!v * rstae!ndv_10 >= rstae!n_min_drive_up And rstbe!a >= a_thr) Or (rstbe!v * rstae!ndv_10 >= rstae!n_min_drive_down And rstbe!a < a_thr)) Then

			If rstbe!P_10 >= rstbe!P_tot Or rstbe!g_min = 10 Then
				rstbe.edit
				rstbe!g_max = 10
				rstbe.Update
				GoTo weiter_max
			End If

		ElseIf Not IsNull(rstbe!n_10) And Not IsNull(rstae!n_min_drive_start_up) And rstbe!Tim <= rstae!t_end_start_phase And ((rstbe!v * rstae!ndv_10 >= rstae!n_min_drive_start_up And rstbe!a >= a_thr) Or (rstbe!v * rstae!ndv_10 >= rstae!n_min_drive_start_down And rstbe!a < a_thr)) Then

			If rstbe!P_10 >= rstbe!P_tot Or rstbe!g_min = 10 Then
				rstbe.edit
				rstbe!g_max = 10
				rstbe.Update
				GoTo weiter_max
			End If


		End If

		If Not IsNull(rstbe!n_9) And (IsNull(rstae!n_min_drive_start_up) Or (Not IsNull(rstae!n_min_drive_start_up) And rstbe!Tim > rstae!t_end_start_phase)) And ((rstbe!v * rstae!ndv_9 >= rstae!n_min_drive_up And rstbe!a >= a_thr) Or (rstbe!v * rstae!ndv_9 >= rstae!n_min_drive_down And rstbe!a < a_thr)) Then

			If rstbe!P_9 >= rstbe!P_tot Or rstbe!g_min = 9 Then
				rstbe.edit
				rstbe!g_max = 9
				rstbe.Update
				GoTo weiter_max
			End If

		ElseIf Not IsNull(rstbe!n_9) And Not IsNull(rstae!n_min_drive_start_up) And rstbe!Tim <= rstae!t_end_start_phase And ((rstbe!v * rstae!ndv_9 >= rstae!n_min_drive_start_up And rstbe!a >= a_thr) Or (rstbe!v * rstae!ndv_9 >= rstae!n_min_drive_start_down And rstbe!a < a_thr)) Then

			If rstbe!P_9 >= rstbe!P_tot Or rstbe!g_min = 9 Then
				rstbe.edit
				rstbe!g_max = 9
				rstbe.Update
				GoTo weiter_max
			End If

		End If

		If Not IsNull(rstbe!n_8) And (IsNull(rstae!n_min_drive_start_up) Or (Not IsNull(rstae!n_min_drive_start_up) And rstbe!Tim > rstae!t_end_start_phase)) And ((rstbe!v * rstae!ndv_8 >= rstae!n_min_drive_up And rstbe!a >= a_thr) Or (rstbe!v * rstae!ndv_8 >= rstae!n_min_drive_down And rstbe!a < a_thr)) Then

			If rstbe!P_8 >= rstbe!P_tot Or rstbe!g_min = 8 Then
				rstbe.edit
				rstbe!g_max = 8
				rstbe.Update
				GoTo weiter_max
			End If

		ElseIf Not IsNull(rstbe!n_8) And Not IsNull(rstae!n_min_drive_start_up) And rstbe!Tim <= rstae!t_end_start_phase And ((rstbe!v * rstae!ndv_8 >= rstae!n_min_drive_start_up And rstbe!a >= a_thr) Or (rstbe!v * rstae!ndv_8 >= rstae!n_min_drive_start_down And rstbe!a < a_thr)) Then

			If rstbe!P_8 >= rstbe!P_tot Or rstbe!g_min = 8 Then
				rstbe.edit
				rstbe!g_max = 8
				rstbe.Update
				GoTo weiter_max
			End If

		End If

		If Not IsNull(rstbe!n_7) And (IsNull(rstae!n_min_drive_start_up) Or (Not IsNull(rstae!n_min_drive_start_up) And rstbe!Tim > rstae!t_end_start_phase)) And ((rstbe!v * rstae!ndv_7 >= rstae!n_min_drive_up And rstbe!a >= a_thr) Or (rstbe!v * rstae!ndv_7 >= rstae!n_min_drive_down And rstbe!a < a_thr)) Then

			If rstbe!P_7 >= rstbe!P_tot Or rstbe!g_min = 7 Then
				rstbe.edit
				rstbe!g_max = 7
				rstbe.Update
				GoTo weiter_max
			End If

		ElseIf Not IsNull(rstbe!n_7) And Not IsNull(rstae!n_min_drive_start_up) And rstbe!Tim <= rstae!t_end_start_phase And ((rstbe!v * rstae!ndv_7 >= rstae!n_min_drive_start_up And rstbe!a >= a_thr) Or (rstbe!v * rstae!ndv_7 >= rstae!n_min_drive_start_down And rstbe!a < a_thr)) Then

			If rstbe!P_7 >= rstbe!P_tot Or rstbe!g_min = 7 Then
				rstbe.edit
				rstbe!g_max = 7
				rstbe.Update
				GoTo weiter_max
			End If

		End If

		If Not IsNull(rstbe!n_6) And (IsNull(rstae!n_min_drive_start_up) Or (Not IsNull(rstae!n_min_drive_start_up) And rstbe!Tim > rstae!t_end_start_phase)) And ((rstbe!v * rstae!ndv_6 >= rstae!n_min_drive_up And rstbe!a >= a_thr) Or (rstbe!v * rstae!ndv_6 >= rstae!n_min_drive_down And rstbe!a < a_thr)) Then

			If rstbe!P_6 >= rstbe!P_tot Or rstbe!g_min = 6 Then
				rstbe.edit
				rstbe!g_max = 6
				rstbe.Update
				GoTo weiter_max
			End If

		ElseIf Not IsNull(rstbe!n_6) And Not IsNull(rstae!n_min_drive_start_up) And rstbe!Tim <= rstae!t_end_start_phase And ((rstbe!v * rstae!ndv_6 >= rstae!n_min_drive_start_up And rstbe!a >= a_thr) Or (rstbe!v * rstae!ndv_6 >= rstae!n_min_drive_start_down And rstbe!a < a_thr)) Then

			If rstbe!P_6 >= rstbe!P_tot Or rstbe!g_min = 6 Then
				rstbe.edit
				rstbe!g_max = 6
				rstbe.Update
				GoTo weiter_max
			End If

		End If

		If Not IsNull(rstbe!n_5) And (IsNull(rstae!n_min_drive_start_up) Or (Not IsNull(rstae!n_min_drive_start_up) And rstbe!Tim > rstae!t_end_start_phase)) And ((rstbe!v * rstae!ndv_5 >= rstae!n_min_drive_up And rstbe!a >= a_thr) Or (rstbe!v * rstae!ndv_5 >= rstae!n_min_drive_down And rstbe!a < a_thr)) Then

			If rstbe!P_5 >= rstbe!P_tot Or rstbe!g_min = 5 Then
				rstbe.edit
				rstbe!g_max = 5
				rstbe.Update
				GoTo weiter_max
			End If

		ElseIf Not IsNull(rstbe!n_5) And Not IsNull(rstae!n_min_drive_start_up) And rstbe!Tim <= rstae!t_end_start_phase And ((rstbe!v * rstae!ndv_5 >= rstae!n_min_drive_start_up And rstbe!a >= a_thr) Or (rstbe!v * rstae!ndv_5 >= rstae!n_min_drive_start_down And rstbe!a < a_thr)) Then

			If rstbe!P_5 >= rstbe!P_tot Or rstbe!g_min = 5 Then
				rstbe.edit
				rstbe!g_max = 5
				rstbe.Update
				GoTo weiter_max
			End If

		End If

		If Not IsNull(rstbe!n_4) And (IsNull(rstae!n_min_drive_start_up) Or (Not IsNull(rstae!n_min_drive_start_up) And rstbe!Tim > rstae!t_end_start_phase)) And ((rstbe!v * rstae!ndv_4 >= rstae!n_min_drive_up And rstbe!a >= a_thr) Or (rstbe!v * rstae!ndv_4 >= rstae!n_min_drive_down And rstbe!a < a_thr)) Then

			If rstbe!P_4 >= rstbe!P_tot Or rstbe!g_min = 4 Then
				rstbe.edit
				rstbe!g_max = 4
				rstbe.Update
				GoTo weiter_max
			End If

		ElseIf Not IsNull(rstbe!n_4) And Not IsNull(rstae!n_min_drive_start_up) And rstbe!Tim <= rstae!t_end_start_phase And ((rstbe!v * rstae!ndv_4 >= rstae!n_min_drive_start_up And rstbe!a >= a_thr) Or (rstbe!v * rstae!ndv_4 >= rstae!n_min_drive_start_down And rstbe!a < a_thr)) Then

			If rstbe!P_4 >= rstbe!P_tot Or rstbe!g_min = 4 Then
				rstbe.edit
				rstbe!g_max = 4
				rstbe.Update
				GoTo weiter_max
			End If

		End If

		If Not IsNull(rstbe!n_3) And (IsNull(rstae!n_min_drive_start_up) Or (Not IsNull(rstae!n_min_drive_start_up) And rstbe!Tim > rstae!t_end_start_phase)) And ((rstbe!v * rstae!ndv_3 >= rstae!n_min_drive_up And rstbe!a >= a_thr) Or (rstbe!v * rstae!ndv_3 >= rstae!n_min_drive_down And rstbe!a < a_thr)) Then

			If rstbe!P_3 >= rstbe!P_tot Or rstbe!g_min = 3 Then
				rstbe.edit
				rstbe!g_max = 3
				rstbe.Update
				GoTo weiter_max
			End If

		ElseIf Not IsNull(rstbe!n_3) And Not IsNull(rstae!n_min_drive_start_up) And rstbe!Tim <= rstae!t_end_start_phase And ((rstbe!v * rstae!ndv_3 >= rstae!n_min_drive_start_up And rstbe!a >= a_thr) Or (rstbe!v * rstae!ndv_3 >= rstae!n_min_drive_start_down And rstbe!a < a_thr)) Then

			If rstbe!P_3 >= rstbe!P_tot Or rstbe!g_min = 3 Then
				rstbe.edit
				rstbe!g_max = 3
				rstbe.Update
				GoTo weiter_max
			End If

		End If

		If Not IsNull(rstbe!n_2) And rstbe!v * rstae!ndv_2 >= 0.9 * idling_speed Then

			rstbe.edit
			rstbe!g_max = 2
			If rstbe!g_min > 2 Then
				rstbe!g_min = 2
			End If
			rstbe.Update
		End If

		weiter_max:

		rstbe.MoveNext

	Loop

'###########################################################################################

	rstbe.MoveFirst

	rstce.MoveFirst
	rstce.MoveNext

	rstde.MoveFirst
	rstde.MoveNext
	rstde.MoveNext

	Do Until rstde.EOF

		If rstbe!g_max = 1 And rstce!g_max = 2 And rstde!g_max = 2 And rstae!ndv_2 * rstce!v < n_ref Then

			rstce.edit
			rstce!g_max = 1
			rstce.Update

			If rstae!ndv_2 * rstde!v < n_ref Then

				rstde.edit
				rstde!g_max = 1
				rstde.Update

			End If

		End If

		If rstbe!g_max <= 1 And rstce!g_max = 1 And rstde!g_max = 2 And rstae!ndv_2 * rstde!v < n_ref Then

			rstde.edit
			rstde!g_max = 1
			rstde.Update

		End If



		rstbe.MoveNext
		rstce.MoveNext
		rstde.MoveNext

	Loop



' Correction of g_min and g_max in case they are empty or 0 ###############################################################

'DoCmd.OpenQuery "A gearshift_table g_min corr"
'DoCmd.OpenQuery "A gearshift_table g_max corr"

'############################################################################################
'correction of g_max for cases where Pavai < Preq for all gears and the previous code chooses g_min as g_max but higher gears have the same or higher Pavai values


	If Kontr226 = False Then

'option for other cycles without annex 2 requirements, a tolerance of 0.5% missing power is allowed
		fact = 0.995

	Else

'option for other cycles with annex 2 requirements, no tolerance for missing power is allowed
		fact = 1

	End If

	rstbe.MoveFirst

	Do Until rstbe.EOF

		If rstbe!g_max = 2 Then

			If rstbe!P_4 >= fact * rstbe!P_2 Then
				rstbe.edit
				rstbe!g_max = 4
				rstbe.Update

			ElseIf rstbe!P_3 >= fact * rstbe!P_2 Then
				rstbe.edit
				rstbe!g_max = 3
				rstbe.Update

			End If
		End If

		rstbe.MoveNext

	Loop

	rstbe.MoveFirst
	Do Until rstbe.EOF

		If rstbe!g_max = 3 Then

			If rstbe!P_5 >= fact * rstbe!P_3 Then
				rstbe.edit
				rstbe!g_max = 5
				rstbe.Update

			ElseIf rstbe!P_4 >= fact * rstbe!P_3 Then
				rstbe.edit
				rstbe!g_max = 4
				rstbe.Update

			End If
		End If

		rstbe.MoveNext

	Loop

	rstbe.MoveFirst
	Do Until rstbe.EOF

		If rstbe!g_max = 4 Then

			If rstbe!P_6 >= fact * rstbe!P_4 Then
				rstbe.edit
				rstbe!g_max = 6
				rstbe.Update

			ElseIf rstbe!P_5 >= fact * rstbe!P_4 Then
				rstbe.edit
				rstbe!g_max = 5
				rstbe.Update

			End If
		End If

		rstbe.MoveNext

	Loop

	rstbe.MoveFirst
	Do Until rstbe.EOF

		If rstbe!g_max = 5 Then

			If rstbe!P_7 >= fact * rstbe!P_5 Then
				rstbe.edit
				rstbe!g_max = 7
				rstbe.Update

			ElseIf rstbe!P_6 >= fact * rstbe!P_5 Then
				rstbe.edit
				rstbe!g_max = 6
				rstbe.Update

			End If
		End If

		rstbe.MoveNext

	Loop

	rstbe.MoveFirst
	Do Until rstbe.EOF

		If rstbe!g_max = 6 Then

			If rstbe!P_8 >= fact * rstbe!P_6 Then
				rstbe.edit
				rstbe!g_max = 8
				rstbe.Update

			ElseIf rstbe!P_7 >= fact * rstbe!P_6 Then
				rstbe.edit
				rstbe!g_max = 7
				rstbe.Update

			End If
		End If

		rstbe.MoveNext

	Loop

	rstbe.MoveFirst
	Do Until rstbe.EOF

		If rstbe!g_max = 7 Then

			If rstbe!P_9 >= fact * rstbe!P_7 Then
				rstbe.edit
				rstbe!g_max = 9
				rstbe.Update

			ElseIf rstbe!P_8 >= fact * rstbe!P_7 Then
				rstbe.edit
				rstbe!g_max = 7
				rstbe.Update

			End If
		End If

		rstbe.MoveNext

	Loop

	rstbe.MoveFirst
	Do Until rstbe.EOF

		If rstbe!g_max = 8 Then

			If rstbe!P_10 >= fact * rstbe!P_8 Then
				rstbe.edit
				rstbe!g_max = 10
				rstbe.Update

			ElseIf rstbe!P_9 >= fact * rstbe!P_8 Then
				rstbe.edit
				rstbe!g_max = 9
				rstbe.Update

			End If
		End If

		rstbe.MoveNext

	Loop

	rstbe.MoveFirst
	Do Until rstbe.EOF

		If rstbe!g_max = 9 Then

			If rstbe!P_10 >= fact * rstbe!P_9 Then
				rstbe.edit
				rstbe!g_max = 10
				rstbe.Update

			End If

		End If

		rstbe.MoveNext

	Loop

'correction of engine speed and gear during decelerations to stop

	rstbe.MoveFirst
	rstce.MoveFirst
	rstce.MoveNext


	Do Until rstce.EOF

		If rstbe!v >= 1 And rstce!v < 1 Then

'MsgBox "time " & rstce!Tim

			k = 0

			Do Until rstce!g_max = 2 And rstce!n_02 < idling_speed And rstce!a < 0 Or rstce!a > 0

				k = k + 1

				rstbe.MovePrevious
				rstce.MovePrevious

			Loop

			If rstce!a > 0 Then

'MsgBox "a > 0, time " & rstce!Tim

				For i = 1 To k + 1

					rstbe.MoveNext
					rstce.MoveNext

				Next i

				GoTo end_corr

			Else

				j = 0

				start_j:

				If rstce!g_max = 2 And rstce!n_02 < idling_speed And rstce!a < 0 Then

					rstce.edit
					rstce!g_max = 1
					rstce!gear_modification = "g_max 2 -> 1, "
					rstce.Update


					rstce.MovePrevious

					j = j + 1

					GoTo start_j

				Else

'MsgBox "time " & rstce!Tim & ", j = " & j

					If j = 0 Then

						GoTo end_j

					Else

						For i = 1 To j

							rstce.MoveNext

						Next i

					End If

				End If



				end_j:

'MsgBox "a < 0, time " & rstce!Tim

				For i = 1 To k + 1

					rstbe.MoveNext
					rstce.MoveNext

				Next i

				GoTo end_corr

			End If


		End If

		end_corr:

		rstbe.MoveNext
		rstce.MoveNext

	Loop

'specify final dec #############################################################################

'correction of engine speed and gear during decelerations to stop

	rstbe.MoveFirst
	rstce.MoveFirst
	rstce.MoveNext


	Do Until rstce.EOF

		If rstbe!v >= 1 And rstce!v < 1 Then

'MsgBox "time " & rstce!Tim

			k = 0

			Do Until rstbe!a >= 0

				k = k + 1

				rstbe.MovePrevious
				rstce.MovePrevious

			Loop

			rstce.edit
			rstce!final_dec = True
			rstce.Update

			For i = 1 To k


				rstce.edit
				rstce!final_dec = True
				rstce.Update

				rstbe.MoveNext
				rstce.MoveNext

			Next i

			GoTo end_corr2



		End If

		end_corr2:

		rstbe.MoveNext
		rstce.MoveNext

	Loop



' The initial gear to be used for each second j of the cycle trace is the highest final possible gear, imax according to annex 2, paragraph 3.5.


	DoCmd.OpenQuery "A gearshift_table gear_gear_max"



	weiter:

	rstie.Close
	rstbe.Close
	rstce.Close
	rstde.Close
	rstke.Close

	weiter_NEDC:
	rstae.Close

'Stop
End Sub

Public Sub numbering_g8()
	Dim wrkWS1
	Dim dbsDB1
	Dim rstde
	Dim rstce



	Dim n As Integer
	Dim cc As Double, cc_old As Double, m As Integer


	Set wrkWS1 = DBEngine.Workspaces(0)
	Set dbsDB1 = wrkWS1.Databases(0)

'GoTo restart


	DoCmd.OpenQuery "A gearshift_table Ind_g8"


	Set rstce = dbsDB1.OpenRecordset("A gearshift_table sort", DB_OPEN_DYNASET)
	rstce.MoveFirst


	cc = 0
	cc_old = 0
	m = 0
	n = 0


	Do Until rstce.EOF



		If rstce![Ind_g8] = True Then


			If m = 0 Then

				rstce.edit

				n = n + 1
				rstce![n_g8] = n
				m = 1
				rstce.Update
't1 = rstce![n_acc]
'Me.Repaint


			Else

				rstce.edit

				rstce![n_g8] = n

				rstce.Update
't1 = rstce![n_acc]
'Me.Repaint


			End If



		Else

			m = 0

			GoTo next_dataset


		End If



		next_dataset:






		rstce.MoveNext




	Loop

	rstce.Close




End Sub

Public Sub numbering_g9()
	Dim wrkWS1
	Dim dbsDB1
	Dim rstde
	Dim rstce



	Dim n As Integer
	Dim cc As Double, cc_old As Double, m As Integer


	Set wrkWS1 = DBEngine.Workspaces(0)
	Set dbsDB1 = wrkWS1.Databases(0)

'GoTo restart


	DoCmd.OpenQuery "A gearshift_table Ind_g9"


	Set rstce = dbsDB1.OpenRecordset("A gearshift_table sort", DB_OPEN_DYNASET)
	rstce.MoveFirst


	cc = 0
	cc_old = 0
	m = 0
	n = 0


	Do Until rstce.EOF



		If rstce![Ind_g9] = True Then


			If m = 0 Then

				rstce.edit

				n = n + 1
				rstce![n_g9] = n
				m = 1
				rstce.Update
't1 = rstce![n_acc]
'Me.Repaint


			Else

				rstce.edit

				rstce![n_g9] = n

				rstce.Update
't1 = rstce![n_acc]
'Me.Repaint


			End If



		Else

			m = 0

			GoTo next_dataset


		End If



		next_dataset:






		rstce.MoveNext




	Loop

	rstce.Close




End Sub

Public Sub numbering_g10()
	Dim wrkWS1
	Dim dbsDB1
	Dim rstde
	Dim rstce



	Dim n As Integer
	Dim cc As Double, cc_old As Double, m As Integer


	Set wrkWS1 = DBEngine.Workspaces(0)
	Set dbsDB1 = wrkWS1.Databases(0)

'GoTo restart


	DoCmd.OpenQuery "A gearshift_table Ind_g10"


	Set rstce = dbsDB1.OpenRecordset("A gearshift_table sort", DB_OPEN_DYNASET)
	rstce.MoveFirst


	cc = 0
	cc_old = 0
	m = 0
	n = 0


	Do Until rstce.EOF



		If rstce![Ind_g10] = True Then


			If m = 0 Then

				rstce.edit

				n = n + 1
				rstce![n_g10] = n
				m = 1
				rstce.Update
't1 = rstce![n_acc]
'Me.Repaint


			Else

				rstce.edit

				rstce![n_g10] = n

				rstce.Update
't1 = rstce![n_acc]
'Me.Repaint


			End If



		Else

			m = 0

			GoTo next_dataset


		End If



		next_dataset:






		rstce.MoveNext




	Loop

	rstce.Close




End Sub

Public Sub gearshift_calculation3()
	Dim wrkWS1
	Dim dbsDB1
	Dim rstce, rstbe
	Dim rstde, rstae
	Dim rstee, rstfe, rstge, rsthe, rstie, rstke
	Dim aa As Double, bb As Double, cc As Double, dd As Double, ee As Double, dt As Single, t As Single, n As Double, m As Integer, k As Integer, h As Integer
	Dim g_acc As Byte, g_cruise As Byte, g_dec As Byte, n_norm_max As Double, P_res As Double, j As Integer, i As Integer, l As Integer, o As Integer, P As Integer
	Dim n_norm_1 As Double, n_norm_2 As Double, n_norm_3 As Double, n_norm_4 As Double, n_norm_5 As Double, n_norm_6 As Double, n_norm As Double
	Dim P_norm_1 As Double, P_norm_2 As Double, P_norm_3 As Double, P_norm_4 As Double, P_norm_5 As Double, P_norm_6 As Double
	Dim v_1 As Double, v_2 As Double, P_1 As Double, P_2 As Double, g_1 As Byte, g_2 As Byte, P_a As Double, P_tot As Double
	Dim a_1 As Double, a_2 As Double, a_3 As Double, a_4 As Double, a_5 As Double, a_6 As Double
	Dim g_2s As Byte, g_2e As Byte, g_2b As Byte, v As Double, P_max As Double, z As Double, IDn_norm As Integer
	Dim n_orig As Integer, v_orig As Double, a As Double, v_de As Double, flag As Byte, flag2 As Byte, flag3 As Byte
	Dim a_de As Double, n_de As Double, n_ce As Double, n_norm_de As Double, IDn_norm_de As Integer, P_a_de As Double, P_tot_de As Double, P_res_de As Double, P_max_de As Double
	Dim downscale_factor As Double, n_max_wot As Double, n_min_wot As Double, Pwot As Double, Pavai As Double, ASM As Double
	Dim SM0 As Double, kr As Double, t_start As Integer, m_old As Integer, flag_text7 As Byte

	flag_text7 = 0

	m_old = 0
	m = 0
	n = 0
	j = 0
	t = 0

	P = 0

	Set wrkWS1 = DBEngine.Workspaces(0)
	Set dbsDB1 = wrkWS1.Databases(0)
	Text85 = ""

	Text20 = "calculate gear use"
	Me.Repaint




	Set rstae = dbsDB1.OpenRecordset("A ST_vehicle_info open", DB_OPEN_DYNASET)
	rstae.MoveFirst

	SM0 = rstae!SM0
	kr = rstae!kr




	If Rahmen36 = 3 Then

		GoTo weiter_NEDC_2


	End If



	Set rstie = dbsDB1.OpenRecordset("A TA_Pwot sort", DB_OPEN_DYNASET)
	rstie.MoveLast
	n_max_wot = rstie.n

	Set rstke = dbsDB1.OpenRecordset("A TA_Pwot sort", DB_OPEN_DYNASET)

	Set rstbe = dbsDB1.OpenRecordset("A gearshift_table sort", DB_OPEN_DYNASET)

	rstie.MoveFirst

	n_min_wot = rstie!n

	rstke.MoveFirst
	rstke.MoveNext

	P = 1

	n = 0
	m = 0
	k = 0
	j = 0


	Set rstce = dbsDB1.OpenRecordset("A gearshift_table sort", DB_OPEN_DYNASET)
	Set rstde = dbsDB1.OpenRecordset("A gearshift_table sort", DB_OPEN_DYNASET)


'Start of v_corr####################################################################################################################
'===================================================================================================================================



	rstbe.MoveFirst

	rstce.MoveFirst
	rstce.MoveNext

	rstde.MoveFirst
	rstde.MoveNext
	rstde.MoveNext

	Do Until rstde.EOF


		n = rstce!nc
		v = rstce!v
		P_res = rstce!P_res
		a = (rstde!v - v) / 3.6
		P_a = a * rstae!test_mass * kr * v / 3600
		P_tot = rstce!P_res + P_a
		P_max = rstce!P_max
		Pavai = rstce!P_max

		If P_tot > rstce!P_max And v >= 1 And n >= n_min_wot Then



			a = (Pavai - P_res) * 3600 / kr / v / rstae!test_mass

			P_a = a * rstae!test_mass * kr * v / 3600

			v_de = v + a * 3.6

			If v_de > rstde!v Then

				v_de = rstde!v

			End If

			n_de = rstde!nc * v_de / rstde!v



			IDn_norm_de = Int(n_de / 10 + 0.5) * 10


			P_res_de = (rstae!f0 * v_de + rstae!f1 * v_de ^ 2 + rstae!f2 * v_de ^ 3) / 3600

			rstie.MoveFirst
			rstke.MoveFirst
			rstke.MoveNext



			If n_de > rstke!n Then

				Do Until rstie!n < n_de And n_de <= rstke!n

					rstie.MoveNext
					rstke.MoveNext

				Loop

			End If

			If n_de = rstke!n Then

				Pavai = rstke!Pavai
				Pwot = rstke!Pwot

			ElseIf n_de < rstie!n Then

				Pavai = rstie!Pavai
				Pwot = rstie!Pwot

			Else

				Pavai = rstie!Pavai + (rstke!Pavai - rstie!Pavai) / (rstke!n - rstie!n) * (n_de - rstie!n)
				Pwot = rstie!Pwot + (rstke!Pwot - rstie!Pwot) / (rstke!n - rstie!n) * (n_de - rstie!n)

			End If


			P_max_de = Pavai

			rstde.edit

			rstde!v = v_de
			rstde!nc = n_de
			rstde!n_kl = IDn_norm_de
			rstde!gear_modification = rstde!gear_modification & "v_corr_de, "
			rstde!P_res = P_res_de
			rstde!P_max = P_max_de
			rstde!Pwot_wo_margin = Pwot
			rstde!safety_margin_Pwot = 1 - Pavai / Pwot

			rstde.Update

		End If

		loopend:

		rstbe.MoveNext
		rstce.MoveNext
		rstde.MoveNext


	Loop

'#############################################################################################################

	rstbe.MoveFirst

	rstce.MoveFirst
	rstce.MoveNext

	rstde.MoveFirst
	rstde.MoveNext
	rstde.MoveNext

	rstbe.edit

	rstbe!a2 = (rstce!v) / 2 / 3.6
	rstbe!vma2 = (rstce!v) / 2 / 3.6 * rstbe!v / 3.6

	rstbe.Update

	Do Until rstde.EOF

		rstbe.edit

		rstbe!a = (rstce!v - rstbe!v) / 3.6
		rstbe!vma = (rstce!v - rstbe!v) / 3.6 * rstbe!v / 3.6

		rstbe!P_a = (rstbe!v * (rstce!v - rstbe!v) / 3.6 * kr * rstae!test_mass) / 3600
		rstbe!P_res = (rstae!f0 * rstbe!v + rstae!f1 * rstbe!v ^ 2 + rstae!f2 * rstbe!v ^ 3) / 3600



		rstbe!P_tot = (rstbe!v * (rstce!v - rstbe!v) / 3.6 * kr * rstae!test_mass) / 3600 + (rstae!f0 * rstbe!v + rstae!f1 * rstbe!v ^ 2 + rstae!f2 * rstbe!v ^ 3) / 3600


		rstbe.Update

		rstce.edit

		rstce!a2 = (rstde!v - rstbe!v) / 2 / 3.6
		rstce!vma2 = (rstde!v - rstbe!v) / 2 / 3.6 * rstce!v / 3.6

		rstce.Update

		rstbe.MoveNext
		rstce.MoveNext
		rstde.MoveNext

	Loop

	rstce.edit
	rstce!a = 0
	rstce!vma = 0
	rstce!a2 = 0
	rstce!vma2 = 0

	rstce.Update




'End of v_corr ####################################################################################################################



	rstie.Close
	rstke.Close
	rstae.Close
	rstbe.Close
	rstce.Close
	rstde.Close


	weiter_NEDC_2:


	DoCmd.OpenQuery "A gearshift_table P_rel"
	DoCmd.OpenQuery "A gearshift_table n_kl2"

	DoCmd.OpenQuery "A gearshift_table n_above_s_Ste"



End Sub

Private Sub Text181_AfterUpdate()
	Dim wrkWS1
	Dim dbsDB1
	Dim rstce
	Dim n_min_drive_up As Integer, n_min_drive_up_max As Integer, n As Integer, n_min_drive_set As Integer


	Set wrkWS1 = DBEngine.Workspaces(0)
	Set dbsDB1 = wrkWS1.Databases(0)
'...

	Set rstce = dbsDB1.OpenRecordset("ST_vehicle_info", DB_OPEN_DYNASET)

	rstce.MoveFirst

	n_min_drive_set = rstce!n_min_drive_set


	n_min_drive_up = Text181


	If n_min_drive_up <= rstce!n_min_drive_set Then

		MsgBox "n_min_drive_up must be higher than n_min_drive_set!"

		rstce.edit
		rstce!n_min_drive_up_modified = False
		rstce.Update
		rstce.Close

		Exit Sub

	ElseIf n_min_drive_up > 2 * n_min_drive_set Then

		MsgBox "n_min_drive_up must not be higher than 2*n_min_drive_set!"

		rstce.edit
		rstce!n_min_drive_up_modified = False
		rstce.Update
		rstce.Close

		Exit Sub

	Else

		If Ko179 = False Then

			rstce.edit
			rstce!n_min_drive_up_modified = False
			rstce.Update
			rstce.Close

			Exit Sub

		Else


			rstce.edit
			rstce!n_min_drive_up_modified = True
			rstce!n_min_drive_up = n_min_drive_up
'rstce!n_min_drive_down = n_min_drive_up
'rstce!n_min_drive = n_min_drive_up
			rstce.Update


			Text152 = n_min_drive_up

			Text152.Requery

			If n_min_drive_up > rstce!n_min_drive_start_up Then

				rstce.edit
				rstce!n_min_drive_start_up = Null
				rstce!n_min_drive_start_down = Null

'rstce!t_end_start_phase = Null
				rstce.Update

				MsgBox "You chose a n_min_drive_up value which is higher than n_min_drive_start_up, please correct n_min_drive_start_up!"

			End If

			rstce.Close

		End If
	End If



End Sub

Private Sub Text197_AfterUpdate()
	Dim wrkWS1
	Dim dbsDB1
	Dim rstce
	Dim n_max1 As Integer, IDclass As Byte


	Set wrkWS1 = DBEngine.Workspaces(0)
	Set dbsDB1 = wrkWS1.Databases(0)
'...

	Set rstce = dbsDB1.OpenRecordset("ST_vehicle_info", DB_OPEN_DYNASET)

	rstce.MoveFirst

	IDclass = rstce!IDclass

	If IDclass = 1 And (Text197 >= 64.4 Or Text197 < 50) Then

		Text197 = ""
		Text197.Requery

		MsgBox "The capped speed must be between 50 km/h and 64 km/h!"

		Exit Sub

	ElseIf IDclass = 2 And (Text197 >= 123.1 Or Text197 < 52) Then

		Text197 = ""
		Text197.Requery

		MsgBox "The capped speed must be between 52 km/h and 122 km/h!"

		Exit Sub

	ElseIf IDclass > 3 And (Text197 >= 131.3 Or Text197 < 60) Then

		Text197 = ""
		Text197.Requery

		MsgBox "The capped speed must be between 60 km/h and 130 km/h!"

		Exit Sub

	Else


		rstce.edit
		rstce!v_cap = Text197

		rstce.Update
		rstce.Close

	End If

End Sub

Public Sub Calculate_speed_capped_cycle()
	Dim wrkWS1
	Dim dbsDB1
	Dim rstce, rstae, rstbe
	Dim n_max1 As Integer, IDclass As Byte
	Dim aa As Double, bb As Double, cc As Double, dd As Double, ee As Double, dt As Single, t As Long, n As Integer, i As Integer, j As Integer
	Dim n_min_drive_fact As Double, n_min_2_fact As Double, m As Integer, k As Integer
	Dim t_last_medium As Integer, t_last_high As Integer, t_last_exhigh As Integer, speed_cap As Integer, missing_time_medium As Integer, missing_time_high As Integer, missing_time_exhigh As Integer
	Dim t_last_exhigh3 As Integer, missing_time_exhigh3 As Integer

	Set wrkWS1 = DBEngine.Workspaces(0)
	Set dbsDB1 = wrkWS1.Databases(0)
'...

	Set rstce = dbsDB1.OpenRecordset("ST_vehicle_info", DB_OPEN_DYNASET)

	rstce.MoveFirst

	DoCmd.OpenQuery "A TB_speed_cap_param del"
	DoCmd.OpenQuery "A TB_speed_cap_param anf2"

	DoCmd.OpenQuery "A TB_t_last del"
	DoCmd.OpenQuery "A TB_t_last anf medium2"
	DoCmd.OpenQuery "A TB_t_last anf high2"
	DoCmd.OpenQuery "A TB_t_last anf exhigh2"
	DoCmd.OpenQuery "A TB_t_last anf exhigh3"

	speed_cap = rstce!v_cap

	Set rstae = dbsDB1.OpenRecordset("TB_t_last", DB_OPEN_DYNASET)
	rstae.MoveFirst

	If rstae!cycle_part = 2 Then

		t_last_medium = rstae!t_last

		If rstce!IDclass > 1 Then

			rstae.MoveNext

			t_last_high = rstae!t_last

			rstae.MoveNext

			t_last_exhigh = rstae!t_last

		Else

			t_last_high = 0
			t_last_exhigh = 0

			If rstce!Cycle <> "WLTC" Then

				rstae.MoveNext
				t_last_exhigh3 = rstae!t_last

'MsgBox "t_last_exhigh3 = " & t_last_exhigh3

			Else

			End If

		End If

	ElseIf rstae!cycle_part = 3 Then

		t_last_medium = 0

		t_last_high = rstae!t_last

		If rstce!IDclass > 1 Then

			rstae.MoveNext

			If Not rstae.EOF Then

				t_last_exhigh = rstae!t_last

			End If

		End If

	ElseIf rstae!cycle_part = 4 Then

		t_last_medium = 0
		t_last_high = 0

		t_last_exhigh = rstae!t_last

	End If


	rstae.Close

	Set rstae = dbsDB1.OpenRecordset("TB_speed_cap_param", DB_OPEN_DYNASET)
	rstae.MoveFirst

	If rstae!cycle_part = 2 Then

		missing_time_medium = rstae!missing_time

		If rstce!IDclass > 1 Or (rstce!IDclass = 1 And rstce!Cycle <> "WLTC") Then


			rstae.MoveNext

			missing_time_high = rstae!missing_time

			rstae.MoveNext

			missing_time_exhigh = rstae!missing_time

'#################################

			If rstce!IDclass = 1 And rstce!Cycle <> "WLTC" Then

				rstae.MoveNext

				missing_time_exhigh3 = rstae!missing_time
'MsgBox "missing_time_exhigh3 = " & missing_time_exhigh3

			End If
		End If

	ElseIf rstae!cycle_part = 3 Then

		missing_time_medium = 0

		missing_time_high = rstae!missing_time

		rstae.MoveNext

		If Not rstae.EOF Then

			missing_time_exhigh = rstae!missing_time

		End If

	ElseIf rstae!cycle_part = 4 Then

		missing_time_medium = 0
		missing_time_high = 0

		missing_time_exhigh = rstae!missing_time

	End If

	rstae.Close

	DoCmd.OpenQuery "A gearshift_table_zw del"

	Set rstae = dbsDB1.OpenRecordset("A gearshift_table sort", DB_OPEN_DYNASET)
	rstae.MoveFirst

	t = rstae!Tim

	Set rstbe = dbsDB1.OpenRecordset("gearshift_table_zw", DB_OPEN_DYNASET)

	rstbe.AddNew

	rstbe!eng_no = rstce!eng_no
	rstbe!vehicle_no = rstce!vehicle_no
	rstbe!description = rstce!description
	rstbe!IDclass = rstce!IDclass
	rstbe!part = rstae!part
	rstbe!part_text = rstae!part_text

	rstbe!Tim = t

	rstbe!v_cap = rstae!v_cap
	rstbe!v = rstae!v_cap

	rstbe.Update

	If t_last_medium = 0 Then

		Do While rstae!part < 3

			rstae.MoveNext

			t = t + 1

			rstbe.AddNew

			rstbe!eng_no = rstce!eng_no
			rstbe!vehicle_no = rstce!vehicle_no
			rstbe!description = rstce!description
			rstbe!IDclass = rstce!IDclass
			rstbe!part = rstae!part
			rstbe!part_text = rstae!part_text
			rstbe!Tim = t

			rstbe!v_cap = rstae!v_cap
			rstbe!v = rstae!v_cap

			rstbe.Update

		Loop

	Else

		Do Until rstae!Tim = t_last_medium

			rstae.MoveNext

			t = t + 1

			rstbe.AddNew

			rstbe!eng_no = rstce!eng_no
			rstbe!vehicle_no = rstce!vehicle_no
			rstbe!description = rstce!description
			rstbe!IDclass = rstce!IDclass
			rstbe!part = rstae!part
			rstbe!part_text = rstae!part_text
			rstbe!Tim = t

			rstbe!v_cap = rstae!v_cap
			rstbe!v = rstae!v_cap

			rstbe.Update

		Loop

		For i = 1 To missing_time_medium

			t = t + 1

			rstbe.AddNew

			rstbe!eng_no = rstce!eng_no
			rstbe!vehicle_no = rstce!vehicle_no
			rstbe!description = rstce!description
			rstbe!IDclass = rstce!IDclass
			rstbe!part = rstae!part
			rstbe!part_text = rstae!part_text
			rstbe!Tim = t

			rstbe!v_cap = speed_cap
			rstbe!v = rstae!v_cap

			rstbe.Update

		Next i


		Do While rstae!part < 3

			rstae.MoveNext

			t = t + 1

			rstbe.AddNew

			rstbe!eng_no = rstce!eng_no
			rstbe!vehicle_no = rstce!vehicle_no
			rstbe!description = rstce!description
			rstbe!IDclass = rstce!IDclass
			rstbe!part = rstae!part
			rstbe!part_text = rstae!part_text
			rstbe!Tim = t

			rstbe!v_cap = rstae!v_cap
			rstbe!v = rstae!v_cap

			rstbe.Update

		Loop

	End If

	If rstce!IDclass = 1 And rstce!Cycle = "WLTC" Then

		Do Until rstae.EOF

			rstae.MoveNext

			If Not rstae.EOF Then
'MsgBox "part = " & rstae!part
'MsgBox "tim = " & rstae!tim

				t = t + 1

				rstbe.AddNew

				rstbe!eng_no = rstce!eng_no
				rstbe!vehicle_no = rstce!vehicle_no
				rstbe!description = rstce!description
				rstbe!IDclass = rstce!IDclass
				rstbe!part = rstae!part
				rstbe!part_text = rstae!part_text
				rstbe!Tim = t

				rstbe!v_cap = rstae!v_cap
				rstbe!v = rstae!v_cap

				rstbe.Update

			End If

		Loop

		GoTo cap_end

	ElseIf rstce!IDclass = 1 And rstce!Cycle <> "WLTC" Then

		Do While rstae!part < 5

			rstae.MoveNext

			t = t + 1

			rstbe.AddNew

			rstbe!eng_no = rstce!eng_no
			rstbe!vehicle_no = rstce!vehicle_no
			rstbe!description = rstce!description
			rstbe!IDclass = rstce!IDclass
			rstbe!part = rstae!part
			rstbe!part_text = rstae!part_text
			rstbe!Tim = t

			rstbe!v_cap = rstae!v_cap
			rstbe!v = rstae!v_cap

			rstbe.Update

		Loop

'#######################################

		Do Until rstae!Tim = t_last_exhigh3

			rstae.MoveNext

			t = t + 1

			rstbe.AddNew

			rstbe!eng_no = rstce!eng_no
			rstbe!vehicle_no = rstce!vehicle_no
			rstbe!description = rstce!description
			rstbe!IDclass = rstce!IDclass
			rstbe!part = rstae!part
			rstbe!part_text = rstae!part_text
			rstbe!Tim = t

			rstbe!v_cap = rstae!v_cap
			rstbe!v = rstae!v_cap

			rstbe.Update

		Loop

		For i = 1 To missing_time_exhigh3

			t = t + 1

			rstbe.AddNew

			rstbe!eng_no = rstce!eng_no
			rstbe!vehicle_no = rstce!vehicle_no
			rstbe!description = rstce!description
			rstbe!IDclass = rstce!IDclass
			rstbe!part = rstae!part
			rstbe!part_text = rstae!part_text
			rstbe!Tim = t

			rstbe!v_cap = speed_cap
			rstbe!v = rstae!v_cap

			rstbe.Update

		Next i


		Do While rstae!part < 6

			rstae.MoveNext

			t = t + 1

			rstbe.AddNew

			rstbe!eng_no = rstce!eng_no
			rstbe!vehicle_no = rstce!vehicle_no
			rstbe!description = rstce!description
			rstbe!IDclass = rstce!IDclass
			rstbe!part = rstae!part
			rstbe!part_text = rstae!part_text
			rstbe!Tim = t

			rstbe!v_cap = rstae!v_cap
			rstbe!v = rstae!v_cap

			rstbe.Update

		Loop

		Do Until rstae.EOF

			rstae.MoveNext

			If Not rstae.EOF Then
'MsgBox "part = " & rstae!part
'MsgBox "tim = " & rstae!tim

				t = t + 1

				rstbe.AddNew

				rstbe!eng_no = rstce!eng_no
				rstbe!vehicle_no = rstce!vehicle_no
				rstbe!description = rstce!description
				rstbe!IDclass = rstce!IDclass
				rstbe!part = rstae!part
				rstbe!part_text = rstae!part_text
				rstbe!Tim = t

				rstbe!v_cap = rstae!v_cap
				rstbe!v = rstae!v_cap

				rstbe.Update

			End If

		Loop

		GoTo cap_end

'#################################################################

	End If

	If t_last_high = 0 Then

		Do While rstae!part < 4

			rstae.MoveNext

			t = t + 1

			rstbe.AddNew

			rstbe!eng_no = rstce!eng_no
			rstbe!vehicle_no = rstce!vehicle_no
			rstbe!description = rstce!description
			rstbe!IDclass = rstce!IDclass
			rstbe!part = rstae!part
			rstbe!part_text = rstae!part_text
			rstbe!Tim = t

			rstbe!v_cap = rstae!v_cap
			rstbe!v = rstae!v_cap

			rstbe.Update

		Loop

	Else

		Do Until rstae!Tim = t_last_high

			rstae.MoveNext

			t = t + 1

			rstbe.AddNew

			rstbe!eng_no = rstce!eng_no
			rstbe!vehicle_no = rstce!vehicle_no
			rstbe!description = rstce!description
			rstbe!IDclass = rstce!IDclass
			rstbe!part = rstae!part
			rstbe!part_text = rstae!part_text
			rstbe!Tim = t

			rstbe!v_cap = rstae!v_cap
			rstbe!v = rstae!v_cap

			rstbe.Update

		Loop

		For i = 1 To missing_time_high

			t = t + 1

			rstbe.AddNew

			rstbe!eng_no = rstce!eng_no
			rstbe!vehicle_no = rstce!vehicle_no
			rstbe!description = rstce!description
			rstbe!IDclass = rstce!IDclass
			rstbe!part = rstae!part
			rstbe!part_text = rstae!part_text
			rstbe!Tim = t

			rstbe!v_cap = speed_cap
			rstbe!v = rstae!v_cap

			rstbe.Update

		Next i

'????????????????????????????????????????????

		Do While rstae!part < 4

			rstae.MoveNext

			t = t + 1

			rstbe.AddNew

			rstbe!eng_no = rstce!eng_no
			rstbe!vehicle_no = rstce!vehicle_no
			rstbe!description = rstce!description
			rstbe!IDclass = rstce!IDclass
			rstbe!part = rstae!part
			rstbe!part_text = rstae!part_text
			rstbe!Tim = t

			rstbe!v_cap = rstae!v_cap
			rstbe!v = rstae!v_cap

			rstbe.Update

		Loop

	End If

	If rstce!Cycle = "WLTC" Or (rstce!Cycle = "EVAP purge" And t_last_medium > 0) Then

		Do Until rstae!Tim = t_last_exhigh

			rstae.MoveNext

			t = t + 1

			rstbe.AddNew

			rstbe!eng_no = rstce!eng_no
			rstbe!vehicle_no = rstce!vehicle_no
			rstbe!description = rstce!description
			rstbe!IDclass = rstce!IDclass
			rstbe!part = rstae!part
			rstbe!part_text = rstae!part_text
			rstbe!Tim = t

			rstbe!v_cap = rstae!v_cap
			rstbe!v = rstae!v_cap

			rstbe.Update

		Loop

		For i = 1 To missing_time_exhigh

			t = t + 1

			rstbe.AddNew

			rstbe!eng_no = rstce!eng_no
			rstbe!vehicle_no = rstce!vehicle_no
			rstbe!description = rstce!description
			rstbe!IDclass = rstce!IDclass
			rstbe!part = rstae!part
			rstbe!part_text = rstae!part_text
			rstbe!Tim = t

			rstbe!v_cap = speed_cap
			rstbe!v = rstae!v_cap

			rstbe.Update

		Next i

		Do While Not rstae.EOF

			rstae.MoveNext

			If Not rstae.EOF Then

				t = t + 1

				rstbe.AddNew

				rstbe!eng_no = rstce!eng_no
				rstbe!vehicle_no = rstce!vehicle_no
				rstbe!description = rstce!description
				rstbe!IDclass = rstce!IDclass
				rstbe!part = rstae!part
				rstbe!part_text = rstae!part_text
				rstbe!Tim = t

				rstbe!v_cap = rstae!v_cap
				rstbe!v = rstae!v_cap

				rstbe.Update

			End If

		Loop

	Else

		Do While Not rstae.EOF

			rstae.MoveNext

			If Not rstae.EOF Then

				t = t + 1

				rstbe.AddNew

				rstbe!eng_no = rstce!eng_no
				rstbe!vehicle_no = rstce!vehicle_no
				rstbe!description = rstce!description
				rstbe!IDclass = rstce!IDclass
				rstbe!part = rstae!part
				rstbe!part_text = rstae!part_text
				rstbe!Tim = t

				rstbe!v_cap = rstae!v_cap
				rstbe!v = rstae!v_cap

				rstbe.Update

			End If

		Loop

	End If

	cap_end:

	rstae.Close
	rstbe.Close
	rstce.Close

	DoCmd.OpenQuery "A gearshift_table_zw act"

	DoCmd.OpenQuery "A gearshift_table_zw gearshift_table"

'calculate accelerations #############################################################

	n = 0
	m = 0
	k = 0
	j = 0



	DoCmd.OpenQuery "A gearshift_table del"
	DoCmd.OpenQuery "A gearshift_table gearshift_table_zw"




End Sub

Public Sub numbering_ST()
	Dim wrkWS1
	Dim dbsDB1
	Dim rstde
	Dim rstce



	Dim n As Integer
	Dim cc As Double, cc_old As Double, m As Integer


	Set wrkWS1 = DBEngine.Workspaces(0)
	Set dbsDB1 = wrkWS1.Databases(0)

'GoTo restart


	DoCmd.OpenQuery "A gearshift_table Ind_ST"


	Set rstce = dbsDB1.OpenRecordset("A gearshift_table sort", DB_OPEN_DYNASET)
	rstce.MoveFirst


	cc = 0
	cc_old = 0
	m = 0
	n = 0


	Do Until rstce.EOF



		If rstce![Ind_ST] = True Then


			If m = 0 Then

				rstce.edit

				n = n + 1
				rstce![n_ST] = n
				m = 1
				rstce.Update
't1 = rstce![n_acc]
'Me.Repaint


			Else

				rstce.edit

				rstce![n_ST] = n

				rstce.Update
't1 = rstce![n_acc]
'Me.Repaint


			End If



		Else

			m = 0

			GoTo next_dataset


		End If



		next_dataset:






		rstce.MoveNext




	Loop

	rstce.Close


End Sub

Private Sub Text221_AfterUpdate()
	Dim wrkWS1
	Dim dbsDB1
	Dim rstce
	Dim n_min_drive_down As Integer, n_min_drive_down_max As Integer, n As Integer


	Set wrkWS1 = DBEngine.Workspaces(0)
	Set dbsDB1 = wrkWS1.Databases(0)
'...

	Set rstce = dbsDB1.OpenRecordset("ST_vehicle_info", DB_OPEN_DYNASET)

	rstce.MoveFirst

	n_min_drive_down_max = 2 * rstce!n_min_drive_set

	n_min_drive_down = Text221

	If n_min_drive_down <= rstce!n_min_drive_set Then

		MsgBox "n_min_drive_down must be higher than n_min_drive_set!"

		rstce.edit
		rstce!n_min_drive_down_modified = False
		rstce.Update
		rstce.Close

		Exit Sub

	ElseIf n_min_drive_down > n_min_drive_down_max Then

		MsgBox "n_min_drive_down must not be higher than 2*n_min_drive_set!"

		rstce.edit
		rstce!n_min_drive_down_modified = False
		rstce.Update
		rstce.Close

		Exit Sub


	Else

		If Ko219 = False Then

			rstce.edit
			rstce!n_min_drive_down_modified = False
			rstce.Update
			rstce.Close

			Exit Sub

		Else

			rstce.edit
			rstce!n_min_drive_down_modified = True
			rstce!n_min_drive_down = n_min_drive_down
			rstce.Update
			rstce.Close

		End If
	End If

	Text224 = n_min_drive_down

	Text224.Requery

End Sub

Public Sub gearshift_calculation2b()
	Dim wrkWS1
	Dim dbsDB1
	Dim rstce, rstbe
	Dim rstde, rstae
	Dim rstee, rstfe, rstge, rsthe, rstie, rstke
	Dim aa As Double, bb As Double, cc As Double, dd As Double, ee As Double, dt As Single, t As Single, n As Double, m As Integer, k As Integer, h As Integer
	Dim g_acc As Byte, g_cruise As Byte, g_dec As Byte, n_norm_max As Double, P_res As Double, j As Integer, i As Integer, l As Integer, o As Integer, P As Integer
	Dim n_norm_1 As Double, n_norm_2 As Double, n_norm_3 As Double, n_norm_4 As Double, n_norm_5 As Double, n_norm_6 As Double, n_norm As Double
	Dim P_norm_1 As Double, P_norm_2 As Double, P_norm_3 As Double, P_norm_4 As Double, P_norm_5 As Double, P_norm_6 As Double
	Dim v_1 As Double, v_2 As Double, P_1 As Double, P_2 As Double, g_0 As Byte, g_1 As Byte, g_2 As Byte, P_a As Double, P_tot As Double
	Dim a_1 As Double, a_2 As Double, a_3 As Double, a_4 As Double, a_5 As Double, a_6 As Double
	Dim g_2s As Byte, g_2e As Byte, g_2b As Byte, v As Double, P_max As Double, z As Double, IDn_norm As Integer
	Dim n_orig As Double, v_orig As Double, a As Double, v_de As Double, flag As Byte, flag2 As Byte, flag3 As Byte
	Dim a_de As Double, n_de As Double, n_norm_de As Double, IDn_norm_de As Integer, P_a_de As Double, P_tot_de As Double, P_res_de As Double, P_max_de As Double
	Dim downscale_factor As Double, n_max_wot As Double, n_min_wot As Double, Pwot As Double, Pavai As Double, ASM As Double, t_end_i As Integer, t_end_j As Integer, t_end_k As Integer
	Dim SM0 As Double, kr As Double, t_start As Integer, m_old As Integer, highidle As Double, Pavai_hidle As Double, g_2s_i As Byte, g_2s_j As Byte, g_2s_k As Byte
	Dim t_l As Integer, t_j As Integer, flag_text7 As Byte

	flag_text7 = 0

	m_old = 0
	m = 0
	n = 0
	j = 0
	t = 0

	P = 0

	Set wrkWS1 = DBEngine.Workspaces(0)
	Set dbsDB1 = wrkWS1.Databases(0)
	Text85 = ""

	Text20 = "calculate gear use"
	Me.Repaint




	Set rstae = dbsDB1.OpenRecordset("A ST_vehicle_info open", DB_OPEN_DYNASET)
	rstae.MoveFirst

	SM0 = rstae!SM0
	kr = rstae!kr



	flag = 0

	If Rahmen36 = 3 Then

		GoTo weiter_NEDC_2


	End If



	Set rstie = dbsDB1.OpenRecordset("A TA_Pwot sort", DB_OPEN_DYNASET)
	rstie.MoveLast
	n_max_wot = rstie.n

	Set rstke = dbsDB1.OpenRecordset("A TA_Pwot sort", DB_OPEN_DYNASET)

	Set rstbe = dbsDB1.OpenRecordset("A gearshift_table sort", DB_OPEN_DYNASET)

	rstie.MoveFirst
	n_min_wot = rstie.n

	rstke.MoveFirst
	rstke.MoveNext

	P = 1

	n = 0
	m = 0
	k = 0
	j = 0
	m_old = 0

	Set rstce = dbsDB1.OpenRecordset("A gearshift_table sort", DB_OPEN_DYNASET)
	Set rstde = dbsDB1.OpenRecordset("A gearshift_table sort", DB_OPEN_DYNASET)



'##################################################################################################
'calculation of engine speed and power
'===================================================================================================



	rstbe.MoveFirst

	m = 0
	n = 0


	Do Until rstbe.EOF


		If rstbe!gear < rstbe!g_min And rstbe!a >= 0 And rstbe!gear > 0 Then

			rstbe.edit

			rstbe!gear = rstbe!g_min
			rstbe!clutch = "engaged"

			rstbe.Update

			m = m + 1

		ElseIf rstbe!gear > rstbe!g_max And rstbe!gear_modification = "" Then

			rstbe.edit

			rstbe!gear = rstbe!g_max
			rstbe!clutch = "engaged"

			rstbe.Update

			n = n + 1

		ElseIf rstbe!v >= 1 Then

			rstbe.edit

			rstbe!clutch = "engaged"

			rstbe.Update

		End If

		rstbe.MoveNext

	Loop


'1. gear 1 s before start
'========================================================================================================

	rstbe.MoveFirst

	rstce.MoveFirst
	rstce.MoveNext

	Do Until rstce.EOF

		flag3 = 0




		If (rstbe!v = 0 And rstbe!a = 0 And rstce!v = 0 And rstce!a > 0) Or (rstbe!v < 1 And rstbe!a > 0) Then

			rstbe.edit
			rstbe!gear = 1
			rstbe!g_min = 1
			rstbe!g_max = 1
			rstbe!clutch = "disengaged"
			rstbe.Update

		End If

		rstbe.MoveNext
		rstce.MoveNext

	Loop

'##########################################################################

	rstbe.MoveFirst


	rstce.MoveFirst
	rstce.MoveNext



	flag3 = 0

	Do Until rstce.EOF




		weiter_flag3:

		rstie.MoveFirst

		rstke.MoveLast

		n_max_wot = rstke!n
		n_min_wot = rstie!n

		rstke.MoveFirst
		rstke.MoveNext

'############################################################################

		If (rstbe!gear = 0 Or rstbe!gear = 1) And rstbe!v < 1 Then

'ßßßßßßßßßßßßßßßßßßßßßßßßßßßßßßßßßßßßßßßßßßßßßßßßßßßßßßßßßßßßßßßßßßßßßßßßßßßßßßßßß

			rstbe.edit
			rstbe!n = rstae!idling_speed
			rstbe!nc = rstae!idling_speed
			rstbe!n_kl = Int(rstae!idling_speed / 10 + 0.5) * 10

			rstbe!P_max = rstie!Pavai
			rstbe!Pwot_wo_margin = rstie!Pwot
			rstbe!safety_margin_Pwot = 1 - rstie!Pavai / rstie!Pwot

			If rstbe!gear = 1 Then
				rstbe!clutch = "disengaged"
			Else
				rstbe!clutch = "engaged, gear lever in neutral"
			End If

			rstbe.Update

'##############################################################################

		ElseIf rstbe!gear = 0 And rstbe!v >= 1 Then

			rstbe.edit
			rstbe!n = rstae!idling_speed
			rstbe!nc = rstae!idling_speed
			rstbe!n_kl = Int(rstae!idling_speed / 10 + 0.5) * 10

			rstbe!P_max = rstie!Pavai
			rstbe!Pwot_wo_margin = rstie!Pwot
			rstbe!safety_margin_Pwot = 1 - rstie!Pavai / rstie!Pwot

			rstbe!clutch = "disengaged"

			rstbe.Update

'################################################################################


		ElseIf rstbe!gear = 1 And rstbe!v >= 1 Then

			rstie.MoveFirst
			rstke.MoveFirst
			rstke.MoveNext

			n = rstbe!n_1

			If n <= rstie!n And Not IsNull(rstbe!n_1) Then

				Pwot = rstie!Pwot
				Pavai = rstie!Pavai

			ElseIf n = rstke!n Then

				Pwot = rstke!Pwot
				Pavai = rstke!Pavai

			ElseIf n > rstie!n Then

				If n > rstke!n Then
					Do Until rstie!n < n And n <= rstke!n

						rstie.MoveNext
						rstke.MoveNext

					Loop

				End If


				Pwot = rstie!Pwot + (rstke!Pwot - rstie!Pwot) / (rstke!n - rstie!n) * (n - rstie!n)
				Pavai = rstie!Pavai + (rstke!Pavai - rstie!Pavai) / (rstke!n - rstie!n) * (n - rstie!n)


			End If

			rstbe.edit

			rstie.MoveFirst
			rstke.MoveFirst
			rstke.MoveNext

			If rstbe!n_01 < rstae!idling_speed And rstbe!a < 0 Then

				rstbe!clutch = "disengaged"

			End If

			If n > rstbe!n_01 Then

				rstbe!clutch = "undefined"

			End If


			If (n < n_min_wot Or n < rstae!idling_speed * rstae!facc_g2) And rstbe!a >= 0 Then

				rstbe!clutch = "undefined"

			End If


			rstbe!nc = n
			rstbe!n_kl = Int(n / 10 + 0.5) * 10
			rstbe!P_max = Pavai
			rstbe!Pwot_wo_margin = Pwot
			rstbe!safety_margin_Pwot = 1 - Pavai / Pwot

			rstbe.Update


' gear 2 ################################################################################################

		ElseIf rstbe!gear = 2 And rstbe!v >= 1 Then


			rstie.MoveFirst
			rstke.MoveFirst
			rstke.MoveNext

			n = rstbe!n_2

			If n <= rstie!n And Not IsNull(rstbe!n_2) Then

				Pwot = rstie!Pwot
				Pavai = rstie!Pavai

			ElseIf n = rstke!n Then

				Pwot = rstke!Pwot
				Pavai = rstke!Pavai

			ElseIf n > rstie!n Then

				If n > rstke!n Then
					Do Until rstie!n < n And n <= rstke!n

						rstie.MoveNext
						rstke.MoveNext

					Loop

				End If


				Pwot = rstie!Pwot + (rstke!Pwot - rstie!Pwot) / (rstke!n - rstie!n) * (n - rstie!n)
				Pavai = rstie!Pavai + (rstke!Pavai - rstie!Pavai) / (rstke!n - rstie!n) * (n - rstie!n)


			End If

			rstbe.edit

			rstie.MoveFirst
			rstke.MoveFirst
			rstke.MoveNext

			If rstbe!n_02 < rstae!idling_speed And rstbe!a < 0 Then

				rstbe!clutch = "disengaged"

			End If

			If n > rstbe!n_02 Then

				rstbe!clutch = "undefined"

			End If

			If (n < n_min_wot Or n < rstae!idling_speed * rstae!facc_g2) And rstbe!a >= 0 Then

				rstbe!clutch = "undefined"

			End If

			rstbe!nc = n
			rstbe!n_kl = Int(n / 10 + 0.5) * 10
			rstbe!P_max = Pavai
			rstbe!Pwot_wo_margin = Pwot
			rstbe!safety_margin_Pwot = 1 - Pavai / Pwot

			rstbe.Update

' gear 3 #################################################

		ElseIf rstbe!gear = 3 And rstbe!v >= 1 Then

			rstie.MoveFirst
			rstke.MoveFirst
			rstke.MoveNext

			n = rstbe!n_3

			If n <= rstie!n And Not IsNull(rstbe!n_3) Then

				Pwot = rstie!Pwot
				Pavai = rstie!Pavai

			ElseIf n = rstke!n Then

				Pwot = rstke!Pwot
				Pavai = rstke!Pavai

			ElseIf n > rstie!n Then

				If n > rstke!n Then
					Do Until rstie!n < n And n <= rstke!n

						rstie.MoveNext
						rstke.MoveNext

					Loop

				End If



				Pwot = rstie!Pwot + (rstke!Pwot - rstie!Pwot) / (rstke!n - rstie!n) * (n - rstie!n)
				Pavai = rstie!Pavai + (rstke!Pavai - rstie!Pavai) / (rstke!n - rstie!n) * (n - rstie!n)


			End If

			rstbe.edit



			rstbe!nc = n
			rstbe!n_kl = Int(n / 10 + 0.5) * 10
			rstbe!P_max = Pavai
			rstbe!Pwot_wo_margin = Pwot
			rstbe!safety_margin_Pwot = 1 - Pavai / Pwot


			rstbe.Update


' gear 4 #################################################

		ElseIf rstbe!gear = 4 And rstbe!v >= 1 Then

			rstie.MoveFirst
			rstke.MoveFirst
			rstke.MoveNext

			n = rstbe!n_4

			If n <= rstie!n And Not IsNull(rstbe!n_4) Then

				Pwot = rstie!Pwot
				Pavai = rstie!Pavai

			ElseIf n = rstke!n Then

				Pwot = rstke!Pwot
				Pavai = rstke!Pavai

			ElseIf n > rstie!n Then

				If n > rstke!n Then
					Do Until rstie!n < n And n <= rstke!n

						rstie.MoveNext
						rstke.MoveNext

					Loop

				End If



				Pwot = rstie!Pwot + (rstke!Pwot - rstie!Pwot) / (rstke!n - rstie!n) * (n - rstie!n)
				Pavai = rstie!Pavai + (rstke!Pavai - rstie!Pavai) / (rstke!n - rstie!n) * (n - rstie!n)


			End If

			rstbe.edit






			rstbe!nc = n
			rstbe!n_kl = Int(n / 10 + 0.5) * 10
			rstbe!P_max = Pavai
			rstbe!Pwot_wo_margin = Pwot
			rstbe!safety_margin_Pwot = 1 - Pavai / Pwot


			rstbe.Update


' gear 5 #################################################

		ElseIf rstbe!gear = 5 And rstbe!v >= 1 Then

			rstie.MoveFirst
			rstke.MoveFirst
			rstke.MoveNext

			n = rstbe!n_5

			If n <= rstie!n And Not IsNull(rstbe!n_5) Then

				Pwot = rstie!Pwot
				Pavai = rstie!Pavai

			ElseIf n = rstke!n Then

				Pwot = rstke!Pwot
				Pavai = rstke!Pavai

			ElseIf n > rstie!n Then

				If n > rstke!n Then
					Do Until rstie!n < n And n <= rstke!n

						rstie.MoveNext
						rstke.MoveNext

					Loop

				End If



				Pwot = rstie!Pwot + (rstke!Pwot - rstie!Pwot) / (rstke!n - rstie!n) * (n - rstie!n)
				Pavai = rstie!Pavai + (rstke!Pavai - rstie!Pavai) / (rstke!n - rstie!n) * (n - rstie!n)


			End If

			rstbe.edit


			rstbe!nc = n
			rstbe!n_kl = Int(n / 10 + 0.5) * 10
			rstbe!P_max = Pavai
			rstbe!Pwot_wo_margin = Pwot
			rstbe!safety_margin_Pwot = 1 - Pavai / Pwot


			rstbe.Update


' gear 6 #################################################

		ElseIf rstbe!gear = 6 And rstbe!v >= 1 Then

			rstie.MoveFirst
			rstke.MoveFirst
			rstke.MoveNext

			n = rstbe!n_6

			If n <= rstie!n And Not IsNull(rstbe!n_6) Then

				Pwot = rstie!Pwot
				Pavai = rstie!Pavai

			ElseIf n = rstke!n Then

				Pwot = rstke!Pwot
				Pavai = rstke!Pavai

			ElseIf n > rstie!n Then

				If n > rstke!n Then
					Do Until rstie!n < n And n <= rstke!n

						rstie.MoveNext
						rstke.MoveNext

					Loop

				End If



				Pwot = rstie!Pwot + (rstke!Pwot - rstie!Pwot) / (rstke!n - rstie!n) * (n - rstie!n)
				Pavai = rstie!Pavai + (rstke!Pavai - rstie!Pavai) / (rstke!n - rstie!n) * (n - rstie!n)


			End If

			rstbe.edit

			rstbe!nc = n
			rstbe!n_kl = Int(n / 10 + 0.5) * 10
			rstbe!P_max = Pavai
			rstbe!Pwot_wo_margin = Pwot
			rstbe!safety_margin_Pwot = 1 - Pavai / Pwot


			rstbe.Update


' gear 7 #################################################

		ElseIf rstbe!gear = 7 And rstbe!v >= 1 Then

			rstie.MoveFirst
			rstke.MoveFirst
			rstke.MoveNext

			n = rstbe!n_7

			If n <= rstie!n And Not IsNull(rstbe!n_7) Then

				Pwot = rstie!Pwot
				Pavai = rstie!Pavai

			ElseIf n = rstke!n Then

				Pwot = rstke!Pwot
				Pavai = rstke!Pavai

			ElseIf n > rstie!n Then

				If n > rstke!n Then
					Do Until rstie!n < n And n <= rstke!n

						rstie.MoveNext
						rstke.MoveNext

					Loop

				End If



				Pwot = rstie!Pwot + (rstke!Pwot - rstie!Pwot) / (rstke!n - rstie!n) * (n - rstie!n)
				Pavai = rstie!Pavai + (rstke!Pavai - rstie!Pavai) / (rstke!n - rstie!n) * (n - rstie!n)


			End If

			rstbe.edit

			rstbe!nc = n
			rstbe!n_kl = Int(n / 10 + 0.5) * 10
			rstbe!P_max = Pavai
			rstbe!Pwot_wo_margin = Pwot
			rstbe!safety_margin_Pwot = 1 - Pavai / Pwot


			rstbe.Update


' gear 8 #################################################

		ElseIf rstbe!gear = 8 And rstbe!v >= 1 Then

			rstie.MoveFirst
			rstke.MoveFirst
			rstke.MoveNext

			n = rstbe!n_8

			If n <= rstie!n And Not IsNull(rstbe!n_8) Then

				Pwot = rstie!Pwot
				Pavai = rstie!Pavai

			ElseIf n = rstke!n Then

				Pwot = rstke!Pwot
				Pavai = rstke!Pavai

			ElseIf n > rstie!n Then

				If n > rstke!n Then
					Do Until rstie!n < n And n <= rstke!n

						rstie.MoveNext
						rstke.MoveNext

					Loop

				End If



				Pwot = rstie!Pwot + (rstke!Pwot - rstie!Pwot) / (rstke!n - rstie!n) * (n - rstie!n)
				Pavai = rstie!Pavai + (rstke!Pavai - rstie!Pavai) / (rstke!n - rstie!n) * (n - rstie!n)


			End If

			rstbe.edit

			rstbe!nc = n
			rstbe!n_kl = Int(n / 10 + 0.5) * 10
			rstbe!P_max = Pavai
			rstbe!Pwot_wo_margin = Pwot
			rstbe!safety_margin_Pwot = 1 - Pavai / Pwot


			rstbe.Update


' gear 9 #################################################

		ElseIf rstbe!gear = 9 And rstbe!v >= 1 Then

			rstie.MoveFirst
			rstke.MoveFirst
			rstke.MoveNext

			n = rstbe!n_9

			If n <= rstie!n And Not IsNull(rstbe!n_9) Then

				Pwot = rstie!Pwot
				Pavai = rstie!Pavai

			ElseIf n = rstke!n Then

				Pwot = rstke!Pwot
				Pavai = rstke!Pavai

			ElseIf n > rstie!n Then

				If n > rstke!n Then
					Do Until rstie!n < n And n <= rstke!n

						rstie.MoveNext
						rstke.MoveNext

					Loop

				End If


				Pwot = rstie!Pwot + (rstke!Pwot - rstie!Pwot) / (rstke!n - rstie!n) * (n - rstie!n)
				Pavai = rstie!Pavai + (rstke!Pavai - rstie!Pavai) / (rstke!n - rstie!n) * (n - rstie!n)


			End If

			rstbe.edit

			rstbe!nc = n
			rstbe!n_kl = Int(n / 10 + 0.5) * 10
			rstbe!P_max = Pavai
			rstbe!Pwot_wo_margin = Pwot
			rstbe!safety_margin_Pwot = 1 - Pavai / Pwot


			rstbe.Update


' gear 10 #################################################

		ElseIf rstbe!gear = 10 And rstbe!v >= 1 Then

			rstie.MoveFirst
			rstke.MoveFirst
			rstke.MoveNext

			n = rstbe!n_10

			If n <= rstie!n And Not IsNull(rstbe!n_10) Then

				Pwot = rstie!Pwot
				Pavai = rstie!Pavai

			ElseIf n = rstke!n Then

				Pwot = rstke!Pwot
				Pavai = rstke!Pavai

			ElseIf n > rstie!n Then

				If n > rstke!n Then
					Do Until rstie!n < n And n <= rstke!n

						rstie.MoveNext
						rstke.MoveNext

					Loop

				End If



				Pwot = rstie!Pwot + (rstke!Pwot - rstie!Pwot) / (rstke!n - rstie!n) * (n - rstie!n)
				Pavai = rstie!Pavai + (rstke!Pavai - rstie!Pavai) / (rstke!n - rstie!n) * (n - rstie!n)


			End If

			rstbe.edit

			rstbe!nc = n
			rstbe!n_kl = Int(n / 10 + 0.5) * 10
			rstbe!P_max = Pavai
			rstbe!Pwot_wo_margin = Pwot
			rstbe!safety_margin_Pwot = 1 - Pavai / Pwot


			rstbe.Update

		End If

'###########################################################################################################


		If flag3 = 1 Then

			GoTo weiter_flag3_1

		End If

		rstbe.MoveNext
		rstce.MoveNext

	Loop

	If flag3 = 0 Then

		flag3 = 1

		If rstbe!v >= 1 And rstbe!gear > 0 Then

			GoTo weiter_flag3

		Else

			rstie.MoveFirst
			rstke.MoveFirst
			rstke.MoveNext


			rstbe.edit
			rstbe!n = rstae!idling_speed
			rstbe!nc = rstae!idling_speed
			rstbe!n_kl = Int(rstae!idling_speed / 10 + 0.5) * 10

			Pavai = rstie!Pavai
			rstbe!P_max = Pavai
			Pwot = rstie!Pwot
			rstbe!Pwot_wo_margin = Pwot
			rstbe!safety_margin_Pwot = 1 - Pavai / Pwot


			rstbe.Update

		End If

	End If

	weiter_flag3_1:

'indicate samples with P_max < P_tot_set

	rstbe.MoveFirst


	Do Until rstbe.EOF

		rstbe.edit
		If rstbe!P_max < rstbe!P_tot_set Then

			rstbe!Pmax_lower_Ptot_set = True

		Else
			rstbe!Pmax_lower_Ptot_set = False

		End If

		rstbe.Update

		rstbe.MoveNext

	Loop




'9 ######################################################################################################
'9d) correct clutch for gear 0 before stop

	rstbe.MoveFirst

	rstce.MoveFirst
	rstce.MoveNext

	Do Until rstce.EOF


		If rstbe!v >= 1 And rstce!v < 1 And (rstbe!gear = 0 Or rstbe!clutch = "disengaged") Then

			k = 0

			Do Until (rstbe!gear > 0 And (rstbe!clutch = "engaged" Or rstbe!clutch = "undefined")) Or rstbe!v <= rstce!v

				rstce.MovePrevious
				rstbe.MovePrevious

				k = k + 1

			Loop

			If rstce!v >= rstbe!v Then

				rstce.MoveNext
				rstbe.MoveNext
				k = k - 1

			End If

			For i = 1 To k

				rstce.edit
				rstce!clutch = "engaged, gear lever in neutral"
				rstce!nc = rstae!idling_speed
				If rstce!gear > 0 Then

					rstce!gear = 0
					rstce!gear_modification = rstce!gear_modification & "9d) correct gear to 0 before stop, "

				End If

				rstce.Update

				rstbe.MoveNext
				rstce.MoveNext

			Next i

			rstbe.MoveNext
			rstce.MoveNext

		Else

			rstbe.MoveNext
			rstce.MoveNext

		End If

	Loop

'****************************************************************************

	rstbe.MoveFirst

	Do Until rstbe.EOF

		rstbe.edit
		rstbe!n = rstbe!nc

		rstbe.Update

		rstbe.MoveNext

	Loop


	rstie.Close
	rstke.Close
	rstae.Close
	rstbe.Close
	rstce.Close
	rstde.Close

	weiter_NEDC_2:


End Sub





Private Sub Text230_AfterUpdate()

	Dim wrkWS1
	Dim dbsDB1
	Dim rstce
	Dim n_min_drive_start_down As Integer, n_min_drive_set As Integer, n_min_drive_up As Integer, n_min_drive_down As Integer, n_min_drive_start_up As Integer

	Set wrkWS1 = DBEngine.Workspaces(0)
	Set dbsDB1 = wrkWS1.Databases(0)
'...

	Set rstce = dbsDB1.OpenRecordset("ST_vehicle_info", DB_OPEN_DYNASET)
	rstce.MoveFirst

	n_min_drive_up = rstce!n_min_drive_up
	n_min_drive_down = rstce!n_min_drive_down
	n_min_drive_set = rstce!n_min_drive_set
	n_min_drive_start_up = Text230

	If n_min_drive_start_up <= rstce!n_min_drive_set Or n_min_drive_start_up > 2 * rstce!n_min_drive_set Or n_min_drive_start_up <= rstce!n_min_drive_up Then

		If rstce!n_min_drive_up = rstce!n_min_drive_set And n_min_drive_start_up <= rstce!n_min_drive_set Then

			MsgBox "n_min_drive_start_up must be higher than n_min_drive_set!"

		ElseIf rstce!n_min_drive_up > rstce!n_min_drive_set And n_min_drive_start_up <= rstce!n_min_drive_up Then

			MsgBox "n_min_drive_start_up must be higher than n_min_drive_up!"

		ElseIf n_min_drive_start_up > 2 * rstce!n_min_drive_set Then

			MsgBox "n_min_drive_start_up must not exceed 2*n_min_drive_set!"

		End If

		Text230 = Null
		Text234 = Null
		Text242 = Null
		Befehl28.Enabled = False

		Exit Sub

	Else

		rstce.edit

		rstce!n_min_drive_start_up = n_min_drive_start_up
		rstce!n_min_drive_start_down = Null
		rstce!t_end_start_phase = Null

		rstce.Update

		Text234 = Null
		Text242 = Null

		Befehl28.Enabled = False

		Text234.Requery
		Text242.Requery

	End If

	rstce.Close

End Sub

Private Sub Text234_AfterUpdate()

	Dim wrkWS1
	Dim dbsDB1
	Dim rstce, rstbe
	Dim t_end_start_phase As Integer

	Set wrkWS1 = DBEngine.Workspaces(0)
	Set dbsDB1 = wrkWS1.Databases(0)
'...

	Set rstce = dbsDB1.OpenRecordset("ST_vehicle_info", DB_OPEN_DYNASET)
	rstce.MoveFirst

	t_end_start_phase = Text234

	DoCmd.OpenQuery "A ST_check_tend_cold delete"


	If Rahmen36 = 1 Then

		DoCmd.OpenQuery "A check_tend_cold_WLTC"

		Set rstbe = dbsDB1.OpenRecordset("ST_check_tend_cold", DB_OPEN_DYNASET)
		rstbe.MoveFirst

		If rstbe!v <> 0 Then

			MsgBox "t_end of the start phase is outside a stop phase!"

			rstce.edit
			rstce!t_end_start_phase = Null
			rstce.Update
			rstce.Close
			rstbe.Close
			Befehl28.Enabled = False
			Text234 = Null

			Exit Sub

		Else

			rstce.edit
			rstce!t_end_start_phase = t_end_start_phase
			rstce.Update
			rstbe.Close
			Befehl28.Enabled = True

		End If

	ElseIf Rahmen36 = 2 Then

		DoCmd.OpenQuery "A check_tend_cold_purge"

		Set rstbe = dbsDB1.OpenRecordset("ST_check_tend_cold", DB_OPEN_DYNASET)
		rstbe.MoveFirst

		If rstbe!v <> 0 Then

			MsgBox "t_end of the start phase is outside a stop phase!"

			rstce.edit
			rstce!t_end_start_phase = Null
			rstce.Update
			rstce.Close
			rstbe.Close
			Befehl28.Enabled = False
			Text234 = Null

			Exit Sub

		Else

			rstce.edit
			rstce!t_end_start_phase = t_end_start_phase
			rstce.Update
			rstbe.Close
			Befehl28.Enabled = True

		End If

	ElseIf Rahmen36 = 4 Then


		DoCmd.OpenQuery "A check_tend_cold_random"

		Set rstbe = dbsDB1.OpenRecordset("ST_check_tend_cold", DB_OPEN_DYNASET)
		rstbe.MoveFirst

		If rstbe!v <> 0 Then

			MsgBox "t_end of the start phase is outside a stop phase!"

			rstce.edit
			rstce!t_end_start_phase = Null
			rstce.Update
			rstce.Close
			rstbe.Close
			Befehl28.Enabled = False
			Text234 = Null

			Exit Sub

		Else

			rstce.edit
			rstce!t_end_start_phase = t_end_start_phase
			rstce.Update
			rstbe.Close
			Befehl28.Enabled = True

		End If

	End If

	rstce.Close

End Sub

Private Sub Text242_AfterUpdate()
	Dim wrkWS1
	Dim dbsDB1
	Dim rstce
	Dim n_min_drive_start_down As Integer, n_min_drive_set As Integer, n_min_drive_up As Integer, n_min_drive_down As Integer, n_min_drive_start_up As Integer

	Set wrkWS1 = DBEngine.Workspaces(0)
	Set dbsDB1 = wrkWS1.Databases(0)
'...

	Set rstce = dbsDB1.OpenRecordset("ST_vehicle_info", DB_OPEN_DYNASET)
	rstce.MoveFirst

	n_min_drive_start_down = Text242
	n_min_drive_down = rstce!n_min_drive_down
	n_min_drive_set = rstce!n_min_drive_set
	n_min_drive_up = rstce!n_min_drive_up
	n_min_drive_start_up = rstce!n_min_drive_start_up

	If n_min_drive_up = n_min_drive_set And n_min_drive_down = n_min_drive_set Then

		If n_min_drive_start_down < n_min_drive_set Then

			MsgBox "n_min_drive_start_down must be equal to either n_min_drive_set or n_min_drive_start_up!"
			Text242 = Null
			Exit Sub

		ElseIf n_min_drive_start_down <> n_min_drive_set And n_min_drive_start_down <> n_min_drive_start_up Then

			MsgBox "n_min_drive_start_down must be equal to either n_min_drive_set or n_min_drive_start_up!"
			Text242 = Null
			Exit Sub

		Else

			rstce.edit

			rstce!n_min_drive_start_down = n_min_drive_start_down

			rstce.Update

			GoTo endsub

		End If


	ElseIf n_min_drive_down > n_min_drive_set And n_min_drive_start_down < n_min_drive_down Then

		MsgBox "n_min_drive_start_down must be equal to either n_min_drive_down or n_min_drive_start_up!"
		Text242 = Null
		Exit Sub

	ElseIf n_min_drive_down >= n_min_drive_start_up And n_min_drive_start_down <> n_min_drive_down Then

		MsgBox "n_min_drive_start_down must be equal to n_min_drive_down!"
		Text242 = Null
		Exit Sub

	ElseIf n_min_drive_down < n_min_drive_start_up And n_min_drive_start_down <> n_min_drive_down And n_min_drive_start_down <> n_min_drive_start_up Then

		MsgBox "n_min_drive_start_down must be equal to either n_min_drive_down or n_min_drive_start_up!"
		Text242 = Null
		Exit Sub

	Else

		rstce.edit

		rstce!n_min_drive_start_down = n_min_drive_start_down

		rstce.Update

	End If

	endsub:

	rstce.Close

End Sub


Public Sub gearshift_calculation2_4c()
	Dim wrkWS1
	Dim dbsDB1
	Dim rstce, rstbe
	Dim rstde, rstae
	Dim rstee, rstfe, rstge, rsthe, rstie, rstke
	Dim aa As Double, bb As Double, cc As Double, dd As Double, ee As Double, dt As Double, t As Double, n As Double, m As Integer, k As Integer, h As Integer
	Dim g_acc As Byte, g_cruise As Byte, g_dec As Byte, n_norm_max As Double, P_res As Double, j As Integer, i As Integer, l As Integer, o As Integer, P As Integer
	Dim n_norm_1 As Double, n_norm_2 As Double, n_norm_3 As Double, n_norm_4 As Double, n_norm_5 As Double, n_norm_6 As Double, n_norm As Double
	Dim P_norm_1 As Double, P_norm_2 As Double, P_norm_3 As Double, P_norm_4 As Double, P_norm_5 As Double, P_norm_6 As Double
	Dim v_1 As Double, v_2 As Double, P_1 As Double, P_2 As Double, g_0 As Byte, g_1 As Byte, g_2 As Byte, P_a As Double, P_tot As Double
	Dim a_1 As Double, a_2 As Double, a_3 As Double, a_4 As Double, a_5 As Double, a_6 As Double
	Dim g_2s As Byte, g_2e As Byte, g_2b As Byte, v As Double, P_max As Double, z As Double, IDn_norm As Integer
	Dim n_orig As Double, v_orig As Double, a As Double, v_de As Double, flag As Byte, flag2 As Byte, flag3 As Byte
	Dim a_de As Double, n_de As Double, n_norm_de As Double, IDn_norm_de As Integer, P_a_de As Double, P_tot_de As Double, P_res_de As Double, P_max_de As Double
	Dim downscale_factor As Double, n_max_wot As Double, n_min_wot As Double, Pwot As Double, Pavai As Double, ASM As Double, t_end_i As Integer, t_end_j As Integer, t_end_k As Integer
	Dim SM0 As Double, kr As Double, t_start As Integer, m_old As Integer, highidle As Double, Pavai_hidle As Double, g_2s_i As Byte, g_2s_j As Byte, g_2s_k As Byte
	Dim t_l As Integer, t_j As Integer, t_old_i As Integer, t_old_j As Integer, t_old_k As Integer, i_old As Integer, j_old As Integer, k_old As Integer
	Dim ti(300) As Long, g_start As Byte, flag_g As Byte, n_4c As Byte, flag_text7 As Byte

	m_old = 0
	m = 0
	n = 0
	j = 0
	t = 0

	flag_text7 = 0

	P = 0

	Set wrkWS1 = DBEngine.Workspaces(0)
	Set dbsDB1 = wrkWS1.Databases(0)
	Text85 = ""

	Text20 = "calculate gear use"
	Me.Repaint


	flag = 0


	P = 1

	n = 0
	m = 0
	k = 0
	j = 0
	m_old = 0

	Set rstae = dbsDB1.OpenRecordset("A ST_vehicle_info open", DB_OPEN_DYNASET)
	rstae.MoveFirst

	Set rstbe = dbsDB1.OpenRecordset("A gearshift_table sort", DB_OPEN_DYNASET)
	Set rstce = dbsDB1.OpenRecordset("A gearshift_table sort", DB_OPEN_DYNASET)
	Set rstde = dbsDB1.OpenRecordset("A gearshift_table sort", DB_OPEN_DYNASET)


	m_old = m_old + 1
	n = 0
	m = 0




'#################################################################################################################
' 4c) other cycles, corr 424 -> 444 only for other cycles

	If Kontr226 = False Then

		rstbe.MoveFirst
		rstce.MoveFirst
		rstce.MoveNext
		rstde.MoveFirst
		rstde.MoveNext
		rstde.MoveNext

		Do Until rstde.EOF


			If rstde!gear >= rstbe!gear And rstce!gear < rstbe!gear - 1 And rstce!gear > 0 Then

				If rstbe!gear = 10 And rstce!v * rstae!ndv_10 >= rstae!n_min_drive Or rstbe!gear = 9 And rstce!v * rstae!ndv_9 >= rstae!n_min_drive Or rstbe!gear = 8 And rstce!v * rstae!ndv_8 >= rstae!n_min_drive Or rstbe!gear = 7 And rstce!v * rstae!ndv_7 >= rstae!n_min_drive Or rstbe!gear = 6 And rstce!v * rstae!ndv_6 >= rstae!n_min_drive Then

					rstce.edit

					rstce!gear = rstbe!gear
					rstce!gear_modification = rstce!gear_modification & "4c) other cycles, corr 424 -> 444 or 425 -> 445, "
					rstce.Update
					m = m + 1

				ElseIf rstbe!gear = 5 And rstce!v * rstae!ndv_5 >= rstae!n_min_drive Or rstbe!gear = 4 And rstce!v * rstae!ndv_4 >= rstae!n_min_drive Or rstbe!gear = 3 And rstce!v * rstae!ndv_3 >= rstae!n_min_drive Or rstbe!gear = 2 And rstce!v * rstae!ndv_2 >= 0.9 * rstae!idling_speed Then

					rstce.edit

					rstce!gear = rstbe!gear
					rstce!gear_modification = rstce!gear_modification & "4c) other cycles, corr 424 -> 444 or 425 -> 445, "
					rstce.Update
					m = m + 1

				End If
			End If

			rstbe.MoveNext
			rstce.MoveNext
			rstde.MoveNext

		Loop

	End If


' 4(c) of annex 2 #################################################################################################

'n_4c = 1 in case of EU WLTP 2nd act amendments

	n_4c = 0

	weiter_n_4c:


'5e) #########################################################################################################
'5e) annex 2, paragraph 4 (c)

	rstbe.MoveFirst

	rstce.MoveFirst
	rstce.MoveNext

	rstde.MoveFirst
	rstde.MoveNext
	rstde.MoveNext

	Do Until rstde.EOF



		If rstbe!gear > 0 And rstce!gear = rstbe!gear + 1 And rstde!gear = rstce!gear Then

			j = 0
			i = 0
			g_ref = rstde!gear

			Do Until rstde!gear <= rstbe!gear

				rstde.MoveNext
				i = i + 1


			Loop

			If i <= 4 Then

				For k = 1 To i

					rstde.MovePrevious

					rstde.edit
					If rstde!g_min <= rstbe!gear Then
						rstde!gear = rstbe!gear
						rstde!gear_modification = rstde!gear_modification & "5e1a) correction according 4(c), "
						m = m + 1
					Else
						rstde!gear_modification = rstde!gear_modification & "5e1a) Necessary gear modification not possible, "
						n = n + 1
					End If
					rstde.Update

				Next k

				rstce.edit
				If rstce!g_min <= rstbe!gear Then
					rstce!gear = rstbe!gear
					rstce!gear_modification = rstce!gear_modification & "5e1b) correction according 4(c), "
					m = m + 1
				Else
					rstce!gear_modification = rstce!gear_modification & "5e1b) Necessary gear modification not possible, "
					n = n + 1
				End If
				rstce.Update

				If rstce!Tim <> rstde!Tim - 1 Then
					MsgBox "Error1 " & rstce!Tim & ", " & rstde!Tim
					Exit Sub
				End If


			ElseIf i > 4 Then

				For k = 1 To i

					rstde.MovePrevious

				Next k

				If rstce!Tim <> rstde!Tim - 1 Then
					MsgBox "Error2 " & rstce!Tim & ", " & rstde!Tim

					Exit Sub
				End If


			End If

		ElseIf rstbe!gear > 0 And rstce!gear = rstbe!gear + 2 And rstde!gear = rstce!gear Then

			j = 0
			i = 0
			g_ref = rstde!gear

			Do Until rstde!gear = g_ref - 1

				rstde.MoveNext
				i = i + 1

			Loop

			If i <= 4 Then

				For k = 1 To i

					rstde.MovePrevious

					rstde.edit
					If rstde!g_min <= g_ref - 1 Then
						rstde!gear = g_ref - 1
						rstde!gear_modification = rstde!gear_modification & "5e2a) correction according 4(c), "
						m = m + 1
					Else
						rstde!gear_modification = rstde!gear_modification & "5e2a) Necessary gear modification not possible, "
						n = n + 1
					End If
					rstde.Update

				Next k

				rstce.edit
				If rstce!g_min <= g_ref - 1 Then
					rstce!gear = g_ref - 1
					rstce!gear_modification = rstce!gear_modification & "5e2b) correction according 4(c), "
					m = m + 1
				Else
					rstce!gear_modification = rstce!gear_modification & "5e2b) Necessary gear modification not possible, "
					n = n + 1
				End If
				rstce.Update

				If rstce!Tim <> rstde!Tim - 1 Then
					MsgBox "Error3"
					Exit Sub
				End If


			ElseIf i > 4 Then

				For k = 1 To i

					rstde.MovePrevious

				Next k

				If rstce!Tim <> rstde!Tim - 1 Then
					MsgBox "Error4"
					Exit Sub
				End If


			End If

		End If

'###########################################################################################################

		rstbe.MoveNext
		rstce.MoveNext
		rstde.MoveNext

	Loop


	If n_4c = 0 Then

		n_4c = 1

		GoTo weiter_n_4c

	End If


' end of 4(c) ###################################################################################################

	rstae.Close
	rstbe.Close
	rstce.Close
	rstde.Close

	Text253 = Text253 + m



End Sub

Public Sub gearshift_calculation2_4df()
	Dim wrkWS1
	Dim dbsDB1
	Dim rstce, rstbe
	Dim rstde, rstae
	Dim rstee, rstfe, rstge, rsthe, rstie, rstke
	Dim aa As Double, bb As Double, cc As Double, dd As Double, ee As Double, dt As Double, t As Double, n As Double, m As Integer, k As Integer, h As Integer
	Dim g_acc As Byte, g_cruise As Byte, g_dec As Byte, n_norm_max As Double, P_res As Double, j As Integer, i As Integer, l As Integer, o As Integer, P As Integer
	Dim n_norm_1 As Double, n_norm_2 As Double, n_norm_3 As Double, n_norm_4 As Double, n_norm_5 As Double, n_norm_6 As Double, n_norm As Double
	Dim P_norm_1 As Double, P_norm_2 As Double, P_norm_3 As Double, P_norm_4 As Double, P_norm_5 As Double, P_norm_6 As Double
	Dim v_1 As Double, v_2 As Double, P_1 As Double, P_2 As Double, g_0 As Byte, g_1 As Byte, g_2 As Byte, P_a As Double, P_tot As Double
	Dim a_1 As Double, a_2 As Double, a_3 As Double, a_4 As Double, a_5 As Double, a_6 As Double
	Dim g_2s As Byte, g_2e As Byte, g_2b As Byte, v As Double, P_max As Double, z As Double, IDn_norm As Integer
	Dim n_orig As Double, v_orig As Double, a As Double, v_de As Double, flag As Byte, flag2 As Byte, flag3 As Byte
	Dim a_de As Double, n_de As Double, n_norm_de As Double, IDn_norm_de As Integer, P_a_de As Double, P_tot_de As Double, P_res_de As Double, P_max_de As Double
	Dim downscale_factor As Double, n_max_wot As Double, n_min_wot As Double, Pwot As Double, Pavai As Double, ASM As Double, t_end_i As Integer, t_end_j As Integer, t_end_k As Integer
	Dim SM0 As Double, kr As Double, t_start As Integer, m_old As Integer, highidle As Double, Pavai_hidle As Double, g_2s_i As Byte, g_2s_j As Byte, g_2s_k As Byte
	Dim t_l As Integer, t_j As Integer, t_old_i As Integer, t_old_j As Integer, t_old_k As Integer, i_old As Integer, j_old As Integer, k_old As Integer
	Dim ti(300) As Long, g_start As Byte, flag_g As Byte, n_4c As Byte, flag_text7 As Byte

	m_old = 0
	m = 0
	n = 0
	j = 0
	t = 0


	P = 0

	Set wrkWS1 = DBEngine.Workspaces(0)
	Set dbsDB1 = wrkWS1.Databases(0)
	Text85 = ""

	Text20 = "calculate gear use"
	Me.Repaint




	Set rstae = dbsDB1.OpenRecordset("A ST_vehicle_info open", DB_OPEN_DYNASET)
	rstae.MoveFirst

	SM0 = rstae!SM0
	kr = rstae!kr



	Set rstie = dbsDB1.OpenRecordset("A TA_Pwot sort", DB_OPEN_DYNASET)
	rstie.MoveLast
	n_max_wot = rstie.n

	Set rstke = dbsDB1.OpenRecordset("A TA_Pwot sort", DB_OPEN_DYNASET)

	Set rstbe = dbsDB1.OpenRecordset("A gearshift_table sort", DB_OPEN_DYNASET)

	rstie.MoveFirst
	rstke.MoveFirst
	rstke.MoveNext

	P = 1

	n = 0
	m = 0
	k = 0
	j = 0
	m_old = 0




	Set rstce = dbsDB1.OpenRecordset("A gearshift_table sort", DB_OPEN_DYNASET)
	Set rstde = dbsDB1.OpenRecordset("A gearshift_table sort", DB_OPEN_DYNASET)
	Set rstee = dbsDB1.OpenRecordset("A gearshift_table sort", DB_OPEN_DYNASET)
	Set rstfe = dbsDB1.OpenRecordset("A gearshift_table sort", DB_OPEN_DYNASET)
	Set rstge = dbsDB1.OpenRecordset("A gearshift_table sort", DB_OPEN_DYNASET)
	Set rsthe = dbsDB1.OpenRecordset("A gearshift_table sort", DB_OPEN_DYNASET)

'6) 4(d) of annex 2 ###################################################################################################################

' New for amendment 6: The check for downshifts during a dec phase is applied prior to the check for downshifts during transitions from acc or const to dec

' No upshift to a higher gear shall be performed within a deceleration phase ###################################################################################

	rstbe.MoveFirst

	rstce.MoveFirst
	rstce.MoveNext

	Do While Not rstce.EOF

		If rstbe!v > rstce!v And rstbe!gear < rstce!gear And rstbe!gear > 0 Then

			rstce.edit
			rstce!gear = rstbe!gear
			rstce!gear_modification = rstce!gear_modification & "6_8) no upshift during dec, "
			rstce.Update
			m = m + 1

		End If

		rstbe.MoveNext
		rstce.MoveNext

	Loop



' 4(e) No upshift to a higher gear at the transition from an acceleration or constant speed phase to a deceleration phase shall be performed
' if the gear in the phase following the deceleration phase is lower than the upshifted gear or is gear 0.
'######################################################################################################################################


	rstbe.MoveFirst

	rstce.MoveFirst
	rstce.MoveNext

	rstde.MoveFirst
	rstde.MoveNext
	rstde.MoveNext

	rstee.MoveFirst
	rstee.MoveNext
	rstee.MoveNext
	rstee.MoveNext

	rstfe.MoveFirst
	rstfe.MoveNext
	rstfe.MoveNext
	rstfe.MoveNext
	rstfe.MoveNext

	rstge.MoveFirst
	rstge.MoveNext
	rstge.MoveNext
	rstge.MoveNext
	rstge.MoveNext
	rstge.MoveNext

	Do Until rstge.EOF



		If rstge!v < rstfe!v And rstfe!v < rstee!v And rstee!v < rstde!v And rstde!v < rstce!v And rstbe!v <= rstce!v And rstbe!v >= 1 And rstge!v >= 1 And rstbe!gear < rstce!gear And rstde!gear = rstce!gear And rstee!gear = rstde!gear And rstfe!gear = rstee!gear And rstge!gear = rstfe!gear Then



			k = 0
			v_1 = rstfe!v
			v_2 = rstge!v
			g_0 = rstbe!gear
			g_1 = rstfe!gear
			g_2 = rstge!gear


			Do Until rstge!gear <> rstfe!gear Or rstge!v < 1 Or rstge!v >= rstfe!v

				rstfe.MoveNext
				rstge.MoveNext

				v_1 = rstfe!v
				v_2 = rstge!v
				g_1 = rstfe!gear
				g_2 = rstge!gear
				k = k + 1

			Loop

			rstfe.MoveNext
			rstge.MoveNext

			k = k + 1



			If rstbe!gear = rstce!gear - 1 And (rstge!gear < rstce!gear Or rstfe!gear < rstce!gear) And rstce!flag_6_1 <> 1 Then


				rstce.edit
				rstce!gear = rstbe!gear
				rstce!gear_modification = rstce!gear_modification & "6_1c) no upshift at transition from acc or const to dec, "
'rstce!flag_6_1 = 1
				rstce.Update
				m = m + 1

				rstde.edit
				rstde!gear = rstbe!gear
				rstde!gear_modification = rstde!gear_modification & "6_1d) no upshift at transition from acc or const to dec, "
'rstde!flag_6_1 = 1
				rstde.Update
				m = m + 1

				rstee.edit
				rstee!gear = rstbe!gear
				rstee!gear_modification = rstee!gear_modification & "6_1e) no upshift at transition from acc or const to dec, "
'rstee!flag_6_1 = 1
				rstee.Update
				m = m + 1

				rstfe.MovePrevious
				rstge.MovePrevious

				If rstge!gear = rstbe!gear + 1 Then

					rstge.edit
					rstge!gear = rstbe!gear
					rstge!gear_modification = rstge!gear_modification & "6_1g) no upshift at transition from acc or const to dec, "
					rstge!flag_6_1 = 1
					rstge.Update
					m = m + 1

				End If

				For i = 1 To k

					rstfe.edit
					rstfe!gear = rstbe!gear
					rstfe!gear_modification = rstfe!gear_modification & "6_1f) no upshift at transition from acc or const to dec, "

					rstfe.Update
					m = m + 1

					rstfe.MovePrevious
					rstge.MovePrevious

				Next i

				rstfe.MoveNext
				rstge.MoveNext


				For i = 1 To k

					rstbe.MoveNext
					rstce.MoveNext
					rstde.MoveNext
					rstee.MoveNext
					rstfe.MoveNext
					rstge.MoveNext

				Next i



				If rstfe!Tim - rstee!Tim <> 1 Then
					MsgBox "6_1 ee " & rstee!Tim & ", 6_1 fe " & rstfe!Tim
					Exit Sub
				End If

			ElseIf rstbe!gear = rstce!gear - 2 And (rstge!gear < rstce!gear Or rstfe!gear < rstce!gear) Then

				rstce.edit
				rstce!gear = rstbe!gear + 1
				rstce!gear_modification = rstce!gear_modification & "6_2c) no upshift by 2 gears at transition from acc or const to dec, "
				rstce!flag_6_1 = 1
				rstce.Update
				m = m + 1

				rstde.edit
				rstde!gear = rstbe!gear + 1
				rstde!gear_modification = rstde!gear_modification & "6_2d) no upshift by 2 gears at transition from acc or const to dec, "
				rstde!flag_6_1 = 1
				rstde.Update
				m = m + 1

				rstee.edit
				rstee!gear = rstbe!gear + 1
				rstee!gear_modification = rstee!gear_modification & "6_2e) no upshift by 2 gears at transition from acc or const to dec, "
				rstee!flag_6_1 = 1
				rstee.Update
				m = m + 1

				rstfe.MovePrevious
				rstge.MovePrevious

				If rstge!gear = rstbe!gear + 2 Then

					rstge.edit
					rstge!gear = rstbe!gear + 1
					rstge!gear_modification = rstge!gear_modification & "6_2g) no upshift by 2 gears at transition from acc or const to dec, "
					rstge!flag_6_1 = 1
					rstge.Update
					m = m + 1

				End If

				For i = 1 To k

					rstfe.edit
					rstfe!gear = rstbe!gear + 1
					rstfe!gear_modification = rstfe!gear_modification & "6_2f) no upshift by 2 gears at transition from acc or const to dec, "
					rstfe!flag_6_1 = 1
					rstfe.Update
					m = m + 1

					rstfe.MovePrevious
					rstge.MovePrevious

				Next i

				rstfe.MoveNext
				rstge.MoveNext


				For i = 1 To k

					rstbe.MoveNext
					rstce.MoveNext
					rstde.MoveNext
					rstee.MoveNext
					rstfe.MoveNext
					rstge.MoveNext

				Next i



				If rstfe!Tim - rstee!Tim <> 1 Then
					MsgBox "6_2 ee " & rstee!Tim & ", 6_2 fe " & rstfe!Tim
					Exit Sub
				End If





			Else

				For i = 1 To k

					rstfe.MovePrevious
					rstge.MovePrevious

				Next i

				For i = 1 To k

					rstbe.MoveNext
					rstce.MoveNext
					rstde.MoveNext
					rstee.MoveNext
					rstfe.MoveNext
					rstge.MoveNext

				Next i

				If rstfe!Tim - rstee!Tim <> 1 Then
					MsgBox "6_3 ee " & rstee!Tim & ", 6_3 fe " & rstfe!Tim
					Exit Sub
				End If

			End If

		End If

		rstbe.MoveNext
		rstce.MoveNext
		rstde.MoveNext
		rstee.MoveNext
		rstfe.MoveNext
		rstge.MoveNext

	Loop





' end of 4 (d) ###########################################################################################################

' 4(e)
'Gear 2 shall be used during a deceleration phase within a short trip of the cycle (not at the end of a short trip) as long as the engine speed does not drop below (0.9 × nidle).
'If the engine speed drops below nidle, the clutch shall be disengaged.
'If the deceleration phase is the last part of a short trip shortly before a stop phase, the second gear shall be used as long as the engine speed does not drop below nidle.
' 4(e) is already dealt with in gearshift_calculation_1

' 4 (f) If during a deceleration phase the duration of a gear sequence between two gear sequences of 3 seconds or more is only 1 second,
'       it shall be replaced by gear 0 and the clutch shall be disengaged.
'       If during a deceleration phase the duration of a gear sequence between two gear sequences of 3 seconds or more is 2 seconds,
'       it shall be replaced by gear 0 for the 1st second and for the 2nd second with the gear that follows after the 2 second period.
'       The clutch shall be disengaged for the 1st second.


' 4 (f) of annex 2, no 1. gear during deceleration ####################################################################################
'===================================================================================================================

'9 ######################################################################################################
'9a) check for gear 1 before stop

	rstbe.MoveFirst

	rstce.MoveFirst
	rstce.MoveNext

	rstde.MoveFirst
	rstde.MoveNext
	rstde.MoveNext

	Do Until rstde.EOF


		If rstce!v >= 1 And rstde!v < 1 Then

			k = 0
			v_1 = rstce!v
			v_2 = v_1 + 1

			If rstce!gear = 1 Then

				rstce.edit
				rstce!gear = 0
				rstce!nc = rstae!idling_speed
				rstce!clutch = "engaged, gear lever in neutral"
				rstce!gear_modification = rstce!gear_modification & "9) check for gear 1 before stop, "
				rstce.Update
				m = m + 1
			Else

				GoTo weiter_stop

			End If


			weiter_stop_loop:

			If rstce!gear > 1 Or v_2 <= v_1 Then

				If k > 0 Then

					For i = 1 To k

						rstce.MoveNext
						rstbe.MoveNext
						rstde.MoveNext


					Next i

				End If

				GoTo weiter_stop

			Else



				v_1 = rstce!v

				k = k + 1

				rstce.MovePrevious
				rstbe.MovePrevious
				rstde.MovePrevious


				If rstbe.BOF Then

					GoTo weiter3

				End If

				v_2 = rstce!v

				If rstce!gear = 1 And v_2 > v_1 And rstbe!v > v_2 Then

					rstce.edit
					rstce!gear = 0
					rstce!nc = rstae!idling_speed
					rstce!clutch = "engaged, gear lever in neutral"
					rstce!gear_modification = rstce!gear_modification & "9) check for gear 1 before stop, "
					rstce.Update
					m = m + 1

				End If

				GoTo weiter_stop_loop

			End If

			GoTo weiter_stop

		Else

			GoTo weiter_stop

		End If


		weiter_stop:



		rstbe.MoveNext
		rstce.MoveNext
		rstde.MoveNext

	Loop

	weiter3:


' 4 (f) ###############################################################################################################################

	rstbe.MoveFirst

	rstce.MoveFirst
	rstce.MoveNext

	rstde.MoveFirst
	rstde.MoveNext
	rstde.MoveNext

	rstee.MoveFirst
	rstee.MoveNext
	rstee.MoveNext
	rstee.MoveNext

	rstfe.MoveFirst
	rstfe.MoveNext
	rstfe.MoveNext
	rstfe.MoveNext
	rstfe.MoveNext

	rstge.MoveFirst
	rstge.MoveNext
	rstge.MoveNext
	rstge.MoveNext
	rstge.MoveNext
	rstge.MoveNext


' 7a) 4(f) #####################################################################################################################

	Do While Not rstge.EOF

		If rstbe!gear = rstce!gear And rstce!gear = rstde!gear And rstde!gear > rstee!gear And ((rstfe!gear < rstee!gear And rstge!gear <= rstfe!gear And rstfe!gear > 1 And rstge!gear > 0) Or (rstfe!gear = rstee!gear And rstge!gear < rstfe!gear And rstfe!gear > 1 And rstge!gear > 0)) Then

			If ((rstbe!v > rstce!v And rstce!v > rstde!v And rstde!v > rstee!v And rstee!v >= rstfe!v)) Or ((rstde!v > rstee!v And rstee!v > rstfe!v And rstfe!v > rstge!v)) Then


				rstee.edit
				rstee!gear = 0
				rstee!clutch = "disengaged"
				rstee!gear_modification = rstee!gear_modification & "7a1a) i,i,i,g4<i,g5<=g4,g6<=g5 -> i,i,i,0,g6,g6, "
				rstee.Update
				m = m + 1

				rstfe.edit
				If rstfe!g_min <= rstge!gear Or rstge!gear = 0 Then
					rstfe!gear = rstge!gear
					rstfe!gear_modification = rstfe!gear_modification & "7a1b) i,i,i,g4<i,g5<=g4,g6<=g5 -> i,i,i,0,g6,g6, "
					If rstge!gear = 0 Then
						rstfe!clutch = "engaged, gear lever in neutral"
					End If
					m = m + 1
				Else
					rstfe!gear_modification = rstfe!gear_modification & "7a1b) Necessary gear modification not possible, "
					n = n + 1
				End If
				rstfe.Update


			End If
		End If


		rstbe.MoveNext
		rstce.MoveNext
		rstde.MoveNext
		rstee.MoveNext
		rstfe.MoveNext
		rstge.MoveNext

	Loop

'#############################################################################################################################

	rstbe.MoveFirst

	rstce.MoveFirst
	rstce.MoveNext

	rstde.MoveFirst
	rstde.MoveNext
	rstde.MoveNext

	rstee.MoveFirst
	rstee.MoveNext
	rstee.MoveNext
	rstee.MoveNext

	rstfe.MoveFirst
	rstfe.MoveNext
	rstfe.MoveNext
	rstfe.MoveNext
	rstfe.MoveNext

	rstge.MoveFirst
	rstge.MoveNext
	rstge.MoveNext
	rstge.MoveNext
	rstge.MoveNext
	rstge.MoveNext


' 7b) 4(f) #####################################################################################################################

	Do While Not rstge.EOF

		If rstbe!v > rstce!v And rstce!v > rstde!v And rstde!v > rstee!v And rstee!v > rstfe!v Then

			If (rstbe!gear > rstde!gear And rstce!gear = 0 And rstde!gear > rstee!gear And rstfe!gear <= rstee!gear And rstge!gear <= rstfe!gear And rstge!gear > 0) Or (rstbe!gear > rstde!gear And rstce!gear = 0 And rstde!gear = rstee!gear And rstfe!gear < rstee!gear And rstge!gear <= rstfe!gear And rstge!gear > 0) Then

				If rstde!g_max - rstfe!gear < 3 Then

					If rstfe!gear = rstge!gear Then

						rstde.edit
						If rstde!g_min <= rstfe!gear Then
							rstde!gear = rstfe!gear
							rstde!gear_modification = rstde!gear_modification & "7b1) j,0,i,i-1,g5<=g4,g6<=g5 -> j,0,g5,g5,g5,g6, "
							m = m + 1
						Else
							rstde!gear_modification = rstde!gear_modification & "7b1) Necessary gear modification not possible, "
							n = n + 1
						End If
						rstde.Update

						rstee.edit
						If rstee!g_min <= rstfe!gear Then
							rstee!gear = rstfe!gear
							rstee!gear_modification = rstee!gear_modification & "7b1) j,0,i,i-1,g5<=g4,g6<=g5 -> j,0,g5,g5,g5,g6, "
							m = m + 1
						Else
							rstee!gear_modification = rstee!gear_modification & "7b1) Necessary gear modification not possible, "
							n = n + 1
						End If
						rstee.Update

					ElseIf rstfe!gear = rstge!gear + 1 Then

						rstde.edit
						If rstde!g_min <= rstfe!gear Then
							rstde!gear = rstfe!gear
							rstde!gear_modification = rstde!gear_modification & "7b2) j,0,i,i-1,g5<=g4,g6<=g5 -> j,0,g5,g5,g5,g6, "
							m = m + 1
						Else
							rstde!gear_modification = rstde!gear_modification & "7b2) Necessary gear modification not possible, "
							n = n + 1
						End If
						rstde.Update

						rstee.edit
						If rstee!g_min <= rstfe!gear Then
							rstee!gear = rstfe!gear
							rstee!gear_modification = rstee!gear_modification & "7b2) j,0,i,i-1,g5<=g4,g6<=g5 -> j,0,g5,g5,g5,g6, "
							m = m + 1
						Else
							rstee!gear_modification = rstee!gear_modification & "7b2) Necessary gear modification not possible, "
							n = n + 1
						End If
						rstee.Update

					Else

						rstde.edit
						If rstde!g_min <= rstge!gear Then
							rstde!gear = rstge!gear
							rstde!gear_modification = rstde!gear_modification & "7b2) j,0,i,i-1,g5<=g4,g6<=g5 -> j,0,g5,g5,g5,g6, "
							m = m + 1
						Else
							rstde!gear_modification = rstde!gear_modification & "7b2) Necessary gear modification not possible, "
							n = n + 1
						End If
						rstde.Update

						rstee.edit
						If rstee!g_min <= rstge!gear Then
							rstee!gear = rstge!gear
							rstee!gear_modification = rstee!gear_modification & "7b2) j,0,i,i-1,g5<=g4,g6<=g5 -> j,0,g5,g5,g5,g6, "
							m = m + 1
						Else
							rstee!gear_modification = rstee!gear_modification & "7b2) Necessary gear modification not possible, "
							n = n + 1
						End If
						rstee.Update

						rstfe.edit
						If rstfe!g_min <= rstge!gear Then
							rstfe!gear = rstge!gear
							rstfe!gear_modification = rstfe!gear_modification & "7b2) j,0,i,i-1,g5<=g4,g6<=g5 -> j,0,g5,g5,g5,g6, "
							m = m + 1
						Else
							rstfe!gear_modification = rstfe!gear_modification & "7b2) Necessary gear modification not possible, "
							n = n + 1
						End If
						rstfe.Update

					End If

				Else

					rstde.edit
					rstde!gear = 0
					rstde!clutch = "disengaged"
					rstde!gear_modification = rstde!gear_modification & "7b3) j,0,i,i-1,g5<=g4,g6<=g5 -> j,0,0,g6,g6,g6, "
					rstde.Update
					m = m + 1


					rstee.edit
					If rstee!g_min <= rstge!gear Or rstge!gear = 0 Then
						rstee!gear = rstge!gear
						rstee!gear_modification = rstee!gear_modification & "7b3) j,0,i,i-1,g5<=g4,g6<=g5 -> j,0,0,g6,g6,g6, "
						m = m + 1
					Else
						rstee!gear_modification = rstee!gear_modification & "7b3) Necessary gear modification not possible, "
						n = n + 1
					End If
					rstee.Update

					rstfe.edit
					If rstfe!g_min <= rstge!gear Or rstge!gear = 0 Then
						rstfe!gear = rstge!gear
						rstfe!gear_modification = rstfe!gear_modification & "7b3) j,0,i,i-1,g5<=g4,g6<=g5 -> j,0,0,g6,g6,g6, "
						m = m + 1
					Else
						rstfe!gear_modification = rstfe!gear_modification & "7b3) Necessary gear modification not possible, "
						n = n + 1
					End If
					rstfe.Update

				End If

			End If
		End If


		rstbe.MoveNext
		rstce.MoveNext
		rstde.MoveNext
		rstee.MoveNext
		rstfe.MoveNext
		rstge.MoveNext

	Loop




' 4(f) ##############################################################################################################################

	rstbe.MoveFirst

	rstce.MoveFirst
	rstce.MoveNext

	rstde.MoveFirst
	rstde.MoveNext
	rstde.MoveNext

	rstee.MoveFirst
	rstee.MoveNext
	rstee.MoveNext
	rstee.MoveNext

	rstfe.MoveFirst
	rstfe.MoveNext
	rstfe.MoveNext
	rstfe.MoveNext
	rstfe.MoveNext

	rstge.MoveFirst
	rstge.MoveNext
	rstge.MoveNext
	rstge.MoveNext
	rstge.MoveNext
	rstge.MoveNext



	Do While Not rstge.EOF

		If rstbe!gear = rstce!gear And rstce!gear = rstde!gear And rstde!gear > rstee!gear And rstfe!gear <= rstee!gear And rstfe!gear > 0 And rstge!gear = 0 Then

			rstee.edit
			rstee!gear = rstge!gear
			rstee!clutch = "disengaged"
			rstee!gear_modification = rstee!gear_modification & "7a2) i,i,i,g4<i,g5=g4,g6=0 -> i,i,i,0,0,0, "
			rstee.Update
			m = m + 1

			rstfe.edit
			rstfe!gear = rstge!gear
			rstfe!clutch = "disengaged"
			rstfe!gear_modification = rstfe!gear_modification & "7a2) i,i,i,g4<i,g5=g4,g6=0 -> i,i,i,0,0,0, "
			m = m + 1

			rstfe.Update


		End If


		rstbe.MoveNext
		rstce.MoveNext
		rstde.MoveNext
		rstee.MoveNext
		rstfe.MoveNext
		rstge.MoveNext

	Loop

' 4 (f) #############################################################################################################################
'final check for 4332 during deceleration, comes from last sub-paragraps of 4(b)

	rstbe.MoveFirst

	rstce.MoveFirst
	rstce.MoveNext

	rstde.MoveFirst
	rstde.MoveNext
	rstde.MoveNext

	rstee.MoveFirst
	rstee.MoveNext
	rstee.MoveNext
	rstee.MoveNext



' 7c) 4(f) 4,3,3,2, -> 4,0,2,2  #####################################################################################################################

	Do While Not rstee.EOF

		If rstbe!v > rstce!v And rstce!v > rstde!v And rstde!v > rstee!v Then

			If rstbe!gear > rstce!gear And rstde!gear = rstce!gear And rstee!gear > 0 And rstee!gear < rstce!gear Then

				rstde.edit
				If rstde!g_min <= rstee!gear Then
					rstde!gear = rstee!gear
					rstde!gear_modification = rstde!gear_modification & "7c) 4,3,3,2 -> 4,0,2,2, "
					m = m + 1
				Else
					rstde!gear_modification = rstde!gear_modification & "7c) Necessary gear modification not possible, "
					n = n + 1
				End If
				rstde.Update

				rstce.edit

				rstce!gear = 0
				rstce!clutch = "disengaged"
				rstce!gear_modification = rstce!gear_modification & "7c) 4,3,3,2 -> 4,0,2,2, "
				m = m + 1
				rstce.Update


			End If
		End If


		rstbe.MoveNext
		rstce.MoveNext
		rstde.MoveNext
		rstee.MoveNext

	Loop




'annex 2, section 4 (f) #######################################################################################
'==============================================================================================================

'################################################################################################################

	rstbe.MoveFirst
	rstce.MoveFirst
	rstce.MoveNext
	rstde.MoveFirst
	rstde.MoveNext
	rstde.MoveNext
	rstee.MoveFirst
	rstee.MoveNext
	rstee.MoveNext
	rstee.MoveNext
	rstfe.MoveFirst
	rstfe.MoveNext
	rstfe.MoveNext
	rstfe.MoveNext
	rstfe.MoveNext
	rstge.MoveFirst
	rstge.MoveNext
	rstge.MoveNext
	rstge.MoveNext
	rstge.MoveNext
	rstge.MoveNext
	rsthe.MoveFirst
	rsthe.MoveNext
	rsthe.MoveNext
	rsthe.MoveNext
	rsthe.MoveNext
	rsthe.MoveNext
	rsthe.MoveNext

	Do Until rsthe.EOF

'If the deceleration phase is the last part of a short trip shortly before a stop phase and the last gear > 0 before the stop phase is used only for a period of up to 2 seconds,
'gear 0 shall be used instead and the gear lever shall be placed in neutral and the clutch shall be engaged.

'8) ###################################################################################################################

'8) >x,>x,x,x,0,0,0 -> >x,>x,0,0,0,0,0, annex 2, section 4 (f)


		If rstce!gear = rstbe!gear And rstbe!gear > rstde!gear And rstde!gear > 0 And (rstde!gear = rstee!gear Or rstee!gear = 0) And rstfe!gear = rstge!gear And rstge!gear = rsthe!gear And rsthe!gear = 0 Then


			rstde.edit
			rstde!gear = 0
			rstde!clutch = "disengaged"
			rstde!gear_modification = rstde!gear_modification & "8a) >x,>x,x,x,0,0,0 -> >x,>x,0,0,0,0,0, "
			m = m + 1
			rstde.Update

			If rstee!gear > 0 Then

				rstee.edit
				rstee!gear = 0
				rstee!clutch = "disengaged"
				rstee!gear_modification = rstee!gear_modification & "8a) >x,>x,x,x,0,0,0 -> >x,>x,0,0,0,0,0, "
				m = m + 1
				rstee.Update

			End If


'8) >x,>x,0,x,x,0,0 -> >x,>x,0,0,0,0,0, annex 2, section 4 (f)


		ElseIf rstce!gear = rstbe!gear And rstbe!gear > rstee!gear And rstde!gear = 0 And rstee!gear = rstfe!gear And rstee!gear > 0 And rstge!gear = 0 And rsthe!gear = 0 And rstfe!v > 1 Then


			rstee.edit
			rstee!gear = 0
			rstee!clutch = "disengaged"
			rstee!gear_modification = rstee!gear_modification & "8b) >x,>x,0,x,x,0,0 -> >x,>x,0,0,0,0,0, "
			m = m + 1
			rstee.Update


			rstfe.edit
			rstfe!gear = 0
			rstfe!clutch = "disengaged"
			rstfe!gear_modification = rstfe!gear_modification & "8b) >x,>x,0,x,x,0,0 -> >x,>x,0,0,0,0,0, "
			m = m + 1
			rstfe.Update



		End If




		rstbe.MoveNext
		rstce.MoveNext
		rstde.MoveNext
		rstee.MoveNext
		rstfe.MoveNext
		rstge.MoveNext
		rsthe.MoveNext

	Loop


	calcend:



	rstie.Close
	rstke.Close
	rstae.Close
	rstbe.Close
	rstce.Close
	rstde.Close
	rstee.Close
	rstfe.Close
	rstge.Close
	rsthe.Close

	Text253 = Text253 + m

End Sub
