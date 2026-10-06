#!/usr/bin/env bash
# Neue Musik aus Google Drive fuers Radio einsortieren (Odoo #1928). Laeuft auf dem ProDesk (pve).
#
#   bash radio_neuzugang.sh "00_INBOX/_Dokumente-zur-Pruefung/rekordbox"            # Probe
#   bash radio_neuzugang.sh "00_INBOX/_Dokumente-zur-Pruefung/rekordbox" --ausfuehren
#
# 1. Drive -> Inbox/neuzugang-<datum> (nur Audio; Drive bleibt unveraendert). Bis zur SSD (#1919)
#    liegt die Musik auf dem Anker (ZFS), deshalb wird dort lokal geschrieben.
# 2. Putzen im Fileserver CT120: APE-Altblock, Titel/Kuenstler/Haendler-Album, bekannte Werbe-Cover.
# 3. Ablegen: Dubletten bleiben im Eingang, neue Titel nach Master_Library/Genre/Kuenstler/Album.
# Die Zuordnung zu den Sendungen (Curated_Playlists 01-10) ist bewusst NICHT Teil davon.
set -euo pipefail
QUELLE=${1:?Drive-Pfad fehlt}
AUS=${2:-}
NAME=neuzugang-$(date +%Y%m%d)
LIVE=/anker-backup/musik-umzug-20261005          # nach SSD-Einbau: Pfad anpassen (#1919)
CT_EIN=/mnt/music/Inbox/$NAME
SICH=/var/lib/beets/$NAME
schritt() { echo; echo "=== $(date '+%T') $*"; }

schritt "1 Drive -> $LIVE/Inbox/$NAME (nur Audio)"
ssh -o BatchMode=yes root@10.1.0.92 "rclone copy 'gdrive:$QUELLE' '$LIVE/Inbox/$NAME' --ignore-case \
  --include '*.{mp3,flac,wav,aiff,aif,m4a,ogg}' --exclude '/Sampler/**' --exclude '/Recording/**' --exclude '**/Sampler/**' \
  --transfers 4 --stats-one-line -v 2>&1 | tail -2; find '$LIVE/Inbox/$NAME' -type f | wc -l"

ct() { pct exec 120 -- "$@"; }
ct mkdir -p "$SICH"
schritt "2a APE-Altbloecke"
ct python3 /var/lib/beets/radio_ape_entfernen.py --root "$CT_EIN" --sicherung "$SICH/ape" $AUS | tail -2
schritt "2b Titel/Kuenstler/Haendler-Alben"
ct python3 /var/lib/beets/radio_titel_putzen.py --root "$CT_EIN" --sicherung "$SICH/titel" $AUS | tail -2
schritt "2c bekannte Werbe-/Haendler-Cover"
ct python3 /var/lib/beets/radio_cover_entfernen.py --root "$CT_EIN" --sha1 /var/lib/beets/entfernen_sha1.txt \
   --sicherung "$SICH/cover" $AUS | tail -2
schritt "3 Ablegen in Master_Library"
ct python3 /var/lib/beets/radio_neuzugang_ablegen.py --quelle "$CT_EIN" --sicherung "$SICH/ablage" $AUS | tail -45
echo; echo "Protokolle: CT120:$SICH"
