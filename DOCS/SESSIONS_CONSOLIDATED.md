# FraWo - Konsolidierte Session-Informationen

**Erstellt:** 2026-05-13
**Quelle:** Analyse aller 449 Claude-Sessions (30 MB)
**Status:** Extrahiert aus den 8 wichtigsten Sessions

---

## 🌐 NETZWERK-INFRASTRUKTUR

### Tailscale IPs (Alle Geräte)

| Gerät | Tailscale IP | Status (letzter Check) |
|-------|--------------|------------------------|
| **wolfstudiopc** | 100.98.31.60 | ✅ ONLINE |
| **proxmox-anker** | 100.69.179.87 | ❌ offline (11h ago) |
| **stockenweiler-pve** | 100.91.20.116 | ❌ offline (3d ago) |
| franz-iphone15 | 100.106.111.38 | offline (35d ago) |
| pixel-9-pro | 100.83.213.17 | offline (8d ago) |
| surface-go-frontend | 100.106.67.127 | offline (7d ago) |
| toolbox | 100.82.26.53 | offline (10h ago) |
| villarechner420 | 100.85.153.121 | offline (2d ago) |
| wohnzimmertv | 100.84.241.124 | offline (43d ago) |
| wolf-surface | 100.79.103.59 | offline (4d ago) |
| wolf-zenbook | 100.76.249.126 | offline (50d ago) |

### Lokale Netzwerk-Segmente

| Subnet | Zweck | Router |
|--------|-------|--------|
| **10.1.0.0/24** | Proxmox Anker - Production Services | 10.1.0.1 |
| **10.2.0.0/24** | Stockenweiler Segment 1 | 10.2.0.1 |
| **10.3.0.0/24** | Stockenweiler Segment 2 | 10.3.0.1 |
| **10.4.0.0/24** | Proxmox Anker - Extended Services | 10.4.0.1 |
| **10.5.0.0/24** | Reserved/Future | 10.5.0.1 |
| **10.10.0.0/24** | Management Network | 10.10.0.1 |
| **10.11.0.0/24** | Development Network | 10.11.0.1 |

---

## 🖥️ PROXMOX ANKER (100.69.179.87)

**Status:** ❌ OFFLINE seit 11h
**Subnet:** 10.1.0.x, 10.4.0.x

### Container/Services auf Anker

| CT ID | Service | IP | Port | Status |
|-------|---------|----|----|--------|
| 100 | - | 10.4.0.100 | - | ❓ |
| 101 | AdGuard Home | 10.1.0.101 | 80/443 | ❌ offline |
| 103 | - | - | - | ❓ |
| 120 | - | - | - | ❓ |
| 200-208 | Various Services | 10.4.0.20x | - | ❌ offline |
| 210 | - | - | - | ❓ |
| 211 | - | - | - | ❓ |
| 220 | - | - | - | ❓ |

### Kritische Services auf Anker

| Service | IP | URL | Zweck |
|---------|----|----|-------|
| **Odoo** | 10.1.0.112 | http://10.1.0.112:8069 | CRM/Website-Backend |
| **Home Assistant** | 10.1.0.24 | http://10.1.0.24:8123 | Smart Home |
| **Nextcloud** | 10.1.0.21 | http://10.1.0.21 | Cloud Storage |
| **Vaultwarden** | 10.1.0.26 | http://10.1.0.26 | Password Manager |
| **AdGuard** | 10.1.0.101 | http://10.1.0.101 | DNS/Ad-Blocking |

---

## 🏠 STOCKENWEILER PVE (100.91.20.116)

**Status:** ❌ OFFLINE seit 3 Tagen
**Subnet:** 10.2.0.x, 10.3.0.x

### Container auf Stockenweiler

| CT ID | Service | IP | Zweck | Memory Issue |
|-------|---------|----|----|--------------|
| **108** | Vaultwarden | - | Password Manager Backup | ⚠️ |
| **109** | PBS (Proxmox Backup Server) | - | Backup Server | 🚨 SWAP 99% |
| **110** | n8n | - | Workflow Automation | 🚨 SWAP 99% |
| 101 | AdGuard | - | DNS (Backup?) | ⚠️ |
| 100-130 | Various | - | Multiple Services | ⚠️ |

