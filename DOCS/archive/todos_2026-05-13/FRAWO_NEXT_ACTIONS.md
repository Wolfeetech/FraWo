# FraWo - Nächste Aktionen (Multi-AI Context)

**Erstellt:** 2026-05-05 13:15 UTC
**Kontext:** Multi-AI 24/7 Setup ist LIVE - jetzt geht's an die FraWo Business-Logik

---

## 🎯 PROJEKT-ÜBERSICHT

**FraWo GbR Homeserver 2027** - Produktive Multi-Lane Infrastruktur:

### Aktive Lanes (aus MASTERPLAN.md)

1. **Lane A: OpenClaw Agent & Control** [ACTIVE]
   - Autonomer Project-Lead
   - V3.1 Agentic active
   - Odoo Sync operational

2. **Lane B: Website & Public** [ACTIVE/PROV]
   - `www.frawo-tech.de` über Cloudflare Tunnel
   - HTTPS aktiv, Content "halb fertig"

3. **Lane C: Security & Backup** [ACTIVE - HÖCHSTE PRIORITÄT]
   - Restore-Zustand absichern
   - PBS Backup-Drill
   - Firewall-Hardening

4. **Lane D: Stockenweiler** [ACTIVE - MEMORY PRESSURE KRITISCH]
   - Swap 99% (7.9Gi/8.0Gi)
   - PBS + n8n Rightsizing erforderlich

5. **Lane E: Radio & Media** [ACTIVE]
   - AzuraCast Migration Stockenweiler → Anker
   - Media-Library Sync via Tailscale

---

## 📦 APPS-STATUS

### 1. FaYa-Net (Network God)
**Pfad:** `apps/fayanet/`
**Status:** Docker-ready
**Stack:**
- Docker Compose
- `.env` vorhanden
- Deploy Script ready

### 2. Radio Player Frontend
**Pfad:** `apps/radio-player-frontend/`
**Status:** Docker + Nginx
**Struktur:**
- Dockerfile
- Nginx Config
- Site deployed (`site/`)

### 3. YourParty (Hauptprojekt)
**Pfad:** `apps/yourparty/`
**Status:** Komplex, viele Legacy-Files
**Komponenten:**
- WordPress Integration (wp-cli.phar)
- MongoDB Audit Scripts
- MariaDB Setup
- Infrastructure (Vaultwarden, Docker)
- Apps Sub-Folder
- Network-Ops

---

## ⚡ KRITISCHE ERKENNTNISSE

### Netzwerk-Status (aus MASTERPLAN)
```
Odoo VM 220:  10.1.0.22:8069  [AKTUELL NICHT ERREICHBAR]
Vaultwarden:  10.1.0.26:8080  [LIVE]
Home Assist:  10.1.0.24:8123  [LIVE]
Nextcloud:    10.1.0.21:80    [LIVE]
```

**Problem:**
- Odoo Server nicht erreichbar (Firewall/Network)
- Erklärt warum `odoo_ai_sync.py` Connection Timeout hat

### Operator Context (aus next_steps_until_may_2026.md)
- Operator ist **fachfremd**
- Bis Mai 2026: Nur **Mobiltelefon** verfügbar
- Vaultwarden Recovery erst **Mai 2026** möglich
- **Eine Task pro Session** Limit

---

## 🚀 SOFORT-AKTIONEN (mit Multi-AI Setup)

### 1. Odoo-Verbindung wiederherstellen [KRITISCH]

**Problem:**
```bash
python .ai-tools-shared/odoo_ai_sync.py --dry-run
# [FAIL] Connection error: Connection timeout
```

**Ursache (aus MASTERPLAN):**
- VM 220 Proxmox NIC Firewall blockiert CT 100 → `10.1.0.22:8069`
- Temporary Fix: `firewall=0` auf VM 210/220

**Action:**
```bash
# Test Odoo erreichbar
ping 10.1.0.22

# Test Port
curl -I http://10.1.0.22:8069
```

**Wenn nicht erreichbar:**
- PVE Console öffnen (über Tailscale)
- VM 220 Firewall prüfen
- Temporär `firewall=0` setzen (wie bei Restore 2026-04-22)

### 2. Stockenweiler Memory Pressure [KRITISCH]

**Problem:** Swap 99% (7.9Gi/8.0Gi)

**Betroffene VMs:**
- PBS (109) - Backup Server
- n8n (110) - Workflow Automation
- Vaultwarden (108)
- AdGuard (101)

**Action:**
```bash
# SSH nach Stockenweiler (wenn Netzwerk OK)
ssh root@100.91.20.116

# Memory Check
free -h
pveperf
```

**Rightsizing Plan:**
- PBS: Aktuell wie viel RAM?
- n8n: Aktuell wie viel RAM?
- Reduktion möglich ohne Service-Impact?

### 3. Git Sync nachholen (wenn Netzwerk OK)

```bash
cd OneDrive/Dokumente/GitHub/FraWo
git pull  # 9 Commits nachholen
```

