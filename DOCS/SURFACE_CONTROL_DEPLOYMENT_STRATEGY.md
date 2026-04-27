# Surface Control Deployment Strategy - Best Practice

**Last Updated**: 2026-04-27
**Status**: Architecture Analysis & Recommendation

## Reality Check: Was ist der Plan?

### Aktuelles Setup (Verstanden)

**1. Surface Go Frontend** (192.168.2.154)
- **Funktion**: Shared Kiosk-Style Frontend Node
- **Standort**: Anker (primär)
- **Zweck**: Mobile/Stationäre Touch-Control-Station
- **Zielgruppe**: Wolf + Franz

**2. Stockenweiler Site**
- **VM 210**: AzuraCast Radio (192.168.178.210) - LIVE
- **VM 360**: Home Assistant Eltern

**3. Radio Nodes**
- **Radio Anker**: Raspberry Pi 4 (10.3.0.10, 192.168.2.155, Tailscale 100.64.23.77) - OFFLINE
- **Radio Stock**: VM 210 Stockenweiler (192.168.178.210) - LIVE

## Die Frage: Eine Instanz, mehrere Zugriffspunkte?

### ✅ RICHTIG VERSTANDEN - Best Practice Konzept:

**Sie wollen EINEN zentralen Control Surface Code**, der von **mehreren physischen Devices** aus erreichbar ist:

1. **Surface Go @ Anker** (mobil/stationär)
2. **Potentiell: Surface Go @ Stockenweiler** (zukünftig?)
3. **Potentiell: Radio Node als Kiosk** (wenn Raspberry Pi wieder online)

### 🎯 Best Practice: "Single Source, Multiple Endpoints"

```
┌─────────────────────────────────────────────────┐
│  Git Repo: artifacts/surface_index_v2.html      │
│  (Single Source of Truth)                       │
└─────────────────────────────────────────────────┘
                     │
         ┌───────────┼───────────┐
         ▼           ▼           ▼
    ┌────────┐  ┌────────┐  ┌────────┐
    │Surface │  │Surface │  │Radio   │
    │Go      │  │Go      │  │Node    │
    │Anker   │  │Stock?  │  │Kiosk?  │
    └────────┘  └────────┘  └────────┘
      Local       Local       Local
      Copy        Copy        Copy
```

## Deployment-Strategie Empfehlung

### Option A: **Git-Pull Deployment** (EMPFOHLEN)

**Konzept:** Jedes Device hat ein Git-Repo-Clone und pulled Updates

**Vorteile:**
- ✅ Version Control
- ✅ Rollback möglich
- ✅ Audit Trail
- ✅ Automatisierbar

**Implementierung:**

```bash
# Auf Surface Go einmalig:
ssh frontend@surface-go
cd /home/frontend
git clone https://github.com/yourorg/FraWo.git homeserver2027-portal
cd homeserver2027-portal

# Symlink für HTTP Server:
ln -s artifacts/surface_index_v2_with_nowplaying.html index.html

# Systemd Service für Auto-Update:
# /home/frontend/.config/systemd/user/surface-update.service
[Unit]
Description=Surface Control Auto-Update
After=network-online.target

[Service]
Type=oneshot
WorkingDirectory=/home/frontend/homeserver2027-portal
ExecStart=/usr/bin/git pull origin main
ExecStartPost=/usr/bin/systemctl --user restart surface-http-server

[Install]
WantedBy=default.target

# Timer für tägliches Update:
# /home/frontend/.config/systemd/user/surface-update.timer
[Unit]
Description=Daily Surface Control Update

[Timer]
OnCalendar=daily
OnBootSec=5min
Persistent=true

[Install]
WantedBy=timers.target
```

**Auto-Update Setup:**
```bash
# Enable timer
systemctl --user enable surface-update.timer
systemctl --user start surface-update.timer

# Manual Update
systemctl --user start surface-update.service
```

### Option B: **Ansible Deployment** (ENTERPRISE-GRADE)

**Konzept:** Centralized Ansible Playbook pushed zu allen Devices

**Vorteile:**
- ✅ Multi-Device Management
- ✅ Configuration as Code
- ✅ Idempotent
- ✅ Bereits etabliert in FraWo

**Implementierung:**

