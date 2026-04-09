#!/bin/bash
export HOMESERVER_PROXMOX_ROOT_PASSWORD='11011995'
./scripts/proxmox_remote_exec.sh "qm guest exec 220 -- bash -c 'cd /opt/homeserver2027/stacks/odoo && echo -e \"task = env['\\'project.task\\''].create({\\'name\\': \\'Endgeräte Franz onboarden\\', \\'description\\': \\'<ul><li>[ ] Surface Go aushändigen und Passwörter testen</li><li>[ ] Nextcloud Mail-App Testnachricht senden</li><li>[ ] AnyDesk-ID verifizieren</li><li>[ ] Portal als Startseite in Kiosk-Mode fixieren</li></ul>\\'})\n\" | docker-compose exec -T web odoo shell -d postgres'"
