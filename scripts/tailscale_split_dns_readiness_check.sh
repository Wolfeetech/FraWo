#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

toolbox_frontdoor_ip() {
  awk '
    /^[[:space:]]*#/ {next}
    /^[[:space:]]*Host[[:space:]]+/ {
      in_toolbox=0
      for (i=2; i<=NF; i++) {
        if ($i == "toolbox") {
          in_toolbox=1
        }
      }
      next
    }
    in_toolbox && /^[[:space:]]*HostName[[:space:]]+/ {
      print $2
      exit
    }
  ' "${ROOT_DIR}/Codex/ssh_config"
}

TOOLBOX_FRONTDOOR_IP="$(toolbox_frontdoor_ip)"
TOOLBOX_FRONTDOOR_IP="${TOOLBOX_FRONTDOOR_IP:-100.82.26.53}"

tailscale_cmd() {
  if command -v tailscale >/dev/null 2>&1; then
    tailscale "$@"
    return
  fi

  if [[ -x "/mnt/c/Program Files/Tailscale/tailscale.exe" ]]; then
    "/mnt/c/Program Files/Tailscale/tailscale.exe" "$@"
    return
  fi

  return 127
}

dns_query_short() {
  local server="$1"
  local domain="$2"

  if command -v dig >/dev/null 2>&1; then
    dig +time=2 +tries=1 +short "@${server}" "${domain}" 2>/dev/null | head -n1
    return
  fi

  if command -v nslookup.exe >/dev/null 2>&1; then
    nslookup.exe "${domain}" "${server}" 2>/dev/null | tr -d '\r' | awk '
      /^Name:[[:space:]]+/ {seen_name=1; next}
      seen_name && /^Address:[[:space:]]+/ {print $2; exit}
    '
    return
  fi
}

tailnet_route_visible_local() {
  local route_output=""

  if command -v powershell.exe >/dev/null 2>&1; then
    route_output="$(powershell.exe -NoProfile -Command '$route = Find-NetRoute -RemoteIPAddress 10.1.0.20 -ErrorAction SilentlyContinue | Format-List InterfaceAlias,NextHop; $route' 2>/dev/null | tr -d '\r')"
  fi

  if printf '%s\n' "${route_output}" | grep -Fq 'InterfaceAlias : Tailscale' && \
     printf '%s\n' "${route_output}" | grep -Fq 'NextHop        : 100.100.100.100'; then
    echo "yes"
  else
    echo "no"
  fi
}

extract_value() {
  local key="$1"
  local data="$2"
  printf '%s\n' "${data}" | awk -F= -v key="$key" '$1 == key {print $2; exit}'
}

tailscale_prefs_json="$(tailscale_cmd debug prefs 2>/dev/null || true)"
tailscale_status_json="$(tailscale_cmd status --json 2>/dev/null || true)"
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

magicdns_toolbox_answer="$(dns_query_short 100.100.100.100 toolbox.tail150400.ts.net)"
if [[ "${magicdns_toolbox_answer}" == "${TOOLBOX_FRONTDOOR_IP}" ]]; then
  magicdns_toolbox_resolves="yes"
else
  magicdns_toolbox_resolves="no"
fi

magicdns_ha_answer="$(dns_query_short 100.100.100.100 ha.hs27.internal)"
if [[ "${magicdns_ha_answer}" == "10.1.0.20" ]]; then
  magicdns_split_ha_resolves="yes"
else
  magicdns_split_ha_resolves="no"
fi

adguard_hs27_answer="$(dns_query_short "${TOOLBOX_FRONTDOOR_IP}" ha.hs27.internal)"
if [[ "${adguard_hs27_answer}" == "10.1.0.20" ]]; then
  adguard_hs27_resolves="yes"
else
  adguard_hs27_resolves="no"
fi

tailnet_route_visible="$(tailnet_route_visible_local)"
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
echo "adguard_resolver_ip=${TOOLBOX_FRONTDOOR_IP}"
echo "adguard_hs27_resolves=${adguard_hs27_resolves}"
echo "adguard_hs27_answer=${adguard_hs27_answer:-missing}"
echo "adguard_pilot_ready=${adguard_pilot_ready:-unknown}"
echo "tailnet_route_visible=${tailnet_route_visible:-unknown}"
echo "split_dns_prereqs_ready=${split_dns_prereqs_ready}"

if [[ "${split_dns_prereqs_ready}" == "yes" && "${magicdns_split_ha_resolves}" == "yes" ]]; then
  echo "recommendation=split_dns_active_validate_phone_clients_and_keep_restricted_nameserver"
elif [[ "${split_dns_prereqs_ready}" == "yes" ]]; then
  echo "recommendation=add_restricted_nameserver_${TOOLBOX_FRONTDOOR_IP}_for_hs27.internal_in_tailscale_admin"
else
  echo "recommendation=approve_subnet_route_then_apply_split_dns_for_hs27.internal"
fi