### 🚨 KRITISCHES PROBLEM: Memory Crisis

**Letzte Diagnose:**
- Swap: 7.9Gi / 8.0Gi (99% voll!)
- Betroffene Services: PBS (109), n8n (110), Vaultwarden (108), AdGuard (101)
- Action needed: RAM-Limits anpassen (rightsizing)

**Geplante Lösung:**
```bash
# Wenn Server wieder online:
ssh root@100.91.20.116
free -h
pveperf
pct config 109  # PBS RAM-Limits prüfen
pct config 110  # n8n RAM-Limits prüfen
```

---

## 🌐 FRAWO WEBSITE & ODOO

### Website
- **Live URL:** https://www.frawo-tech.de
- **Status:** 🔴 LIVE OHNE DSGVO-Compliance!
- **Backend:** Odoo Website Builder (10.1.0.112:8069)

### 🚨 KRITISCHE PROBLEME

1. **DSGVO-Compliance fehlt**
   - ❌ Kein Impressum
   - ❌ Keine Datenschutzerklärung
   - 🚨 Rechtliches Risiko: Bis zu €20M Strafe
   - Action: `python scripts/generate_legal_pages.py`

2. **Odoo nicht erreichbar**
   - IP: 10.1.0.112
   - Port: 8069
   - Grund: Proxmox Anker offline

### Odoo Tasks (aus Sessions)

| Task ID | Beschreibung | Status |
|---------|--------------|--------|
| 132 | Meta Tags hinzufügen | 📝 Bereit |
| 133 | Open Graph Tags | 📝 Bereit |
| 134 | H2 Struktur verbessern | 📝 Bereit |
| 135 | Impressum erstellen | 🔴 KRITISCH |
| 136 | Datenschutz erstellen | 🔴 KRITISCH |
| 137 | JSON-LD Structured Data | 📦 Backlog |
| 138 | Gzip/Brotli Compression | 📦 Backlog |
| 139 | Bilder-Optimierung (WebP) | 📦 Backlog |
| 140 | Radio Player Integration | 📦 Backlog |

---

## 📁 GIT REPOSITORY

**Repo:** OneDrive/Dokumente/GitHub/FraWo
**Branch:** main
**Remote:** origin/main

### Aktueller Status (2026-05-13)
```
Branch: main
Ahead of origin: 1 commit
Working tree: clean
Untracked: (keine)

Letzte Commits:
- 7c369d1 - Konsolidiere alle TODOs
- ca3e199 - Update START_HERE.md
- 456fe71 - Archive old TODOs
- 21622d4 - HTML tags self-closing fix
- 2816c0c - Prepare v4 Website Launch
```

### Scripts im Repository

| Script | Zweck | Status |
|--------|-------|--------|
| `generate_legal_pages.py` | Impressum/Datenschutz | 🔴 Benötigt |
| `website_seo_boost.py` | SEO-Optimierung | 📝 Bereit |
| `fix_html_attributes_again.py` | HTML-Cleanup | ✅ Erstellt |
| `odoo_ai_sync.py` | Bidirektionaler Sync | 📦 Geplant |
| `prove_device_rollout.ps1` | Device-Verification | 📦 Geplant |
| `release_mvp_gate.py` | Release-Gate | 📦 Mai 2026 |

---

## 🎯 ALLE CONTAINER-IDS (Aus Sessions extrahiert)

### Proxmox Anker
- CT: 100, 101, 102, 103, 104, 105, 106, 120, 121, 200, 201, 202, 203, 204, 205, 206, 207, 208, 210, 211, 212, 220

### Stockenweiler
- CT: 100, 101, 108, 109, 110, 130, 150

---

## 📊 PROJEKT-APPS

| App | Pfad | Beschreibung | Status |
|-----|------|--------------|--------|
| **fayanet** | apps/fayanet/ | Haupt-Website (FraWo-Tech) | ✅ Live |
| **radio-player-frontend** | apps/radio-player-frontend/ | Radio Player UI | 📦 Entwicklung |
| **yourparty** | apps/yourparty/ | Party-App? | ❓ |

---

