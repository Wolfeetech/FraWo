# ---------------------------------------------------------------------------
# modules/lxc/outputs.tf
# ---------------------------------------------------------------------------

output "lxc_id" {
  description = "Proxmox container ID."
  value       = proxmox_virtual_environment_container.this.vm_id
}

output "hostname" {
  description = "Container hostname."
  value       = proxmox_virtual_environment_container.this.initialization[0].hostname
}

output "node_name" {
  description = "Proxmox node hosting the container."
  value       = proxmox_virtual_environment_container.this.node_name
}
