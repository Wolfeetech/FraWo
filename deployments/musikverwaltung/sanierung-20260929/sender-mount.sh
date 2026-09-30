#!/bin/sh
# 🤖 [Claude] 29.09.2026 — Odoo #1263/#1090: AzuraCast (VM220) auf die Freigabe [sender] umstellen.
# Container sieht /mnt/library per rslave -> kein Container-Neustart noetig.
# Rueckweg: /etc/fstab.bak-20260929-sender zurueck, dann gleiche zwei Mount-Befehle.
set -e
sudo cp -a /etc/fstab /etc/fstab.bak-20260929-sender
sudo sed -i 's#^//10.1.0.94/music /mnt/library cifs credentials=/root/.smbcreds,rw,#//10.1.0.94/sender /mnt/library cifs credentials=/root/.smbcreds,ro,#' /etc/fstab
grep '/mnt/library' /etc/fstab
sudo umount -l /mnt/library
sudo mount /mnt/library
mount | grep /mnt/library
for d in Inbox _STAGING_RAW Quarantine Curated_Playlists.bak-20260914; do
  [ -e "/mnt/library/$d" ] && echo "NOCH SICHTBAR: $d" || echo "ausgeblendet: $d"
done
ls /mnt/library/Curated_Playlists/01_Sunrise | head -2
sudo docker exec azuracast ls /var/azuracast/hdd_library/Curated_Playlists/ | head -3
