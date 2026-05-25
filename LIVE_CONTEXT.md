# LIVE CONTEXT

## Infrastructure Status & Governance (2026-05-25)

- **Status**: **ANKER OPERATIONAL — VOLLSTÄNDIG AUDITIERT**. Stockenweiler weiterhin offline.
- **Letzter Audit**: 2026-05-25 11:30–12:10 Europe/Berlin (Claude Sonnet 4.6 + Wolf)
- **Heute behoben**: Odoo VM eingefroren → Force-Restart → SSH-Config-Fix → Swap angelegt → Zombie-Container entfernt

---

## KRITISCHE PROBLEME

### 🔴 1. cloud.frawo-tech.de → 502 (Cloudflare Tunnel falsche IP)
- **Ursache**: Cloudflared-Tunnel-Ingress zeigt auf alte IP `10.1.0.21` (alt: `10.1.0.x`-Subnetz)
- **Korrekt wäre**: `http://10.4.0.21` (Nextcloud VM 300, aktuelles `10.4.0.x`-Subnetz)
- **Fix**: Cloudflare Dashboard → Zero Trust → Tunnels → Ingress Rule für `cloud.frawo-tech.de` auf `http://10.4.0.21` ändern (Wolf, manuell)
- **Nextcloud selbst**: Läuft einwandfrei (intern HTTP 302 ✓, VM up 22h)

### 🔴 2. Stockenweiler PVE — physisch offline
- **Tailscale**: `100.91.20.116` — offline, last seen **15 Tage** vor Audit
- **Benötigt**: Physischer Besuch in Rothkreuz zum Einschalten
- **Blockiert**: Lane D (Radio/HA), Lane E (AzuraCast Migration)
- **Hinweis**: AzuraCast läuft aktuell provisorisch auf VM 220 (Odoo VM) — Ziel ist CT 130 (radio-node)

### ⚠️ 3. hs27-media NFS-Share: 80% voll
- **Mount**: `/mnt/hs27-media` auf Anker PVE (gemountet vom Storage-Node CT 110)
- **Belegung**: 78G / 98G → **nur noch 20G frei**
- **Aktion**: Alte Mediendateien aufräumen oder NFS-Share erweitern

### ⚠️ 4. Anker PVE RAM: hoch
- **RAM**: 10GB / 15GB genutzt, Swap: 3.5GB / 8GB aktiv
- **Ursache**: Viele VMs/CTs gleichzeitig aktiv (5 VMs + 5 CTs)
- **Aktion**: PBS-VM (240) RAM-Bedarf prüfen; ggf. VMs mit niedrigerem Bedarf trimmen

---

## ANKER — ALLE SERVICES (Stand: 2026-05-25)

### PVE Node
- **Version**: PVE 9.1.19, Kernel 7.0.2-6-pve
- **Uptime**: 1 Tag 1:14
- **IP**: `10.4.0.92` / Tailscale `100.69.179.87`

### VMs
| VMID | Name | Status | RAM | Disk | Dienste |
|------|------|--------|-----|------|---------|
| 210 | haos | ✅ running | 2GB allok. | 32GB | Home Assistant OS |
| 220 | odoo | ✅ running | 2.4/2.9GB | 39% (12G/32G) | Odoo 17, PostgreSQL 15, AzuraCast (provisorisch) |
| 240 | PBS-FraWo | ✅ running | 2GB allok. | 32GB | Proxmox Backup Server |
| 300 | nextcloud | ✅ running | 582MB/1.9GB | 16% (4.6G/32G) | Nextcloud + DB + Redis |
| 330 | paperless | ✅ running | 1.2/1.9GB | 27% (8G/32G) | Paperless-ngx + Tika + Gotenberg + DB |

### LXC Container
| CTID | Name | Status | Dienste |
|------|------|--------|---------|
| 100 | toolbox | ✅ running | Caddy, Uptime Kuma, Jellyfin, AdGuard, Open-WebUI, cloudflared |
| 101 | adguard-slave | ✅ running | AdGuard Home (Slave) |
| 110 | storage-node | ✅ running | NFS/Storage Services |
| 120 | vaultwarden | ✅ running | Vaultwarden (Bitwarden-kompatibel) |
| 130 | radio-node | ✅ running | AzuraCast (Ziel, aktuell noch leer) |

### Storage (Anker PVE)
| Pfad | Größe | Belegt | Frei | Status |
|------|-------|--------|------|--------|
| `/` (PVE root, ssd2tb LVM) | 68G | 28G | 38G | ✅ 43% |
| `/mnt/ssd2tb` | 1.8T | 175G | 1.6T | ✅ 11% |
| `/mnt/music_ssd` | 983G | 177G | 806G | ✅ 18% |
| `/mnt/hs27-media` (NFS) | 98G | 78G | 21G | ⚠️ 80% |
| `gdrive:` (rclone) | 5.1T | 1.9T | 3.3T | ✅ 37% |

