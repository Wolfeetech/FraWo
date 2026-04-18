@echo off
setlocal

powershell -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0bootstrap_windows_operator_workstation.ps1"

if errorlevel 1 (
  echo status=failed
  exit /b 1
)

echo status=ready
