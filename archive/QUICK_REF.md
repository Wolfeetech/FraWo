# FraWo - Quick Reference

**Datum:** 2026-05-13

---

## ⚡ SOFORT-AKTIONEN

### 1. Git Sync (JETZT machbar)
```bash
cd OneDrive/Dokumente/GitHub/FraWo
git pull --rebase && git push
```

### 2. Website DSGVO (wenn Odoo online)
```bash
python scripts/generate_legal_pages.py
```

### 3. Memory Fix (wenn Server online)
```bash
ssh root@100.91.20.116
free -h
```

---

## 🌐 NETZWERK-STATUS

| Server | IP | Tailscale | Status |
|--------|-------|-----------|--------|
| Odoo | 10.4.0.22 | - | ❌ offline |
| Anker | - | 100.69.179.87 | ❌ 10h ago |
| Stockenweiler | - | 100.91.20.116 | ❌ 3d ago |

---

## 📋 TOP 5 TASKS

1. 🚨 Netzwerk wiederherstellen
2. 🔴 DSGVO-Compliance (Impressum/Datenschutz)
3. ⚠️ Git Sync (divergiert)
4. 🔥 Stockenweiler Memory (Swap 99%)
5. 💡 Website SEO

---

## 📁 WICHTIGE DATEIEN

- [TODO_MASTER.md](TODO_MASTER.md) - Alle Tasks
- [START_HERE.md](START_HERE.md) - Vollständige Übersicht
- [MASTERPLAN.md](MASTERPLAN.md) - Projekt-Strategie

---

## 🔧 NÜTZLICHE BEFEHLE

```bash
# Status prüfen
git status
tailscale status
ping 10.4.0.22

# Server verbinden
ssh root@100.69.179.87     # Anker
ssh root@100.91.20.116     # Stockenweiler

# Memory prüfen
free -h
pct list

# Website deployen
cd scripts
python generate_legal_pages.py
python website_seo_boost.py
```

---

## 📊 ZAHLEN

- **13 Tasks** gesamt
- **3 kritisch** (sofort)
- **9 blockiert** (Netzwerk offline)
- **1 machbar** jetzt (Git Sync)

---

## ✅ EMPFEHLUNG

**JETZT:** Git Sync durchführen
**DANN:** Netzwerk diagnostizieren
**DANACH:** DSGVO-Compliance sicherstellen
