#!/bin/bash
# ==============================================================================
# FraWo Alopri-Scan-Ingest (CT120 Samba -> CT110 Paperless-ngx)
# ==============================================================================
# Liest Scans aus der Samba-Ablage (/mnt/music_hdd/Scans/[Alois,Heidi,Franz,Wolfgang])
# ein, versieht sie mit Personen-Präfix und übergibt sie atomar an den
# Paperless-Consume-Ordner auf CT110.
# ==============================================================================
set -euo pipefail

SCAN_BASE="/mnt/music_hdd/Scans"
LOG="/var/log/frawo-scan-ingest.log"
STAGING="/opt/frawo-gdrive-bridge/scan-staging"
mkdir -p "$STAGING"

# Unterstützte Unterordner / Personen
PERSONS=("Alois" "Heidi" "Franz" "Wolfgang")

for person in "${PERSONS[@]}"; do
  folder="$SCAN_BASE/$person"
  [ -d "$folder" ] || continue

  shopt -s nullglob
  for f in "$folder"/*; do
    [ -f "$f" ] || continue
    
    # Dateiende prüfen (.pdf, .jpg, .jpeg, .png, .tiff)
    ext="${f##*.}"
    ext_lower=$(echo "$ext" | tr '[:upper:]' '[:lower:]')
    case "$ext_lower" in
      pdf|jpg|jpeg|png|tif|tiff) ;;
      *) continue ;;
    esac

    # Mindestalter 10 Sekunden (verhindert unvollständiges Kopieren durch den Scanner)
    file_age=$(( $(date +%s) - $(stat -c %Y "$f") ))
    if [ "$file_age" -lt 10 ]; then
      continue
    fi

    orig_name=$(basename "$f")
    timestamp=$(date +%Y%m%d_%H%M%S)
    target_name="SCAN_${person}_${timestamp}_${orig_name}"
    staging_file="$STAGING/$target_name"

    # Datei atomar nach Staging verschieben
    mv "$f" "$staging_file"

    # Nach CT110 in den Paperless-Consume-Ordner pushen
    if pct push 110 "$staging_file" "/opt/paperless/consume/$target_name"; then
      rm -f "$staging_file"
      echo "$(date -Is) OK [Person: $person] $orig_name -> $target_name" >> "$LOG"
    else
      echo "$(date -Is) FEHLER beim Push nach CT110: $staging_file" >> "$LOG"
    fi
  done
done
