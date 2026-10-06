#!/usr/bin/env bash
# Drive 00_INBOX -> Nextcloud (wolf) nach Wolfs Regeln vom 06.10. (Odoo #1927). Laeuft auf VM300 als systemd-run-Einheit.
# Nur KOPIE (rclone copy): Drive bleibt unveraendert, Originale erst nach Nachweis in den Papierkorb.
# Musik ist ausgenommen (laeuft ueber #1929 ins Radio). Tagsueber gedrosselt, nachts frei.
set -uo pipefail
NC=/var/lib/docker/volumes/nextcloud_nextcloud/_data/data/wolf/files
LOG=/root/drive-inbox-nach-nextcloud.log
OHNE_MUSIK=(--ignore-case --exclude '*.{mp3,flac,wav,aiff,aif,m4a,ogg}' --exclude '.Trash-*/**')
OPT=(--bwlimit "08:00,2M 23:00,off" --transfers 4 --checkers 8 --tpslimit 8 --retries 5
     --low-level-retries 20 --stats 10m --stats-one-line -v)

kopiere() {  # Drive-Unterordner von 00_INBOX -> Ziel relativ zu wolf/files
  echo "=== $(date '+%F %T') $1 -> $2" >> "$LOG"
  rclone copy "gdrive:00_INBOX/$1" "$NC/$2" "${OHNE_MUSIK[@]}" "${OPT[@]}" >> "$LOG" 2>&1
  echo "=== $(date '+%F %T') fertig rc=$? $1" >> "$LOG"
}

# Kleines zuerst, damit es frueh sichtbar ist
kopiere "_Verarbeitet_Technik_2026-10"      "80_Technik/Software/Installer_2026-10"
kopiere "_Programme-Technik"                "80_Technik/Software/_Programme-Technik"
kopiere "Image-Line"                        "80_Technik/Software/Image-Line"
kopiere "Sammlung/PIONEER"                  "80_Technik/Rekordbox/Sammlung_PIONEER"
kopiere "PIONEER"                           "80_Technik/Rekordbox/PIONEER"
kopiere "Sammlung/Home_files"               "80_Technik/Rekordbox/Home_files"
for d in netzwerk_collective_docs_2025-05-05 azuracast_collective_docs_2025-05-05 playlist_collective_docs_2025-05-05 "Colab Notebooks"; do
  kopiere "$d"                              "80_Technik/IT/Alt-Doku/$d"
done
kopiere "WorkingHours"                      "60_Arbeit/WorkingHours"
kopiere "Working Hours "                    "60_Arbeit/WorkingHours_2"
kopiere "wwolfitec"                         "60_Arbeit/wwolfitec"
kopiere "Noerpel"                           "60_Arbeit/Noerpel"
kopiere "My Games"                          "90_Privat/My Games"
kopiere "KEINE AHNUNG"                      "00_Unsortiert/KEINE AHNUNG"
kopiere "MISC"                              "00_Unsortiert/MISC"
kopiere "Downloads"                         "00_Unsortiert/Downloads"
kopiere "SharedAsLink"                      "00_Unsortiert/SharedAsLink"
kopiere "Bild & Video"                      "Fotos & Videos/Bild & Video"
kopiere "_Fotos-Videos"                     "Fotos & Videos/_Fotos-Videos"
kopiere "MObilEE ZZ"                        "Fotos & Videos/MObilEE ZZ"

chown -R 33:33 "$NC"
docker exec -u www-data nextcloud_app_1 php occ files:scan --path=wolf/files >> "$LOG" 2>&1
echo FERTIG >> "$LOG"
