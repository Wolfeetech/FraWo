> ⚠️ **TEILWEISE VERALTET.** Aktueller Live-Stand: **[NOW.md](NOW.md)**. Kern-Korrekturen: frawo-docker-1 = VMware-VM auf **Flos** Host (kein HW-Zugriff; Wolfs Eltern = Testkunden). Echte Subnetze: Rothkreuz 10.1.0.0/24 + 10.3.0.0/24 (Radio-DMZ), Stockenweiler-ESXi 10.30.8.0/24. Domain = **frawo.tech** (nicht frawo-tech.de).

# FraWo GbR — Infrastruktur-Karte
**Stand: 2026-06-17 | Verifiziert durch Live-Check**

## Übersicht

```mermaid
graph TB
    subgraph INTERNET["🌐 Internet"]
        CF["☁️ Cloudflare<br/>frawo.tech<br/>cloud/funk/vault.frawo.tech"]
    end

    subgraph TAILSCALE["🔒 Tailscale Mesh VPN (100.x.x.x)"]
        direction TB

        subgraph PRODESK["🖥️ PRODESK PVE — Master / Workhorse<br/>10.1.0.128 | TS: 100.91.20.116"]
            CT101["📦 CT 101 AdGuard<br/>10.1.0.52"]
            CT103["📦 CT 103 NPM Proxy<br/>10.1.0.149"]
            CT108["🔐 CT 108 Vaultwarden<br/>10.1.0.95"]
            CT110_P["📦 CT 110 n8n<br/>10.1.0.100"]
            CT120_P["📦 CT 120 Fileserver NAS<br/>10.1.0.94"]
            CT140["📦 CT 140 Odoo ERP<br/>10.1.0.112<br/>(odoo:17 + postgres:15)"]
            VM360["🏠 VM 360 HAOS Eltern<br/>192.168.2.154"]
        end

        subgraph ANKER["🖥️ ANKER PVE — Sekundär-Produktion<br/>10.1.0.92 | TS: 100.69.179.87"]
            VM210["🏠 VM 210 HAOS Intern<br/>10.4.0.24 (routed)"]
            VM220["⚙️ VM 220 Odoo (Legacy)<br/>10.4.0.22"]
            CT101_A["📦 CT 101 AdGuard Slave"]
            CT110_A["📦 CT 110 Storage Node"]
        end

        subgraph STOCKENWEILER["🐳 STOCKENWEILER — Site B (Flos ESXi Host)<br/>Netz: 10.30.8.x"]
            D_DOCKER["🐳 frawo-docker-1 (10.30.8.22)<br/>TS: 100.94.32.41<br/>━━━━━━━━━━━━━━━━<br/>n8n / Grafana / Portainer<br/>Prometheus / LS25 Server"]
            D_WIN["🖥️ win-j1aenasv2fj (10.30.8.21)<br/>TS: 100.97.147.67<br/>(Windows Server - Offline)"]
        end

        subgraph CLIENTS["💻 Clients"]
            SPC["🖥️ wolfstudiopc<br/>TS: 100.98.31.60<br/>Dev-Workstation"]
        end
    end

    CF -->|"CF Tunnel (FraWo-RK)<br/>HTTPS"| CT140
    CF -->|"CF Tunnel<br/>HTTPS"| CT108
    CT103 -->|"proxy"| CT140
    CT103 -->|"proxy"| CT108
    SPC -->|"SSH/Samba"| PRODESK
```

---

## Storage-Architektur

- **ProDesk local-lvm**: Speicherpool für Container (CT 101-140) auf ProDesk.
- **Samba Fileserver (CT 120)**: Stellt das Musikarchiv (`music`) und Scanner-Ablagen (`scans`) im Netzwerk unter `\\10.1.0.94` zur Verfügung.
- **Google Drive**: Synchronisation mit `gdrive:` erfolgt über rclone vom Storage-Node.
- **ssd2tb (Anker)**: ⚠️ **Achtung: Physisch nicht vorhanden!** Inactive/Phantom-Config, keine Datensicherungen dorthin schreiben.

---

## Datenfluss: Dokumente

```
Eingang → Scanner/Upload → Samba scans Share (CT 120)
                             ↓ rclone (alle 5 Min)
                         Paperless-ngx (Legacy VM 330 / Neu TBD)
                             ↓ OCR + Archivierung
                         Nextcloud-Archiv (frawo.tech)
```

---

## Was noch fehlt / offen

| Problem | Prio | Fix | Status |
|---|---|---|---|
| Windows VM offline | 🔴 | Flo muss die Windows Server VM auf dem ESXi starten. | Ausstehend |
| Odoo Repatriierung abschließen | 🔴 | DNS-Einträge von `frawo.tech` auf den ProDesk CT 140 Tunnel umleiten. | In Arbeit |
| Radio Konsolidierung | 🟡 | Medienspeicher CT 120 mit AzuraCast CT 141 verbinden und Playlisten synchronisieren. | Ausstehend |
| PBS Backups einrichten | 🟡 | Datensicherung auf dem ProDesk PBS (CT 109) aktivieren (ohne ssd2tb). | Ausstehend |

---

*Verifiziert: 2026-06-17 — Live-Check der ProDesk- und Anker-Topologie durch Antigravity.*
