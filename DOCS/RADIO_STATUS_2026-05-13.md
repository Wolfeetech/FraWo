# Radio / AzuraCast Status - 2026-05-13

> [!WARNING]
> **HISTORISCHER SNAPSHOT (nicht entscheidungsfuehrend).**
> Verbindliche Runtime-SSOT: `/home/runner/work/FraWo/FraWo/OPERATIONS/RADIO_OPERATIONS_SSOT.md`


**Update:** Nach Studio PC Cleanup & DSGVO-Compliance
**Ziel:** funk.frawo-tech.de für AzuraCast einrichten

---

## 🎯 AKTUELLER STATUS

### Infrastruktur

| Component | IP | Status | Notizen |
|-----------|----|----|---------|
| **Anker Radio Node** | 10.3.0.9 | ❌ OFFLINE | AzuraCast Primary |
| **Stocki Radio VM** | 192.168.178.210 | ❌ OFFLINE | Legacy Node (Stocki offline) |
| **Storage Node** | 10.1.0.30 | ❓ UNBEKANNT | SMB Share für Media |
| **Proxmox Anker** | 100.69.179.87 | ✅ ONLINE | Host |
| **Proxmox Stockenweiler** | 100.91.20.116 | ❌ OFFLINE | Host (3d offline) |

### Aktuelles Setup (aus AZURACAST_STATUS_2026-04-30.md)

**Letzte bekannte Konfiguration (30.04.2026):**
- **Primary:** Anker Node (10.3.0.9) mit AzuraCast Docker
- **Stream URL:** `http://radio.hs27.internal/listen/frawo-funk/radio.mp3`
- **Storage:**
  - Anker USB: `/srv/radio-library/music-usb/`
  - Network SMB: `/srv/radio-library/music-network/` → `//10.1.0.30/Media`
- **Media Dirs:**
  - `frawo_curated/` - Kuratierte Library
  - `frawo_incoming/` - Upload-Dir
  - `yourparty_Libary/` - Legacy (1.7GB, 3.631 files)

---

## 🚨 AKTUELLE PROBLEME

### 1. Radio Node offline (10.3.0.9)
**Problem:** Ping schlägt fehl, HTTP nicht erreichbar
**Ursache:** Vermutlich Container/LXC auf Proxmox Anker gestoppt
**Impact:** Kein Radio-Stream verfügbar

### 2. Stockenweiler komplett offline
**Problem:** Host seit 3 Tagen offline
**Impact:**
- VM 210 (Stocki Radio) nicht erreichbar
- 283GB Legacy-Library nicht verfügbar
- Backup/Relay ausgefallen

### 3. Storage Node Status unbekannt
**Problem:** 10.1.0.30 Erreichbarkeit nicht getestet
**Impact:** SMB Mount für Media unklar

### 4. funk.frawo-tech.de nicht konfiguriert
**Problem:** DNS existiert nicht
**Impact:** Keine öffentliche Domain für Radio

---

## 📋 AUFGABEN

### 🔥 KRITISCH (Sofort)

#### 1. Radio Node auf Proxmox Anker finden & starten
```bash
ssh root@100.69.179.87
pct list | grep -i radio  # Container-ID finden
pct status <ID>            # Status prüfen
pct start <ID>             # Container starten
pct enter <ID>             # In Container einloggen

# Wenn kein Container:
# → LXC neu erstellen oder Docker-Host finden
```

#### 2. Storage Node Status prüfen
```bash
# Von Studio PC
ping 10.1.0.30

# Von Proxmox Anker
ssh root@100.69.179.87
ping 10.1.0.30
curl -s http://10.1.0.30  # Test SMB Server
```

#### 3. AzuraCast Service Status
```bash
# Wenn Radio Node läuft:
ssh wolf@10.3.0.9
docker ps | grep azuracast
docker-compose -f /path/to/docker-compose.yml ps
curl -s http://localhost/api/station/frawo-funk
```

---

### 💡 WICHTIG (Diese Woche)

#### 4. funk.frawo-tech.de DNS Setup

**Option A: Cloudflare (Empfohlen)**
```
DNS Record erstellen:
Type: A
Name: funk
Content: <PUBLIC_IP> oder Cloudflare Tunnel
Proxy: ✅ (Orange Cloud)
TTL: Auto
```

**Option B: Nginx Proxy Manager**
```
NPM auf Proxmox Anker:
Proxy Host erstellen:
Domain: funk.frawo-tech.de
Forward to: 10.3.0.9:80
SSL: Let's Encrypt
```

#### 5. Radio Player V2 auf Website integrieren
```bash
# In Odoo Website
# Sticky Footer mit:
# - Now Playing (API: http://10.3.0.9/api/nowplaying/frawo-funk)
# - Stream URL: https://funk.frawo-tech.de/listen/frawo-funk/radio.mp3
```

#### 6. Media Library Organization
```
Struktur:
/mnt/data/media/
├── frawo_curated/
│   ├── Rock/
│   ├── Pop/
│   ├── Electronic/
│   └── ...
├── frawo_incoming/       # Uploads
└── yourparty_library/    # Legacy
```

---

### 📦 BACKLOG

#### 7. Stockenweiler Radio Migration
**Wenn Stocki wieder online:**
```bash
# 283GB Legacy Library migrieren
bash scripts/radio/migrate_stocki_to_storage_node.sh
```

#### 8. High Availability Setup
```
Primary: Anker (10.3.0.9)
Backup: Stocki VM 210 (wenn online)
Relay: Icecast auf beiden Nodes
Load Balancer: HAProxy oder NPM
```

#### 9. Radio Player Frontend Deployment
```bash
# Auf Surface Go
scp apps/radio-player-frontend/site/index_v2.html \
  frawo@192.168.2.154:~/radio-player/index.html
```

