@echo off
powershell.exe -Command "Set-NetIPInterface -InterfaceIndex 18 -InterfaceMetric 10"
powershell.exe -Command "Set-NetIPInterface -InterfaceIndex 17 -InterfaceMetric 40"
