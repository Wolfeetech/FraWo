# ROADMAP — FraWo GbR Infrastruktur
**Stand: 2026-05-25 | Letzte Konsolidierung: Claude Sonnet 4.6 + Wolf**

**SSOT-Hierarchie:**
- **Odoo** (`FraWo_GbR` → "🚀 Homeserver 2027: Masterplan") → Wer macht was, Status, Priorität
- **GitHub** (diese Datei, `LIVE_CONTEXT.md`, `STATUS.md`) → Technische Wahrheit
- **Konflikt**: Odoo für Status, GitHub für Konfiguration

---

## ZIELARCHITEKTUR 2027 (Masterplan)

```
ANKER PVE (Primary)              STOCKENWEILER (Site B, 10.30.8.x)
├── Odoo ERP (VM 220)            ├── frawo-docker-1 (10.30.8.22)
├── Nextcloud (VM 300)           │   Debian 13, 188G, SSH ✅
├── Paperless (VM 330)           │   Rolle: TBD nach Audit
├── PBS Backup (VM 240) ←fix     │   (Monitoring/Backup/Staging)
├── HAOS FraWo (VM 210)          │   HAOS Eltern → Option hier
├── Toolbox CT 100 (Caddy/Edge)  └── win-j1aenasv2fj (Management)
├── radio-node CT 130 ✅ LIVE         Stockenweiler PVE: EINGESTELLT
│   ├── AzuraCast ✅ (Port 80)        YourParty: EINGESTELLT
│   ├── Navidrome ✅ (Port 4533)
│   └── FraWo Radio Backend ←TODO
├── storage-node CT 110 (CIFS)
├── vaultwarden CT 120
└── adguard CT 100+101

ÖFFENTLICH                       INTERN (via AdGuard + Caddy CT 100)
├── frawo-tech.de ✅ (Odoo)      ├── odoo.hs27.internal ✅
├── cloud.frawo-tech.de ←fix CF  ├── cloud.hs27.internal ✅
├── radio.frawo-tech.de ←TODO    ├── radio.hs27.internal ✅ (CT 130)
└── Cloudflare Tunnel            ├── ha/media/paperless/vault ✅
                                 └── navidrome.hs27.internal ←TODO
```

---

## SPRINT 2026-05-25 — STATUS

### ✅ Heute erledigt

| Task | Was | Fix |
|------|-----|-----|
| #65 | rclone rate limiting | `--tpslimit 8 --tpslimit-burst 10` |
| #138 | Caddy gzip/zstd + IP-Fix | Alle 10.1.0.x → 10.4.0.x, ha/media/radio Routes neu |
| #229 | Email DMARC-Fix | p=reject → p=none, SMTP funktioniert |
| #229 | Trommlerzug Rechnung | INV/2026/00006 (100€) gesendet ✅ |
| #229 | Bodensee Auftrag | S00007 gesendet ✅ |
| #230 | CT 130 Static IP | 10.4.0.28 (war DHCP) |
| #59 | DNS AdGuard | 4 neue Einträge (radio-node, storage-node, pve, adguard-slave) |
| #162 | **AzuraCast Migration CT 130** | War bereits erledigt (6 Wochen live) — Caddy-Route umgestellt |
| CT 130 RAM | 2GB → 4GB | `pct set 130 -memory 4096` live |
| frawo-docker-1 | SSH zugänglich | 10.30.8.22, Debian 13, 188G, sudo ✅ |
| Git Push | DNS-Fix | curloptResolve Workaround (Tailscale DNS kaputt) |
| Odoo SSOT | 10+ Tasks aktualisiert, 8 neue erstellt | Vollständiger Stand |

### 🔴 KRITISCH — Wolf sofort

