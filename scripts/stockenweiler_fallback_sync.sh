#!/bin/bash
# Sync critical media and backups to the remote Stockenweiler 1TB HDD daily.
# This strictly overwrites / mirrors to prevent space bloat (Fallback Strategy).

SOURCE_DIR="/mnt/wolf-ee/hs27_local_dump_archive" # TBD exact path
TARGET_HOST="root@100.91.20.116"
TARGET_DIR="/mnt/stockenweiler-hdd/remote_fallback_backup"

echo "Starting Fallback Sync to Stockenweiler at $(date)"
# Using --delete to ensure exact mirroring and avoid bloating the 1TB disk over time
rsync -aP --delete "${SOURCE_DIR}/" "${TARGET_HOST}:${TARGET_DIR}/"
echo "Sync Complete at $(date)"
