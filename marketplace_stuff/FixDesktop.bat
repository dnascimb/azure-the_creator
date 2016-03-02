@echo off
REG ADD "HKCU\Software\Microsoft\Internet Explorer\Main" /v Window_Placement /t REG_BINARY /d 2c0000000000000001000000ffffffffffffffffffffffffffffffff01000000E60100007F02000010040000 /f
cls
exit


