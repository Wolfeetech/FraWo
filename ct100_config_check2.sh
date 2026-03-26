#!/usr/bin/env bash
set -euo pipefail
sshpass -p 11011995 ssh -o StrictHostKeyChecking=no root@192.168.2.10 <<'SSH'
pct config 100
pvesm list local-lvm | grep 'vm-100' || true
SSH