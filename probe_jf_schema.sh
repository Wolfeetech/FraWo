set -euo pipefail
sshpass -p 11011995 ssh -o StrictHostKeyChecking=no root@192.168.2.10 "pct exec 100 -- bash -lc 'sqlite3 /srv/jellyfin/config/data/jellyfin.db \".schema Users\"'"