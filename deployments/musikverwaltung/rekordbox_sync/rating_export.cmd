@echo off
cd /d "%~dp0"
python rating_export.py >> rating_export.log 2>&1
python ..\..\radio\radio_vote_weights.py >> radio_vote_weights.log 2>&1
