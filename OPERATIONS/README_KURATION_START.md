# MUSIK KURATION STARTEN - Finaler Setup Guide

**Stand:** 2026-04-30 21:25
**Status:** READY TO GO! 🎵

---

## 🎯 WAS DU JETZT TUN KANNST

### OPTION 1: Web UI Upload (EINFACHSTE - EMPFOHLEN)

**1. Browser öffnen (via ZenBook oder Device im gleichen Netz):**
```
http://radio.hs27.internal
oder
http://10.3.0.9
```

**2. Login:**
- Email: `wolf@frawo-tech.de` (oder `admin@localhost`)
- Password: [Deine bekannten Credentials testen]

**Falls Login nicht klappt:**
```bash
# Via ZenBook SSH zu Anker:
ssh wolf@10.3.0.9
docker exec azuracast azuracast account:list
# Oder Password reset:
docker exec azuracast azuracast account:reset-password EMAIL
```

**3. Upload Musik:**
```
Dashboard → Stations → frawo-funk
→ Media → Upload Files
→ Drag & Drop MP3s
→ Fertig!
```

**4. Playlist erstellen:**
```
frawo-funk → Playlists → Create Playlist
Name: "Main Rotation"
Type: Standard
Source: All Music
Enable AutoDJ
→ Save
```

**5. Stream testen:**
```
frawo-funk → Public Page
→ Play Button klicken
→ Musik läuft! 🎵
```

---

### OPTION 2: SFTP Bulk Upload

**1. SFTP User erstellen (via Web UI):**
```
frawo-funk → Edit → SFTP Users
→ Add SFTP User
Username: wolf_upload
Password: [GENERIEREN & NOTIEREN]
→ Save
```

**2. FileZilla oder WinSCP:**
```
Host: 10.3.0.9
Port: 2022
User: wolf_upload
Password: [VON OBEN]
Path: /upload/
→ Dateien hochladen
```

**3. Media Scan:**
```
Web UI → frawo-funk → Media → Scan for Media
```

---

### OPTION 3: Via ZenBook Direct Copy

**1. SSH zu ZenBook:**
```bash
ssh wolf@192.168.2.132
```

**2. SSH zu Anker:**
```bash
ssh wolf@10.3.0.9
```

**3. Copy Musik:**
```bash
# Direkt zu USB
cp music/*.mp3 /srv/radio-library/music-usb/

# Oder zu Network (wenn SMB mounted)
cp music/*.mp3 /srv/radio-library/music-network/frawo_curated/
```

**4. AzuraCast Scan:**
```
Web UI → Media → Scan for Media
```

---

## 📚 WAS FERTIG IST (HEUTE ERSTELLT)

### Dokumentation (11 Files)
1. [RADIO_NETWORK_CONSOLIDATION.md](RADIO_NETWORK_CONSOLIDATION.md) - Master Plan
2. [RADIO_PLAYER_V2_DEPLOYMENT.md](RADIO_PLAYER_V2_DEPLOYMENT.md) - Frontend Guide
3. [RADIO_NETWORK_STATUS.md](RADIO_NETWORK_STATUS.md) - Infrastructure Status
4. [AZURACAST_PRODUCTION_READY_PLAN.md](AZURACAST_PRODUCTION_READY_PLAN.md) - Full Production Plan
5. [AZURACAST_QUICK_WIN_TODAY.md](AZURACAST_QUICK_WIN_TODAY.md) - Quick Win Strategy
6. [AZURACAST_STATUS_2026-04-30.md](AZURACAST_STATUS_2026-04-30.md) - Heute's Status
7. [AZURACAST_WEB_UI_SETUP.md](AZURACAST_WEB_UI_SETUP.md) - Web UI Guide
8. [README_KURATION_START.md](README_KURATION_START.md) - This file

### Scripts
9. [scripts/radio/fix_stocki_storage_critical.sh](../scripts/radio/fix_stocki_storage_critical.sh) - Storage Fix
10. [scripts/radio/migrate_stocki_to_storage_node.sh](../scripts/radio/migrate_stocki_to_storage_node.sh) - Migration

