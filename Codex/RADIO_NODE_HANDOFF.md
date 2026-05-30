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

### SD-Karte

- **Frisch geflasht** mit Raspberry Pi Imager → Ubuntu Server 22.04 LTS arm64 (Pi 4)
- cloud-init: **minimal** — nur SSH-Keys + Tailscale, kein package_upgrade
- User: `wolf` / PW: `11011995` (für Sudo/Fallback)
- WLAN Fallback: `EasyBox-WLAN` (PW: `11011995`)
- instance-id: `radio-node-v7`
- Boot-Zeit bis SSH erreichbar: ~2–3 Minuten

### Netz

- MAC: `e4:5f:01:b0:a7:0b` (Raspberry Pi Trading — bestätigt)
- UCG-Port: Port 3, Anker-DMZ-Radio VLAN (10.3.0.0/24)
- DHCP-IP im LAN: `10.3.0.7` (erwartet, UCG-reserviert)
- Tailscale-IP: **noch offen** — nach Join: `tailscale status | grep radio-node`

### Was cloud-init einrichtet (minimal, ~2 Min)

- User `wolf` mit 4 SSH-Keys (alle 4 Geräte)
- SSH-Hardening Drop-in
- Tailscale install + `tailscale up --authkey=... --hostname=radio-node --accept-routes --ssh`
- **Tailscale SSH aktiviert** (`--ssh`): Zugang über Tailscale-App ohne Key-Setup

---

## SSH-Zugang

```bash
# Nach Tailscale-Join — IP aus:
tailscale status | grep radio-node

ssh wolf@<tailscale-ip>

# SSH Key auf wolf-surface:
# C:\Users\Admin\.ssh\id_ed25519  (wolf@wolf-surface-2026)
```

### Alle autorisierten Keys auf dem Pi

| Key | Maschine |
|---|---|
| `wolf@wolf-surface-2026` | Surface (primär) |
| `studiopc@wolfstudioPC` | Studio PC |
| `zenbook_admin` | ZenBook |
| `Admin@Surface-Work` | Surface Work |

Zusätzlich: **Tailscale SSH** — jedes Gerät im Tailnet kann ohne Key zugreifen (Tailscale-App → SSH).

---

## Tailscale

- Auth-Key: `tskey-auth-kkWC2C1Xmq11CNTRL-Z51zhJ7YZMcGq4555QEdLct4UjvUYkbyi` (gültig bis 2026-07-26, reusable)
- ~~Alter Key (verbraucht/abgelaufen): `tskey-auth-kwxioQ1K9111CNTRL-vNfdYbHeDP8PC1TLvff6Q8xVjB12Ftfae`~~
- Tailnet: `w.prinz1101@gmail.com`
- Hostname im Tailscale: `radio-node`
- wolf-surface: `100.79.103.59`
- Proxmox-Anker: `100.69.179.87`
- Toolbox: `100.82.26.53`

---

## Nächste Schritte nach Tailscale-Join

### 1 — Tailscale-IP in Inventory eintragen

Datei: `ansible/inventory.ini`

```ini
[raspberry_pi_radio]
radio-node ansible_host=<tailscale-ip> ansible_user=wolf
```

### 2 — Post-Boot Setup ausführen

```bash
ssh wolf@<tailscale-ip>
bash -s < scripts/radio_node_post_boot_setup.sh
```

Script erledigt:

- 2 GB Swap (Pi 4 braucht das für AzuraCast)
- Docker + Docker Compose sicherstellen
- AzuraCast Stable installieren (unattended)
- ffmpeg installieren
- Live-Capture Systemd-Service registrieren

### 3 — AzuraCast Web-UI

```
http://<tailscale-ip>/
```

- Station `frawo-funk` anlegen (Shortcode: `frawo-funk`)
- Live Broadcasting aktivieren
- Source-Password notieren

### 4 — Live Capture aktivieren

```bash
sudo nano /etc/radio-live-capture.env
# ICECAST_SOURCE_PASSWORD=<password aus AzuraCast>
# AUDIO_DEVICE=hw:1,0  (prüfen mit: arecord -l)

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
| `scripts/radio_node_post_boot_setup.sh` | Post-Boot Setup (Swap, AzuraCast, ffmpeg, Live-Capture) |
| `ansible/inventory.ini` | Tailscale-IP nach Boot eintragen |
| `ansible/inventory/host_vars/raspberry_pi_radio.yml` | Pi-Konfiguration |

---

## Bekannte Probleme / Lektionen gelernt

| Problem | Ursache | Fix |
|---|---|---|
| BOM in user-data | PowerShell UTF-8 schreibt BOM | `New-Object System.Text.UTF8Encoding $false` |
| cloud-init läuft nicht erneut | gleiche instance-id | instance-id in meta-data inkrementieren (v1→v2→…) |
| SSH key mismatch | alter Key war korrupt | neues Keypair generiert: `wolf@wolf-surface-2026` |
| Tailscale joinnt nicht | package_upgrade blockiert runcmd 40+ Min | package_upgrade entfernt, minimal cloud-init |
| Tailscale auth-link statt Auto-Join | Key war einmalig/ungültig | neuer reusable Key generiert |
| Proxmox/Toolbox SSH kaputt | neues Surface-Keypair nicht registriert | neuen Public Key in Proxmox-Webkonsole eintragen |

---

## Offene Punkte

- [ ] Tailscale-IP nach Join in `ansible/inventory.ini` eintragen
- [ ] SSH-Key `wolf@wolf-surface-2026` in Proxmox-Anker + Toolbox `authorized_keys` eintragen
- [ ] AzuraCast via `radio_node_post_boot_setup.sh` installieren
- [ ] Station `frawo-funk` in AzuraCast einrichten
- [ ] Live-Capture Service Source-Password eintragen + aktivieren
- [ ] USB Audio Interface anschließen + Device prüfen (`arecord -l`)
- [ ] WiFi / Hotspot-Konfiguration nach erstem SSH-Login
- [ ] Tailscale Funnel für externen Stream-Zugang (optional)
