#!/usr/bin/env bash
set -euo pipefail

resolve_operator_home() {
  if [[ -n "${SUDO_USER:-}" && "${SUDO_USER}" != "root" ]]; then
    getent passwd "${SUDO_USER}" | cut -d: -f6
  elif [[ -n "${HOME:-}" ]]; then
    printf '%s\n' "${HOME}"
  else
    getent passwd "$(id -un)" | cut -d: -f6
  fi
}

OPERATOR_HOME="$(resolve_operator_home)"
SURFACE_DIR="${OPERATOR_HOME}/Downloads/Homeserver2027/install-media/surface"
SURFACE_ISO="${SURFACE_DIR}/ubuntu-24.04.4-desktop-amd64.iso"
SURFACE_SHA="3a4c9877b483ab46d7c3fbe165a0db275e1ae3cfe56a5657e5a47c2f99a99d1e"
SURFACE_URL="https://releases.ubuntu.com/noble/ubuntu-24.04.4-desktop-amd64.iso"

mkdir -p "${SURFACE_DIR}"

echo "[fetch-surface-iso] Resuming Surface ISO download"
wget -c -O "${SURFACE_ISO}" "${SURFACE_URL}"

actual_sha="$(sha256sum "${SURFACE_ISO}" | awk '{print $1}')"
if [[ "${actual_sha}" != "${SURFACE_SHA}" ]]; then
  echo "[fetch-surface-iso] SHA256 mismatch" >&2
  echo "expected=${SURFACE_SHA}" >&2
  echo "actual=${actual_sha}" >&2
  exit 1
fi

echo "[fetch-surface-iso] sha256 ok"
echo "surface_iso=${SURFACE_ISO}"
