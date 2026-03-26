#!/usr/bin/env bash
set -euo pipefail
sshpass -p 11011995 ssh -o StrictHostKeyChecking=no root@192.168.2.10 'lvs -a -o lv_name,lv_size,origin,data_percent,metadata_percent pve'