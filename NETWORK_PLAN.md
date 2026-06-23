> ⚠️ **TEILWEISE VERALTET.** Aktueller Live-Stand: **[NOW.md](NOW.md)**. Kern-Korrekturen: frawo-docker-1 = VMware-VM auf **Flos** Host (kein HW-Zugriff; Wolfs Eltern = Testkunden). Echte Subnetze: Rothkreuz 10.1.0.0/24 + 10.3.0.0/24, Stockenweiler-ESXi 10.30.8.0/24, ProDesk/Easybox 192.168.2.0/24 (NICHT 10.4.0.x). Domain = **frawo.tech**. Easybox → UCG → 10.1.0.x. Ingress läuft über NPM auf CT 103 (10.1.0.149) statt Toolbox (CT 100).

# FraWo GbR — Netzwerk-Plan & Abhängigkeiten
**Stand: 2026-05-26 | Security-Audit-konsolidiert**

## SSOT Contract

- `NETWORK_PLAN.md` beschreibt die fuehrende Netz-, Service- und Abhaengigkeitswahrheit.
- Odoo fuehrt keine Runtime-Topologie, sondern Aufgaben und Ownership.
- `STATUS.md` ist Audit, nicht Governance.
- Secrets gehoeren ausschliesslich in Vaultwarden, nicht in dieses Dokument.

---

## GESAMTARCHITEKTUR

```
╔══════════════════════════════════════════════════════════════════════════════╗
║                        INTERNET / CLOUDFLARE                                ║
║  frawo-tech.de  |  cloud.frawo-tech.de  |  funk.frawo-tech.de              ║
║  home.frawo-tech.de  |  vault.frawo-tech.de                                ║
╚═══════════════╤══════════════════════════════════════════════════════════════╝
                │ HTTPS/443 via CF Tunnel
                │
╔═══════════════▼══════════════════════════════════════════════════════════════╗
║                    TAILSCALE MESH VPN (100.x.x.x)                           ║
║  Alle Nodes encrypted verbunden — kein offener Port nach außen               ║
║  Tailscale-IPs: 100.69.179.87 | 100.82.26.53 | 100.78.88.33 | 100.94.32.41 ║
╚════╤═════════════════════════════════════════╤═══════════════════════════════╝
     │                                         │
     ▼  LAN: 10.4.0.x                         ▼  Tailscale: 100.94.32.41
╔════════════════════════════════╗      ╔══════════════════════════════════╗
║  ANKER PVE (Proxmox)           ║      ║  STOCKENWEILER (Site B)          ║
║  10.4.0.99 | TS: 100.69.179.87 ║      ║  frawo-docker-1 | 10.30.8.22    ║
║  Primärer Produktionsserver    ║      ║  Debian 13 Trixie, 188G         ║
╚════════════════════════════════╝      ╚══════════════════════════════════╝
```

---

## ANKER PVE — VM/CT Übersicht

```
ANKER PVE (10.4.0.99)
│
├── CT 100: TOOLBOX (10.4.0.20) ← CENTRAL INGRESS
│   ├── Caddy (HTTP Proxy, Port 80/443)     ← ALLE .hs27.internal domains
│   ├── AdGuard Home (DNS, Port 53)         ← DNS für alle Clients
│   │   └── Auth: Vaultwarden-verwaltet ✅
│   ├── cloudflared (CF Tunnel)             ← öffentliche Domains
│   ├── Uptime Kuma (Port 3001)             ← Monitoring UI
│   ├── Jellyfin (Port 8096)                ← media.hs27.internal
│   └── Open-WebUI (Port 3000)              ← KI-Interface
│
├── CT 101: ADGUARD-SLAVE (10.4.0.101)
│   └── AdGuard Home (DNS Backup)
│
├── CT 110: STORAGE-NODE (10.4.0.30)
│   ├── CIFS/Samba: media-share
│   └── CIFS/Samba: docs-share
│
├── CT 120: VAULTWARDEN (10.4.0.26)
│   ├── Vaultwarden :8080                   ← vault.hs27.internal
│   ├── SIGNUPS: disabled ✅
│   └── Admin-Token: argon2id ✅
│
├── CT 130: RADIO-NODE (10.4.0.28, TS: 100.78.88.33)
│   ├── AzuraCast (Port 80/443/8000)        ← radio.hs27.internal + funk.frawo-tech.de
│   │   ├── /radio.mp3 (192 kbps MP3)
│   │   ├── /hifi.mp3 (320 kbps MP3)
│   │   └── /mobile.aac (64 kbps AAC)
│   ├── Navidrome (Port 4533)               ← navidrome.hs27.internal
│   ├── Radio Backend API (Port 9500)       ← radio-api.hs27.internal (FastAPI)
│   ├── Samba (Port 445) ← music-share ⚠️ (auf LAN beschränken)
│   └── Tailscale (TS: 100.78.88.33) ✅
│
├── VM 210: HAOS (10.4.0.24)
│   └── Home Assistant OS               ← ha.hs27.internal + home.frawo-tech.de
│
├── VM 220: ODOO (10.4.0.22)
│   ├── Odoo 17 ERP (Port 8069)         ← odoo.hs27.internal
│   │   └── Port: 127.0.0.1:8069 ✅ (heute geändert, war 0.0.0.0!)
│   └── PostgreSQL 15 (intern)
│
├── VM 240: PBS-FRAWO (10.4.0.25)
│   └── Proxmox Backup Server ⚠️ kein Netzwerk (Task #159)
│
├── VM 300: NEXTCLOUD (10.4.0.21)
│   ├── Nextcloud 33 (Port 80)          ← cloud.hs27.internal + cloud.frawo-tech.de
│   ├── MariaDB 10.11 (intern)
│   └── Redis (intern)
│
└── VM 330: PAPERLESS (10.4.0.23)
    ├── Paperless-ngx (Port 8000)       ← paperless.hs27.internal
    ├── PostgreSQL 15 (intern)
    ├── Redis (intern)
    ├── Tika (Port 9998, intern)
    └── Gotenberg (Port 3000, intern)
```

