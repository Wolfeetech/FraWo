#!/bin/bash
# Meldet den Google-Drive-Push-Kanal an/erneuert ihn. Google-Kanäle
# laufen nach maximal 7 Tagen ab -> läuft 1x/Woche per systemd-Timer,
# NICHT alle paar Minuten. Siehe OPERATIONS/PAPERLESS_OPERATIONS.md.
#
# 22.08.2026: Nach einem harten Stromausfall (Bauarbeiten) scheiterte
# der Lauf 2 Minuten nach dem Boot mit curl-Exitcode 60 (SSL-Fehler,
# vermutlich Systemzeit vor der NTP-Synchronisierung). Deshalb jetzt
# mit mehreren Versuchen statt einmaligem Abbruch.
set -uo pipefail

ENV_FILE="/etc/frawo/gdrive-webhook.env"
[ -f "$ENV_FILE" ] && . "$ENV_FILE"

if [ -z "${GDRIVE_WEBHOOK_SECRET:-}" ] || [ -z "${WEBHOOK_URL:-}" ]; then
  echo "GDRIVE_WEBHOOK_SECRET oder WEBHOOK_URL fehlt in $ENV_FILE" >&2
  exit 1
fi

LOG="/var/log/frawo-gdrive-watch-renew.log"

try_renew() {
  # Frischen Access-Token über rclone holen (rclone refresht selbst).
  rclone lsf gdrive: --max-depth 1 >/dev/null 2>&1 || true
  ACCESS_TOKEN=$(rclone config show gdrive | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)

  if [ -z "$ACCESS_TOKEN" ]; then
    echo "$(date -Is) FEHLER: kein Access-Token von rclone" >> "$LOG"
    return 1
  fi

  CHANNEL_ID="frawo-paperless-$(date +%Y%m%d%H%M%S)"

  START_PAGE_TOKEN=$(curl -s -H "Authorization: Bearer $ACCESS_TOKEN" \
      'https://www.googleapis.com/drive/v3/changes/startPageToken' \
      | grep -o '"startPageToken": *"[^"]*"' | cut -d'"' -f4)

  if [ -z "$START_PAGE_TOKEN" ]; then
    echo "$(date -Is) FEHLER: kein startPageToken erhalten" >> "$LOG"
    return 1
  fi

  RESP=$(curl -s -w "\n%{http_code}" -X POST \
    "https://www.googleapis.com/drive/v3/changes/watch?pageToken=${START_PAGE_TOKEN}" \
    -H "Authorization: Bearer $ACCESS_TOKEN" \
    -H "Content-Type: application/json" \
    -d "{\"id\":\"$CHANNEL_ID\",\"type\":\"web_hook\",\"address\":\"$WEBHOOK_URL\",\"token\":\"$GDRIVE_WEBHOOK_SECRET\"}")

  HTTP_CODE=$(echo "$RESP" | tail -1)
  BODY=$(echo "$RESP" | head -n -1)

  if [ "$HTTP_CODE" = "200" ]; then
    echo "$(date -Is) OK Kanal $CHANNEL_ID angemeldet" >> "$LOG"
    return 0
  else
    echo "$(date -Is) FEHLER ($HTTP_CODE): $BODY" >> "$LOG"
    return 1
  fi
}

ATTEMPTS=5
for i in $(seq 1 "$ATTEMPTS"); do
  if try_renew; then
    exit 0
  fi
  if [ "$i" -lt "$ATTEMPTS" ]; then
    echo "$(date -Is) Versuch $i/$ATTEMPTS fehlgeschlagen, erneuter Versuch in 20s" >> "$LOG"
    sleep 20
  fi
done

echo "$(date -Is) FEHLER: alle $ATTEMPTS Versuche fehlgeschlagen" >> "$LOG"
exit 1
