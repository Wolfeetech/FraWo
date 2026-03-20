#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

extract_http_code() {
  local url="$1"
  curl -s -o /dev/null -w '%{http_code}' --max-time 10 "$url" || true
}

service_status="$(ssh toolbox 'systemctl is-enabled homeserver-compose-toolbox-media.service && systemctl is-active homeserver-compose-toolbox-media.service && docker ps --format "{{.Names}}|{{.Status}}" | rg "^jellyfin\\|" || true' 2>/dev/null || true)"
library_dirs="$(ssh toolbox 'find /srv/media-library -maxdepth 1 -mindepth 1 -type d | sed "s#/srv/media-library/##" | sort | tr "\n" ","' 2>/dev/null || true)"

internal_http="$(extract_http_code "http://media.hs27.internal")"
direct_http="$(extract_http_code "http://192.168.2.20:8096")"
mobile_http="$(extract_http_code "http://100.99.206.128:8449")"

echo "media_internal_http=${internal_http:-000}"
echo "media_direct_http=${direct_http:-000}"
echo "media_mobile_http=${mobile_http:-000}"
printf '%s\n' "${service_status}"
echo "media_library_dirs=${library_dirs%,}"

if [[ "${internal_http:-000}" =~ ^(200|302)$ && "${direct_http:-000}" =~ ^(200|302)$ ]]; then
  echo "toolbox_media_server_ready=yes"
  echo "recommendation=use_jellyfin_ui_to_create_admin_and_attach_movies_shows_music_libraries"
else
  echo "toolbox_media_server_ready=no"
  echo "recommendation=inspect_toolbox_media_stack_and_caddy_proxy"
fi
