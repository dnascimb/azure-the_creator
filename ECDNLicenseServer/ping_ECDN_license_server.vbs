
Const ForReading = 1
Const csFSpec = "license.txt"

strLicense = "file_not_found"

Set objFSO = CreateObject("Scripting.FileSystemObject")

If objFSO.FileExists(csFSpec) Then
    Set objFile = objFSO.GetFile(csFSpec)

    If objFile.Size > 0 Then
        strLicense = objFSO.OpenTextFile(csFSpec, ForReading).ReadAll
    Else
        strLicense = "empty"
    End If
End If

strLicense = Trim(strLicense)
If strLicense = "" Then 
    strLicense = "empty"
End If

'URL to open....
sUrl = "https://api.ac1.kontiki.com/api/v2/health/license/" + strLicense

HTTPGet sUrl

Function HTTPGet(sUrl)
  set oHTTP = CreateObject("Microsoft.XMLHTTP")
  oHTTP.open "GET", sUrl, false
  oHTTP.send ""
  set oHTTP = Nothing
 End Function