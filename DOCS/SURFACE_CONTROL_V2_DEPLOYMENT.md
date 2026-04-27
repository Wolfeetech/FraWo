# Surface Control V2 - Deployment Guide

**Version**: 2.1 Production
**Date**: 2026-04-27
**Status**: Ready for Deployment

## Quick Start

```bash
# Deploy to Surface Go
ansible-playbook ansible/playbooks/deploy_surface_control_v2.yml

# Check deployment
ansible surface_go_frontend -m shell -a "systemctl --user status firefox-kiosk"
```

## Features Deployed

### ✅ Multi-Node Architecture
- **Stockenweiler Server** (192.168.178.210) - Radio Hauptlast
- **Anker Server** (10.1.0.0/24) - Upload/Musik/Dokumente
- **Mobile Funk Pi** (10.3.0.10) - Events/DJ/Backup

### ✅ Intelligent Features
- **Site Auto-Detection**: Erkennt Anker/Stock/Mobil automatisch
- **Smart Failover**: Radio API wählt beste Endpoint
- **Now-Playing Widget**: Live Album Art + Song Details
- **Multi-Source Radio**: Stock (HTTPS/HTTP) → Mobile (Fallback)
- **Production Odoo**: 4 Actions mit Deep-Link Handler

### ✅ Monitoring & Updates
- **Health Checks**: Alle 60s
- **Site Re-Detection**: Alle 5 Minuten
- **Auto-Update**: Alle 6 Stunden via Git Pull
- **Status Display**: `📍 Anker · 2 Knoten`

## Deployment Steps

### 1. Pre-Flight Check

```bash
# Verify Surface Go is reachable
ansible surface_go_frontend -m ping

# Check current configuration
ansible surface_go_frontend -m shell -a "ls -la /home/frontend/homeserver2027-portal"
```

### 2. Deploy

```bash
cd c:\WORKSPACE\FraWo

# Syntax check
ansible-playbook ansible/playbooks/deploy_surface_control_v2.yml --syntax-check

# Dry run
ansible-playbook ansible/playbooks/deploy_surface_control_v2.yml --check

# Deploy
ansible-playbook ansible/playbooks/deploy_surface_control_v2.yml
```

### 3. Verify Deployment

```bash
# Check services on Surface Go
ssh frontend@surface-go

# HTTP Server
systemctl --user status surface-http-server

# Firefox Kiosk
systemctl --user status firefox-kiosk

# Auto-Update Timer
systemctl --user status surface-control-update.timer

# Check logs
journalctl --user -u firefox-kiosk -f
```

### 4. Test Functionality

Open Firefox Kiosk and verify:

**✅ Site Detection:**
- Footer shows: `📍 Anker · 2 Knoten` (if at Anker)
- Console logs site detection results

**✅ Radio Widget:**
- Now-Playing displays song info
- Album art loads
- Status shows: `LIVE · Stock` or `LIVE · Mobile`

**✅ Odoo Actions:**
- Click "Aufgaben" → Deep-link to Taskboard
- Click "Projekte" → Deep-link to Projects
- Click "Kalender" → Deep-link to Calendar
- Click "Odoo Dashboard" → Fallback to login

**✅ Service Links:**
- All Dokumente, System links work
- Radio links open correct endpoints

## Systemd Services

### surface-http-server.service
```ini
[Unit]
Description=Surface Control HTTP Server
After=network-online.target

[Service]
Type=simple
WorkingDirectory=/home/frontend/homeserver2027-portal
ExecStart=/usr/bin/python3 -m http.server 17827 --bind 127.0.0.1
Restart=always
RestartSec=10

[Install]
WantedBy=default.target
```

### firefox-kiosk.service
```ini
[Unit]
Description=Firefox Kiosk Mode - Surface Control
After=surface-http-server.service
Requires=surface-http-server.service

[Service]
Type=simple
Environment=DISPLAY=:0
ExecStartPre=/bin/sleep 3
ExecStart=/usr/bin/firefox --kiosk http://127.0.0.1:17827
Restart=always
RestartSec=10

[Install]
WantedBy=default.target
```

### surface-control-update.timer
```ini
[Unit]
Description=Surface Control Auto-Update Timer

[Timer]
OnBootSec=5min
OnUnitActiveSec=6h
Persistent=true

[Install]
WantedBy=timers.target
```

## Manual Operations

### Force Update
```bash
ssh frontend@surface-go
systemctl --user start surface-control-update.service
```

### Restart Firefox Kiosk
```bash
ssh frontend@surface-go
systemctl --user restart firefox-kiosk
```

