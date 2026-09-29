#!/bin/bash
# deployments/paperless/frawo-gdrive-inbox-pull.sh
set -euo pipefail

STAGING="/opt/frawo-gdrive-bridge/staging"
LOG="/var/log/frawo-gdrive-inbox.log"
mkdir -p "$STAGING"

# Holen von neuen Dateien (mindestens 30s alt, um unfertige Uploads zu vermeiden)
rclone move "gdrive:00_INBOX/_Dokumente-zur-Pruefung" "$STAGING" \
  --drive-chunk-size 64M --drive-upload-cutoff 64M \
  --min-age 30s -q --create-empty-src-dirs

shopt -s nullglob
for f in "$STAGING"/*; do
  [ -f "$f" ] || continue
  raw_name=$(basename "$f")
  # Sanitize special unicode characters (like fullwidth solidus U+FF0F)
  clean_name=$(echo "$raw_name" | tr '／' '_')
  if [ "$raw_name" != "$clean_name" ]; then
    mv "$f" "$STAGING/$clean_name"
    f="$STAGING/$clean_name"
  fi
  
  # Seit 29.09.2026 (Claude): Handy-Uploads kommen teils ohne ".pdf" an (z. B. "...Pixel9pdf").
  # Paperless ignoriert Dateien ohne bekannte Endung STILLSCHWEIGEND - so lagen Belege
  # wochenlang im Eingang. Erkennung am Inhalt (%PDF-), nicht am Namen.
  if [ "$(head -c 5 "$f")" = "%PDF-" ] && [[ "${clean_name,,}" != *.pdf ]]; then
    basis="${clean_name%[Pp][Dd][Ff]}"; basis="${basis%.}"
    basis="$(printf '%s' "$basis" | sed 's/[[:space:]]*$//')"
    echo "$(date -Is) UMBENANNT $clean_name -> ${basis}.pdf" >> "$LOG"
    clean_name="${basis}.pdf"
    mv "$f" "$STAGING/$clean_name"
    f="$STAGING/$clean_name"
  fi

  if pct push 110 "$f" "/opt/paperless/consume/$clean_name"; then
    rm -f "$f"
    echo "$(date -Is) OK $clean_name" >> "$LOG"
  else
    echo "$(date -Is) FEHLER beim Kopieren nach CT110: $clean_name" >> "$LOG"
  fi
done
