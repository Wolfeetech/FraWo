# LIVE CONTEXT — FraWo GbR Infrastruktur
**Single Source of Truth für technischen Zustand**
*Letzte vollständige Aktualisierung: 2026-05-25 — Claude Sonnet 4.6 + Wolf*

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
| VM 240 | PBS-FraWo | 10.4.0.25 (konfiguriert) | Proxmox Backup Server | ⚠️ kein Netzwerk |
| VM 300 | nextcloud | 10.4.0.21 | Nextcloud + DB + Redis | ✅ running |
| VM 330 | paperless | 10.4.0.23 | Paperless-ngx + Tika + Gotenberg | ✅ running |
| CT 100 | toolbox | 10.4.0.20 | Caddy · Uptime Kuma · Jellyfin · AdGuard · Open-WebUI · cloudflared | ✅ running |
| CT 101 | adguard-slave | 10.4.0.101 | AdGuard Home (Slave/Backup) | ✅ running |
| CT 110 | storage-node | 10.4.0.30 | CIFS/Samba (media + docs) | ✅ running |
| CT 120 | vaultwarden | 10.4.0.26 | Vaultwarden (Bitwarden-kompatibel) | ✅ running |
| CT 130 | radio-node | **10.4.0.28** | AzuraCast (port 80/443/8000) + Navidrome (port 4533) + Samba music-share + Radio Backend API (port 9500) | ✅ running, RAM 4GB, Tailscale installiert (pending: restart + Wolf-Auth) |
| VM 220 | odoo | 10.4.0.22 | Odoo 17 ERP only (AzuraCast abgeschaltet ✅) | ✅ running |

### STOCKENWEILER — Site B (Schiffscontainer, 10.30.8.x)
**Stockenweiler PVE: EINGESTELLT** (ersetzt durch frawo-docker-1)

