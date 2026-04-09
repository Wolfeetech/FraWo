#!/usr/bin/env bash
set -euo pipefail

CT_ID="100"
SNAPSHOT_NAME="codex-pre-toolbox-ts-20260318"
SNAPSHOT_DESC="Before exposing /dev/net/tun to toolbox and rebooting for Tailscale prep"

log() {
  printf '[toolbox-tun] %s\n' "$*"
}

remote() {
  ssh proxmox "$@"
}

log "Creating safety snapshot ${SNAPSHOT_NAME}"
remote "pct listsnapshot ${CT_ID} | awk '{print \$1}' | grep -Fx '${SNAPSHOT_NAME}' >/dev/null || pct snapshot ${CT_ID} ${SNAPSHOT_NAME} -description '${SNAPSHOT_DESC}'"

log "Checking existing dev passthrough config"
if remote "pct config ${CT_ID} | grep -Eq '^dev0: /dev/net/tun(,|$)'"; then
  log "/dev/net/tun passthrough already present"
else
  log "Enabling /dev/net/tun passthrough"
  remote "pct set ${CT_ID} --dev0 /dev/net/tun,uid=0,gid=0,mode=0666"
fi

log "Rebooting toolbox container to apply device mapping"
remote "pct reboot ${CT_ID}"

log "Waiting for toolbox container to come back"
for _ in $(seq 1 15); do
  if remote "pct exec ${CT_ID} -- true" >/dev/null 2>&1; then
    break
  fi
  sleep 2
done

log "Verifying /dev/net/tun inside toolbox"
remote "pct exec ${CT_ID} -- bash -lc 'ls -l /dev/net/tun'"
