#!/usr/bin/env bash
set -euo pipefail
sshpass -p 11011995 ssh -o StrictHostKeyChecking=no root@192.168.2.10 <<'SSH'
du -xh --max-depth=2 /var/lib/vz 2>/dev/null | sort -h | tail -n 40
SSH