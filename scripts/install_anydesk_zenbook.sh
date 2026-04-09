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
BASE_DIR="${OPERATOR_HOME}/Downloads/Homeserver2027/install-media"
PKG="${BASE_DIR}/remote/anydesk_8.0.0_amd64.deb"
TMP_PKG=""

cleanup() {
  if [[ -n "${TMP_PKG}" && -f "${TMP_PKG}" ]]; then
    rm -f "${TMP_PKG}"
  fi
}

trap cleanup EXIT

if [[ "${EUID}" -ne 0 ]]; then
  echo "AKTION VON DIR ERFORDERLICH: dieses Script mit sudo ausfuehren." >&2
  echo "Beispiel: sudo $0" >&2
  exit 2
fi

if [[ ! -f "${PKG}" ]]; then
  echo "Missing AnyDesk package. Run ./scripts/fetch_install_media.sh first." >&2
  exit 1
fi

echo "[anydesk-install] Installing ${PKG}"
apt-get update
TMP_PKG="$(mktemp /tmp/anydesk_8.0.0_XXXXXX.deb)"
install -m 0644 "${PKG}" "${TMP_PKG}"
apt-get install -y "${TMP_PKG}"
systemctl enable --now anydesk.service

if [[ -n "${ANYDESK_PASSWORD:-}" ]]; then
  echo "[anydesk-install] Setting unattended-access password from ANYDESK_PASSWORD"
  echo "${ANYDESK_PASSWORD}" | anydesk --set-password
fi

echo "[anydesk-install] Completed"
anydesk --version || true
systemctl --no-pager --full status anydesk.service | sed -n '1,12p'
