#!/usr/bin/env bash
set -euo pipefail
sshpass -p 11011995 ssh -o StrictHostKeyChecking=no root@192.168.2.10 <<'SSH'
set -euo pipefail
pct create 120 local:vztmpl/debian-12-standard_12.12-1_amd64.tar.zst \
  --hostname vaultwarden \
  --cores 1 \
  --memory 1024 \
  --swap 256 \
  --rootfs local-lvm:8 \
  --net0 name=eth0,bridge=vmbr0,ip=192.168.2.26/24,gw=192.168.2.1 \
  --password 'qb6RN1jOvKznCkuDTPucEaJi' \
  --unprivileged 1 \
  --features nesting=1 \
  --onboot 1
pct start 120
pct status 120
SSH