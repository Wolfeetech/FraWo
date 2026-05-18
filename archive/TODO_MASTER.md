# FraWo - Master TODO Liste
**Erstellt:** 2026-05-13
**Status:** Konsolidiert aus allen TODO-Dokumenten

---

## 🚨 KRITISCH - Sofort erledigen

### 1. Netzwerk-Infrastruktur wiederherstellen
**Status:** ❌ BLOCKIERT
**Problem:**
- Proxmox Anker offline (10h)
- Stockenweiler offline (3d)
- Odoo Server nicht erreichbar
- Kein SSH-Zugriff möglich

**Action:**
```bash
# Geräte physisch prüfen und neustarten
# Tailscale auf allen Servern prüfen
# Netzwerk-Routing prüfen (10.1.0.x vs 10.4.0.x)
```

**Blocker für:** Alle anderen Infrastruktur-Tasks

---

### 2. Website Legal Compliance (DSGVO)
**Status:** 🔴 KRITISCH - Rechtliches Risiko
**Odoo Task IDs:** 135, 136
**Dauer:** ~2h

**Warum kritisch:**
- www.frawo-tech.de ist LIVE ohne Impressum/Datenschutz
- DSGVO-Verstoß: Bis zu €20M Strafe möglich
- Abmahnrisiko sehr hoch

**Action:**
```bash
cd OneDrive/Dokumente/GitHub/FraWo
python scripts/generate_legal_pages.py

# Oder manuell in Odoo:
# http://10.4.0.22:8069 → Website Editor
# Impressum + Datenschutz Seiten erstellen
```

