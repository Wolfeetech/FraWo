# 🚀 DEPLOY SURFACE CONTROL V2 NOW!

**Status**: Git pushed ✅ | Ready for deployment ⏳

## Quick Deploy Commands (Copy & Paste)

### Step 1: Verify Surface Go is online

```bash
ping 192.168.2.154
```

**Expected**: `Reply from 192.168.2.154`

---

### Step 2: Deploy HTML (Manual Method)

```bash
# Copy HTML to Surface Go
scp c:/WORKSPACE/FraWo/artifacts/surface_index_v2_with_nowplaying.html frontend@192.168.2.154:/home/frontend/homeserver2027-portal/index.html
```

**Password**: `[Surface Go frontend user password]`

---

### Step 3: Create systemd services

```bash
# SSH into Surface Go
ssh frontend@192.168.2.154

# Create systemd user directory
mkdir -p ~/.config/systemd/user

# Create HTTP Server service
cat > ~/.config/systemd/user/surface-http-server.service << 'EOF'
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
EOF

# Create Firefox Kiosk service
cat > ~/.config/systemd/user/firefox-kiosk.service << 'EOF'
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
EOF

# Create Auto-Update Timer
cat > ~/.config/systemd/user/surface-control-update.timer << 'EOF'
[Unit]
Description=Surface Control Auto-Update Timer

[Timer]
OnBootSec=5min
OnUnitActiveSec=6h
Persistent=true

[Install]
WantedBy=timers.target
EOF

# Create Auto-Update Service
cat > ~/.config/systemd/user/surface-control-update.service << 'EOF'
[Unit]
Description=Surface Control Auto-Update from Git
After=network-online.target

[Service]
Type=oneshot
WorkingDirectory=/home/frontend/homeserver2027-portal
ExecStart=/usr/bin/git fetch origin
ExecStart=/usr/bin/git reset --hard origin/main

[Install]
WantedBy=default.target
EOF

# Reload systemd
systemctl --user daemon-reload

# Enable and start services
systemctl --user enable surface-http-server
systemctl --user enable firefox-kiosk
systemctl --user enable surface-control-update.timer

systemctl --user start surface-http-server
systemctl --user start firefox-kiosk
systemctl --user start surface-control-update.timer
```

---

### Step 4: Verify Deployment

```bash
# Still on Surface Go via SSH

# Check HTTP Server
systemctl --user status surface-http-server

# Check Firefox Kiosk
systemctl --user status firefox-kiosk

# Check Auto-Update Timer
systemctl --user status surface-control-update.timer

# View Firefox logs
journalctl --user -u firefox-kiosk -n 50
```

**Expected Output**:
- HTTP Server: `Active: active (running)`
- Firefox Kiosk: `Active: active (running)`
- Update Timer: `Active: active (waiting)`

---

### Step 5: Test on Surface Go

**Physical Access Required**

1. **Check Firefox Kiosk is running**
   - Should see Surface Control V2 in fullscreen
   - Footer shows: `📍 Anker · 2 Knoten` (or similar)

2. **Open Developer Console** (if accessible)
   - Press `F12`
   - Check Console for:
     ```
     🚀 Surface Control V2 initializing...
     📦 Multi-Node Architecture: Anker + Stock + Mobile
     🔍 Detecting current site...
     📍 Site detected: anker
     ✅ Surface Control V2 ready
     ```

3. **Test Features**:
   - ✅ Radio Widget shows Now-Playing
   - ✅ Click "Aufgaben" → Odoo Taskboard öffnet
   - ✅ Click "Radio4yourparty" → Player öffnet
   - ✅ All service links work

---

## Alternative: Git Clone Method (If not already done)

