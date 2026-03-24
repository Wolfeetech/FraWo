# ---------------------------------------------------------------------------
# modules/lxc/main.tf – Proxmox LXC container resource (bpg/proxmox provider)
# ---------------------------------------------------------------------------

resource "proxmox_virtual_environment_container" "this" {
  vm_id        = var.lxc_id
  description  = var.description
  node_name    = var.node_name
  unprivileged = var.unprivileged
  started      = var.started

  initialization {
    hostname = var.hostname

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

  cpu {
    cores = var.cores
  }

  memory {
    dedicated = var.memory_mb
  }

  disk {
    datastore_id = var.storage_id
    size         = var.disk_size_gb  # integer GiB – bpg/proxmox provider native format
  }

  network_interface {
    name    = "eth0"
    bridge  = var.bridge
    vlan_id = var.vlan_tag
  }

  operating_system {
    template_file_id = var.os_template
    type             = "debian"
  }

  lifecycle {
    ignore_changes = [
      # Allow manual disk resizes without triggering a full replacement.
      disk,
    ]
  }
}
