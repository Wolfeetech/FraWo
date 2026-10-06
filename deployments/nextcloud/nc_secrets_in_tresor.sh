#!/usr/bin/env bash
# Nextcloud-Geheimnisse in Vaultwarden (agent@, Allgemein/Automations-Secrets) und Altdatei vernichten (Odoo #1930/#1931).
# /root/nc_secrets.txt auf VM300 ist eine Abschrift von 06/2026, fuer alle lesbar (644). Abgelegt werden die
# LIVE-Werte aus config.php (massgeblich), danach wird die Abschrift per shred entfernt.
# Von Wolf am StudioPC zu starten:
#   ! bash C:/Users/StudioPC/FraWo/deployments/nextcloud/nc_secrets_in_tresor.sh
set -euo pipefail
for K in dbpassword secret passwordsalt; do
  ssh -o BatchMode=yes root@10.1.0.227 "ssh -o BatchMode=yes root@10.1.0.21 'docker exec -u www-data nextcloud_app_1 php occ config:system:get $K' | tr -d '\r\n' | frawo-secret ablegen 'Nextcloud VM300 config.php $K' $K https://cloud.frawo.tech"
done
ssh -o BatchMode=yes root@10.1.0.227 "ssh -o BatchMode=yes root@10.1.0.21 'shred -u /root/nc_secrets.txt && echo Altdatei vernichtet'"
