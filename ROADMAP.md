> ⚠️ **TEILWEISE VERALTET.** Aktueller Live-Stand: **[NOW.md](NOW.md)**. Kern-Korrekturen: frawo-docker-1 = VMware-VM auf **Flos** Host (kein HW-Zugriff; Wolfs Eltern = Testkunden). Echte Subnetze: Rothkreuz 10.1.0.0/24 + 10.3.0.0/24, Stockenweiler-ESXi 10.30.8.0/24, ProDesk/Easybox 192.168.2.0/24 (NICHT 10.4.0.x). Domain = **frawo.tech**. Easybox → UCG → 10.1.0.x.

# ROADMAP — FraWo GbR Infrastruktur
**Stand: 2026-05-28 | Letzte Konsolidierung: Claude Sonnet 4.6 + Wolf**

**SSOT-Hierarchie:**
- **Odoo** (`FraWo_GbR` → `🚀 Homeserver 2027: Masterplan`) → Task-Wahrheit fuer Status, Owner, Prioritaet, Blocker, Review und Abschluss
- **Repo** (`ROADMAP.md`, `LIVE_CONTEXT.md`, `NETWORK_PLAN.md`, `MASTERPLAN.md`) → technische und betriebliche Wahrheit
- **STATUS.md** → Audit, nicht Governance
- **MEMORY.md** → Langzeitwissen, nicht fuehrende Runtime-Wahrheit

---

## ZIELARCHITEKTUR 2027 (Masterplan)

```
ANKER PVE (Primary)              STOCKENWEILER (Site B, 10.30.8.x)
├── Odoo ERP (VM 220)            ├── frawo-docker-1 (10.30.8.22)
├── Nextcloud (VM 300)           │   Debian 13, 188G, SSH ✅
├── Paperless (VM 330)           │   Rolle: Production Secondary Node
├── PBS Backup (VM 240) ←fix     │   Fokus: Monitoring / Relay / kuratierte Automation
├── HAOS FraWo (VM 210)          │   HAOS Eltern → Option hier
├── Toolbox CT 100 (Caddy/Edge)  └── win-j1aenasv2fj (Management)
├── radio-node CT 130 ✅ LIVE         Stockenweiler PVE: EINGESTELLT
│   ├── AzuraCast ✅ (Port 80)        YourParty: EINGESTELLT
│   ├── Navidrome ✅ (Port 4533)
│   └── FraWo Radio Backend ✅ (Port 9500)
├── storage-node CT 110 (CIFS)
├── vaultwarden CT 120
└── adguard CT 100+101

ÖFFENTLICH                       INTERN (via AdGuard + Caddy CT 100)
├── frawo-tech.de ✅ (Odoo)      ├── odoo.hs27.internal ✅
├── cloud.frawo-tech.de ←fix CF  ├── cloud.hs27.internal ✅
├── radio.frawo-tech.de ←TODO    ├── radio.hs27.internal ✅ (CT 130)
└── Cloudflare Tunnel            ├── ha/media/paperless/vault ✅
                                 └── navidrome.hs27.internal ✅
```

---

## SPRINT 2026-05-25 — STATUS

### ✅ Erledigt (2026-05-25 + 26 + 27)

