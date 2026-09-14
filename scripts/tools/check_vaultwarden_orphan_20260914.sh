#!/bin/bash
# Diagnose (14.09.2026): findet Vaultwarden-Org-Mitgliedschaften, die auf einen
# nicht mehr existierenden Benutzer zeigen (Ursache des Absturzes in
# get_org_user_mini_details / Endlos-Ladekreis beim Anlegen einer Collection).
# Liest nur Metadaten (Status, E-Mail), keine Passwort-Inhalte.
set -euo pipefail

ssh anker-pve bash -s <<'REMOTE'
set -euo pipefail
pct exec 108 -- docker cp vaultwarden:/data/db.sqlite3 /tmp/vw_check.sqlite3
pct pull 108 /tmp/vw_check.sqlite3 /tmp/vw_check_host.sqlite3
echo "=== Mitgliedschaften der FraWo-Organisation ==="
sqlite3 /tmp/vw_check_host.sqlite3 "SELECT uo.uuid, uo.user_uuid, uo.status, u.email FROM users_organizations uo LEFT JOIN users u ON uo.user_uuid = u.uuid WHERE uo.org_uuid='2c199131-c9ad-432c-bf78-323602baf892';"
pct exec 108 -- rm -f /tmp/vw_check.sqlite3
rm -f /tmp/vw_check_host.sqlite3
REMOTE
