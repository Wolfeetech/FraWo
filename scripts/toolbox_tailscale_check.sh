#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "${ROOT_DIR}/scripts/inventory_remote.sh"
source "${ROOT_DIR}/scripts/toolbox_remote.sh"

log() {
  printf '[tailscale-check] %s\n' "$*"
}

log "Checking Proxmox passthrough for /dev/net/tun"
run_proxmox_remote "pct config 100 | grep -E '^dev0: /dev/net/tun(,|$)'"

log "Checking toolbox runtime prerequisites"
run_toolbox_remote "ls -l /dev/net/tun"
run_toolbox_remote "systemctl is-enabled tailscaled"
run_toolbox_remote "systemctl is-active tailscaled"
run_toolbox_remote "sysctl net.ipv4.ip_forward net.ipv6.conf.all.forwarding"

log "Reading Tailscale backend state"
run_toolbox_remote "tailscale status --json 2>/dev/null | python3 -c 'import json,sys; data=json.load(sys.stdin); print(\"backend_state=\" + data.get(\"BackendState\", \"unknown\")); print(\"dns_name=\" + data.get(\"Self\", {}).get(\"DNSName\", \"unknown\").rstrip(\".\")); raw=json.dumps(data); print(\"tailnet_route_visible=\" + (\"yes\" if \"192.168.2.0/24\" in raw else \"no\"))' || echo backend_state=unavailable"
run_toolbox_remote "tailscale debug prefs 2>/dev/null | python3 -c 'import json,sys; data=json.load(sys.stdin); routes=data.get(\"AdvertiseRoutes\", []); print(\"route_advertised_local=\" + (\"yes\" if \"192.168.2.0/24\" in routes else \"no\"))' || echo route_advertised_local=unknown"
