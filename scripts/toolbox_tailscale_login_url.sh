#!/usr/bin/env bash
set -euo pipefail

ssh root@toolbox "tailscale up --json --reset --hostname=toolbox --advertise-routes=192.168.2.0/24 --accept-dns=false --timeout=10s >/tmp/toolbox_tailscale_up.json 2>/tmp/toolbox_tailscale_up.err || true; tailscale status --json" \
  | python3 -c 'import json,sys; data=json.load(sys.stdin); print("backend_state=" + data.get("BackendState", "unknown")); print("auth_url=" + data.get("AuthURL", ""))'