### View Logs
```bash
# Firefox logs
journalctl --user -u firefox-kiosk -n 50

# HTTP server logs
journalctl --user -u surface-http-server -n 50

# Update logs
journalctl --user -u surface-control-update -n 20
```

### Manual File Update (Emergency)
```bash
# From StudioPC
scp artifacts/surface_index_v2_with_nowplaying.html \
  frontend@surface-go:/home/frontend/homeserver2027-portal/index.html

# Reload Firefox
ssh frontend@surface-go "systemctl --user restart firefox-kiosk"
```

## Console Debugging

Press `F12` in Firefox Kiosk to open Developer Console:

```javascript
// Check site detection
console.log(currentSite);

// Check node availability
console.log('Nodes:', currentSite.nodes);

// Check active radio endpoint
console.log('Radio API:', activeRadioEndpoint);

// Force re-detection
detectSite().then(console.log);

// Check service health
console.log('Health:', serviceHealth);
```

## Troubleshooting

### Issue: Site shows "Isolated"
**Cause**: None of the probe endpoints reachable
**Fix**:
```bash
# Check network
ping 10.1.0.20        # Anker
ping 192.168.178.210  # Stock

# Check Tailscale
tailscale status
```

### Issue: Radio Widget not showing
**Cause**: API endpoint not reachable or CORS errors
**Fix**:
```bash
# Test API manually
curl -k https://192.168.178.210/api/station/1/nowplaying

# Check browser console for CORS errors
# Radio API will retry with HTTP fallback
```

### Issue: Odoo deep links don't work
**Cause**: Fragment URLs not supported by Odoo version
**Fix**: Links fallback to `/web` automatically, user can navigate manually

### Issue: Auto-update not working
**Cause**: Git repo not configured or credentials missing
**Fix**:
```bash
ssh frontend@surface-go
cd /home/frontend/homeserver2027-portal

# Check git status
git status
git remote -v

# Manual pull
git fetch origin
git reset --hard origin/main
```

## Rollback Procedure

```bash
# Ansible created backup with timestamp
ssh frontend@surface-go
cd /home/frontend/homeserver2027-portal
ls -la index.html*

# Restore previous version
cp index.html.2026-04-27@15:30:42~ index.html

# Restart Firefox
systemctl --user restart firefox-kiosk
```

## Performance Metrics

**Load Time**: < 500ms (local network)
**Site Detection**: ~2-4s (parallel probes)
**Radio API Update**: 15s interval
**Service Health Check**: 60s interval
**Site Re-Detection**: 5 minutes
**Memory Usage**: ~15-20MB (Firefox)

## Security Notes

- HTTP Server binds to localhost only (127.0.0.1)
- No external network exposure
- Service links use internal DNS (hs27.internal)
- No secrets in HTML/JavaScript
- Auto-update pulls from trusted Git repo only

## Next Steps After Deployment

1. **Monitor initial 24h**:
   ```bash
   journalctl --user -u firefox-kiosk -f
   ```

2. **Test all three site locations**:
   - @ Anker: Should detect `anker`
   - @ Stockenweiler: Should detect `stockenweiler`
   - Via Tailscale only: Should detect available nodes

3. **Verify auto-update** (after 6h):
   ```bash
   journalctl --user -u surface-control-update
   ```

4. **Test failover scenarios**:
   - Disconnect from Anker network → Should detect Stock
   - Stop Stock radio → Should show widget hide after 3 failures

## Architecture Summary

```
┌─────────────────────────────────────────┐
│  Surface Go Frontend (mobil)            │
│  - Firefox Kiosk (Port 17827)           │
│  - Site Auto-Detection                  │
│  - Multi-Node Routing                   │
└─────────────────────────────────────────┘
                │
    ┌───────────┼───────────┐
    ▼           ▼           ▼
┌─────────┐ ┌─────────┐ ┌─────────┐
│ Anker   │ │ Stock   │ │ Mobile  │
│ Server  │ │ Server  │ │ Funk Pi │
│10.1.0.x │ │192.178.x│ │10.3.0.x │
└─────────┘ └─────────┘ └─────────┘
 Upload/     Hauptlast   Events/
 Dokumente   Radio       DJ
```

## Support

**Documentation**:
- Architecture: `DOCS/SURFACE_CONTROL_ARCHITECTURE_CORRECTED.md`
- Production Guide: `DOCS/SURFACE_CONTROL_V2_PRODUCTION.md`
- Deployment Strategy: `DOCS/SURFACE_CONTROL_DEPLOYMENT_STRATEGY.md`

**Playbook**: `ansible/playbooks/deploy_surface_control_v2.yml`
**Source**: `artifacts/surface_index_v2_with_nowplaying.html`

**Contact**: Wolf Admin <wolf@frawo-tech.de>
