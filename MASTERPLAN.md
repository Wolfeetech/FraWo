# MASTERPLAN – Homeserver 2027

> **Status:** Living document – every architectural decision must be recorded here first.  
> Last updated: 2026-03-24

---

## Table of Contents

1. [Network Architecture](#1-network-architecture)
2. [VLAN Definitions](#2-vlan-definitions)
3. [Compute Resources](#3-compute-resources)
4. [Storage Tiers](#4-storage-tiers)
5. [Service Catalogue](#5-service-catalogue)
6. [Backup & Recovery Policies](#6-backup--recovery-policies)
7. [Security Baseline](#7-security-baseline)
8. [Naming Conventions](#8-naming-conventions)

---

## 1. Network Architecture

### Physical Topology

| Segment | CIDR | Gateway | Notes |
|---|---|---|---|
| Management | `10.0.0.0/24` | `10.0.0.1` | Proxmox hosts, IPMI/iDRAC, admin access only |
| LAN (Trusted) | `10.10.0.0/22` | `10.10.0.1` | Workstations, NAS clients |
| IoT | `10.20.0.0/24` | `10.20.0.1` | Isolated; no Internet-bound DNS override |
| DMZ | `10.30.0.0/24` | `10.30.0.1` | Reverse-proxy, public-facing services |
| Containers | `10.40.0.0/22` | `10.40.0.1` | LXC workloads |
| VMs | `10.50.0.0/22` | `10.50.0.1` | Terraform-managed VMs |
| VPN | `10.99.0.0/24` | `10.99.0.1` | WireGuard / remote access |

### Firewall Rules (summary)

* Management segment is **not reachable** from LAN without VPN.
* Inter-VLAN routing is **deny-by-default**; explicit allow-rules only.
* DMZ may reach Containers on specific ports (80/443 → reverse proxy).
* IoT has no inbound rules from any other segment.

---

## 2. VLAN Definitions

| VLAN ID | Name | Segment | Tagged On |
|---|---|---|---|
| 10 | `mgmt` | `10.0.0.0/24` | Proxmox uplink, trunk |
| 20 | `lan_trusted` | `10.10.0.0/22` | Access ports, trunk |
| 30 | `iot` | `10.20.0.0/24` | Access ports (IoT switch) |
| 40 | `dmz` | `10.30.0.0/24` | Trunk (DMZ ports) |
| 50 | `containers` | `10.40.0.0/22` | Trunk (Proxmox bridges) |
| 60 | `vms` | `10.50.0.0/22` | Trunk (Proxmox bridges) |
| 99 | `vpn` | `10.99.0.0/24` | Trunk (WireGuard VM) |

Proxmox bridges: `vmbr0` (untagged/native), `vmbr1` (VLAN-aware trunk).

---

## 3. Compute Resources

### Proxmox Nodes

| Node | Role | CPU | RAM | Primary Storage |
|---|---|---|---|---|
| `pve-01` | Primary hypervisor | 8 cores | 64 GB | NVMe |
| `pve-02` | Secondary / HA pair | 8 cores | 32 GB | NVMe |

### VM Templates

| Template ID | OS | Purpose |
|---|---|---|
| 9000 | Debian 12 (cloud-init) | General-purpose VMs |
| 9001 | Ubuntu 22.04 (cloud-init) | Service VMs |

### LXC Templates

| Template | Purpose |
|---|---|
| `debian-12-standard` | Lightweight containers |

---

## 4. Storage Tiers

| Tier | Storage ID | Type | Use Case | Retention |
|---|---|---|---|---|
| Tier 0 | `local-nvme` | `dir` / ZFS | VM disks (performance) | – |
| Tier 1 | `local-hdd` | ZFS RAID-Z1 | Bulk data, media | – |
| Tier 2 | `backup-nas` | NFS / SMB mount | Proxmox Backup Server (PBS) | 30 days |
| Tier 3 | `offsite-s3` | S3-compatible | Off-site encrypted backups | 90 days |

> **Rule:** No VM or container may store its disk on `backup-nas` or `offsite-s3`.  
> Backups must flow: VM disk (Tier 0) → PBS job → Tier 2 → rclone sync → Tier 3.

---

## 5. Service Catalogue

| Service | Type | Host/Container | VLAN | Notes |
|---|---|---|---|---|
| Proxmox VE | Hypervisor | `pve-01`, `pve-02` | mgmt (10) | |
| Nginx Proxy Manager | LXC | `ct-101` | dmz (40) | Reverse proxy |
| AdGuard Home | LXC | `ct-102` | mgmt (10) | DNS for all VLANs |
| Vaultwarden | VM | `vm-201` | containers (50) | Password manager |
| Nextcloud | VM | `vm-202` | containers (50) | Self-hosted cloud |
| Home Assistant | LXC | `ct-103` | iot (30) | IoT automation |
| WireGuard | VM | `vm-203` | vpn (99) + dmz (40) | VPN gateway |
| Proxmox Backup Server | VM | `vm-204` | mgmt (10) | Backup target |
| Monitoring (Grafana/Prometheus) | VM | `vm-205` | mgmt (10) | |

---

## 6. Backup & Recovery Policies

### Schedule

| Scope | Tool | Schedule (cron) | Retention |
|---|---|---|---|
| All VMs | Proxmox Backup Server | `0 2 * * *` (02:00 daily) | 7 daily, 4 weekly, 3 monthly |
| All LXC | Proxmox Backup Server | `0 3 * * *` (03:00 daily) | 7 daily, 4 weekly, 3 monthly |
| Off-site sync | rclone + Tier 3 | `0 5 * * *` (05:00 daily) | 90 days |

### Recovery Objectives

| Metric | Target |
|---|---|
| RTO (Recovery Time Objective) | < 4 hours |
| RPO (Recovery Point Objective) | < 24 hours |

### Backup Encryption

* All PBS jobs use client-side encryption (`PBS_ENCRYPTION_KEY` env var; key stored in Vaultwarden).
* Off-site S3 objects encrypted at rest (`rclone crypt` remote).

---

## 7. Security Baseline

1. **No hardcoded credentials** anywhere in the codebase – use `ansible-vault` or environment variables.
2. **SSH**: password authentication disabled; ED25519 key pairs only; root login disabled.
3. **Firewall**: `nftables` managed by Ansible role `common`; default-deny inbound.
4. **Proxmox API**: API token authentication only (no username/password in Terraform).
5. **Unattended upgrades**: enabled on all Debian/Ubuntu nodes.
6. **Fail2ban**: deployed on all SSH-exposed hosts.
7. **CIS Benchmark**: Level 1 controls applied via `common` Ansible role.
8. **Secrets rotation**: at minimum annually; rotated immediately on suspected compromise.

---

## 8. Naming Conventions

### Terraform / Proxmox

| Resource | Pattern | Example |
|---|---|---|
| VM | `vm-{id}-{service}` | `vm-201-vaultwarden` |
| LXC | `ct-{id}-{service}` | `ct-101-npmgr` |
| Terraform module | `{type}_{service}` | `module.vm_vaultwarden` |
| Terraform variable | `snake_case` | `proxmox_node_name` |

### Ansible

| Resource | Pattern | Example |
|---|---|---|
| Role | `snake_case` | `common`, `proxmox_node` |
| Group var file | `{group}.yml` | `all.yml`, `webservers.yml` |
| Vault file | `vault_{scope}.yml` | `vault_all.yml` |
| Tag | `{role}:{task}` | `common:hardening` |

### Git Branches

| Branch | Purpose |
|---|---|
| `main` | Production-ready, protected |
| `dev` | Integration branch |
| `feature/*` | New features / services |
| `hotfix/*` | Emergency fixes |
