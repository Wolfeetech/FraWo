# Radio Network Status Report

**Datum:** 2026-04-30
**Status:** CONSOLIDATION IN PROGRESS

---

## Executive Summary

✅ **Radio Player V2 ERSTELLT** - Minimalistisch, touch-optimiert, multi-station
🔴 **Stocki Storage KRITISCH** - NFS 100% voll (1.9T/1.9T)
🟡 **Deployment BLOCKIERT** - Stream-URLs müssen verifiziert werden
🟡 **Credentials UNGEKLÄRT** - Einheitlicher Admin-Zugang fehlt

---

## Network Topology

```
┌─────────────────────────────────────────────────────┐
│                  RADIO NETWORK                       │
│                                                      │
│  ┌──────────────┐              ┌──────────────┐    │
│  │ Anker Node   │              │ Stocki Node  │    │
│  │ (Production) │              │  (Legacy)    │    │
│  └──────────────┘              └──────────────┘    │
│                                                      │
│  Raspberry Pi 4                 VM 210              │
│  10.3.0.9                       192.168.178.210     │
│  VLAN 103                       Tailscale           │
│                                                      │
│  Station:                       Station:             │
│  frawo-funk                     radio.yourparty      │
│                                                      │
│  Music:                         Music:               │
│  USB 76E8-CACF                  NFS 192.168.178.25  │
│  2.120 Dateien                  283 GB, 23.461 Tracks│
│  ✅ OK                          🔴 100% VOLL        │
│                                                      │
│  Status:                        Status:              │
│  ✅ LIVE                        ⚠️ LIVE (degraded)  │
└─────────────────────────────────────────────────────┘

             ↓ Stream ↓

┌─────────────────────────────────────────────────────┐
│            RADIO PLAYER V2                          │
│          (Surface Go Frontend)                       │
│                                                      │
│  Location: 192.168.2.154                            │
│  Target: Firefox Kiosk Mode                         │
│  Port: 17828 (Python HTTP Server)                   │
│                                                      │
│  Features:                                          │
│  ✅ Minimalistisches Design                         │
│  ✅ 2-Station Support                               │
│  ✅ Touch-optimiert                                 │
│  ✅ Live Now-Playing                                │
│  ✅ Selbst editierbar (HTML/CSS/JS)                 │
│                                                      │
│  Status: 🔴 NOT DEPLOYED YET                        │
└─────────────────────────────────────────────────────┘
```

---

## CRITICAL ISSUES

### 1. Stocki NFS Storage 100% voll 🔴

**Problem:**
- NFS Server `192.168.178.25:/mnt/music_hdd` ist **1.9T/1.9T (100%)**
- VM 210 Root Disk OK (42G/61G = 69%)
- Music Library `yourparty_Libary`: **283 GB, 23.461 Tracks**

**Impact:**
- Keine neuen Uploads möglich
- AzuraCast kann keine Media-Changes schreiben
- Playlists können nicht aktualisiert werden

**Lösungsoptionen:**

**A) Migration zu Storage Node (EMPFOHLEN)**
```bash
# 1. Copy music library
rsync -avz --progress \
  192.168.178.25:/mnt/music_hdd/yourparty_Libary \
  //10.1.0.30/Media/yourparty_Libary

# 2. Update VM 210 fstab
# Ersetze NFS mit SMB mount wie Anker Node
# //10.1.0.30/Media/yourparty_Libary /var/azuracast/music_storage cifs ...

# 3. Deduplizierung mit Anker USB-Library
# Anker: 2.120 Dateien
# Stocki: 23.461 Dateien
# Overlap analysieren und konsolidieren
```

**B) NFS Disk Erweitern**
```bash
# Option nur wenn NFS auf dedizierter Disk liegt
# Disk +500GB hinzufügen
```

**C) Stocki Dekommissionieren**
```bash
# Library nach Anker migrieren
# VM 210 herunterfahren
# Nur Anker produktiv
```

---

### 2. Einheitliche Login-Credentials fehlen 🟡

**Status:** Nicht verifiziert

**Anker Node:**
- URL: `http://radio.hs27.internal/login`
- Admin-User: TBD
- Password: TBD (Vaultwarden?)

**Stocki Node:**
- URL: `https://radio.yourparty.tech/login` (oder IP)
- Admin-User: TBD
- Password: TBD

**Aktion:**
```bash
# Anker
ssh wolf@10.3.0.9
docker exec azuracast bash -c 'azuracast account:list'

# Stocki
ssh stock-pve "qm guest exec 210 -- docker exec azuracast bash -c 'azuracast account:list'"
```

---

### 3. Stream-URLs nicht verifiziert 🟡

