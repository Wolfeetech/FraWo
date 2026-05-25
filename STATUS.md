# Aktueller Status & Praxis-Scan (Stand: 2026-05-25)

Dieses Dokument beschreibt den **tatsächlich getesteten und diagnostizierten** Zustand des Systems nach vollständigem Audit.

---

## 1. Heute behoben (2026-05-25)

| Problem | Ursache | Fix |
|---------|---------|-----|
| Odoo VM (220) komplett eingefroren | Alle Userspace-Prozesse frozen (OOM-Kill, kein Swap) | Force-Stop + Start via PVE |
| SSH nicht erreichbar auf VM 220 | `sshd_config.d/10-hs27-lan-only.conf` hatte alte IP `192.168.2.22` | `ListenAddress 0.0.0.0` gesetzt |
| OOM-Kill Risiko auf VM 220 | Kein Swap konfiguriert, RAM 2.4/2.9GB voll | 2GB Swapfile angelegt + `/etc/fstab` Eintrag |
| Zombie-Container auf VM 220 | `edge_web_1` (Created) + `edge_db_1` (Exited) | `docker rm` ausgeführt |

---

## 2. Was läuft und getestet ist (Fakten)

### 🌍 Öffentliche Dienste
- **`https://www.frawo-tech.de/`**: **ERREICHBAR** ✅ HTTP 200
- **`https://frawo-tech.de/`**: **ERREICHBAR** ✅ HTTP 200

### 🖥️ Odoo (VM 220)
- **`10.4.0.22:8069`**: **ERREICHBAR** ✅ HTTP 200
- **Via Toolbox**: `http://100.82.26.53:8444` → HTTP 200 ✅
- Container: `odoo-web-1` Up, `odoo-db-1` Up ✅
- Datenbank: `FraWo_GbR` ✅
- Swap: 2GB aktiv ✅

### ☁️ Nextcloud (VM 300)
- **Intern** `10.4.0.21:80`: HTTP 302 ✅
- Containers: `nextcloud_app_1`, `nextcloud_db_1`, `nextcloud_redis_1` — alle Up 22h+ ✅
- **Öffentlich** `cloud.frawo-tech.de`: ❌ HTTP 502 (Cloudflare Tunnel hat alte IP, siehe unten)

### 📄 Paperless (VM 330)
- **Intern** `10.4.0.23:8000`: HTTP 302 ✅
- Containers: webserver (healthy), tika, broker, gotenberg, db — alle Up ✅

### 🏠 Toolbox (CT 100)
- Caddy: Up 5 Wochen, Config valid ✅
- Uptime Kuma: healthy ✅
- Jellyfin: healthy ✅
- AdGuard: Up ✅
- Open-WebUI: healthy ✅
- cloudflared: aktiv (systemd) ✅
- Disk: 60% ⚠️

---

## 3. Was defekt oder offen ist

### 🔴 cloud.frawo-tech.de → HTTP 502
- **Ursache**: Cloudflare Zero Trust Tunnel-Ingress zeigt auf **alte IP `10.1.0.21`**
- **Nextcloud läuft** auf `10.4.0.21` und ist intern erreichbar
- **Fix**: Cloudflare Dashboard → Zero Trust → Tunnels → Ingress Rule für `cloud.frawo-tech.de` → Origin auf `http://10.4.0.21` ändern
- **Weitere veraltete IPs im Tunnel prüfen** (radio, vault, ha usw.)

### 🔴 Stockenweiler PVE — offline
- SSH `stock-pve` (`100.91.20.116`): NICHT ERREICHBAR — physisch ausgeschaltet
- Last seen Tailscale: **15 Tage**
- Benötigt: Physischer Besuch in Rothkreuz (Wolf)
- Blockiert: AzuraCast Migration, Home Assistant Eltern, Lane D + E

### ⚠️ hs27-media: 80% voll
- `/mnt/hs27-media` (NFS-Share vom Storage-Node): 78G / 98G
- Aktion: Alte Mediendateien prüfen und aufräumen

### ⚠️ frawo-docker-1 nicht zugänglich
- Tailscale: `100.94.32.41` aktiv, aber SSH-Key nicht hinterlegt
- Rolle im System unklar — muss eingeordnet werden

### ⚠️ StudioPC — Docker inaktiv
- Docker läuft, nur gestoppte Dev-Container (YourParty, VS Code)
- Rolle als SSH-Brücke und lokaler Docker-Host nach Best Practice definieren

---

## 4. Nächste Schritte (priorisiert)

### Sofort (Agent):
1. ~~Odoo VM reparieren~~ ✅ Erledigt heute
2. **Cloudflare Tunnel Ingress-IPs prüfen und auf `10.4.0.x` aktualisieren** (Dashboard)
3. Git commit + push dieser Docs

### Wolf (manuell):
4. **Stockenweiler PVE physisch einschalten** (Rothkreuz vor Ort)
5. **Windows Registry UDP-Fix** (Admin-Terminal, aus LIVE_CONTEXT.md)
6. **Cloudflare Dashboard**: Tunnel-Ingress `cloud.frawo-tech.de` → `http://10.4.0.21`
7. **hs27-media aufräumen**: 78G/98G belegt → Platz schaffen

### Gemeinsam (Wolf + Agent):
8. **frawo-docker-1 SSH-Key hinterlegen** + Rolle definieren
9. **StudioPC Rolle** in Infrastruktur definieren (SSH-Bridge? Local Dev? CI?)
10. **Cloudflare Security Headers** (Transform Rules — aus STATUS 2026-05-20 noch offen)
11. **Uptime Kuma** externer Check konfigurieren (aktuell intern auf Toolbox — Best Practice: externer VPS)

---

## 5. Bekannte Konfigurationsdrift (10.1.0.x → 10.4.0.x)

Bei der Netzwerk-Migration wurden nicht alle Config-Files aktualisiert:

| Datei | Problem | Fix |
|-------|---------|-----|
| `/etc/ssh/sshd_config.d/10-hs27-lan-only.conf` auf VM 220 | `192.168.2.22` + `10.1.0.x` statt `10.4.0.x` | ✅ Heute gefixt |
| Cloudflare Tunnel Ingress (Dashboard) | `10.1.0.21` für Nextcloud | ❌ Noch offen |
| Weitere Tunnel-Ingress-Rules (vault, ha, radio) | Wahrscheinlich auch `10.1.0.x` | ❌ Prüfen |

---

*Updated: 2026-05-25 12:10 Europe/Berlin*
*Audit: Claude Sonnet 4.6 + Wolf*
