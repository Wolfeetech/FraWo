# FraWo Infrastruktur-Dokumentation (INFRA.md)

**Master-Kopie:** OpenClaw-Workspace `/root/.openclaw/workspace/INFRA.md` (Stand: 12.09.2026)  
Kopie im Repo: `INFRA.md`

---

## 1. Hypervisor & Nodes

| Host | IP | Hardware / Rolle | Storage / Backups |
|---|---|---|---|
| **stock-pve** | `10.1.0.128` | HP ProDesk 600 G4 Mini (am UCG Port 1) — 🟢 **Wieder online seit 13.09.2026** | PVE 8.2, 15 GiB RAM (4,8G belegt), Thin-Pool `data` (54%), Tailscale `100.91.20.116`. |
| **anker-pve** | `10.1.0.92` | Lenovo ThinkCentre M720q (Anker-Server) — **Trägt gesamten Kernbetrieb** | Proxmox VE 8, ZFS Mirror `anker-backup` (1,7 TB frei), Thin-Pool `data` (65%), rclone GDrive. |
| **pbs-frawo** | `10.1.0.7` | Proxmox Backup Server (VM 240 auf anker-pve) | Tägliche PBS-Snapshots & vzdump um 04:00 Uhr nach Google Drive (`daily-all-pbs`). |
| **StudioPC** | `10.1.0.211` | Windows 11 Workstation | UltraVNC (Port 5900), Tailscale `100.98.31.60`. |
| **UCG Ultra** | `10.1.0.1` | UniFi Cloud Gateway (Router/Firewall) | Port 1: stock-pve, Port 2: AC Mesh, Port 3: StudioPC, Port 4: anker-pve, Port 5: WAN1 (FritzBox). |

---

## 2. Aktive Container & Virtual Machines

