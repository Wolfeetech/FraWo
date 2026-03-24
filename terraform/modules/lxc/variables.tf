# ---------------------------------------------------------------------------
# modules/lxc/variables.tf
# ---------------------------------------------------------------------------

variable "lxc_id" {
  description = "Proxmox container ID (must be unique per cluster)."
  type        = number
}

variable "hostname" {
  description = "Container hostname – must follow pattern ct-{id}-{service} (MASTERPLAN §8)."
  type        = string
}

variable "description" {
  description = "Human-readable description of the container's purpose."
  type        = string
  default     = ""
}

variable "node_name" {
  description = "Proxmox node on which the container is created."
  type        = string
}

variable "cores" {
  description = "Number of vCPU cores."
  type        = number
  default     = 1
}

variable "memory_mb" {
  description = "RAM in MiB."
  type        = number
  default     = 512
}

variable "storage_id" {
  description = "Proxmox storage ID for the container root filesystem (MASTERPLAN §4)."
  type        = string
}

variable "disk_size_gb" {
  description = "Root filesystem size in GiB."
  type        = number
  default     = 8
}

variable "vlan_tag" {
  description = "VLAN tag for the primary network interface (MASTERPLAN §2)."
  type        = number
}

variable "ssh_public_key" {
  description = "ED25519 public key for SSH access (MASTERPLAN §7)."
  type        = string
  sensitive   = true
}

variable "os_template" {
  description = "LXC OS template (content type 'vztmpl') on the Proxmox node."
  type        = string
  default     = "local:vztmpl/debian-12-standard_12.7-1_amd64.tar.zst"
}

variable "bridge" {
  description = "Proxmox network bridge."
  type        = string
  default     = "vmbr1"
}

variable "unprivileged" {
  description = "Run container as unprivileged (recommended)."
  type        = bool
  default     = true
}

variable "started" {
  description = "Whether the container should be running after creation."
  type        = bool
  default     = true
}
