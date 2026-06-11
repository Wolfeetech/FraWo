> ⚠️ **TEILWEISE VERALTET.** Aktueller Live-Stand: **[NOW.md](NOW.md)**. Kern-Korrekturen: frawo-docker-1 = VMware-VM auf **Flos** Host (kein HW-Zugriff; Wolfs Eltern = Testkunden). Echte Subnetze: Rothkreuz 10.1.0.0/24 + 10.3.0.0/24 (Radio-DMZ), Stockenweiler-ESXi 10.30.8.0/24, ProDesk/Easybox 192.168.2.0/24 (NICHT 10.4.0.x). Domain = **frawo.tech** (nicht frawo-tech.de).

# LIVE CONTEXT — FraWo GbR Infrastruktur
**Single Source of Truth für technischen Zustand**
*Letzte vollständige Aktualisierung: 2026-05-31 — Claude Sonnet 4.6 + Wolf*

---

## ARCHITEKTUR-ÜBERSICHT

```
┌─────────────────────────────────────────────────────────────┐
│                    TAILSCALE MESH (VPN)                      │
│         Alle Nodes sicher verbunden, kein offener Port       │
└──────────────┬──────────────────────┬───────────────────────┘
               │                      │
    ┌──────────▼──────────┐  ┌────────▼──────────────────────┐
    │   ANKER PVE          │  │  STOCKENWEILER (Site B)        │
    │   10.4.0.99          │  │  Netz: 10.30.8.x (Container)  │
    │   Tailscale:         │  │  PVE: EINGESTELLT              │
    │   100.69.179.87      │  │                                │
    │   PRIMARY PRODUCTION │  │  frawo-docker-1 (10.30.8.22)  │
    └──────────┬──────────┘  │  Tailscale: 100.94.32.41      │
               │             │  Debian 13, 188G, SSH ✅       │
    [VMs/CTs]  │             │  Rolle: TBD (Monitoring/Backup)│
               │             │                                │
               │             │  win-j1aenasv2fj (10.30.8.21) │
               │             │  Tailscale: 100.97.147.67      │
               │             │  Windows, Claude Code ✅        │
               │             └────────────────────────────────┘
```

---

## NODE-ROLLEN (verbindlich)

### ANKER PVE — Primäre Produktion
**IP**: `10.4.0.99` | **Tailscale**: `100.69.179.87` | **PVE**: 9.1.19, Kernel 7.0.2-6-pve

| ID | Name | IP | Rolle | Status |
|----|------|----|-------|--------|
| VM 210 | haos | 10.4.0.24 | Home Assistant OS (FraWo intern) | ✅ running |
| VM 240 | PBS-FraWo | 10.4.0.25 | Proxmox Backup Server 4.2, Datastore 500GB, Backup 02:00, Cloud-Sync 05:00 | ✅ running |
| VM 300 | nextcloud | 10.4.0.21 | Nextcloud + DB + Redis | ✅ running |
| VM 330 | paperless | 10.4.0.23 | Paperless-ngx + Tika + Gotenberg | ✅ running |
| CT 100 | toolbox | 10.4.0.20 | Caddy · Uptime Kuma · Jellyfin · AdGuard · Open-WebUI | ✅ running |
| CT 101 | adguard-slave | 10.4.0.101 | AdGuard Home (Slave/Backup) | ✅ running |
| CT 110 | storage-node | 10.4.0.30 | CIFS/Samba (media + docs) | ✅ running |
| CT 120 | vaultwarden | 10.4.0.26 | Vaultwarden (Bitwarden-kompatibel) | ✅ running |
| CT 130 | radio-node | **10.4.0.28** | AzuraCast (port 80/443/8000) + Navidrome (port 4533) + Samba music-share + Radio Backend API (port **9500**) + **funk-community Site (port 9501)** — V1 deployed 2026-06-01: DSGVO Donation-Flow, Supporter-Beitrag (Trinkgeld), System-Chat, Redis Rate-Limiting, Admin-Key Auth | ✅ running, RAM 6GB, **Tailscale: 100.78.88.33** ✅ |
| VM 220 | odoo | 10.4.0.22 | Odoo 17 ERP only (AzuraCast abgeschaltet ✅) | ✅ running, restart=unless-stopped, startup order=3 |

