#!/usr/bin/env bash

set -euxo pipefail

export ANSIBLE_CONFIG="${PWD}/ansible.cfg"
export ANSIBLE_INVENTORY_PATH="${PWD}/ansible/inventory/hosts.yml"

ansible --inventory "${ANSIBLE_INVENTORY_PATH}" nextcloud_vm -m shell -a 'cd /opt/homeserver2027/stacks/nextcloud && docker-compose pull && docker-compose up -d --remove-orphans' --become
ansible --inventory "${ANSIBLE_INVENTORY_PATH}" odoo_vm -m shell -a 'cd /opt/homeserver2027/stacks/odoo && docker-compose pull && docker-compose up -d --remove-orphans' --become
ansible --inventory "${ANSIBLE_INVENTORY_PATH}" paperless_vm -m shell -a 'cd /opt/homeserver2027/stacks/paperless && docker-compose pull && docker-compose up -d --remove-orphans' --become
ansible --inventory "${ANSIBLE_INVENTORY_PATH}" toolbox -m shell -a 'cd /opt/homeserver2027/stacks/toolbox-network && docker-compose pull && docker-compose up -d --remove-orphans' --become
ansible --inventory "${ANSIBLE_INVENTORY_PATH}" toolbox -m shell -a 'cd /opt/homeserver2027/stacks/media && docker-compose pull && docker-compose up -d --remove-orphans' --become

echo "Ansible stack updates completed!"