```yaml
# ansible/playbooks/deploy_surface_control.yml
---
- name: Deploy Surface Control V2
  hosts: surface_frontends
  become: no
  tasks:
    - name: Ensure control surface directory exists
      file:
        path: "{{ surface_go_portal_dir }}"
        state: directory
        owner: "{{ surface_go_kiosk_user }}"
        mode: '0755'

    - name: Copy Surface Control HTML
      copy:
        src: ../../artifacts/surface_index_v2_with_nowplaying.html
        dest: "{{ surface_go_portal_dir }}/index.html"
        owner: "{{ surface_go_kiosk_user }}"
        mode: '0644'
      notify: Reload Firefox Kiosk

    - name: Ensure HTTP server is running
      systemd:
        name: surface-http-server
        state: started
        enabled: yes
        scope: user
      become_user: "{{ surface_go_kiosk_user }}"

  handlers:
    - name: Reload Firefox Kiosk
      systemd:
        name: firefox-kiosk
        state: restarted
        scope: user
      become_user: "{{ surface_go_kiosk_user }}"
```

**Inventory:**
```yaml
# ansible/inventory/hosts.yml
surface_frontends:
  hosts:
    surface_go_anker:
      ansible_host: 192.168.2.154
    # Zukünftig:
    # surface_go_stock:
    #   ansible_host: 192.168.178.XXX
```

**Deployment Command:**
```bash
# Von StudioPC aus:
ansible-playbook ansible/playbooks/deploy_surface_control.yml

# Nur für ein Device:
ansible-playbook ansible/playbooks/deploy_surface_control.yml -l surface_go_anker
```

### Option C: **HTTP-Pull von Central Server** (DYNAMIC)

**Konzept:** Surface lädt HTML vom zentralen Server (Toolbox)

**Vorteile:**
- ✅ Instant Updates
- ✅ No deployment needed
- ✅ Single file to maintain

**Nachteile:**
- ❌ Requires Toolbox uptime
- ❌ No offline capability
- ❌ Network dependency

**Implementierung:**

```bash
# Auf Toolbox (CT 100):
# Serve via Caddy
/srv/portal/surface/index.html -> surface_index_v2_with_nowplaying.html

# Auf Surface Go:
# Firefox Kiosk URL ändern:
http://portal.hs27.internal/surface/
```

## Empfohlene Architektur: **Hybrid Approach**

### Layer 1: Git as SSOT
```
Git Repo (StudioPC)
└── artifacts/surface_index_v2_with_nowplaying.html
```

### Layer 2: Central Distribution (Toolbox)
```
CT 100 Caddy
├── /srv/portal/surface/index.html (Git-synced)
└── http://portal.hs27.internal/surface/
```

### Layer 3: Local Caching (Surface Devices)
```
Surface Go
├── /home/frontend/homeserver2027-portal/index.html
├── Systemd Timer: Daily Git Pull
└── Fallback: Local copy if network down
```

### Implementation Steps:

**1. StudioPC → Git Commit:**
```bash
# Nach Änderungen:
cd c:\WORKSPACE\FraWo
git add artifacts/surface_index_v2_with_nowplaying.html
git commit -m "feat: update Surface Control V2"
git push origin main
```

**2. Toolbox → Git Pull Hook:**
```bash
# /srv/portal/surface/update.sh
#!/bin/bash
cd /srv/frawo-repo
git pull origin main
cp artifacts/surface_index_v2_with_nowplaying.html /srv/portal/surface/index.html
systemctl reload caddy
```

**3. Surface Go → Dual Source:**
```bash
# Firefox Kiosk URL:
http://portal.hs27.internal/surface/

# Fallback Service:
ExecStart=/usr/bin/firefox --kiosk http://localhost:17827 || http://portal.hs27.internal/surface/
```

## Service-Aware URL-Switching

### Intelligente Backend-Selektion

Das Surface Control sollte **automatisch** den verfügbaren Service-Standort wählen:

```javascript
// In surface_index_v2_with_nowplaying.html
const serviceEndpoints = {
  radio: {
    primary: 'http://radio-stock.hs27.internal',  // Wenn DNS läuft
    fallback: 'http://192.168.178.210',            // Direct IP
    anker: 'http://radio-anker.hs27.internal',     // Wenn Pi online
  },
  odoo: {
    primary: 'http://odoo.hs27.internal',
    fallback: 'http://10.1.0.22:8069'
  }
};

// Auto-detect verfügbaren Endpoint
async function getAvailableEndpoint(service) {
  for (const [name, url] of Object.entries(serviceEndpoints[service])) {
    if (await checkServiceHealth(name, url)) {
      return url;
    }
  }
  return serviceEndpoints[service].primary; // Fallback
}
```

## Multi-Site Considerations

### Stockenweiler vs. Anker

**Unterschiede:**
- **Netzwerk**: Anker 10.1.0.0/24, Stockenweiler 192.168.178.0/24
- **Radio**: Anker hat Pi (offline), Stockenweiler hat VM 210 (online)
- **DNS**: hs27.internal resolved nur in Anker

**Lösung: Site-Detection:**