---

## STOCKENWEILER (frawo-docker-1)

```
frawo-docker-1 (10.30.8.22 | TS: 100.94.32.41)
│
├── n8n Automation (Port 5678)          ← n8n.hs27.internal
├── Portainer CE (Port 9000/9443)       ← portainer.hs27.internal
│   └── Credentials: Vaultwarden-verwaltet ✅
├── Grafana (Port 3001)                 ← grafana.hs27.internal
│   └── Credentials: Vaultwarden-verwaltet
├── Prometheus (Port 9091)              ← prometheus.hs27.internal
│   └── Scraping: frawo-docker-1 Node-Exporter
├── Node Exporter (Port 9100)           ← frawo-docker-1 Metriken
└── Icecast Relay (Port 8000)           ← radio-stock.hs27.internal
    └── RELAY: CT 130 (100.78.88.33:8000) via Tailscale
        ├── /radio.mp3
        ├── /hifi.mp3
        └── /mobile.aac
```

---

## DATENFLUSS — Request-Routing

```
ÖFFENTLICHER ZUGRIFF:
User → cloud.frawo-tech.de → Cloudflare → CF Tunnel (cloudflared@CT100) 
    → Nextcloud (10.4.0.21:80)

INTERNER ZUGRIFF:
User (LAN/VPN) → cloud.hs27.internal 
    → AdGuard DNS → 10.4.0.20 (CT 100)
    → Caddy Reverse Proxy → 10.4.0.21:80 (Nextcloud)

RADIO-STREAM (öffentlich):
Hörer → funk.frawo-tech.de → CF Tunnel → AzuraCast (10.4.0.28:80/8000)

RADIO-STREAM (Relay, intern):
Hörer → radio-stock.hs27.internal → Caddy → 100.94.32.41:8000 (Icecast-Relay)
    → TAILSCALE → 100.78.88.33:8000 (AzuraCast CT 130)
```

---

## ABHÄNGIGKEITSMATRIX

| Service | Hängt ab von | Wird genutzt von |
|---------|-------------|-----------------|
| AdGuard CT 100 | - | ALLE internen Clients (DNS) |
| Caddy CT 100 | AdGuard (DNS intern) | Alle .hs27.internal Domains |
| cloudflared CT 100 | Caddy | CF Tunnel → alle öfftl. Domains |
| Odoo VM 220 | PostgreSQL (intern) | frawo-tech.de, odoo.hs27.internal |
| Nextcloud VM 300 | MariaDB, Redis (intern) | cloud.frawo-tech.de, cloud.hs27.internal |
| Paperless VM 330 | PostgreSQL, Redis, Tika, Gotenberg | paperless.hs27.internal |
| AzuraCast CT 130 | Tailscale (für Relay) | funk.frawo-tech.de, radio.hs27.internal |
| Navidrome CT 130 | music_ssd (lokal) | navidrome.hs27.internal |
| Radio Backend CT 130 | AzuraCast API | radio-api.hs27.internal |
| Icecast-Relay frawo-docker-1 | Tailscale → CT 130:8000 | radio-stock.hs27.internal |
| Grafana frawo-docker-1 | Prometheus frawo-docker-1 | grafana.hs27.internal |
| Prometheus frawo-docker-1 | Node-Exporter | Grafana Dashboards |
| n8n frawo-docker-1 | - (standalone) | n8n.hs27.internal |
| Portainer frawo-docker-1 | Docker Socket | portainer.hs27.internal |