| Name | Tailscale | Lokal-IP | OS | Rolle | Status |
|------|-----------|---------|-----|-------|--------|
| frawo-docker-1 | 100.94.32.41 | 10.30.8.22 | Debian 13 Trixie | **n8n (port 5678)** + Icecast-Relay (TODO #242), 31GB RAM, 173G frei | ✅ SSH via Key (pw: vault!), PasswordAuth deaktiviert |
| win-j1aenasv2fj | 100.97.147.67 | 10.30.8.21 | Windows | Management-PC, SSH-Bridge, Claude Code | ✅ |

**HAOS Eltern** (lief auf eingestelltem PVE): Neue Heimat TBD — Option frawo-docker-1 (Task #241)

**frawo-docker-1 Dienste** (entdeckt 2026-05-26):
- n8n Workflow Automation (Port 5678, Docker, /home/wolf/n8n/) — Odoo Task #245
- Icecast-Relay (Task #242): pending Tailscale CT 130 Auth + Neustart

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

---

## ÖFFENTLICHE DIENSTE

| URL | Status | Backend |
|-----|--------|---------|
| https://www.frawo-tech.de | ✅ HTTP 200 | Odoo via Cloudflare |
| https://frawo-tech.de | ✅ HTTP 200 | Redirect zu www |
| https://cloud.frawo-tech.de | 🔴 HTTP 502 | CF-Tunnel zeigt auf alte IP 10.1.0.21 → Fix: Wolf Dashboard |
| https://radio.frawo-tech.de | ❓ nicht konfiguriert | Ziel: AzuraCast CT 130 |

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
| radio.hs27.internal | **10.4.0.28:80** | ✅ | AzuraCast auf CT 130 — **heute migriert** |
| radio-node.hs27.internal | 10.4.0.28 | ✅ | Direkt-Zugriff CT 130 |
| storage-node.hs27.internal | 10.4.0.30 | ✅ | Direkt CT 110 |
| pve.hs27.internal | 10.4.0.99 | ✅ | PVE Web UI |
| adguard-slave.hs27.internal | 10.4.0.101 | ✅ | AdGuard Slave |

| navidrome.hs27.internal | 10.4.0.28:4533 | ✅ | Navidrome auf CT 130 (music_ssd) |
| radio-anker.hs27.internal | 10.4.0.28:80 | ✅ | AzuraCast CT 130 (Anker-Standort) |
| radio-stock.hs27.internal | 10.30.8.22:8000 | 🔴 | Icecast Relay frawo-docker-1 (TODO #242) |
| radio-api.hs27.internal | 10.4.0.28:9500 | ✅ | FraWo Radio Backend API (FastAPI) |
| n8n.hs27.internal | 10.30.8.22:5678 | ✅ | n8n Workflow Automation (frawo-docker-1) |

## FRAWO FUNK RADIO

**Station**: FraWo Funk — "Das Non-Stop Radio vom Bodensee." (Electronic / Alternative)
**Source**: CT 130 (radio-node, 10.4.0.28), AzuraCast `latest`
**Öffentliche Domain**: `funk.frawo-tech.de`

| Stream | URL | Format | Bitrate |
|--------|-----|--------|---------|
| Hifi | `https://funk.frawo-tech.de/listen/frawo_funk/hifi.mp3` | MP3 | 320 kbps |
| Standard | `https://funk.frawo-tech.de/listen/frawo_funk/radio.mp3` | MP3 | 192 kbps |
| Mobile | `https://funk.frawo-tech.de/listen/frawo_funk/mobile.aac` | AAC | 64 kbps |

**Interne Icecast URLs** (direkt, kein Cloudflare):
- `http://10.4.0.28:8000/radio.mp3` (intern, 192 kbps)
- `http://100.94.32.41:8000/radio.mp3` (via Tailscale, für Relays)

**Relay-Architektur (geplant)**:
- CT 130 = Source → frawo-docker-1 Icecast-Relay → Stockenweiler 10.30.8.x lokal
- CT 130 = Source → Raspberry Pi Icecast-Relay → Mobile Events (WiFi-Hotspot)

---

## STORAGE

| Pfad | Typ | Größe | Belegt | Frei | Hinweis |
|------|-----|-------|--------|------|---------|
| `/` (PVE local) | LVM | 70G | 28G | 38G | ✅ 40% |
| `/mnt/ssd2tb` | dir | 1.9T | 175G | 1.6T | ✅ 9.5% |
| `/mnt/music_ssd` | dir | 983G | 177G | 806G | ✅ 18% |
| `/mnt/hs27-media` | CIFS | 98G | 73G | 21G | ⚠️ 74%, Mount stale (Kernel-Bug, Fix: PVE-Neustart) |
| `gdrive:` | rclone | 5.4T | 1.9T | 3.3T | ✅ 36% |
| `local-lvm` (LVM thin) | lvmthin | 164G | 2G | 162G | ✅ 1% — fast leer! |

**hs27-media Breakdown:**
- `FraWo_Radio_Library/Clean` = 63G (Radio-Library, Kern-Content)
- `FraWo_Radio_Library/Quarantine` = 5.6G (458 MP3s, abgelehnt — Wolf entscheidet)
- `yourparty_Libary` = 1.3G (YourParty eingestellt → Archivieren/Löschen)
- `Duplicates` = ✅ gelöscht (109M)

**Langzeit-Fix**: Radio-Library (63G) auf `/mnt/music_ssd` (806G frei) umziehen → hs27-media-Share dauerhaft entlasten.

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
| cloud.frawo-tech.de → 502 | 🔴 | CF Dashboard: Zero Trust → Tunnel → 10.4.0.21 | Wolf |
| Tailscale hs27.internal DNS | 🔴 | tailscale.com/admin/dns: 10.1.0.20 → 10.4.0.20 | Wolf |
| **Passwort-Audit** (#244) | 🔴 | Alle Credentials in Vaultwarden (vault.hs27.internal) | Wolf |
| **frawo-docker-1 Recovery** (#226) | 🔴 | GRUB Single-User-Mode → passwd wolf → SSH-Key → PasswordAuth deaktivieren | Wolf (physisch) |
| PBS VM 240 kein Netzwerk | 🟡 | PVE Web Console → VNC → IP prüfen | Wolf |
| Icecast Relay frawo-docker-1 | 🟡 | SSH-Recovery nötig (#226), dann deploy (#242) | Agent |
| HAOS Eltern — neue Heimat | 🟡 | frawo-docker-1 (Docker) oder verzichten? (#241) | Wolf |
| /mnt/hs27-media stale | 🟡 | PVE-Neustart (Wartungsfenster) | Agent/Wolf |
| DKIM für frawo-tech.de | 🟡 | Strato-Panel → DomainKeys | Wolf |
| StudioPC auf 10.1.0.x | 🟢 | UCG DHCP-Reservation auf 10.4.0.x | Wolf |
| Odoo Admin-Passwort | 🟡 | AuditTemp2026! → permanentes Passwort (#244) | Wolf |

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

*Updated: 2026-05-26 — Claude Sonnet 4.6 + Wolf*
