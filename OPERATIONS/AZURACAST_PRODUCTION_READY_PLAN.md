# AzuraCast Production-Ready Plan

**Status:** IN EXECUTION
**Datum:** 2026-04-30
**Ziel:** Komplette AzuraCast Infra fertig für Music Kuration HEUTE

---

## CRITICAL PATH (Heute fertig!)

### 1. STOCKI STORAGE FIX 🔴 KRITISCH
**Problem:** NFS 100% voll → Kein Upload/Änderungen möglich
**Lösung:** Migration zu Storage Node SMB

```bash
# OPTION 1: Quick Cleanup (5 Min)
bash scripts/radio/fix_stocki_storage_critical.sh

# OPTION 2: Vollständige Migration (1-3h)
bash scripts/radio/migrate_stocki_to_storage_node.sh
```

**Acceptance:**
- [ ] Stocki Music Storage < 80%
- [ ] AzuraCast kann Dateien schreiben
- [ ] Stream läuft weiter

---

### 2. ANKER NODE FINALISIERUNG
**Ziel:** Production-ready für Music Kuration

**Checklist:**
- [ ] Admin-Credentials dokumentiert
- [ ] SMB Mount zu Storage Node aktiv
- [ ] Station "frawo-funk" konfiguriert
- [ ] Stream-URL verifiziert
- [ ] API `/api/nowplaying` funktioniert
- [ ] Music Upload-Pfad klar

**Actions:**
```bash
# SSH zu Anker
ssh wolf@10.3.0.9

# 1. Admin Account prüfen
docker exec azuracast azuracast account:list

# 2. SMB Mount Status
df -h | grep storage
mount | grep storage

# 3. Stream URL
curl -s http://localhost/api/station/frawo-funk | jq -r '.listen_url'

# 4. Station Media Path
docker exec azuracast ls -lah /var/azuracast/stations/frawo-funk/media
```

---

### 3. MUSIC LIBRARY KONSOLIDIERUNG
**Ziel:** Eine zentrale, kuratierbare Library

**Current State:**
- **Anker USB:** 2.120 Dateien (USB `76E8-CACF`)
- **Stocki NFS:** 23.461 Dateien (283GB)
- **Storage Node:** Leer (vorbereitet für Ziel)

**Target State:**
```
//10.1.0.30/Media/
├── yourparty_Libary/          ← Stocki Migration
│   └── (23.461 Tracks)
├── frawo_curated/             ← Neue kuratierte Library
│   ├── Electronic/
│   ├── Rock/
│   ├── HipHop/
│   └── ...
└── frawo_incoming/            ← Upload-Staging
```

**Actions:**
```bash
# 1. Storage Node vorbereiten
ssh root@10.1.0.30
mkdir -p /srv/storage/media/{yourparty_Libary,frawo_curated,frawo_incoming}
chown -R nobody:nogroup /srv/storage/media/frawo_*
chmod -R 775 /srv/storage/media/frawo_*

# 2. Beide Nodes auf Storage Node mounten
# Anker: Bereits in host_vars vorbereitet
# Stocki: Nach Migration

# 3. Deduplizierung
# Anker USB vs Stocki NFS overlaps finden
# fdupes oder MD5-Checksummen
```

---

### 4. EINHEITLICHE ADMIN-CREDENTIALS

**Ziel:** Ein Login für beide AzuraCast Nodes

**Standard:**
- Username: `wolf` (oder `admin`)
- Password: In Vaultwarden speichern
- Email: `wolf@frawo-tech.de`

**Actions:**
```bash
# Anker Node
ssh wolf@10.3.0.9
docker exec azuracast azuracast account:reset-password wolf@frawo-tech.de

# Stocki Node
ssh -J stock-pve 192.168.178.210
docker exec azuracast azuracast account:reset-password wolf@frawo-tech.de

# Vaultwarden Entry
# Title: AzuraCast Admin (All Nodes)
# Username: wolf@frawo-tech.de
# Password: [GENERIERT]
# URLs:
#   - http://radio.hs27.internal
#   - https://radio.yourparty.tech
```

---

### 5. STREAM-URLS VERIFIZIEREN

**Anker (frawo-funk):**
```bash
ssh wolf@10.3.0.9 "curl -s http://localhost/api/station/frawo-funk | jq"

# Expected:
{
  "station": {
    "name": "FraWo - Funk",
    "shortcode": "frawo-funk",
    "listen_url": "http://radio.hs27.internal/listen/frawo-funk/radio.mp3"
  }
}
```

**Stocki (yourparty):**
```bash
ssh -J stock-pve 192.168.178.210 "curl -s http://localhost/api/station/yourparty | jq"

# Expected:
{
  "station": {
    "name": "Radio YourParty",
    "shortcode": "yourparty",
    "listen_url": "https://radio.yourparty.tech/listen/yourparty/radio.mp3"
  }
}
```

---

### 6. KURATION VORBEREITEN

**Workflow:**
1. Upload zu `frawo_incoming/` via SMB (Windows Explorer)
2. Dateien prüfen (Metadata, Quality)
3. In Genres sortieren → `frawo_curated/Genre/`
4. In AzuraCast importieren
5. Playlists erstellen

