#!/bin/bash
# Einmal-Skript (14.09.2026): entfernt die alten, bereits deaktivierten
# Misch-Playlists 846-855 endgueltig aus AzuraCast und raeumt ihre
# Symlink-Ordner weg. Wolf hat das am 14.09.2026 ausdruecklich freigegeben.
#
# Sicherheitsnetz: Die vollstaendige Sicherung dieser Playlists inkl. aller
# Titel-Zuordnungen (7647 Datensaetze) liegt im Repo unter
#   deployments/radio/backups/alte-playlists-846-855-backup-20260914.sql
# und ist bereits committed (Rueckweg jederzeit moeglich).
#
# NICHT angefasst werden: _Emergency (enthaelt den Notfall-Titel) und
# _Jingles - die haengen an keiner Playlist und bleiben bestehen.
set -euo pipefail

ALT_IDS="846,847,848,849,851,852,853,854,855"
ORDNER="Ch1_Acoustik_Ambient Ch2_Soft_Groove Ch3_Harder_Styles Ch4_Roadtrip_Classics Sunrise"

echo "=== 0/5 Sicherung im Repo vorhanden? ==="
BACKUP="$(dirname "$0")/../../deployments/radio/backups/alte-playlists-846-855-backup-20260914.sql"
if [ ! -s "$BACKUP" ]; then
  echo "ABBRUCH: Sicherung fehlt unter $BACKUP" >&2
  exit 1
fi
echo "vorhanden ($(wc -l < "$BACKUP") Zeilen)"

echo "=== 1/5 Sender vorher ==="
curl -s --max-time 10 "https://funk.frawo.tech/api/nowplaying/1" \
  | python3 -c "import json,sys; d=json.load(sys.stdin); print('  online:', d.get('is_online'), '| laeuft:', d.get('now_playing',{}).get('playlist'))"

echo "=== 2/5 Pruefen, dass die 10 neuen Shows aktiv sind (Sicherheitsanker) ==="
AKTIV=$(ssh stock-pve "qm guest exec 210 -- /bin/bash -c \"docker exec azuracast sh -c 'mariadb -h \\\"\\\$MYSQL_HOST\\\" -u \\\"\\\$MYSQL_USER\\\" -p\\\"\\\$MYSQL_PASSWORD\\\" \\\"\\\$MYSQL_DATABASE\\\" --skip-column-names -e \\\"SELECT COUNT(*) FROM station_playlists WHERE station_id=1 AND is_enabled=1;\\\"'\"" \
  | python3 -c "import json,sys; print(json.load(sys.stdin).get('out-data','0').strip())")
echo "  aktive Playlists: $AKTIV"
if [ "$AKTIV" -lt 10 ]; then
  echo "ABBRUCH: weniger als 10 aktive Shows - hier stimmt etwas nicht." >&2
  exit 1
fi

echo "=== 3/5 Alte Playlists loeschen ==="
ssh stock-pve "qm guest exec 210 -- /bin/bash -c \"docker exec azuracast sh -c 'mariadb -h \\\"\\\$MYSQL_HOST\\\" -u \\\"\\\$MYSQL_USER\\\" -p\\\"\\\$MYSQL_PASSWORD\\\" \\\"\\\$MYSQL_DATABASE\\\" -e \\\"DELETE FROM station_playlists WHERE id IN ($ALT_IDS);\\\"'\""
echo "  geloescht."

echo "=== 4/5 Sender neu laden (Pflicht nach DB-Aenderung) ==="
ssh stock-pve "qm guest exec 210 -- /bin/bash -c \"docker exec azuracast azuracast_cli azuracast:radio:restart 1\"" >/dev/null
sleep 15
curl -s --max-time 15 "https://funk.frawo.tech/api/nowplaying/1" \
  | python3 -c "import json,sys; d=json.load(sys.stdin); print('  online:', d.get('is_online'), '| laeuft:', d.get('now_playing',{}).get('playlist'))"

echo "=== 5/5 Alte Symlink-Ordner wegraeumen (verschieben, nicht loeschen) ==="
ssh stock-pve "pct exec 120 -- sh -lc 'mkdir -p /mnt/music/_stillgelegt-20260914; cd /mnt/music/Curated_Playlists; for d in $ORDNER; do [ -d \"\$d\" ] && mv \"\$d\" /mnt/music/_stillgelegt-20260914/ && echo \"  verschoben: \$d\"; done; echo; echo \"  verbleibend:\"; ls /mnt/music/Curated_Playlists/'"

echo
echo "Fertig. Rueckweg falls noetig: Sicherung einspielen und Ordner aus"
echo "/mnt/music/_stillgelegt-20260914/ zurueckschieben."