| Task | Was | Fix |
|------|-----|-----|
| #65 | rclone rate limiting | `--tpslimit 8 --tpslimit-burst 10` |
| #138 | Caddy gzip/zstd + IP-Fix | Alle 10.1.0.x → 10.4.0.x, ha/media/radio Routes neu |
| #229 | Email DMARC-Fix | p=reject → p=none, SMTP funktioniert |
| #230 | CT 130 Static IP | 10.4.0.28 (war DHCP) |
| #59 | DNS AdGuard | radio-api, navidrome, radio-anker, radio-stock, radio-node etc. |
| #162/#238 | **AzuraCast Migration CT 130** | War bereits erledigt (6 Wochen live) — VM 220 AzuraCast abgeschaltet ✅ |
| CT 130 RAM | 2GB → 4GB | `pct set 130 -memory 4096` live |
| frawo-docker-1 | SSH zugänglich | 10.30.8.22, Debian 13, 188G, sudo ✅ |
| frawo-docker-1 | **Monitoring Stack deployed** | Portainer, Grafana, Prometheus und Node-Exporter produktiv dokumentiert ✅ |
| **Odoo #fix** | **restart=unless-stopped** | Container hatten kein Restart-Policy → nach VM-Reboot offline. Fix: unless-stopped + PVE startup order=3 ✅ |
| #239 | Navidrome Route | navidrome.hs27.internal → CT 130:4533 ✅ |
| **#233** | **FraWo Radio Backend** | **FastAPI deployed CT 130:9500, radio-api.hs27.internal ✅** |
| #226 | **frawo-docker-1 SSH** | SSH-Zugang bereinigt, Key deployed, PasswordAuth deaktiviert ✅ |
| #245 | n8n entdeckt | n8n lief undokumentiert auf frawo-docker-1:5678 → Caddy+DNS hinzugefügt ✅ |
| **CT 130** | **Tailscale live** | TUN-Device via LXC raw config, tailscale up --ssh, IP: 100.78.88.33 ✅ |
| **#242** | **Icecast Relay deployed** | frawo-docker-1:8000 relayed alle 3 Streams von CT 130 via Tailscale ✅ |
| Git Push | DNS-Fix | curloptResolve Workaround (Tailscale DNS kaputt) |
| **Security Audit** | **Live-Audit aller Nodes** | PVE, CT 100/110/120/130, VM 220/300/330, frawo-docker-1 — alle geprüft ✅ |
| **AdGuard Auth** | **Kritisch: war offen!** | Auth gesetzt, Vaultwarden aktualisiert, 401 fuer unauth bestaetigt ✅ |
| **Portainer Init** | War nie initialisiert | Initialisiert, Vaultwarden aktualisiert, Zugriff verifiziert ✅ |
| **Odoo Port** | 8069 war auf 0.0.0.0 | Geändert auf 127.0.0.1:8069 — kein Direktzugriff mehr ✅ |
| **#244** | **Vaultwarden Credentials** | 19/19 Items gespeichert | API-Pfad dokumentiert, Secrets im Vault statt im Repo ✅ |
| **#250** | **frawo-docker-1 UFW** | UFW aktiv | deny incoming, allow 100.64.0.0/10 + 10.30.8.0/24, via nsenter-Workaround ✅ |
| **#252** | **Nextcloud trusted_proxies** | 10.4.0.0/24 + 100.64.0.0/10 | via occ bereinigt, alte 10.1.0.x Einträge entfernt ✅ |
| **#253** | **CT 130 Samba gesichert** | bind interfaces + hosts allow | nur 10.4.0.0/24 + Tailscale ✅ |
| **Vaultwarden Admin-Token** | argon2id wiederhergestellt | Admin-Token rotiert und ausserhalb des Repos referenziert ✅ |
| **#256** | **StudioPC Monitoring** | windows_exporter 0.30.4 | Port 9182, Prometheus scrapt, Grafana-Dashboard live ✅ |
| **#237** | **frawo-docker-1 apt cleanup** | 00CDMountPoint entfernt | nsenter via privilegiertem Docker ✅ |
| **Odoo Kanban SSOT** | Bereinigung | 8 Tasks Erledigt, 9 Duplikate Canceled | Board reflekriert jetzt Realität ✅ |
| **SSH Config** | frawo-docker alias | `ssh frawo-docker` via hs27_ops_ed25519 | Direktzugriff ohne Tailscale-IP ✅ |
| **#171** | **Uptime Kuma** | 14 Monitore, Status-Page live | Status-Page erreichbar, Credentials nur in Vaultwarden ✅ |
| **CT 130 RAM** | 4GB → 6GB | Liquidsoap-Druck | pct set 130 -memory 6144 ✅ |
| **#257** | **Musik-Pipeline** | beets + AcoustID läuft | screen gdrive-sync + beets-import auf PVE Host aktiv 🔄 |

### ✅ Erledigt (2026-05-27 + 28)

