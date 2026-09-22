# Surface Go Neuaufbau (Teil 1) — Umsetzungsplan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Den Surface Go ohne Anwesenheit vor Ort frisch installieren und so einrichten, dass er nach jedem Neustart
selbst in FRAWO Home Control startet — reproduzierbar aus dem Repo.

**Architecture:** Ein auf dem OptiPlex gebautes Ubuntu-24.04-**Server**-Abbild enthält eine Antwortdatei
(`/autoinstall.yaml`). Der laufende Surface startet es einmalig per GRUB-Loopback (`toram`), installiert sich
unbeaufsichtigt, kommt per WLAN zurück; danach richtet `frawo-surface-setup.sh` GNOME, Benutzer, Starter, Portal
und Wartung ein. `pruefen.sh` ist die Abnahme als Code und läuft vor und nach jedem Schritt.

**Tech Stack:** Ubuntu 24.04 LTS (subiquity-Autoinstall, GRUB, GNOME/Wayland, dconf), Chromium-Snap, Python 3,
xorriso, Proxmox (Test-VM), UniFi-API (`ucg.py`), Prometheus.

**Spec:** `DOCS/specs/2026-09-22-surface-neuaufbau-design.md`

**Planentscheidung (präzisiert die Spec):** Installationsmedium ist das **Server**-Abbild (≈ 3 GB, passt sicher in
8 GB RAM für `toram`); GNOME (`ubuntu-desktop-minimal`) kommt per Einrichtungsskript. Das Ergebnis entspricht der Spec.
Scheitert `toram` im Probelauf, gilt **Weg B (USB-Stick)** — eine zusätzliche Partition wird **nicht** angelegt.

## Global Constraints

- Gerät: Surface Go 1, WLAN `wlp1s0` (QCA6174), MAC `d8:c4:97:c6:0e:b0`, Ziel-Adresse `10.4.0.38` (IoT, VLAN 104)
- Benutzer: `anzeige` (Autologin, **kein** sudo, Passwort gesperrt) · `frawo` (nur SSH-Schlüssel, sudo NOPASSWD, Passwort gesperrt)
- SSH-Schlüssel: StudioPC `~/.ssh/hs27_ops_ed25519.pub` + OptiPlex `/root/.ssh/id_*.pub`
- Tailscale: immer `--accept-routes=false`
- Bildschirm aus nach 600 s, **kein** Ruhezustand; Sicherheitsupdates mit Neustart 04:00
- Starter: Home Control `http://127.0.0.1:17827/` · Radio Control `http://127.0.0.1:17827/#tab-radio` · Monitor `http://10.1.0.35:3000/d/frawo-zentrale`
- Chromium-Parameter: `--ozone-platform=wayland --enable-wayland-ime --force-device-scale-factor=1.6`
- **Secrets:** WLAN-Passwort nie im Repo; nur im gebauten Abbild (`chmod 600`) und nur so lange wie nötig
- Wolf **keine** Odoo-Meldungen: Chatter nur `subtype=note`, Jarvis nur über `partner_ids=[124]`
- Zugang heute: StudioPC → `ssh -o IdentitiesOnly=yes -i ~/.ssh/hs27_ops_ed25519 frawo@10.4.0.38`
- Alle Skripte mit LF-Zeilenenden (Write-Tool), `bash -n` vor jedem Einsatz

## Dateien

| Pfad (Repo) | Aufgabe |
|---|---|
| `deployments/network/ucg.py` | UniFi-Werkzeug (Kopie von OptiPlex `/root/m1/ucg.py`, + Netz `iot`) |
| `deployments/surface/os/pruefen.sh` | Abnahme als Code, `PASS`/`FAIL` je Punkt, Exit = Anzahl FAIL |
| `deployments/surface/os/autoinstall.yaml.vorlage` | Antwortdatei mit Platzhaltern `@@WLAN_PSK@@`, `@@PASSWORT_HASH@@`, `@@SSH_KEYS@@` |
| `deployments/surface/os/schluessel/*.pub` | öffentliche SSH-Schlüssel |
| `deployments/surface/os/baue-iso.sh` | baut `frawo-surface.iso` auf dem OptiPlex |
| `deployments/surface/os/neuinstallation-aktivieren.sh` | legt den einmaligen GRUB-Starteintrag an |
| `deployments/surface/os/frawo-surface-setup.sh` | Einrichtung nach der Installation (idempotent) |
| `deployments/surface/os/dateien/…` | udev-Regel, dconf, GDM, Starter, Portal-Dienst, Update-Regel |
| `deployments/surface/os/sichern.sh` | Sicherung Surface → ProDesk (läuft auf dem StudioPC) |

---

### Task 1: Werkzeuge ins Repo und Abnahme als Code

**Files:**
- Create: `deployments/network/ucg.py` (von OptiPlex holen, dann ändern)
- Create: `deployments/surface/os/pruefen.sh`

**Interfaces:**
- Produces: `pruefen.sh [--vm]` — gibt je Punkt `PASS <text>` / `FAIL <text>` aus, Exit-Code = Anzahl FAIL.
  `--vm` überspringt WLAN-, Tailscale-, AnyDesk- und Touch-Punkte.
- Produces: `ucg.py reserve MAC IP iot NAME` (neues Netz `iot` = `69d1001127ec024b992dcb88`)
- Produces: `ucg.py forget MAC` (entfernt eine Zuteilung, z. B. die der Test-VM)

- [ ] **Step 1: `ucg.py` ins Repo holen**

```bash
ssh -o BatchMode=yes anker-pve 'ssh -o BatchMode=yes root@10.1.0.227 "cat /root/m1/ucg.py"' > /c/Users/StudioPC/FraWo/deployments/network/ucg.py
grep -c FRAWO_UNIFI_KEY /c/Users/StudioPC/FraWo/deployments/network/ucg.py   # erwartet: >= 1, KEIN Schlüsselwert in der Datei
```

- [ ] **Step 2: Netz `iot` ergänzen** — in `ucg.py` die Zeile `NET = {...}` ersetzen durch:

```python
NET = {"lan": "69d0ff7727ec024b992dcb6f", "server": "69d0ff9b27ec024b992dcb7f", "iot": "69d1001127ec024b992dcb88"}
```

Und vor dem Block `if __name__ == "__main__":` die Funktion `forget` ergänzen, danach in die Befehlstabelle aufnehmen:

```python
def forget(mac):
    call("POST", "/cmd/stamgr", {"cmd": "forget-sta", "macs": [mac.lower()]})
    rest = [u for u in call("GET", "/rest/user") if u.get("mac", "").lower() == mac.lower()]
    print(f"{mac} vergessen" if not rest else f"FEHLER: {mac} noch vorhanden")
```

```python
    {"backup": backup, "native": native, "reserve": reserve, "ports": ports, "forget": forget}[cmd](*args)
```

