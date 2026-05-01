# AzuraCast Quick Win - HEUTE Kuration starten!

**Datum:** 2026-04-30 21:05
**Ziel:** Wolf kann HEUTE beginnen Musik zu kuratieren

---

## STRATEGIE: Anker Node First!

**Reality Check:**
- ✅ **Anker Node:** Production-ready, USB Music aktiv
- 🔴 **Stocki Node:** NFS 100% voll, 19.830 Dateien fehlen auf Storage Node
- ⏱️ **Stocki Migration:** 283GB = 1-3 Stunden

**→ Fokus HEUTE: Anker Node perfekt machen, Stocki SPÄTER**

---

## QUICK WIN PLAN (30 Min)

### 1. Anker Node Production Status ✅
```bash
# SSH läuft bereits (bb46924, bb8afff tasks)
# Warten auf:
# - Admin Account List
# - Stream URL

# Falls SSH timeout:
ssh wolf@10.3.0.9
docker exec azuracast azuracast account:list
curl -s http://localhost/api/station/frawo-funk | jq -r '.listen_url'
```

### 2. SMB Mount Anker → Storage Node 🔴 KRITISCH
```bash
ssh wolf@10.3.0.9

# Check current mount
df -h | grep storage
mount | grep 10.1.0.30

# Mount SMB if not mounted
sudo mkdir -p /srv/radio-library/music-network
sudo mount -t cifs //10.1.0.30/Media /srv/radio-library/music-network \
  -o username=radio,password=RADIO_PASSWORD,uid=1000,gid=1000,vers=3.0

# Verify
ls -lah /srv/radio-library/music-network/frawo_curated
```

### 3. AzuraCast Media Path konfigurieren
```bash
# Web UI: http://radio.hs27.internal
# Login mit Wolf credentials
# Station: frawo-funk
# Media → "Add Media Storage Location"
# Path: /var/azuracast/stations/frawo-funk/media/network
# Adapter: Local
```

### 4. Upload-Workflow TEST
```bash
# Von StudioPC
# 1. SMB Mount testen
net use Z: \\10.1.0.30\Media /user:radio RADIO_PASSWORD

# 2. Test-Datei kopieren
# Kopiere 1 MP3 nach Z:\frawo_incoming\

# 3. Auf Anker Node sichtbar?
ssh wolf@10.3.0.9
ls -lah /srv/radio-library/music-network/frawo_incoming/

# 4. In AzuraCast importieren
# Web UI → Media → Scan for new files
```

---

## KURATION WORKFLOW (Ab HEUTE)

### Schritt 1: Upload via SMB
```
StudioPC → \\10.1.0.30\Media\frawo_incoming\
```

### Schritt 2: Metadata prüfen
- Tool: MP3Tag (Windows)
- Pflichtfelder: Artist, Title, Album, Genre, Year
- Cover Art: Mindestens 500x500px

### Schritt 3: Sortieren in Genres
```
frawo_curated/
├── Electronic/
├── Rock/
├── HipHop/
├── Pop/
├── Jazz/
└── ...
```

### Schritt 4: AzuraCast Import
```
Web UI → Media → Scan for Media Files
→ frawo-funk Station
→ Media Storage Location: network
```

### Schritt 5: Playlist erstellen
```
frawo-funk → Playlists → Create New
- Name: "Electronic Rotation"
- Type: Advanced
- Source: Directory = /network/Electronic/
- Weight: 10
- Enable AutoDJ
```

---

## STOCKI NODE - SPÄTER (Morgen oder Wochenende)

**Problem:** 283GB Migration dauert 1-3h
**Lösung:** NFS cleanup ODER vollständige Migration

**Option A: Quick Cleanup (5 Min)**
```bash
# Temp files löschen
ssh -J stock-pve 192.168.178.210
sudo find /var/azuracast/music_storage -name '*.tmp' -delete
sudo find /var/azuracast/music_storage -name '.DS_Store' -delete

# NFS Server direkt
ssh 192.168.178.25  # Wenn möglich
df -h
# Große Dateien identifizieren und ggf. löschen
```

**Option B: Vollständige Migration (Morgen)**
```bash
bash scripts/radio/migrate_stocki_to_storage_node.sh
# 283GB rsync: 1-3 Stunden
# Danach: Stocki auf SMB wie Anker
```

---

## PRODUCTION-READY STATUS

### Anker Node (frawo-funk)
- [ ] Admin-Login verifiziert
- [ ] Stream-URL: `http://radio.hs27.internal/listen/frawo-funk/radio.mp3`
- [ ] SMB Mount: `//10.1.0.30/Media` → `/srv/radio-library/music-network`
- [ ] AzuraCast Media Location: `/var/azuracast/stations/frawo-funk/media/network`
- [ ] Upload-Test: StudioPC → SMB → Anker → AzuraCast ✅
- [ ] AutoDJ läuft

### Storage Node
- ✅ Music Directories: `frawo_curated`, `frawo_incoming` created
- ✅ SMB Share `Media` aktiv
- ✅ User: `radio`
- [ ] Von StudioPC erreichbar: `\\10.1.0.30\Media`

### Kuration Workflow
- [ ] SMB Mount von StudioPC
- [ ] Upload-Path dokumentiert
- [ ] Metadata-Standard definiert
- [ ] Genre-Struktur angelegt
- [ ] AzuraCast Import funktioniert

---

## HEUTE ABEND DONE = KURATION KANN STARTEN!

**Checklist:**
1. ✅ Storage Node Music Directories bereit
2. 🔄 Anker SMB Mount zu Storage Node
3. 🔄 StudioPC SMB Test
4. 🔄 Upload-Workflow funktioniert
5. 🔄 Erste Playlist in AzuraCast

**Stocki kann warten** - Die 283GB Legacy-Library ist nice-to-have, aber nicht nötig um HEUTE zu starten!

---

## NEXT COMMANDS

```bash
# 1. Check Anker SSH tasks
# (Warten auf bb46924, bb8afff)

# 2. Anker SMB Mount
ssh wolf@10.3.0.9
sudo mount -t cifs //10.1.0.30/Media /srv/radio-library/music-network \
  -o credentials=/etc/hs27/storage-node-media.credentials,uid=1000,gid=1000

# 3. StudioPC SMB Test
net use Z: \\10.1.0.30\Media /user:radio

# 4. Test-Upload
# Kopiere 1 MP3 → Z:\frawo_incoming\

# 5. AzuraCast Web UI
# http://radio.hs27.internal
# Media → Scan
```
