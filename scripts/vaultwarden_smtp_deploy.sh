#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PROXMOX_REMOTE="${ROOT_DIR}/scripts/proxmox_remote_exec.sh"
RUNTIME_HELPER="${ROOT_DIR}/scripts/app_smtp_runtime_vars.py"

read_effective_var() {
  python3 "${RUNTIME_HELPER}" --get "$1"
}

b64() {
  printf '%s' "$1" | base64 | tr -d '\n'
}

SMTP_HOST="$(read_effective_var homeserver_mail_smtp_host)"
SMTP_PORT="$(read_effective_var homeserver_mail_smtp_port)"
SMTP_SECURE_RAW="$(read_effective_var homeserver_mail_smtp_secure)"
SMTP_FROM="$(read_effective_var homeserver_mail_sender_email)"
SMTP_FROM_NAME="$(read_effective_var homeserver_mail_sender_name)"
SMTP_USER="$(read_effective_var homeserver_mail_smtp_auth_username)"
SMTP_PASSWORD="${HOMESERVER_MAIL_SMTP_PASSWORD:-}"

VAULTWARDEN_DOMAIN="${HOMESERVER_VAULTWARDEN_DOMAIN:-https://vault.hs27.internal}"
VAULTWARDEN_VMID="${HOMESERVER_VAULTWARDEN_VMID:-120}"

if [[ -z "${SMTP_HOST}" || -z "${SMTP_PORT}" || -z "${SMTP_FROM}" || -z "${SMTP_USER}" || -z "${SMTP_PASSWORD}" ]]; then
  echo "vaultwarden_smtp_ready=no" >&2
  echo "recommendation=export_HOMESERVER_MAIL_SMTP_PASSWORD_and_complete_mail_runtime" >&2
  exit 1
fi

case "${SMTP_SECURE_RAW,,}" in
  tls|starttls)
    SMTP_SECURITY="starttls"
    ;;
  ssl|ssl_tls|force_tls|smtps)
    SMTP_SECURITY="force_tls"
    ;;
  off|none|plain)
    SMTP_SECURITY="off"
    ;;
  *)
    echo "Unsupported Vaultwarden SMTP security mapping from homeserver_mail_smtp_secure=${SMTP_SECURE_RAW}" >&2
    exit 2
    ;;
esac

REMOTE_COMMAND="$(cat <<EOF
set -euo pipefail
export VW_DOMAIN_B64='$(b64 "${VAULTWARDEN_DOMAIN}")'
export VW_SMTP_HOST_B64='$(b64 "${SMTP_HOST}")'
export VW_SMTP_PORT_B64='$(b64 "${SMTP_PORT}")'
export VW_SMTP_SECURITY_B64='$(b64 "${SMTP_SECURITY}")'
export VW_SMTP_FROM_B64='$(b64 "${SMTP_FROM}")'
export VW_SMTP_FROM_NAME_B64='$(b64 "${SMTP_FROM_NAME}")'
export VW_SMTP_USERNAME_B64='$(b64 "${SMTP_USER}")'
export VW_SMTP_PASSWORD_B64='$(b64 "${SMTP_PASSWORD}")'
export VW_SIGNUPS_ALLOWED_B64='$(b64 "false")'
export VW_INVITATIONS_ALLOWED_B64='$(b64 "true")'
export VW_UPDATE_SCRIPT_B64='$(cat <<PYCODE | base64 | tr -d "\n"
import base64
import os
import pathlib
import shutil
import time

path = pathlib.Path("/opt/homeserver2027/stacks/vaultwarden/.env")
backup = path.with_name(f"{path.name}.bak.{int(time.time())}")

updates = {
    "DOMAIN": base64.b64decode(os.environ["VW_DOMAIN_B64"]).decode(),
    "SIGNUPS_ALLOWED": base64.b64decode(os.environ["VW_SIGNUPS_ALLOWED_B64"]).decode(),
    "INVITATIONS_ALLOWED": base64.b64decode(os.environ["VW_INVITATIONS_ALLOWED_B64"]).decode(),
    "SMTP_HOST": base64.b64decode(os.environ["VW_SMTP_HOST_B64"]).decode(),
    "SMTP_PORT": base64.b64decode(os.environ["VW_SMTP_PORT_B64"]).decode(),
    "SMTP_SECURITY": base64.b64decode(os.environ["VW_SMTP_SECURITY_B64"]).decode(),
    "SMTP_FROM": base64.b64decode(os.environ["VW_SMTP_FROM_B64"]).decode(),
    "SMTP_FROM_NAME": base64.b64decode(os.environ["VW_SMTP_FROM_NAME_B64"]).decode(),
    "SMTP_USERNAME": base64.b64decode(os.environ["VW_SMTP_USERNAME_B64"]).decode(),
    "SMTP_PASSWORD": base64.b64decode(os.environ["VW_SMTP_PASSWORD_B64"]).decode(),
}

original_lines = path.read_text(encoding="utf-8").splitlines()
shutil.copy2(path, backup)

result = []
seen = set()
for raw in original_lines:
    stripped = raw.strip()
    if not stripped or stripped.startswith("#") or "=" not in raw:
        result.append(raw)
        continue
    key, _value = raw.split("=", 1)
    if key in updates:
        if key not in seen:
            result.append(f"{key}={updates[key]}")
            seen.add(key)
        continue
    result.append(raw)
    seen.add(key)

for key, value in updates.items():
    if key not in seen:
        result.append(f"{key}={value}")

path.write_text("\\n".join(result).rstrip() + "\\n", encoding="utf-8")
print(f"vaultwarden_env_backup={backup}")
for key in ("DOMAIN", "SIGNUPS_ALLOWED", "INVITATIONS_ALLOWED", "SMTP_HOST", "SMTP_PORT", "SMTP_SECURITY", "SMTP_FROM", "SMTP_FROM_NAME", "SMTP_USERNAME"):
    print(f"{key}={updates[key]}")
print("SMTP_PASSWORD=<redacted>")
PYCODE
)'

pct exec ${VAULTWARDEN_VMID} -- sh -lc 'echo "\$VW_UPDATE_SCRIPT_B64" | base64 -d >/tmp/vaultwarden_env_update.py && python3 /tmp/vaultwarden_env_update.py && rm -f /tmp/vaultwarden_env_update.py'

pct exec ${VAULTWARDEN_VMID} -- sh -lc 'cd /opt/homeserver2027/stacks/vaultwarden && if docker compose version >/dev/null 2>&1; then docker compose up -d; else docker-compose up -d; fi'

pct exec ${VAULTWARDEN_VMID} -- sh -lc 'sleep 2; for i in \$(seq 1 60); do status=\$(docker inspect --format "{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}" vaultwarden 2>/dev/null || true); echo vaultwarden_health=\${status}; if [ "\${status}" = "healthy" ] || [ "\${status}" = "running" ]; then exit 0; fi; sleep 2; done; exit 1'
EOF
)"

"${PROXMOX_REMOTE}" "${REMOTE_COMMAND}"
