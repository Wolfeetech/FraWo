#!/usr/bin/env bash
# =============================================================================
# FraWo GbR — AzuraCast Payload (Database & Config) Backup
# =============================================================================
# This script runs on Stockenweiler VM 210 (AzuraCast) to create a daily,
# lightweight snapshot of station configs, playlists, and historical data.
# It excludes heavy music media files and copies archives to the Storage Node.
# =============================================================================

set -euo pipefail

# Configurations
AZURACAST_DIR="/var/azuracast"
BACKUP_LOCAL_DIR="/var/azuracast/backups"
BACKUP_REMOTE_DIR="/mnt/storage/media/backups/azuracast_payload" # Storage Node Mount
ROTATION_DAYS=7
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILENAME="azuracast_payload_${TIMESTAMP}.zip"

log() {
  printf '[backup-azuracast] %s\n' "$*"
}

error() {
  printf '[backup-azuracast] [ERROR] %s\n' "$*" >&2
}

# 1. Pre-flight Checks
log "Starting daily AzuraCast database & configuration backup..."

if [ ! -d "$AZURACAST_DIR" ]; then
  error "AzuraCast installation directory not found at $AZURACAST_DIR"
  exit 1
fi

mkdir -p "$BACKUP_LOCAL_DIR"

# 2. Trigger AzuraCast Native CLI Backup (Excluding Media)
log "Running AzuraCast CLI backup (excluding heavy music media)..."
cd "$AZURACAST_DIR"

# Detect if using Docker Compose V2 or V1
if docker compose version >/dev/null 2>&1; then
  DOCKER_CMD="docker compose"
else
  DOCKER_CMD="docker-compose"
fi

# Execute native CLI backup tool in web container
if ! $DOCKER_CMD exec -T web azuracast_cli backup "$BACKUP_LOCAL_DIR/$BACKUP_FILENAME" --exclude-media; then
  # Fallback if executing through docker container directly
  log "Warning: Docker Compose exec failed, attempting fallback direct docker container exec..."
  if ! docker exec -t azuracast azuracast_cli backup "/var/azuracast/backups/$BACKUP_FILENAME" --exclude-media; then
    error "Failed to create AzuraCast backup via CLI!"
    exit 1
  fi
fi

log "Backup file successfully created: $BACKUP_LOCAL_DIR/$BACKUP_FILENAME"

# 3. Copy to Central Storage Node (if mounted)
if [ -d "$BACKUP_REMOTE_DIR" ]; then
  log "Syncing backup to off-host Storage Node: $BACKUP_REMOTE_DIR"
  mkdir -p "$BACKUP_REMOTE_DIR"
  if cp "$BACKUP_LOCAL_DIR/$BACKUP_FILENAME" "$BACKUP_REMOTE_DIR/"; then
    log "Off-host sync successful."
  else
    log "Warning: Failed to copy backup to Storage Node. Keeping local copy only."
  fi
else
  log "Warning: Central Storage Node mount not found at $BACKUP_REMOTE_DIR. Skipping off-host sync."
fi

# 4. Prune Local Backups (Keep last $ROTATION_DAYS days)
log "Pruning local backups older than $ROTATION_DAYS days..."
find "$BACKUP_LOCAL_DIR" -name "azuracast_payload_*.zip" -type f -mtime +"$ROTATION_DAYS" -exec rm -f {} \; -print

# 5. Prune Remote Storage Node Backups (Keep last $ROTATION_DAYS days)
if [ -d "$BACKUP_REMOTE_DIR" ]; then
  log "Pruning remote backups on Storage Node older than $ROTATION_DAYS days..."
  find "$BACKUP_REMOTE_DIR" -name "azuracast_payload_*.zip" -type f -mtime +"$ROTATION_DAYS" -exec rm -f {} \; -print
fi

log "Backup rotation and execution completed successfully!"
