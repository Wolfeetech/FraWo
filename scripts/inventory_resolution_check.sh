#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
INVENTORY_FILE="${ROOT_DIR}/NETWORK_INVENTORY.md"

unknown_review_count="$(awk '
  /^## Unknown Review Bucket/ {in_section=1; next}
  in_section && /^## / {exit}
  in_section && /^\| `192\.168\.2\./ {count++}
  END {print count+0}
' "${INVENTORY_FILE}")"

mapfile -t unresolved_labels < <(awk '
  /Remaining router-only labels still to map 1:1 onto active IPs:/ {capture=1; next}
  capture && /^  - / {exit}
  capture && /^    - / {
    val=$0
    sub(/^    - /, "", val)
    if (val != "none") print val
  }
' "${INVENTORY_FILE}")

if (( ${#unresolved_labels[@]} == 0 )); then
  unresolved_router_labels_csv="none"
else
  unresolved_router_labels_csv="$(IFS=,; printf '%s' "${unresolved_labels[*]}")"
fi

inventory_resolution_ready="no"
if [[ "${unknown_review_count}" == "0" ]]; then
  inventory_resolution_ready="yes"
fi

echo "inventory_unknown_review_count=${unknown_review_count}"
echo "unresolved_router_labels=${unresolved_router_labels_csv}"
echo "inventory_resolution_ready=${inventory_resolution_ready}"

if [[ "${inventory_resolution_ready}" == "yes" ]]; then
  echo "recommendation=inventory_is_clean_enough_for_gateway_prework"
elif [[ "${unresolved_router_labels_csv}" == "none" ]]; then
  echo "recommendation=resolve_remaining_owner_mapping_for_unknown_private_mac_clients"
else
  echo "recommendation=finish_manual_easybox_lease_mapping_before_gateway_cutover"
fi