- [ ] **Step 3: Prüfskript schreiben** — `deployments/surface/os/pruefen.sh`:

```bash
#!/bin/bash
# Abnahme Surface-Neuaufbau (Spec Abschnitt 4). Laeuft AUF dem Geraet als root: sudo -n bash pruefen.sh
# Ausgabe: PASS/FAIL je Punkt. Exit-Code = Anzahl FAIL.  --vm: ohne WLAN/Tailscale/AnyDesk/Touch.
VM=0; [ "${1:-}" = "--vm" ] && VM=1
F=0
ok()   { echo "PASS $1"; }
nein() { echo "FAIL $1"; F=$((F+1)); }
pr()   { if eval "$2" >/dev/null 2>&1; then ok "$1"; else nein "$1"; fi; }

pr "sshd: Passwort-Anmeldung aus"          "sudo -n sshd -T | grep -qx 'passwordauthentication no'"
pr "frawo: Passwort gesperrt"              "sudo -n passwd -S frawo | grep -q ' L '"
pr "frawo: sudo ohne Passwort"             "runuser -u frawo -- sudo -n true"
pr "anzeige: existiert"                    "id anzeige"
pr "anzeige: kein sudo"                    "! id -nG anzeige | grep -qw sudo"
pr "anzeige: Passwort gesperrt"            "sudo -n passwd -S anzeige | grep -q ' L '"
pr "GDM: Autologin anzeige"                "grep -qx 'AutomaticLogin=anzeige' /etc/gdm3/custom.conf"
pr "Sitzung anzeige laeuft"                "loginctl list-sessions --no-legend | grep -qw anzeige"
pr "Home Control laeuft"                   "pgrep -u anzeige -f 'chromium.*--app=http://127.0.0.1:17827/'"
pr "Portal antwortet"                      "curl -fsS -o /dev/null -m 5 http://127.0.0.1:17827/"
pr "dconf: Bildschirmtastatur an"          "grep -q 'screen-keyboard-enabled=true' /etc/dconf/db/local.d/00-frawo"
pr "dconf: kein Ruhezustand"               "grep -q \"sleep-inactive-ac-type='nothing'\" /etc/dconf/db/local.d/00-frawo"
pr "dconf: Bildschirm aus nach 600 s"      "grep -q 'idle-delay=uint32 600' /etc/dconf/db/local.d/00-frawo"
pr "Starter: drei vorhanden"               "[ \$(ls /usr/share/applications/frawo-*.desktop | wc -l) -eq 3 ]"
pr "Updates: Neustart 04:00"               "grep -q 'Automatic-Reboot-Time \"04:00\"' /etc/apt/apt.conf.d/52frawo-updates"
pr "node_exporter antwortet"               "curl -fsS -o /dev/null -m 5 http://127.0.0.1:9100/metrics"
pr "Odoo erreichbar :8069"                 "timeout 4 bash -c '</dev/tcp/10.1.0.112/8069'"
pr "Home Assistant erreichbar :8123"       "timeout 4 bash -c '</dev/tcp/10.1.0.40/8123'"
pr "Grafana erreichbar :3000"              "timeout 4 bash -c '</dev/tcp/10.1.0.35/3000'"
pr "Kein Installationsrest /frawo-install" "[ ! -e /frawo-install ]"
if [ $VM = 0 ]; then
  pr "Route Server-Netz ueber Gateway"      "ip route get 10.1.0.112 | grep -q 'via 10.4.0.1 dev wlp1s0'"
  pr "Tailscale: RouteAll aus"              "sudo -n tailscale debug prefs | grep -q '\"RouteAll\": false'"
  pr "AnyDesk-Dienst aktiv"                 "systemctl is-active --quiet anydesk"
  pr "udev: Phantom-Tastatur ignoriert"     "[ -f /etc/udev/rules.d/99-frawo-phantom-tastatur.rules ]"
fi
echo "--- $F Fehler"
exit $F
```

- [ ] **Step 4: Prüfung gegen den HEUTIGEN Surface laufen lassen — sie muss scheitern können**

```bash
cd /c/Users/StudioPC/FraWo/deployments/surface/os && bash -n pruefen.sh
scp -q -o IdentitiesOnly=yes -i ~/.ssh/hs27_ops_ed25519 pruefen.sh frawo@10.4.0.38:/tmp/
ssh -o IdentitiesOnly=yes -i ~/.ssh/hs27_ops_ed25519 frawo@10.4.0.38 'sudo -n bash /tmp/pruefen.sh; echo "exit=$?"'
```
Expected: mehrere `FAIL` (u. a. `anzeige: existiert`, `GDM: Autologin anzeige`, `dconf: …`), `exit` > 0.
Und `PASS` bei `Odoo erreichbar`, `Route Server-Netz ueber Gateway`, `Tailscale: RouteAll aus` (am 22.09. repariert).

- [ ] **Step 5: `ucg.py` auf dem OptiPlex aktualisieren und `iot` testen**

```bash
cat /c/Users/StudioPC/FraWo/deployments/network/ucg.py | ssh -o BatchMode=yes anker-pve 'ssh -o BatchMode=yes root@10.1.0.227 "cp /root/m1/ucg.py /root/m1/ucg.py.bak-20260922 && cat > /root/m1/ucg.py && cd /root/m1 && python3 ucg.py ports"'
```
Expected: vier Port-Zeilen wie zuvor (Werkzeug funktioniert unverändert).

- [ ] **Step 6: Commit**

```bash
cd /c/Users/StudioPC/FraWo && git add deployments/network/ucg.py deployments/surface/os/pruefen.sh
git commit -m "🤖 [Claude] Surface-Neuaufbau: Abnahme als Code + ucg.py im Repo"
```

---

### Task 2: Antwortdatei und Installationsabbild

**Files:**
- Create: `deployments/surface/os/autoinstall.yaml.vorlage`
- Create: `deployments/surface/os/schluessel/studiopc-hs27_ops.pub`, `deployments/surface/os/schluessel/optiplex-root.pub`
- Create: `deployments/surface/os/baue-iso.sh`
- Create: `deployments/surface/os/neuinstallation-aktivieren.sh`

**Interfaces:**
- Consumes: `ucg.py` `call('GET','/rest/wlanconf')` (Task 1)
- Produces: OptiPlex `/root/surface-iso/frawo-surface.iso` + `frawo-surface.iso.sha256` (Datei-Rechte 600)
- Produces: `sudo bash neuinstallation-aktivieren.sh` — erwartet `/frawo-install/frawo-surface.iso` + `.sha256`
  auf dem Zielgerät, setzt einen **einmaligen** GRUB-Start (`next_entry=frawo-neu`); genutzt in Task 4 und Task 6

- [ ] **Step 1: Öffentliche Schlüssel ablegen**

