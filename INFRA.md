# FraWo Infrastruktur-Dokumentation (INFRA.md)

**Master-Kopie:** OpenClaw-Workspace `/root/.openclaw/workspace/INFRA.md` (Stand: 2026-09-06)

---

## 1. Hypervisor & Nodes

| Host | IP | Hardware / Rolle | Storage / Backups |
|---|---|---|---|
| **stock-pve** | `10.1.0.128` | HP ProDesk 600 G4 (Stockenweiler) | Proxmox VE 8, /mnt/data_family, /mnt/music_hdd |
| **anker-pve** | `10.1.0.92` | Anker Server | Proxmox VE 8, ZFS Mirror `anker-backup`, rclone GDrive |
| **pbs-frawo** | `10.1.0.7` | Proxmox Backup Server (VM 240) | Tägliche PBS-Snapshots um 04:00 Uhr |
| **StudioPC** | `10.1.0.211` | Windows 11 Workstation | UltraVNC (Port 5900, Monitor 2 extended workspace) |
| **UCG Ultra** | `10.1.0.1` | UniFi Cloud Gateway (Router/FW) | VLAN 1 (Server), VLAN 4 (IoT `10.4.0.0/24`) |

---

## 2. Container & Virtual Machines

| VMID | Host | Name | IP | Port(s) | Zweck & Service |
|---|---|---|---|---|---|
| **101** | stock-pve | `adguard` | `10.1.0.52` | 53 (DNS), 300 (Web), 8080 (Sync API) | **Primärer DNS-Server** + `adguardhome-sync.service` (Master) |
| **101** | anker-pve | `adguard-slave` | `10.1.0.27` | 53 (DNS), 3000 (Web) | **Sekundärer DNS-Server** (Replica, kontinuierlich synchronisiert) |
| **106** | stock-pve | `wireguard` | `10.1.0.x` | 51820 | VPN Gateway |
| **108** | stock-pve | `vaultwarden` | `10.1.0.95` | 80 / 443 | SSOT für alle Passwörter & Tokens (`vault.frawo-tech.de`) |
| **110** | stock-pve | `n8n / paperless` | `10.1.0.96` | 5678 / 8000 | Workflows & Dokumentenarchiv |
| **120** | stock-pve | `fileserver` | `10.1.0.120` | Samba / NFS | Musik- und Datenfreigaben |
| **140** | stock-pve | `frawotech-web` | `10.1.0.112` | 8069 (Odoo 19), 80/443 (Nginx) | ERP, CRM, Touch Cockpit (`/frawo/touch/cockpit`), Auto-Login |
| **150** | stock-pve | `monitoring-stack` | `10.1.0.35` | 9090 (Prom), 9093 (Alert), 3000 (Grafana), 9115 (Blackbox) | Prometheus Monitoring, Alertmanager |
| **130** | anker-pve | `radio-node` | `10.1.0.38` | 8000 (Icecast), 80/443 (AzuraCast) | Funk FraWo Web-Radio (`funk.frawo-tech.de`) |
| **150** | anker-pve | `openclaw` | `10.1.0.31` | 19001 (Servassi-Hook), 18789 (OpenClaw) | **Jarvis** (Persistenter Koordinator & Monitoring-Empfänger) |
| **210** | anker-pve | `haos` | `10.1.0.40` | 8123 (Home Assistant) | Hausautomation, Lovelace Touch Dashboard (`/jarvis-touch`) |
| **240** | anker-pve | `PBS-FraWo` | `10.1.0.7` | 8007 (PBS API/Web) | Proxmox Backup Server |

---

## 3. Hochverfügbarkeit, Synchronisation & Daemons

1. **DNS Replikation (`adguardhome-sync`):**
   - **Service:** `adguardhome-sync.service` auf ProDesk CT101 (`10.1.0.52`)
   - **Takt:** Alle 15 Minuten (Cron) + sofortiger Sync bei Service-Start
   - **Umfang:** DNS-Rewrites, User Rules, Sperrlisten, Filterlisten, Client-Einstellungen
   - **API-Port:** `http://10.1.0.52:8080/api/v1/status`
2. **Kiosk-Display & Touch-Steuerung:**
   - **Host:** ProDesk (`10.1.0.128`) `tty2`
   - **X11-Daemon:** `onboard --layout Compact --theme Nightshade`
   - **Browser:** Chromium Fullscreen auf `http://10.1.0.40:8123/jarvis-touch/home`
3. **Backup-Zeitplan (3-2-1):**
   - **04:00 Uhr:** PBS-Backup aller VMs/CTs nach `pbs-frawo` (`10.1.0.7`)
   - **04:00 Uhr:** Offsite rclone Cloud-Backup nach Google Drive
   - **05:30 Uhr:** Lokales VZDump-HDD-Fallback auf `/mnt/data_family/proxmox_backups`
4. **Paperless Dokumenten-Ingest (`frawo-paperless-ingest`):**
   - **Service:** `frawo-paperless-ingest.timer` auf CT110 (`10.1.0.96`)
   - **Takt:** Alle 10 Minuten
   - **Umfang:** `rclone move` aus `gdrive:00_INBOX/_Dokumente-zur-Pruefung` direkt nach `/opt/paperless/consume` mit automatischer Rechtekorrektur (UID 1000)
   - **Owner:** Antigravity / Jarvis (erledigt Task #1363, ersetzt toten ProDesk-Webhook)

---

## 4. Rote Linien & Sicherheitsregeln

- **Shelly 10.4.0.11 (MAC `e4:b0:63:d5:66:1c`):** IT-/Netzwerk-Stromversorgung. In Home Assistant Entity gesperrt (`disabled_by=user`). Niemals schalten!
- **Secrets:** Nur Vaultwarden (`vault.frawo-tech.de`). Keine Klartext-Secrets in Commits, Chats oder Scratch-Dateien.
- **Peer-Review:** Änderungen an Produktiv-Services oder Configs erfordern Vier-Augen-Freigabe im Odoo-Chatter.
