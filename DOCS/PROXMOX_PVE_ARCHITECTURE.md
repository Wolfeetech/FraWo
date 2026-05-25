# Proxmox VE (PVE) Architecture - Anker-PVE

**Stand:** Mai 2026
**Host:** Anker-PVE
**IP (Tailscale):** `100.69.179.87`
**Standard IP:** `10.4.0.92` (Management-Netzwerk)
**SSH:** Authentifizierung via `pve_ed25519` Key

Dieses Dokument beschreibt die aktuelle Hypervisor- und Gast-Architektur des `anker-pve` Hosts basierend auf dem Echtzeit-Status der Systemkonfiguration.

---

## 1. Storage-Konfiguration

Der Proxmox Host nutzt verschiedene Storage-Pools zur Bereitstellung von Disks für VMs und Container sowie für Backups.

- **`local` (Directory, ext4 auf `/var/lib/vz`)**: Speichert ISOs, Container-Templates (vztmpl) und einige Root-Disks. Aktuell 33G / 68G genutzt.
- **`local-lvm` (LVM-Thin)**: Der schnelle primäre Speicher für System-Disks (z.B. Odoo, HAOS, Toolbox).
- **`ssd2tb` (Directory, auf `/mnt/ssd2tb`, 1.8 TB NVMe/SSD)**: Hauptspeicher für ressourcenintensive Systeme. Hostet die neuen, produktiven VMs (Nextcloud 300, Paperless 330), den PBS (240) und die Radio-Node (130).
- **`music_ssd` (Directory, auf `/mnt/music_ssd`, 1 TB)**: Mount für Musikdaten und Radio-Library (983 GB Kapazität).
- **`google-drive` (Directory, auf `/mnt/google-drive`)**: Rclone Mount für Cloud-Backups.
- **`stockenweiler-data` (NFS)**: Remote-Storage am Standort Stockenweiler (`100.91.20.116`). 
- **`pbs-usb` (Directory)**: Lokaler Mount für den Proxmox Backup Server (USB-Datenträger).

---

## 2. Netzwerk-Konfiguration

- **`vmbr0`**: Die zentrale Bridge. Bindet an den physischen Port `nic0` und bezieht im Host-System ihre IP dynamisch.
- Die VMs und Container sind an `vmbr0` angeschlossen und nutzen IP-Adressen aus dem internen Subnetz (z.B. `10.4.0.0/24`), welches vom UCG-Gateway (`10.4.0.1`) verwaltet wird.

---

## 3. Aktive Virtual Machines (VMs)

| VMID | Name          | Status   | RAM (MB) | IP               | Storage / Bemerkung                                    |
| ---- | ------------- | -------- | -------- | ---------------- | ------------------------------------------------------ |
| 210  | haos          | Running  | 2048     | (dhcp/mac)       | Home Assistant OS (Root-Disk auf `local-lvm`)         |
| 220  | odoo          | Running  | 4096     | 10.4.0.22        | Odoo 17 / Website (Root-Disk auf `local-lvm`)          |
| 240  | PBS-FraWo     | Running  | 2048     | 10.4.0.25        | Proxmox Backup Server (Disks auf `ssd2tb`)             |
| 300  | nextcloud     | Running  | 3072     | 10.4.0.21        | **Neue Instanz** (ersetzt VM 200, auf `ssd2tb`)        |
| 330  | paperless     | Running  | 3072     | 10.4.0.23        | **Neue Instanz** (ersetzt VM 230, auf `ssd2tb`)        |

*Historie: Die Legacy-VMs 200 (Nextcloud) und 230 (Paperless) sind gestoppt und wurden durch die leistungsfähigeren VMs 300 und 330 auf dem neuen `ssd2tb` Storage abgelöst.*

---

## 4. Aktive LXC Container (CTs)

| CTID | Name          | Status  | RAM (MB) | IP               | Funktion / Besonderheiten                              |
| ---- | ------------- | ------- | -------- | ---------------- | ------------------------------------------------------ |
| 100  | toolbox       | Running | 1024     | 10.4.0.20        | Frontdoor (Caddy Reverse Proxy, AdGuard, Jellyfin)     |
| 101  | adguard-slave | Stopped | 512      | 10.1.0.101       | Redundanter DNS-Node                                   |
| 110  | storage-node  | Running | 1024     | 10.4.0.30        | SMB/NFS Share. Bind-Mount auf Google Drive Backup      |
| 120  | vaultwarden   | Running | 1024     | 10.4.0.26        | Bitwarden / Vaultwarden Passwortmanager                |
| 130  | radio-node    | Running | 2048     | dhcp             | AzuraCast / Radio-Dienste. (Mount: `music_ssd`)        |

---

## 5. Security & Isolation

- **CT 100 (toolbox)**: Unprivileged Container. Fungiert als Tailscale Access-Node und Caddy Reverse Proxy, bildet somit die alleinige Ingress-Frontdoor für interne Dienste.
- **VM-Firewalls**: Auf den VMs Odoo (220) und HAOS (210) wurde die Proxmox VM-Firewall in der Konfiguration deaktiviert (`firewall=0`). Hintergrund ist ein bekannter Bug mit asymmetrischem Routing (conntrack) zwischen CT 100 (veth) und den VMs (tap). Die Absicherung erfolgt stattdessen über OS-Level Firewalls (z.B. UFW auf der Odoo-VM) und die übergeordnete Unifi-Gateway Firewall.
- **Host-Zugriff**: Der Proxmox Host hat keine Dienste öffentlich im Internet exponiert. Administrativer Zugriff ist nur via internem LAN oder Tailscale-VPN (`100.69.179.87`) möglich.
