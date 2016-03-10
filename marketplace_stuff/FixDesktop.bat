@echo off
REG ADD "HKCU\Software\Microsoft\Internet Explorer\Main" /v Window_Placement /t REG_BINARY /d 2c0000000000000001000000ffffffffffffffffffffffffffffffffffffffffe80100008002000012040000 /f
REG ADD "HKLM\Software\Wow6432Node\Kontiki\kontiki" /v dmWidth /t REG_DWORD /d 640 /f
REG ADD "HKLM\Software\Wow6432Node\Kontiki\kontiki" /v dmHeight /t REG_DWORD /d 500 /f
cls
exit


