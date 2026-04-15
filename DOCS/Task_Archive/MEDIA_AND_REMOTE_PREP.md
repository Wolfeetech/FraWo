# Install Media and Remote Access Prep

## Zweck

Dieses Runbook haelt den sauberen Vorbereitungsstand fuer:

- `Raspberry Pi 4` als spaeteren Radio-/AzuraCast-Node
- `Surface Go` als Clean-Rebuild-Ziel fuer den Frontend-Knoten
- `ZenBook` fuer spaeteren Remote-Zugriff via AnyDesk

## Aktuell erkannte Wechseldatentraeger

| Device | Groesse | Erkennung | Aktueller Stand | Ziel |
| --- | --- | --- | --- | --- |
| `/dev/mmcblk0` | `29.7G` | SD-Karte im Slot | Ubuntu-Pi-Image ist bereits geflasht; `system-boot` wurde auf `radio-node` First-Boot-Seed umgestellt | Raspberry Pi 4 Installationsmedium |
| `/dev/sdd` | `7.7G` | Generic USB, Label `PVE` | altes Proxmox-Bootmedium | dedizierter blauer Install-/Image-Stick mit `Ventoy` |
| `/dev/sdc` | `14.4G` | Kingston DataTraveler 2.0 | derzeit noch Uebergangsinhalt vom frueheren Surface-Prep | spaeter mobiler `Favorites`-Stick |

## Entscheidungen

1. `Raspberry Pi 4`
   - Ziel-OS: `Ubuntu Server 22.04.5 LTS ARM64 preinstalled for Raspberry Pi`
   - Zielmedium: `/dev/mmcblk0`
   - Begruendung: passt zur bisherigen Homeserver-Planung fuer den spaeteren dedizierten Radio-Node
2. `Surface Go`
   - Ziel-OS: `Ubuntu Desktop 24.04.4 LTS amd64`
   - Zielmedium ist jetzt bewusst der blaue `8G`-Stick `/dev/sdd`
   - Rolle: dedizierter Install-/Image-Stick mit `Ventoy`
3. `Kingston Favorites Stick`
   - Zielmedium: `/dev/sdc`
   - Rolle: mobiler Favoriten-Stick fuer Lieblings-Tracks und Playlist-Transfers
   - Dateisystem-Ziel: `exFAT`
   - kuratierte Ordner: `Favorites`, `Playlists`, `To_Radio`, `Archive`
4. `ZenBook`
   - AnyDesk ist auf dem lokalen ZenBook inzwischen installiert und aktiv
   - aktueller lokaler Desktop ist `Ubuntu 24.04.4 LTS` mit `X11`, also prinzipiell passend fuer AnyDesk

## Vorbereitete Download-Artefakte

Standardpfad:

`/home/wolf/Downloads/Homeserver2027/install-media`

Erwartete Dateien:

- `surface/ubuntu-24.04.4-desktop-amd64.iso`
- `surface/SHA256SUMS`
- `rpi/ubuntu-22.04.5-preinstalled-server-arm64+raspi.img.xz`
- `rpi/SHA256SUMS`
- `tools/ventoy-1.1.10-linux.tar.gz`
- `tools/sha256.txt`
- `remote/anydesk_8.0.0_amd64.deb`

Wenn die grosse Surface-ISO spaeter separat oder erneut fortgesetzt werden soll:

```bash
make surface-iso-fetch
```

## Operator-Schritte

### Raspberry Pi SD-Karte beschreiben

Destruktiv:

- loescht den kompletten Inhalt von `/dev/mmcblk0`

Befehl:

```bash
sudo ./scripts/flash_rpi_sd_card.sh /dev/mmcblk0
```

### Raspberry Pi First-Boot-Seed schreiben

Direkt nach dem Flashen und noch bevor der Pi das erste Mal bootet, kann die SD-Karte fuer den spaeteren Remote-Betrieb vorbereitet werden.

Das schreibt auf die Boot-Partition:

- Hostname `radio-node`
- Admin-User `wolf`
- den SSH-Public-Key des aktuellen ZenBook-Operators
- DHCP fuer `eth0`
- Basispakete fuer den ersten Remote-Zugriff

Befehl:

```bash
sudo ./scripts/prepare_rpi_firstboot_seed.sh /dev/mmcblk0
```

