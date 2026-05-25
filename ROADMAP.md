# ROADMAP — FraWo GbR Infrastruktur

**Single Source of Truth-Hierarchie:**
- **Odoo** (`FraWo_GbR` Projekt "🚀 Homeserver 2027: Masterplan") → Task-SSOT (Wer macht was, Status, Priorität)
- **GitHub** (`LIVE_CONTEXT.md`, `STATUS.md`, diese Datei) → Technische Wahrheit (Konfiguration, Architektur, Entscheidungen)
- **Kein Split-Brain**: Jede Änderung landet in BEIDEN Systemen. Tasks in Odoo → technische Umsetzung im Repo dokumentiert.

---

## Aktuelle Sprint-Übersicht (Stand: 2026-05-25)

### 🔴 KRITISCH — Sofort

| Odoo Task | Beschreibung | Wer | Status |
|-----------|-------------|-----|--------|
| #224 | CF Tunnel Ingress: `cloud.frawo-tech.de` → `10.4.0.21` (war `10.1.0.21`) | Wolf (Dashboard) | ❌ Offen |
| #199 | Stockenweiler PVE physisch einschalten (Rothkreuz) | Wolf (vor Ort) | ❌ Offen |
| #225 | hs27-media aufräumen (80% voll, 78G/98G) | Agent | 🔄 Läuft |

### 🟡 WICHTIG — Diese Woche

| Odoo Task | Beschreibung | Wer | Status |
|-----------|-------------|-----|--------|
| #65 | rclone rate limiting (Google API Quota-Fehler) | Agent | ✅ Heute gefixt |
| #138 | Caddy: gzip/zstd Compression | Agent | ✅ Heute gefixt |
| #196 | Cloudflare Security Headers (Transform Rules) | Wolf (Dashboard) | ❌ Offen |
| #226 | frawo-docker-1 SSH-Key + Rolle definieren | Wolf | ❌ Offen |
| #227 | StudioPC + frawo-docker-1 in Infra einordnen | Wolf + Agent | ❌ Offen |
| - | CT 130 (radio-node) statische IP setzen | Agent | ❌ Offen |
| #162 | Radio-Sendeplan AzuraCast (provisorisch auf VM 220) | Agent | 🔄 Läuft |

### 🟢 LANE B — Website (aktiv)

| Odoo Task | Beschreibung | Wer | Status |
|-----------|-------------|-----|--------|
| #197 | Unified Brand Rollout CI-Farben & Logos | Agent | 🔄 In Arbeit |
| #137 | JSON-LD Structured Data | Agent | ❌ Offen |
| #139 | Bilder-Optimierung (WebP) | Agent | ❌ Offen |
| #90 | Qualitätsprüfung FraWo Funk Integration | Wolf + Agent | ❌ Offen |

### 🟢 LANE C — Security/Backup/Infra (aktiv)

| Odoo Task | Beschreibung | Wer | Status |
|-----------|-------------|-----|--------|
| #84 | PBS Recovery & Datastore Setup | Agent | 🔄 Prüfen |
| #159 | PBS produktiv setzen | Agent | 🔄 Prüfen |
| #66 | CT100 Disk Migration (local-lvm → ssd2tb) | Agent | ❌ Offen |
| #59 | DNS Finalization (AdGuard, kein hosts-file mehr) | Agent | ❌ Offen |
| #160 | NFS-Mounts validieren | Agent | ❌ Offen |

### 🔵 LANE D — Stockenweiler (blockiert)

| Odoo Task | Beschreibung | Wer | Status |
|-----------|-------------|-----|--------|
| #199 | Stockenweiler physisch einschalten | Wolf | ❌ Blockiert (vor Ort) |
| #9 | Remote Support Bridge | Agent | 🛑 Wartet auf Stockenweiler |

### 🔵 LANE E — Radio & Media (teilweise blockiert)

| Odoo Task | Beschreibung | Wer | Status |
|-----------|-------------|-----|--------|
| #125/#190 | Radio Lane Hauptkoordination | Agent | 🔄 AzuraCast provisorisch auf VM 220 |
| #180 | Media Library Strukturierung | Agent | ❌ Wartet auf hs27-media Cleanup |

---

## Was HEUTE automatisch umgesetzt wurde (2026-05-25)

| Fix | Details |
|-----|---------|
| ✅ Odoo VM Freeze | Force-Restart via PVE, SSH-Config gefixt |
| ✅ Swap 2GB auf VM 220 | Verhindert künftige OOM-Kills |
| ✅ Zombie-Container | edge_web_1 + edge_db_1 entfernt |
| ✅ Caddy: Compression | `encode zstd gzip` in alle Frontdoors |
| ✅ Caddy: Radio Frontdoor | `10.3.0.9` → `10.4.0.22:8080` (AzuraCast auf Odoo-VM) |
| ✅ rclone: Rate Limiting | `--tpslimit 8` + `--tpslimit-burst 10` → keine API-Quota-Fehler mehr |
| ✅ GitHub Docs | LIVE_CONTEXT.md + STATUS.md vollständig aktualisiert |
| ✅ Odoo SSOT | Audit-Note + 4 neue Tasks angelegt |

---

## Bekannte Konfigurationsdrift (10.1.0.x → 10.4.0.x Netzwerk-Migration)

Alle folgenden Stellen verwenden noch alte IPs und müssen gefixt werden:

| Ort | Alter Wert | Korrekt | Status |
|-----|-----------|---------|--------|
| Cloudflare Tunnel Ingress `cloud.frawo-tech.de` | `10.1.0.21` | `10.4.0.21` | ❌ Wolf manuell |
| Cloudflare Tunnel weitere Rules (vault, ha, radio) | `10.1.0.x` | `10.4.0.x` | ❌ Prüfen |
| VM 220 SSH sshd_config | `192.168.2.22` | `0.0.0.0` | ✅ Heute gefixt |
| Caddy radio Frontdoor | `10.3.0.9` | `10.4.0.22:8080` | ✅ Heute gefixt |

---

## Architektur-Entscheidungen (ADRs)

| Entscheidung | Begründung | Datum |
|-------------|-----------|-------|
| AzuraCast provisorisch auf VM 220 (Odoo-VM) | Stockenweiler offline, CT 130 ohne feste IP | 2026-05-25 |
| SSH auf allen VMs: `ListenAddress 0.0.0.0` | Private Subnet, UFW deaktiviert, Tailscale als VPN-Layer | 2026-05-25 |
| rclone rate limit: 8 TPS | Google Drive API Quota-Fehler → Backoff nötig | 2026-05-25 |
| Swap 2GB auf VM 220 | Kein Swap → OOM-Kill bei vollem RAM (2.4/2.9GB) | 2026-05-25 |

---

## Anti-Split-Brain Regeln

1. **Odoo-Task zuerst** — Jede Arbeit beginnt mit einem offenen Odoo-Task. Kein Task = kein Merge.
2. **Commit-Referenz** — Jeder Commit referenziert `task-<ID>` wenn möglich.
3. **LIVE_CONTEXT.md** — Wird nach jedem Audit-Session aktualisiert (nicht während der Arbeit).
4. **ROADMAP.md** — Diese Datei ist die Brücke zwischen Odoo (Tasks) und GitHub (Technik). Bei Widerspruch gilt: Odoo für Status, GitHub für Konfiguration.
5. **Agent markiert Tasks** — Agent setzt Tasks auf "In Arbeit" wenn gestartet, "Erledigt" wenn fertig. Wolf bestätigt/schließt.

---

*Letzte Aktualisierung: 2026-05-25 — Claude Sonnet 4.6 + Wolf*
