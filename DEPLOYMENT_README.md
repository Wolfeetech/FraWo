# Surface Control V2 - Quick Deployment

## 🚀 Schnellstart

### Option 1: Automatisches Deployment (Ansible)

```bash
# In WSL/Linux Terminal
cd /mnt/c/WORKSPACE/FraWo

# Syntax Check
./scripts/deploy_surface_control_v2.sh --syntax

# Dry Run (check was passieren würde)
./scripts/deploy_surface_control_v2.sh --check

# Deploy!
./scripts/deploy_surface_control_v2.sh --deploy
```

### Option 2: Manuelles Deployment (SSH)

```bash
# 1. HTML kopieren
scp artifacts/surface_index_v2_with_nowplaying.html \
  frontend@192.168.2.154:/home/frontend/homeserver2027-portal/index.html

# 2. SSH zum Surface Go
ssh frontend@192.168.2.154

# 3. Services neu starten
systemctl --user restart surface-http-server
systemctl --user restart firefox-kiosk

# 4. Logs checken
journalctl --user -u firefox-kiosk -f
```

## 📋 Pre-Flight Checklist

- [ ] Surface Go ist online: `ping 192.168.2.154`
- [ ] SSH funktioniert: `ssh frontend@192.168.2.154`
- [ ] Git Commit ist gepushed (optional für Auto-Update)
- [ ] Backup der alten Version (Ansible macht automatisch)

## 🔍 Nach dem Deployment

### Verify Services

```bash
ssh frontend@surface-go

# Check HTTP Server
systemctl --user status surface-http-server

# Check Firefox Kiosk
systemctl --user status firefox-kiosk

# Check Auto-Update Timer
systemctl --user status surface-control-update.timer
systemctl --user list-timers
```

### Test Functionality

**Öffne Firefox Kiosk und prüfe:**

1. **Site Detection** (F12 Console):
   - `currentSite.location` sollte `anker` sein (wenn @ Anker)
   - Footer zeigt: `📍 Anker · 2 Knoten`

2. **Radio Widget**:
   - Now-Playing zeigt Song-Info
   - Album Art lädt
   - Status: `LIVE · Stock`

3. **Odoo Links**:
   - Click "Aufgaben" → Taskboard öffnet
   - Click "Projekte" → Projektboard öffnet
   - Click "Kalender" → Calendar öffnet

4. **Service Links**:
   - Nextcloud, Paperless, Portal funktionieren
   - Radio Player links öffnen

## 🛠️ Troubleshooting

### Firefox Kiosk startet nicht

```bash
# Logs anschauen
journalctl --user -u firefox-kiosk -n 50

# HTTP Server läuft?
systemctl --user status surface-http-server

# Manuell starten
systemctl --user start firefox-kiosk
```

### Site zeigt "Isoliert"

```bash
# Netzwerk prüfen
ping 10.1.0.20         # Anker Toolbox
ping 192.168.178.210   # Stock Radio

# Tailscale aktiv?
tailscale status
```

### Radio Widget nicht sichtbar

```bash
# API manuell testen
curl -k https://192.168.178.210/api/station/1/nowplaying

# Browser Console öffnen (F12)
# Schaue nach CORS oder Network Errors
```

## 📊 Monitoring

### Live Logs

```bash
# Firefox Kiosk
journalctl --user -u firefox-kiosk -f

# HTTP Server
journalctl --user -u surface-http-server -f

# Alle User Services
journalctl --user -f
```

### Status Check

```bash
# Alle Services auf einen Blick
systemctl --user list-units | grep surface
systemctl --user list-units | grep firefox
```

### Performance

```bash
# Memory Usage
ps aux | grep firefox

# Network Connections
ss -tulpn | grep 17827
```

## 🔄 Updates

### Auto-Update (alle 6h)

```bash
# Timer Status
systemctl --user status surface-control-update.timer

# Nächster Run
systemctl --user list-timers | grep surface

# Manuell triggern
systemctl --user start surface-control-update.service
```

### Manual Update

```bash
# Von StudioPC aus
cd /mnt/c/WORKSPACE/FraWo
git pull
./scripts/deploy_surface_control_v2.sh --deploy

# Oder nur HTML kopieren
scp artifacts/surface_index_v2_with_nowplaying.html \
  frontend@surface-go:/home/frontend/homeserver2027-portal/index.html
ssh frontend@surface-go "systemctl --user restart firefox-kiosk"
```

## 🎯 Features im Einsatz

### Console Commands (F12)

```javascript
// Site Info
console.log(currentSite)

// Verfügbare Nodes
console.log(currentSite.nodes)

// Aktiver Radio Endpoint
console.log(activeRadioEndpoint)

// Service Health
console.log(serviceHealth)

// Force Re-Detection
detectSite().then(console.log)

// Check Services
checkServices()
```

### Keyboard Shortcuts

- **F11** oder **Alt+Enter**: Fullscreen Toggle
- **F5**: Reload Page
- **F12**: Developer Console

## 📚 Dokumentation

- **Architecture**: `DOCS/SURFACE_CONTROL_ARCHITECTURE_CORRECTED.md`
- **Production Guide**: `DOCS/SURFACE_CONTROL_V2_PRODUCTION.md`
- **Deployment Guide**: `DOCS/SURFACE_CONTROL_V2_DEPLOYMENT.md`
- **Strategy**: `DOCS/SURFACE_CONTROL_DEPLOYMENT_STRATEGY.md`

## 🆘 Emergency Rollback

```bash
ssh frontend@surface-go
cd /home/frontend/homeserver2027-portal

# Ansible hat Backup erstellt
ls -la index.html*

# Restore previous version
cp index.html.TIMESTAMP~ index.html

# Restart
systemctl --user restart firefox-kiosk
```

## 🎉 Success Indicators

Deployment ist erfolgreich wenn:

- ✅ Firefox Kiosk läuft: `systemctl --user is-active firefox-kiosk` → `active`
- ✅ HTTP Server läuft: `systemctl --user is-active surface-http-server` → `active`
- ✅ Auto-Update Timer aktiv: `systemctl --user is-active surface-control-update.timer` → `active`
- ✅ Site Detection zeigt korrekte Location im Footer
- ✅ Radio Widget zeigt Now-Playing
- ✅ Alle Service-Links funktionieren

## 📞 Support

**Git Commit**: ce90929
**Playbook**: `ansible/playbooks/deploy_surface_control_v2.yml`
**HTML**: `artifacts/surface_index_v2_with_nowplaying.html`

Bei Problemen: Logs checken und Troubleshooting-Section oben durchgehen!
