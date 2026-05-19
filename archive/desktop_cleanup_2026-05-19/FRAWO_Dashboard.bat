@echo off
REM FRAWO Ops - Full Infrastructure Dashboard
REM Double-click to run complete status check

title FRAWO Ops - Infrastructure Dashboard

echo.
echo ================================================================================
echo                     FRAWO Ops - Infrastructure Dashboard
echo ================================================================================
echo.

REM Run full dashboard
python "%USERPROFILE%\Desktop\frawo_ops_dashboard.py"

echo.
echo ================================================================================
echo.
echo Press any key to close...
pause >nul
