#!/usr/bin/env bash
set -euo pipefail
sshpass -p 11011995 ssh -o StrictHostKeyChecking=no root@192.168.2.10 "pct help move_volume || pct help move-volume || true"