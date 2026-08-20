#!/bin/bash
# STALE (2026-08-20): references ansible/playbooks/bootstrap_surface_go_frontend.yml,
# which was archived to archive/ansible-homeserver2027/ when the new
# stock-pve/anker-pve baseline (ansible/playbooks/baseline.yml) was built.
# It also points ANSIBLE_VAULT_PASSWORD_FILE at vault_pass.sh, which does not
# match ansible.cfg's vault_password_file (ansible/.vault_pass). Needs an
# operator decision: restore the Surface Go playbook from the archive, or
# retire this script. Not fixed here - out of scope for the baseline plan.
export ANSIBLE_CONFIG="${PWD}/ansible.cfg"
export ANSIBLE_INVENTORY_PATH="${PWD}/ansible/inventory/hosts.yml"
export ANSIBLE_VAULT_PASSWORD_FILE="${PWD}/vault_pass.sh"

chmod +x vault_pass.sh
ansible-playbook --inventory "${ANSIBLE_INVENTORY_PATH}" "${PWD}/ansible/playbooks/bootstrap_surface_go_frontend.yml"
