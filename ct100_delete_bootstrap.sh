set -euo pipefail
sshpass -p 11011995 ssh -o StrictHostKeyChecking=no root@192.168.2.10 'pct exec 100 -- bash -lc "time ionice -c3 nice -n 19 rm -rf /srv/media-library/music/bootstrap-radio-usb"'