# FraWo – Homeserver 2027

> **Single Source of Truth (SSOT) hierarchy:**
> `README.md` (entry point) → [`MASTERPLAN.md`](MASTERPLAN.md) (architecture) → [`AGENTS.md`](AGENTS.md) (agent roles)

## Overview

**FraWo / Homeserver 2027** is a fully automated, security-hardened private-cloud environment built on **Proxmox VE 8.x / 9.x**.  
All infrastructure is managed as code – no manual GUI changes are ever applied to the hypervisor.

| Layer | Tooling |
|---|---|
| Hypervisor | Proxmox VE 8.x / 9.x (API-only management) |
| Provisioning (IaC) | Terraform – `bpg/proxmox` provider |
| Configuration / Hardening | Ansible (roles, `ansible-vault` for secrets) |
| Secret Management | `ansible-vault` / environment variables – **zero hardcoded credentials** |
| Version Control | GitHub (StudioPC = master admin node; Laptops = read/minor-edit) |

## Repository Layout

```
FraWo/
├── README.md              # ← you are here
├── MASTERPLAN.md          # Definitive architecture reference
├── AGENTS.md              # AI-agent operational boundaries & roles
├── terraform/
│   ├── main.tf            # Root module – calls child modules
│   ├── variables.tf       # Input variables (no defaults for secrets)
│   ├── outputs.tf         # Exported values
│   ├── providers.tf       # bpg/proxmox provider configuration
│   ├── terraform.tfvars.example  # Example vars file (no real credentials)
│   └── modules/
│       ├── vm/            # Proxmox VM module
│       └── lxc/           # Proxmox LXC container module
└── ansible/
    ├── ansible.cfg        # Project-level Ansible configuration
    ├── inventory/
    │   └── hosts.yml      # Static inventory (no passwords)
    ├── group_vars/
    │   └── all.yml        # Non-secret group variables
    ├── site.yml           # Master playbook
    └── roles/
        ├── common/        # OS baseline & hardening
        └── proxmox_node/  # Proxmox-specific node configuration
```

## Quick Start

### Prerequisites

* Terraform ≥ 1.7
* Ansible ≥ 2.15
* Access to the Proxmox API (token stored in `TF_VAR_proxmox_api_token` env var)

### Terraform

```bash
cd terraform/
cp terraform.tfvars.example terraform.tfvars   # fill in YOUR values
terraform init
terraform plan
terraform apply
```

### Ansible

```bash
cd ansible/
# Decrypt vault before running (or pass --ask-vault-pass)
ansible-playbook -i inventory/hosts.yml site.yml
```

## Architecture Drift Policy

Any change that contradicts [`MASTERPLAN.md`](MASTERPLAN.md) **must not** be merged.  
See [`AGENTS.md`](AGENTS.md) for the review process followed by AI agents.