Danach ist der beabsichtigte Ablauf:

1. SD-Karte flashen
2. First-Boot-Seed schreiben
3. Pi booten und ans LAN haengen
4. Codex/Gemini uebernehmen den Rest vom ZenBook aus via `SSH` und `ansible/playbooks/bootstrap_raspberry_pi_radio.yml`

Live-Stand vom `2026-03-19`:

- die SD-Karte wurde bereits auf den Ubuntu-Pi-Partitionsstand `system-boot` / `writable` gebracht
- `user-data`, `network-config` und `meta-data` wurden bereits auf `radio-node` umgeschrieben
- die Originale wurden als `*.orig` gesichert
- der Pi wurde danach erfolgreich gebootet, per `SSH` und `Tailscale` integriert und host-seitig fuer AzuraCast vorbereitet
- AzuraCast laeuft inzwischen intern auf dem Pi; `radio.hs27.internal` zeigt aktuell auf die Setup-Seite

### USB-Rollen in einem Schritt vorbereiten

Destruktiv:

- loescht den kompletten Inhalt von `/dev/sdd`
- loescht den kompletten Inhalt von `/dev/sdc`

Ergebnis:

- `/dev/sdd` wird der dedizierte `Ventoy`-Image-Stick
- `/dev/sdc` wird ein sauberer `exFAT`-Favorites-Stick

Befehl:

```bash
sudo ./scripts/prepare_usb_stick_roles.sh /dev/sdd /dev/sdc
```

### Surface-Installer-Stick vorbereiten

Wenn nur ein einzelnes Surface-Installmedium gebraucht wird:

```bash
sudo ./scripts/prepare_surface_usb_ventoy.sh /dev/sdd
```

Die Surface-spezifische Einzelvorbereitung bleibt intern als Hilfsskript bestehen, ist aber nicht mehr der bevorzugte Zielzustand fuer `/dev/sdc`.

## Surface-Strategie

Beim Surface wird bewusst nicht versucht, die gesamte Desktop-Installation blind vorab in den USB-Stick "hinein zu backen".

Warum:

- der Desktop-Rebuild ist hardware- und benutzernaeher als ein Headless-Pi
- eine vollautomatische Desktop-Autoinstall wuerde lokale Admin-Zugangsdaten vorab fest verdrahten muessen
- der professionelle Standard ist hier: saubere Grundinstallation, danach uebernimmt der vorbereitete Remote-Bootstrap

Das heisst praktisch:

1. Ubuntu Desktop 24.04 sauber installieren
2. LAN sicherstellen
3. danach uebernimmt Codex/Gemini den Rest ueber den vorbereiteten Post-Install-Pfad

## Wichtiger Kapazitaetshinweis

- `/dev/sdd` mit `7.7G` reicht fuer `Ventoy` plus genau ein grosses Ubuntu-Desktop-ISO praktisch gerade so.
- Als dedizierter einzelner Install-/Image-Stick ist `/dev/sdd` akzeptabel.
- `/dev/sdc` wird nicht mehr als Install-Stick geplant, sondern als mobiler Favorites-Stick.

### AnyDesk auf dem ZenBook installieren

Destruktiv ist das nicht, aber es braucht `sudo`. Dieser Schritt ist auf dem aktuellen ZenBook bereits erfolgreich gelaufen; die Befehle bleiben fuer Reinstall oder Wiederherstellung dokumentiert.

Standard-Installation:

```bash
sudo ./scripts/install_anydesk_zenbook.sh
```

Wenn gleich ein Passwort fuer unbeaufsichtigten Zugriff gesetzt werden soll:

```bash
sudo ANYDESK_PASSWORD='HIER-EIN-STARKES-NEUES-PASSWORT' ./scripts/install_anydesk_zenbook.sh
```

## Nach dem Operator-Schritt uebernimmt Codex/Gemini wieder

- Pi-SD-Karte:
  - Einbindung des Raspberry Pi in Inventar, Tailscale- und Radio-Plan
- Surface-Stick:
  - Surface-Rebuild-Pfad weiterziehen und Post-Install-Baseline anwenden
- AnyDesk:
  - Verifikation, Dokumentation und sichere Remote-Betriebsnotiz
