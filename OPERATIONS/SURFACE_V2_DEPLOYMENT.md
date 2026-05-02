# Surface Control V2 Deployment Operations

Stand: `2026-04-22`

## Zweck

Operative Anleitung für das Deployment von Surface Control V2 auf dem Surface Go Frontend.

## Voraussetzungen

- [ ] Surface Go Frontend ist erreichbar via SSH
- [ ] Ansible-Inventar ist konfiguriert (`surface_go_frontend`)
- [ ] Tailscale-Verbindung ist aktiv
- [ ] Repo ist auf dem neuesten Stand (`git pull`)

## Deployment-Methoden

### Methode 1: Schnelles Manuelles Update (5 Minuten)

**Verwendung**: Wenn nur die HTML-Datei aktualisiert werden soll.

```bash
# 1. Aus dem FraWo-Repo-Root
cd c:/Users/StudioPC/OneDrive/Dokumente/GitHub/FraWo

# 2. Kopiere V2 HTML zum Surface Go
scp artifacts/surface_index_v2.html frawo@surface-go-frontend:/home/frontend/homeserver2027-portal/index.html

# 3. SSH zum Surface Go
ssh frawo@surface-go-frontend

# 4. Restart Portal Service
sudo systemctl restart homeserver2027-surface-portal.service

# 5. Verifiziere Service
sudo systemctl status homeserver2027-surface-portal.service

# 6. Test im Browser
curl http://127.0.0.1:17827 | head -20

# 7. Exit SSH
exit
```

### Methode 2: Vollständiges Ansible Deployment (15 Minuten)

**Verwendung**: Für komplette Neukonfiguration oder Updates von Manifest + HTML.

```bash
# 1. Aus dem FraWo-Repo-Root
cd c:/Users/StudioPC/OneDrive/Dokumente/GitHub/FraWo

# 2. Ansible Inventory prüfen
ansible-inventory --list | grep surface_go_frontend

# 3. Vault-Passwort bereit haben
# (wird interaktiv abgefragt oder via --vault-password-file)

# 4. Playbook ausführen
ansible-playbook ansible/playbooks/bootstrap_surface_go_frontend.yml --ask-vault-pass

# 5. Warte auf Completion (ca. 10-15 Min)

# 6. SSH zum Surface Go und verifiziere
ssh frawo@surface-go-frontend
systemctl status homeserver2027-surface-portal.service
curl http://127.0.0.1:17827
exit
```

### Methode 3: Remote-Test ohne Deployment (2 Minuten)

**Verwendung**: Um zu testen, ob Surface Go erreichbar ist.

```bash
# 1. SSH Test
ssh frawo@surface-go-frontend "echo 'Surface Go erreichbar'"

# 2. Service Status Check
ssh frawo@surface-go-frontend "systemctl is-active homeserver2027-surface-portal.service"

# 3. Portal HTTP Check
ssh frawo@surface-go-frontend "curl -s http://127.0.0.1:17827 | head -5"

# 4. Firefox Kiosk Check
ssh frawo@surface-go-frontend "ps aux | grep firefox | grep -v grep"
```

## Verifikation nach Deployment

### Checkliste: V2 Features

Führe diese Checks auf dem Surface Go durch (direkt am Gerät oder via SSH):

```bash
# 1. Portal Service läuft
systemctl is-active homeserver2027-surface-portal.service
# Expected: active

# 2. Portal antwortet auf HTTP
curl -I http://127.0.0.1:17827
# Expected: HTTP/1.0 200 OK

# 3. V2 HTML ist deployed
curl http://127.0.0.1:17827 | grep "Surface Control V2"
# Expected: gefunden

# 4. System-Kategorie ist vorhanden
curl http://127.0.0.1:17827 | grep "group-system"
# Expected: gefunden

# 5. Status Badge ist vorhanden
curl http://127.0.0.1:17827 | grep "status-badge"
# Expected: gefunden

# 6. Fullscreen Button ist vorhanden
curl http://127.0.0.1:17827 | grep "toggleFullscreen"
# Expected: gefunden
```

### Visual Verification (am Surface Go)

**Am Gerät selbst prüfen**:

- [ ] Firefox startet automatisch nach Login
- [ ] Surface Control wird im Fullscreen angezeigt
- [ ] 4 Kategorien sind sichtbar: Dokumente, Odoo, Radio, System
- [ ] System-Kategorie zeigt: Portal, Vaultwarden, Home Assistant, Jellyfin
- [ ] Status-Badge zeigt "Live" mit Animation
- [ ] Clock zeigt aktuelle Uhrzeit (Format: HH:MM)
- [ ] Touch auf Action Card funktioniert (öffnet Service)
- [ ] "Neu laden" Button funktioniert
- [ ] "Vollbild" Button funktioniert
- [ ] F11 togglet Fullscreen
- [ ] Touch-Feedback bei Tap sichtbar

## Troubleshooting

