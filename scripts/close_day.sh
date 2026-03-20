#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

cd "${ROOT_DIR}"

make inventory-check
make ansible-ping
make qga-check
make business-drift-check
make backup-list
make backup-prune-dry-run
make proxmox-local-backup-check
make haos-stage-gate
make security-baseline-check
bash ./scripts/refresh_live_context.sh

echo "Day close validation complete."
echo "Review these files before stopping:"
echo "  - ${ROOT_DIR}/LIVE_CONTEXT.md"
echo "  - ${ROOT_DIR}/MORNING_ROUTINE.md"
echo "  - ${ROOT_DIR}/SECURITY_BASELINE.md"
echo "  - ${ROOT_DIR}/SESSION_CLOSEOUT.md"
echo "  - ${ROOT_DIR}/NETWORK_INVENTORY.md"
echo "  - ${ROOT_DIR}/BACKUP_RESTORE_PROOF.md"
