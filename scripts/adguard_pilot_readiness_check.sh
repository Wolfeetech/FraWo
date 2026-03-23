#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ADGUARD_IP="192.168.2.20"

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
  dig +time=2 +tries=1 +short "@${ADGUARD_IP}" "${domain}" 2>/dev/null | head -n1
}

adguard_port53_ready="no"
if timeout 3 bash -lc "exec 3<>/dev/tcp/${ADGUARD_IP}/53" 2>/dev/null; then
  adguard_port53_ready="yes"
fi

adguard_admin_lan_http="$(curl -fsS -o /dev/null -w '%{http_code}' --max-time 5 "http://${ADGUARD_IP}:3000" 2>/dev/null || true)"
if [[ "${adguard_admin_lan_http}" == "000" || -z "${adguard_admin_lan_http}" ]]; then
  adguard_admin_lan_surface="no"
else
  adguard_admin_lan_surface="yes"
fi

rewrite_portal_answer="$(extract_short_answer portal.hs27.internal)"
rewrite_ha_answer="$(extract_short_answer ha.hs27.internal)"
rewrite_cloud_answer="$(extract_short_answer cloud.hs27.internal)"

if [[ "${rewrite_portal_answer}" == "${ADGUARD_IP}" ]]; then
  adguard_rewrite_portal="yes"
else
  adguard_rewrite_portal="no"
fi

if [[ "${rewrite_ha_answer}" == "${ADGUARD_IP}" ]]; then
  adguard_rewrite_ha="yes"
else
  adguard_rewrite_ha="no"
fi

if [[ "${rewrite_cloud_answer}" == "${ADGUARD_IP}" ]]; then
  adguard_rewrite_cloud="yes"
else
  adguard_rewrite_cloud="no"
fi

allowed_lan_clients="$(bool_from_grep '  - "192.168.2.0/24"' "${ROOT_DIR}/ansible/inventory/host_vars/toolbox.yml")"
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

echo "adguard_ip=${ADGUARD_IP}"
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
