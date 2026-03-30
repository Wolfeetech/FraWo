#!/usr/bin/env bash

set -euxo pipefail

export ANSIBLE_CONFIG="${PWD}/ansible.cfg"
export ANSIBLE_INVENTORY_PATH="${PWD}/ansible/inventory/hosts.yml"

echo "Pinging Surface..."
ansible --inventory "${ANSIBLE_INVENTORY_PATH}" --vault-password-file .vault_pass surface_go_frontend -m ping

echo "Deploying to Surface..."
ansible-playbook --inventory "${ANSIBLE_INVENTORY_PATH}" --vault-password-file .vault_pass ansible/playbooks/bootstrap_surface_go_frontend.yml
