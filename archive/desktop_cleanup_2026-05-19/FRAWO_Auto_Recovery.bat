@echo off
REM FRAWO Ops - Automated Recovery System
REM Double-click to attempt automatic service recovery

title FRAWO Ops - Auto Recovery

echo.
echo ================================================================================
echo                     FRAWO Ops - Automated Recovery System
echo ================================================================================
echo.
echo This will attempt to automatically recover offline services.
echo.
pause

REM Run auto recovery
python "%USERPROFILE%\Desktop\frawo_auto_recovery.py"

echo.
echo ================================================================================
echo.
echo Press any key to close...
pause >nul