---

## KRITISCHER PFAD (SPOF — Single Point of Failure)

```
AdGuard CT 100 fällt aus → ALLE .hs27.internal Domains tot
    → Fallback: CT 101 AdGuard-Slave (10.4.0.101) ← muss als Backup-DNS konfiguriert sein!

Caddy CT 100 fällt aus → ALLE internen Domains nicht erreichbar
    → Kein Fallback (Single Point of Failure!)

Tailscale fällt aus → Icecast-Relay (frawo-docker-1 → CT 130) tot
    → frawo-docker-1 nicht erreichbar von CT 100
    → Fallback: LAN 10.30.8.22 (nur von Stockenweiler)

CF Tunnel fällt aus → ALLE öffentlichen Domains tot
    → Kein Fallback
```

---

## FIREWALL-STATUS (Audit 2026-05-26)

| Node | Firewall | Status |
|------|---------|--------|
| PVE Host | keine | ❌ KRITISCH |
| CT 100 Toolbox | keine (Container-Netz) | ⚠️ |
| CT 120 Vaultwarden | keine | ⚠️ |
| CT 130 Radio-Node | Samba eingeschränkt ✅ | ✅ bind interfaces + hosts allow (10.4.0.0/24 + Tailscale) |
| VM 220 Odoo | keine | ❌ (fail2ban fehlt) |
| VM 300 Nextcloud | keine (SSH deaktiviert) | ⚠️ |
| VM 330 Paperless | keine (SSH nur 127.0.0.1) | ✅ SSH OK |
| frawo-docker-1 | UFW aktiv ✅ | ✅ deny incoming, allow Tailscale+LAN |

---

## SECRET-REFERENZEN

Alle Credentials, Tokens und Admin-Logins leben in **Vaultwarden**.
- Repo-Dokumente referenzieren nur noch den passenden Vault-Eintrag.
- Aktueller Stand: produktive Kern-Services sind im Vault dokumentiert.

| Service | User | Status |
|---------|------|--------|
| AdGuard CT 100 | Vault-Eintrag | ✅ In Vaultwarden |
| Portainer frawo-docker-1 | Vault-Eintrag | ✅ In Vaultwarden |
| Grafana frawo-docker-1 | Vault-Eintrag | ✅ In Vaultwarden |
| Odoo VM 220 | Vault-Eintrag | ⚠️ Rotationsstatus im Vault verifizieren |
| Nextcloud VM 300 | Vault-Eintrag | ✅ In Vaultwarden |
| Paperless VM 330 | Vault-Eintrag | ✅ In Vaultwarden |
| Vaultwarden CT 120 | Offline-/Vault-Referenz | ✅ Admin-Zugriff ausserhalb des Repos |

---

## OFFENE SICHERHEITSLÜCKEN (priorisiert)

| Prio | Node | Problem | Fix |
|------|------|---------|-----|
| ❌ JETZT | VM 220 Odoo | Legacy-Temp-Credential aus Alt-Doku muss als rotiert/verifiziert gelten | Vaultwarden-Eintrag pruefen und Rotation bestaetigen |
| ❌ JETZT | alle | Passwörter in Vaultwarden eintragen | vault.hs27.internal |
| ✅ DONE | frawo-docker-1 | UFW aktiv | deny incoming, allow 100.64.0.0/10 + 10.30.8.0/24 |
| ⚠️ WOCHE | PVE Host | Kein PVE-Firewall | PVE Web UI → Datacenter → Firewall |
| ✅ DONE | CT 130 | Samba eingeschränkt | bind interfaces + hosts allow 10.4.0.0/24 |
| ✅ DONE | VM 300 | trusted_proxies bereinigt | 10.4.0.0/24 + 100.64.0.0/10 via occ |
| ⚠️ MONAT | CT 100 | Port 5555 (python3, unbekannt) | Prozess identifizieren/beenden |
| ⚠️ MONAT | PVE | 21 OS-Updates ausstehend | `apt upgrade` |

---

*Zuletzt aktualisiert: 2026-05-27 — Vaultwarden Setup + UFW + Samba + Nextcloud + Claude Sonnet 4.6*
