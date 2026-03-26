#!/usr/bin/env bash
set -euo pipefail
sshpass -p 11011995 ssh -o StrictHostKeyChecking=no root@192.168.2.10 <<'SSH'
set -euo pipefail
mkdir -p /mnt/wolf-ee
mountpoint -q /mnt/wolf-ee || mount -t ntfs3 /dev/sda2 /mnt/wolf-ee
mkdir -p /mnt/wolf-ee/hs27_root_relief/template
if [ -d /var/lib/vz/template/iso ] && [ ! -L /var/lib/vz/template/iso ]; then
  mv /var/lib/vz/template/iso /mnt/wolf-ee/hs27_root_relief/template/iso
  ln -s /mnt/wolf-ee/hs27_root_relief/template/iso /var/lib/vz/template/iso
fi
if [ -d /var/lib/vz/template/qcow2 ] && [ ! -L /var/lib/vz/template/qcow2 ]; then
  mv /var/lib/vz/template/qcow2 /mnt/wolf-ee/hs27_root_relief/template/qcow2
  ln -s /mnt/wolf-ee/hs27_root_relief/template/qcow2 /var/lib/vz/template/qcow2
fi
df -h /
ls -ld /var/lib/vz/template/iso /var/lib/vz/template/qcow2
SSH