@echo off
REM FRAWO Ops - Quick Status Check
REM Double-click to run instant infrastructure check

title FRAWO Ops - Quick Status Check

echo.
echo ========================================
echo    FRAWO Ops - Quick Status Check
echo ========================================
echo.

REM Run quick check
python "%USERPROFILE%\Desktop\pve_check.py"

echo.
echo ========================================
echo.
echo Press any key to close...
pause >nul
