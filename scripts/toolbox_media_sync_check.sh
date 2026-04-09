#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "${ROOT_DIR}/scripts/toolbox_remote.sh"

mount_state="$(run_toolbox_remote 'findmnt -T /srv/media-library/music-network >/dev/null 2>&1 && echo yes || echo no' 2>/dev/null || echo no)"
target_state="$(run_toolbox_remote 'test -d /srv/media-library/music-network/yourparty_Libary && echo yes || echo no' 2>/dev/null || echo no)"
target_file_count="$(run_toolbox_remote 'find /srv/media-library/music-network/yourparty_Libary -type f 2>/dev/null | wc -l' 2>/dev/null || echo 0)"
target_size="$(run_toolbox_remote 'du -sh /srv/media-library/music-network/yourparty_Libary 2>/dev/null | awk "{print \$1}"' 2>/dev/null || echo 0)"

echo "toolbox_media_storage_mount_ready=${mount_state:-no}"
echo "toolbox_media_storage_target_ready=${target_state:-no}"
echo "toolbox_media_sync_target_file_count=${target_file_count:-0}"
echo "toolbox_media_sync_target_size=${target_size:-0}"
echo "toolbox_media_sync_service_state=retired"
echo "toolbox_media_sync_timer_state=retired"
echo "toolbox_media_sync_timer_enabled=retired"

if [[ "${mount_state}" == "yes" && "${target_state}" == "yes" ]]; then
  echo "toolbox_media_sync_ready=yes"
  echo "recommendation=central_smb_media_path_is_ready_for_jellyfin"
else
  echo "toolbox_media_sync_ready=no"
  echo "recommendation=mount_storage_node_media_share_on_toolbox_and_verify_target_subdir"
fi
