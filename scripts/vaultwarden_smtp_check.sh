#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PROXMOX_REMOTE="${ROOT_DIR}/scripts/proxmox_remote_exec.sh"
RUNTIME_HELPER="${ROOT_DIR}/scripts/app_smtp_runtime_vars.py"

read_effective_var() {
  python3 "${RUNTIME_HELPER}" --get "$1"
}

SMTP_HOST="$(read_effective_var homeserver_mail_smtp_host)"
SMTP_PORT="$(read_effective_var homeserver_mail_smtp_port)"
SMTP_FROM="$(read_effective_var homeserver_mail_sender_email)"
SMTP_USER="$(read_effective_var homeserver_mail_smtp_auth_username)"
SMTP_SECURE_RAW="$(read_effective_var homeserver_mail_smtp_secure)"
EXPECTED_DOMAIN="${HOMESERVER_VAULTWARDEN_DOMAIN:-https://vault.hs27.internal}"
VAULTWARDEN_VMID="${HOMESERVER_VAULTWARDEN_VMID:-120}"

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
    SMTP_SECURITY=""
    ;;
esac

REMOTE_COMMAND="$(cat <<EOF
set -euo pipefail
export VW_CHECK_SCRIPT_B64='$(cat <<PYCODE | base64 | tr -d "\n"
from pathlib import Path

env = {}
for raw in Path("/opt/homeserver2027/stacks/vaultwarden/.env").read_text(encoding="utf-8").splitlines():
    stripped = raw.strip()
    if not stripped or stripped.startswith("#") or "=" not in raw:
        continue
    key, value = raw.split("=", 1)
    env[key] = value

checks = {
    "vaultwarden_domain_ready": env.get("DOMAIN", "") == "${EXPECTED_DOMAIN}",
    "vaultwarden_signups_disabled": env.get("SIGNUPS_ALLOWED", "") == "false",
    "vaultwarden_invitations_enabled": env.get("INVITATIONS_ALLOWED", "") == "true",
    "vaultwarden_smtp_host_ready": env.get("SMTP_HOST", "") == "${SMTP_HOST}",
    "vaultwarden_smtp_port_ready": env.get("SMTP_PORT", "") == "${SMTP_PORT}",
    "vaultwarden_smtp_security_ready": env.get("SMTP_SECURITY", "") == "${SMTP_SECURITY}",
    "vaultwarden_smtp_from_ready": env.get("SMTP_FROM", "") == "${SMTP_FROM}",
    "vaultwarden_smtp_user_ready": env.get("SMTP_USERNAME", "") == "${SMTP_USER}",
    "vaultwarden_smtp_password_present": bool(env.get("SMTP_PASSWORD", "").strip()),
}

for key, value in checks.items():
    print(f"{key}={'yes' if value else 'no'}")
PYCODE
)'

pct exec ${VAULTWARDEN_VMID} -- sh -lc 'echo "\$VW_CHECK_SCRIPT_B64" | base64 -d >/tmp/vaultwarden_env_check.py && python3 /tmp/vaultwarden_env_check.py && rm -f /tmp/vaultwarden_env_check.py'

pct exec ${VAULTWARDEN_VMID} -- sh -lc 'printf "vaultwarden_alive_response="; wget -qO- http://127.0.0.1:8080/alive; echo'
EOF
)"

OUTPUT="$("${PROXMOX_REMOTE}" "${REMOTE_COMMAND}")"
printf '%s\n' "${OUTPUT}"

if ! grep -q '^vaultwarden_domain_ready=yes$' <<<"${OUTPUT}"; then
  exit 1
fi
if ! grep -q '^vaultwarden_signups_disabled=yes$' <<<"${OUTPUT}"; then
  exit 1
fi
if ! grep -q '^vaultwarden_invitations_enabled=yes$' <<<"${OUTPUT}"; then
  exit 1
fi
if ! grep -q '^vaultwarden_smtp_host_ready=yes$' <<<"${OUTPUT}"; then
  exit 1
fi
if ! grep -q '^vaultwarden_smtp_port_ready=yes$' <<<"${OUTPUT}"; then
  exit 1
fi
if ! grep -q '^vaultwarden_smtp_security_ready=yes$' <<<"${OUTPUT}"; then
  exit 1
fi
if ! grep -q '^vaultwarden_smtp_from_ready=yes$' <<<"${OUTPUT}"; then
  exit 1
fi
if ! grep -q '^vaultwarden_smtp_user_ready=yes$' <<<"${OUTPUT}"; then
  exit 1
fi
if ! grep -q '^vaultwarden_smtp_password_present=yes$' <<<"${OUTPUT}"; then
  exit 1
fi
if ! grep -q '^vaultwarden_alive_response=' <<<"${OUTPUT}"; then
  exit 1
fi