---

## TOOLBOX (CT 100) — Service Details

- **IP**: `10.4.0.20` / Tailscale `100.82.26.53`
- **Disk**: 13G / 23G (60%) ⚠️
- **Containers**:
  - `toolbox-network-caddy-1` — Up 5 Wochen, Config ✅ valid
  - `uptime-kuma` — Up 5 Wochen (healthy) ✅
  - `jellyfin` — Up 5 Wochen (healthy) ✅
  - `toolbox-network-adguard-1` — Up 5 Wochen ✅
  - `open-webui` — Up 5 Wochen (healthy) ✅
- **cloudflared**: aktiv (systemd), Tunnel-Token konfiguriert

---

## ODOO VM (220) — Heute gefixt

- **IP**: `10.4.0.22` / User `wolf`
- **SSH**: jetzt auf `0.0.0.0:22` (war: nur `127.0.0.1` — altes `10.1.0.x`-Config-Artifact)
- **Swap**: 2GB angelegt und in `/etc/fstab` eingetragen (war: kein Swap → OOM-Kill Risiko)
- **Zombie-Container**: `edge_web_1` und `edge_db_1` entfernt
- **Odoo**: HTTP 200 ✅, DB `FraWo_GbR` ✅
- **Root-Cause des Einfrierens**: Wahrscheinlich OOM-Kill bei vollem RAM (kein Swap) → alle Prozesse frozen, SSH-Daemon abgestürzt

---

## ÖFFENTLICHE FRONTDOORS (Stand: 2026-05-25)

| URL | Status | Anmerkung |
|-----|--------|-----------|
| `https://www.frawo-tech.de` | ✅ HTTP 200 | Odoo Website via Cloudflare |
| `https://frawo-tech.de` | ✅ HTTP 200 | Redirect zu www |
| `https://cloud.frawo-tech.de` | 🔴 HTTP 502 | CF-Tunnel zeigt auf alte IP 10.1.0.21 |
| `https://odoo.frawo-tech.de` | ❓ nicht konfiguriert | |
| `https://docs.frawo-tech.de` | ❓ nicht konfiguriert | |

## INTERNE FRONTDOORS (via Caddy auf Toolbox, :84xx)

| Host / Port | Upstream | Status |
|-------------|----------|--------|
| `odoo.hs27.internal` / `:8444` | `10.4.0.22:8069` | ✅ HTTP 200 |
| `cloud.hs27.internal` / `:8445` | `10.4.0.21:80` | ✅ HTTP 302 (intern OK) |
| `paperless.hs27.internal` / `:8446` | `10.4.0.23` | läuft |
| `vault.hs27.internal` / `:8442` | `10.4.0.26:8080` | ⚠️ Backend prüfen |
| `ha.hs27.internal` / `:8443` | HAOS | ⚠️ IP prüfen |
| `media.hs27.internal` / `:8449` | Jellyfin (Toolbox) | ✅ |

---

## NETZWERK-HINWEIS (StudioPC)

- **UDP Port Exhaustion (Event 4266)**: Durch Dual-Gateway (WLAN Easybox `192.168.2.1` + LAN UCG `10.4.0.1`) und VPN-Flapping
- **Empfehlung** (Admin-Terminal, noch ausstehend):
  ```powershell
  Set-ItemProperty -Path 'HKLM:\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters' -Name 'MaxUserPort' -Value 65534 -Type DWord
  Set-ItemProperty -Path 'HKLM:\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters' -Name 'TcpTimedWaitDelay' -Value 30 -Type DWord
  ```

---

## OFFENE BAUSTELLEN — frawo-docker-1 & StudioPC

- **frawo-docker-1** (`100.94.32.41`): Tailscale-Node vorhanden, SSH-Key nicht hinterlegt → Rolle/Zweck unklar, muss in Gesamtarchitektur eingeordnet werden
- **StudioPC** (wolfstudiopc): Docker läuft, aber nur gestoppte Dev-Container (YourParty). Keine aktiven Services. Rolle als SSH-Bridge und lokaler Docker-Host nach Best Practice definieren.
- **→ Aktion**: Beide Nodes gemeinsam mit Wolf nach Best Practice in die Infrastruktur einordnen

---

## WORKSPACE STATUS

- Operator: **Wolf**
- Working path: `C:\Users\StudioPC\OneDrive\Dokumente\GitHub\FraWo`
- Git: main branch
- SSH Key: `hs27_ops_ed25519` (Anker/VMs), `pve_ed25519` (Anker PVE root)

---

*Updated: 2026-05-25 12:10 Europe/Berlin*
*Audit durchgeführt von: Claude Sonnet 4.6 + Wolf*