```bash
mkdir -p /c/Users/StudioPC/FraWo/deployments/surface/os/schluessel
cp ~/.ssh/hs27_ops_ed25519.pub /c/Users/StudioPC/FraWo/deployments/surface/os/schluessel/studiopc-hs27_ops.pub
ssh -o BatchMode=yes anker-pve 'ssh -o BatchMode=yes root@10.1.0.227 "cat /root/.ssh/id_ed25519.pub 2>/dev/null || cat /root/.ssh/id_rsa.pub"' > /c/Users/StudioPC/FraWo/deployments/surface/os/schluessel/optiplex-root.pub
grep -L '^ssh-' /c/Users/StudioPC/FraWo/deployments/surface/os/schluessel/*.pub   # erwartet: keine Ausgabe
```

- [ ] **Step 2: Antwortdatei-Vorlage** — `deployments/surface/os/autoinstall.yaml.vorlage`:

```yaml
autoinstall:
  version: 1
  refresh-installer:
    update: false
  locale: de_DE.UTF-8
  timezone: Europe/Berlin
  keyboard:
    layout: de
  source:
    id: ubuntu-server-minimal
  network:
    version: 2
    ethernets:
      kabel:
        match:
          name: "en*"
        dhcp4: true
        optional: true
    wifis:
      wlp1s0:
        dhcp4: true
        optional: true
        access-points:
          "FraWo__ioT":
            password: "@@WLAN_PSK@@"
  apt:
    fallback: offline-install
  storage:
    layout:
      name: direct
  identity:
    hostname: surface-go
    realname: FraWo Wartung
    username: frawo
    password: "@@PASSWORT_HASH@@"
  ssh:
    install-server: true
    allow-pw: false
    authorized-keys:
@@SSH_KEYS@@
  packages:
    - wpasupplicant
    - curl
  late-commands:
    - "echo 'frawo ALL=(ALL) NOPASSWD:ALL' > /target/etc/sudoers.d/frawo && chmod 440 /target/etc/sudoers.d/frawo"
    - "curtin in-target -- passwd -l frawo"
  shutdown: reboot
```

- [ ] **Step 3: Bauskript** — `deployments/surface/os/baue-iso.sh`:

```bash
#!/bin/bash
# Baut /root/surface-iso/frawo-surface.iso (Ubuntu 24.04 Server + /autoinstall.yaml). Laeuft auf dem OptiPlex als root.
# Enthaelt das WLAN-Passwort -> Ergebnis chmod 600, NIE ins Repo, nach dem Einsatz loeschen.
# Aufruf: REPO_OS=/root/surface-os bash baue-iso.sh
set -euo pipefail
REPO_OS=${REPO_OS:-/root/surface-os}
ARBEIT=/root/surface-iso
BASIS=https://releases.ubuntu.com/24.04
command -v xorriso >/dev/null || apt-get install -y xorriso
mkdir -p "$ARBEIT" && chmod 700 "$ARBEIT" && cd "$ARBEIT"
curl -fsSL "$BASIS/SHA256SUMS" -o SHA256SUMS
ISO=$(grep -o 'ubuntu-24\.04\.[0-9]*-live-server-amd64\.iso' SHA256SUMS | sort -V | tail -1)
[ -f "$ISO" ] || curl -fL --retry 3 -o "$ISO" "$BASIS/$ISO"
grep -E " \*?$ISO\$" SHA256SUMS | sha256sum -c -

PSK=$(python3 -c "
import sys; sys.path.insert(0, '/root/m1')
from ucg import call
print([w for w in call('GET', '/rest/wlanconf') if w.get('name') == 'FraWo__ioT'][0]['x_passphrase'])")
HASH=$(openssl passwd -6 "$(openssl rand -base64 24)")
export PSK HASH
umask 077
python3 - "$REPO_OS/autoinstall.yaml.vorlage" "$REPO_OS/schluessel" > autoinstall.yaml <<'PY'
import glob, json, os, sys
t = open(sys.argv[1], encoding='utf-8').read()
keys = [open(f).read().strip() for f in sorted(glob.glob(sys.argv[2] + '/*.pub'))]
t = t.replace('@@WLAN_PSK@@', json.dumps(os.environ['PSK'])[1:-1])
t = t.replace('@@PASSWORT_HASH@@', os.environ['HASH'])
t = t.replace('@@SSH_KEYS@@', '\n'.join('      - "%s"' % k for k in keys))
sys.stdout.write(t)
PY
python3 -c "import yaml; d=yaml.safe_load(open('autoinstall.yaml')); assert d['autoinstall']['ssh']['authorized-keys'], 'keine Schluessel'; assert '@@' not in open('autoinstall.yaml').read()"

xorriso -osirrox on -indev "$ISO" -extract /boot/grub/grub.cfg grub.cfg >/dev/null 2>&1
chmod u+w grub.cfg
sed -i -E 's|(linux\s+/casper/vmlinuz)\s+---|\1 autoinstall ---|' grub.cfg
sed -i -E 's/^set timeout=.*/set timeout=3/' grub.cfg
grep -q 'vmlinuz autoinstall ---' grub.cfg

rm -f frawo-surface.iso
xorriso -indev "$ISO" -outdev frawo-surface.iso \
  -map autoinstall.yaml /autoinstall.yaml \
  -map grub.cfg /boot/grub/grub.cfg \
  -boot_image any replay >/dev/null 2>&1
chmod 600 frawo-surface.iso autoinstall.yaml
sha256sum frawo-surface.iso > frawo-surface.iso.sha256
# Nachweis ohne das Passwort auszugeben:
xorriso -osirrox on -indev frawo-surface.iso -extract /autoinstall.yaml /dev/stdout 2>/dev/null | grep -c 'FraWo__ioT'
xorriso -osirrox on -indev frawo-surface.iso -extract /boot/grub/grub.cfg /dev/stdout 2>/dev/null | grep -c 'vmlinuz autoinstall ---'
cat frawo-surface.iso.sha256
```

- [ ] **Step 3b: Aktivierungsskript** — `deployments/surface/os/neuinstallation-aktivieren.sh`:

```bash
#!/bin/bash
# Aktiviert EINMALIG den Start ins Installationsabbild (GRUB-Loopback + toram).
# Startet das Abbild nicht, bootet der naechste Start wieder das alte System.
set -euo pipefail
cd /frawo-install
sha256sum -c frawo-surface.iso.sha256
cp -n /etc/default/grub /etc/default/grub.bak-$(date +%Y%m%d)
sed -i 's/^GRUB_DEFAULT=.*/GRUB_DEFAULT=saved/' /etc/default/grub
cat > /etc/grub.d/42_frawo_neuinstallation <<'EOF'
#!/bin/sh
exec tail -n +3 $0
menuentry "FraWo-Neuinstallation (automatisch)" --id frawo-neu {
    insmod part_gpt
    insmod ext2
    insmod iso9660
    insmod loopback
    set isofile="/frawo-install/frawo-surface.iso"
    search --no-floppy --set=root --file $isofile
    loopback loop ($root)$isofile
    linux (loop)/casper/vmlinuz iso-scan/filename=$isofile toram autoinstall ---
    initrd (loop)/casper/initrd
}
EOF
chmod 755 /etc/grub.d/42_frawo_neuinstallation
update-grub
grub-set-default 0
grub-reboot frawo-neu
grub-editenv list
echo "Bereit - naechster Start (einmalig): FraWo-Neuinstallation"
```

