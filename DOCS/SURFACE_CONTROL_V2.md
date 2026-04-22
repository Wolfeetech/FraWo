# Surface Control V2 - Enhanced Frontend

Stand: `2026-04-22`

## Zweck

**Surface Control** ist das zentrale Touch-optimierte Frontend für den Surface Go, das direkten Zugriff auf alle produktiven FraWo-Services bietet.

## Was ist neu in V2

### ✨ Neue Features

1. **System-Kategorie hinzugefügt**
   - Portal (Homeserver-Portal)
   - Vaultwarden (Passwort-Manager)
   - Home Assistant (Smart Home)
   - Jellyfin (Media Center)

2. **Verbesserte UI/UX**
   - Touch-optimierte Action Cards mit Hover-Effekten
   - Status-Badge mit Live-Indikator
   - Vollbild-Funktion (F11 oder Alt+Enter)
   - Keyboard Shortcuts (F5 für Reload)
   - Touch-Feedback Animationen

3. **Enhanced Manifest**
   - Erweiterte Actions mit Prioritäten
   - Gruppendefinitionen mit Metadata
   - Service-Status Tracking
   - Shortcodes für schnelle Referenz

4. **Bessere Accessibility**
   - ARIA-Labels für Screen Reader
   - Touch-freundliche Target-Größen (min 44x44px)
   - Keyboard-Navigation Support
   - Responsive Grid-Layout

### 🎨 Design-Verbesserungen

- **Moderneres Glassmorphism-Design**
- **Animierte Status-Badges**
- **Verbesserte Action-Card Interaktionen**
- **Touch-optimierte Spacing**
- **Direct vs. Login Meta-Tags** (farbcodiert)

## Architektur

```
┌─────────────────────────────────────────────────┐
│  Surface Go Frontend (Ubuntu + GNOME Kiosk)     │
├─────────────────────────────────────────────────┤
│  Firefox Kiosk Mode                             │
│  http://127.0.0.1:17827                        │
├─────────────────────────────────────────────────┤
│  homeserver2027-surface-portal.service          │
│  Python HTTP Server                             │
│  Serving: /home/frontend/homeserver2027-portal │
├─────────────────────────────────────────────────┤
│  surface_index_v2.html (Static HTML)            │
│  ├─ Inline CSS (Touch-optimized)               │
│  ├─ Inline JS (Clock, Fullscreen, Shortcuts)   │
│  └─ Actions from manifests/control_surface/    │
└─────────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────┐
│  Internal Services (via hs27.internal)          │
├─────────────────────────────────────────────────┤
│  ✓ Nextcloud (cloud.hs27.internal)             │
│  ✓ Paperless (paperless.hs27.internal)         │
│  ✓ Odoo (odoo.hs27.internal)                   │
│  ✓ Radio (radio.hs27.internal)                 │
│  ✓ Portal (portal.hs27.internal)               │
│  ✓ Vaultwarden (vault.hs27.internal)           │
│  ✓ Home Assistant (ha.hs27.internal)           │
│  ✓ Jellyfin (media.hs27.internal)              │
└─────────────────────────────────────────────────┘
```

## Actions Manifest V2

### Schema

```json
{
  "version": 2,
  "render_ready_only": true,
  "actions": [
    {
      "id": "unique_id",
      "label": "Display Name",
      "note": "Short description",
      "group": "Category",
      "code": "XX",
      "target_url": "http://service.hs27.internal/path",
      "requires_login": true|false,
      "status": "ready|backlog",
      "verified": true|false,
      "priority": 10
    }
  ],
  "groups": [
    {
      "id": "group_id",
      "name": "Group Name",
      "eyebrow": "Section Label",
      "description": "Group description",
      "priority": 10
    }
  ]
}
```

### Verfügbare Groups

| Group | Eyebrow | Description | Priority |
|-------|---------|-------------|----------|
| `Dokumente` | Dokumente | Eingang und Archiv | 10 |
| `Odoo` | Aufgaben & Projekte | Odoo Projektmanagement | 20 |
| `Radio` | Audio | Radio Player und Control | 30 |
| `System` | System | Zentrale Services | 40 |
| `Stockenweiler` | Stockenweiler Support | Support-Funktionen | 900 |

### Action Codes

| Code | Service | Type |
|------|---------|------|
| `NC` | Nextcloud | Dokumente |
| `PL` | Paperless | Dokumente |
| `OD` | Odoo | Aufgaben |
| `RA` | Radio | Player |
| `RC` | Radio Control | Admin |
| `HP` | Portal | System |
| `VW` | Vaultwarden | System |
| `HA` | Home Assistant | System |
| `JF` | Jellyfin | System |

## Deployment

### Ansible Playbook

```bash
cd /path/to/FraWo
ansible-playbook ansible/playbooks/bootstrap_surface_go_frontend.yml
```

### Manuelle Installation (V2)

1. **Kopiere V2 HTML**
   ```bash
   scp artifacts/surface_index_v2.html frawo@surface-go-frontend:/home/frontend/homeserver2027-portal/index.html
   ```

2. **Restart Portal Service**
   ```bash
   ssh frawo@surface-go-frontend
   sudo systemctl restart homeserver2027-surface-portal.service
   ```

3. **Verifiziere**
   ```bash
   curl http://127.0.0.1:17827
   ```

### Service Status

```bash
# Check portal service
systemctl status homeserver2027-surface-portal.service

# Check Firefox kiosk
ps aux | grep firefox

# Check auto-login
cat /etc/gdm3/custom.conf
```

