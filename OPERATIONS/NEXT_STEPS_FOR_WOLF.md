# Next Steps für Wolf - Action Items

**Datum:** 2026-04-30 21:30
**Status:** INFRASTRUCTURE READY - User-Actions erforderlich

---

## ✅ WAS AUTOMATISIERT FERTIG IST

### Infrastructure Checks ✅
- **Storage Node:** SMB User `radio` aktiv, Directories bereit
- **Anker Node:** Erreichbar (ping OK), Docker läuft
- **Stocki Node:** VM läuft, Storage-Problem analysiert
- **Documentation:** 8 Docs + 2 Scripts + Radio Player V2

### Automated Setup ✅
- Storage Node Music Directories erstellt
- SMB User verifiziert
- Network-Routing geprüft
- Container-Status verifiziert

---

## 🔴 NEXT STEPS - BENÖTIGT WOLF'S INPUT

### SCHRITT 1: Web UI Login testen (5 Min)

**Action:**
```
1. Browser öffnen (via ZenBook oder anderem Device im LAN):
   http://10.3.0.9
   oder
   http://radio.hs27.internal

2. Login mit bekannten Credentials:
   - wolf@frawo-tech.de
   - Oder: admin@localhost
   - Password: [Deine AzuraCast Credentials]

3. Falls Login fehlschlägt:
   → DANN: Schritt 2 via ZenBook SSH
```

**Erwartetes Ergebnis:**
- AzuraCast Dashboard sichtbar
- Station "frawo-funk" oder "FraWo - Funk" vorhanden
- Status: Broadcasting

---

### SCHRITT 2: Password Reset (Falls Login fehlschlägt)

**Action:**
```bash
# Via ZenBook (192.168.2.132)
ssh wolf@192.168.2.132

# Dann zu Anker Radio Node
ssh wolf@10.3.0.9

# Admin Accounts auflisten
docker exec azuracast azuracast account:list

# Password reset für bekannten User
docker exec azuracast azuracast account:reset-password EMAIL_HIER

# Oder neuen Admin erstellen
docker exec azuracast azuracast account:create \
  --email wolf@frawo-tech.de \
  --password DEIN_PASSWORT_HIER
```

**Erwartetes Ergebnis:**
- Account-Liste zeigt User
- Password erfolgreich geändert
- Login im Web UI funktioniert

---

### SCHRITT 3: Test-Upload durchführen (5 Min)

**Action:**
```
Web UI → frawo-funk → Media → Upload Files
→ 1-2 Test-MP3s hochladen (Drag & Drop)
→ Warten bis Upload fertig
```

**Erwartetes Ergebnis:**
- Dateien in Media-Liste sichtbar
- Metadata erkannt (Artist, Title)
- Kein Error

---

### SCHRITT 4: Erste Playlist erstellen (5 Min)

**Action:**
```
Web UI → frawo-funk → Playlists → Create Playlist

Name: "Main Rotation"
Type: Standard
Source: All Media
Weight: 10
Schedule: Always play
Enable: ✓
→ Save

Dann:
frawo-funk → Edit → AutoDJ
→ Enable AutoDJ: ✓
→ Save
```

**Erwartetes Ergebnis:**
- Playlist existiert
- Songs in Playlist
- AutoDJ aktiv
- Stream läuft

---

### SCHRITT 5: Stream testen (2 Min)

**Action:**
```
Web UI → frawo-funk → Public Page
→ Play Button klicken

Oder direkt:
http://10.3.0.9/public/frawo-funk
```

**Erwartetes Ergebnis:**
- Audio Player startet
- Musik läuft
- Now Playing zeigt aktuellen Song

---

## 🎵 DANACH: KURATION KANN BEGINNEN!

### Upload-Workflow
```
Option A: Web UI Upload
  → frawo-funk → Media → Upload Files

Option B: SFTP (Bulk)
  → SFTP User erstellen in Web UI
  → FileZilla: 10.3.0.9:2022

Option C: Direct Copy (via ZenBook SSH)
  → scp files to /srv/radio-library/music-usb/
```

### Organization
```
1. Metadata prüfen (MP3Tag)
2. Nach Genre sortieren
3. Playlists per Genre erstellen
4. Rotation weights anpassen
```

---

## 🔧 OPTIONAL - SPÄTER

### Storage Node SMB Mount (via ZenBook)

**Wenn du via ZenBook direkten Network-Zugang zu Anker hast:**

