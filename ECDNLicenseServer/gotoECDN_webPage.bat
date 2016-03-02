@echo off
REG ADD "HKCU\Software\Microsoft\Internet Explorer\Main" /v Window_Placement /t REG_BINARY /d 2c0000000000000001000000ffffffffffffffffffffffffffffffff36010000200000004706000010040000 /f
start iexplore http://kollective.com/microsoft/azure-marketplace/
cls
exit


