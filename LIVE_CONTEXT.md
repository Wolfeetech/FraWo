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
    ┌──────────▼──────────┐  ┌────────▼───────────────┐
    │   ANKER PVE          │  │  STOCKENWEILER (Site B)  │
    │   10.4.0.99          │  │  192.168.178.x           │
    │   Tailscale:         │  │  Tailscale:              │
    │   100.69.179.87      │  │  100.91.20.116 (offline) │
    │   PRIMARY PRODUCTION │  │  ELTERN-HAUS             │
    └──────────┬──────────┘  └────────┬───────────────┘
               │                      │
    [alle VMs/CTs unten]    ┌─────────▼──────────────┐
                            │  frawo-docker-1          │
                            │  Tailscale: 100.94.32.41 │
                            │  Lokal: 10.30.8.22       │
                            │  Physisch: Schiffscontainer│
                            │  Stockenweiler (10.30.8.x)│
                            │  OS: Debian 13 Trixie    │
                            │  Disk: 188G frei         │
                            │  SSH: wolf (sudo) ✅     │
                            └────────────────────────┘
```

---

## NODE-ROLLEN (verbindlich)

### ANKER PVE — Primäre Produktion
**IP**: `10.4.0.99` | **Tailscale**: `100.69.179.87` | **PVE**: 9.1.19, Kernel 7.0.2-6-pve

| ID | Name | IP | Rolle | Status |
|----|------|----|-------|--------|
| VM 210 | haos | 10.4.0.24 | Home Assistant OS (FraWo intern) | ✅ running |
| VM 220 | odoo | 10.4.0.22 | Odoo 17 ERP + AzuraCast (provisorisch) | ✅ running |
| VM 240 | PBS-FraWo | 10.4.0.25 (konfiguriert) | Proxmox Backup Server | ⚠️ kein Netzwerk |
| VM 300 | nextcloud | 10.4.0.21 | Nextcloud + DB + Redis | ✅ running |
| VM 330 | paperless | 10.4.0.23 | Paperless-ngx + Tika + Gotenberg | ✅ running |
| CT 100 | toolbox | 10.4.0.20 | Caddy · Uptime Kuma · Jellyfin · AdGuard · Open-WebUI · cloudflared | ✅ running |
| CT 101 | adguard-slave | 10.4.0.101 | AdGuard Home (Slave/Backup) | ✅ running |
| CT 110 | storage-node | 10.4.0.30 | CIFS/Samba (media + docs) | ✅ running |
| CT 120 | vaultwarden | 10.4.0.26 | Vaultwarden (Bitwarden-kompatibel) | ✅ running |
| CT 130 | radio-node | **10.4.0.28** | AzuraCast (Ziel) + FraWo Radio Backend | ✅ running, IP heute gesetzt |

### STOCKENWEILER PVE — Site B (Eltern-Haus)
**IP lokal**: `192.168.178.172` | **Tailscale**: `100.91.20.116` | **Status**: offline seit 15 Tagen

| Was | Wo | Status |
|-----|----|--------|
| Home Assistant (Eltern) | HAOS VM | offline (PVE offline) |
| frawo-docker-1 | Schiffscontainer | Tailscale 100.94.32.41, Lokal 10.30.8.22, SSH ✅ (wolf/sudo), Debian 13 Trixie, 188G frei |

### ENTWICKLUNGSMASCHINEN (keine Produktion)
| Name | Tailscale | Netzwerk | Rolle |
|------|-----------|---------|-------|
| wolfstudiopc | 100.98.31.60 | 10.1.0.210 (alt!) | Dev-Workstation, lokales Docker-Testing |
| wolf-surface | 100.79.103.59 | - | Mobile Dev |
| wolf-zenbook | 100.76.249.126 | - | Linux Dev |
| surface-go-frontend | 100.106.67.127 | - | Frontend-Entwicklung |

### STOCKENWEILER INFRASTRUKTUR (Schiffscontainer / Eltern-Haus)
| Name | Tailscale | Lokal-IP | Rolle | Status |
|------|-----------|---------|-------|--------|
| frawo-docker-1 | 100.94.32.41 | 10.30.8.22 | Phys. Server, Debian 13 Trixie, 188G Disk, Rolle TBD | ✅ SSH wolf/sudo |
| win-j1aenasv2fj | 100.97.147.67 | 10.30.8.21 | Windows-PC Stockenweiler, SSH-Bridge + Claude Code | ✅ |

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

| Domain (AdGuard) | Caddy Port | Upstream | Status |
|------------------|-----------|---------|--------|
| odoo.hs27.internal | :8444 | 10.4.0.22:8069 | ✅ |
| cloud.hs27.internal | :8445 | 10.4.0.21:80 | ✅ intern |
| paperless.hs27.internal | :8446 | 10.4.0.23:8000 | ✅ |
| vault.hs27.internal | :8442 | 10.4.0.26:8080 | ⚠️ prüfen |
| ha.hs27.internal | :8443 | 10.4.0.24:8123 | ✅ |
| media.hs27.internal | :8449 | 10.4.0.20:8096 (Jellyfin) | ✅ |
| radio.hs27.internal | :8448 | 10.4.0.22:8080 (AzuraCast VM220 provisorisch) | ✅ |
| radio-node.hs27.internal | direkt | 10.4.0.28 | ✅ neu |
| storage-node.hs27.internal | direkt | 10.4.0.30 | ✅ neu |
| pve.hs27.internal | direkt | 10.4.0.99 | ✅ neu |
| adguard-slave.hs27.internal | direkt | 10.4.0.101 | ✅ neu |

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
| cloud.frawo-tech.de → 502 | 🔴 | CF Dashboard: Tunnel → 10.4.0.21 | Wolf |
| PBS VM 240 kein Netzwerk | 🔴 | PVE Web Console → VNC → IP prüfen | Wolf |
| /mnt/hs27-media stale | 🟡 | PVE-Neustart (Wartungsfenster) | Agent/Wolf |
| frawo-docker-1 SSH-Key deployen | 🟡 | SSH läuft via Passwort — hs27_ops_ed25519.pub in authorized_keys | Wolf |
| Tailscale hs27.internal DNS | 🟡 | admin-console: nameserver 10.1.0.20 → 10.4.0.20 | Wolf |
| Stockenweiler offline | 🔴 | Physisch einschalten (Rothkreuz) | Wolf |
| DKIM für frawo-tech.de | 🟡 | Strato-Panel → DomainKeys | Wolf |
| StudioPC auf 10.1.0.x | 🟢 | UCG DHCP-Reservation auf 10.4.0.x | Wolf |
| Odoo Admin-Passwort | 🟡 | Temporär: AuditTemp2026! → Wolf setzt permanent | Wolf |

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

*Updated: 2026-05-25 — Claude Sonnet 4.6 + Wolf*