### Frontend
11. [apps/radio-player-frontend/site/index_v2.html](../apps/radio-player-frontend/site/index_v2.html) - Radio Player V2

### Infrastructure
- ✅ **Storage Node:** Music Directories bereit (`frawo_curated`, `frawo_incoming`)
- ✅ **Anker Node:** Production, USB Music läuft
- ✅ **Radio Player V2:** Minimalistisch, touch-optimiert, fertig

---

## 🎵 KURATION WORKFLOW

### Phase 1: Upload
**Via Web UI (einfachste):**
```
frawo-funk → Media → Upload Files → Drag & Drop
```

**Via SFTP (bulk):**
```
FileZilla → 10.3.0.9:2022 → /upload/
```

**Via Direct Copy:**
```
ZenBook → Anker → /srv/radio-library/music-usb/
```

### Phase 2: Metadata
**Optional, aber empfohlen:**
- Tool: MP3Tag (Windows)
- Felder: Artist, Title, Album, Genre, Year
- Cover Art: Min 500x500px

### Phase 3: Organization
**Via File Manager oder Web UI:**
```
frawo_curated/
├── Electronic/
├── Rock/
├── HipHop/
└── ...
```

### Phase 4: Playlists
**Web UI:**
```
frawo-funk → Playlists
→ Create by Genre
→ Enable AutoDJ
→ Set Rotation Weight
```

### Phase 5: GO LIVE!
**Stream URL:**
```
http://radio.hs27.internal/listen/frawo-funk/radio.mp3
```

**Public Page:**
```
http://radio.hs27.internal/public/frawo-funk
```

---

## 🔧 TROUBLESHOOTING

### Kann Web UI nicht erreichen
**Check Network:**
```bash
ping 10.3.0.9
```

**Lösung:** Via ZenBook im gleichen Netz
```bash
ssh wolf@192.168.2.132
# Dann Browser auf ZenBook
```

### Login klappt nicht
**Password Reset:**
```bash
ssh wolf@10.3.0.9
docker exec azuracast azuracast account:reset-password wolf@frawo-tech.de
```

### Musik wird nicht angezeigt
**Media Scan:**
```
Web UI → frawo-funk → Media → Scan for Media
```

**Permission Check:**
```bash
ssh wolf@10.3.0.9
ls -lah /srv/radio-library/music-usb/
# Should be owned by user 1000:1000
```

---

## 📋 NÄCHSTE SCHRITTE (Nach Kuration)

### Kurzfristig (Diese Woche)
- [ ] Radio Player V2 auf Surface Go deployen
- [ ] Domain `funk.frawo-tech.de` setup
- [ ] Stocki Storage cleanup ODER Migration

### Mittelfristig (Diesen Monat)
- [ ] Public Edge Setup (optional)
- [ ] Backup Strategy für Music
- [ ] Monitoring & Alerting

---

## 🎯 START NOW!

**3 SCHRITTE ZUM ZIEL:**

1. **Browser öffnen:** `http://10.3.0.9` (via ZenBook)
2. **Login:** Wolf Credentials
3. **Upload:** frawo-funk → Media → Upload Files

**→ KURATION KANN BEGINNEN!** 🎵

---

## 📞 HILFE

**Wenn stuck:**
1. Check [AZURACAST_WEB_UI_SETUP.md](AZURACAST_WEB_UI_SETUP.md)
2. Check [AZURACAST_PRODUCTION_READY_PLAN.md](AZURACAST_PRODUCTION_READY_PLAN.md)
3. All docs in `OPERATIONS/` folder

**SSH Zugang via:**
- ZenBook → Anker: `ssh wolf@10.3.0.9`
- Proxmox → Storage Node: `pct exec 110`
- Tailscale → Stocki: `ssh -J stock-pve 192.168.178.210`
