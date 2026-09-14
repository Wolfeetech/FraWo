#!/bin/bash
# Fix (14.09.2026): entfernt die verwaiste Vaultwarden-Org-Mitgliedschaft
# d309b890-b834-443e-96bc-bedbd70ebd67 (user_uuid b743d585-...-0e3260bef677
# existiert nicht mehr in der users-Tabelle), die den Absturz in
# get_org_user_mini_details / Endlos-Ladekreis beim Anlegen einer Collection
# verursacht.
#
# Ablauf: Container sauber stoppen (WAL-Checkpoint), komplette DB sichern,
# NUR diese eine Zeile per stabiler UUID loeschen, Container neu starten.
set -euo pipefail
ORPHAN_UUID="d309b890-b834-443e-96bc-bedbd70ebd67"
DB="/opt/vaultwarden/vw-data/db.sqlite3"

ssh anker-pve bash -s <<REMOTE
set -euo pipefail
STAMP=\$(date +%Y%m%d-%H%M%S)

echo "1/6 Vaultwarden sauber stoppen (WAL-Checkpoint)..."
pct exec 108 -- sh -lc 'cd /opt/vaultwarden && docker compose stop'

echo "2/6 Backup der Datenbank (inkl. WAL/SHM falls vorhanden)..."
pct exec 108 -- sh -lc 'cp ${DB} ${DB}.bak-\${STAMP}; cp ${DB}-wal ${DB}-wal.bak-\${STAMP} 2>/dev/null || true; cp ${DB}-shm ${DB}-shm.bak-\${STAMP} 2>/dev/null || true'

echo "3/6 Datenbank zum Bearbeiten herunterladen..."
pct pull 108 ${DB} /tmp/vw_fix_host.sqlite3

echo "4/6 Verwaiste Zeile loeschen (Ziel-UUID: ${ORPHAN_UUID})..."
sqlite3 /tmp/vw_fix_host.sqlite3 "DELETE FROM users_organizations WHERE uuid='${ORPHAN_UUID}';"
echo "Geloeschte Zeilen (sollte 1 sein):"
sqlite3 /tmp/vw_fix_host.sqlite3 "SELECT changes();"

echo "5/6 Reparierte Datenbank zurueckspielen..."
pct push 108 /tmp/vw_fix_host.sqlite3 ${DB}
rm -f /tmp/vw_fix_host.sqlite3

echo "6/6 Vaultwarden wieder starten..."
pct exec 108 -- sh -lc 'cd /opt/vaultwarden && docker compose up -d'
sleep 3
pct exec 108 -- docker inspect vaultwarden --format 'Status: {{.State.Status}}'
REMOTE

echo ""
echo "=== Oeffentliche Erreichbarkeit ==="
curl -s -o /dev/null -w "HTTP %{http_code}\n" https://vault.frawo.tech/alive --max-time 10
echo ""
echo "Fertig. Bitte https://vault.frawo.tech/ neu laden und Organisation/Collection-Anlage testen."
