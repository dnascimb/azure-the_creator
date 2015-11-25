REG ADD HKLM\Software\Microsoft\ServerManager /v DoNotOpenServerManagerAtLogon /t REG_DWORD /d 1 /f
REG ADD HKLM\Software\Microsoft\ServerManager /v RefreshInterval /t REG_DWORD /d 4294967295 /f

REG ADD HKLM\System\CurrentControlSet\Control\Network\NewNetworkWindowOff /f
REG ADD HKLM\System\CurrentControlSet\Control\Network\NetworkLocationWizard /v HideWizard /t REG_DWORD /d 1 /f
