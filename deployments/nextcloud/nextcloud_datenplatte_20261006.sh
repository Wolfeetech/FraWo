#!/bin/bash
# Nextcloud-Daten auf neue 500-GB-Platte (sdb) umziehen (Odoo #1930). Laeuft auf VM300.
set -euo pipefail
DEV=/dev/sdb
[ "$(lsblk -bdno SIZE $DEV)" = "536870912000" ] || { echo "ABBRUCH: $DEV ist nicht die neue 500-GB-Platte"; exit 1; }
[ -z "$(lsblk -no FSTYPE $DEV)" ] && [ "$(lsblk -no NAME $DEV | wc -l)" = 1 ] || { echo "ABBRUCH: $DEV nicht leer"; exit 1; }
D=/var/lib/docker/volumes/nextcloud_nextcloud/_data/data
mkfs.ext4 -q -L ncdata $DEV
UUID=$(blkid -s UUID -o value $DEV)
mkdir -p /srv/ncdata-neu && mount $DEV /srv/ncdata-neu
docker exec -u www-data nextcloud_app_1 php occ maintenance:mode --on
rsync -aHAX "$D/" /srv/ncdata-neu/
A=$(du -s --apparent-size "$D" | cut -f1); N=$(du -s --apparent-size /srv/ncdata-neu | cut -f1)
echo "alt=$A KB neu=$N KB"
umount /srv/ncdata-neu
mv "$D" "$D.alt-20261006"; mkdir "$D"
cp -p /etc/fstab /etc/fstab.bak-20261006
echo "UUID=$UUID $D ext4 defaults,noatime 0 2" >> /etc/fstab
systemctl daemon-reload; mount "$D"
chown 33:33 "$D"; chmod 0770 "$D"
ls -la "$D" | head -5
docker exec -u www-data nextcloud_app_1 php occ maintenance:mode --off
docker exec -u www-data nextcloud_app_1 php occ status | grep -E "installed|maintenance"
df -h "$D" | tail -1