### Problem: SSH-Verbindung schlägt fehl

```bash
# Test Tailscale
tailscale status | grep surface

# Test Ping
ping surface-go-frontend.tail-scale.ts.net

# Test SSH mit verbose
ssh -v frawo@surface-go-frontend
```

**Lösung**:
1. Prüfe Tailscale-Verbindung auf beiden Seiten
2. Prüfe SSH-Service auf Surface Go
3. Prüfe Firewall-Regeln

### Problem: Portal Service startet nicht

```bash
# Detaillierte Logs
ssh frawo@surface-go-frontend "sudo journalctl -u homeserver2027-surface-portal.service -n 50 --no-pager"

# Service-Datei prüfen
ssh frawo@surface-go-frontend "cat /etc/systemd/system/homeserver2027-surface-portal.service"

# Manual Start Test
ssh frawo@surface-go-frontend "cd /home/frontend/homeserver2027-portal && python3 -m http.server 17827 --bind 127.0.0.1"
```

**Lösung**:
1. Prüfe ob Python3 installiert ist
2. Prüfe Datei-Permissions in `/home/frontend/homeserver2027-portal/`
3. Prüfe ob Port 17827 bereits belegt ist

### Problem: HTML-Datei nicht aktualisiert

```bash
# Prüfe Datei-Datum
ssh frawo@surface-go-frontend "ls -la /home/frontend/homeserver2027-portal/index.html"

# Prüfe Datei-Inhalt
ssh frawo@surface-go-frontend "head -30 /home/frontend/homeserver2027-portal/index.html"

# Prüfe Owner
ssh frawo@surface-go-frontend "stat /home/frontend/homeserver2027-portal/index.html"
```

**Lösung**:
1. SCP erneut mit `-v` für verbose
2. Prüfe Ziel-Pfad korrekt
3. Prüfe Schreib-Rechte für `frawo` user

### Problem: Services nicht erreichbar (hs27.internal)

```bash
# DNS Test
ssh frawo@surface-go-frontend "nslookup odoo.hs27.internal"

# Ping Test
ssh frawo@surface-go-frontend "ping -c 2 portal.hs27.internal"

# /etc/hosts Check
ssh frawo@surface-go-frontend "cat /etc/hosts | grep hs27"
```

**Lösung**:
1. Prüfe DNS-Konfiguration (UniFi/Tailscale)
2. Prüfe `/etc/hosts` Einträge
3. Prüfe Tailscale Magic DNS

## Rollback-Prozedur

Falls V2 Probleme macht, Rollback zu V1:

```bash
# 1. SSH zum Surface Go
ssh frawo@surface-go-frontend

# 2. Backup V2 (falls nicht schon geschehen)
sudo cp /home/frontend/homeserver2027-portal/index.html /home/frontend/homeserver2027-portal/index_v2_backup.html

# 3. Hole V1 vom Repo
# (Option A: Lokal kopieren und hochladen)
# (Option B: Git checkout auf Surface Go falls Repo dort ist)

# 4. Restart Service
sudo systemctl restart homeserver2027-surface-portal.service

# 5. Verifiziere
curl http://127.0.0.1:17827 | head -20
```

## Automation für CI/CD (Future)

**GitHub Actions Workflow** (Placeholder):

```yaml
name: Deploy Surface Control V2

on:
  push:
    paths:
      - 'artifacts/surface_index_v2.html'
      - 'manifests/control_surface/actions_v2.json'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Deploy to Surface Go
        run: |
          scp artifacts/surface_index_v2.html frawo@surface-go-frontend:/home/frontend/homeserver2027-portal/index.html
          ssh frawo@surface-go-frontend "sudo systemctl restart homeserver2027-surface-portal.service"
```

## Post-Deployment Dokumentation

Nach erfolgreichem Deployment:

1. **Update LIVE_CONTEXT.md**
   ```markdown
   - Surface Go Frontend: Running V2 (deployed YYYY-MM-DD)
   ```

2. **Update Odoo-Projektboard**
   - Markiere die Surface-bezogene Aufgabe im Projekt `🚀 Homeserver 2027: Masterplan` als erledigt oder passe den Status an

3. **GitHub Issue schließen** (falls vorhanden)

4. **Operator-Logbuch** aktualisieren

## Related Documentation

- **V2 Features**: `DOCS/SURFACE_CONTROL_V2.md`
- **Actions Manifest**: `manifests/control_surface/actions_v2.json`
- **Ansible Playbook**: `ansible/playbooks/bootstrap_surface_go_frontend.yml`
- **Host Variables**: `ansible/inventory/host_vars/surface_go_frontend.yml`

## Approval Required

**Operator Action**: Deployment nur nach Freigabe durch Wolf/Franz.

**Maintenance Window**: Empfohlen außerhalb der Arbeitszeiten.

---

Stand: 2026-04-22
Status: Ready for Execution
Nächster Schritt: OpenClaw Stabilisierung
