#!/usr/bin/env bash
set -euo pipefail
sshpass -p 11011995 ssh -o StrictHostKeyChecking=no root@192.168.2.10 <<'SSH'
set -euo pipefail
pct shutdown 100 --timeout 60 || true
sleep 5
if pct status 100 | grep -q running; then
  pct stop 100
fi
pct move-volume 100 rootfs local-lvm --delete 1
pct start 100
sleep 15
pct status 100
pvesm status
SSH