```bash
ssh wolf@10.3.0.9

# SMB Credentials (Storage Node User: radio)
# Password: [MUSS NOCH GESETZT WERDEN - siehe unten]

sudo bash -c 'cat > /etc/hs27/storage-node-media.credentials <<EOF
username=radio
password=PASSWORT_HIER
EOF'
sudo chmod 600 /etc/hs27/storage-node-media.credentials

# Mount
sudo mount -t cifs //10.1.0.30/Media /srv/radio-library/music-network \
  -o credentials=/etc/hs27/storage-node-media.credentials,uid=1000,gid=1000,vers=3.0

# Verify
df -h | grep 10.1.0.30
ls -lah /srv/radio-library/music-network/frawo_curated
```

**SMB Password setzen (auf Storage Node via Proxmox):**
```bash
# Von einem System mit Proxmox Zugang
ssh root@100.69.179.87
pct exec 110 -- smbpasswd radio
# → Passwort eingeben (2x)
# → Passwort notieren für oben!
```

---

### Stocki Storage Cleanup/Migration

**Erst nach Anker production-ready!**

**Quick Cleanup (5 Min):**
```bash
ssh -J stock-pve 192.168.178.210
sudo find /var/azuracast/music_storage -name "*.tmp" -delete
sudo find /var/azuracast/music_storage -name ".DS_Store" -delete
df -h /var/azuracast/music_storage
```

**Vollständige Migration (1-3h):**
```bash
# Vom Repo
bash scripts/radio/migrate_stocki_to_storage_node.sh
# → 283GB rsync
# → Stocki auf SMB umstellen
```

---

### Radio Player V2 Deployment

**Surface Go Frontend:**
```bash
# Copy file
scp apps/radio-player-frontend/site/index_v2.html \
  frawo@192.168.2.154:/home/frawo/radio-player/index.html

# SSH zu Surface Go
ssh frawo@192.168.2.154

# Update Stream URLs in HTML (falls nötig)
# Dann: Firefox Kiosk restart
```

---

## 📋 PRIORITY ORDER

**JETZT (Heute Abend):**
1. ✅ Web UI Login
2. ✅ Test-Upload (1-2 MP3s)
3. ✅ Erste Playlist
4. ✅ Stream testen
5. ✅ → KURATION BEGINNEN!

**MORGEN/SPÄTER:**
6. ⏱️ SMB Mount (optional, für zentrale Library)
7. ⏱️ Stocki Migration (optional, 283GB Legacy-Musik)
8. ⏱️ Radio Player V2 Deployment (optional, Frontend)

---

## 🆘 TROUBLESHOOTING

### Web UI nicht erreichbar
```
Problem: http://10.3.0.9 lädt nicht
Check: Bist du im gleichen Netzwerk wie Anker?
Lösung: Via ZenBook (192.168.2.132) im Browser
```

### Login fehlschlägt
```
Problem: Credentials nicht akzeptiert
Lösung: SSH zu Anker → docker exec → account:reset-password
Details: Siehe SCHRITT 2 oben
```

### Upload fehlschlägt
```
Problem: Dateien können nicht hochgeladen werden
Check 1: Disk Space auf Anker (df -h)
Check 2: File Format (MP3, FLAC, AAC supported)
Check 3: Browser Console (F12) für Errors
```

### Stream lädt nicht
```
Problem: Audio Player startet nicht
Check 1: AutoDJ enabled?
Check 2: Playlist hat Songs?
Check 3: Station Broadcasting Status
```

---

## 📚 DOCUMENTATION REFERENCE

**Für Details siehe:**
- [README_KURATION_START.md](README_KURATION_START.md) ← **START GUIDE**
- [AZURACAST_WEB_UI_SETUP.md](AZURACAST_WEB_UI_SETUP.md) ← **WEB UI DETAILS**
- [AZURACAST_PRODUCTION_READY_PLAN.md](AZURACAST_PRODUCTION_READY_PLAN.md) ← **FULL PLAN**

**Alle Docs in:** `OPERATIONS/` Folder

---

## ✅ SUMMARY

**WAS AUTOMATISIERT FERTIG IST:**
- Infrastructure analysiert & dokumentiert
- Storage Node Music Directories bereit
- Scripts & Frontend fertig
- 8 Docs geschrieben

**WAS WOLF JETZT TUN MUSS:**
1. Web UI Login (5 Min)
2. Test-Upload (5 Min)
3. Playlist erstellen (5 Min)
4. Stream testen (2 Min)
5. → Kuration beginnen!

**Total Time: ~20 Minuten bis KURATION live!** 🎵
