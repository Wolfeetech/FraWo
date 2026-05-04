#!/usr/bin/env bash
set -euo pipefail

MAIL_ENV="/root/.config/homeserver2027/mail_alias_router.env"
ODOO_ENV="/root/.config/homeserver2027/odoo_agent_rpc.env"
TOOL="/opt/homeserver2027/tools/odoo_agent_intake_bridge.py"

for env_file in "${MAIL_ENV}" "${ODOO_ENV}"; do
  if [[ ! -f "${env_file}" ]]; then
    echo "missing env file: ${env_file}" >&2
    exit 1
  fi
  # shellcheck disable=SC1090
  source "${env_file}"
done

python3 "${TOOL}" \
  --imap-user "${HS27_IMAP_USER:?HS27_IMAP_USER fehlt}" \
  --unseen-only \
  --tag "${HS27_AGENT_INTAKE_TAG:-Lane A: MVP}" \
  --apply