| Task | Was | Fix |
|------|-----|-----|
| **Tailscale Split DNS** | hs27.internal → 100.82.26.53 (war 10.4.0.20) | Dashboard konfiguriert, DNS-Test ✅ |
| **#235** | Hosts-Datei cleanup | hs27.internal Einträge bereinigt ✅ |
| **cloud.frawo-tech.de** | CF Tunnel Nextcloud | HTTP 302→200 bestätigt ✅ (war 502) |
| **KRITISCH: Vault-Recovery** | vw_newkey.py hatte falschen sym key generiert — alle 429 Org-Items verschlüsselt mit falschem Key | Backup von 2026-05-26-02:12 extrahiert, original sym key wiederhergestellt, wolf akey neu verschlüsselt ✅ |
| **Vault Crypto-Kette** | Vollständige Python-Implementierung Bitwarden E2E Crypto: PBKDF2→HKDF→AES-CBC→RSA-OAEP→AES-CBC | Alle 437 Items entschlüsselbar, Cloudflare + Tailscale API-Token in Vault gespeichert ✅ |
| **Vault-Recovery** | Operator-Vaultzugriff nach Recovery bestaetigt | Alle Items sichtbar, keine Klartext-Referenz mehr im Repo ✅ |
| **#258** | Workflow-Doku | Brainstorm-Stage #86 erstellt, Odoo-Workflow dokumentiert | Agent |
| **#259** | **Dokument-Ökosystem: Option A** | Nextcloud als Hub — Wolf genehmigt 2026-05-27 | Agent |
| Nextcloud Admin | Passwort rotiert und via occ gesetzt | Login bestaetigt HTTP 200, Secret nur im Vault ✅ |
| Nextcloud Ordner | /Dokumente/Eingang, /Archiv, /Verträge, /Rechnungen | WebDAV MKCOL ✅ |
| Paperless Admin | Passwort rotiert und API-Token neu erzeugt | Zugriff verifiziert, Secret nur im Vault ✅ |
| **rclone + Cron** | VM 330: rclone move nextcloud:Dokumente/Eingang → Paperless consume alle 5 min | /etc/cron.d/nc-to-paperless, cron installiert ✅ |
| **Paperless post-consume** | PAPERLESS_POST_CONSUME_SCRIPT → NC/Archiv upload nach OCR | Script als bind-mount in Container ✅ |
| **End-to-End Test** | PDF upload NC/Eingang → Paperless Doc #14 "test_frawo" | Duplikat-Erkennung funktioniert ✅ |

### 🔴 KRITISCH — Wolf sofort

| Odoo | Was | Wo | Anleitung |
|------|-----|-----|-----------|
| #235 | ~~Tailscale DNS Fix~~ | ✅ DONE | Split DNS konfiguriert (Wolf 2026-05-26) |
| #224 | ~~CF Tunnel~~ | ✅ DONE | alle 6 Routen korrekt, alle Backends 200/302 (Wolf 2026-05-26) |
| ~~#244~~ | ~~Passwort-Audit~~ | ✅ DONE | 19 Credentials in Vaultwarden, agent@frawo-tech.de ✅ |
| CT 130 | ~~Tailscale Auth~~ | ✅ DONE | radio-node 100.78.88.33 live |
| #159 | PBS Netzwerk-Fix | PVE Web UI | VM 240 → Console → ip addr / cloud-init prüfen |
| ~~#249~~ | ~~Odoo Admin-PW~~ | 🛑 Blockiert bis Go-Live | Vault-Eintrag aktualisiert, Repo enthaelt keine Klartext-Referenz mehr |

### 🟡 NÄCHSTE AGENT-TASKS

| Odoo | Was | Wartet auf | Priorität |
|------|-----|-----------|-----------|
| #240 | ~~funk.frawo-tech.de CF-Tunnel~~ | ✅ DONE — 10.4.0.28 korrekt | — |
| #225 | hs27-media: Radio-Library auf music_ssd | PVE-Neustart (CIFS-Stale) → prüfen ob jetzt OK | Mittel |
| #234 | frawo-docker-1 Rolle dokumentieren | ✅ NETWORK_PLAN.md erstellt | Agent |
| #84/#159 | PBS produktiv setzen | Netzwerk-Fix Wolf | Mittel |
| #197 | Website Brand Rollout | Odoo-Website-Zugang | Niedrig |
| ~~#250~~ | ~~frawo-docker-1 UFW~~ | ✅ DONE | UFW aktiv |
| **#251** | PVE Firewall aktivieren | Wolf-Entscheidung welche Ports | HOCH |
| ~~#253~~ | ~~CT 130 Samba auf LAN beschränken~~ | ✅ DONE | bind interfaces, hosts allow |
| ~~#252~~ | ~~Nextcloud trusted_proxies~~ | ✅ DONE | 10.4.0.0/24 + 100.64.0.0/10 |
| **#259** | Dokument-Ökosystem (#259): Odoo Nextcloud Connector installieren | OCA-Modul-Test | Mittel |
| **BRAINSTORM** | Kalender-Integration: Google ↔ Odoo ↔ Nextcloud | Wolf-Freigabe | Niedrig |
| **#265** | HP ProDesk Stockenweiler: Eltern-PC + Server-Fallback | Wolf-Infos (#266) | Mittel |

