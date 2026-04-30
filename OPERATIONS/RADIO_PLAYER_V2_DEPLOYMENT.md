# Radio Player V2 Deployment Plan

## Status: READY FOR DEPLOYMENT
**Erstellt:** 2026-04-30
**Ziel:** Surface Go Kiosk Frontend

---

## V2 Features

### Design Philosophy
- **Minimalistisch:** Wenig Text, visuelle Elemente im Vordergrund
- **Editierbar:** Reines HTML/CSS/JS, kein Build-Step nötig
- **Touch-First:** Große Buttons für Surface Go Touchscreen
- **Multi-Station:** Anker + Stocki gleichzeitig sichtbar

### Visual Elements
- 🎵 Logo (Gradient Box)
- 📻 FraWo Funk Station Icon
- 🎧 Radio YourParty Station Icon
- 📍 Location Badges
- ● Live-Status (Pulsierend grün/rot)

### Technical Stack
- Pure HTML5/CSS3/JavaScript
- No frameworks, no build process
- Fetch API for nowplaying updates
- HTML5 Audio Element for streaming

---

## Deployment-Optionen

### Option A: Standalone HTML (Quick Test)
```bash
# Copy to Surface Go
scp apps/radio-player-frontend/site/index_v2.html frawo@192.168.2.154:~/radio-player.html

# Open in Firefox Kiosk
firefox --kiosk file:///home/frawo/radio-player.html
```

### Option B: Python HTTP Server (Current Surface Setup)
```bash
# On Surface Go
cd ~/
mkdir -p radio-player
# Copy index_v2.html to index.html
python3 -m http.server 17828 --directory ~/radio-player

# Firefox Kiosk
firefox --kiosk http://localhost:17828
```

### Option C: Docker/Nginx (Production)
- Use existing `apps/radio-player-frontend/Dockerfile`
- Replace `site/index.html` with `index_v2.html`
- Deploy to Proxmox CT or VM
- Reverse proxy via NPM

---

## Pre-Deployment Checklist

### 1. Stream URLs verifizieren
**Anker (FraWo Funk):**
- [ ] Base URL: `http://radio.hs27.internal`
- [ ] Stream Endpoint: `/listen/frawo-funk/radio.mp3` oder `/radio/8000/radio.mp3`
- [ ] API Endpoint: `/api/nowplaying/frawo-funk`
- [ ] Test: `curl http://radio.hs27.internal/api/nowplaying/frawo-funk`

**Stocki (Radio YourParty):**
- [ ] Base URL: `https://radio.yourparty.tech` (oder Internal IP)
- [ ] Stream Endpoint: TBD
- [ ] API Endpoint: TBD
- [ ] Test: Aktuell offline wegen Storage

### 2. Netzwerk-Zugriff
**Surface Go → Anker Radio:**
- [ ] Surface Go IP: `192.168.2.154`
- [ ] Anker Radio IP: `10.3.0.9` (VLAN 103)
- [ ] Test: `ping 10.3.0.9` von Surface Go
- [ ] DNS: `radio.hs27.internal` auflösen

**Surface Go → Stocki Radio:**
- [ ] Via Tailscale oder Public Domain
- [ ] Test nach Storage-Fix

### 3. CORS Headers
**Problem:** Browser kann API nicht fetchen wenn CORS fehlt
**Lösung:** AzuraCast hat CORS standardmäßig aktiviert
**Test:**
```bash
curl -H "Origin: http://localhost:17828" \
     -H "Access-Control-Request-Method: GET" \
     -X OPTIONS \
     http://radio.hs27.internal/api/nowplaying/frawo-funk
```

### 4. Surface Go Kiosk Setup
- [ ] Firefox Kiosk Mode aktiv
- [ ] Auto-Start nach Boot
- [ ] Auto-Login User `frawo`
- [ ] Fullscreen (F11)
- [ ] No Screensaver

---

## Stream Endpoint Discovery

### Methode 1: AzuraCast API
```bash
# Get station info
curl http://radio.hs27.internal/api/station/frawo-funk

# Expected response includes:
# - listen_url: Direct stream URL
# - mounts: Available stream mounts
```

### Methode 2: AzuraCast Web UI
1. Login zu `http://radio.hs27.internal`
2. Station "FraWo Funk" öffnen
3. "Public Pages" → "Embed Player"
4. Stream URL kopieren

### Methode 3: Docker Inspect
```bash
ssh wolf@10.3.0.9
docker exec azuracast bash -c 'cat /var/azuracast/stations/frawo-funk/config/icecast.xml | grep listen-socket'
```

---

## Deployment Steps

### Phase 1: Local Test (StudioPC)
```bash
cd /c/WORKSPACE/FraWo/apps/radio-player-frontend/site
cp index_v2.html index.html
python -m http.server 8080
# Open http://localhost:8080
```

### Phase 2: Surface Go Deployment
```bash
# 1. Copy file
scp apps/radio-player-frontend/site/index_v2.html frawo@192.168.2.154:/home/frawo/radio-player/index.html

# 2. SSH to Surface Go
ssh frawo@192.168.2.154

# 3. Start server
cd ~/radio-player
python3 -m http.server 17828

# 4. Update Firefox Kiosk target
# Edit ~/.config/autostart/firefox-kiosk.desktop
# Exec=firefox --kiosk http://localhost:17828
```

### Phase 3: Integration Test
- [ ] Surface Go kann Anker Radio streamen
- [ ] Now-Playing Updates funktionieren
- [ ] Touch-Interaktion smooth
- [ ] Auto-Reload bei Network-Drop
- [ ] Fullscreen ohne Scrollbars

---

## Customization Guide (Für Wolf)

### Station hinzufügen/ändern
Datei: `index_v2.html` (Zeile ~180)
```html
<div class="station" data-station="STATION-ID" data-url="http://SERVER">
  <div class="status-badge"></div>
  <div class="station-icon">🎸</div> <!-- Emoji ändern -->
  <div class="station-name">Mein Radio</div>
  <div class="station-location">📍 Ort</div>
  <div class="nowplaying" id="nowplaying-STATION-ID">Loading...</div>
</div>
```

### Farben ändern
Datei: `index_v2.html` (Zeile ~30-40)
```css
background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); /* Background */
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); /* Accent */
```

### Logo ändern
Datei: `index_v2.html` (Zeile ~175)
```html
<div class="logo">🎵</div> <!-- Emoji oder Bild -->
```

---

## Troubleshooting

### Stream lädt nicht
1. Check Network: `ping radio.hs27.internal`
2. Check API: `curl http://radio.hs27.internal/api/nowplaying`
3. Check Browser Console (F12)
4. CORS-Header prüfen

### Now-Playing nicht aktualisiert
1. Browser Console: JavaScript-Errors?
2. API-Endpoint erreichbar?
3. Station-ID korrekt?

### Touch nicht responsive
1. Viewport-Meta-Tag prüfen
2. Button-Größe erhöhen (min 44x44px)
3. CSS `touch-action` prüfen

---

## Next Steps

1. ✅ V2 Design erstellt
2. 🔴 Stream-URLs für beide Stationen ermitteln
3. 🔴 CORS/Network-Test Anker → Surface Go
4. 🔴 Deployment zu Surface Go
5. 🔴 Stocki Radio nach Storage-Fix integrieren
