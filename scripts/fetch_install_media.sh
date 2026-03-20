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
BASE_DIR="${1:-${OPERATOR_HOME}/Downloads/Homeserver2027/install-media}"
SURFACE_DIR="${BASE_DIR}/surface"
RPI_DIR="${BASE_DIR}/rpi"
TOOLS_DIR="${BASE_DIR}/tools"
REMOTE_DIR="${BASE_DIR}/remote"

SURFACE_ISO="ubuntu-24.04.4-desktop-amd64.iso"
SURFACE_SHA="3a4c9877b483ab46d7c3fbe165a0db275e1ae3cfe56a5657e5a47c2f99a99d1e"
SURFACE_URL="https://releases.ubuntu.com/noble/${SURFACE_ISO}"
SURFACE_SHA_URL="https://releases.ubuntu.com/noble/SHA256SUMS"

RPI_IMG="ubuntu-22.04.5-preinstalled-server-arm64+raspi.img.xz"
RPI_SHA="fd7687c5c9422a6c7ba4717c227bf6473fe4e0c954d5a9f664201dcecc63e822"
RPI_URL="https://cdimage.ubuntu.com/releases/22.04/release/${RPI_IMG}"
RPI_SHA_URL="https://cdimage.ubuntu.com/releases/22.04/release/SHA256SUMS"

VENTOY_VERSION="1.1.10"
VENTOY_TGZ="ventoy-${VENTOY_VERSION}-linux.tar.gz"
VENTOY_URL="https://github.com/ventoy/Ventoy/releases/download/v${VENTOY_VERSION}/${VENTOY_TGZ}"
VENTOY_SHA_URL="https://github.com/ventoy/Ventoy/releases/download/v${VENTOY_VERSION}/sha256.txt"

ANYDESK_DEB="anydesk_8.0.0_amd64.deb"
ANYDESK_URL="https://deb.anydesk.com/pool/main/a/anydesk/${ANYDESK_DEB}"

download() {
  local url="$1"
  local out="$2"
  local tmp="${out}.part"
  mkdir -p "$(dirname "${out}")"
  if [[ -s "${out}" ]]; then
    echo "[fetch-install-media] Keeping existing $(basename "${out}")"
    return
  fi
  if [[ -s "${tmp}" ]]; then
    echo "[fetch-install-media] Resuming $(basename "${out}")"
    curl -fL -C - --progress-bar "${url}" -o "${tmp}"
  else
    echo "[fetch-install-media] Downloading $(basename "${out}")"
    curl -fL --progress-bar "${url}" -o "${tmp}"
  fi
  mv "${tmp}" "${out}"
}

verify_sha256() {
  local file="$1"
  local expected="$2"
  local actual
  actual="$(sha256sum "${file}" | awk '{print $1}')"
  if [[ "${actual}" != "${expected}" ]]; then
    echo "[fetch-install-media] SHA256 mismatch for ${file}" >&2
    echo "expected=${expected}" >&2
    echo "actual=${actual}" >&2
    exit 1
  fi
  echo "[fetch-install-media] sha256 ok: $(basename "${file}")"
}

verify_ventoy_sha() {
  local file="$1"
  local shafile="$2"
  local expected
  expected="$(awk -v name="$(basename "${file}")" '$2 == name {print $1}' "${shafile}")"
  if [[ -z "${expected}" ]]; then
    echo "[fetch-install-media] Could not find Ventoy checksum for $(basename "${file}")" >&2
    exit 1
  fi
  verify_sha256 "${file}" "${expected}"
}

mkdir -p "${SURFACE_DIR}" "${RPI_DIR}" "${TOOLS_DIR}" "${REMOTE_DIR}"

download "${RPI_SHA_URL}" "${RPI_DIR}/SHA256SUMS"
download "${RPI_URL}" "${RPI_DIR}/${RPI_IMG}"
verify_sha256 "${RPI_DIR}/${RPI_IMG}" "${RPI_SHA}"

download "${VENTOY_SHA_URL}" "${TOOLS_DIR}/sha256.txt"
download "${VENTOY_URL}" "${TOOLS_DIR}/${VENTOY_TGZ}"
verify_ventoy_sha "${TOOLS_DIR}/${VENTOY_TGZ}" "${TOOLS_DIR}/sha256.txt"

download "${ANYDESK_URL}" "${REMOTE_DIR}/${ANYDESK_DEB}"

download "${SURFACE_SHA_URL}" "${SURFACE_DIR}/SHA256SUMS"
download "${SURFACE_URL}" "${SURFACE_DIR}/${SURFACE_ISO}"
verify_sha256 "${SURFACE_DIR}/${SURFACE_ISO}" "${SURFACE_SHA}"

cat <<EOF
[fetch-install-media] Completed
base_dir=${BASE_DIR}
surface_iso=${SURFACE_DIR}/${SURFACE_ISO}
rpi_image=${RPI_DIR}/${RPI_IMG}
ventoy_archive=${TOOLS_DIR}/${VENTOY_TGZ}
anydesk_deb=${REMOTE_DIR}/${ANYDESK_DEB}
EOF
