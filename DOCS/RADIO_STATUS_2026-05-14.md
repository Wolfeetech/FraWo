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

### Login

| Feld | Wert |
|------|------|
| URL | `http://10.4.0.233` |
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
| Backend | Liquidsoap |
| Stream | `/listen/frawo_funk/radio.mp3` (192kbps MP3) |

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

---

## 📋 NÄCHSTE SCHRITTE

### 🔥 SOFORT (Musik uploaden)

1. [ ] Musik aus `/mnt/music/yourparty.radio/` (67 GB) in AzuraCast importieren
2. [ ] Musik aus `/mnt/music/FraWo_Musikarchiv/` (5 GB) importieren
3. [ ] Erste Playlist "Main Rotation" erstellen
4. [ ] AutoDJ aktivieren → Stream läuft!

### 💡 DIESE WOCHE

5. [ ] funk.frawo-tech.de DNS (Cloudflare)
6. [ ] NPM/Caddy Proxy Host (10.4.0.233:80)
7. [ ] SSL/HTTPS via Let's Encrypt
8. [ ] Radio Player für frawo-tech.de Website
9. [ ] System-URL auf funk.frawo-tech.de ändern

### 📦 BACKLOG

10. [ ] Jellyfin in CT 130 neben AzuraCast (gleiche Music Library)
11. [ ] Timezone auf Europe/Berlin stellen
12. [ ] SFTP-Zugang für Musik-Upload konfigurieren
13. [ ] Backup-Routine einrichten
14. [ ] Raspberry Pi (wenn gefunden) als Relay/Backup

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

**Status:** 🟢 ONLINE — Musik fehlt noch
**Nächster Schritt:** Musik aus Music SSD in AzuraCast laden
**Verantwortlich:** Wolf / Claude
