@echo off
set SURFACE_IP=192.168.2.154
set SOURCE_HTML=C:\WORKSPACE\FraWo\artifacts\surface_index_v2_with_nowplaying.html
set TARGET_PATH=/home/frontend/homeserver2027-portal/index.html

echo ########################################################
echo # FRAWO SURFACE CONTROL V2 DEPLOYMENT
echo ########################################################
echo.
echo Source: %SOURCE_HTML%
echo Target: %TARGET_PATH% on %SURFACE_IP%
echo.
echo Bitte gib das Passwort fuer den User 'frontend' ein, wenn du dazu aufgefordert wirst.
echo.

scp "%SOURCE_HTML%" frontend@%SURFACE_IP%:%TARGET_PATH%

if %errorlevel% neq 0 (
    echo.
    echo [!] Fehler beim Kopieren der Datei.
    pause
    exit /b %errorlevel%
)

echo.
echo [+] HTML erfolgreich kopiert. Starte Kiosk neu...
echo.

ssh frontend@%SURFACE_IP% "systemctl --user restart firefox-kiosk"

echo.
echo [+] Deployment abgeschlossen!
echo ########################################################
pause
