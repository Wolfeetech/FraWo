#!/usr/bin/env bash
set -euo pipefail

PROXMOX_HOST="proxmox"
HAOS_VMID="210"
HAOS_CONFIG_DIR="/mnt/data/supervisor/homeassistant"
HAOS_MAIN_CONFIG="${HAOS_CONFIG_DIR}/configuration.yaml"
HAOS_HTTP_CONFIG="${HAOS_CONFIG_DIR}/http.yaml"
TRUSTED_PROXY_IP="192.168.2.20"

log() {
  printf '[haos-reverse-proxy] %s\n' "$*"
}

remote_guest_exec() {
  local command="$1"
  ssh "${PROXMOX_HOST}" "qm guest exec ${HAOS_VMID} -- /bin/sh -lc ${command@Q}"
}

log "Ensuring HAOS VM ${HAOS_VMID} exists"
ssh "${PROXMOX_HOST}" "qm status ${HAOS_VMID} >/dev/null"

log "Writing managed Home Assistant proxy configuration"
remote_guest_exec "
set -e
mkdir -p '${HAOS_CONFIG_DIR}'
touch '${HAOS_MAIN_CONFIG}'
if ! grep -qx 'http: !include http.yaml' '${HAOS_MAIN_CONFIG}'; then
  printf '\nhttp: !include http.yaml\n' >> '${HAOS_MAIN_CONFIG}'
fi
cat > '${HAOS_HTTP_CONFIG}' <<'EOF'
use_x_forwarded_for: true
trusted_proxies:
  - ${TRUSTED_PROXY_IP}
EOF
"

log "Checking Home Assistant core configuration"
remote_guest_exec "/usr/bin/ha core check --no-progress"

log "Restarting Home Assistant core"
remote_guest_exec "/usr/bin/ha core restart --no-progress"

log "Managed reverse proxy settings applied"