Die `sha256`-Datei enthält den Dateinamen ohne Pfad (von `baue-iso.sh` so erzeugt) — daher `cd /frawo-install`.

- [ ] **Step 4: Auf dem OptiPlex bauen**

```bash
cd /c/Users/StudioPC/FraWo/deployments/surface/os && bash -n baue-iso.sh && bash -n neuinstallation-aktivieren.sh
tar -cf - autoinstall.yaml.vorlage baue-iso.sh schluessel | ssh -o BatchMode=yes anker-pve 'ssh -o BatchMode=yes root@10.1.0.227 "rm -rf /root/surface-os && mkdir -p /root/surface-os && tar -xf - -C /root/surface-os && REPO_OS=/root/surface-os bash /root/surface-os/baue-iso.sh"'
```
Expected: `…iso: OK` (Prüfsumme Ubuntu), dann `1`, `1` (Antwortdatei + Starteintrag im Abbild), zuletzt die SHA256 von `frawo-surface.iso`. **Kein** Passwort in der Ausgabe.

- [ ] **Step 5: Commit** (nur Vorlage, Schlüssel, Skript — nie das Abbild)

```bash
cd /c/Users/StudioPC/FraWo && git add deployments/surface/os/autoinstall.yaml.vorlage deployments/surface/os/baue-iso.sh deployments/surface/os/neuinstallation-aktivieren.sh deployments/surface/os/schluessel
git commit -m "🤖 [Claude] Surface-Neuaufbau: Antwortdatei + Abbild-Bau (ohne Passwort)"
```

---

### Task 3: Einrichtungsskript

**Files:**
- Create: `deployments/surface/os/frawo-surface-setup.sh`
- Create: `deployments/surface/os/dateien/99-frawo-phantom-tastatur.rules`
- Create: `deployments/surface/os/dateien/dconf-profile-user`
- Create: `deployments/surface/os/dateien/00-frawo`
- Create: `deployments/surface/os/dateien/gdm-custom.conf`
- Create: `deployments/surface/os/dateien/frawo-home-control.desktop`
- Create: `deployments/surface/os/dateien/frawo-radio-control.desktop`
- Create: `deployments/surface/os/dateien/frawo-monitor.desktop`
- Create: `deployments/surface/os/dateien/frawo-home-control-autostart.desktop`
- Create: `deployments/surface/os/dateien/frawo-portal.service`
- Create: `deployments/surface/os/dateien/52frawo-updates`

**Interfaces:**
- Consumes: Portal-Dateien `deployments/surface/server.py`, `deployments/surface/frawo_anker_hub.html`
- Produces: `sudo bash frawo-surface-setup.sh [--vm]` — erwartet das Verzeichnis `deployments/surface/` als
  `/root/frawo-surface/` auf dem Zielgerät; Umgebungsvariable `TS_AUTHKEY` optional (nur ohne `--vm`)

- [ ] **Step 1: Dateien anlegen**

`dateien/99-frawo-phantom-tastatur.rules`:
```
SUBSYSTEM=="input", ATTRS{name}=="AT Translated Set 2 keyboard", ENV{LIBINPUT_IGNORE_DEVICE}="1"
```

`dateien/dconf-profile-user`:
```
user-db:user
system-db:local
```

`dateien/00-frawo`:
```
[org/gnome/desktop/a11y/applications]
screen-keyboard-enabled=true

[org/gnome/desktop/session]
idle-delay=uint32 600

[org/gnome/settings-daemon/plugins/power]
sleep-inactive-ac-type='nothing'
sleep-inactive-battery-type='nothing'

[org/gnome/desktop/screensaver]
lock-enabled=false

[org/gnome/desktop/interface]
text-scaling-factor=1.25

[org/gnome/shell]
favorite-apps=['frawo-home-control.desktop', 'frawo-radio-control.desktop', 'frawo-monitor.desktop', 'chromium_chromium.desktop', 'anydesk.desktop', 'org.gnome.Settings.desktop']
```

`dateien/gdm-custom.conf`:
```
[daemon]
AutomaticLoginEnable=true
AutomaticLogin=anzeige

[security]

[xdmcp]

[chooser]

[debug]
```

`dateien/frawo-home-control.desktop`:
```
[Desktop Entry]
Type=Application
Name=FRAWO Home Control
Comment=Touchboard: Haus, Aufgaben, Termine
Exec=/snap/bin/chromium --app=http://127.0.0.1:17827/ --ozone-platform=wayland --enable-wayland-ime --force-device-scale-factor=1.6 --no-first-run
Icon=go-home
Terminal=false
Categories=Utility;
```

`dateien/frawo-radio-control.desktop`:
```
[Desktop Entry]
Type=Application
Name=FRAWO Radio Control
Comment=Radio auf den Lautsprechern steuern
Exec=/snap/bin/chromium --app=http://127.0.0.1:17827/#tab-radio --ozone-platform=wayland --enable-wayland-ime --force-device-scale-factor=1.6 --no-first-run
Icon=audio-x-generic
Terminal=false
Categories=Utility;
```

`dateien/frawo-monitor.desktop`:
```
[Desktop Entry]
Type=Application
Name=FRAWO Monitor
Comment=Zustand der Anlage
Exec=/snap/bin/chromium --app=http://10.1.0.35:3000/d/frawo-zentrale --ozone-platform=wayland --enable-wayland-ime --force-device-scale-factor=1.6 --no-first-run
Icon=utilities-system-monitor
Terminal=false
Categories=Utility;
```

`dateien/frawo-home-control-autostart.desktop`:
```
[Desktop Entry]
Type=Application
Name=FRAWO Home Control (Autostart)
Exec=/snap/bin/chromium --app=http://127.0.0.1:17827/ --ozone-platform=wayland --enable-wayland-ime --force-device-scale-factor=1.6 --no-first-run --start-fullscreen
X-GNOME-Autostart-Delay=5
Terminal=false
```

