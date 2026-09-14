@echo off
cd /d "%~dp0"
python rating_export.py >> rating_export.log 2>&1
