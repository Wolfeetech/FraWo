#!/bin/bash
# Google Drive in Nextcloud einbinden (Odoo #1930). Laeuft auf VM300.
set -euo pipefail
cat > /etc/systemd/system/rclone-gdrive.service <<'UNIT'
[Unit]
Description=Google Drive fuer Nextcloud einhaengen (rclone, Odoo #1930)
After=network-online.target
Wants=network-online.target
Before=docker.service

[Service]
Type=notify
ExecStartPre=/bin/mkdir -p /mnt/extern/gdrive
ExecStart=/usr/bin/rclone mount gdrive: /mnt/extern/gdrive --config /root/.config/rclone/rclone.conf \
  --allow-other --uid 33 --gid 33 --umask 007 --vfs-cache-mode writes --vfs-cache-max-size 20G \
  --dir-cache-time 10m --poll-interval 1m --tpslimit 8 --log-level NOTICE
ExecStop=/bin/fusermount3 -u /mnt/extern/gdrive
Restart=on-failure
RestartSec=20

[Install]
WantedBy=multi-user.target
UNIT
systemctl daemon-reload
systemctl enable --now rclone-gdrive.service
sleep 5
ls /mnt/extern/gdrive | head -3
C=/opt/homeserver2027/stacks/nextcloud/docker-compose.yml
cp -p $C $C.bak-20261006
grep -q /mnt/extern $C || sed -i 's#      - nextcloud:/var/www/html#      - nextcloud:/var/www/html\n      - /mnt/extern:/mnt/extern:rslave#' $C
grep -n "/mnt/extern" $C
cd /opt/homeserver2027/stacks/nextcloud && docker-compose up -d app 2>&1 | tail -2
sleep 15
O="docker exec -u www-data nextcloud_app_1 php occ"
docker exec nextcloud_app_1 ls /mnt/extern/gdrive | head -3
$O app:enable files_external | tail -1
ID=$($O files_external:create "Google Drive" local null::null -c datadir=/mnt/extern/gdrive | grep -o -E "[0-9]+$")
$O files_external:applicable --add-user=wolf "$ID" >/dev/null
$O files_external:list | head -6
