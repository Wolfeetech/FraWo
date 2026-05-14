# Radio / AzuraCast Status - 2026-05-14

**Update:** AzuraCast erfolgreich auf Proxmox Anker deployed (CT 130)
**Status:** 🟢 ONLINE — Setup abgeschlossen, bereit für Musik

---

## 🎯 AKTUELLER STATUS: ✅ AZURACAST LIVE

### Neue Infrastruktur

| Component | IP / Details | Status |
|-----------|-------------|--------|
| **CT 130 (radio-node)** | `10.4.0.233` | ✅ RUNNING |
| **AzuraCast Web UI** | `http://10.4.0.233` | ✅ ONLINE |
| **Station "FraWo Funk"** | ID: 1, Shortcode: `frawo_funk` | ✅ KONFIGURIERT |
| **Stream URL** | `http://10.4.0.233/listen/frawo_funk/radio.mp3` | ✅ BEREIT |
| **Public Player** | `http://10.4.0.233/public/frawo_funk` | ✅ BEREIT |
| **Now Playing API** | `http://10.4.0.233/api/nowplaying/frawo_funk` | ✅ BEREIT |
| **Music SSD** | `/mnt/music` (983 GB, 72 GB belegt) | ✅ GEMOUNTET |

### Container Specs (CT 130)

| Eigenschaft | Wert |
|-------------|------|
| Hostname | `radio-node` |
| OS | Ubuntu 24.04 LTS |
| RAM | 2 GB + 1 GB Swap |
| Cores | 2 |
| Rootfs | 32 GB auf `ssd2tb` (USB 3.0 2TB SSD) |
| Music Mount | `/mnt/music_ssd` → `/mnt/music` (bind) |
| Docker | v29.4.3 + Compose v5.1.3 |
| AzuraCast RAM | ~640 MB (von 2 GB) |
| Onboot | ✅ Ja |
| **Audio Processing** | 🎛️ **master_me** (Multiband Mastering, -14 LUFS, ReplayGain) |
| **AutoCue** | ⚡ Aktiviert (Nahtlose Cues, Stille-Erkennung) |

### Login

| Feld | Wert |
|------|------|
| URL | `https://funk.frawo-tech.de` |
| User | `wolf@frawo-tech.de` |
| Passwort | `FraWoFunk2026!` |
| SFTP Port | `2022` |

### Station Config

| Feld | Wert |
|------|------|
| Name | FraWo Funk |
| Shortcode | `frawo_funk` |
| Beschreibung | Community Radio. Bodensee. |
| Genre | Electronic / Alternative / Community |
| Frontend | Icecast |
| Backend | Liquidsoap (v2.3+) |
| **Mount 1 (Standard)** | 📻 `/listen/frawo_funk/radio.mp3` (192kbps MP3) |
| **Mount 2 (Studio)** | 🎧 `/listen/frawo_funk/hifi.mp3` (320kbps MP3 Studio Quality) |
| **Mount 3 (Mobile)** | 📱 `/listen/frawo_funk/mobile.aac` (64kbps AAC+ HE-v2 für Unterwegs) |

---

## ✅ WAS ERLEDIGT WURDE

1. ✅ Proxmox Anker Zugang verifiziert
2. ✅ Raspberry Pi Status geprüft (OFFLINE — physisch nicht erreichbar)
3. ✅ Entscheidung: AzuraCast auf Proxmox Anker statt Pi
4. ✅ CT 130 erstellt (Ubuntu 24.04, ssd2tb Storage)
5. ✅ Music SSD gemountet (/mnt/music_ssd → /mnt/music)
6. ✅ Docker installiert
7. ✅ AppArmor-Fix für LXC+Docker
8. ✅ AzuraCast installiert und gestartet
9. ✅ Setup-Wizard: Admin-Account erstellt
10. ✅ Setup-Wizard: Station "FraWo Funk" erstellt
11. ✅ Setup-Wizard: System-Einstellungen konfiguriert
12. ✅ API verifiziert: `{"online":true}`
13. ✅ Musik aus Music SSD (Clean Library) in AzuraCast importiert (476+ Tracks gescannt)
14. ✅ Erste Playlist "Main Rotation" erstellt und Tracks zugewiesen (287+ Tracks aktiv)
15. ✅ AutoDJ aktiviert → Stream läuft & Now Playing API liefert aktuelle Songdaten

---

## 📋 NÄCHSTE SCHRITTE

### 💡 DIESE WOCHE

