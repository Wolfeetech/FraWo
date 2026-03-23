#!/usr/bin/env bash
set -euo pipefail

OPEN_BROWSER="${OPEN_BROWSER:-1}"
WAIT_SECONDS="${WAIT_SECONDS:-180}"
POLL_SECONDS="${POLL_SECONDS:-5}"

log() {
  printf '[tailscale-join] %s\n' "$*"
}

status_json() {
  ssh root@toolbox "tailscale status --json"
}

refresh_login_json() {
  ssh root@toolbox "tailscale up --json --reset --hostname=toolbox --advertise-routes=192.168.2.0/24 --accept-dns=false --timeout=10s >/tmp/toolbox_tailscale_up.json 2>/tmp/toolbox_tailscale_up.err || true; tailscale status --json"
}

parse_json_field() {
  local field="$1"
  local json_input="$2"
  python3 -c '
import json
import sys

field = sys.argv[1]
data = json.loads(sys.stdin.read())
value = data.get(field, "")
if isinstance(value, list):
    print(",".join(str(v) for v in value))
elif value is None:
    print("")
else:
    print(value)
' "$field" <<<"${json_input}"
}

json="$(refresh_login_json)"
backend_state="$(parse_json_field BackendState "$json")"
auth_url="$(parse_json_field AuthURL "$json")"

log "backend_state=${backend_state}"
if [ -n "${auth_url}" ]; then
  log "auth_url=${auth_url}"
else
  log "auth_url=unavailable"
fi

if [ "${OPEN_BROWSER}" = "1" ] && [ -n "${auth_url}" ]; then
  if command -v xdg-open >/dev/null 2>&1; then
    log "opening_auth_url_in_browser=yes"
    xdg-open "${auth_url}" >/dev/null 2>&1 || log "browser_open_failed"
  else
    log "opening_auth_url_in_browser=no"
  fi
fi

if [ "${backend_state}" = "Running" ]; then
  log "already_joined=yes"
  exit 0
fi

deadline=$((SECONDS + WAIT_SECONDS))
while [ "${SECONDS}" -lt "${deadline}" ]; do
  sleep "${POLL_SECONDS}"
  json="$(status_json)"
  backend_state="$(parse_json_field BackendState "$json")"
  log "poll_backend_state=${backend_state}"
  if [ "${backend_state}" = "Running" ]; then
    tailscale_ips="$(python3 -c '
import json
import sys
data = json.loads(sys.stdin.read())
ips = data.get("TailscaleIPs") or []
print(",".join(ips))
' <<<"${json}")"
    dns_name="$(python3 -c '
import json
import sys
data = json.loads(sys.stdin.read())
self_node = data.get("Self") or {}
print(self_node.get("DNSName", ""))
' <<<"${json}")"
    log "join_complete=yes"
    log "tailscale_ips=${tailscale_ips}"
    log "dns_name=${dns_name}"
    exit 0
  fi
done

log "join_complete=no"
log "next_step=finish_tailnet_login_and_route_approval_manually"
exit 2
