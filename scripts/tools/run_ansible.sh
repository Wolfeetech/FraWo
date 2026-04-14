#!/bin/bash
export ANSIBLE_CONFIG="${PWD}/ansible.cfg"
export ANSIBLE_INVENTORY_PATH="${PWD}/ansible/inventory/hosts.yml"
export ANSIBLE_VAULT_PASSWORD_FILE="${PWD}/vault_pass.sh"

chmod +x vault_pass.sh
ansible-playbook --inventory "${ANSIBLE_INVENTORY_PATH}" "${PWD}/ansible/playbooks/bootstrap_surface_go_frontend.yml"
