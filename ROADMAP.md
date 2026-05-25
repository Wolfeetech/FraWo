# ROADMAP — FraWo GbR Infrastruktur
**Stand: 2026-05-25 | Letzte Konsolidierung: Claude Sonnet 4.6 + Wolf**

**SSOT-Hierarchie:**
- **Odoo** (`FraWo_GbR` → "🚀 Homeserver 2027: Masterplan") → Wer macht was, Status, Priorität
- **GitHub** (diese Datei, `LIVE_CONTEXT.md`, `STATUS.md`) → Technische Wahrheit
- **Konflikt**: Odoo für Status, GitHub für Konfiguration

---

## ZIELARCHITEKTUR 2027 (Masterplan)

```
ANKER PVE (Primary)              STOCKENWEILER (Site B)
├── Odoo ERP (VM 220)            ├── HAOS Eltern
├── Nextcloud (VM 300)           ├── frawo-docker-1 (Schiffscontainer)
├── Paperless (VM 330)           │   └── Rolle: Monitoring-Stack ODER
├── PBS Backup (VM 240) ←fix     │       Staging ODER Backup-Relay
├── HAOS FraWo (VM 210)          └── [YourParty: EINGESTELLT]
├── Toolbox CT 100 (Caddy/Edge)
├── radio-node CT 130 ←TARGET
│   ├── AzuraCast (Streaming)
│   └── FraWo Radio Backend (FastAPI+PG+Redis)
├── storage-node CT 110 (CIFS)
├── vaultwarden CT 120
└── adguard CT 100+101

ÖFFENTLICH                       INTERN
├── frawo-tech.de (Odoo)         ├── *.hs27.internal (AdGuard)
├── cloud.frawo-tech.de ←fix     ├── :84xx Caddy Ports
├── radio.frawo-tech.de ←TODO    └── Tailscale für Admin
└── Cloudflare Tunnel (cloudflared CT 100)
```

---

## SPRINT 2026-05-25 — STATUS

### ✅ Heute erledigt

| Task | Was | Fix |
|------|-----|-----|
| #65 | rclone rate limiting | `--tpslimit 8 --tpslimit-burst 10` |
| #138 | Caddy gzip/zstd | `encode zstd gzip` alle Frontdoors |
| #229 | Email DMARC-Fix | p=reject → p=none, SMTP funktioniert |
| #229 | Trommlerzug Rechnung | INV/2026/00006 (100€) gesendet ✅ |
| #229 | Bodensee Auftrag | S00007 gesendet ✅ |
| #230 | CT 130 Static IP | 10.4.0.28 (war DHCP) |
| #59 | DNS AdGuard | 4 neue Einträge (radio-node, storage-node, pve, adguard-slave) |
| Odoo SSOT | 6 Tasks aktualisiert, 2 neue erstellt | Alle Notizen mit Details |

### 🔴 KRITISCH — Wolf sofort

| Odoo | Was | Wo | Anleitung |
|------|-----|-----|-----------|
| #224 | CF Tunnel cloud.frawo-tech.de | Cloudflare Dashboard | Zero Trust → Tunnels → Ingress → 10.4.0.21 |
| #199 | Stockenweiler einschalten | Physisch Rothkreuz | Vor Ort |
| #159 | PBS Netzwerk-Fix | PVE Web UI | VM 240 → Console → ip addr / cloud-init prüfen |
| #226 | frawo-docker-1 SSH-Key | win-j1aenasv2fj | SSH-Key von dem PC auf frawo-docker-1 kopieren |

### 🟡 NÄCHSTE AGENT-TASKS (automatisierbar sobald Voraussetzungen erfüllt)

| Odoo | Was | Wartet auf | Priorität |
|------|-----|-----------|-----------|
| #162 | AzuraCast → CT 130 migrieren | Stockenweiler online (oder Entscheidung ohne) | Hoch |
| - | FraWo Radio Backend deployen (CT 130) | AzuraCast-Migration | Hoch |
| #225 | hs27-media: Radio-Library auf music_ssd | Wolf-Entscheidung + PVE-Wartung | Mittel |
| #227 | frawo-docker-1 Rolle + Dienste definieren | SSH-Key Wolf | Mittel |
| #84/#159 | PBS produktiv setzen | Netzwerk-Fix Wolf | Mittel |
| #197 | Website Brand Rollout | Odoo-Website-Zugang | Niedrig |
| #137 | JSON-LD Structured Data | Brand Rollout | Niedrig |
| #139 | WebP Bilder | Brand Rollout | Niedrig |

