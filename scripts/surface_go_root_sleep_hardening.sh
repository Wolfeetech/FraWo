#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REMOTE_SCRIPT="${ROOT_DIR}/scripts/surface_go_root_sleep_hardening_remote.sh"
SURFACE_HOSTNAME="surface-go-frontend"
DEFAULT_TAILSCALE_IP="100.106.67.127"
SURFACE_USER="frawo"

resolve_surface_host() {
  if command -v tailscale >/dev/null 2>&1; then
    local tail_ip
    tail_ip="$(tailscale status 2>/dev/null | awk -v host="${SURFACE_HOSTNAME}" '$2 == host {print $1; exit}')"
    if [[ -n "${tail_ip}" ]]; then
      printf '%s\n' "${tail_ip}"
      return
    fi
  fi
  printf '%s\n' "${DEFAULT_TAILSCALE_IP}"
}

TARGET_HOST="${1:-$(resolve_surface_host)}"

echo "[surface-root-sleep] Target host=${TARGET_HOST}"
echo "[surface-root-sleep] This will prompt once for the Surface sudo password."

ssh -t "${SURFACE_USER}@${TARGET_HOST}" 'bash -s' < "${REMOTE_SCRIPT}"