**Anker (frawo-funk):**
- API Endpoint: `http://radio.hs27.internal/api/nowplaying/frawo-funk`
- Stream URL: TBD (vermutlich `/listen/frawo-funk/radio.mp3`)

**Stocki (radio.yourparty):**
- API Endpoint: TBD
- Stream URL: TBD

**Test Required:**
```bash
# Via Toolbox oder Anker Node selbst
curl http://radio.hs27.internal/api/station/frawo-funk | jq '.listen_url'
```

---

## COMPLETED WORK ✅

### Radio Player V2 Design
- **File:** `apps/radio-player-frontend/site/index_v2.html`
- **Features:**
  - Minimalistisches Design (Gradients, Emojis)
  - 2-Station Grid (Anker + Stocki)
  - Touch-optimierte Buttons (80px+)
  - Live Now-Playing mit Auto-Refresh
  - Status-Badges (Live/Offline)
  - HTML5 Audio Player
  - Keine Frameworks, pure HTML/CSS/JS

### Storage Audit
- VM 210 Root Disk: ✅ OK (69%)
- NFS Music Storage: 🔴 100% VOLL
- Library Size: 283 GB, 23.461 Tracks
- NFS Server: 192.168.178.25 (identifiziert, erreichbar)

### Network Inventory
- Anker Node: ✅ Production, Stabil
- Stocki Node: ⚠️ Live aber degraded
- Legacy CTs (207/208/211): Nicht gefunden (bereits dekommissioniert)

---

## NEXT ACTIONS (Priorisiert)

### 1. KRITISCH: Stocki Storage Fix
- [ ] Entscheidung: Migration vs. Disk-Erweiterung vs. Dekommission
- [ ] Wenn Migration: rsync zu Storage Node
- [ ] Wenn Erweiterung: PVE Disk +500GB
- [ ] VM 210 fstab aktualisieren
- [ ] AzuraCast Container neu starten
- [ ] Verify: df -h zeigt < 80%

### 2. Stream-URLs Discovery
- [ ] SSH zu Anker Node
- [ ] `curl http://localhost/api/station/frawo-funk`
- [ ] Extrahiere `listen_url`
- [ ] Test-Stream im Browser
- [ ] Update `index_v2.html` mit korrekter URL

### 3. Credentials Audit
- [ ] Anker: Account-List
- [ ] Stocki: Account-List
- [ ] Passwort-Standard festlegen
- [ ] Vaultwarden-Eintrag erstellen
- [ ] Credentials über Nodes synchronisieren

### 4. Radio Player V2 Deployment
- [ ] `index_v2.html` → Surface Go kopieren
- [ ] Python HTTP Server starten (Port 17828)
- [ ] Firefox Kiosk auf `http://localhost:17828` umstellen
- [ ] Network-Test: Surface Go → Anker Radio
- [ ] Touch-Interaktion testen
- [ ] Fullscreen-Mode verifizieren

### 5. Domain-Migration Planung
- [ ] `funk.frawo-tech.de` DNS-Setup
- [ ] Cloudflare Tunnel oder NPM Reverse Proxy
- [ ] TLS-Zertifikat
- [ ] Redirect `radio.yourparty.tech` → `funk.frawo-tech.de`

---

## PRODUCTION-READY DEFINITION

**Anker Node (frawo-funk):**
- ✅ AzuraCast läuft stabil
- 🔴 Einheitlicher Admin-Zugang
- ✅ SMB-Mount vorbereitet
- ✅ Internal DNS erreichbar
- 🔴 Stream-URL verifiziert

**Stocki Node (radio.yourparty):**
- ✅ Live-Streaming funktioniert
- 🔴 Storage < 80%
- 🔴 Einheitlicher Admin-Zugang
- 🔴 Domain-Migration
- ⚠️ Memory-Druck reduziert

**Radio Player V2:**
- ✅ Design fertig
- 🔴 Deployed auf Surface Go
- 🔴 Multi-Station funktioniert
- 🔴 Touch-optimiert getestet
- 🔴 Auto-refresh verifiziert

---

## FILES CREATED

- `OPERATIONS/RADIO_NETWORK_CONSOLIDATION.md` - Hauptplan
- `OPERATIONS/RADIO_PLAYER_V2_DEPLOYMENT.md` - Deployment-Guide
- `apps/radio-player-frontend/site/index_v2.html` - Neues Frontend

---

## CONTACT

**Wolf Admin:**
- Anker SSH: `ssh wolf@10.3.0.9`
- Stocki SSH: `ssh -J stock-pve 192.168.178.210`
- Surface Go: `ssh frawo@192.168.2.154`
