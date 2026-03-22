#!/usr/bin/env bash
set -euo pipefail

service_state="$(ssh toolbox 'systemctl is-active homeserver2027-media-sync.service 2>/dev/null || true')"
timer_state="$(ssh toolbox 'systemctl is-active homeserver2027-media-sync.timer 2>/dev/null || true')"
timer_enabled="$(ssh toolbox 'systemctl is-enabled homeserver2027-media-sync.timer 2>/dev/null || true')"
target_file_count="$(ssh toolbox 'find /srv/media-library/music/bootstrap-radio-usb -type f 2>/dev/null | wc -l' 2>/dev/null || echo 0)"
target_size="$(ssh toolbox 'du -sh /srv/media-library/music/bootstrap-radio-usb 2>/dev/null | awk "{print \$1}"' 2>/dev/null || echo 0)"

echo "toolbox_media_sync_service_state=${service_state:-unknown}"
echo "toolbox_media_sync_timer_state=${timer_state:-unknown}"
echo "toolbox_media_sync_timer_enabled=${timer_enabled:-unknown}"
echo "toolbox_media_sync_target_file_count=${target_file_count:-0}"
echo "toolbox_media_sync_target_size=${target_size:-0}"

if [[ "${timer_state}" == "active" && "${timer_enabled}" == "enabled" ]]; then
  echo "toolbox_media_sync_ready=yes"
  echo "recommendation=allow_initial_or_periodic_radio_music_sync_to_populate_jellyfin_library"
else
  echo "toolbox_media_sync_ready=no"
  echo "recommendation=inspect_media_sync_service_timer_and_radio_access"
fi
