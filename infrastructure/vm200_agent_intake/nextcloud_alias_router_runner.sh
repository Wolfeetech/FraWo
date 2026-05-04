#!/usr/bin/env bash
set -euo pipefail

MAIL_ENV="/root/.config/homeserver2027/mail_alias_router.env"
TOOL="/opt/homeserver2027/tools/nextcloud_imap_alias_router.py"

if [[ ! -f "${MAIL_ENV}" ]]; then
  echo "missing env file: ${MAIL_ENV}" >&2
  exit 1
fi

# shellcheck disable=SC1090
source "${MAIL_ENV}"

python3 "${TOOL}" \
  --imap-user "${HS27_IMAP_USER:?HS27_IMAP_USER fehlt}" \
  --unseen-only \
  --apply
