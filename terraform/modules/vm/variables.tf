# ---------------------------------------------------------------------------
# modules/vm/variables.tf
# ---------------------------------------------------------------------------

variable "vm_id" {
  description = "Proxmox VM ID (must be unique per cluster)."
  type        = number
}

variable "name" {
  description = "VM name – must follow pattern vm-{id}-{service} (MASTERPLAN §8)."
  type        = string
}

variable "description" {
  description = "Human-readable description of the VM's purpose."
  type        = string
  default     = ""
}

variable "node_name" {
  description = "Proxmox node on which the VM is created."
  type        = string
}

variable "cores" {
  description = "Number of vCPU cores."
  type        = number
  default     = 2
}

variable "memory_mb" {
  description = "RAM in MiB."
  type        = number
  default     = 2048
}

variable "storage_id" {
  description = "Proxmox storage ID for the VM disk (MASTERPLAN §4)."
  type        = string
}

variable "disk_size_gb" {
  description = "OS disk size in GiB."
  type        = number
  default     = 20
}

variable "vlan_tag" {
  description = "VLAN tag for the primary network interface (MASTERPLAN §2)."
  type        = number
}

variable "ssh_public_key" {
  description = "ED25519 public key for cloud-init SSH access."
  type        = string
  sensitive   = true
}

variable "template_id" {
  description = "Clone source VM template ID (MASTERPLAN §3)."
  type        = number
  default     = 9000
}

variable "bridge" {
  description = "Proxmox network bridge."
  type        = string
  default     = "vmbr1"
}

variable "os_type" {
  description = "Guest OS type hint for Proxmox."
  type        = string
  default     = "l26"
}

variable "started" {
  description = "Whether the VM should be running after creation."
  type        = bool
  default     = true
}