| Odoo | Was | Wo | Anleitung |
|------|-----|-----|-----------|
| #235 | **Tailscale DNS Fix** | tailscale.com/admin/dns | Split DNS hs27.internal: 10.1.0.20 → 10.4.0.20 — StudioPC ohne Internet-DNS |
| #224 | CF Tunnel cloud.frawo-tech.de | Cloudflare Dashboard | Zero Trust → Tunnels → Public Hostname → 10.4.0.21 |
| #199 | Stockenweiler PVE einschalten | Physisch Rothkreuz | Vor Ort |
| #159 | PBS Netzwerk-Fix | PVE Web UI | VM 240 → Console → ip addr / cloud-init prüfen |
| #226 | frawo-docker-1 SSH-Key | Von win-j1aenasv2fj (10.30.8.21) | `ssh wolf@10.30.8.22 "mkdir -p ~/.ssh && echo 'ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAICps0AFY3eiRRj/h7j1jVf+IynVbZqwA2wOErxCa9cms studiopc@hs27-ops' >> ~/.ssh/authorized_keys && chmod 700 ~/.ssh && chmod 600 ~/.ssh/authorized_keys"` |

### 🟡 NÄCHSTE AGENT-TASKS (automatisierbar sobald Voraussetzungen erfüllt)

| Odoo | Was | Wartet auf | Priorität |
|------|-----|-----------|-----------|
| #238 | VM 220 AzuraCast (Port 8080) abschalten | Wolf-Bestätigung (gleiche Daten?) | Hoch |
| #233 | FraWo Radio Backend deployen (CT 130) | VM 220 Azura abgeschaltet | Hoch |
| #240 | radio.frawo-tech.de → Cloudflare Tunnel | Wolf (CF Dashboard) | Hoch |
| #225 | hs27-media: Radio-Library auf music_ssd | PVE-Neustart (CIFS-Stale) | Mittel |
| #234 | frawo-docker-1 Rolle + Dienste definieren | SSH-Key (#226) | Mittel |
| #239 | Navidrome: navidrome.hs27.internal Route | - | Niedrig |
| #84/#159 | PBS produktiv setzen | Netzwerk-Fix Wolf | Mittel |
| #197 | Website Brand Rollout | Odoo-Website-Zugang | Niedrig |

### 🛑 OFFEN — Wolf-Entscheidung nötig

| Was | Frage |
|-----|-------|
| HAOS Eltern (#241) | frawo-docker-1 (Docker) ODER verzichten? |
| frawo-docker-1 Rolle (#234) | Monitoring / Backup-Relay / Staging / Kombi? |
| VM 220 AzuraCast abschalten (#238) | CT 130 = gleiche Daten wie VM 220? Bestätigung Wolf |

---

## ENTSCHEIDUNGEN (ADRs)

| Entscheidung | Begründung | Datum |
|-------------|-----------|-------|
| AzuraCast Ziel: CT 130 (radio-node) | Best Practice: dedizierter Radio-Node, 10.4.0.28 | 2026-05-25 |
| FraWo Radio Backend (FastAPI) → CT 130 | Gemeinsam mit AzuraCast, low latency, single node | 2026-05-25 |
| YourParty: EINGESTELLT | Kein aktiver Betrieb mehr, Code archivieren | 2026-05-25 |
| Stockenweiler PVE: EINGESTELLT | Durch frawo-docker-1 + win-jx ersetzt, kein Einschalten mehr | 2026-05-25 |
| frawo-docker-1: DER Stockenweiler Compute-Node | Debian 13, 188G, SSH aktiv, ersetzt PVE | 2026-05-25 |
| AzuraCast CT 130: bereits seit 6 Wochen live | Migration war erledigt, Caddy umgestellt | 2026-05-25 |
| CT 130 RAM: 4GB | Swap-Druck wegen Navidrome+AzuraCast, hot-upgrade | 2026-05-25 |
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
| frawo-docker-1 | 100.94.32.41 | 10.30.8.22 | Phys. Server | Schiffscontainer Stockenweiler, Debian 13 Trixie |
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
