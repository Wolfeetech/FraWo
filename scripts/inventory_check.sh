#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
INVENTORY_PATH="${HOMESERVER_INVENTORY_FILE:-${ROOT_DIR}/ansible/inventory/hosts.yml}"
OUTPUT_PATH="${HOMESERVER_INVENTORY_CHECK_OUTPUT:-/tmp/homeserver2027_inventory.json}"
ANSIBLE_CONFIG_PATH="${ROOT_DIR}/ansible.cfg"

mkdir -p "$(dirname "${OUTPUT_PATH}")"

if command -v ansible-inventory >/dev/null 2>&1; then
  ANSIBLE_CONFIG="${ANSIBLE_CONFIG_PATH}" ansible-inventory --inventory "${INVENTORY_PATH}" --list > "${OUTPUT_PATH}"
  echo "inventory_check_mode=ansible-inventory"
  echo "inventory_check_output=${OUTPUT_PATH}"
  exit 0
fi

python3 - <<'PY' "${INVENTORY_PATH}" "${OUTPUT_PATH}"
import json
import sys
from pathlib import Path

import yaml

inventory_path = Path(sys.argv[1])
output_path = Path(sys.argv[2])

with inventory_path.open("r", encoding="utf-8") as handle:
    data = yaml.safe_load(handle)

output_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
print("inventory_check_mode=python-yaml-fallback")
print(f"inventory_check_output={output_path}")
PY