`dateien/frawo-portal.service`:
```
[Unit]
Description=FraWo Touchboard-Portal (127.0.0.1:17827)
After=network-online.target
Wants=network-online.target

[Service]
ExecStart=/usr/bin/python3 /opt/frawo-portal/server.py
DynamicUser=yes
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

`dateien/52frawo-updates`:
```
Unattended-Upgrade::Automatic-Reboot "true";
Unattended-Upgrade::Automatic-Reboot-Time "04:00";
```

- [ ] **Step 2: Einrichtungsskript** — `deployments/surface/os/frawo-surface-setup.sh`:

```bash
#!/bin/bash
# Richtet den frisch installierten Surface ein (Spec Abschnitt 1). Wiederholbar.
# Erwartet deployments/surface/ als /root/frawo-surface/. Aufruf als root:
#   bash /root/frawo-surface/os/frawo-surface-setup.sh          (Surface; TS_AUTHKEY optional)
#   bash /root/frawo-surface/os/frawo-surface-setup.sh --vm     (Probelauf: ohne Tailscale/AnyDesk-Rueckspielung)
set -euo pipefail
VM=0; [ "${1:-}" = "--vm" ] && VM=1
OS=$(cd "$(dirname "$0")" && pwd)
D="$OS/dateien"
PORTAL_SRC=$(dirname "$OS")
export DEBIAN_FRONTEND=noninteractive

echo "== Pakete"
apt-get update -q
apt-get install -y -q ubuntu-desktop-minimal prometheus-node-exporter unattended-upgrades python3 curl
snap list chromium >/dev/null 2>&1 || snap install chromium

echo "== Benutzer anzeige"
id anzeige >/dev/null 2>&1 || useradd -m -s /bin/bash -c "Anzeige" anzeige
passwd -l anzeige >/dev/null
gpasswd -d anzeige sudo >/dev/null 2>&1 || true
passwd -l frawo >/dev/null

echo "== GDM, udev, dconf"
install -m 644 "$D/gdm-custom.conf" /etc/gdm3/custom.conf
install -m 644 "$D/99-frawo-phantom-tastatur.rules" /etc/udev/rules.d/99-frawo-phantom-tastatur.rules
udevadm control --reload
install -D -m 644 "$D/dconf-profile-user" /etc/dconf/profile/user
install -D -m 644 "$D/00-frawo" /etc/dconf/db/local.d/00-frawo
dconf update

echo "== Starter"
for s in frawo-home-control frawo-radio-control frawo-monitor; do
  install -m 644 "$D/$s.desktop" "/usr/share/applications/$s.desktop"
done
install -D -m 644 "$D/frawo-home-control-autostart.desktop" /etc/xdg/autostart/frawo-home-control.desktop

echo "== Portal"
install -d -m 755 /opt/frawo-portal
install -m 644 "$PORTAL_SRC/server.py" /opt/frawo-portal/server.py
install -m 644 "$PORTAL_SRC/frawo_anker_hub.html" /opt/frawo-portal/frawo_anker_hub.html
install -m 644 "$PORTAL_SRC/frawo_anker_hub.html" /opt/frawo-portal/index.html
install -m 644 "$D/frawo-portal.service" /etc/systemd/system/frawo-portal.service
systemctl daemon-reload
systemctl enable --now frawo-portal.service
systemctl restart frawo-portal.service

echo "== Updates, node_exporter"
install -m 644 "$D/52frawo-updates" /etc/apt/apt.conf.d/52frawo-updates
systemctl enable --now prometheus-node-exporter

echo "== AnyDesk"
if ! command -v anydesk >/dev/null; then
  install -d -m 755 /etc/apt/keyrings
  curl -fsSL https://keys.anydesk.com/repos/DEB-GPG-KEY -o /etc/apt/keyrings/anydesk.asc
  echo "deb [signed-by=/etc/apt/keyrings/anydesk.asc] https://deb.anydesk.com all main" > /etc/apt/sources.list.d/anydesk.list
  apt-get update -q && apt-get install -y -q anydesk
fi
if [ $VM = 0 ] && [ -f /root/anydesk-sicherung/service.conf ]; then
  systemctl stop anydesk
  install -m 600 /root/anydesk-sicherung/service.conf /etc/anydesk/service.conf
  install -m 600 /root/anydesk-sicherung/system.conf /etc/anydesk/system.conf
  systemctl start anydesk
fi

if [ $VM = 0 ]; then
  echo "== Tailscale"
  command -v tailscale >/dev/null || curl -fsSL https://tailscale.com/install.sh | sh
  if ! tailscale status >/dev/null 2>&1; then
    tailscale up --accept-routes=false --hostname=surface-go ${TS_AUTHKEY:+--auth-key="$TS_AUTHKEY"}
  fi
  tailscale set --accept-routes=false
fi

echo "== fertig - Neustart noetig, damit Autologin, udev und dconf greifen"
```

- [ ] **Step 3: Syntax prüfen**

```bash
cd /c/Users/StudioPC/FraWo/deployments/surface/os && bash -n frawo-surface-setup.sh && echo OK
```
Expected: `OK`

- [ ] **Step 4: Commit**

```bash
cd /c/Users/StudioPC/FraWo && git add deployments/surface/os/frawo-surface-setup.sh deployments/surface/os/dateien
git commit -m "🤖 [Claude] Surface-Neuaufbau: Einrichtungsskript + Konfigurationsdateien"
```

---

### Task 4: Probelauf in einer Test-VM (Gate für alles Weitere)

**Files:** keine neuen — testet Task 1–3. Ergebnis wird in Odoo #1558 protokolliert.

**Interfaces:**
- Consumes: `frawo-surface.iso` (Task 2), `frawo-surface-setup.sh` (Task 3), `pruefen.sh` (Task 1)
- Produces: Entscheidung **Weg A freigegeben** oder **nur Weg B** (Odoo-Notiz)

Die Test-VM bekommt die feste MAC `BC:24:11:99:09:90` und per Zuteilung die Adresse **`10.1.0.199`**
(Server-Netz, vom StudioPC erreichbar). Im Folgenden heißt sie `VM=frawo@10.1.0.199`.

- [ ] **Step 1: Zuteilung setzen, VM 990 auf dem OptiPlex anlegen** (UEFI wie der Surface, 6 GB RAM, Netz zunächst **getrennt**)

```bash
ssh -o BatchMode=yes anker-pve 'ssh -o BatchMode=yes root@10.1.0.227 "
cd /root/m1 && python3 ucg.py reserve bc:24:11:99:09:90 10.1.0.199 server surface-test
cp /root/surface-iso/frawo-surface.iso /var/lib/vz/template/iso/frawo-surface-test.iso && chmod 600 /var/lib/vz/template/iso/frawo-surface-test.iso
qm create 990 --name surface-test --memory 6144 --cores 2 --bios ovmf --machine q35 \
  --efidisk0 local-lvm:1,efitype=4m,pre-enrolled-keys=0 --scsihw virtio-scsi-single --scsi0 local-lvm:32 \
  --net0 virtio=BC:24:11:99:09:90,bridge=vmbr0,link_down=1 --ide2 local:iso/frawo-surface-test.iso,media=cdrom \
  --boot order=\"scsi0;ide2\" --ostype l26
