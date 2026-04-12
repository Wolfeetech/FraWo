#!/bin/bash
export HOMESERVER_PROXMOX_ROOT_PASSWORD='11011995'
./scripts/proxmox_remote_exec.sh 'qm guest exec 200 -- bash -c "cd /opt/homeserver2027/stacks/nextcloud && docker-compose exec -T -u www-data app php occ app:install mail"'
