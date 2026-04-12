#!/usr/bin/env bash

set -euxo pipefail

export HOMESERVER_PROXMOX_ROOT_PASSWORD='11011995'

# Update CT 100
./scripts/proxmox_remote_exec.sh 'pct exec 100 -- bash -c "export DEBIAN_FRONTEND=noninteractive; apt-get update && apt-get dist-upgrade -yq && apt-get autoremove -yq"'

# Update VM 200
./scripts/proxmox_remote_exec.sh 'qm guest exec 200 -- bash -c "export DEBIAN_FRONTEND=noninteractive; apt-get update && apt-get dist-upgrade -yq && apt-get autoremove -yq"'

# Update VM 220
./scripts/proxmox_remote_exec.sh 'qm guest exec 220 -- bash -c "export DEBIAN_FRONTEND=noninteractive; apt-get update && apt-get dist-upgrade -yq && apt-get autoremove -yq"'

# Update VM 230
./scripts/proxmox_remote_exec.sh 'qm guest exec 230 -- bash -c "export DEBIAN_FRONTEND=noninteractive; apt-get update && apt-get dist-upgrade -yq && apt-get autoremove -yq"'

echo "OS updates completed!"
