> ⚠️ **TEILWEISE VERALTET.** Aktueller Live-Stand: **[NOW.md](NOW.md)**. Kern-Korrekturen: frawo-docker-1 = VMware-VM auf **Flos** Host (kein HW-Zugriff; Wolfs Eltern = Testkunden). Echte Subnetze: Rothkreuz 10.1.0.0/24 + 10.3.0.0/24 (Radio-DMZ), Stockenweiler-ESXi 10.30.8.0/24. Domain = **frawo.tech** (nicht frawo-tech.de).

# LIVE CONTEXT — FraWo GbR Infrastruktur
**Single Source of Truth für technischen Zustand**
*Letzte vollständige Aktualisierung: 2026-06-17 — Antigravity (Gemini 3.5 Flash) + Wolf*

---

## ARCHITEKTUR-ÜBERSICHT

```
┌─────────────────────────────────────────────────────────────┐
│                    TAILSCALE MESH (VPN)                      │
│         Alle Nodes sicher verbunden, kein offener Port       │
└──────────────┬──────────────────────┬───────────────────────┘
               │                      │
    ┌──────────▼──────────┐  ┌────────▼──────────────────────┐
    │   PRODESK PVE        │  │  STOCKENWEILER (Site B)        │
    │   10.1.0.128         │  │  Netz: 10.30.8.x              │
    │   Tailscale:         │  │  frawo-docker-1 (10.30.8.22)  │
    │   100.91.20.116      │  │  Tailscale: 100.94.32.41      │
    │   Rolle: Master      │  │  Rolle: n8n, LS25 Server      │
    └─────────────────────┘  │                                │
                             │  win-j1aenasv2fj (offline)     │
                             │  Tailscale: 100.97.147.67      │
                             │  Windows Server VM             │
                             └────────────────────────────────┘
```

---

## NODE-ROLLEN (verbindlich)

### PRODESK (stockenweiler-pve) — Master / Workhorse
**Lokal-IP**: `10.1.0.128` | **Tailscale**: `100.91.20.116` | **Standort**: Rothkreuz UCG-Netz

| ID/LXC | Name | IP | Rolle | Status |
|---|---|---|---|---|
| VM 360 | homeassistant-eltern | 192.168.2.154 | HomeAssistant Eltern (Master-VM) | ✅ running |
| CT 101 | adguard | 10.1.0.52 | DNS / Ad-Blocking | ✅ running |
| CT 103 | npm | 10.1.0.149 | Reverse-Proxy | ✅ running |
| CT 106 | wireguard | — | VPN | ✅ running |
| CT 108 | vaultwarden | 10.1.0.95 | Passwort-Tresor | ✅ running |
| CT 109 | pbs | — | Proxmox Backup Server | ✅ running |
| CT 110 | n8n | 10.1.0.100 | Automation | ✅ running |
| CT 120 | fileserver | 10.1.0.94 | NAS (SMB) | ✅ running |
| CT 140 | frawotech-web | 10.1.0.112 | Odoo 17 (odoo-web & odoo-db & cloudflared) | ✅ running |
| CT 141 | azuracast-rk | — | Neue AzuraCast Instanz | ⏹ stopped |
| CT 150 | monitoring-stack | — | Prometheus / Grafana | ⏹ stopped |

---

### ANKER PVE — Sekundäre Produktion
**Lokal-IP**: `10.1.0.92` | **Tailscale**: `100.69.179.87` | **Standort**: Rothkreuz

