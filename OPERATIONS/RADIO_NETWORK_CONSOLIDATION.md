# Radio Network Consolidation Plan

## Status: IN PROGRESS
**Erstellt:** 2026-04-30
**Ziel:** Production-Ready Radio Network mit einheitlicher Kontrolle

---

## Aktuelles Radio-Netzwerk

### 1. Raspberry Pi Radio Node (Anker - Production)
- **Host:** `raspberry_pi_radio` (10.3.0.9, VLAN 103)
- **Station:** `frawo-funk`
- **Status:** ✅ Internal Live with USB Music
- **AzuraCast:** Deployed, läuft stabil
- **Zugriff:** `http://radio.hs27.internal/login`
- **Musikquelle:** USB `76E8-CACF` + optional SMB `//10.1.0.30/Media`
- **Site:** Anker (Hauptstandort Rothkreuz)

### 2. AzuraCast VM Stockenweiler (Remote - Legacy)
- **Host:** `azuracast_vm_stock` (VM 210 @ stock-pve)
- **IP Lokal:** `192.168.178.210`
- **IP Ziel:** `10.11.0.10` (VLAN 111)
- **Station:** `Radio4yourparty`
- **Status:** ⚠️ Live-Streaming-Verified BUT Critical Issues
- **Domain Legacy:** `radio.yourparty.tech`
- **Site:** Stockenweiler (Remote über Tailscale)
- **Backend:** Liquidsoap + Icecast
- **Playlists:** Wolfarites, Wolf Lounge
- **KRITISCH:**
  - Storage: 100% voll
  - Memory: 70% Swap-Nutzung
  - Music Library: 283 GB

### 3. Mobile Node
- **Status:** Noch nicht deployed
- **Geplant:** Mobile Streaming-Lösung

---

## Legacy Payload Stockenweiler (vor Abbau zu sichern)

**VM 210:** `azuracast-vm` (Running, 4 GB RAM, 64 GB Disk)
**Status:** Aktuell live, aber unter Ressourcendruck

**Weitere potenzielle Legacy-Komponenten:**
- CT 207: `radio-wordpress-prod` (nicht gefunden)
- CT 208: `mariadb-server` (nicht gefunden)
- CT 211: `radio-api` (nicht gefunden)

**Aktion erforderlich:** Vollständiges Inventar aller radio-bezogenen VMs/CTs in Stocki vor Abbau

---

## Konsolidierungs-Anforderungen

### A. Einheitliche Login-Credentials
**Problem:** Verschiedene AzuraCast-Instanzen haben unterschiedliche Logins
**Ziel:** Einheitlicher Admin-Zugang für Wolf über alle Nodes
**Status:** 🔴 TODO

**Schritte:**
1. Aktuellen Admin-User in `raspberry_pi_radio` erfassen
2. Admin-User in `azuracast_vm_stock` (VM 210) prüfen
3. Passwort-Standard festlegen (Vaultwarden-Integration)
4. Credentials über alle Nodes synchronisieren

### B. Storage-Druck Stocki beheben ✅ ANALYSIERT

**Problem:** NFS Music Storage 192.168.178.25 ist 100% voll (1.9T/1.9T)
**VM 210 Root Disk:** 61G total, 42G used (69%) ✅ OK
**Status:** 🔴 CRITICAL - NFS Server blockiert

**Audit-Ergebnis:**

- **NFS Mount:** `192.168.178.25:/mnt/music_hdd` → `/var/azuracast/music_storage`
- **Music Library:** `yourparty_Libary` = **283 GB, 23.461 Tracks**
- **Docker Mounts:** Station Data in Volume, Music via NFS
- **NFS Server:** 192.168.178.25 (erreichbar, TTL=64)

**Optionen:**

1. **Music Library → Storage Node migrieren** (283 GB → `//10.1.0.30/Media/yourparty_Libary`)
2. **NFS Server Disk erweitern** (aktuell 1.9T @ 100%)
3. **Deduplizierung mit Anker-USB-Library** (2.120 vs 23.461 Files)
4. **Stocki Node dekommissionieren** (nur Anker produktiv)

### C. Domain-Migration
**Von:** `radio.yourparty.tech`
**Nach:** `funk.frawo-tech.de`
**Status:** 🟡 PLANNED

**Schritte:**
1. `funk.frawo-tech.de` DNS-Setup vorbereiten
2. Cloudflare Tunnel oder Public Edge Proxy
3. TLS-Zertifikat
4. Graceful Cutover mit Redirect

### D. Zentrale Netzwerk-Kontrolle
**Ziel:** Wolf hat Full Control über alle Radio-Nodes
**Status:** 🟡 PARTIAL

**Nodes:**
- ✅ Anker (radio-node): SSH + Tailscale + AzuraCast Admin
- ⚠️ Stocki (VM 210): Tailscale SSH routing, AzuraCast Admin prüfen
- 🔴 Mobile: Noch nicht deployed

---

## Nächste Schritte (Priorisiert)

### 1. KRITISCH: Stocki Storage-Audit
```bash
ssh stock-pve "qm status 210"
ssh -J stock-pve 192.168.178.210 "df -h"
ssh -J stock-pve 192.168.178.210 "du -sh /var/azuracast/stations/*"
```

### 2. Login-Credentials Audit
```bash
# Anker Node
ssh wolf@10.3.0.9 "docker exec azuracast bash -c 'azuracast account:list'"

# Stocki Node
ssh -J stock-pve 192.168.178.210 "docker exec azuracast azuracast account:list"
```

### 3. Music Library Deduplizierung
- Inventar Stocki: `/var/azuracast/stations/*/media`
- Inventar Anker: `/srv/radio-library/music-usb/yourparty.radio`
- Overlap-Analyse
- Konsolidierung zu `//10.1.0.30/Media/yourparty_Libary`

### 4. Radio Player Frontend Deployment
**Blockers:**
- Einheitliche API-Endpoints
- Einheitliche Station-Shortcodes
- Stabile `/api/nowplaying` auf allen Nodes

---

## Production-Ready Definition

✅ **Anker Node:**
- AzuraCast läuft stabil
- Einheitlicher Admin-Zugang
- SMB-Mount zu Storage Node funktioniert
- `radio.hs27.internal` intern erreichbar

🔴 **Stocki Node:**
- Storage < 80%
- Memory < 50% Swap
- Einheitlicher Admin-Zugang
- Domain-Migration abgeschlossen oder Redirect aktiv

🔴 **Mobile Node:**
- Noch nicht definiert

✅ **Radio Player Frontend:**
- Deployed auf Surface Go Frontend
- Multi-Station-Support (Anker + Stocki)
- Touch-optimiert
- Auto-refresh Nowplaying

---

## Eskalation

**Storage-Notfall Stocki:**
1. Sofortiger Stop nicht-essentieller Playlists
2. Log-Rotation prüfen
3. Temp-Files cleanup
4. Disk-Erweiterung in PVE

**Netzwerk-Ausfall:**
1. Tailscale-Status prüfen
2. Direct LAN-Access als Fallback
3. AzuraCast Container-Status

**Stream-Ausfall:**
1. Pi-Ressourcen (CPU/RAM/Storage)
2. SMB-Mount Status
3. AzuraCast Container-Logs
4. Liquidsoap Backend-Status
