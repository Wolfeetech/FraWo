# ---------------------------------------------------------------------------
# variables.tf – Root module input variables
# ---------------------------------------------------------------------------
# Sensitive variables must NEVER have default values.
# Supply them via terraform.tfvars (git-ignored) or TF_VAR_* env vars.
# ---------------------------------------------------------------------------

# ── Proxmox nodes ───────────────────────────────────────────────────────────

variable "proxmox_node_primary" {
  description = "Name of the primary Proxmox node (matches MASTERPLAN §3)."
  type        = string
  default     = "pve-01"
}

variable "proxmox_node_secondary" {
  description = "Name of the secondary Proxmox node (matches MASTERPLAN §3)."
  type        = string
  default     = "pve-02"
}

# ── SSH ──────────────────────────────────────────────────────────────────────

variable "ssh_public_key" {
  description = "ED25519 public key injected into VM/LXC cloud-init (no passwords)."
  type        = string
  sensitive   = true
}

# ── Storage ──────────────────────────────────────────────────────────────────

variable "storage_tier0" {
  description = "Tier-0 storage ID for VM/LXC disks (MASTERPLAN §4)."
  type        = string
  default     = "local-nvme"
}

# ── Networking ───────────────────────────────────────────────────────────────

variable "vlan_containers" {
  description = "VLAN tag for the containers segment (MASTERPLAN §2)."
  type        = number
  default     = 50
}

variable "vlan_vms" {
  description = "VLAN tag for the VMs segment (MASTERPLAN §2)."
  type        = number
  default     = 60
}

variable "vlan_dmz" {
  description = "VLAN tag for the DMZ segment (MASTERPLAN §2)."
  type        = number
  default     = 40
}

variable "vlan_mgmt" {
  description = "VLAN tag for the management segment (MASTERPLAN §2)."
  type        = number
  default     = 10
}

variable "vlan_iot" {
  description = "VLAN tag for the IoT segment (MASTERPLAN §2)."
  type        = number
  default     = 30
}

variable "vlan_vpn" {
  description = "VLAN tag for the VPN segment (MASTERPLAN §2)."
  type        = number
  default     = 99
}
