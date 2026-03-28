#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "${ROOT_DIR}/scripts/toolbox_remote.sh"

extract_http_code() {
  local url="$1"
  curl -s -o /dev/null -w '%{http_code}' --max-time 10 "$url" || true
}

service_status="$(
  run_toolbox_remote '
    systemctl is-enabled homeserver-compose-toolbox-media.service 2>/dev/null || true
    systemctl is-active homeserver-compose-toolbox-media.service 2>/dev/null || true
    docker ps --format "{{.Names}}|{{.Status}}" 2>/dev/null | grep "^jellyfin|" || true
  ' 2>/dev/null || true
)"
library_dirs="$(run_toolbox_remote 'find /srv/media-library -maxdepth 1 -mindepth 1 -type d | sed "s#/srv/media-library/##" | sort | tr "\n" ","' 2>/dev/null || true)"
startup_wizard_completed="$(
  run_toolbox_remote 'python3 - <<'"'"'PY'"'"'
import json
import urllib.request

try:
    data = json.load(urllib.request.urlopen("http://127.0.0.1:8096/System/Info/Public", timeout=8))
    print(str(data.get("StartupWizardCompleted", False)).lower())
except Exception:
    print("unknown")
PY' 2>/dev/null || true
)"

internal_http="$(extract_http_code "http://media.hs27.internal")"
direct_http="$(extract_http_code "http://192.168.2.20:8096")"
mobile_http="$(extract_http_code "http://100.99.206.128:8449")"

echo "media_internal_http=${internal_http:-000}"
echo "media_direct_http=${direct_http:-000}"
echo "media_mobile_http=${mobile_http:-000}"
echo "media_startup_wizard_completed=${startup_wizard_completed:-unknown}"
printf '%s\n' "${service_status}"
echo "media_library_dirs=${library_dirs%,}"

if [[ "${internal_http:-000}" =~ ^(200|302)$ && "${direct_http:-000}" =~ ^(200|302)$ ]]; then
  echo "toolbox_media_server_ready=yes"
  if [[ "${startup_wizard_completed:-unknown}" == "true" ]]; then
    echo "recommendation=continue_media_sync_and_begin_client_rollout"
  else
    echo "recommendation=use_jellyfin_ui_to_create_admin_and_attach_movies_shows_music_libraries"
  fi
else
  echo "toolbox_media_server_ready=no"
  echo "recommendation=inspect_toolbox_media_stack_and_caddy_proxy"
fi
