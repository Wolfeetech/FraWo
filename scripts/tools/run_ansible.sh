#!/bin/bash
# STALE (2026-08-20): references ansible/playbooks/bootstrap_surface_go_frontend.yml,
# which was archived to archive/ansible-homeserver2027/ when the new
# stock-pve/anker-pve baseline (ansible/playbooks/baseline.yml) was built.
# Needs an operator decision: restore the Surface Go playbook from the
# archive, or retire this script. Not fixed here - out of scope.
#
# SECURITY FIX (2026-09-14): previously pointed ANSIBLE_VAULT_PASSWORD_FILE
# at scripts/tools/vault_pass.sh, which had the real vault password
# hardcoded in plaintext and committed to this public repo since
# 2026-03-30. That file is deleted. Now points at the correctly gitignored
# ansible/.vault_pass (matches ansible.cfg's vault_password_file).
# TODO(Wolf): ansible/inventory/group_vars/all/vault.yml is still encrypted
# with the leaked password - rekey it with a new one (`ansible-vault rekey`)
# and drop the new password into ansible/.vault_pass. Not done by the agent:
# writing/handling vault passwords is blocked by design.
export ANSIBLE_CONFIG="${PWD}/ansible.cfg"
export ANSIBLE_INVENTORY_PATH="${PWD}/ansible/inventory/hosts.yml"
export ANSIBLE_VAULT_PASSWORD_FILE="${PWD}/ansible/.vault_pass"

ansible-playbook --inventory "${ANSIBLE_INVENTORY_PATH}" "${PWD}/ansible/playbooks/bootstrap_surface_go_frontend.yml"