```javascript
// Auto-detect site based on network
async function detectSite() {
  // Try Anker-specific endpoint
  if (await fetch('http://10.1.0.20')) {
    return 'anker';
  }
  // Try Stockenweiler-specific endpoint
  if (await fetch('http://192.168.178.210')) {
    return 'stockenweiler';
  }
  return 'unknown';
}

// Site-specific service URLs
const siteConfig = {
  anker: {
    radio: 'http://radio-anker.hs27.internal',
    odoo: 'http://odoo.hs27.internal'
  },
  stockenweiler: {
    radio: 'http://192.168.178.210',
    odoo: 'http://192.168.178.XXX' // Falls Odoo auch dort läuft
  }
};
```

## Auto-Update Mechanismus

### Systemd Timer (EMPFOHLEN)

```bash
# /etc/systemd/user/surface-control-update.timer
[Unit]
Description=Surface Control Auto-Update Timer

[Timer]
OnBootSec=2min
OnUnitActiveSec=6h
Persistent=true

[Install]
WantedBy=timers.target

# /etc/systemd/user/surface-control-update.service
[Unit]
Description=Update Surface Control from Git
After=network-online.target

[Service]
Type=oneshot
WorkingDirectory=/home/frontend/homeserver2027-portal
ExecStart=/usr/bin/git fetch origin
ExecStart=/usr/bin/git reset --hard origin/main
ExecStartPost=/bin/systemctl --user reload firefox-kiosk

[Install]
WantedBy=default.target
```

**Enable:**
```bash
systemctl --user enable surface-control-update.timer
systemctl --user start surface-control-update.timer
```

## Rollout Plan

### Phase 1: Single Surface Go @ Anker (CURRENT)
1. ✅ Ansible Playbook erstellen
2. ✅ Lokales Git-Repo auf Surface
3. ✅ Systemd Timer für Auto-Update
4. ✅ Test mit surface_index_v2_with_nowplaying.html

### Phase 2: Toolbox Central Distribution
1. Git-Pull Hook auf CT 100 Toolbox
2. Caddy /surface/ Endpoint
3. Surface Go configured für dual-source (local + remote)

### Phase 3: Multi-Device (FUTURE)
1. Surface Go @ Stockenweiler hinzufügen
2. Radio Node als Kiosk (wenn Pi online)
3. Site-Detection Logic aktivieren

## Recommended Next Steps

### JETZT (Immediate):

**1. Ansible Playbook erstellen:**
```bash
# Datei: ansible/playbooks/deploy_surface_control.yml
# Siehe oben
```

**2. Deployment testen:**
```bash
ansible-playbook ansible/playbooks/deploy_surface_control.yml --check
ansible-playbook ansible/playbooks/deploy_surface_control.yml
```

**3. Auto-Update Timer auf Surface:**
```bash
ssh frontend@surface-go
systemctl --user enable surface-control-update.timer
```

### BALD (Short-term):

**4. Git-Pull Hook auf Toolbox:**
```bash
# /srv/portal/surface/sync.sh + Cron
```

**5. DNS-Einträge deployen:**
```bash
# radio-stock.hs27.internal -> 192.168.178.210
# radio-anker.hs27.internal -> 10.3.0.10
```

**6. Site-Detection implementieren:**
```javascript
// In surface_index_v2_with_nowplaying.html
```

### SPÄTER (Long-term):

**7. Multi-Site Support:**
- Surface @ Stockenweiler
- Radio Node Kiosk Mode

**8. Advanced Features:**
- WebSocket für Real-Time Updates
- Service Health Dashboard
- Custom Shortcuts

## Security Considerations

### Single Source of Truth
- ✅ Git Repo ist SSOT
- ✅ Kein manuelles Editing auf Devices
- ✅ Alle Änderungen via Git Commit

### Access Control
- ✅ Surface Go: Local user `frontend` (non-admin)
- ✅ HTTP Server: localhost:17827 (no external exposure)
- ✅ Git Pull: Read-only access ausreichend

### Audit Trail
- ✅ Git Commit History
- ✅ Systemd Journal Logging
- ✅ Service Health Logs

## Zusammenfassung

**Best Practice für FraWo:**

1. **Git als SSOT** - alle Änderungen im Repo
2. **Ansible für Deployment** - idempotent, multi-device ready
3. **Systemd Timer für Auto-Update** - regelmäßige Sync
4. **Lokale Kopie + Remote Fallback** - Offline-Fähigkeit
5. **Site-Detection** - Multi-Standort Support

**Macht das Sinn?** ✅ JA!

- Eine Code-Base für alle Devices
- Zentrale Wartung
- Automatische Distribution
- Multi-Site Ready
- Offline Fallback

**Nächster Schritt:** Ansible Playbook erstellen und deployen?
