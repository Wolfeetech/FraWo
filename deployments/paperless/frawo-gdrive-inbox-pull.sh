#!/bin/bash
# Holt neue Dateien aus Google Drive (00_INBOX/_Dokumente-zur-Pruefung) und
# legt sie in den Paperless-Consume-Ordner auf CT110. Läuft per Cron alle
# 5 Minuten auf stock-pve. Teil der Paperless-GDrive-Pipeline,
# siehe OPERATIONS/PAPERLESS_OPERATIONS.md im FraWo-Repo.
set -euo pipefail

STAGING="/opt/frawo-gdrive-bridge/staging"
LOG="/var/log/frawo-gdrive-inbox.log"
mkdir -p "$STAGING"

# --min-age verhindert, dass eine noch laufende Google-Drive-Hochladung
# mitten drin gegriffen wird.
rclone move "gdrive:00_INBOX/_Dokumente-zur-Pruefung" "$STAGING" \
  --drive-chunk-size 64M --drive-upload-cutoff 64M \
  --min-age 30s -q --create-empty-src-dirs

shopt -s nullglob
for f in "$STAGING"/*; do
  [ -f "$f" ] || continue
  filename=$(basename "$f")
  if pct push 110 "$f" "/opt/paperless/consume/$filename"; then
    rm -f "$f"
    echo "$(date -Is) OK $filename" >> "$LOG"
  else
    echo "$(date -Is) FEHLER beim Kopieren nach CT110: $filename" >> "$LOG"
  fi
done
