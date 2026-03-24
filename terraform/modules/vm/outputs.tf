# ---------------------------------------------------------------------------
# modules/vm/outputs.tf
# ---------------------------------------------------------------------------

output "vm_id" {
  description = "Proxmox VM ID."
  value       = proxmox_virtual_environment_vm.this.vm_id
}

output "name" {
  description = "VM name."
  value       = proxmox_virtual_environment_vm.this.name
}

output "node_name" {
  description = "Proxmox node hosting the VM."
  value       = proxmox_virtual_environment_vm.this.node_name
}