## Konfiguration

### Host Variables

Siehe: `ansible/inventory/host_vars/surface_go_frontend.yml`

**Wichtige Variablen**:
- `surface_go_portal_http_port`: `17827`
- `surface_go_portal_bind_address`: `127.0.0.1`
- `surface_go_kiosk_start_url`: `http://127.0.0.1:17827`
- `surface_go_browser_binary`: `/usr/bin/firefox`
- `surface_go_kiosk_user`: `frontend`
- `surface_go_admin_user`: `frawo`

### Touch Optimizations

**Text Scaling**: `1.25`
**Idle Delay**: `0` (never sleep)
**Screen Keyboard**: Enabled
**Accessibility**: Enabled

### Desktop Launchers

**Kiosk User** (`frontend`):
- FRAWO Control (auto-launch in kiosk mode)
- Bildschirmtastatur

**Admin User** (`frawo`):
- FRAWO Control
- Bildschirmtastatur
- Radio Control
- AnyDesk
- StudioPC Remote

## Features

### Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `F11` | Toggle Fullscreen |
| `Alt+Enter` | Toggle Fullscreen |
| `F5` | Reload Page |

### Touch Gestures

- **Tap**: Navigate to service
- **Long Press**: Show browser context menu (if enabled)
- **Swipe**: Browser navigation (if enabled)

### Accessibility

- ARIA labels für alle interaktiven Elemente
- Keyboard-Navigation mit Tab
- Touch-Target min 44x44px (WCAG 2.1 AAA)
- High-Contrast Mode Support

## Verifikation

### V2 Features Checklist

- [ ] System-Kategorie mit 4 Services sichtbar
- [ ] Status-Badge zeigt "Live" mit Puls-Animation
- [ ] Vollbild-Funktion funktioniert (F11)
- [ ] Touch-Feedback bei Tap auf Action Cards
- [ ] Footer-Status zeigt "Surface Go Frontend" als aktiv
- [ ] "Neu laden" Button funktioniert
- [ ] Alle Services erreichbar (kein 404)
- [ ] Touch-Keyboard funktioniert
- [ ] Auto-Login als `frontend` user
- [ ] Firefox Kiosk-Mode startet automatisch

### Service Endpoints Test

```bash
# Test all endpoints
for url in \
  "http://cloud.hs27.internal" \
  "http://paperless.hs27.internal" \
  "http://odoo.hs27.internal" \
  "http://radio.hs27.internal" \
  "http://portal.hs27.internal" \
  "http://vault.hs27.internal" \
  "http://ha.hs27.internal" \
  "http://media.hs27.internal"; do
  echo "Testing: $url"
  curl -I "$url" 2>/dev/null | head -1
done
```

## Troubleshooting

### Problem: Portal Service nicht erreichbar

**Lösung**:
```bash
sudo systemctl status homeserver2027-surface-portal.service
sudo systemctl restart homeserver2027-surface-portal.service
sudo journalctl -u homeserver2027-surface-portal.service -f
```

### Problem: Firefox Kiosk startet nicht

**Lösung**:
```bash
# Check kiosk script
cat /home/frontend/.config/gnome-kiosk-script/kiosk-script

# Check launcher
cat /usr/local/bin/homeserver2027-frawo-control

# Test manually
sudo -u frontend /usr/local/bin/homeserver2027-frawo-control --kiosk
```

### Problem: Services nicht erreichbar (hs27.internal)

**Lösung**:
```bash
# Check DNS
nslookup odoo.hs27.internal

# Check Tailscale
sudo tailscale status

# Check /etc/hosts
cat /etc/hosts | grep hs27
```

### Problem: Touch-Keyboard erscheint nicht

**Lösung**:
```bash
# Check dconf settings
dconf dump /org/gnome/desktop/a11y/applications/

# Launch manually
/usr/local/bin/homeserver2027-touch-keyboard
```

## Nächste Schritte (Backlog)

1. **Scan-Workflow implementieren**
   - Integration mit Scanner-Gerät
   - Direct-Upload zu Nextcloud Eingang
   - Status-Feedback

2. **Stockenweiler Support-Funktionen**
   - TV/Magenta Remote-Support
   - Fernhilfe-Workflow
   - Vater Home Assistant Zugang

3. **Service Health Checks**
   - Real-time Status Monitoring
   - Auto-refresh bei Failures
   - Notification System

4. **Dark/Light Mode Toggle**
   - User Preference Persistence
   - Auto-Switch basierend auf Tageszeit

## Related Files

- **HTML**: `artifacts/surface_index_v2.html`
- **Manifest**: `manifests/control_surface/actions_v2.json`
- **Playbook**: `ansible/playbooks/bootstrap_surface_go_frontend.yml`
- **Host Vars**: `ansible/inventory/host_vars/surface_go_frontend.yml`
- **Templates**: `ansible/templates/frontend/`

## GitHub Issues

- Related: Surface Go Frontend Setup
- Related: Kiosk Mode Implementation

## Changelog

### V2 (2026-04-22)
- Added System category with 4 services
- Enhanced UI with animations and touch feedback
- Added fullscreen mode and keyboard shortcuts
- Improved accessibility and touch optimizations
- Extended actions manifest with priorities

### V1 (Initial)
- Basic 3-column layout
- Dokumente, Odoo, Radio categories
- Static HTML with simple clock
- Basic touch support

---

Stand: 2026-04-22
Autor: Claude Sonnet 4.5 + Wolf
Status: Ready for Deployment
