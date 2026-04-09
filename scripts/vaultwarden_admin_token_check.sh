#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PROXMOX_REMOTE="${ROOT_DIR}/scripts/proxmox_remote_exec.sh"
VAULTWARDEN_VMID="${HOMESERVER_VAULTWARDEN_VMID:-120}"

REMOTE_COMMAND="$(cat <<EOF
set -euo pipefail
export VW_ADMIN_CHECK_SCRIPT_B64='$(cat <<PYCODE | base64 | tr -d "\n"
from pathlib import Path

env = {}
for raw in Path("/opt/homeserver2027/stacks/vaultwarden/.env").read_text(encoding="utf-8").splitlines():
    stripped = raw.strip()
    if not stripped or stripped.startswith("#") or "=" not in raw:
        continue
    key, value = raw.split("=", 1)
    env[key] = value

token = env.get("ADMIN_TOKEN", "")
print(f"vaultwarden_admin_token_hashed={'yes' if token.startswith(chr(36) + 'argon2id' + chr(36)) else 'no'}")
PYCODE
)'

pct exec ${VAULTWARDEN_VMID} -- sh -lc 'echo "\$VW_ADMIN_CHECK_SCRIPT_B64" | base64 -d >/tmp/vaultwarden_admin_check.py && python3 /tmp/vaultwarden_admin_check.py && rm -f /tmp/vaultwarden_admin_check.py'

pct exec ${VAULTWARDEN_VMID} -- sh -lc 'docker logs --tail 80 vaultwarden 2>&1 | if grep -Fq "plain text \`ADMIN_TOKEN\`"; then echo vaultwarden_admin_token_plaintext_warning=yes; else echo vaultwarden_admin_token_plaintext_warning=no; fi'
EOF
)"

OUTPUT="$("${PROXMOX_REMOTE}" "${REMOTE_COMMAND}")"
printf '%s\n' "${OUTPUT}"

if ! grep -q '^vaultwarden_admin_token_hashed=yes$' <<<"${OUTPUT}"; then
  exit 1
fi
if ! grep -q '^vaultwarden_admin_token_plaintext_warning=no$' <<<"${OUTPUT}"; then
  exit 1
fi
