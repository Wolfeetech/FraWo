#!/usr/bin/env bash
# pbs_rclone_gdrive_sync.sh — Sync PBS datastore to Google Drive with rate-limit handling
# and ssd2tb local fallback.
#
# Accounts for Google API quota/rate-limit events during large backup traffic:
#   - Bandwidth cap via --bwlimit to avoid quota exhaustion
#   - Transaction-per-second cap via --tpslimit / --tpslimit-burst
#   - Automatic retry with --retries and --low-level-retries
#
# Fallback order:
#   1. Primary: gdrive:pbs-backups (Google Drive via rclone)
#   2. Fallback: /mnt/ssd2tb/pbs-backups (local 2TB SSD mirror)
#
# Intended schedule (cron on PBS VM 240):
#   0 5 * * * /usr/local/bin/pbs_rclone_gdrive_sync.sh >> /var/log/pbs-rclone-sync.log 2>&1
set -euo pipefail

PBS_DATASTORE_PATH="${PBS_DATASTORE_PATH:-/mnt/pbs-data}"
GDRIVE_REMOTE="${GDRIVE_REMOTE:-gdrive:pbs-backups}"
SSD2TB_FALLBACK_PATH="${SSD2TB_FALLBACK_PATH:-/mnt/ssd2tb/pbs-backups}"

# Google API rate-limit settings
# --bwlimit: cap upload bandwidth (MiB/s) to avoid quota bursts
# --tpslimit: transactions per second limit
# --tpslimit-burst: short burst allowance
RCLONE_BWLIMIT="${RCLONE_BWLIMIT:-50M}"
RCLONE_TPSLIMIT="${RCLONE_TPSLIMIT:-8}"
RCLONE_TPSLIMIT_BURST="${RCLONE_TPSLIMIT_BURST:-16}"

LOG_PREFIX="[pbs-rclone-sync]"

log() {
  printf '%s %s %s\n' "$(date -u '+%Y-%m-%dT%H:%M:%SZ')" "${LOG_PREFIX}" "$*"
}

sync_to_gdrive() {
  log "Starting primary sync: ${PBS_DATASTORE_PATH} -> ${GDRIVE_REMOTE}"
  rclone sync "${PBS_DATASTORE_PATH}/" "${GDRIVE_REMOTE}/" \
    --bwlimit "${RCLONE_BWLIMIT}" \
    --tpslimit "${RCLONE_TPSLIMIT}" \
    --tpslimit-burst "${RCLONE_TPSLIMIT_BURST}" \
    --retries 5 \
    --low-level-retries 10 \
    --retries-sleep 30s \
    --stats 60s \
    --stats-log-level NOTICE \
    --log-level INFO \
    --transfers 4 \
    --checkers 8 \
    --exclude "*.tmp" \
    --exclude "*.lock"
  log "Primary sync complete: ${GDRIVE_REMOTE}"
}

sync_to_ssd2tb_fallback() {
  if [[ ! -d "${SSD2TB_FALLBACK_PATH%/*}" ]]; then
    log "ssd2tb mount path ${SSD2TB_FALLBACK_PATH%/*} not available; skipping fallback."
    return 1
  fi
  mkdir -p "${SSD2TB_FALLBACK_PATH}"
  log "Starting fallback sync: ${PBS_DATASTORE_PATH} -> ${SSD2TB_FALLBACK_PATH}"
  rsync -aP --delete \
    --exclude="*.tmp" \
    --exclude="*.lock" \
    "${PBS_DATASTORE_PATH}/" "${SSD2TB_FALLBACK_PATH}/"
  log "Fallback sync complete: ${SSD2TB_FALLBACK_PATH}"
}

check_ssd2tb_health() {
  if mountpoint -q "${SSD2TB_FALLBACK_PATH%/*}" 2>/dev/null; then
    if df "${SSD2TB_FALLBACK_PATH%/*}" >/dev/null 2>&1; then
      echo "healthy"
      return 0
    fi
  fi
  echo "unavailable"
  return 1
}

log "=== PBS rclone sync started ==="
log "Source datastore: ${PBS_DATASTORE_PATH}"

gdrive_ok=false
if sync_to_gdrive; then
  gdrive_ok=true
  log "gdrive_sync=ok"
else
  log "gdrive_sync=FAILED — will attempt ssd2tb fallback"
fi

ssd2tb_status="$(check_ssd2tb_health || echo 'unavailable')"
log "ssd2tb_health=${ssd2tb_status}"

if [[ "${ssd2tb_status}" == "healthy" ]]; then
  if sync_to_ssd2tb_fallback; then
    log "ssd2tb_fallback_sync=ok"
  else
    log "ssd2tb_fallback_sync=FAILED"
  fi
else
  log "ssd2tb_fallback_sync=skipped (disk unavailable — hardware check required)"
fi

if [[ "${gdrive_ok}" == "false" && "${ssd2tb_status}" != "healthy" ]]; then
  log "CRITICAL: Both primary (gdrive) and fallback (ssd2tb) sync failed."
  exit 1
fi

log "=== PBS rclone sync finished ==="
