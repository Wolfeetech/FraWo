#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
INVENTORY_FILE="${ROOT_DIR}/NETWORK_INVENTORY.md"

awk '
  BEGIN {
    print "inventory_unknown_review_report=yes"
  }
  /^## Unknown Review Bucket/ {in_unknown=1; next}
  in_unknown && /^## / {in_unknown=0}
  in_unknown && /^\| `192\.168\.2\./ {
    line=$0
    gsub(/^|[[:space:]]+$/, "", line)
    split(line, parts, "|")
    ip=parts[2]; host=parts[3]; mac=parts[4]; next_action=parts[13]
    gsub(/^[[:space:]]+|[[:space:]]+$/, "", ip)
    gsub(/^[[:space:]]+|[[:space:]]+$/, "", host)
    gsub(/^[[:space:]]+|[[:space:]]+$/, "", mac)
    gsub(/^[[:space:]]+|[[:space:]]+$/, "", next_action)
    gsub(/`/, "", ip)
    gsub(/`/, "", host)
    gsub(/`/, "", mac)
    gsub(/`/, "", next_action)
    unknown_count++
    print "unknown_" unknown_count "_ip=" ip
    print "unknown_" unknown_count "_host=" host
    print "unknown_" unknown_count "_mac=" mac
    print "unknown_" unknown_count "_next_action=" next_action
  }
  /the authenticated overview also shows additional current router labels requiring clean classification:/ {capture_labels=1; next}
  capture_labels && /^  - / {capture_labels=0}
  capture_labels && /^    - / {
    label=$0
    sub(/^    - /, "", label)
    labels[++label_count]=label
  }
  END {
    print "inventory_unknown_review_count=" (unknown_count+0)
    if (label_count == 0) {
      print "inventory_alias_review_count=0"
      print "inventory_alias_review_labels=none"
    } else {
      csv=""
      for (i = 1; i <= label_count; i++) {
        csv = csv (i == 1 ? "" : ";") labels[i]
      }
      print "inventory_alias_review_count=" label_count
      print "inventory_alias_review_labels=" csv
    }
    if ((unknown_count+0) == 0) {
      print "recommendation=inventory_unknown_bucket_is_empty"
    } else {
      print "recommendation=resolve_remaining_owner_mapping_for_unknown_private_mac_clients"
    }
  }
' "${INVENTORY_FILE}"
