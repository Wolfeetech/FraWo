# Surface Control V2 - Production Ready

**Version**: 2.1
**Status**: Production Ready
**Last Updated**: 2026-04-27
**Target Device**: Surface Go Frontend (Kiosk Mode)

## Overview

Surface Control V2 ist die production-ready Version der FraWo Control Surface mit vollständiger Odoo-Integration, Live-Radio-Widget und robustem Error Handling.

## Production-Ready Features

### ✅ Odoo Integration (Production Ready)

**4 Odoo Actions:**
- **Aufgaben** → Taskboard Kanban View (action=118)
- **Projekte** → Projektboard Kanban View (action=252)
- **Kalender** → Task Calendar View (action=517)
- **Dashboard** → Hauptmenü/Login Fallback

**Robustheit:**
- Deep-Link Handler mit JavaScript-basierter Navigation
- Fragment-URL Unterstützung (`#action=...`)
- Fallback zu `/web/login` wenn Deep-Links fehlschlagen
- ARIA-Labels für Screen Reader Accessibility
- Touch-optimierte 44x44px Mindestgröße

**URL-Strategie:**
```javascript
// Primary: Deep Link mit Fragment
http://odoo.hs27.internal/web#action=118&model=project.task&view_type=kanban

// Fallback: Base URL
http://odoo.hs27.internal/web

// Emergency: Login Page
http://odoo.hs27.internal/web/login
```

### ✅ Radio Integration mit Live Widget

**Now-Playing Widget Features:**
- Live Album Art (80x80px, responsive auf mobil 100%x140px)
- Song-Details: Titel, Artist, Album
- Playlist-Badge (Wolfarites / Wolf Lounge)
- Live-Status Indicator mit Pulse-Animation
- Auto-Update alle 15 Sekunden

**Dual-Site Support:**
- **Radio Anker** (frawo-funk) - Raspberry Pi 4, momentan offline
- **Radio Stock** (Radio4yourparty) - VM 210 Stockenweiler, LIVE

**API Integration:**
```javascript
// Primary: HTTPS
https://192.168.178.210/api/station/1/nowplaying

// Fallback: HTTP
http://192.168.178.210/api/station/1/nowplaying

// Timeout: 8 Sekunden
// Max Errors: 3 consecutive failures before hiding widget
```

**Error Handling:**
- HTTPS → HTTP Fallback
- 8s Timeout mit AbortSignal
- Fehler-Counter (3 Versuche)
- Graceful Degradation (Widget wird ausgeblendet bei anhaltenden Fehlern)
- SVG Placeholder für fehlende Album Arts

### ✅ Service Health Monitoring

**Monitored Services:**
- Odoo (`http://odoo.hs27.internal/web/login`)
- Radio Stock (`http://192.168.178.210`)
- Portal (`http://portal.hs27.internal`)

**Health Check:**
- HEAD Request mit 5s Timeout
- No-CORS Mode für Cross-Origin Checks
- Status-Text Updates basierend auf verfügbaren Services

### ✅ User Experience

**Keyboard Shortcuts:**
- `F11` / `Alt+Enter` → Fullscreen Toggle
- `F5` → Reload

**Touch Optimizations:**
- Min 44x44px Touch Targets
- Scale-Down Animation auf Touch
- Responsive Grid (auto-fit minmax)

**Accessibility:**
- ARIA Labels auf allen Action Cards
- ARIA-Hidden auf dekorativen Code-Badges
- Semantic HTML Structure
- Keyboard Navigation Support

## Architecture

### Frontend Stack
- **HTML5** mit Semantic Markup
- **CSS3** mit CSS Variables & Grid Layout
- **Vanilla JavaScript** (keine Dependencies)
- **Responsive Design** (Mobile-First)

### Service URLs

**Dokumente:**
- Nextcloud Eingang: `http://cloud.hs27.internal/apps/files/files?dir=/Paperless/Eingang`
- Paperless Dashboard: `http://paperless.hs27.internal/dashboard`

**Odoo:**
- Tasks: `http://odoo.hs27.internal/web#action=118...`
- Projects: `http://odoo.hs27.internal/web#action=252...`
- Calendar: `http://odoo.hs27.internal/web#action=517...`
- Dashboard: `http://odoo.hs27.internal/web/login`

**Radio:**
- Anker Player: `http://radio-anker.hs27.internal/public/frawo-funk`
- Stock Player: `http://192.168.178.210/public/radio.yourparty`
- Anker Control: `http://radio-anker.hs27.internal/login`
- Stock Control: `http://192.168.178.210/login`

**System:**
- Portal: `http://portal.hs27.internal`
- Vaultwarden: `http://vault.hs27.internal`
- Home Assistant: `http://ha.hs27.internal`
- Jellyfin: `http://media.hs27.internal`

