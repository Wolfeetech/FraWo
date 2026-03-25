#!/usr/bin/env bash
set -euo pipefail

TOKEN_USER="root@pam"
TOKEN_NAME="codex"

if ! command -v pveum >/dev/null 2>&1; then
  echo "pveum not found; run this on the Proxmox host" >&2
  exit 1
fi

echo "Creating Proxmox API token ${TOKEN_USER}!${TOKEN_NAME} ..." >&2
output=$(pveum user token add "$TOKEN_USER" "$TOKEN_NAME" --privsep 0 --expire 0)
printf '%s\n' "$output"
secret=$(printf '%s\n' "$output" | awk -F': ' '/value:/ {print $2; exit}')

if [[ -z "${secret:-}" ]]; then
  echo "Token secret not found in command output." >&2
  exit 1
fi

echo
printf 'Windows PowerShell:\n'
printf 'setx PROXMOX_API_TOKEN_ID "%s"\n' "$TOKEN_NAME"
printf 'setx PROXMOX_API_TOKEN_SECRET "%s"\n' "$secret"

echo
printf 'WSL current shell:\n'
printf 'export PROXMOX_API_TOKEN_ID=%q\n' "$TOKEN_NAME"
printf 'export PROXMOX_API_TOKEN_SECRET=%q\n' "$secret"