| VMID | Host | Name | IP | Port(s) | Zweck & Service |
|---|---|---|---|---|---|
| **101** | stock-pve | `adguard` | `10.1.0.52` | 53 (DNS), 3000 (Web) | Primärer DNS-Server (ProDesk) |
| **101** | anker-pve | `adguard-slave` | `10.1.0.27` | 53 (DNS), 3000 (Web) | Sekundärer DNS-Server (Anker) |
| **106** | anker-pve | `wireguard` | `10.1.0.239` | 51820 | VPN Gateway (aus ProDesk-PBS wiederhergestellt) |
| **108** | anker-pve | `vaultwarden` | `10.1.0.95` | 80 / 443 | SSOT für alle Passwörter & Tokens (`vault.frawo.tech`) |
| **110** | anker-pve | `n8n / paperless` | `10.1.0.100` | 5678 / 8000 | Workflows & Paperless-ngx (`paperless.frawo.tech`), 192 Dokumente |
| **130** | anker-pve | `radio-node` | `10.1.0.200` | 9500 | Docker: Radio-Backend, PostgreSQL, Redis |
| **140** | anker-pve | `frawotech-web` | `10.1.0.112` | 8069 (Odoo 19), 80/443 (Nginx) | ERP, CRM, Touch Cockpit, Cloudflare-Tunnel |
| **150** | anker-pve | `openclaw` | `10.1.0.31` | 19001 (Servassi-Hook), 19000 (Gateway) | **Jarvis** (Persistenter Koordinator & Monitoring-Empfänger) |
| **155** | anker-pve | `monitoring-stack` | `10.1.0.35` | 9090 (Prom), 9093 (Alert), 3000 (Grafana) | Prometheus, Alertmanager, Grafana (ex CT150 auf ProDesk) |
| **120** | stock-pve | `fileserver` | `10.1.0.94` | 445 (SMB) | Samba Fileserver, Musikarchiv (`//10.1.0.94/music`, 1.9 TB) |
| **210** | stock-pve | `azuracast-vm` | `10.1.0.38` | 8000 (Icecast), 80 / 443 | Webradio FraWo Funk (`funk.frawo.tech`), AutoDJ, Liquidsoap |
| **210** | anker-pve | `haos` | `10.1.0.40` | 8123 (Home Assistant) | Hausautomation Rothkreuz, Lovelace Touch Dashboard |
| **240** | anker-pve | `PBS-FraWo` | `10.1.0.7` | 8007 (PBS API/Web) | Proxmox Backup Server |
| **300** | anker-pve | `nextcloud` | `10.1.0.21` | 80 / 443 | Cloud Storage (`cloud.frawo.tech`) |
| **360** | stock-pve | `homeassistant-eltern` | `10.1.0.248` | 8123 (Home Assistant) | **Smart Home Alois (Stockenweiler)** — aktiv, WireGuard-VPN nach `192.168.178.0/24` |
| **—** | OptiPlex 7050 | `frawo-ai-worker` | `10.1.0.227` / `10.0.0.227` | 11434 (Ollama) | **FraWo On-Premises KI (24/7 Mitarbeiter, Employee #13)** — Qwen 2.5 7B (`frawo-mitarbeiter`) & 3B (`frawo-mitarbeiter-fast`), persistently resident in RAM |

### Hinweise zu Speichermounts & Radio
- **AzuraCast VM 210/220 (`10.1.0.38`):** Bind-Mount `/mnt/library` (`//10.1.0.94/music`) mit `:rslave`. In AzuraCast-Konfiguration muss `enable_auto_cue: false` bleiben, da synchrone Lautheitsanalysen über CIFS das 29s-Liquidsoap-Timeout überschreiten.

---

## 3. Hochverfügbarkeit, Daemons & Sicherheitsnetze

1. **Backup-TÜV (`frawo-backup-tuev`):**
   - **Service & Timer:** `frawo-backup-tuev.timer` auf `anker-pve` (täglich 08:00 CEST)
   - **Skript:** `/usr/local/bin/frawo-backup-tuev.sh` (Repo: `scripts/frawo-backup-tuev.sh`)
   - **Prüfumfang:** 5/5 Kern-Sicherungen (Odoo lokal, Odoo Cloud gcrypt entschlüsselt gegengelesen, Gäste-Cloud, ZFS-Mirror, PBS)
   - **Alarmierung:** Textfile-Collector Metrik für Prometheus + Telegram-Morgenbriefing via `@Frawo_bot` an Wolf
2. **Odoo Restore-Test (`frawo-odoo-restore-test`):**
   - **Service & Timer:** `frawo-odoo-restore-test.timer` auf `anker-pve` (sonntags 09:00 CEST)
   - **Skript:** `/usr/local/bin/odoo-restore-test.sh` (Repo: `scripts/odoo-restore-test.sh`)
   - **Funktion:** Testet echten SQL-Abzug via Streaming-Pipeline in temporäre Einweg-DB in CT140 Postgres, verifiziert 800 Tabellen und 6 Kern-Tabellen.
3. **Wache über die Überwachung (`frawo-wache`):**
   - **Cron:** `/etc/cron.d/frawo-wache` auf `anker-pve` (alle 10 Minuten)
   - **Skript:** `/usr/local/bin/monitoring-watchdog.sh`
   - **Funktion:** Prüft von außen, ob Prometheus, Alertmanager und Grafana auf CT155 antworten. `absent()`-Regel in Prometheus sichert gegen stillen Ausfall.
4. **Paperless Ingest & Triage:**
   - **Service & Timer:** `frawo-gdrive-inbox-pull.timer` auf `anker-pve` (alle 10 Minuten)
   - **Funktion:** Holt neue Dokumente aus `gdrive:00_INBOX/_Dokumente-zur-Pruefung` via `rclone move` und schiebt sie per `pct push 110` in den Consume-Ordner von CT110.
   - **Triage-Status:** Altbestand (1066 Dateien) vollständig in `_Fotos-Videos`, `_Programme-Technik` und `_Duplikate` aufgeteilt. 0 lose Dateien im Wurzelverzeichnis.
5. **Tagesbericht an Wolf:**
   - **Odoo-Cron 44 / Server-Aktion 828:** Täglich um 12:04 CEST via Brevo-Relay per E-Mail an `wolf@frawo.tech`.
   - **Inhalt:** Tagesplan, Kalendertermine, Aufgaben nach Ort (@rk22, @villa, @stockenweiler, etc.), offene Entscheidungen, Meilensteine.

---

## 4. Rote Linien & Sicherheitsregeln

- **Shelly 10.4.0.11 (MAC `e4:b0:63:d5:66:1c`):** IT-/Netzwerk-Stromversorgung. Niemals schalten!
- **Secrets:** Nur Vaultwarden (`vault.frawo.tech`). Keine Klartext-Secrets in Commits, Chats oder Scratch-Dateien.
- **WIP-Disziplin:** Max. 6 Aufgaben gleichzeitig in `🚀 In Arbeit` über alle FraWo-Kernprojekte.
- **Peer-Review (Vier-Augen-Prinzip):** Änderungen an Produktiv-Services oder Kern-Configs erfordern Odoo-Chatter-Gegenprüfung durch einen zweiten Agenten.
