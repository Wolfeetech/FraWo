#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

extract_value() {
  local key="$1"
  local data="$2"
  printf '%s\n' "${data}" | awk -F= -v key="$key" '$1 == key {print $2; exit}'
}

tailscale_prefs_json="$(tailscale debug prefs 2>/dev/null || true)"
tailscale_status_json="$(tailscale status --json 2>/dev/null || true)"
toolbox_tailscale_output="$(timeout 15 "${ROOT_DIR}/scripts/toolbox_tailscale_check.sh" 2>/dev/null || true)"
adguard_pilot_output="$(timeout 10 "${ROOT_DIR}/scripts/adguard_pilot_readiness_check.sh" 2>/dev/null || true)"

if printf '%s\n' "${tailscale_prefs_json}" | grep -Fq '"CorpDNS": true'; then
  zenbook_accepts_tailscale_dns="yes"
else
  zenbook_accepts_tailscale_dns="no"
fi

if printf '%s\n' "${tailscale_status_json}" | grep -Fq '"MagicDNSEnabled": true'; then
  magicdns_enabled="yes"
else
  magicdns_enabled="no"
fi

magicdns_toolbox_answer="$(dig +time=2 +tries=1 +short @100.100.100.100 toolbox.tail150400.ts.net 2>/dev/null | head -n1)"
if [[ "${magicdns_toolbox_answer}" == "100.99.206.128" ]]; then
  magicdns_toolbox_resolves="yes"
else
  magicdns_toolbox_resolves="no"
fi

magicdns_ha_answer="$(dig +time=2 +tries=1 +short @100.100.100.100 ha.hs27.internal 2>/dev/null | head -n1)"
if [[ "${magicdns_ha_answer}" == "192.168.2.20" ]]; then
  magicdns_split_ha_resolves="yes"
else
  magicdns_split_ha_resolves="no"
fi

adguard_hs27_answer="$(dig +time=2 +tries=1 +short @192.168.2.20 ha.hs27.internal 2>/dev/null | head -n1)"
if [[ "${adguard_hs27_answer}" == "192.168.2.20" ]]; then
  adguard_hs27_resolves="yes"
else
  adguard_hs27_resolves="no"
fi

tailnet_route_visible="$(extract_value tailnet_route_visible "${toolbox_tailscale_output}")"
adguard_pilot_ready="$(extract_value adguard_pilot_ready "${adguard_pilot_output}")"

split_dns_prereqs_ready="no"
if [[ \
  "${magicdns_enabled}" == "yes" && \
  "${zenbook_accepts_tailscale_dns}" == "yes" && \
  "${magicdns_toolbox_resolves}" == "yes" && \
  "${adguard_hs27_resolves}" == "yes" && \
  "${adguard_pilot_ready}" == "yes" && \
  "${tailnet_route_visible}" == "yes" \
 ]]; then
  split_dns_prereqs_ready="yes"
fi

echo "magicdns_enabled=${magicdns_enabled}"
echo "zenbook_accepts_tailscale_dns=${zenbook_accepts_tailscale_dns}"
echo "magicdns_toolbox_resolves=${magicdns_toolbox_resolves}"
echo "magicdns_toolbox_answer=${magicdns_toolbox_answer:-missing}"
echo "magicdns_split_ha_resolves=${magicdns_split_ha_resolves}"
echo "magicdns_split_ha_answer=${magicdns_ha_answer:-missing}"
echo "adguard_hs27_resolves=${adguard_hs27_resolves}"
echo "adguard_hs27_answer=${adguard_hs27_answer:-missing}"
echo "adguard_pilot_ready=${adguard_pilot_ready:-unknown}"
echo "tailnet_route_visible=${tailnet_route_visible:-unknown}"
echo "split_dns_prereqs_ready=${split_dns_prereqs_ready}"

if [[ "${split_dns_prereqs_ready}" == "yes" && "${magicdns_split_ha_resolves}" == "yes" ]]; then
  echo "recommendation=split_dns_active_validate_phone_clients_and_keep_restricted_nameserver"
elif [[ "${split_dns_prereqs_ready}" == "yes" ]]; then
  echo "recommendation=add_restricted_nameserver_192.168.2.20_for_hs27.internal_in_tailscale_admin"
else
  echo "recommendation=approve_subnet_route_then_apply_split_dns_for_hs27.internal"
fi
