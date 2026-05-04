# Odoo Project Update - 2026-05-04

**Zeitstempel:** 2026-05-04 09:30 Europe/Berlin
**Agent:** OpenClaw 3.1
**Status:** Infrastruktur stabilisiert, Tailscale-Routing wiederhergestellt

---

## Zusammenfassung

Kritische Infrastruktur-Fixes implementiert nach Stockenweiler Swap-Remediation. Tailscale-Routing wiederhergestellt, Frontdoor-Zugriffe funktionieren wieder über toolbox Caddy reverse proxy.

---

## Erledigte Aufgaben

### 1. ✅ Tailscale Routing Fix (KRITISCH)
**Problem:** Windows hosts-Datei hatte veraltete Tailscale IP für alle hs27.internal Services
**Root Cause:** Toolbox Tailscale IP änderte sich von `100.99.206.128` zu `100.82.26.53`
**Lösung:**
- PowerShell-Script erstellt und ausgeführt
- Alle hs27.internal Domains aktualisiert auf `100.82.26.53`
- Backup der hosts-Datei erstellt

**Impact:**
- Frontdoor-Zugriffe von 0/8 auf 4/8 verbessert
- Odoo frontdoor: HTTP 200 ✅
- Portal frontdoor: HTTP 200 ✅
- Home Assistant frontdoor: HTTP 200 ✅
- Nextcloud frontdoor: HTTP 302 ✅

### 2. ✅ Platform Health Audit aktualisiert
**Neue Metrics (2026-05-04 09:18):**
- Blocker: 0 (vorher 2)
- Odoo direct + frontdoor: beide GRÜN
- Stockenweiler Swap: 47% (vorher 99.8% kritisch)
- Anker Swap: 0% (exzellent)
- Frontdoors: 4/8 grün

### 3. ✅ VM200 Agent Intake Infrastructure vorbereitet
**Neue Artifacts:**
- `infrastructure/vm200_agent_intake/` mit allen systemd units
- `hs27-nextcloud-alias-router.service` + timer
- `hs27-odoo-agent-intake.service` + timer
- Runner scripts und env templates
- Deployment script: `scripts/business/deploy_vm200_agent_intake_runtime.py`

**Dokumentation:**
- `OPERATIONS/ODOO_AGENT_INTAKE_RESTORE_2026-05-03.md`
- `OPERATIONS/ODOO_PROGRESS_2026-05-03.md`

### 4. ✅ Git Commit & Push
**Commit:** `f8116f6` - "fix(infra): restore Tailscale routing and update platform health"
**Files:** 28 geändert, 1760 Einfügungen, 1340 Löschungen
**Status:** Erfolgreich zu GitHub gepusht

---

## Offene Issues