1. [ ] funk.frawo-tech.de DNS (Cloudflare Dashboard Public Hostname anlegen)
2. ✅ Caddy Proxy Host konfiguriert (http://funk.frawo-tech.de -> 10.4.0.233:80)
3. ✅ SSL/HTTPS via Cloudflare Zero Trust
4. ✅ Radio Player für frawo-tech.de Website (Embed-Code vorbereitet)
5. ✅ System-URL auf funk.frawo-tech.de geändert

### 📦 BACKLOG

6. ✅ Navidrome Media Server in CT 130 neben AzuraCast (gleiche Music Library / music-ssd)
7. ✅ Timezone auf Europe/Berlin gestellt (via .env)
8. ✅ Samba & SFTP-Zugänge für Musik-Upload konfiguriert (Samba Share & Port 2022 aktiv)
9. ✅ Backup-Routine eingerichtet (Täglich 04:00 Uhr, 7 Kopien, Media excluded)
10. [ ] Raspberry Pi (wenn gefunden) als Relay/Backup

---

## 📂 MUSIK-SORTIERUNG, TAGGING & SYNC (Workflow)

Um die Musikbibliothek professionell zu pflegen, ID3-Tags zu bearbeiten und Playlists zu synchronisieren, stehen zwei dedizierte Zugänge bereit, die direkt mit AzuraCast verknüpft sind:

### 1. Navidrome Web-Medienserver (GUI & Streaming)
- **URL:** `http://media.hs27.internal` (oder direkt `http://10.4.0.233:4533`)
- **Funktion:** Visuelles Verwalten, Sortieren, Anhören und Erstellen von Playlists. Navidrome greift auf denselben Speicher (`/mnt/music`) zu. Jede Änderung wird dank automatischer Scan-Routinen sofort in AzuraCast übernommen.

### 2. Samba Netzwerkfreigabe (Für Windows / macOS Desktop-Tools)
- **Pfad:** `\\10.4.0.233\music` (im Windows Explorer als Netzlaufwerk einbinden)
- **Zugriff:** Gastzugriff / Ohne Passwort im LAN (oder User `smbuser`, Passwort `FraWoFunk2026!`)
- **Professioneller Workflow:** Öffne dieses Netzlaufwerk direkt in Tools wie **Mp3tag**, **MusicBrainz Picard** oder **Rekordbox**, um Cover-Bilder, BPM, Key, ISRC und Titel-Tags in den Originaldateien zu normieren.

---

## 🎧 WEBSITE EMBED-CODE (Für frawo-tech.de)
Um den Live-Player auf der FraWo-Website einzubinden, nutze folgenden iFrame-Snippet:
```html
<iframe src="https://funk.frawo-tech.de/public/frawo_funk?theme=dark" 
        frameborder="0" 
        allowtransparency="true" 
        style="width: 100%; min-height: 150px; border: 0;">
</iframe>
```

---

## 📊 RESSOURCEN-BUDGET (Anker nach CT 130)

| Was | RAM allokiert | RAM tatsächlich | Status |
|-----|---------------|-----------------|--------|
| CT 100 (Toolbox) | 2 GB | 359 MB | ✅ |
| CT 110 (Storage) | 1 GB | 21 MB | ✅ |
| CT 120 (Vaultwarden) | 1 GB | 68 MB | ✅ |
| **CT 130 (Radio)** | **2 GB** | **640 MB** | ✅ **NEU** |
| VM 210 (HAOS) | 3 GB | ~2.3 GB | ✅ |
| VM 220 (Odoo) | 3 GB | ~1.6 GB | ✅ |
| VM 240 (PBS) | 2 GB | ? | ✅ |
| **Gesamt aktiv** | **14 GB** | **~5-6 GB** | ✅ |
| **Frei** | **~2 GB** | **~10 GB** | ✅ |
| VM 200 (Nextcloud) | 3 GB | - | ⏸️ gestoppt |
| VM 230 (Paperless) | 3 GB | - | ⏸️ gestoppt |

> **Hinweis:** Wenn Nextcloud + Paperless starten (je 3 GB), wird's eng.
> Empfehlung: RAM-Allokation der VMs reduzieren (Odoo 3→2 GB, HAOS 3→2 GB)
> oder Host-RAM aufrüsten (aktuell 16 GB).

---

## 📝 WICHTIGE HINWEISE

### Raspberry Pi (alter Radio-Node)
- Status: **OFFLINE** seit mindestens Mai 2026
- IPs: 192.168.2.155 / 100.64.23.77 / 10.3.0.9 — alle unreachable
- Nicht in Tailscale gelistet
- **Aktion:** Physisch prüfen wenn gelegenheit

### Proxmox LXC Config
```
# /etc/pve/lxc/130.conf
arch: amd64
cores: 2
features: nesting=1,keyctl=1
hostname: radio-node
memory: 2048
mp0: /mnt/music_ssd,mp=/mnt/music
net0: name=eth0,bridge=vmbr0,ip=dhcp
onboot: 1
ostype: ubuntu
rootfs: ssd2tb:130/vm-130-disk-0.raw,size=32G
swap: 1024
unprivileged: 0
lxc.apparmor.profile: unconfined
```

---

**Status:** 🟢 ONLINE — Stream läuft aktiv!
**Nächster Schritt:** DNS/Proxy für funk.frawo-tech.de oder Nextcloud/Paperless starten.
**Verantwortlich:** Wolf / Gemini
