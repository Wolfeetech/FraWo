#!/usr/bin/env bash
set -euo pipefail

python_output="$(
  ssh -o BatchMode=yes root@toolbox python3 - <<'PY'
import json
import sqlite3
import urllib.request

result = {
    "startup_wizard_completed": "unknown",
    "admin_user_count": 0,
    "total_user_count": 0,
    "music_library_attached": "no",
    "music_library_paths": [],
}

try:
    data = json.load(urllib.request.urlopen("http://127.0.0.1:8096/System/Info/Public", timeout=8))
    result["startup_wizard_completed"] = str(data.get("StartupWizardCompleted", False)).lower()
except Exception:
    pass

con = sqlite3.connect("/srv/jellyfin/config/data/jellyfin.db")
cur = con.cursor()

try:
    rows = list(cur.execute("select PasswordResetProviderId, InvalidLoginAttemptCount, Username from Users"))
    result["total_user_count"] = len(rows)
    result["admin_user_count"] = len(rows)
except Exception:
    pass

try:
    rows = list(
        cur.execute(
            """
            select Name, Path
            from BaseItems
            where Path like '/media/music%'
            order by Path
            """
        )
    )
    result["music_library_paths"] = [path for _, path in rows[:20]]
    if any(path == "/media/music" for _, path in rows):
        result["music_library_attached"] = "yes"
except Exception:
    pass

con.close()

for key, value in result.items():
    if isinstance(value, list):
        print(f"{key}={','.join(value)}")
    else:
        print(f"{key}={value}")
PY
)"

printf '%s\n' "${python_output}"

startup_wizard_completed="$(printf '%s\n' "${python_output}" | awk -F= '/^startup_wizard_completed=/{print $2}')"
admin_user_count="$(printf '%s\n' "${python_output}" | awk -F= '/^admin_user_count=/{print $2}')"
music_library_attached="$(printf '%s\n' "${python_output}" | awk -F= '/^music_library_attached=/{print $2}')"

if [[ "${startup_wizard_completed}" == "true" && "${admin_user_count:-0}" -ge 1 && "${music_library_attached}" == "yes" ]]; then
  echo "toolbox_jellyfin_ui_ready=yes"
  echo "recommendation=continue_media_sync_and_start_client_rollout"
else
  echo "toolbox_jellyfin_ui_ready=no"
  echo "recommendation=finish_jellyfin_ui_setup_before_client_rollout"
fi
