#!/usr/bin/env bash
set -euo pipefail
sshpass -p 11011995 ssh -o StrictHostKeyChecking=no root@192.168.2.10 <<'SSH'
set -euo pipefail
mkdir -p /mnt/wolf-ee/hs27_root_relief/root-home
if [ -d /root/.antigravity-server ] && [ ! -L /root/.antigravity-server ]; then
  mv /root/.antigravity-server /mnt/wolf-ee/hs27_root_relief/root-home/.antigravity-server
  ln -s /mnt/wolf-ee/hs27_root_relief/root-home/.antigravity-server /root/.antigravity-server
fi
if [ -d /root/.cache ] && [ ! -L /root/.cache ]; then
  mv /root/.cache /mnt/wolf-ee/hs27_root_relief/root-home/.cache
  ln -s /mnt/wolf-ee/hs27_root_relief/root-home/.cache /root/.cache
fi
journalctl --vacuum-time=3d >/dev/null 2>&1 || true
rm -rf /var/cache/apt/archives/* || true
df -h /
SSH