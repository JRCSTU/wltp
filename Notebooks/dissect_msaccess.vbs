' Usage:
'  cscript decompose.vbs <input file> <path>

' Converts all modules, classes, forms and macros from an Access Project file (.adp) <input file> to
' text and saves the results in separate files to <path>.  Requires Microsoft Access.
' From same thread. but:
'    https://stackoverflow.com/a/35501159/548792

Option Explicit

Const acForm = 2
Const acModule = 5
Const acMacro = 4
Const acReport = 3
Const acQuery = 1
Const acExportTable = 0

' BEGIN CODE
Dim fso, relDoc, ACCDBFilename, sExportpath
Set fso = CreateObject("Scripting.FileSystemObject")
Set relDoc = CreateObject("Microsoft.XMLDOM")

If (Wscript.Arguments.Count = 0) Then
    MsgBox "Please provide the .accdb database file", vbExclamation, "Error"
    Wscript.Quit()
End If
ACCDBFilename = fso.GetAbsolutePathName(Wscript.Arguments(0))

If (Wscript.Arguments.Count = 1) Then
 sExportpath = ""
Else
 sExportpath = Wscript.Arguments(1)
End If


exportModulesTxt ACCDBFilename, sExportpath

If (Err <> 0) And (Err.Description <> Null) Then
    MsgBox Err.Description, vbExclamation, "Error"
    Err.Clear
End If


function NormalizeFname(filename)
    dim re : Set re = new regexp

    re.Pattern = "[^\w :\\\.]"
    re.Global = True

    NormalizeFname = re.Replace(filename, "_")
end function


Function exportModulesTxt(ACCDBFilename, sExportpath)
    Dim myComponent, sModuleType, sTempname, sOutstring, sFname
    Dim myType, myName, myPath, hasRelations
    myType = fso.GetExtensionName(ACCDBFilename)
    myName = fso.GetBaseName(ACCDBFilename)
    myPath = fso.GetParentFolderName(ACCDBFilename)

    'if no path was given as argument, use a relative directory
    If (sExportpath = "") Then
        sExportpath = myPath & "\Source"
    End If
    'On Error Resume Next
    fso.DeleteFolder (sExportpath) ', force=True
    fso.CreateFolder (sExportpath)
    On Error GoTo 0

    Wscript.Echo "starting Access..."
    Dim oApplication
    Set oApplication = CreateObject("Access.Application")
    Wscript.Echo "Opening " & ACCDBFilename & " ..."
    If (Right(ACCDBFilename, 4) = ".adp") Then
     oApplication.OpenAccessProject ACCDBFilename
    Else
     oApplication.OpenCurrentDatabase ACCDBFilename
    End If
    oApplication.Visible = False

    Wscript.Echo "exporting..."
    Dim myObj
    For Each myObj In oApplication.CurrentProject.AllForms
        Wscript.Echo "Exporting FORM " & myObj.FullName
        sFname = NormalizeFname(myObj.FullName)
        oApplication.SaveAsText acForm, myObj.FullName, sExportpath & "\" & sFname & ".form.vbs"
        oApplication.DoCmd.Close acForm, myObj.FullName
    Next
    For Each myObj In oApplication.CurrentProject.AllModules
        sFname = NormalizeFname(myObj.FullName)
        Wscript.Echo "Exporting MODULE " & myObj.FullName
        oApplication.SaveAsText acModule, myObj.FullName, sExportpath & "\" & sFname & ".module.vbs"
    Next
    For Each myObj In oApplication.CurrentProject.AllMacros
        sFname = NormalizeFname(myObj.FullName)
        Wscript.Echo "Exporting MACRO " & myObj.FullName
        oApplication.SaveAsText acMacro, myObj.FullName, sExportpath & "\" & sFname & ".macro.txt"
    Next
    For Each myObj In oApplication.CurrentProject.AllReports
        sFname = NormalizeFname(myObj.FullName)
        Wscript.Echo "Exporting REPORT " & myObj.FullName
        oApplication.SaveAsText acReport, myObj.FullName, sExportpath & "\" & sFname & ".report.txt"
    Next
    For Each myObj In oApplication.CurrentDb.QueryDefs
        sFname = NormalizeFname(myObj.Name)
        Wscript.Echo "Exporting QUERY " & myObj.Name
        oApplication.SaveAsText acQuery, myObj.Name, sExportpath & "\" & sFname & ".query.txt"
    Next
    For Each myObj In oApplication.CurrentDb.TableDefs
     If Not Left(myObj.Name, 4) = "MSys" Then
      sFname = NormalizeFname(myObj.Name)
      Wscript.Echo "Exporting TABLE " & myObj.Name
      oApplication.ExportXml acExportTable, myObj.Name, , sExportpath & "\" & sFname & ".table.txt"
      'put the file path as a second parameter if you want to export the table data as well, instead of ommiting it and passing it into a third parameter for structure only
     End If
    Next

    hasRelations = False
    relDoc.appendChild relDoc.createElement("Relations")
    For Each myObj In oApplication.CurrentDb.Relations  'loop though all the relations
    If Not Left(myObj.Name, 4) = "MSys" Then
     Dim relName, relAttrib, relTable, relFoTable, fld
     hasRelations = True

     relDoc.ChildNodes(0).appendChild relDoc.createElement("Relation")
     Set relName = relDoc.createElement("Name")
     relName.Text = myObj.Name
     relDoc.ChildNodes(0).LastChild.appendChild relName

     Set relAttrib = relDoc.createElement("Attributes")
     relAttrib.Text = myObj.Attributes
     relDoc.ChildNodes(0).LastChild.appendChild relAttrib

     Set relTable = relDoc.createElement("Table")
     relTable.Text = myObj.Table
     relDoc.ChildNodes(0).LastChild.appendChild relTable

     Set relFoTable = relDoc.createElement("ForeignTable")
     relFoTable.Text = myObj.ForeignTable
     relDoc.ChildNodes(0).LastChild.appendChild relFoTable

     Wscript.Echo "Exporting relation " & myObj.Name & " between tables " & myObj.Table & " -> " & myObj.ForeignTable

     For Each fld In myObj.Fields   'in case the relationship works with more fields
      Dim lf, ff
      relDoc.ChildNodes(0).LastChild.appendChild relDoc.createElement("Field")

      Set lf = relDoc.createElement("Name")
      lf.Text = fld.Name
      relDoc.ChildNodes(0).LastChild.LastChild.appendChild lf

      Set ff = relDoc.createElement("ForeignName")
      ff.Text = fld.ForeignName
      relDoc.ChildNodes(0).LastChild.LastChild.appendChild ff

      Wscript.Echo "  Involving fields " & fld.Name & " -> " & fld.ForeignName
     Next
    End If
    Next
    If hasRelations Then
     relDoc.InsertBefore relDoc.createProcessingInstruction("xml", "version='1.0'"), relDoc.ChildNodes(0)
     relDoc.Save sExportpath & "\relations.rel.txt"
     Wscript.Echo "Relations successfuly saved in file relations.rel.txt"
    End If

    oApplication.CloseCurrentDatabase
    oApplication.Quit

End Function
