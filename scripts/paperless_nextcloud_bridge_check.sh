#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

remote_cmd='
set -euo pipefail
systemctl is-active --quiet homeserver2027-paperless-nextcloud-bridge.timer
echo bridge_timer_active=yes
systemctl is-enabled homeserver2027-paperless-nextcloud-bridge.timer >/dev/null 2>&1 && echo bridge_timer_enabled=yes
test -f /root/.config/rclone/rclone.conf && echo rclone_config_present=yes
test -d /var/lib/docker/volumes/paperless_consume/_data && echo consume_dir_present=yes
test -d /var/lib/docker/volumes/paperless_media/_data/documents/archive && echo archive_dir_present=yes
rclone --config /root/.config/rclone/rclone.conf lsd nextcloud_frontend:Paperless | sed "s/^/remote_dir /"
'

ssh -o BatchMode=yes wolf@10.1.0.23 "sudo -n bash -lc ${remote_cmd@Q}"
