# 🚀 FraWo - START HERE

**Letzte Aktualisierung:** 2026-05-13
**Status:** Alle TODOs konsolidiert ✅

---

## 📍 AKTUELLE SITUATION

### Netzwerk-Status
- ❌ **Proxmox Anker:** offline (10h)
- ❌ **Stockenweiler:** offline (3d)
- ❌ **Odoo Server:** nicht erreichbar
- ✅ **Lokale Umgebung:** funktioniert

### Repository-Status
- ✅ **Git:** Synchronisiert mit `origin/main` (und 4 Commits voraus, bereit zum Pushen)
- 📄 **Untracked:** Keine


---

## 🎯 MASTER TODO LISTE

**Vollständige Liste:** [TODO_MASTER.md](TODO_MASTER.md)

### 🚨 KRITISCH (Sofort)

**#1 - Netzwerk wiederherstellen**
```bash
# Proxmox/Stockenweiler physisch prüfen
# Tailscale auf Servern neustarten
```
→ Blockiert 9 weitere Tasks

**#2 - Website DSGVO-Compliance** 🔴 RECHTLICH KRITISCH
```bash
cd OneDrive/Dokumente/GitHub/FraWo
python scripts/generate_legal_pages.py
```
→ Impressum + Datenschutz fehlen auf www.frawo-tech.de

**#3 - Git Sync** (OHNE Netzwerk machbar) - ✅ ERLEDIGT
```bash
# Git Pull & Rebase durchgeführt, lokale Änderungen committed.
# Bereit für git push!
```

---

### 🔥 WICHTIG (Diese Woche)

**#4 - Stockenweiler Memory** (Swap 99%)
**#5 - Website SEO** (Quick Wins)
**#6 - PBS Restore-Drill**
**#7 - Security Baseline Check**

---

### 💡 BACKLOG

**#8 - Radio Player Integration**
**#9 - Radio Migration (Lane E)**
**#10 - Website Performance**

---

### 🔮 MAI 2026

**#11 - Vaultwarden Recovery** (physischer Zugang nötig)
**#12 - Bidirektionaler Odoo Sync**
**#13 - Device Rollout**

---

## 📊 STATISTIK

- **Gesamt:** 13 Tasks
- **Kritisch:** 3
- **Diese Woche:** 4
- **Backlog:** 3
- **Mai 2026:** 3

**Blockiert durch Netzwerk:** 9 Tasks
**Sofort machbar:** 1 Task (Git)

---

## 🎬 NÄCHSTE AKTIONEN

### Option A: Mit Netzwerk-Zugriff
```
1. Server neustarten/prüfen
2. Website DSGVO-Compliance (2h)
3. Stockenweiler Memory Fix (30min)
4. SEO Quick Wins (1h)
```

### Option B: Ohne Netzwerk (JETZT)
```
1. Git Sync durchführen (10min) ✅ EMPFOHLEN
2. Lokale Scripts vorbereiten
3. Dokumentation verbessern
```

---

## 📁 PROJEKT-STRUKTUR

```
FraWo/
├── TODO_MASTER.md          ← Vollständige Task-Liste
├── START_HERE.md           ← Diese Datei
├── MASTERPLAN.md           ← Projekt-Strategie
├── DOCS/
│   ├── archive/
│   │   └── todos_2026-05-13/  ← Alte TODOs archiviert
│   └── plans/
├── scripts/
│   ├── generate_legal_pages.py
│   ├── website_seo_boost.py
│   └── fix_html_attributes_again.py  (untracked)
└── apps/
    ├── fayanet/
    ├── radio-player-frontend/
    └── yourparty/
```

---

## ✅ WAS WURDE ERLEDIGT

- ✅ Alle TODO-Dokumente konsolidiert
- ✅ 3 alte TODO-Dateien archiviert nach `DOCS/archive/todos_2026-05-13/`
- ✅ Status-Check durchgeführt (Netzwerk, Git, Infrastruktur)
- ✅ Master-TODO-Liste erstellt mit Prioritäten
- ✅ Obsolete Tasks identifiziert und dokumentiert

---

## 🔗 WICHTIGE LINKS

- **Website:** https://www.frawo-tech.de
- **Odoo:** http://10.4.0.22:8069 (aktuell offline)
- **Tailscale Admin:** https://login.tailscale.com
- **GitHub Repo:** https://github.com/[your-repo]/FraWo

---

## 💡 EMPFEHLUNG

**JETZT machen (ohne Netzwerk):**
```bash
cd OneDrive/Dokumente/GitHub/FraWo
git status
git log --oneline -5
git pull --rebase
```

**DANACH (wenn Netzwerk da):**
1. 🚨 Website Legal Compliance (DSGVO!) - HÖCHSTE PRIORITÄT
2. 🔥 Stockenweiler Memory Crisis
3. 💡 SEO Quick Wins

---

**Los geht's! 🚀**
