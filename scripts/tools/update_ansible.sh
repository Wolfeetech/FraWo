#!/usr/bin/env bash

# STALE (2026-08-20): the nextcloud_vm/odoo_vm/paperless_vm/toolbox host
# groups below belonged to the old "homeserver2027" inventory, archived to
# archive/ansible-homeserver2027/ when the new stock-pve/anker-pve baseline
# (ansible/inventory/hosts.yml, group pve_hosts) was built. None of these
# groups exist in the current inventory, so every ansible call below will
# fail. Needs an operator decision: retire this script, or re-point it at
# whatever now runs these docker-compose stacks. Not fixed here - out of
# scope for the baseline plan (host-OS level only, no app deployments).
set -euxo pipefail

export ANSIBLE_CONFIG="${PWD}/ansible.cfg"
export ANSIBLE_INVENTORY_PATH="${PWD}/ansible/inventory/hosts.yml"

ansible --inventory "${ANSIBLE_INVENTORY_PATH}" nextcloud_vm -m shell -a 'cd /opt/homeserver2027/stacks/nextcloud && docker-compose pull && docker-compose up -d --remove-orphans' --become
ansible --inventory "${ANSIBLE_INVENTORY_PATH}" odoo_vm -m shell -a 'cd /opt/homeserver2027/stacks/odoo && docker-compose pull && docker-compose up -d --remove-orphans' --become
ansible --inventory "${ANSIBLE_INVENTORY_PATH}" paperless_vm -m shell -a 'cd /opt/homeserver2027/stacks/paperless && docker-compose pull && docker-compose up -d --remove-orphans' --become
ansible --inventory "${ANSIBLE_INVENTORY_PATH}" toolbox -m shell -a 'cd /opt/homeserver2027/stacks/toolbox-network && docker-compose pull && docker-compose up -d --remove-orphans' --become
ansible --inventory "${ANSIBLE_INVENTORY_PATH}" toolbox -m shell -a 'cd /opt/homeserver2027/stacks/media && docker-compose pull && docker-compose up -d --remove-orphans' --become

echo "Ansible stack updates completed!"