**Abhängigkeit:** Benötigt Odoo-Zugriff (siehe #1)

---

### 3. Git Sync & Repository bereinigen
**Status:** ⚠️ DIVERGIERT
**Dauer:** 10 Min

**Problem:**
- Branch divergiert: 2 local vs 1 remote commit
- 1 untracked file: `scripts/fix_html_attributes_again.py`

**Action:**
```bash
cd OneDrive/Dokumente/GitHub/FraWo
git status
git log --oneline -5
git pull --rebase  # oder git merge
git add scripts/fix_html_attributes_again.py
git commit -m "Add HTML attribute fix script"
git push
```

---

## 🔥 WICHTIG - Diese Woche

### 4. Stockenweiler Memory Crisis
**Status:** ⏸️ PAUSIERT (Server offline)
**Problem:** Swap 99% (7.9Gi/8.0Gi) - laut letztem Report

**Betroffene Services:**
- PBS (109) - Backup Server
- n8n (110) - Workflow Automation
- Vaultwarden (108)
- AdGuard (101)

**Action:**
```bash
# Wenn Server wieder online:
ssh root@100.91.20.116
free -h
pveperf

# Rightsizing:
pct config 109  # PBS
pct config 110  # n8n
# RAM-Limits anpassen
```

**Abhängigkeit:** Benötigt Netzwerk-Zugriff (siehe #1)

---

### 5. Website SEO Quick Wins
**Status:** 📝 BEREIT
**Odoo Task IDs:** 132, 133, 134
**Dauer:** ~1h

**Tasks:**
- Meta Tags hinzufügen
- Open Graph Tags
- H2 Struktur verbessern
- Sitemap generieren

**Action:**
```bash
cd OneDrive/Dokumente/GitHub/FraWo
python scripts/website_seo_boost.py
```

**Abhängigkeit:** Benötigt Odoo-Zugriff oder lokale Website-Dateien

---

### 6. PBS Restore-Drill wiederholen
**Status:** 📋 GEPLANT
**Dauer:** 30-60 Min
**Priorität:** Wichtig für Data Recovery Readiness

**Action:**
```bash
cd OneDrive/Dokumente/GitHub/FraWo
make pbs-restore-proof
```

**Nachweis:** Exit status OK + Snapshot sichtbar in PBS

**Abhängigkeit:** Benötigt Proxmox-Zugriff (siehe #1)

---

### 7. Security Baseline Check
**Status:** 📋 GEPLANT
**Dauer:** ~2h

**Tasks:**
- Tailnet Route-Freigabe prüfen
- Split-DNS schließen
- Firewall-Rules validieren
- NFS/RPC Exposure begrenzen

**Action:**
```bash
cd OneDrive/Dokumente/GitHub/FraWo
make security-baseline-check
```

**Abhängigkeit:** Benötigt Proxmox-Zugriff (siehe #1)

---

## 💡 NÄCHSTE SCHRITTE

### 8. Radio Player Integration
**Status:** 📦 BACKLOG
**Odoo Task ID:** 140
**Dauer:** ~3h

**Features:**
- Sticky Footer Player
- AzuraCast API Integration
- Now Playing Info
- Live-Stream Link

**Action:**
```bash
cd OneDrive/Dokumente/GitHub/FraWo/apps/radio-player-frontend
# Frontend verbessern
# In Website integrieren
```

---

### 9. Radio Migration (Lane E)
**Status:** 📦 BACKLOG
**Dauer:** ~1 Tag

**Tasks:**
- AzuraCast Stockenweiler → Anker migrieren
- Media-Library Sync via Tailscale
- Icecast Relay Setup
- Odoo CRM Integration

---

### 10. Website Performance Optimierung
**Status:** 📦 BACKLOG
**Odoo Task IDs:** 137, 138, 139

**Tasks:**
- JSON-LD Structured Data
- Gzip/Brotli Compression
- Bilder-Optimierung (WebP)
- CDN Setup

---

## 🔮 SPÄTER / MAI 2026

### 11. Vaultwarden Recovery (Physischer Zugang nötig)
**Status:** ⏰ GEPLANT MAI 2026
**Frühestes Datum:** 2026-05-01

**Action:**
- 2× physische Offline-Kopien erstellen
- Option A: Papierausdruck + USB-Stick
- Option B: 2× USB-Stick an getrennten Orten
- Sichtprüfung: Beide Kopien lesbar
- `scripts/release_mvp_gate.py` ausführen

**Blocker:** Benötigt physischen Zugang (Drucker/USB)

---

### 12. Bidirektionaler Odoo Sync
**Status:** 📦 BACKLOG

**Ziel:** Änderungen in Odoo zurück ins Git schreiben

**Action:**
```python
# .ai-tools-shared/odoo_ai_sync.py erweitern
# Bidirektionale Synchronisation implementieren
```

---

### 13. Device Rollout verifizieren
**Status:** ⏸️ BLOCKIERT bis Mai 2026?

**Geräte:**
- Franz Surface
- Franz iPhone

**Action:**
```powershell
# Wenn Geräte verfügbar:
scripts/prove_device_rollout.ps1
```

---

## 📊 STATISTIK

**Gesamt:** 13 Tasks
- 🚨 **KRITISCH:** 3 (davon 1 blockiert alles)
- 🔥 **WICHTIG:** 4 (diese Woche)
- 💡 **NORMAL:** 3 (backlog)
- 🔮 **SPÄTER:** 3 (Mai 2026)

**Blockiert durch Netzwerk-Ausfall:** 9 Tasks
**Sofort machbar (offline):** 1 Task (Git Sync)
**Benötigt physischen Zugang:** 1 Task (Vaultwarden)

---

## 🎯 EMPFOHLENE REIHENFOLGE

### Jetzt (ohne Netzwerk):
1. ✅ Git Sync & Repository bereinigen (#3)

### Sobald Netzwerk wieder da:
2. 🚨 Website Legal Compliance (#2) - DSGVO!
3. 🔥 Stockenweiler Memory Crisis (#4)
4. 💡 Website SEO Quick Wins (#5)
5. 🔒 PBS Restore-Drill (#6)
6. 🔒 Security Baseline Check (#7)

### Diese Woche (wenn Zeit):
7. 🎵 Radio Player Integration (#8)

### Mai 2026:
8. 🔐 Vaultwarden Recovery (#11)

---

## 📝 NOTIZEN

**Netzwerk-Problem diagnostizieren:**
- Warum sind Proxmox-Server offline?
- Tailscale-Problem oder physische Verbindung?
- Router/Firewall-Issue?

**Prioritäten-Shift:**
- Ohne Netzwerk: Fokus auf lokale Tasks (Git, Dokumentation)
- Mit Netzwerk: Sofort DSGVO-Compliance sicherstellen!

---

## 🔄 OBSOLETE TASKS (Erledigt/Nicht mehr relevant)

- ✅ Multi-AI Setup → LIVE
- ✅ Odoo SSOT Workflow → Implementiert
- ✅ Task Scheduler → Läuft
- ❌ "9 Commits hinter origin" → Jetzt nur 1 commit difference
- ❌ Codex Session Parser → Nicht priorisiert

---

**Letzte Aktualisierung:** 2026-05-13
**Nächste Review:** Nach Netzwerk-Wiederherstellung
