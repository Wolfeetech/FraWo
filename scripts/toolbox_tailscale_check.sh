#!/usr/bin/env bash
set -euo pipefail

log() {
  printf '[tailscale-check] %s\n' "$*"
}

log "Checking Proxmox passthrough for /dev/net/tun"
ssh proxmox "pct config 100 | grep -E '^dev0: /dev/net/tun(,|$)'"

log "Checking toolbox runtime prerequisites"
ssh root@toolbox "ls -l /dev/net/tun"
ssh root@toolbox "systemctl is-enabled tailscaled"
ssh root@toolbox "systemctl is-active tailscaled"
ssh root@toolbox "sysctl net.ipv4.ip_forward net.ipv6.conf.all.forwarding"

log "Reading Tailscale backend state"
ssh root@toolbox "tailscale status --json 2>/dev/null | python3 -c 'import json,sys; data=json.load(sys.stdin); print(\"backend_state=\" + data.get(\"BackendState\", \"unknown\")); print(\"dns_name=\" + data.get(\"Self\", {}).get(\"DNSName\", \"unknown\").rstrip(\".\")); raw=json.dumps(data); print(\"tailnet_route_visible=\" + (\"yes\" if \"192.168.2.0/24\" in raw else \"no\"))' || echo backend_state=unavailable"
ssh root@toolbox "tailscale debug prefs 2>/dev/null | python3 -c 'import json,sys; data=json.load(sys.stdin); routes=data.get(\"AdvertiseRoutes\", []); print(\"route_advertised_local=\" + (\"yes\" if \"192.168.2.0/24\" in routes else \"no\"))' || echo route_advertised_local=unknown"