| ID/LXC | Name | IP | Rolle | Status |
|---|---|---|---|---|
| VM 210 | haos | 10.4.0.24 | Home Assistant OS (FraWo intern) | ✅ running (routed) |
| VM 220 | odoo | 10.4.0.22 | Odoo 17 ERP (Legacy, gestoppt/archiviert) | ✅ running |
| VM 240 | PBS-FraWo | — | Backup-VM (Keine Backups auf ssd2tb!) | ⏹ stopped |
| VM 300 | nextcloud | — | Nextcloud (Legacy, archivieren) | ⏹ stopped |
| VM 330 | paperless | — | Paperless (Legacy, archivieren) | ⏹ stopped |
| CT 100 | toolbox | — | Interner DNS / Caddy | ⏹ stopped |
| CT 101 | adguard-slave | 10.1.0.27 (IPv6) | DNS-Slave | ✅ running |
| CT 110 | storage-node | 10.1.0.81 (IPv6) | Storage / gdrive | ✅ running |
| CT 120 | vaultwarden | — | Dublette (entsorgen) | ⏹ stopped |
| CT 130 | radio-node | 100.78.88.33 | AzuraCast / Navidrome | ⏹ stopped |

---

### STOCKENWEILER — Site B (Flos ESXi-Host)
**Netz**: `10.30.8.x` | **HW-Zugriff**: Keiner (nur Mieter-VMs)

| Name | Tailscale | Lokal-IP | Rolle | Status |
|---|---|---|---|---|
| **frawo-docker-1** | 100.94.32.41 | 10.30.8.22 | Docker Host (n8n, Prometheus, LS25 Server) | 🟢 ONLINE (symmetrische 150 kbps Drossel) |
| **win-j1aenasv2fj** | 100.97.147.67 | 10.30.8.21 | Windows Server VM (AnyDesk: `1522346646`) | 🔴 OFFLINE (ausgeschaltet) |

---

## ÖFFENTLICHE DIENSTE (frawo.tech)

| URL | Status | Backend | Ingress |
|---|---|---|---|
| https://www.frawo.tech | ✅ HTTP 200 | CF-Tunnel -> ProDesk CT140 | odoo-web:8069 |
| https://frawo.tech | ✅ HTTP 200 | CF-Tunnel -> ProDesk CT140 | odoo-web:8069 |
| https://vault.frawo.tech | ✅ | CF-Tunnel -> ProDesk CT108 | vaultwarden:8080 |
| https://n8n.frawo.tech | ✅ | CF-Tunnel -> ProDesk CT110 | n8n:5678 |
| https://music.frawo.tech | ⚠️ | TBD | Navidrome |
| https://funk.frawo.tech | ⚠️ | TBD | AzuraCast |

---

## STORAGE-ÜBERSICHT

- **ProDesk local-lvm**: Primärer SSD-Speicher für aktive Container.
- **NAS / Fileserver (CT 120)**: `\\10.1.0.94` (wolf / `FraWoNAS2026!`). Samba-Freigaben für `music` (Musik-Library) und `scans`.
- **Anker local-lvm**: SSD-Speicher für VMs auf Anker.
- **Anker local-backups (`/mnt/ssd2tb`)**: ⚠️ **Achtung: SSD existiert physisch nicht!** Der PBS-Datastore dort hat kein physisches Backing.

---

## EMAIL / SMTP (Brevo / Strato)

- **Brevo SMTP (Odoo-Mails)**: `smtp-relay.brevo.com:2525`, Login: `ae8c51001@smtp-brevo.com`, Key in `frawo_credentials_2026-05-30.txt`.
- **Strato SMTP (Infrastruktur)**: `smtp.strato.de:465` (SSL), Login: `webmaster@frawo-tech.de`.

---

## OFT GESTELLTE KI-AGENTEN-FRAGEN (SSOT)

- **Warum ist der Stockenweiler-Download so langsam?**
  Der ESXi-Host von Flo leitet den Datenverkehr über einen netcup-VPS-Tunnel um, der künstlich auf ~150 kbit/s gedrosselt ist. Deshalb werden alle Produktivdienste (Odoo, Radio) nach Rothkreuz auf den ProDesk repatriiert.
- **Welches Repo ist kanonisch?**
  Das Haupt-Repository unter `C:\Users\StudioPC\FraWo` ist das kanonische Verzeichnis. Die Junctions `C:\Users\Admin\Workspace\FraWo` und `C:\WORKSPACE\FraWo` sollten darauf verweisen.

*Zuletzt aktualisiert am 17. Juni 2026.*
