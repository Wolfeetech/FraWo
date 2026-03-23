#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

cd "${ROOT_DIR}"

make inventory-check
make ansible-ping
make qga-check
make business-drift-check
make toolbox-network-check
make toolbox-portal-status-check
make toolbox-media-check
make toolbox-tailscale-check
make rpi-radio-integration-check
make rpi-radio-usb-check
make haos-reverse-proxy-check
make backup-list
make proxmox-local-backup-check
make pbs-stage-gate
make pbs-proof-check
make haos-stage-gate
make security-baseline-check
make surface-go-check
bash ./scripts/refresh_live_context.sh

echo "Day start validation complete."
echo "Review these files before implementing changes:"
echo "  - ${ROOT_DIR}/LIVE_CONTEXT.md"
echo "  - ${ROOT_DIR}/MORNING_ROUTINE.md"
echo "  - ${ROOT_DIR}/SECURITY_BASELINE.md"
echo "  - ${ROOT_DIR}/SESSION_CLOSEOUT.md"