qm start 990"'
```
Expected: `bc:24:11:99:09:90 -> 10.1.0.199 (server) bestaetigt`; VM startet vom Abbild (`scsi0` ist leer).

- [ ] **Step 2: Offline-Installation abwarten, dann Netz zuschalten**

Die Installation läuft **ohne Netz** (worst case am Surface). Nach 25 min Netz zuschalten und auf SSH warten:
```bash
sleep 1500
ssh -o BatchMode=yes anker-pve 'ssh -o BatchMode=yes root@10.1.0.227 "qm set 990 --net0 virtio=BC:24:11:99:09:90,bridge=vmbr0"'
ssh-keygen -R 10.1.0.199 >/dev/null 2>&1
for i in $(seq 1 40); do sleep 30; timeout 8 ssh -o BatchMode=yes -o StrictHostKeyChecking=accept-new -o IdentitiesOnly=yes -i ~/.ssh/hs27_ops_ed25519 frawo@10.1.0.199 true 2>/dev/null && { echo "SSH da"; break; }; echo "warte $i"; done
ssh -o IdentitiesOnly=yes -i ~/.ssh/hs27_ops_ed25519 frawo@10.1.0.199 'dpkg -l wpasupplicant | tail -1; sudo -n true && echo SUDO-OK; hostname; sudo -n passwd -S frawo; sudo -n ls /var/log/installer/ | head -3'
```
Expected: `ii  wpasupplicant …` (**offline** aus dem Abbild installiert), `SUDO-OK`, `surface-go`, `frawo L …`,
Installer-Protokolle vorhanden.
Kommt nach weiteren 20 min kein SSH: in der Proxmox-Oberfläche die Konsole von VM 990 ansehen (Installer-Fehler
steht dort) → Fehler beheben, Abbild neu bauen, Step 1 wiederholen.
**Lässt sich Offline-Installation nicht erreichen → Entscheidung „nur Weg B“, Task 6 entfällt.**

- [ ] **Step 3: Einrichtung + Abnahme in der VM**

```bash
cd /c/Users/StudioPC/FraWo/deployments && tar -cf - surface | ssh -o IdentitiesOnly=yes -i ~/.ssh/hs27_ops_ed25519 frawo@10.1.0.199 'sudo -n rm -rf /root/frawo-surface && sudo -n mkdir -p /root/frawo-surface && sudo -n tar -xf - -C /root/frawo-surface --strip-components=1'
ssh -o IdentitiesOnly=yes -i ~/.ssh/hs27_ops_ed25519 frawo@10.1.0.199 'sudo -n bash /root/frawo-surface/os/frawo-surface-setup.sh --vm && sudo -n systemctl reboot'
sleep 150
ssh -o IdentitiesOnly=yes -i ~/.ssh/hs27_ops_ed25519 frawo@10.1.0.199 'sudo -n bash /root/frawo-surface/os/pruefen.sh --vm; echo exit=$?'
```
Expected: alle Punkte `PASS` außer den Netz-Erreichbarkeiten, falls die VM nicht im IoT-Netz hängt (Odoo/HA/Grafana
sind vom LAN aus trotzdem erreichbar → auch `PASS`); `Kein Installationsrest` `PASS`; `exit=0`.
Bei `FAIL`: Skript korrigieren, erneut ausführen (idempotent), commit.

- [ ] **Step 4: Fern-Neuinstallation IN der VM proben** (der eigentliche Weg A)

Die VM läuft jetzt **mit** Netz — das ist hier gewollt: geprüft wird der Loopback-Start samt `toram`, nicht mehr die
Offline-Fähigkeit (die hat Step 2 gezeigt). Vorher das CD-Laufwerk entfernen, damit nur der GRUB-Weg zählt:
```bash
ssh -o BatchMode=yes anker-pve 'ssh -o BatchMode=yes root@10.1.0.227 "qm set 990 --delete ide2"'
ssh -o BatchMode=yes anker-pve 'ssh -o BatchMode=yes root@10.1.0.227 "cat /root/surface-iso/frawo-surface.iso"' | ssh -o IdentitiesOnly=yes -i ~/.ssh/hs27_ops_ed25519 frawo@10.1.0.199 'sudo -n mkdir -p /frawo-install && sudo -n tee /frawo-install/frawo-surface.iso >/dev/null'
ssh -o BatchMode=yes anker-pve 'ssh -o BatchMode=yes root@10.1.0.227 "cat /root/surface-iso/frawo-surface.iso.sha256"' | ssh -o IdentitiesOnly=yes -i ~/.ssh/hs27_ops_ed25519 frawo@10.1.0.199 'sudo -n tee /frawo-install/frawo-surface.iso.sha256 >/dev/null'
scp -o IdentitiesOnly=yes -i ~/.ssh/hs27_ops_ed25519 /c/Users/StudioPC/FraWo/deployments/surface/os/neuinstallation-aktivieren.sh frawo@10.1.0.199:/tmp/
ssh -o IdentitiesOnly=yes -i ~/.ssh/hs27_ops_ed25519 frawo@10.1.0.199 'sudo -n bash /tmp/neuinstallation-aktivieren.sh && sudo -n systemctl reboot'
ssh-keygen -R 10.1.0.199 >/dev/null 2>&1
for i in $(seq 1 90); do sleep 30; if timeout 8 ssh -o BatchMode=yes -o StrictHostKeyChecking=accept-new -o IdentitiesOnly=yes -i ~/.ssh/hs27_ops_ed25519 frawo@10.1.0.199 'test ! -e /opt/frawo-portal && echo FRISCH' 2>/dev/null; then break; fi; echo "warte $i"; done
```
Expected vor dem Neustart: `frawo-surface.iso: OK`, `next_entry=frawo-neu`. Danach: `FRISCH` (das in Step 3
eingerichtete Portal ist weg → die VM hat sich **selbst neu installiert**). **Das ist der Nachweis für Weg A.**
Kommt `FRISCH` nicht, aber das alte System antwortet (Portal noch da) → Loopback-Start gescheitert, Konsole prüfen.
Hängt der Installer (Platte „in use“ o. ä., in der Konsole sichtbar) → Entscheidung „nur Weg B“.

- [ ] **Step 5: VM entfernen, Ergebnis protokollieren**

```bash
ssh -o BatchMode=yes anker-pve 'ssh -o BatchMode=yes root@10.1.0.227 "qm stop 990; qm destroy 990 --purge; rm -f /var/lib/vz/template/iso/frawo-surface-test.iso; cd /root/m1 && python3 ucg.py forget bc:24:11:99:09:90"'
ssh-keygen -R 10.1.0.199 >/dev/null 2>&1
```
Expected: `bc:24:11:99:09:90 vergessen`.
Odoo-Notiz an #1558 (`subtype=note`): Ergebnis Step 2–4, Entscheidung A/B.

---

### Task 5: Sichern und feste Adresse

**Files:**
- Create: `deployments/surface/os/sichern.sh`

**Interfaces:**
- Produces: ProDesk `/mnt/data_family/backups/surface-20260922/surface.tar.gz` (+ `.sha256`);
  StudioPC-lokal **nicht**. AnyDesk-Dateien für Task 7 unter ProDesk `/mnt/data_family/backups/surface-20260922/anydesk/`.

- [ ] **Step 1: Skript** — `deployments/surface/os/sichern.sh`:

```bash
#!/bin/bash
# Sichert Home-Ordner, AnyDesk-Kennung und Portal des Surface auf den ProDesk. Laeuft auf dem StudioPC (Git Bash).
set -euo pipefail
S="ssh -o BatchMode=yes -o IdentitiesOnly=yes -i $HOME/.ssh/hs27_ops_ed25519 frawo@10.4.0.38"
P="ssh -o BatchMode=yes pve"
Z=/mnt/data_family/backups/surface-20260922
$P "mkdir -p $Z/anydesk && chmod 700 $Z"
$S 'sudo -n tar -C / -czf - home etc/anydesk' | $P "cat > $Z/surface.tar.gz"
$S 'sudo -n tar -C /etc/anydesk -cf - service.conf system.conf' | $P "tar -xf - -C $Z/anydesk && chmod 600 $Z/anydesk/*"
$P "cd $Z && sha256sum surface.tar.gz > surface.tar.gz.sha256 && tar -tzf surface.tar.gz > inhalt.txt && wc -l < inhalt.txt"
$P "grep -c -e 'etc/anydesk/service.conf' -e 'homeserver2027-portal/server.py' $Z/inhalt.txt; ls -la $Z/anydesk"
```

- [ ] **Step 2: Ausführen**

```bash
bash -n /c/Users/StudioPC/FraWo/deployments/surface/os/sichern.sh && bash /c/Users/StudioPC/FraWo/deployments/surface/os/sichern.sh
```
Expected: Eintragsanzahl > 1000, Treffer `2`, zwei Dateien in `anydesk/` (Rechte `-rw-------`).
`tar -tzf` ohne Fehler = Archiv lesbar (Rücklese-Nachweis).

- [ ] **Step 3: Feste Adresse am Gateway**

```bash
ssh -o BatchMode=yes anker-pve 'ssh -o BatchMode=yes root@10.1.0.227 "cd /root/m1 && python3 ucg.py reserve d8:c4:97:c6:0e:b0 10.4.0.38 iot surface-go"'
```
Expected: `d8:c4:97:c6:0e:b0 -> 10.4.0.38 (iot) bestaetigt`

- [ ] **Step 4: Commit**

```bash
cd /c/Users/StudioPC/FraWo && git add deployments/surface/os/sichern.sh && git commit -m "🤖 [Claude] Surface-Neuaufbau: Sicherung auf den ProDesk"
```

---

### Task 6: Fern-Neuinstallation am Surface (nur wenn Task 4 = Weg A freigegeben)

**Files:** keine neuen — nutzt `neuinstallation-aktivieren.sh` aus Task 2 (im Probelauf bewährt).

**Interfaces:**
- Consumes: `/frawo-install/frawo-surface.iso` + `.sha256` auf dem Zielgerät; Task-5-Sicherung ist erledigt
- Produces: frisch installierter Surface, erreichbar als `frawo@10.4.0.38` mit neuem Host-Schlüssel

- [ ] **Step 1: Vorbedingungen prüfen** — Task 4 hat „Weg A freigegeben“ ergeben, Task 5 Sicherung ist
  rückgelesen, Wolf weiß Bescheid (Surface ist ~30 min weg). Fehlt eins davon: **nicht** weitermachen.

- [ ] **Step 2: Abbild übertragen** (Surface-Platte hat 202 GB frei)

```bash
ssh -o BatchMode=yes anker-pve 'ssh -o BatchMode=yes root@10.1.0.227 "cat /root/surface-iso/frawo-surface.iso"' | ssh -o IdentitiesOnly=yes -i ~/.ssh/hs27_ops_ed25519 frawo@10.4.0.38 'sudo -n mkdir -p /frawo-install && sudo -n chmod 700 /frawo-install && sudo -n tee /frawo-install/frawo-surface.iso >/dev/null'
ssh -o BatchMode=yes anker-pve 'ssh -o BatchMode=yes root@10.1.0.227 "cat /root/surface-iso/frawo-surface.iso.sha256"' | ssh -o IdentitiesOnly=yes -i ~/.ssh/hs27_ops_ed25519 frawo@10.4.0.38 'sudo -n tee /frawo-install/frawo-surface.iso.sha256 >/dev/null'
```

- [ ] **Step 3: Aktivieren und neu starten**

```bash
scp -o IdentitiesOnly=yes -i ~/.ssh/hs27_ops_ed25519 /c/Users/StudioPC/FraWo/deployments/surface/os/neuinstallation-aktivieren.sh frawo@10.4.0.38:/tmp/
ssh -o IdentitiesOnly=yes -i ~/.ssh/hs27_ops_ed25519 frawo@10.4.0.38 'sudo -n bash /tmp/neuinstallation-aktivieren.sh && sudo -n systemctl reboot'
```
Expected vor dem Neustart: `frawo-surface.iso: OK` und `next_entry=frawo-neu`.

- [ ] **Step 4: Rückkehr abwarten** (bis 45 min)

```bash
ssh-keygen -R 10.4.0.38 >/dev/null 2>&1
for i in $(seq 1 90); do sleep 30; if timeout 8 ssh -o BatchMode=yes -o StrictHostKeyChecking=accept-new -o IdentitiesOnly=yes -i ~/.ssh/hs27_ops_ed25519 frawo@10.4.0.38 'hostname; test ! -d /home/frontend && echo FRISCH' 2>/dev/null; then break; fi; echo "warte $i"; done
```
Expected: `surface-go` und `FRISCH`.

- [ ] **Step 5 (nur wenn nach 45 min nichts kommt): Weg B**

Zuerst die billigste Möglichkeit: Wolf steckt den **USB-C-Netzwerkadapter** an (Kabel ins Anker-Lan) — hängt nur
das WLAN, kommt der Surface per DHCP im Arbeitsplatz-Netz hoch (`10.0.0.x`, UCG-Clientliste, MAC `b8:31:b5:41:67:db`).

Hilft das nicht: Stick schreiben. Wolf steckt einen **echten** Stick (≥ 8 GB) in den OptiPlex. Erkennen **nur** über
Seriennummer und Größe (Lehre gefälschter Stick), dann Größe per Schreib-/Lesetest prüfen, dann schreiben:
```bash
ssh -o BatchMode=yes anker-pve 'ssh -o BatchMode=yes root@10.1.0.227 "lsblk -d -o NAME,SIZE,MODEL,SERIAL,TRAN | grep usb"'
# -> Geraet bestimmen, z. B. sdX. Nur fortfahren, wenn TRAN=usb und Groesse plausibel.
ssh -o BatchMode=yes anker-pve 'ssh -o BatchMode=yes root@10.1.0.227 "apt-get install -y f3 >/dev/null; f3probe --destructive --time-ops /dev/sdX"'
# Expected: "Good news: The device ... is the real thing"
ssh -o BatchMode=yes anker-pve 'ssh -o BatchMode=yes root@10.1.0.227 "dd if=/root/surface-iso/frawo-surface.iso of=/dev/sdX bs=4M conv=fsync status=none && sync && cmp -n \$(stat -c %s /root/surface-iso/frawo-surface.iso) /root/surface-iso/frawo-surface.iso /dev/sdX && echo STICK-OK"'
```
Expected: `STICK-OK`. Vor Ort: Stick über USB-C in den Surface, beim Einschalten die **Leiser-Taste** halten →
Installation läuft ohne Eingabe (Starteintrag enthält `autoinstall`, Wartezeit 3 s). Dann weiter mit Step 4.

---

### Task 7: Einrichtung am Surface und Abnahme

**Interfaces:**
- Consumes: Task 3 (Skript), Task 5 (AnyDesk-Sicherung), Tailscale-Auth-Key (einmalig, 1 h gültig, per Tailscale-API)

- [ ] **Step 1: Repo-Stand und AnyDesk-Sicherung auf den Surface**

```bash
cd /c/Users/StudioPC/FraWo/deployments && tar -cf - surface | ssh -o IdentitiesOnly=yes -i ~/.ssh/hs27_ops_ed25519 frawo@10.4.0.38 'sudo -n mkdir -p /root/frawo-surface && sudo -n tar -xf - -C /root/frawo-surface --strip-components=1'
ssh -o BatchMode=yes pve 'tar -C /mnt/data_family/backups/surface-20260922 -cf - anydesk' | ssh -o IdentitiesOnly=yes -i ~/.ssh/hs27_ops_ed25519 frawo@10.4.0.38 'sudo -n mkdir -p /root/anydesk-sicherung && sudo -n tar -xf - -C /root/anydesk-sicherung --strip-components=1 && sudo -n ls /root/anydesk-sicherung'
```
Expected: `service.conf  system.conf`

- [ ] **Step 2: Einrichtung mit Tailscale-Schlüssel** (Schlüssel nur in der Sitzungsvariable, nie in eine Datei)

```bash
TS_AUTHKEY=$(curl -fsS -u "$TAILSCALE_API_KEY:" -X POST https://api.tailscale.com/api/v2/tailnet/-/keys \
  -H 'Content-Type: application/json' \
  -d '{"capabilities":{"devices":{"create":{"reusable":false,"ephemeral":false,"preauthorized":true}}},"expirySeconds":3600}' | python -c "import json,sys;print(json.load(sys.stdin)['key'])")
