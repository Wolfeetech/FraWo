#!/usr/bin/env bash

set -euxo pipefail

export HOMESERVER_PROXMOX_ROOT_PASSWORD='11011995'

# Update Nextcloud
./scripts/proxmox_remote_exec.sh 'qm guest exec 200 -- bash -c "cd /opt/homeserver2027/stacks/nextcloud && docker-compose pull && docker-compose up -d --remove-orphans"'

# Update Odoo
./scripts/proxmox_remote_exec.sh 'qm guest exec 220 -- bash -c "cd /opt/homeserver2027/stacks/odoo && docker-compose pull && docker-compose up -d --remove-orphans"'

# Update Paperless
./scripts/proxmox_remote_exec.sh 'qm guest exec 230 -- bash -c "cd /opt/homeserver2027/stacks/paperless && docker-compose pull && docker-compose up -d --remove-orphans"'

# Update Toolbox & Media
./scripts/proxmox_remote_exec.sh 'pct exec 100 -- bash -c "cd /opt/homeserver2027/stacks/toolbox-network && docker-compose pull && docker-compose up -d --remove-orphans"'
./scripts/proxmox_remote_exec.sh 'pct exec 100 -- bash -c "cd /opt/homeserver2027/stacks/media && docker-compose pull && docker-compose up -d --remove-orphans"'

echo "Docker stack updates completed!"