```bash
# On Surface Go
ssh frontend@192.168.2.154

# Clone repo (if not exists)
cd /home/frontend
git clone https://github.com/Wolfeetech/FraWo.git homeserver2027-portal

# OR if exists, update
cd /home/frontend/homeserver2027-portal
git pull origin main

# Create symlink to HTML
ln -sf artifacts/surface_index_v2_with_nowplaying.html index.html

# Then continue with Step 3 above (systemd services)
```

---

## Troubleshooting

### Surface Go not reachable at 192.168.2.154

**Try alternative IPs**:
```bash
# Check ansible inventory
cat ansible/inventory/hosts.yml | grep surface

# Try Tailscale IP (if configured)
ping [tailscale-ip]
```

### Services fail to start

```bash
# Check logs
journalctl --user -u surface-http-server -n 50
journalctl --user -u firefox-kiosk -n 50

# Check if port 17827 is already in use
ss -tulpn | grep 17827

# Check if Firefox is installed
which firefox
```

### Auto-Update not working

```bash
# Verify Git is configured
cd /home/frontend/homeserver2027-portal
git status
git remote -v

# Test manual update
systemctl --user start surface-control-update.service

# Check logs
journalctl --user -u surface-control-update -n 20
```

---

## Success Checklist

- [ ] Surface Go pingable at 192.168.2.154
- [ ] HTML copied to `/home/frontend/homeserver2027-portal/index.html`
- [ ] HTTP Server running: `systemctl --user is-active surface-http-server` → `active`
- [ ] Firefox Kiosk running: `systemctl --user is-active firefox-kiosk` → `active`
- [ ] Auto-Update Timer active: `systemctl --user is-active surface-control-update.timer` → `active`
- [ ] Surface Control V2 visible in Firefox Kiosk
- [ ] Site Detection works (footer shows location)
- [ ] Radio Widget displays Now-Playing
- [ ] Odoo links work
- [ ] All service links functional

---

## Quick Commands Summary

```bash
# Deploy HTML
scp artifacts/surface_index_v2_with_nowplaying.html frontend@192.168.2.154:/home/frontend/homeserver2027-portal/index.html

# Restart services
ssh frontend@192.168.2.154 "systemctl --user restart firefox-kiosk"

# View logs
ssh frontend@192.168.2.154 "journalctl --user -u firefox-kiosk -f"

# Check status
ssh frontend@192.168.2.154 "systemctl --user status firefox-kiosk surface-http-server surface-control-update.timer"
```

---

## 🎉 When Deployment is Complete

You should see:

**On Surface Go Display**:
- Surface Control V2 in fullscreen Firefox Kiosk
- `📍 Anker · 2 Knoten` in footer
- Now-Playing Widget showing current song from Radio Stock
- All service cards clickable and working

**Console (F12)**:
```
🚀 Surface Control V2 initializing...
📦 Multi-Node Architecture: Anker + Stock + Mobile
🔍 Detecting current site...
📍 Site detected: anker
🔗 Node availability: { anker: true, stock: true, mobile: false }
✅ Radio API endpoint: https://192.168.178.210/api/station/1/nowplaying
✅ Surface Control V2 ready
🎯 Active location: anker
🔗 Available nodes: anker, stock
```

**Features Working**:
- ✅ Multi-Node Architecture
- ✅ Site Auto-Detection
- ✅ Intelligent Radio Failover
- ✅ Now-Playing Widget (LIVE · Stock)
- ✅ Production Odoo Integration
- ✅ Service Health Monitoring
- ✅ Auto-Update (every 6h)

---

## Files Deployed

- **HTML**: `surface_index_v2_with_nowplaying.html` → `/home/frontend/homeserver2027-portal/index.html`
- **Services**: 4 systemd user services/timers
- **Git**: Optional auto-update from `main` branch

## Git Commits

- `ce90929` - Surface Control V2 (HTML + Docs + Ansible)
- `546587c` - Deployment Scripts

**Status**: ✅ Pushed to GitHub

---

**READY TO DEPLOY!** 🚀

Just need Surface Go to be online at 192.168.2.154!
