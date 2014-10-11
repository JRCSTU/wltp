1. REPLACE CLASS 1
2. Add vehicle_ids i ...
2. Execute:
    Private Sub JRC_save_all_vehicles()
        Dim wotIds(1 To 2) As Integer
        Dim engines(1 To 2)
        Dim rds As Recordset2
        Dim db As Database
        Dim veh As String, export_name As String
        Dim fs As New FileSystemObject
        Dim engId As Integer
        Dim wot, cls, v_max
        Dim expTable As String

        engines(1) = "petrol"
        wotIds(1) = 26
        engines(2) = "diesel"
        wotIds(2) = 25

        Set wrsp = DBEngine.Workspaces(0)
        Set db = wrsp.Databases(0)

        Set rds = db.OpenRecordset("SELECT vehicle_no, comments, IDengine, pmr_km, v_max FROM vehicle_info", DB_OPEN_SNAPSHOT, A_ALL)
            '& _
            '    "INNER JOIN JRC_vehs ON vehicle_info.vehicle_no = JRC_vehs.veh_no ORDER BY vehicle_no", DB_OPEN_SNAPSHOT)
        rds.MoveFirst

        On Error GoTo ErrorInFIle
        Do Until rds.EOF
            veh = rds!vehicle_no
            comment = rds!comments
            engId = rds!IDengine
            wot = wotIds(engId)
            eng = engines(engId)
            export_name = "D:\tmp\wltp-heinz-results\" & veh & "-" & eng & "-" & comment
            pmr = rds!pmr_km
            v_max = rds!v_max

            DoEvents

            If fs.FileExists(export_name & ".xls") Or fs.FileExists(export_name & ".csv") Then
                Debug.Print ("SKIPPED: " & export_name)
            Else
                '' Decide class
                ''
                If pmr <= 22 Then
                    cls = 1
                ElseIf pmr <= 34 Then
                    cls = 2
                ElseIf v_max < 120 Then
                    cls = 4
                Else
                    cls = 5
                End If
                Call DSetValue("ST_WLTC_version", "class", cls)
                'Kombinationsfeld52_AfterUpdate

                DoEvents
                Kombinationsfeld12 = veh
                Call Kombinationsfeld12_AfterUpdate

                DoEvents
                Kombinationsfeld13 = wot
                Call Kombinationsfeld13_AfterUpdate

                DoEvents
                Call Befehl28_Click
                '''DoCmd.OpenQuery "A gearshift_table check_results_final"

                Debug.Print ("Storing class: " & cls & ", " & export_name)

                DoEvents
                'expTable = "A gearshift_table_export"
                expTable = "A gearshift_table check_results_final"
                DoCmd.TransferSpreadsheet acExport, acSpreadsheetTypeExcel9, expTable, export_name, -1
                'DoCmd.TransferText acExportDelim, Null, "A gearshift_table_export", export_name, -1
            End If

    NextFile:
            DoEvents
            rds.MoveNext
        Loop
        rds.Close

        Exit Sub
    ErrorInFIle:
        Debug.Print ("FAILED veh: " & veh)
        GoTo NextFile
    End Sub



