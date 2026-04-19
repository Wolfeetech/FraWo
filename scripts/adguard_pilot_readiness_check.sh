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

ADGUARD_SERVICE_IP="10.1.0.20"
ADGUARD_RESOLVER_IP="$(toolbox_frontdoor_ip)"
ADGUARD_RESOLVER_IP="${ADGUARD_RESOLVER_IP:-100.82.26.53}"

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

bool_from_grep() {
  local needle="$1"
  local file="$2"
  if grep -Fqx "${needle}" "${file}"; then
    echo "yes"
  else
    echo "no"
  fi
}

extract_short_answer() {
  local domain="$1"
  dns_query_short "${ADGUARD_RESOLVER_IP}" "${domain}"
}

adguard_port53_ready="no"
if timeout 3 bash -lc "exec 3<>/dev/tcp/${ADGUARD_RESOLVER_IP}/53" 2>/dev/null; then
  adguard_port53_ready="yes"
fi

adguard_admin_lan_http="$(curl -fsS -o /dev/null -w '%{http_code}' --max-time 5 "http://${ADGUARD_RESOLVER_IP}:3000" 2>/dev/null || true)"
if [[ "${adguard_admin_lan_http}" == "000" || -z "${adguard_admin_lan_http}" ]]; then
  adguard_admin_lan_surface="no"
else
  adguard_admin_lan_surface="yes"
fi

rewrite_portal_answer="$(extract_short_answer portal.hs27.internal)"
rewrite_ha_answer="$(extract_short_answer ha.hs27.internal)"
rewrite_cloud_answer="$(extract_short_answer cloud.hs27.internal)"

if [[ "${rewrite_portal_answer}" == "${ADGUARD_SERVICE_IP}" ]]; then
  adguard_rewrite_portal="yes"
else
  adguard_rewrite_portal="no"
fi

if [[ "${rewrite_ha_answer}" == "${ADGUARD_SERVICE_IP}" ]]; then
  adguard_rewrite_ha="yes"
else
  adguard_rewrite_ha="no"
fi

if [[ "${rewrite_cloud_answer}" == "${ADGUARD_SERVICE_IP}" ]]; then
  adguard_rewrite_cloud="yes"
else
  adguard_rewrite_cloud="no"
fi

allowed_lan_clients="$(bool_from_grep '  - "10.1.0.0/24"' "${ROOT_DIR}/ansible/inventory/host_vars/toolbox.yml")"
allowed_tailscale_clients="$(bool_from_grep '  - "100.64.0.0/10"' "${ROOT_DIR}/ansible/inventory/host_vars/toolbox.yml")"

pilot_client_primary="wolf-ZenBook-UX325EA-UX325EA"
pilot_client_secondary="Wolf_Pixel_after_mobile_validation"

adguard_pilot_ready="no"
if [[ \
  "${adguard_port53_ready}" == "yes" && \
  "${adguard_admin_lan_surface}" == "no" && \
  "${adguard_rewrite_portal}" == "yes" && \
  "${adguard_rewrite_ha}" == "yes" && \
  "${allowed_lan_clients}" == "yes" && \
  "${allowed_tailscale_clients}" == "yes" \
 ]]; then
  adguard_pilot_ready="yes"
fi

echo "adguard_resolver_ip=${ADGUARD_RESOLVER_IP}"
echo "adguard_service_ip=${ADGUARD_SERVICE_IP}"
echo "adguard_port53_ready=${adguard_port53_ready}"
echo "adguard_admin_lan_surface=${adguard_admin_lan_surface}"
echo "adguard_rewrite_portal=${adguard_rewrite_portal}"
echo "adguard_rewrite_portal_answer=${rewrite_portal_answer:-missing}"
echo "adguard_rewrite_ha=${adguard_rewrite_ha}"
echo "adguard_rewrite_ha_answer=${rewrite_ha_answer:-missing}"
echo "adguard_rewrite_cloud=${adguard_rewrite_cloud}"
echo "adguard_rewrite_cloud_answer=${rewrite_cloud_answer:-missing}"
echo "adguard_allowed_lan_clients=${allowed_lan_clients}"
echo "adguard_allowed_tailscale_clients=${allowed_tailscale_clients}"
echo "pilot_client_primary=${pilot_client_primary}"
echo "pilot_client_secondary=${pilot_client_secondary}"
echo "adguard_pilot_ready=${adguard_pilot_ready}"

if [[ "${adguard_pilot_ready}" == "yes" ]]; then
  echo "recommendation=pilot_direct_queries_are_safe_then_only_move_zenbook_to_client_level_dns"
else
  echo "recommendation=stabilize_adguard_bindings_rewrites_or_client_policy_before_dns_pilot"
fi
