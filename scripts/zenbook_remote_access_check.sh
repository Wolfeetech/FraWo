#!/usr/bin/env bash
set -euo pipefail

x_session="${XDG_SESSION_TYPE:-unknown}"
echo "x_session=${x_session}"

tailscale_service="$(systemctl is-active tailscaled 2>/dev/null || echo inactive)"
echo "tailscaled_service=${tailscale_service}"

if tailscale status --json >/tmp/homeserver2027_tailscale_status.json 2>/dev/null; then
  echo "tailscale_joined=yes"
  jq -r '"tailscale_dns_name=\(.Self.DNSName)\ntailscale_ipv4=\(.Self.TailscaleIPs[] | select(test("^[0-9.]+$")))"' /tmp/homeserver2027_tailscale_status.json
else
  echo "tailscale_joined=no"
fi

if dpkg -s anydesk >/dev/null 2>&1; then
  echo "anydesk_installed=yes"
  anydesk_service="$(systemctl is-active anydesk 2>/dev/null || echo inactive)"
  echo "anydesk_service=${anydesk_service}"
  printf 'anydesk_id='
  anydesk --get-id 2>/dev/null || true
  printf '\n'
else
  echo "anydesk_installed=no"
fi

if curl -I --max-time 10 http://100.99.206.128:8447 >/tmp/homeserver2027_portal_headers.txt 2>/dev/null; then
  portal_http="$(awk 'NR==1{print $2}' /tmp/homeserver2027_portal_headers.txt)"
  echo "toolbox_portal_over_tailscale_http=${portal_http}"
else
  echo "toolbox_portal_over_tailscale_http=unreachable"
fi

if curl -I --max-time 10 http://100.99.206.128:8448 >/tmp/homeserver2027_radio_headers.txt 2>/dev/null; then
  radio_http="$(awk 'NR==1{print $2}' /tmp/homeserver2027_radio_headers.txt)"
  echo "toolbox_radio_over_tailscale_http=${radio_http}"
else
  echo "toolbox_radio_over_tailscale_http=unreachable"
fi