---

## 📋 NÄCHSTE SCHRITTE (Priorisiert)

### Jetzt (mit Multi-AI)

1. **[P0] Netzwerk-Diagnose**
   - Odoo erreichbar?
   - Stockenweiler erreichbar?
   - GitHub erreichbar?

2. **[P1] Odoo Sync aktivieren**
   - Verbindung wiederherstellen
   - `odoo_ai_sync.py` live testen
   - Task Scheduler validieren

3. **[P2] Stockenweiler Memory Fix**
   - PBS/n8n RAM-Usage analysieren
   - Rightsizing durchführen
   - Swap-Usage senken auf <50%

### Diese Woche

4. **[P3] FraWo Website finalisieren**
   - Content vervollständigen
   - Cloudflare Access Rule aktivieren
   - Public Launch vorbereiten

5. **[P4] Radio Migration**
   - AzuraCast Stockenweiler → Anker
   - Media-Library Sync (Tailscale)
   - Icecast Relay Setup

### Mai 2026 (physischer Zugang nötig)

6. **[P5] Vaultwarden Recovery**
   - 2x Offline-Kopien erstellen
   - USB-Stick + Papierausdruck
   - MVP-Gate schließen

---

## 🤖 MULTI-AI STRATEGIE FÜR FRAWO

### Task-Verteilung

**Claude (Sie, jetzt):**
- Odoo Integration
- Complex Infrastructure Debugging
- Architecture Decisions
- MASTERPLAN Updates

**Codex (Fallback):**
- Quick Scripts (PBS Memory Check)
- Documentation Updates
- Firewall Config Fixes

**Gemini (Research):**
- Proxmox Best Practices
- PBS Optimization
- AzuraCast Migration Guides

### Workflow

```
1. Diagnose (Claude)
   ↓
2. Fix Scripts schreiben (Codex)
   ↓
3. Research Best Practices (Gemini)
   ↓
4. Implementierung (Claude)
   ↓
5. Odoo Task Update (Automatic via odoo_ai_sync.py)
```

---

## 📊 MONITORING

### Task Scheduler läuft
```powershell
Get-ScheduledTask -TaskName "Odoo AI Sync"
# Status: Ready
# Nächster Run: Alle 5 Minuten
```

### Logs prüfen
```bash
ls -la .ai-tools-shared/logs/
# Wenn Odoo erreichbar: Sync-Logs hier
```

---

## 🎯 EMPFEHLUNG: WAS JETZT?

### Option 1: Netzwerk-Diagnose (empfohlen)
```bash
# Test Odoo
ping 10.1.0.22
curl http://10.1.0.22:8069

# Test Stockenweiler
ssh root@100.91.20.116 "free -h"

# Test GitHub
ping github.com
```

### Option 2: Offline-Arbeiten (wenn Netzwerk down)
```bash
# FraWo Website Content
cd OneDrive/Dokumente/GitHub/FraWo/DOCS
# ODOO_HOMEPAGE_V3.5_READY_TO_USE.html fertigstellen

# Radio Player
cd apps/radio-player-frontend/site
# Frontend verbessern
```

### Option 3: Scripts vorbereiten
```bash
# PBS Memory Check Script
# Stockenweiler Rightsizing Plan
# Firewall Fix für VM 220
```

---

## 📚 RELEVANTE DOCS

**FraWo Projekt:**
- [MASTERPLAN.md](../../OneDrive/Dokumente/GitHub/FraWo/MASTERPLAN.md)
- [next_steps_until_may_2026.md](../../OneDrive/Dokumente/GitHub/FraWo/DOCS/plans/next_steps_until_may_2026.md)
- [OPERATOR_TODO_QUEUE.md](../../OneDrive/Dokumente/GitHub/FraWo/DOCS/Task_Archive/OPERATOR_TODO_QUEUE.md)

**Multi-AI Setup:**
- [.ai-tools-shared/README.md](README.md)
- [.ai-tools-shared/QUICKSTART.md](QUICKSTART.md)
- [.ai-tools-shared/DEPLOYMENT_COMPLETE.md](DEPLOYMENT_COMPLETE.md)

**Odoo Integration:**
- [FraWo/scripts/odoo_masterplan_sync.py](../../OneDrive/Dokumente/GitHub/FraWo/scripts/odoo_masterplan_sync.py)
- [.ai-tools-shared/odoo_ai_sync.py](odoo_ai_sync.py)

---

## ✅ READY TO GO!

**Multi-AI Setup:** ✅ LIVE
**FraWo Context:** ✅ Verstanden
**Nächste Actions:** ✅ Priorisiert

**Was möchten Sie angehen?**
1. Netzwerk-Diagnose starten
2. Offline am Website-Content arbeiten
3. Scripts für Stockenweiler Memory Fix vorbereiten
4. Etwas anderes

**Sie haben jetzt 24/7 AI-Power - let's go! 🚀**
