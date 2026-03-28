#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
EXTRA_VARS_FILE="$(mktemp)"

cleanup() {
  rm -f "${EXTRA_VARS_FILE}"
}

trap cleanup EXIT
umask 077

python3 "${ROOT_DIR}/scripts/app_smtp_runtime_vars.py" --validate-ready --write-extra-vars "${EXTRA_VARS_FILE}"

ANSIBLE_CONFIG="${ROOT_DIR}/ansible.cfg" \
ansible-playbook \
  --inventory "${ROOT_DIR}/ansible/inventory/hosts.yml" \
  "${ROOT_DIR}/ansible/playbooks/deploy_app_smtp_baseline.yml" \
  --extra-vars "@${EXTRA_VARS_FILE}" \
  "$@"