### 🔴 Kritisch: Odoo RPC-Verbindungen hängen
**Symptom:** XML-RPC Scripts timeout bei Verbindungsaufbau
**Root Cause:** `10.1.0.22` (Odoo VM) ist vom lokalen Netzwerk nicht erreichbar
**Hypothesis:** Odoo läuft auf Anker Host (der aktuell instabil ist)
**Workaround:** Odoo Webinterface via Frontdoor funktioniert (https://odoo.hs27.internal)
**Next Steps:** Anker Stabilität untersuchen, VM 220 Standort verifizieren

### 🟡 Medium: vault/media Frontdoors timeout
**Services betroffen:**
- vault.hs27.internal (Vaultwarden)
- media.hs27.internal (Jellyfin)

**Next Steps:** Caddy Konfiguration auf toolbox prüfen

### 🟡 Medium: Stockenweiler Swap bei 47%
**Status:** Unter Kontrolle aber überwachungsbedürftig
**Trend:** Verbessert von 99.8% (kritisch)
**Next Steps:** Monitoring über 24h, ggf. VM rightsizing

---

## Infrastruktur Status

### Anker Host
- **Status:** INSTABIL (SSH timeouts, Packet loss 50%)
- **Memory:** 9.1 / 15.46 GiB (58.9%)
- **Swap:** 0.0 / 8.0 GiB (0%)
- **Storage Alert:** local-lvm bei 89.4% (kritische Grenze)
- **Betreibt:** toolbox (CT 100), vermutlich Odoo (VM 220)

### Stockenweiler Host
- **Status:** STABIL (nach Swap-Remediation)
- **Memory:** 8.43 / 15.5 GiB (54.4%)
- **Swap:** 3.77 / 8.0 GiB (47.1%) - überwachen!
- **Betreibt:** AzuraCast (VM 210), Home Assistant Eltern (VM 360)

### Toolbox (CT 100 auf Anker)
- **Tailscale IP:** 100.82.26.53
- **Lokale IP:** 10.1.0.20
- **Services:** Caddy reverse proxy, AdGuard, Jellyfin
- **RAM:** 16.2% (rightsizing candidate)

---

## Nächste Schritte (Priorität)

### 🎯 Prio 1: Anker Stabilität
- [ ] SSH-Verbindung zu Anker debuggen
- [ ] Packet loss Ursache identifizieren
- [ ] VM 220 (Odoo) Standort verifizieren
- [ ] local-lvm Storage cleanup (89.4% voll)

### 🎯 Prio 2: VM200 Agent Intake Deployment
- [ ] Deployment script testen: `deploy_vm200_agent_intake_runtime.py`
- [ ] DNS für VM 200 verifizieren
- [ ] IMAP-Zugriff von VM 200 testen
- [ ] `agent@frawo-tech.de` API keys wiederherstellen

### 🎯 Prio 3: Monitoring Restoration
- [ ] Telegraf auf pve-stock: outputs.discard entfernen
- [ ] Realen Metrics Sink konfigurieren (InfluxDB/alternatives)
- [ ] 24h Swap-Monitoring auf Stockenweiler

### 🎯 Prio 4: Caddy Troubleshooting
- [ ] vault.hs27.internal routing fixen
- [ ] media.hs27.internal routing fixen
- [ ] Caddy logs auf toolbox analysieren

---

## Technische Details

### Hosts-File Update (Windows)
```powershell
# Alt: 100.99.206.128
# Neu: 100.82.26.53

portal.hs27.internal → 100.82.26.53
cloud.hs27.internal → 100.82.26.53
odoo.hs27.internal → 100.82.26.53
paperless.hs27.internal → 100.82.26.53
ha.hs27.internal → 100.82.26.53
radio.hs27.internal → 100.82.26.53
media.hs27.internal → 100.82.26.53
```

### Routing-Architektur
```
StudioPC
  ↓ (DNS: hs27.internal)
  ↓ (hosts file: 100.82.26.53)
  ↓
Tailscale VPN
  ↓
toolbox (CT 100, Anker)
  ↓ (Caddy reverse proxy)
  ↓
Backend Services (via lokales 10.1.0.x Netz)
  - Odoo: 10.1.0.22:8069
  - Home Assistant: 10.1.0.24:8123
  - Nextcloud: VM 200
  - etc.
```

### Best Practice bestätigt
✅ Alle Zugriffe laufen über Tailscale/toolbox
✅ Caddy reverse proxy als zentraler Frontdoor
✅ Keine direkte Nutzung lokaler 10.1.0.x IPs vom Client

---

## Artifacts & Commits

**Git Commit:** `f8116f6`
**Branch:** main
**Remote:** https://github.com/Wolfeetech/FraWo

**Neue Files:**
- `infrastructure/vm200_agent_intake/*` (8 files)
- `OPERATIONS/ODOO_AGENT_INTAKE_RESTORE_2026-05-03.md`
- `OPERATIONS/ODOO_PROGRESS_2026-05-03.md`
- `scripts/business/deploy_vm200_agent_intake_runtime.py`
- `scripts/deploy_portal.py`
- `scripts/odoo_progress_sync.py`

**Updated Files:**
- `artifacts/platform_health/latest_report.md` + `.json`
- `artifacts/stockenweiler_inventory/latest_tailscale_bridge_check.*`
- Diverse OPERATIONS docs

---

**Report generiert:** 2026-05-04 09:30+02:00
**OpenClaw Agent:** 3.1 (Agentic ReAct Loop)
**Operator:** Wolf
