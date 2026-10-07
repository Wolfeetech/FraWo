#!/usr/bin/env bash
# Woechentliche verschluesselte Aussen-Kopie der Nextcloud nach Google Drive (Odoo #1957, Wolf 07.10.2026: "Ja, einrichten").
# Laeuft auf VM300 (Timer So 03:00). Ziel: rclone-crypt "nc-crypt" = gdrive:FraWo-Verschluesselt/nextcloud
# (Schluessel in Vaultwarden: "Nextcloud Cloud-Sicherung rclone-crypt Passwort/Salt").
# - Datenbank-Abzug (mariadb-dump) + Nutzerdaten; ohne Vorschau-Cache (appdata_*/preview), ohne Logs
# - nur Aenderungen (sync); Geloeschtes/Ueberschriebenes landet 30 Tage in nc-crypt:_papierkorb/<datum>
# - Ergebnis als Textfile-Metrik fuer Prometheus (falls node_exporter-Verzeichnis vorhanden) und im Log
set -uo pipefail
DATA=/var/lib/docker/volumes/nextcloud_nextcloud/_data/data
DUMP=/var/backups/nextcloud-db
LOG=/var/log/nextcloud-cloud-sicherung.log
HEUTE=$(date +%F)
exec >> "$LOG" 2>&1
echo "=== $(date '+%F %T') Start"
mkdir -p "$DUMP"; chmod 700 "$DUMP"

docker exec nextcloud_db_1 sh -c 'exec mariadb-dump --single-transaction --quick --all-databases -uroot -p"${MARIADB_ROOT_PASSWORD:-$MYSQL_ROOT_PASSWORD}"' \
  | gzip > "$DUMP/nextcloud-db-$HEUTE.sql.gz.tmp" && mv "$DUMP/nextcloud-db-$HEUTE.sql.gz.tmp" "$DUMP/nextcloud-db-$HEUTE.sql.gz"
RC_DB=$?
find "$DUMP" -name 'nextcloud-db-*.sql.gz' -mtime +14 -delete
echo "DB-Abzug rc=$RC_DB ($(du -h "$DUMP/nextcloud-db-$HEUTE.sql.gz" 2>/dev/null | cut -f1))"

OPT=(--backup-dir "nc-crypt:_papierkorb/$HEUTE" --transfers 4 --checkers 8 --tpslimit 8 --retries 5
     --low-level-retries 20 --bwlimit "06:00,4M 23:00,off" --stats 15m --stats-one-line -v)
rclone sync "$DUMP" nc-crypt:db "${OPT[@]}"; RC1=$?
rclone sync "$DATA" nc-crypt:data "${OPT[@]}" --exclude 'appdata_*/preview/**' --exclude 'nextcloud.log*' \
  --exclude 'lost+found/**' --exclude '*/cache/**' --exclude '*/uploads/**'; RC2=$?
rclone delete nc-crypt:_papierkorb --min-age 30d --tpslimit 8 && rclone rmdirs nc-crypt:_papierkorb --leave-root --tpslimit 8
RC=$(( RC_DB + RC1 + RC2 ))
echo "=== $(date '+%F %T') Ende rc=$RC (db=$RC_DB dbsync=$RC1 daten=$RC2)"

M=/var/lib/prometheus/node-exporter
if [ -d "$M" ]; then
  { echo "# HELP frawo_nextcloud_cloud_sicherung_ok 1 = letzte woechentliche Aussen-Sicherung fehlerfrei"
    echo "frawo_nextcloud_cloud_sicherung_ok $([ $RC -eq 0 ] && echo 1 || echo 0)"
    echo "frawo_nextcloud_cloud_sicherung_zeit $(date +%s)"; } > "$M/nextcloud_cloud_sicherung.prom.tmp" && mv "$M/nextcloud_cloud_sicherung.prom.tmp" "$M/nextcloud_cloud_sicherung.prom"
fi
exit $RC
