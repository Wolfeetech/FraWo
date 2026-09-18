#!/usr/bin/env bash
set -uo pipefail

SERVICE="${SERVICE:-rclone-gdrive-v2.service}"
MOUNT_POINT="${MOUNT_POINT:-/mnt/google-drive}"
MAIL_TO="${MAIL_TO:-dev@frawo-tech.de}"
MAX_ATTEMPTS="${MAX_ATTEMPTS:-3}"
SLEEP_SECONDS="${SLEEP_SECONDS:-20}"
LOG_FILE="${LOG_FILE:-/var/log/rclone-gdrive-watchdog.log}"
LOCK_FILE="${LOCK_FILE:-/run/rclone-gdrive-watchdog.lock}"

send_mail() {
  local subject="$1"
  local body="$2"

  if command -v mail >/dev/null 2>&1; then
    printf '%s\n' "$body" | mail -s "$subject" "$MAIL_TO"
  elif command -v sendmail >/dev/null 2>&1; then
    {
      printf 'To: %s\n' "$MAIL_TO"
      printf 'Subject: %s\n' "$subject"
      printf '\n%s\n' "$body"
    } | sendmail -t
  else
    printf '%s %s\n' "$(date -Is)" "mail command not found; alert was: $subject" >> "$LOG_FILE"
  fi
}

log() {
  printf '%s %s\n' "$(date -Is)" "$*" >> "$LOG_FILE"
}

healthy() {
  mountpoint -q "$MOUNT_POINT" && (systemctl is-active --quiet "$SERVICE" || systemctl is-active --quiet rclone-gdrive-temp.service)
}

exec 9>"$LOCK_FILE"
if ! flock -n 9; then
  log "watchdog already running"
  exit 0
fi

if healthy; then
  log "$SERVICE healthy and $MOUNT_POINT mounted"
  exit 0
fi

log "$SERVICE unhealthy or $MOUNT_POINT not mounted; starting restart attempts"

attempt=1
while [ "$attempt" -le "$MAX_ATTEMPTS" ]; do
  log "restart attempt $attempt/$MAX_ATTEMPTS for $SERVICE"
  systemctl restart "$SERVICE" >> "$LOG_FILE" 2>&1 || true
  sleep "$SLEEP_SECONDS"

  if healthy; then
    log "$SERVICE recovered after attempt $attempt"
    exit 0
  fi

  attempt=$((attempt + 1))
done

status="$(systemctl status "$SERVICE" --no-pager -l 2>&1 | tail -n 40 || true)"
mounts="$(findmnt "$MOUNT_POINT" 2>&1 || true)"
message="$SERVICE could not recover after $MAX_ATTEMPTS restart attempts.

Mount check:
$mounts

Recent service status:
$status"

log "$SERVICE failed after $MAX_ATTEMPTS attempts"
send_mail "proxmox-anker rclone-gdrive failed" "$message"
exit 2