**Tools:**
- **SMB Mount:** `\\10.1.0.30\Media`
- **Windows Explorer:** Drag & Drop
- **MP3Tag:** Metadata-Editor
- **AzuraCast Web UI:** Media Management

**SMB Access von StudioPC:**
```powershell
# Network Drive mappen
net use Z: \\10.1.0.30\Media /user:STORAGE_USER STORAGE_PASSWORD

# Oder direkt im Explorer
\\10.1.0.30\Media
```

---

## PRODUCTION-READY CHECKLIST

### Anker Node (frawo-funk)
- [ ] Admin-Login funktioniert
- [ ] SMB Mount zu Storage Node: `//10.1.0.30/Media/frawo_curated`
- [ ] Stream-URL: `http://radio.hs27.internal/listen/frawo-funk/radio.mp3`
- [ ] API Now-Playing: `http://radio.hs27.internal/api/nowplaying/frawo-funk`
- [ ] Media Upload-Path: `/var/azuracast/stations/frawo-funk/media`
- [ ] Playlist "Main Rotation" existiert
- [ ] AutoDJ läuft

### Stocki Node (radio.yourparty)
- [ ] Storage < 80%
- [ ] Admin-Login funktioniert (gleiche Credentials wie Anker)
- [ ] SMB Mount zu Storage Node (nach Migration)
- [ ] Stream-URL: `https://radio.yourparty.tech/listen/yourparty/radio.mp3`
- [ ] API Now-Playing funktioniert
- [ ] Memory < 50% Swap

### Storage Node
- [ ] SMB Share `Media` erreichbar
- [ ] Directories: `yourparty_Libary`, `frawo_curated`, `frawo_incoming`
- [ ] Permissions: `nobody:nogroup`, `775`
- [ ] Von StudioPC mountbar: `\\10.1.0.30\Media`

### Radio Player V2
- [ ] Deployed auf Surface Go
- [ ] Stream-URLs korrekt
- [ ] Now-Playing Updates funktionieren
- [ ] Touch-optimiert getestet

---

## EXECUTION ORDER (Heute!)

### Phase 1: Stocki Storage Fix (30 Min - 3h)
1. Run `fix_stocki_storage_critical.sh` (Quick cleanup)
2. **ENTSCHEIDUNG:** Migration oder Cleanup ausreichend?
3. Wenn Migration: Run `migrate_stocki_to_storage_node.sh` (1-3h)

### Phase 2: Credentials & Verification (15 Min)
1. Anker Admin-Account prüfen
2. Stocki Admin-Account prüfen
3. Passwörter vereinheitlichen
4. Vaultwarden-Entry erstellen
5. Stream-URLs testen

### Phase 3: Music Library Setup (30 Min)
1. Storage Node Directories erstellen
2. SMB von StudioPC testen
3. Anker SMB Mount aktivieren
4. Upload-Workflow testen

### Phase 4: Kuration kann beginnen! ✅
1. Musik via SMB hochladen
2. In AzuraCast importieren
3. Playlists bauen
4. AutoDJ aktivieren

---

## NACH HEUTE

### Short-term (Diese Woche)
- [ ] Radio Player V2 auf Surface Go deployen
- [ ] Domain-Migration `radio.yourparty.tech` → `funk.frawo-tech.de`
- [ ] Deduplizierung Anker USB vs Stocki Library
- [ ] Public Edge Setup (optional)

### Mid-term (Diesen Monat)
- [ ] Mobile Node Setup
- [ ] Backup-Strategy für Music Library
- [ ] Monitoring & Alerting
- [ ] SMTP für AzuraCast (nach Pi SSH-Fix)

---

## SUPPORT SCRIPTS

**Storage Fix:**
- `scripts/radio/fix_stocki_storage_critical.sh` - Quick cleanup
- `scripts/radio/migrate_stocki_to_storage_node.sh` - Full migration

**Verification:**
- `scripts/radio/verify_azuracast_production.sh` - Full health check

**Music Management:**
- `scripts/radio/deduplicate_libraries.sh` - Find duplicates
- `scripts/radio/import_to_azuracast.sh` - Batch import

---

## TROUBLESHOOTING

### Stocki Storage immer noch voll
1. Check NFS Server direkt: `ssh 192.168.178.25`
2. Disk erweitern am NFS Server selbst
3. Oder: Vollständige Migration zu Storage Node

### SMB Mount funktioniert nicht
1. Credentials prüfen: `/etc/hs27/storage-node-media.credentials`
2. Network Test: `ping 10.1.0.30`
3. SMB Test: `smbclient //10.1.0.30/Media -U USER`

### Stream lädt nicht
1. Container Status: `docker ps`
2. Liquidsoap Logs: `docker logs azuracast`
3. Port Check: `netstat -tlnp | grep 8000`

### AzuraCast CLI funktioniert nicht
1. Container exec: `docker exec azuracast bash`
2. CLI Path: `which azuracast`
3. Permissions: Container läuft als User `azuracast`
