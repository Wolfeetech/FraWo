# ---------------------------------------------------------------------------
# modules/vm/main.tf – Proxmox VM resource (bpg/proxmox provider)
# ---------------------------------------------------------------------------

resource "proxmox_virtual_environment_vm" "this" {
  vm_id       = var.vm_id
  name        = var.name
  description = var.description
  node_name   = var.node_name
  started     = var.started

  clone {
    vm_id = var.template_id
    full  = true
  }

  cpu {
    cores = var.cores
    type  = "host"
  }

  memory {
    dedicated = var.memory_mb
  }

  disk {
    datastore_id = var.storage_id
    interface    = "scsi0"
    size         = var.disk_size_gb  # integer GiB – bpg/proxmox provider native format
    discard      = "on"
  }

  network_device {
    bridge  = var.bridge
    vlan_id = var.vlan_tag
    model   = "virtio"
  }

  initialization {
    user_account {
      # Password login is disabled; key-only access (MASTERPLAN §7).
      keys = [var.ssh_public_key]
    }

    ip_config {
      ipv4 {
        address = "dhcp"
      }
    }
  }

  lifecycle {
    ignore_changes = [
      # Allow manual disk resizes without triggering a full replacement.
      disk,
    ]
  }
}
