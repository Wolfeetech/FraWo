#!/usr/bin/env bash
set -euo pipefail
sshpass -p 11011995 ssh -o StrictHostKeyChecking=no root@192.168.2.10 <<'SSH'
mount | grep -E 'sdb|Wolf|ntfs|hs27_local_dump_archive|media'
lsblk -f
SSH