### 🛑 OFFEN — Wolf-Entscheidung nötig

| Was | Frage |
|-----|-------|
| HAOS Eltern (#241) | frawo-docker-1 (Docker, hat bereits n8n + 31GB RAM frei) ODER verzichten? |
| Kalender (#260) | Google Calendar, Odoo Kalender, Nextcloud Kalender verbinden — welcher ist Master? |
| HP ProDesk (#265/#266) | = alter Stockenweiler PVE. Defekt, in Rothkreuz zur Reparatur. Wolf diagnostiziert vor Ort. |

---

## ENTSCHEIDUNGEN (ADRs)

| Entscheidung | Begründung | Datum |
|-------------|-----------|-------|
| AzuraCast Ziel: CT 130 (radio-node) | Best Practice: dedizierter Radio-Node, 10.4.0.28 | 2026-05-25 |
| FraWo Radio Backend (FastAPI) → CT 130 | Gemeinsam mit AzuraCast, low latency, single node | 2026-05-25 |
| YourParty: EINGESTELLT | Kein aktiver Betrieb mehr, Code archivieren | 2026-05-25 |
| Stockenweiler PVE: REAKTIVIERT | War eingestellt, ist defekt nach Rothkreuz, wird repariert → neue Rolle: Eltern-PC + Fallback | 2026-05-28 |
| frawo-docker-1: DER Stockenweiler Compute-Node | Debian 13, 188G, SSH aktiv, ersetzt PVE | 2026-05-25 |
| frawo-docker-1 Rolle: Monitoring+Relay+Automation | n8n+Portainer+Grafana+Prometheus+Icecast-Relay | 2026-05-26 |
| CT 130 Tailscale: 100.78.88.33 | LXC cgroup2+mount.entry statt tun=1 (PVE 9 inkompatibel) | 2026-05-26 |
| Icecast-Relay via Tailscale | frawo-docker-1 relayed von CT 130 100.78.88.33 — kein offener Port | 2026-05-26 |
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
| radio-node | **100.78.88.33** | 10.4.0.28 | CT 130 | AzuraCast + Navidrome + Radio Backend (neu: Tailscale ✅) |
| frawo-docker-1 | 100.94.32.41 | 10.30.8.22 | Phys. Server | Production Secondary Node: Monitoring, Relay, kuratierte Automation |
| stockenweiler-pve | 100.91.20.116 | 192.168.178.172 | HP ProDesk / PVE | 🔧 In Reparatur (Rothkreuz) — nach Fix: Eltern-PC + Fallback-Server (#265) |
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

---

## SECRET-REFERENZEN

- Alle produktiven Credentials, Tokens und Admin-Logins leben ausschliesslich in Vaultwarden.
- Repo-Dokumente duerfen nur noch den passenden Vault-Eintrag oder die betroffene Systemrolle referenzieren.

*Letzte Aktualisierung: 2026-05-28 — Claude Sonnet 4.6 + Wolf — Vault-Recovery, Dokument-Ökosystem (Nextcloud+Paperless), Kalender-Brainstorm*

---
*Zuletzt aktualisiert: 2026-06-06*

## Status je Phase

| Phase | Epic | Stand |
|-------|------|-------|
| Phase 1 Fundament | T481 | 🚀 95% — Radio-Voting live, Firewall gesichert, Tunnel-HA |
| Phase 2 Studio & Radio | T482 | ⚙️ 30% — Radio live, Voting läuft, Backend stabil |
| Phase 3 Business | T483 | 🚀 40% — CRM DE, Services-Portfolio, Angebots-Templates |
| Phase 4 Smart Home | T484 | 📋 5% — HA läuft, Setup ausstehend |
| Phase 5 Wachstum | T485 | 📋 10% — GrowBox Kanban-Stages, Pflanzen eingeordnet |