### STOCKENWEILER — Site B (Schiffscontainer, 10.30.8.x)
**Stockenweiler PVE: EINGESTELLT** (ersetzt durch frawo-docker-1)

| Name | Tailscale | Lokal-IP | OS | Rolle | Status |
|------|-----------|---------|-----|-------|--------|
| frawo-docker-1 | 100.94.32.41 | 10.30.8.22 | Debian 13 Trixie | **n8n (5678)** + **Portainer (9000)** + **Grafana (3001)** + **Prometheus (9091)** + Node-Exporter (9100) + Icecast-Relay (TODO #242), 31GB RAM, 173G frei | ✅ SSH via Key (pw: vault!), PasswordAuth deaktiviert |
| win-j1aenasv2fj | 100.97.147.67 | 10.30.8.21 | Windows | Management-PC, SSH-Bridge, Claude Code | ✅ |

**HAOS Eltern** (lief auf eingestelltem PVE): Neue Heimat TBD — Option frawo-docker-1 (Task #241)

**frawo-docker-1 Dienste** (Stand 2026-05-26):
- n8n Workflow Automation (Port 5678, Docker, /home/wolf/n8n/) — Task #245 ✅
- Portainer CE (Port 9000/9443, /home/wolf/stacks/infra/) ✅
- Grafana (Port 3001, PW: FrawoGrafana2026!, /home/wolf/stacks/monitoring/) ✅
- Prometheus (Port 9091, /home/wolf/stacks/monitoring/) ✅
- Node Exporter (Port 9100) ✅
- Icecast-Relay (Port 8000, /home/wolf/stacks/icecast-relay/) ✅ LIVE — relay von CT 130 via Tailscale 100.78.88.33

**frawo-docker-1 Tailscale** (nach nächstem CT 130 Neustart):
- tailscaled installiert auf CT 130 (PVE TUN-Feature aktiviert)
- Wolf muss auf tailscale.com/admin das neue Device genehmigen
- Dann: frawo-docker-1 kann direkt CT 130:8000 via Tailscale erreichen

### ENTWICKLUNGSMASCHINEN (keine Produktion)
| Name | Tailscale | Netzwerk | Rolle |
|------|-----------|---------|-------|
| wolfstudiopc | 100.98.31.60 | 10.1.0.210 (alt!) | Dev-Workstation, lokales Docker-Testing |
| wolf-surface | 100.79.103.59 | - | Mobile Dev |
| wolf-zenbook | 100.76.249.126 | - | Linux Dev |
| surface-go-frontend | 100.106.67.127 | - | Frontend-Entwicklung |
| wolf-admin-pc | TBD | Admin-PC | Ops-PC (dieser PC), frisch eingerichtet 2026-05-30, SSH-Key `hs27_ops_ed25519` generiert, deployment ausstehend |

---

## ÖFFENTLICHE DIENSTE

| URL | Status | Backend |
|-----|--------|---------|
| https://www.frawo-tech.de | ✅ HTTP 200 | CF-Tunnel → 10.4.0.22 (Odoo) |
| https://frawo-tech.de | ✅ HTTP 200 | CF-Tunnel → 10.4.0.22 (Redirect zu www) |
| https://cloud.frawo-tech.de | ✅ | CF-Tunnel → 10.4.0.21 (Nextcloud) |
| https://funk.frawo-tech.de | ✅ HTTP 200 | CF-Tunnel → **100.78.88.33:9501** (funk-community Site CT 130) |
| https://navidrome.frawo-tech.de | ✅ HTTP 200 | CF-Tunnel → **100.78.88.33:4533** (Navidrome CT 130) |
| https://home.frawo-tech.de | ✅ | CF-Tunnel → 10.4.0.24:8123 (HAOS) |
| https://vault.frawo-tech.de | ✅ | CF-Tunnel → 10.4.0.26:8080 (Vaultwarden) |
| https://odoo.frawo-tech.de | ✅ | CF-Tunnel → 10.4.0.22:8069 (Odoo ERP) |

**Cloudflare Tunnel**: cloudflared als systemd-Service auf **anker-pve** (100.69.179.87), Tunnel-ID `7ceb61ed-86fc-4665-80ce-d490be94dcf0`, lokale Config `/etc/cloudflared/config.yml`. Remote-Routen in Cloudflare ZT Dashboard verwaltet (remote config überschreibt lokale Ingress-Regeln). Alle CT-130-Routen via Tailscale-IP `100.78.88.33` wegen Tailscale-Routing-Table-52-Problem auf CT130.

---

## INTERNE DIENSTE (via Caddy CT 100 / AdGuard)
**Caddy läuft als Docker-Container** `toolbox-network-caddy-1` auf CT 100, Config: `/root/stacks/toolbox-network/Caddyfile`

| Domain (AdGuard) | Upstream | Status | Hinweis |
|------------------|---------|--------|---------|
| odoo.hs27.internal | 10.4.0.22:8069 | ✅ | Odoo 17 ERP |
| cloud.hs27.internal | 10.4.0.21:80 | ✅ | Nextcloud |
| paperless.hs27.internal | 10.4.0.23:8000 | ✅ | Paperless-ngx |
| vault.hs27.internal | 10.4.0.26:8080 | ✅ | Vaultwarden |
| ha.hs27.internal | 10.4.0.24:8123 | ✅ | Home Assistant (HAOS) |
| media.hs27.internal | 10.4.0.20:8096 | ✅ | Jellyfin (CT 100 lokal) |
| radio.hs27.internal | **100.78.88.33:9501** | ✅ | funk-community Site CT 130 (via Tailscale, Caddy-Route) |
| radio-node.hs27.internal | 10.4.0.28 | ✅ | Direkt-Zugriff CT 130 |
| storage-node.hs27.internal | 10.4.0.30 | ✅ | Direkt CT 110 |
| pve.hs27.internal | 10.4.0.99 | ✅ | PVE Web UI |
| adguard-slave.hs27.internal | 10.4.0.101 | ✅ | AdGuard Slave |

| navidrome.hs27.internal | 100.78.88.33:4533 | ✅ | Navidrome auf CT 130 (music_ssd, via Tailscale) |
| radio-anker.hs27.internal | 100.78.88.33:80 | ✅ | AzuraCast CT 130 (Anker-Standort, via Tailscale) |
| radio-stock.hs27.internal | 10.30.8.22:8000 | ✅ | Icecast Relay frawo-docker-1 → CT 130 via Tailscale 100.78.88.33 |
| radio-api.hs27.internal | 10.4.0.28:9500 | ✅ | FraWo Radio Backend API (FastAPI) |
| n8n.hs27.internal | 10.30.8.22:5678 | ✅ | n8n Workflow Automation (frawo-docker-1) |
| portainer.hs27.internal | 10.30.8.22:9000 | ✅ | Portainer CE (frawo-docker-1) |
| grafana.hs27.internal | 10.30.8.22:3001 | ✅ | Grafana (frawo-docker-1, PW: FrawoGrafana2026!) |
| prometheus.hs27.internal | 10.30.8.22:9091 | ✅ | Prometheus (frawo-docker-1) |

## FRAWO FUNK RADIO

**Station**: FraWo Funk — "Das Non-Stop Radio vom Bodensee." (Electronic / Alternative)
**Source**: CT 130 (radio-node, 10.4.0.28), AzuraCast `latest`
**Öffentliche Domain**: `funk.frawo-tech.de`

### Community Site (funk-community)
**Deployed**: CT 130, `/opt/funk-community/`, Port 9501, nginx-Container
**Öffentlich**: `https://funk.frawo-tech.de/` (CF-Tunnel → 100.78.88.33:9501) ✅ HTTP 200 live seit 2026-05-31
**Intern**: `http://radio.hs27.internal` (Caddy CT100 → 100.78.88.33:9501) ✅
**Features**: Now-Playing, Play/Pause Player, Voting (👍/👎), Song-Request, Community-Chat (localStorage Name)
**Backend**: radio-backend FastAPI `/api/v1/community/` (Port 9500 extern / 8000 intern)
**Source-Code**: `apps/funk-community/` (Repo), deployed via `docker compose up -d` auf CT130
**TODO**: Song-Request API via AzuraCast API-Key aktivieren (`AZURACAST_API_KEY` in `/opt/frawo-radio-backend/.env`)

### Radio-Backend API
**Deployed**: CT 130, `/opt/frawo-radio-backend/`, Port 9500 (extern) / 8000 (intern)
**Docker-Network**: `frawo-radio-backend_frawo-network` (172.21.0.0/16)
**AzuraCast-Verbindung**: `http://172.20.0.1/api` (Docker-Bridge-Gateway zu azuracast_default)
**Endpoints**: `/api/v1/community/nowplaying`, `/votes`, `/chat`, `/requests/*`, `/stations`, `/nowplaying`

| Stream | URL | Format | Bitrate |
|--------|-----|--------|---------|
| Hifi | `https://funk.frawo-tech.de/listen/frawo_funk/hifi.mp3` | MP3 | 320 kbps |
| Standard | `https://funk.frawo-tech.de/listen/frawo_funk/radio.mp3` | MP3 | 192 kbps |
| Mobile | `https://funk.frawo-tech.de/listen/frawo_funk/mobile.aac` | AAC | 64 kbps |

**Interne Icecast URLs** (direkt, kein Cloudflare):
- `http://100.78.88.33:8000/radio.mp3` (via Tailscale, 192 kbps) — LAN 10.4.0.28 nicht direkt erreichbar!
- `http://100.94.32.41:8000/radio.mp3` (Icecast-Relay frawo-docker-1)

**Relay-Architektur**:
- CT 130 = Source → frawo-docker-1 Icecast-Relay (100.94.32.41:8000) → Stockenweiler lokal ✅ LIVE
- CT 130 = Source → Raspberry Pi Icecast-Relay → Mobile Events (WiFi-Hotspot) — geplant

### Tailscale-Routing-Hinweis CT 130
CT 130 hat Tailscale-Routing-Table 52, die ALLE 10.4.0.x-Pakete über `tailscale0` leitet.
**Folge**: CT 130 ist von PVE/anderen CTs via LAN (10.4.0.28) NICHT direkt erreichbar.
**Fix**: Immer Tailscale-IP `100.78.88.33` für CT-130-Dienste verwenden (Caddy, cloudflared, etc.).

---

## STORAGE

| Pfad | Typ | Größe | Belegt | Frei | Hinweis |
|------|-----|-------|--------|------|---------|
| `/` (PVE local) | LVM | 70G | 28G | 38G | ✅ 40% |
| `/mnt/ssd2tb` | dir | 1.9T | 175G | 1.6T | ✅ 9.5% |
| `/mnt/music_ssd` | dir | 983G | 177G | 806G | ✅ 18% |
| `/mnt/hs27-media` | CIFS | 98G | 73G | 21G | ⚠️ stale (Kernel-Bug, Fix: PVE-Neustart) — Radio-Library Migration via tar-pipe läuft |
| `gdrive:` | rclone | 5.4T | 1.9T | 3.3T | ✅ 36% |
| `local-lvm` (LVM thin) | lvmthin | 164G | 2G | 162G | ✅ 1% — fast leer! |

**hs27-media Breakdown:**
- `FraWo_Radio_Library/Clean` = 63G (Radio-Library, Kern-Content)
- `FraWo_Radio_Library/Quarantine` = 5.6G (458 MP3s, abgelehnt — Wolf entscheidet)
- `yourparty_Libary` = 1.3G (YourParty eingestellt → Archivieren/Löschen)
- `Duplicates` = ✅ gelöscht (109M)

**Migration läuft**: Radio-Library (63G) via tar-pipe CT 110 → `/mnt/music_ssd/FraWo_Radio_Library/` (PVE direkt, kein PVE-Neustart nötig)

---

## EMAIL / SMTP

| Parameter | Wert |
|-----------|------|
| Server | smtp.strato.de:587 (STARTTLS) |
| User | webmaster@frawo-tech.de |
| from_filter | frawo-tech.de |
| DMARC | v=DMARC1;p=none; (heute geändert von p=reject) |
| SPF | v=spf1 include:spf.strato.de ~all ✅ |
| DKIM | nicht konfiguriert (TODO: Strato-Einstellungen) |
| Status | ✅ Email funktioniert seit heute |

---

## BEKANNTE OFFENE BAUSTELLEN

| Problem | Priorität | Fix | Wer |
|---------|-----------|-----|-----|
| cloud.frawo-tech.de | ✅ HTTP 200 | Behoben — CF Tunnel zeigt auf 10.4.0.21 | 2026-05-30 |
| funk.frawo-tech.de Community-Site | ✅ HTTP 200 | CF Tunnel → 100.78.88.33:9501, Community-Site live | 2026-05-31 |
| navidrome.frawo-tech.de | ✅ HTTP 200 | CF Tunnel → 100.78.88.33:4533 | 2026-05-31 |
| Tailscale hs27.internal DNS | 🔴 | tailscale.com/admin/dns: 10.1.0.20 → 10.4.0.20 | Wolf |
| wolf-admin-pc SSH-Key | 🔴 | Key generiert (`C:\Users\Admin\bin\hs27_ops_ed25519`), deployment pending — run `bin\setup_ssh.ps1` als Admin | Wolf |
| **Passwort-Audit** (#244) | 🔴 | Alle Credentials in Vaultwarden (vault.hs27.internal) | Wolf |
| **frawo-docker-1 Recovery** (#226) | 🔴 | GRUB Single-User-Mode → passwd wolf → SSH-Key → PasswordAuth deaktivieren | Wolf (physisch) |
| PBS VM 240 kein Netzwerk | 🟡 | PVE Web Console → VNC → IP prüfen | Wolf |
| Icecast Relay frawo-docker-1 | ✅ LIVE | radio.mp3/hifi.mp3/mobile.aac relay von CT 130 via Tailscale | Agent 2026-05-26 |
| HAOS Eltern — neue Heimat | 🟡 | frawo-docker-1 (Docker) oder verzichten? (#241) | Wolf |
| /mnt/hs27-media stale | 🟡 | PVE-Neustart (Wartungsfenster) — Radio-Library wird parallel migriert | Agent/Wolf |
| DKIM für frawo-tech.de | 🟡 | Strato-Panel → DomainKeys | Wolf |
| StudioPC auf 10.1.0.x | 🟢 | UCG DHCP-Reservation auf 10.4.0.x | Wolf |
| Odoo Admin-Passwort | 🟡 | AuditTemp2026! → permanentes Passwort (#244) | Wolf |
| **Odoo Instabilität** | ✅ FIXED | restart=unless-stopped + PVE startup order=3 | Agent 2026-05-26 |

---

## NETZWERK HINWEISE

- **StudioPC** Tailscale zeigt `direct 10.1.0.210:41641` — noch auf altem Subnetz, nicht 10.4.0.x
- **UDP Port Exhaustion**: Dual-Gateway (WLAN Easybox 192.168.2.1 + LAN UCG 10.4.0.1) → Registry-Fix ausstehend:
  ```powershell
  Set-ItemProperty -Path 'HKLM:\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters' -Name 'MaxUserPort' -Value 65534 -Type DWord
  Set-ItemProperty -Path 'HKLM:\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters' -Name 'TcpTimedWaitDelay' -Value 30 -Type DWord
  ```

---

## NETZWERK HINWEIS — frawo-docker-1
- **Stockenweiler-Subnet**: 10.30.8.x (eigenes, nicht 192.168.178.x Eltern-Haus)
- **SSH via Passwort**: vom Stockenweiler-PC (10.30.8.21) direkt erreichbar
- **Via Tailscale**: 100.94.32.41, via StudioPC Tailscale direkt SSH möglich sobald Key deployed
- **apt-cdrom**: Warnung beim Update (DVD-Source in sources.list) — ignorierbar, internet-Repos funktionieren

*Updated: 2026-05-31 — Claude Sonnet 4.6 + Wolf*