### 🛑 BLOCKIERT (wartet auf Stockenweiler)

| Was | Warum |
|-----|-------|
| Home Assistant Eltern | Stockenweiler-PVE offline |
| frawo-docker-1 volle Integration | Stockenweiler offline → kein Vor-Ort-Zugang |
| YourParty Cleanup/Archiv | Stockenweiler-Daten (eingestellt, aber aufräumen) |

---

## ENTSCHEIDUNGEN (ADRs)

| Entscheidung | Begründung | Datum |
|-------------|-----------|-------|
| AzuraCast Ziel: CT 130 (radio-node) | Best Practice: dedizierter Radio-Node, 10.4.0.28 | 2026-05-25 |
| FraWo Radio Backend (FastAPI) → CT 130 | Gemeinsam mit AzuraCast, low latency, single node | 2026-05-25 |
| YourParty: EINGESTELLT | Kein aktiver Betrieb mehr, Code archivieren | 2026-05-25 |
| frawo-docker-1: Schiffscontainer Stockenweiler | Physischer Standort bestätigt, Rolle noch TBD | 2026-05-25 |
| DMARC: p=none | DKIM fehlt → p=reject blockiert Strato-Relay | 2026-05-25 |
| StudioPC: nur Entwicklung | Keine Produktions-Services, Docker nur lokal | 2026-05-25 |
| hs27-media CIFS Stale | Kernel-Bug, Fix: PVE-Neustart Wartungsfenster | 2026-05-25 |
| rclone rate limit 8 TPS | Google Drive API-Quota-Fehler | 2026-05-25 |
| Swap 2GB VM 220 | OOM-Kill bei vollem RAM (2.4/2.9GB) | 2026-05-25 |
| ListenAddress 0.0.0.0 SSH | Private Subnet, Tailscale als VPN | 2026-05-25 |

---

## KONSOLIDIERTER NODE-ÜBERBLICK

| Node | Tailscale | Lokal-IP | Typ | Rolle |
|------|-----------|----------|-----|-------|
| proxmox-anker | 100.69.179.87 | 10.4.0.99 | PVE | Primary Hypervisor |
| toolbox | 100.82.26.53 | 10.4.0.20 | CT 100 | Edge/Ingress/Monitoring |
| frawo-docker-1 | 100.94.32.41 | ? | Phys. Server | Schiffscontainer Stockenweiler |
| stockenweiler-pve | 100.91.20.116 | 192.168.178.172 | PVE | Site B Hypervisor (offline) |
| wolfstudiopc | 100.98.31.60 | 10.1.0.210 | Windows PC | Dev-Workstation |
| wolf-surface | 100.79.103.59 | - | Windows | Mobile Dev |
| wolf-zenbook | 100.76.249.126 | - | Linux | Linux Dev |
| surface-go-frontend | 100.106.67.127 | - | Linux | Frontend-Dev |
| villarechner420 | 100.85.153.121 | - | Windows | Villa-PC |
| wohnzimmertv | 100.84.241.124 | - | Android | Wohnzimmer TV |
| franz-iphone15 | 100.106.111.38 | - | iOS | Franz's Phone |
| pixel-9-pro | 100.83.213.17 | - | Android | Wolf's Phone |
| win-j1aenasv2fj | 100.97.147.67 | - | Windows | Stockenweiler-PC (SSH-Bridge zu frawo-docker-1) |

---

## ANTI-SPLIT-BRAIN REGELN

1. **Odoo-Task zuerst** — Kein Merge ohne offenen Task
2. **Commit-Referenz** — `task-<ID>` in Commits wenn möglich
3. **LIVE_CONTEXT.md** — Nach jedem Audit aktualisieren
4. **ROADMAP.md** — Brücke Odoo ↔ GitHub. Konflikt: Odoo für Status, GitHub für Konfiguration
5. **Agent markiert Tasks** — "In Arbeit" wenn gestartet, "Erledigt" wenn fertig. Wolf bestätigt.
6. **Keine Ghost-Services** — Jeder laufende Dienst ist in LIVE_CONTEXT dokumentiert
7. **Node-Rollen** — Jede Maschine hat eine klar definierte Rolle (keine Mehrfachbelegung ohne ADR)

---

*Letzte Aktualisierung: 2026-05-25 — Claude Sonnet 4.6 + Wolf*
