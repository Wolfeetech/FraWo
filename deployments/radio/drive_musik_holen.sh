#!/usr/bin/env bash
# Alle Musik aus Google Drive (ausser der Bibliotheks-Sicherung FraWo_Musik) auf den Anker kopieren (Odoo #1929).
# Drive bleibt unveraendert (rclone copy). Struktur bleibt erhalten -> Nachweis je Drive-Datei moeglich.
# Tagsueber gedrosselt (Hausanschluss), nachts frei. Laeuft als systemd-Unit auf dem Anker.
set -uo pipefail
ZIEL=/anker-backup/drive-musik-20261006
LOG=/root/drive-musik-holen.log
FILTER=(--ignore-case --filter '+ *.{mp3,flac,wav,aiff,aif,m4a,ogg}' --filter '- *')
for QUELLE in "Stockenweiler" "FraWo_Radio_Library" "00_INBOX"; do
  echo "=== $(date '+%F %T') $QUELLE" >> "$LOG"
  rclone copy "gdrive:$QUELLE" "$ZIEL/$QUELLE" "${FILTER[@]}" \
    --bwlimit "08:00,4M 23:00,off" --transfers 4 --checkers 8 --tpslimit 8 \
    --retries 5 --low-level-retries 20 --stats 10m --stats-one-line -v >> "$LOG" 2>&1
  echo "=== $(date '+%F %T') $QUELLE fertig, rc=$?" >> "$LOG"
done
echo FERTIG >> "$LOG"