ssh -o IdentitiesOnly=yes -i ~/.ssh/hs27_ops_ed25519 frawo@10.4.0.38 "sudo -n TS_AUTHKEY='$TS_AUTHKEY' bash /root/frawo-surface/os/frawo-surface-setup.sh && sudo -n rm -rf /frawo-install /root/anydesk-sicherung && sudo -n systemctl reboot"
```
(`TAILSCALE_API_KEY` vorher aus Vaultwarden bzw. der Memory-Referenz in die Sitzung laden.)
Danach alten Tailnet-Eintrag `surface-go-frontend` per API löschen (`DELETE /api/v2/device/{id}`).

- [ ] **Step 3: Abnahme**

```bash
sleep 150; ssh -o IdentitiesOnly=yes -i ~/.ssh/hs27_ops_ed25519 frawo@10.4.0.38 'sudo -n bash /root/frawo-surface/os/pruefen.sh; echo exit=$?'
```
Expected: alle `PASS`, `exit=0`.

- [ ] **Step 4: Prometheus-Messziel** (vorher per Odoo-Notiz mit Jarvis abstimmen — er pflegt die Ziele mit)

In CT155 `/etc/prometheus/prometheus.yml` unter `scrape_configs` ergänzen, vorher sichern:
`pct exec 155 -- sh -c 'cp -n /etc/prometheus/prometheus.yml /etc/prometheus/prometheus.yml.bak-$(date +%Y%m%d)'`
```yaml
  - job_name: node_surface
    static_configs:
      - targets: ['10.4.0.38:9100']
        labels:
          instance: surface-go