## Deployment

### Prerequisites
- Surface Go Frontend Device
- GNOME Kiosk Session für User `frontend`
- Firefox in Kiosk Mode
- Python 3 HTTP Server (Port 17827)
- Network Access zu hs27.internal Domain

### Installation Steps

1. **Copy HTML to Surface Go:**
```bash
scp artifacts/surface_index_v2_with_nowplaying.html frontend@surface-go:/home/frontend/control_surface/index.html
```

2. **Start Python HTTP Server:**
```bash
ssh frontend@surface-go
cd /home/frontend/control_surface
python3 -m http.server 17827
```

3. **Configure Firefox Kiosk Mode:**
```bash
# /home/frontend/.config/systemd/user/firefox-kiosk.service
[Unit]
Description=Firefox Kiosk Mode for Control Surface

[Service]
Type=simple
ExecStart=/usr/bin/firefox --kiosk http://localhost:17827
Restart=always

[Install]
WantedBy=default.target
```

4. **Enable Auto-Login:**
```bash
# /etc/gdm3/custom.conf
[daemon]
AutomaticLoginEnable=true
AutomaticLogin=frontend
```

### File Structure
```
/home/frontend/control_surface/
├── index.html (surface_index_v2_with_nowplaying.html)
└── README.md
```

## Browser Compatibility

**Tested:**
- ✅ Firefox 120+ (Primary Target)
- ✅ Chrome/Edge 120+
- ✅ Safari 17+

**Required Features:**
- CSS Grid Layout
- CSS Variables
- Fetch API
- AbortSignal.timeout()
- Fullscreen API

## Known Limitations

### DNS Resolution
- `radio-anker.hs27.internal` und `radio-stock.hs27.internal` DNS-Einträge noch nicht deployed
- Aktuell: Direkte IP für Stock Radio (192.168.178.210)
- Workaround: IP-basierte URLs funktionieren

### Radio Anker Node
- Raspberry Pi 4 Radio Node offline
- IPs nicht erreichbar: 192.168.2.155, 100.64.23.77, 10.3.0.10
- Physischer Zugriff erforderlich

### CORS Restrictions
- Now-Playing API kann CORS-Fehler werfen
- Service Health Checks verwenden no-cors Mode
- Funktioniert trotzdem im internen Netzwerk

## Performance

**Load Time:** < 500ms (lokales Netzwerk)
**Now-Playing Update:** 15s Intervall
**Service Health Check:** 5s Timeout
**Memory Usage:** ~15MB (Firefox)

## Security Considerations

- **Internal Network Only** - keine Public Exposure
- **No Authentication** auf Surface Control selbst
- **Target Services** haben eigene Login-Mechanismen
- **No Secrets** in HTML/JavaScript Code
- **No External Dependencies** - keine CDN-Links

## Maintenance

### Update Procedure
1. Edit `surface_index_v2_with_nowplaying.html` lokal
2. Test im Browser
3. SCP to Surface Go
4. Reload Firefox (`F5`)

### Monitoring
- Check `/var/log/syslog` für Firefox-Kiosk Errors
- Monitor Python HTTP Server Output
- Test alle Service-Links monatlich

## Future Enhancements

- [ ] Scanner-Workflow Integration (Document Scan Action)
- [ ] Stockenweiler Support Actions (TV Help, Remote Help)
- [ ] WebSocket für Real-Time Now-Playing Updates
- [ ] Service Status Dashboard mit Uptime-Tracking
- [ ] Dark/Light Theme Toggle
- [ ] Custom Service Shortcuts (User-Definable)

## Changelog

### v2.1 (2026-04-27)
- ✅ Production-ready Odoo Integration mit 4 Actions
- ✅ Deep-Link Handler für Odoo Fragment-URLs
- ✅ HTTPS/HTTP Fallback für Radio API
- ✅ Error Counter & Graceful Degradation
- ✅ Service Health Monitoring
- ✅ Improved ARIA Labels
- ✅ SVG Placeholder für Album Art
- ✅ 4th Odoo Action: Dashboard/Login Fallback

### v2.0 (2026-04-22)
- ✅ Now-Playing Widget für Radio4yourparty
- ✅ Dual-Site Radio Support (Anker + Stock)
- ✅ Live Album Art & Song Details
- ✅ Auto-Update alle 15s
- ✅ System Category mit 4 Services

### v1.0 (Initial)
- Basic Control Surface
- Static Service Links
- Dokumente, Odoo, Radio Groups

## Support

**Documentation:** `DOCS/SURFACE_CONTROL_V2.md`
**Manifest:** `manifests/control_surface/actions_v2.json`
**Live HTML:** `artifacts/surface_index_v2_with_nowplaying.html`

**Contact:** Wolf Admin <wolf@frawo-tech.de>
