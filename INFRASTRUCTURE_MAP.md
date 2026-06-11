> ⚠️ **TEILWEISE VERALTET.** Aktueller Live-Stand: **[NOW.md](NOW.md)**. Kern-Korrekturen: frawo-docker-1 = VMware-VM auf **Flos** Host (kein HW-Zugriff; Wolfs Eltern = Testkunden). Echte Subnetze: Rothkreuz 10.1.0.0/24 + 10.3.0.0/24 (Radio-DMZ), Stockenweiler-ESXi 10.30.8.0/24, ProDesk/Easybox 192.168.2.0/24 (NICHT 10.4.0.x). Domain = **frawo.tech** (nicht frawo-tech.de).

# FraWo GbR — Infrastruktur-Karte
**Stand: 2026-05-30 | Verifiziert durch Live-Check**

## Übersicht

```mermaid
graph TB
    subgraph INTERNET["🌐 Internet"]
        CF["☁️ Cloudflare<br/>frawo-tech.de<br/>cloud/funk/vault.frawo-tech.de"]
    end

    subgraph TAILSCALE["🔒 Tailscale Mesh VPN (100.x.x.x)"]
        direction TB

        subgraph ANKER["🖥️ ANKER PVE — Primär-Produktion<br/>10.4.0.99 | TS: 100.69.179.87"]
            CT100["📦 CT 100 TOOLBOX<br/>10.4.0.20 | TS: 100.82.26.53<br/>━━━━━━━━━━━━━━━━<br/>Caddy (Reverse Proxy)<br/>AdGuard Home (DNS)<br/>cloudflared (CF Tunnel)<br/>Uptime Kuma"]

            CT101["📦 CT 101<br/>AdGuard Slave<br/>10.4.0.101"]

            CT110["📦 CT 110 Storage-Node<br/>10.4.0.30<br/>CIFS/Samba Media+Docs"]

            CT120["🔐 CT 120 Vaultwarden<br/>10.4.0.26<br/>Bitwarden-kompatibel<br/>437 Credentials"]

            CT130["📻 CT 130 Radio-Node<br/>10.4.0.28 | TS: 100.78.88.33<br/>━━━━━━━━━━━━━━━━<br/>AzuraCast (funk.frawo-tech.de)<br/>Navidrome<br/>Radio Backend API :9500"]

            VM210["🏠 VM 210 HAOS<br/>10.4.0.24<br/>Home Assistant OS"]

            VM220["⚙️ VM 220 ODOO<br/>10.4.0.22<br/>Odoo 17 ERP<br/>DB: FraWo_GbR"]

            VM240["💾 VM 240 PBS<br/>10.4.0.25<br/>⚠️ kein Netzwerk"]

            VM300["☁️ VM 300 Nextcloud<br/>10.4.0.21<br/>cloud.frawo-tech.de<br/>Dokument-Hub"]

            VM330["📄 VM 330 Paperless<br/>10.4.0.23<br/>OCR + Archiv<br/>→ NC/Archiv"]
        end

        subgraph STOCKENWEILER["🐳 STOCKENWEILER — Site B<br/>frawo-docker-1 | 10.30.8.22 | TS: 100.94.32.41"]
            D_N8N["🔄 n8n Automation<br/>:5678"]
            D_OC["🦞 OpenClaw AI Gateway<br/>:19000<br/>@Frawo_ClawBot<br/>gpt-4o primär"]
            D_GRAF["📊 Grafana<br/>:3001"]
            D_PROM["📈 Prometheus<br/>:9091"]
            D_ICE["📡 Icecast Relay<br/>:8000"]
            D_PORT["🐳 Portainer<br/>:9000"]
        end

        subgraph CLIENTS["💻 Clients"]
            SPC["🖥️ wolfstudiopc<br/>TS: 100.98.31.60<br/>Dev-Workstation"]
            TELEGRAM["📱 Telegram<br/>@Frawo_ClawBot"]
        end
    end

    CF -->|"CF Tunnel<br/>HTTPS"| CT100
    CT100 -->|"proxy"| CT130
    CT100 -->|"proxy"| VM220
    CT100 -->|"proxy"| VM300
    CT100 -->|"proxy"| CT120
    CT100 -->|"proxy"| VM210
    CT100 -->|"DNS"| CT101
    CT130 -->|"Icecast Stream"| D_ICE
    VM330 -->|"post-consume →"| VM300
    D_OC -->|"XML-RPC"| VM220
    D_OC -->|"Webhook"| D_N8N
    TELEGRAM -->|"Messages"| D_OC
    SPC -->|"SSH/Browser"| CT100
```

---

## Storage-Architektur (Anker PVE)

```mermaid
graph LR
    subgraph NVMe["💨 NVMe (primär)"]
        LVM["local-lvm<br/>LVM-Thin Pool<br/>156 GB<br/>30% genutzt"]
    end
    subgraph USB["🔌 USB-SSD (nur Backup)"]
        SSD["ssd2tb<br/>1.9 TB<br/>9% genutzt<br/>⚠️ Bad Sectors"]
    end
    subgraph CLOUD["☁️ Cloud"]
        GDRIVE["Google Drive<br/>5.4 TB<br/>CT 110 Disk"]
    end

    LVM --> CT100_S["CT 100-130<br/>VM 210-330"]
    SSD --> DUMPS["Alte Backups<br/>(images leer!)"]
    GDRIVE --> CT110_S["CT 110 Storage-Node<br/>Disk"]
```

---

## Datenfluss: Dokumente

```
Eingang → cloud.frawo-tech.de/Dokumente/Eingang
             ↓ rclone (alle 5 Min, VM 330 cron)
         Paperless consume_dir (VM 330)
             ↓ OCR + Klassifizierung
         Paperless DB + paperless-to-nc.sh
             ↓
         cloud.frawo-tech.de/Dokumente/Archiv/{Korrespondent}/{Jahr}/
```

## Datenfluss: Radio

```
FraWo Musikarchiv (CT 110 Samba) → AzuraCast (CT 130)
                                       ↓ Icecast Stream :8000
                                   frawo-docker-1 Icecast-Relay
                                       ↓ CF Tunnel
                                   funk.frawo-tech.de (öffentlich)
```

---

## Was noch fehlt / offen

| Problem | Prio | Fix |
|---------|------|-----|
| PVE Firewall nicht aktiv | 🔴 | PVE Web UI → Datacenter → Firewall |
| VM 240 PBS kein Netzwerk | 🟡 | VNC Console → Netzwerk konfigurieren |
| Anthropic API kein Guthaben | 🟡 | console.anthropic.com → Billing |
| Tailscale Subnet Route nicht approved | 🟡 | admin.tailscale.com → proxmox-anker → approve |
| OpenClaw Email Channel fehlt | 🟢 | agent@frawo-tech.de IMAP/SMTP konfigurieren |

---

*Verifiziert: 2026-05-30 — Live-Check aller Services durch Claude Sonnet 4.6 + Wolf*