---

## 🎵 AZURACAST SETUP (Wenn Radio Node läuft)

### Erste Schritte

1. **Web-UI Zugriff:**
   ```
   URL: http://10.3.0.9
   User: wolf@frawo-tech.de (oder admin)
   Pass: <aus Vaultwarden - aber offline!>
   ```

2. **Station erstellen/prüfen:**
   - Name: FraWo Funk
   - Slug: frawo-funk
   - Frontend: Icecast
   - Bitrate: 128 kbps

3. **Media hinzufügen:**
   ```
   Web UI → Media → Upload
   Oder: SSH + SMB Mount
   ```

4. **Playlist erstellen:**
   ```
   Name: Main Rotation
   Type: Advanced
   Source: frawo_curated/
   AutoDJ: Enable
   ```

5. **Stream testen:**
   ```bash
   curl -I http://10.3.0.9/listen/frawo-funk/radio.mp3
   # Oder im Browser öffnen
   ```

---

## 🔗 DOMAIN ROUTING

### Ziel-Architektur

```
Internet (funk.frawo-tech.de)
  ↓
Cloudflare (DNS + CDN)
  ↓
Cloudflare Tunnel ODER Public IP
  ↓
Nginx Proxy Manager (Proxmox Anker)
  ↓
AzuraCast (10.3.0.9)
  ↓
Stream: /listen/frawo-funk/radio.mp3
API: /api/nowplaying/frawo-funk
```

### Cloudflare Tunnel Setup (Sicher, kein Port-Forwarding)

```bash
# Auf Proxmox Anker
docker run -d \
  --name cloudflared \
  cloudflare/cloudflared:latest \
  tunnel --no-autoupdate run \
  --token <TUNNEL_TOKEN>

# Cloudflare Dashboard:
# Tunnel → Create Tunnel → funk-frawo
# Public Hostname: funk.frawo-tech.de → http://10.3.0.9:80
```

---

## 📊 MEDIA LIBRARY STATUS (Letzte bekannt)

| Location | Size | Files | Status |
|----------|------|-------|--------|
| Stocki VM 210 NFS | 283 GB | 23.461 | ❌ Offline |
| Anker USB | ? | ? | ❓ |
| Storage Node frawo_curated | 0 GB | 0 | ✅ Bereit |
| Storage Node frawo_incoming | 0 GB | 0 | ✅ Bereit |
| Storage Node yourparty_library | 1.7 GB | 3.631 | ✅ |

**Gesamte verfügbare Library:** ~1.7 GB (nur yourparty)
**Legacy Library (offline):** 283 GB

---

## 🎯 NÄCHSTE SCHRITTE (Priorisiert)

### JETZT (15 Min)

1. ✅ Status dokumentiert (diese Datei)
2. 🔄 Radio Node auf Proxmox Anker finden
3. 🔄 Container/LXC starten
4. 🔄 AzuraCast Service prüfen

### HEUTE (1h)

5. 🔄 funk.frawo-tech.de DNS erstellen (Cloudflare)
6. 🔄 NPM Proxy Host einrichten
7. 🔄 Stream-Test durchführen
8. 🔄 Storage Node Erreichbarkeit prüfen

### DIESE WOCHE (3h)

9. 📦 Radio Player in Odoo Website integrieren
10. 📦 Media Library neu organisieren
11. 📦 Erste kuratierte Playlist erstellen
12. 📦 Dokumentation aktualisieren

### SPÄTER (wenn Stocki online)

13. 📦 283GB Legacy Library migrieren
14. 📦 Backup/Relay Setup auf Stocki
15. 📦 High Availability testen

---

## 📝 WICHTIGE NOTIZEN

### Credentials
- **AzuraCast Admin:** In Vaultwarden (aktuell offline!)
- **Storage Node SMB:** User `radio`, Password in `.env` oder Vaultwarden
- **SSH Anker Radio:** `wolf@10.3.0.9` (Tailscale SSH)

### Dokumente (im Repo)
- [AZURACAST_PLAN.md](../AZURACAST_PLAN.md) - Original Plan
- [OPERATIONS/AZURACAST_STATUS_2026-04-30.md](../OPERATIONS/AZURACAST_STATUS_2026-04-30.md) - Letzter Status
- [OPERATIONS/RADIO_NETWORK_CONSOLIDATION.md](../OPERATIONS/RADIO_NETWORK_CONSOLIDATION.md) - Network Plan
- [apps/radio-player-frontend/](../apps/radio-player-frontend/) - Frontend Code

### Scripts
- `scripts/radio/migrate_stocki_to_storage_node.sh` - Migration Script
- `scripts/radio/fix_stocki_storage_critical.sh` - Storage Fix
- `scripts/radio/backup_azuracast_payload.sh` - Backup Script

---

## ✅ ERFOLGS-KRITERIEN

**Radio ist "LIVE" wenn:**
- ✅ funk.frawo-tech.de ist erreichbar
- ✅ Stream läuft (HTTP 200 auf `/listen/frawo-funk/radio.mp3`)
- ✅ AutoDJ spielt Musik (mindestens 10 Tracks)
- ✅ Now Playing API funktioniert
- ✅ Radio Player auf Website integriert

**Bonus (Nice-to-have):**
- 🌟 SSL/HTTPS funktioniert
- 🌟 Cloudflare CDN aktiv
- 🌟 Backup/Relay auf Stocki läuft
- 🌟 Media Library > 50GB kuratiert

---

**Status:** 🟡 WAITING FOR RADIO NODE
**Nächster Check:** Nach Radio Node wird gestartet
**Verantwortlich:** Wolf (mit Claude Support)
