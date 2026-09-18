#!/bin/bash
# Stellt nach Reboot sicher: CIFS-Musik-Mount da + AzuraCast sieht die Medien
# FraWo 2.0 - Versioniert in deployments/radio/radio-boot-fix.sh
mountpoint -q /mnt/library || mount /mnt/library 2>/dev/null
sleep 3
cnt=$(docker exec azuracast bash -c 'find /var/azuracast/hdd_library -maxdepth 2 -type f 2>/dev/null | head -1 | wc -l' 2>/dev/null)
if [ "${cnt:-0}" -lt 1 ]; then
    logger -t radio-boot-fix "hdd_library leer -> restart azuracast"
    docker restart azuracast
else
    logger -t radio-boot-fix "hdd_library gesund und verbunden"
fi
