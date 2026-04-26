# Radio Node — Agent Handoff

Stand: 2026-04-27

## Was ist der Radio Node

Raspberry Pi 4 als mobile Audio-Workstation für FraWo:

- Analog Line-In (USB Audio Interface) → Live-Stream + lokale Aufnahme
- AzuraCast (Docker) als Stream-Server
- Tailscale für VPN-Konnektivität von überall (Hotspot-Betrieb)
- Headless — kein Monitor, alles per SSH / Web-Dashboard steuerbar

---

## Aktueller Status (Stand 2026-04-27)

### Netz

- Pi läuft, IP vom UCG erhalten: **`10.3.0.7`** (Anker-DMZ-Radio VLAN)
- MAC: `e4:5f:01:b0:a7:0b` (Raspberry Pi Trading — bestätigt)
- cloud-init läuft aktiv (Package-Download sichtbar im UCG, ~18 MB Traffic)
- Tailscale noch nicht gejoint (cloud-init runcmd läuft nach packages)
- Tailscale Auth-Key aktiv, join passiert automatisch wenn packages fertig

### SD-Karte

- Ubuntu Server 22.04 LTS arm64 für Raspberry Pi 4
- user-data: korrekt, kein BOM, `#cloud-config` Zeile 1
- instance-id: `homeserver2027-radio-node-v4`

### Was cloud-init einrichtet (läuft gerade)

- User `wolf` mit 4 SSH Keys
- Packages: openssh-server, docker.io, cifs-utils, avahi-daemon, jq, gnupg, curl, ca-certificates, unattended-upgrades, apt-transport-https
- Verzeichnisse: `/opt/homeserver2027/radio-node`, `/srv/radio-library/*`, `/srv/radio-assets/*`
- SSH-Hardening Drop-in, sudoers
- Tailscale install + `tailscale up --authkey=... --hostname=radio-node --accept-routes`

---

## SSH-Zugang

```bash
# Nach Tailscale-Join — IP aus: tailscale status | grep radio-node
ssh wolf@<tailscale-ip>

# SSH Key auf wolf-surface:
# Privat:  C:\Users\Admin\.ssh\id_ed25519
# Publik:  wolf@wolf-surface-2026  (NEUES KEY-PAAR — alter Key war korrupt)
```

### Alle autorisierten Keys auf dem Pi

| Key | Maschine |
|---|---|
| `wolf@wolf-surface-2026` | Surface (diese Maschine) — primär |
| `studiopc@wolfstudioPC` | Studio PC |
| `zenbook_admin` | ZenBook |
| `Admin@Surface-Work` | Surface Work |

---

## Nächste Schritte nach Tailscale-Join

### 1 — Tailscale-IP in Inventory eintragen

Datei: `ansible/inventory.ini`

```ini
[raspberry_pi_radio]
radio-node ansible_host=<tailscale-ip> ansible_user=wolf
```

### 2 — AzuraCast einrichten

```bash
ssh wolf@<tailscale-ip>
bash -s < scripts/radio_node_post_boot_setup.sh
```

Script `scripts/radio_node_post_boot_setup.sh` erledigt:

- 2 GB Swap anlegen (Pi 4 braucht das für AzuraCast)
- Docker Compose sicherstellen
- AzuraCast Stable installieren (unattended)
- ffmpeg installieren
- Live-Capture Systemd-Service registrieren (noch nicht starten)

### 3 — AzuraCast Web-UI

```
http://<tailscale-ip>/
```

- Station `frawo-funk` anlegen (Shortcode: `frawo-funk`)
- Live Broadcasting aktivieren
- Source-Password notieren

### 4 — Live Capture aktivieren

```bash
# Source-Password eintragen:
sudo nano /etc/radio-live-capture.env
# ICECAST_SOURCE_PASSWORD=<password aus AzuraCast>
# AUDIO_DEVICE=hw:1,0  (Behringer UCA202 oder prüfen mit: arecord -l)

sudo systemctl enable --now radio-live-capture
```

### 5 — WiFi für Hotspot-Betrieb

```bash
sudo nmcli dev wifi connect "<SSID>" password "<PW>"
```

---

## Architektur: Mobile Streaming

```
[Plattenspieler / Mixer]
        | Line Out (Cinch)
        v
[USB Audio Interface]   <- Behringer UCA202 empfohlen
        | USB
        v
[Raspberry Pi 4]  <->  [Tailscale VPN]  <->  Internet
   |-- ffmpeg (ALSA capture + encode)           |
   |     |-- -> AzuraCast Live Broadcast   [Hotspot 4G/5G]
   |     `-- -> /srv/radio-library/recordings/
   `-- AzuraCast (Docker, Port 80)
         `-- Stream: /radio/listen/frawo-funk/radio.mp3
```

Zuhörer erreichen den Stream via:

- Intern: `http://<tailscale-ip>/radio/listen/frawo-funk/radio.mp3`
- Extern (geplant): Tailscale Funnel oder öffentlicher Relay

---

## Relevante Repo-Dateien

| Datei | Inhalt |
|---|---|
| `ansible/inventory/host_vars/raspberry_pi_radio.yml` | Pi-Konfiguration (Pfade, Shortcuts) |
| `ansible/playbooks/prepare_raspberry_pi_azuracast_host.yml` | AzuraCast-Vorbereitung (Ansible) |
| `ansible/playbooks/deploy_raspberry_pi_azuracast.yml` | AzuraCast-Install (Ansible) |
| `ansible/playbooks/tune_raspberry_pi_azuracast_resources.yml` | Pi-spezifische Ressourcen-Limits |
| `scripts/radio_node_post_boot_setup.sh` | Post-Boot Setup (Shell, kein Ansible nötig) |
| `scripts/rpi_radio_readiness_check.sh` | Readiness-Check via SSH |
| `ansible/inventory.ini` | Tailscale-IP nach Boot eintragen |

---

## Tailscale

- Auth-Key: `tskey-auth-kwxioQ1K9111CNTRL-vNfdYbHeDP8PC1TLvff6Q8xVjB12Ftfae` (gültig bis 2026-07-25)
- Tailnet: `w.prinz1101@gmail.com`
- Hostname im Tailscale: `radio-node`
- Diese Maschine (wolf-surface): `100.79.103.59`
- Proxmox: `100.69.179.87`
- Toolbox: `100.82.26.53`

---

## Offene Punkte

- [ ] Tailscale-IP nach Join in `ansible/inventory.ini` eintragen
- [ ] AzuraCast via `radio_node_post_boot_setup.sh` installieren
- [ ] Station `frawo-funk` in AzuraCast einrichten
- [ ] Live-Capture Service Source-Password eintragen + aktivieren
- [ ] USB Audio Interface anschließen + Device prüfen (`arecord -l`)
- [ ] WiFi / Hotspot-Konfiguration nach erstem SSH-Login
- [ ] `package_upgrade: true` aus user-data entfernen (nach erstem Boot unnötig)
- [ ] Tailscale Funnel für externen Stream-Zugang (optional)
- [ ] VLAN 103 Migration im UCG (geplanter Endzustand laut Inventory)
