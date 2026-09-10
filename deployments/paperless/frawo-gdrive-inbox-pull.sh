#!/usr/bin/env bash
# frawo-gdrive-inbox-pull.sh
# Holt neue Dateien aus Google Drive (00_INBOX/_Dokumente-zur-Pruefung) und
# verschiebt sie direkt in den Paperless-Consume-Ordner auf CT110.
# Laeuft per systemd-Timer (frawo-paperless-ingest.timer) alle 10 Minuten auf CT110.
# Teil der Paperless-GDrive-Pipeline (siehe OPERATIONS/PAPERLESS_OPERATIONS.md).
# Ersetzt den alten ProDesk-Webhook und Google-Watch-Erneuerungszyklus.

set -euo pipefail

CONSUME_DIR="/opt/paperless/consume"
GDRIVE_DIR="gdrive:00_INBOX/_Dokumente-zur-Pruefung"
LOCK_FILE="/var/lock/frawo-paperless-ingest.lock"
LOG_FILE="/var/log/frawo-paperless-ingest.log"

# Mutex gegen ueberlappende Laeufe
exec 200>"$LOCK_FILE"
flock -n 200 || {
    echo "$(date -Is) [SKIP] Ein anderer Ingest-Lauf ist noch aktiv."
    exit 0
}

if [ ! -d "$CONSUME_DIR" ]; then
    echo "$(date -Is) [ERROR] Consume-Verzeichnis $CONSUME_DIR existiert nicht!" | tee -a "$LOG_FILE" >&2
    exit 1
fi

TMP_OUT=$(mktemp /tmp/rclone-ingest.XXXXXX)
trap 'rm -f "$TMP_OUT"' EXIT

if rclone move "$GDRIVE_DIR" "$CONSUME_DIR" \
    --drive-chunk-size 64M \
    --drive-upload-cutoff 64M \
    --min-age 30s \
    -v --stats-one-line > "$TMP_OUT" 2>&1; then
    
    # Berechtigungen fuer Paperless Consumer (UID 1000) sicherstellen
    chown -R 1000:1000 "$CONSUME_DIR"
    find "$CONSUME_DIR" -mindepth 1 -type f -exec chmod 664 {} + 2>/dev/null || true
    find "$CONSUME_DIR" -mindepth 1 -type d -exec chmod 775 {} + 2>/dev/null || true

    # Wenn Dateien uebertragen wurden, ins Log schreiben
    if grep -q "Transferred:" "$TMP_OUT" && ! grep -q "Transferred: *0 B / 0 B" "$TMP_OUT"; then
        echo "$(date -Is) [PULL] Neue Dokumente nach $CONSUME_DIR uebernommen:" | tee -a "$LOG_FILE"
        cat "$TMP_OUT" | tee -a "$LOG_FILE"
    fi
else
    echo "$(date -Is) [ERROR] rclone move fehlgeschlagen:" | tee -a "$LOG_FILE" >&2
    cat "$TMP_OUT" | tee -a "$LOG_FILE" >&2
    exit 1
fi

exit 0
