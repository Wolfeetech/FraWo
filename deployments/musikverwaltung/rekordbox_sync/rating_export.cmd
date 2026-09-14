@echo off
cd /d "%~dp0"
python rating_export.py >> rating_export.log 2>&1
python ..\beets_rating_sync.py >> beets_rating_sync.log 2>&1
python ..\..\radio\radio_vote_weights.py >> radio_vote_weights.log 2>&1
python ..\..\radio\radio_best_of_week.py >> radio_best_of_week.log 2>&1