```
```bash
ssh -o BatchMode=yes anker-pve 'pct exec 155 -- /usr/local/bin/prometheus-neu-laden.sh && pct exec 155 -- sh -c "sleep 30; curl -s localhost:9090/api/v1/query --data-urlencode query=up{job=\"node_surface\"}"'
```
Expected: `reload_successful = 1` und `"value":[…,"1"]`. Gleiche Änderung in `deployments/monitoring/prometheus.yml`, commit.

- [ ] **Step 5: Abbild aufräumen** (enthält das WLAN-Passwort)

```bash
ssh -o BatchMode=yes anker-pve 'ssh -o BatchMode=yes root@10.1.0.227 "shred -u /root/surface-iso/autoinstall.yaml; rm -f /root/surface-iso/frawo-surface.iso*; ls /root/surface-iso"'
```
Expected: nur noch das Original-Ubuntu-Abbild und `SHA256SUMS`.

---

### Task 8: Abschluss

- [ ] **Step 1: Spec nachziehen** — in `DOCS/specs/2026-09-22-surface-neuaufbau-design.md` die Planentscheidung
  (Server-Abbild, GNOME per Skript) und das Ergebnis des Probelaufs eintragen; Abnahme-Kästchen abhaken.
- [ ] **Step 2: Memory** `reference_frawo_surface_touchboard.md` neu schreiben: Benutzer `anzeige`/`frawo`,
  Portal unter `/opt/frawo-portal` (`frawo-portal.service`), Zugang per `hs27_ops`, Neuaufbau = `baue-iso.sh` + Task 6/7.
- [ ] **Step 3: Odoo #1558** — Notiz mit Ergebnis (was, wo, wie geprüft), `@Jarvis` per `partner_ids=[124]` zur
  Gegenprüfung; Stufe bleibt „In Arbeit“ bis Review ✅ und **Wolfs Sichtprüfung** (Tastatur, Vollbild, AnyDesk).
- [ ] **Step 4: Zeiterfassung** — `account.analytic.line` auf Task 1558, `employee_id` 11, ehrlich geschätzt.
- [ ] **Step 5: Commit + Push**

```bash
cd /c/Users/StudioPC/FraWo && git add DOCS/specs/2026-09-22-surface-neuaufbau-design.md deployments/monitoring/prometheus.yml
git commit -m "🤖 [Claude] Surface-Neuaufbau abgeschlossen: Abnahme gruen" && git push origin main
```
