@echo off
setlocal
where ssh >nul 2>&1 || (echo OpenSSH-Client fehlt & exit /b 2)
powershell.exe -ExecutionPolicy Bypass -File "%~dp0PVE-SSH.ps1"
