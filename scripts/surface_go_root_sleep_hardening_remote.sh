#!/usr/bin/env bash
set -euo pipefail

echo "[surface-root-sleep] Reloading systemd units"
sudo systemctl daemon-reload

echo "[surface-root-sleep] Masking sleep targets"
sudo systemctl mask sleep.target suspend.target hibernate.target hybrid-sleep.target

echo "[surface-root-sleep] Verifying targets"
systemctl is-enabled sleep.target suspend.target hibernate.target hybrid-sleep.target
systemctl status sleep.target suspend.target hibernate.target hybrid-sleep.target --no-pager --lines=2

echo "[surface-root-sleep] Completed"
