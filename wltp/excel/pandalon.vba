' Copyright 2013-2019 European Commission (JRC);
' Licensed under the EUPL (the 'Licence');
' You may not use this work except in compliance with the Licence.
' You may obtain a copy of the Licence at: http://ec.europa.eu/idabc/eupl
'
Option Explicit

Private Sub InvokePython(python_body As String, import_my_python As Boolean)
'' Before invoking `python_body` code prefixes with boilerplate-code for `xlwings` and with excel's folder into python's sys.path.
'' If import_my_python is `True`, it also imports a same-named python-file.
    
    Dim python_prefix As String
    Dim python_code As String
    Dim wb_bname As String
    
    '' The `sys` module and workbook-path included in `sys.path` downstream.
    '
    python_prefix = "import os; " & _
                    "from xlwings import Workbook, Range; " & vbCr & _
                    "wb = Workbook(r'" & ThisWorkbook.FullName & "'); "

    If import_my_python Then
        Dim fso As New FileSystemObject
        wb_bname = fso.GetBaseName(ThisWorkbook.Name)
        python_prefix = python_prefix & "import " & wb_bname & " as mypy; "
    End If
    
    python_code = python_prefix & vbCr & python_body
    
    Call pandalon_RunPython(python_code)
End Sub

Sub RunSelectionAsPython()
    Call RunSelectionAsPython_(False)
End Sub
Sub RunSelectionAsMyPython()
    Call RunSelectionAsPython_(True)
End Sub
Sub RunSelectionAsPython_(import_my_python As Boolean)
'' Uses `xlwings` library to run the active-selection as Python code.
    Dim python_body As String
    Dim wb_name As String
    Dim c
    
    python_body = ""
    For Each c In Selection
        If c.Value <> vbNullString Then
            python_body = python_body & c.Value & vbCr
        End If
    Next c
    
    Call InvokePython(python_body, import_my_python)
End Sub