## 🔐 WICHTIGE CREDENTIALS/LOCATIONS

| Service | Location | Backup |
|---------|----------|--------|
| Vaultwarden (Primary) | Proxmox Anker (10.1.0.26) | ❌ offline |
| Vaultwarden (Backup) | Stockenweiler CT 108 | ❌ offline |
| PBS Backups | Stockenweiler CT 109 | ❌ offline |
| Git Credentials | ~/.git-credentials | ✅ lokal |

**🚨 KRITISCH:** Beide Vaultwarden-Instanzen offline = Kein Passwort-Zugriff!

---

## 🎵 RADIO/AZURACAST

**Geplante Migration:** Stockenweiler → Anker (Lane E)

Tasks:
- AzuraCast migrieren
- Media-Library Sync via Tailscale
- Icecast Relay Setup
- Odoo CRM Integration
- Radio Player Frontend in Website integrieren

---

## 📋 MASTER TODO-LISTE (Konsolidiert)

### 🚨 KRITISCH (Sofort)
1. **Netzwerk wiederherstellen** - Proxmox Anker + Stockenweiler
2. **Website DSGVO** - Impressum + Datenschutz (RECHTLICH!)
3. **Git Push** - 1 Commit voraus

### 🔥 WICHTIG (Diese Woche)
4. **Stockenweiler Memory Crisis** - Swap 99%
5. **Website SEO Quick Wins** - Meta/OG Tags
6. **PBS Restore-Drill** - Backup-Test
7. **Security Baseline Check** - Firewall/DNS

### 💡 BACKLOG
8. **Radio Player Integration**
9. **Radio Migration (Lane E)**
10. **Website Performance Optimierung**

### 🔮 MAI 2026
11. **Vaultwarden Recovery** (physischer Zugang)
12. **Bidirektionaler Odoo Sync**
13. **Device Rollout Verification**

---

## 🔍 WAS WURDE AUS DEN SESSIONS GELERNT

### Wiederkehrende Probleme (aus 449 Sessions):
1. **Netzwerk-Instabilität** - Proxmox-Server häufig offline
2. **Memory-Probleme** - Stockenweiler Swap immer kritisch
3. **DSGVO-Compliance** - Seit Wochen nicht erledigt
4. **Git-Sync-Issues** - Branch divergiert regelmäßig
5. **Vaultwarden-Abhängigkeit** - Single Point of Failure

### Häufigste Themen (Erwähnungen in Sessions):
- **Git:** 941× (Repository-Management)
- **Odoo:** 292× (Website/CRM-Backend)
- **FraWo:** 316× (Projekt-Kontext)
- **Stockenweiler:** 149× (Server-Probleme)
- **Proxmox:** 93× (Infrastruktur)
- **TODO:** 69× (Task-Management)

---

## 💾 SESSION-ARCHIVIERUNG

**Wichtigste Sessions (BEHALTEN):**
- 0f2a0b35-c417-4a0f-82b3-9e9552bef2b1.jsonl (2.6 MB) - FraWo-Doku
- b28c64e3-4f98-4e60-b6fa-a865d81c0c53.jsonl (1.9 MB) - Odoo/Git
- 6e7d572a-7dba-4f76-98f8-537a8378108a.jsonl (2.0 MB) - Stockenweiler
- 94ded831-512e-4d85-861d-52ee7e8985ef.jsonl (1.7 MB) - Multi-Thema
- 5154183b-aa0d-4741-a362-2e10eeab36ac.jsonl (1.3 MB) - FraWo/Git
- 86662fd3-a49f-4a6c-b113-4cf1a5533cd4.jsonl (500 KB) - TODOs
- 023717eb-f300-4d76-ab1b-b40f1f5952f8.jsonl (1.2 MB) - Stockenweiler
- e0d4bdfd-aeac-4b7e-b3eb-8215634bbb6f.jsonl (1.3 MB) - Mix

**Löschbar:**
- 81 leere Sessions (0 Bytes)
- ~150 Mini-Sessions (<2 KB)
- ~200 redundante Sessions

---

**Letzte Aktualisierung:** 2026-05-13
**Nächste Schritte:** Siehe [TODO_MASTER.md](../TODO_MASTER.md)
