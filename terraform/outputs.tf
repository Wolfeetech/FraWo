# ---------------------------------------------------------------------------
# outputs.tf – Root module exported values
# ---------------------------------------------------------------------------

output "vm_ids" {
  description = "Map of service name → Proxmox VM ID."
  value = {
    vaultwarden  = module.vm_vaultwarden.vm_id
    nextcloud    = module.vm_nextcloud.vm_id
    wireguard    = module.vm_wireguard.vm_id
    pbs          = module.vm_pbs.vm_id
    monitoring   = module.vm_monitoring.vm_id
  }
}

output "lxc_ids" {
  description = "Map of service name → Proxmox LXC container ID."
  value = {
    npmgr         = module.lxc_npmgr.lxc_id
    adguard       = module.lxc_adguard.lxc_id
    home_assistant = module.lxc_home_assistant.lxc_id
  }
}
