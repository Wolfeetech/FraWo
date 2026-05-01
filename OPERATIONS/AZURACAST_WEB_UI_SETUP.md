# AzuraCast Web UI Setup - HEUTE Kuration starten!

**Datum:** 2026-04-30 21:20
**Strategie:** Web UI statt SSH - schneller zum Ziel!

---

## DIREKTER WEB-ZUGANG (Kein SSH nötig!)

### Anker Node
**URL:** http://radio.hs27.internal
**Von:** StudioPC (wenn im gleichen Netzwerk) ODER ZenBook

### Alternative: Via Browser auf ZenBook
```bash
# Via RDP oder TeamViewer zu ZenBook
# Dann Browser: http://10.3.0.9
```

---

## SETUP SCHRITTE (Web UI)

### 1. Admin Login prüfen
```
URL: http://radio.hs27.internal/login
Credentials: Bekannte Wolf-Credentials testen
```

**Falls Login nicht funktioniert:**
```bash
# Via ZenBook SSH zu Anker
ssh wolf@10.3.0.9
docker exec azuracast azuracast account:reset-password wolf@frawo-tech.de
```

### 2. Station Status prüfen
```
Dashboard → Stations → frawo-funk
→ Status: Broadcasting?
→ Now Playing: Song aktuell?
→ Listeners: 0 ist OK
```

### 3. Media Storage Location hinzufügen
```
frawo-funk → Edit → Media Storage Locations
→ Add Storage Location
Name: "Network Music"
Path: /var/azuracast/stations/frawo-funk/media/network
Adapter: Local Filesystem
→ Save
```

**Wichtig:** Der Path `/var/azuracast/stations/frawo-funk/media/network`
muss auf Host gemountet sein als SMB zu Storage Node.

### 4. USB Music Check
```
frawo-funk → Media → Files
→ Sollte USB Music zeigen (2.120+ Dateien)
→ Wenn leer: Media → Scan for Media
```

### 5. Upload via Media Manager
```
frawo-funk → Media → Upload Files
→ Drag & Drop MP3s
→ Oder: Bulk Upload via SFTP
```

### 6. Playlist erstellen
```
frawo-funk → Playlists → Create Playlist
Name: "Main Rotation"
Type: Standard (oder Advanced für mehr Kontrolle)
Source: All Music (oder Directory-Filter)
Weight: 10
Schedule: Always On
Enable: ✓
→ Save

→ Playlists → Main Rotation → Edit
→ "Schedule" Tab
→ Add Schedule Item: Always play
→ Save
```

### 7. AutoDJ aktivieren
```
frawo-funk → Edit
→ AutoDJ Tab
→ Enable AutoDJ: ✓
→ Save
```

---

## UPLOAD WORKFLOW (OHNE SMB MOUNT)

### Option 1: Web UI Upload (Einfachste)
```
1. Browser: http://radio.hs27.internal
2. Login
3. frawo-funk → Media → Upload Files
4. Drag & Drop MP3s
5. Media → Scan for Media (falls nötig)
6. Fertig!
```

### Option 2: SFTP (Bulk Upload)
```
Host: radio.hs27.internal (oder 10.3.0.9)
Port: 2022 (AzuraCast SFTP)
User: azuracast_sftp_frawo-funk
Password: (aus AzuraCast UI generieren)
Path: /upload/

Tools: FileZilla, WinSCP, etc.
```

**SFTP User erstellen:**
```
frawo-funk → Edit → SFTP Users
→ Add User
Username: wolf_upload
Password: [GENERIEREN]
→ Save
→ Credentials notieren!
```

### Option 3: Direct Copy via ZenBook
```bash
# MP3s von StudioPC zu ZenBook kopieren
# Dann von ZenBook:
scp music/*.mp3 wolf@10.3.0.9:/srv/radio-library/music-usb/
```

---

## KURATION STARTEN (JETZT MÖGLICH!)

### Schritt 1: Test-Upload
```
1. Web UI → frawo-funk → Media → Upload
2. Upload 1-2 Test-MP3s
3. Media → Scan for Media
4. Verify: Dateien tauchen in Media-Liste auf
```

### Schritt 2: Playlist Test
```
1. Playlists → Main Rotation
2. Check: Songs in Playlist?
3. Station Dashboard → Now Playing
4. Stream URL testen in Browser
```

### Schritt 3: Bulk Upload beginnen!
```
1. SFTP User erstellen
2. FileZilla/WinSCP nutzen
3. Batch-Upload von Musik-Collection
4. Media Scan
5. Playlists organisieren nach Genre
```

---

## SMB MOUNT (Optional, später via ZenBook)

**Wenn ZenBook Zugang zu Anker:**
```bash
ssh wolf@10.3.0.9

# Check if already mounted
df -h | grep 10.1.0.30

# If not, mount manually:
sudo mount -t cifs //10.1.0.30/Media /srv/radio-library/music-network \
  -o username=radio,password=RADIO_PASS,uid=1000,gid=1000,vers=3.0

# Verify
ls -lah /srv/radio-library/music-network/frawo_curated
```

---

## CREDENTIALS NEEDED

### Storage Node SMB
- **Share:** `\\10.1.0.30\Media`
- **User:** `radio`
- **Password:** [IN VAULTWARDEN oder bei Storage Node Setup]

**Password finden:**
```bash
# Auf Storage Node (via Proxmox)
ssh root@100.69.179.87
pct exec 110 -- cat /etc/samba/smbpasswd | grep radio
# Oder: pdbedit -L -v
```

### AzuraCast Admin
- **URL:** http://radio.hs27.internal/login
- **Email:** wolf@frawo-tech.de (oder admin@localhost)
- **Password:** [Testen oder via CLI reset]

---

## TROUBLESHOOTING

### Login funktioniert nicht
```bash
# Via ZenBook SSH zu Anker:
ssh wolf@192.168.2.132
ssh wolf@10.3.0.9  # Von ZenBook zu Anker
docker exec azuracast azuracast account:list
# Oder neuen Account:
docker exec azuracast azuracast account:create --email wolf@frawo-tech.de --password YOUR_PASSWORD
```

### Stream lädt nicht
```
1. Station Status: Broadcasting?
2. Mount Point aktiv?
3. AutoDJ enabled?
4. Playlist hat Songs?
```

### Media Upload fehlschlägt
```
1. Disk Space: df -h
2. Permissions: Docker Container als User azuracast
3. File Format: MP3, FLAC, AAC supported
```

---

## NEXT STEPS

**JETZT:**
1. ✅ Browser öffnen: http://radio.hs27.internal
2. ✅ Login testen
3. ✅ Station Status prüfen
4. ✅ Test-Upload (1-2 MP3s)
5. ✅ Playlist erstellen
6. ✅ Stream testen

**DANN KURATION!** 🎵
- Upload via Web UI oder SFTP
- Playlists nach Genre organisieren
- AutoDJ läuft = Radio ist live!

**SMB Mount ist OPTIONAL** - Web UI Upload reicht für HEUTE!
