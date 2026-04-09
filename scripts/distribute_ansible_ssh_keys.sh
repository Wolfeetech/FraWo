#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "${ROOT_DIR}/scripts/inventory_remote.sh"

DEFAULT_WINDOWS_KEY="/mnt/c/Users/StudioPC/.ssh/id_ed25519_frawo_new"
KEY_SOURCE="${HOMESERVER_ANSIBLE_IDENTITY_SOURCE:-${DEFAULT_WINDOWS_KEY}}"
KEY_CACHE="${HOMESERVER_ANSIBLE_IDENTITY_CACHE_FILE:-${HOME}/.ssh/homeserver2027_ansible_ed25519}"
KEY_CACHE_PUB="${KEY_CACHE}.pub"

log() {
  printf '[ansible-key-distribute] %s\n' "$*"
}

stage_keypair() {
  local private_source="$1"
  local public_source="${private_source}.pub"

  if [[ ! -r "${private_source}" ]]; then
    echo "ansible_key_distribute_error=missing_private_key:${private_source}" >&2
    return 1
  fi

  if [[ ! -r "${public_source}" ]]; then
    echo "ansible_key_distribute_error=missing_public_key:${public_source}" >&2
    return 1
  fi

  install -d -m 700 "$(dirname "${KEY_CACHE}")"
  install -m 600 "${private_source}" "${KEY_CACHE}"
  install -m 644 "${public_source}" "${KEY_CACHE_PUB}"
}

render_root_remote_command() {
  local pub_b64="$1"
  cat <<EOF
pct exec 100 -- bash -lc 'pub=\$(printf %s ${pub_b64@Q} | base64 -d); install -d -m 700 /root/.ssh; touch /root/.ssh/authorized_keys; chmod 600 /root/.ssh/authorized_keys; grep -qxF "\$pub" /root/.ssh/authorized_keys || echo "\$pub" >> /root/.ssh/authorized_keys; tail -n 1 /root/.ssh/authorized_keys'
EOF
}

render_wolf_remote_command() {
  local vmid="$1"
  local pub_b64="$2"
  cat <<EOF
qm guest exec ${vmid} -- bash -lc 'pub=\$(printf %s ${pub_b64@Q} | base64 -d); install -d -m 700 -o wolf -g wolf /home/wolf/.ssh; touch /home/wolf/.ssh/authorized_keys; chown wolf:wolf /home/wolf/.ssh/authorized_keys; chmod 600 /home/wolf/.ssh/authorized_keys; grep -qxF "\$pub" /home/wolf/.ssh/authorized_keys || echo "\$pub" >> /home/wolf/.ssh/authorized_keys; chown wolf:wolf /home/wolf/.ssh/authorized_keys; tail -n 1 /home/wolf/.ssh/authorized_keys'
EOF
}

main() {
  local pub_key
  local pub_b64

  log "staging keypair from ${KEY_SOURCE}"
  stage_keypair "${KEY_SOURCE}"

  pub_key="$(tr -d '\r\n' < "${KEY_CACHE_PUB}")"
  pub_b64="$(printf '%s' "${pub_key}" | base64 -w0)"

  log "installing key on toolbox root"
  run_proxmox_remote "$(render_root_remote_command "${pub_b64}")"

  for vmid in 200 220 230; do
    log "installing key on vm ${vmid} user wolf"
    run_proxmox_remote "$(render_wolf_remote_command "${vmid}" "${pub_b64}")"
  done

  echo "ansible_key_private=${KEY_CACHE}"
  echo "ansible_key_public=${KEY_CACHE_PUB}"
}

main "$@"
