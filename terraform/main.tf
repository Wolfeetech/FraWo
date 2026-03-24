# ---------------------------------------------------------------------------
# main.tf – Root module
# Instantiates all child modules defined in MASTERPLAN §5 Service Catalogue.
# ---------------------------------------------------------------------------

# ── VMs ──────────────────────────────────────────────────────────────────────

module "vm_vaultwarden" {
  source       = "./modules/vm"
  vm_id        = 201
  name         = "vm-201-vaultwarden"
  description  = "Password manager – Vaultwarden"
  node_name    = var.proxmox_node_primary
  cores        = 2
  memory_mb    = 2048
  storage_id   = var.storage_tier0
  disk_size_gb = 20
  vlan_tag     = var.vlan_containers
  ssh_public_key = var.ssh_public_key
}

module "vm_nextcloud" {
  source       = "./modules/vm"
  vm_id        = 202
  name         = "vm-202-nextcloud"
  description  = "Self-hosted cloud – Nextcloud"
  node_name    = var.proxmox_node_primary
  cores        = 4
  memory_mb    = 4096
  storage_id   = var.storage_tier0
  disk_size_gb = 100
  vlan_tag     = var.vlan_containers
  ssh_public_key = var.ssh_public_key
}

module "vm_wireguard" {
  source       = "./modules/vm"
  vm_id        = 203
  name         = "vm-203-wireguard"
  description  = "VPN gateway – WireGuard"
  node_name    = var.proxmox_node_primary
  cores        = 2
  memory_mb    = 1024
  storage_id   = var.storage_tier0
  disk_size_gb = 10
  vlan_tag     = var.vlan_vpn
  ssh_public_key = var.ssh_public_key
}

module "vm_pbs" {
  source       = "./modules/vm"
  vm_id        = 204
  name         = "vm-204-pbs"
  description  = "Proxmox Backup Server"
  node_name    = var.proxmox_node_secondary
  cores        = 2
  memory_mb    = 4096
  storage_id   = var.storage_tier0
  disk_size_gb = 50
  vlan_tag     = var.vlan_mgmt
  ssh_public_key = var.ssh_public_key
}

module "vm_monitoring" {
  source       = "./modules/vm"
  vm_id        = 205
  name         = "vm-205-monitoring"
  description  = "Monitoring stack – Grafana + Prometheus"
  node_name    = var.proxmox_node_primary
  cores        = 2
  memory_mb    = 4096
  storage_id   = var.storage_tier0
  disk_size_gb = 40
  vlan_tag     = var.vlan_mgmt
  ssh_public_key = var.ssh_public_key
}

# ── LXC containers ───────────────────────────────────────────────────────────

module "lxc_npmgr" {
  source        = "./modules/lxc"
  lxc_id        = 101
  hostname      = "ct-101-npmgr"
  description   = "Reverse proxy – Nginx Proxy Manager"
  node_name     = var.proxmox_node_primary
  cores         = 2
  memory_mb     = 1024
  storage_id    = var.storage_tier0
  disk_size_gb  = 10
  vlan_tag      = var.vlan_dmz
  ssh_public_key = var.ssh_public_key
}

module "lxc_adguard" {
  source        = "./modules/lxc"
  lxc_id        = 102
  hostname      = "ct-102-adguard"
  description   = "DNS filter – AdGuard Home"
  node_name     = var.proxmox_node_primary
  cores         = 1
  memory_mb     = 512
  storage_id    = var.storage_tier0
  disk_size_gb  = 5
  vlan_tag      = var.vlan_mgmt
  ssh_public_key = var.ssh_public_key
}

module "lxc_home_assistant" {
  source        = "./modules/lxc"
  lxc_id        = 103
  hostname      = "ct-103-homeassistant"
  description   = "IoT automation – Home Assistant"
  node_name     = var.proxmox_node_primary
  cores         = 2
  memory_mb     = 2048
  storage_id    = var.storage_tier0
  disk_size_gb  = 20
  vlan_tag      = var.vlan_iot
  ssh_public_key = var.ssh_public_key
}
