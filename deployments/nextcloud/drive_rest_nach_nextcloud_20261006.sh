#!/usr/bin/env bash
# Drive-Restbestand -> Nextcloud (wolf) nach DOCS/ABLAGEORDNUNG.md (Odoo #1927). Laeuft auf VM300 als systemd-run-Einheit,
# startet erst, wenn drive-inbox-nach-nextcloud fertig ist (Bandbreite). Nur KOPIE, Drive bleibt unveraendert.
# Belege aus 10-99 gehen getrennt in den Paperless-Eingang; Musik laeuft ueber #1929; proxmox_backups (alt) bleibt aussen vor.
set -uo pipefail
NC=/var/lib/docker/volumes/nextcloud_nextcloud/_data/data/wolf/files
LOG=/root/drive-rest-nach-nextcloud.log
OHNE=(--ignore-case --exclude '*.{mp3,flac,wav,aiff,aif,m4a,ogg}' --exclude '.Trash-*/**' --exclude '.env/**'
      --exclude 'node_modules/**' --exclude '.vscode/**')
OPT=(--bwlimit "06:00,2M 21:00,off" --transfers 4 --checkers 8 --tpslimit 8 --retries 5
     --low-level-retries 20 --stats 10m --stats-one-line -v)

while systemctl is-active --quiet drive-inbox-nach-nextcloud; do sleep 300; done

kopiere() {
  echo "=== $(date '+%F %T') $1 -> $2" >> "$LOG"
  rclone copy "gdrive:$1" "$NC/$2" "${OHNE[@]}" "${OPT[@]}" >> "$LOG" 2>&1
  echo "=== $(date '+%F %T') fertig rc=$? $1" >> "$LOG"
}

# Arbeitsunterlagen aus der alten Drive-Ablage (keine Belege)
kopiere "60_Arbeit und Gewebe/Ausbildereignung"          "60_Arbeit_und_Gewerbe/Ausbildung/Ausbildereignung"
kopiere "60_Arbeit und Gewebe/Cloud_Speicher_Privat"     "70_Projekte/Wolfprox/Cloud_Speicher_Privat"
kopiere "70_Projekte/Wolfprox_Systemdokumentation"       "70_Projekte/Wolfprox/Systemdokumentation"
kopiere "70_Projekte/Hobbys_Freizeit_Private_Projekte"   "95_Privat/Hobbys_Projekte"
kopiere "70_Projekte/Wohnen_Haushalt"                    "50_Wohnen/Haushalt"
kopiere "70_Projekte/manuals"                            "80_Technik/Handbuecher"
kopiere "99_Archiv/Archiv-KI-Komplettarchiv"             "99_Archiv/KI-Komplettarchiv"
kopiere "99_Archiv/Private_Korrespondenz"                "95_Privat/Korrespondenz"
kopiere "Messungen NTi"                                  "80_Technik/Ton/Messungen_NTi"
kopiere "Google AI Studio"                               "80_Technik/IT/Google_AI_Studio"

# Alte Komplettsicherung Stockenweiler (Wolfs Daten 2023-07/2026) als durchsuchbarer Altbestand
for d in "Dokumente" "backups" "bis 24" "Onenotes" "Programme" "KEINE AHNUNG" "private_videos" "paperless_init" \
         "FraWo_review_imports_archives" "Media Monkey Database" "temp_rescue" "Deutsch" "MediaMonkey" \
         "VBANReceptor_v1005" "VBANTalkie_v1006" "paperless_mongo_sync"; do
  kopiere "Stockenweiler/data_family/$d"                 "99_Archiv/Altbestand_Stockenweiler/$d"
done

chown -R 33:33 "$NC"
docker exec -u www-data nextcloud_app_1 php occ files:scan --path=wolf/files >> "$LOG" 2>&1
echo FERTIG >> "$LOG"
