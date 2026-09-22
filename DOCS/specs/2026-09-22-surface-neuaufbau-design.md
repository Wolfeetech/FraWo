# Surface Go neu aufsetzen — Entwurf (Teil 1 von 4)

> Stand 22.09.2026 · Claude · von Wolf freigegeben am 22.09.2026 · Odoo-Aufgabe „🖥️ Surface Go neu aufsetzen als reiner Bildschirm“ (#1558)

## Ziel

Der Surface Go wird **frisch und reproduzierbar** aufgesetzt — ohne dass jemand davor stehen muss — und für
drei Aufgaben vorbereitet: **FRAWO HOME CONTROL**, **RADIO CONTROL**, **MONITOR**.
Ein Ersatzgerät soll sich mit denselben Dateien in rund einer Stunde gleich einrichten lassen.

## Gesamtvorhaben — vier Teilprojekte, je mit eigenem Entwurf

| Teil | Inhalt | Status |
|---|---|---|
| **1** | Surface neu aufsetzen und vorbereiten (dieses Dokument) | Entwurf freigegeben |
| 2 | Touchboard auf einen Server + HOME CONTROL | offen |
| 3 | RADIO CONTROL — Radio auf Cast-/HA-Lautsprechern starten/stoppen **über Home Assistant**; der Surface spielt selbst nichts ab | offen |
| 4 | MONITOR — Anlagen-Zustand (Grafana), aktuelle Alarme, Energie & Verbrauch, Kameras (über HA) | offen |

Teil 1 legt nur die **Starter** für die drei Funktionen an. Bis Teil 2–4 fertig sind, zeigen sie auf das
heutige Touchboard bzw. die Grafana-Zentrale.

## Ausgangslage (gemessen 22.09.2026)

| Merkmal | Wert |
|---|---|
| Gerät | Surface Go (1. Generation, 2018, LTE-Modell „1825 Commercial“) |
| CPU / RAM / Platte | Pentium 4415Y · 8 GB · 256 GB NVMe (Toshiba KBG30ZPZ256G) |
| WLAN | Qualcomm QCA6174 (Treiber `ath10k`, im Standard-Kernel) |
| Touch | ELAN9038 (I²C-HID, im Standard-Kernel) |
| Firmware | UEFI, Secure Boot **aus** |
| Heute | Ubuntu 24.04.5, GNOME/Wayland, Benutzer `frawo` + `frontend`, Portal-Dienst lokal |
| Netz | WLAN `FraWo__ioT`, `10.4.0.38`, MAC `d8:c4:97:c6:0e:b0` |
| Kabel-Rückfall | Microsoft-USB-C-Netzwerkadapter, MAC `b8:31:b5:41:67:db` (dem Gateway bekannt) |
| Wartungszugang | SSH-Schlüssel `hs27_ops` (StudioPC) → `frawo@10.4.0.38`, `sudo` ohne Passwort |

Befunde vom 22.09., am selben Tag behoben: Tailscale nahm fremde Routen an (`RouteAll`) und schickte allen
Verkehr ins Server-Netz in den Tunnel; drei Surface-Ausnahmen am Gateway standen **hinter** der Sperre
„IoT → Server“ (20010) und griffen nie.

## Entwurf

### 1. Was auf dem Surface läuft

- **Ubuntu 24.04 LTS Desktop (GNOME, Wayland)**, minimale Installation. Kein fester Kiosk-Modus — Wolf will
  weiterhin andere Programme nutzen können („Kiosk nur, wenn es Einfachheit bringt“).
- **Zwei Benutzer mit klarer Rolle:**
  - `anzeige` — automatische Anmeldung am Bildschirm, **keine** Admin-Rechte
  - `frawo` — nur Wartung, Anmeldung ausschließlich per SSH-Schlüssel, Passwort gesperrt, `sudo`
- **Drei Starter** (Dock + Desktop), jeweils Chromium-App-Fenster
  (`--app=URL --ozone-platform=wayland --enable-wayland-ime`):

  | Starter | Ziel bis Teil 2–4 fertig sind |
  |---|---|
  | FRAWO Home Control | heutiges Touchboard (Portal aus dem Repo, `deployments/surface/`) |
  | FRAWO Radio Control | Touchboard, Reiter `#tab-radio` |
  | FRAWO Monitor | Grafana-Zentrale `http://10.1.0.35:3000/d/frawo-zentrale` |

  Home Control startet nach der Anmeldung automatisch im Vollbild.
- **Bildschirmtastatur:** GNOME-Tastatur (Wischgeste), dazu die zwei bekannten Korrekturen:
  udev-Regel gegen die Phantom-Tastatur (`AT Translated Set 2 keyboard` ignorieren) und Chromium mit
  Wayland-Texteingabe.
- **Netz:** WLAN `FraWo__ioT`; feste Zuteilung `10.4.0.38` am Gateway; Tailscale mit
  `--accept-routes=false` fest eingestellt; SSH-Schlüssel StudioPC (`hs27_ops`) und OptiPlex-root.
- **AnyDesk** wie bisher; die bisherige Kennung wird nach Möglichkeit übernommen
  (Sicherung von `/etc/anydesk/`).
- **Strom und Bildschirm:** kein Ruhezustand (Gerät bleibt erreichbar); Bildschirm geht nach 10 min aus,
  eine Berührung weckt ihn.
  Automatische Sicherheitsupdates, nötiger Neustart um 04:00.
- **Überwachung:** `prometheus-node-exporter` auf dem Surface, Messziel in Prometheus (CT155).
  Fehlt der Surface länger als 30 min, wird das in Grafana sichtbar — **keine** Handy-Meldung
  (kein kritisches Gerät, Wolfs Vorgabe „weniger Meldungen“).

### 2. Ablauf

1. **Vorbereiten (ohne Risiko)**
   - `deployments/surface/os/autoinstall.yaml` — Antwortdatei (Vorlage, **ohne** WLAN-Passwort)
   - `deployments/surface/os/frawo-surface-setup.sh` — Einrichtung nach der Installation (idempotent)
   - WLAN-Passwort wird erst beim Einspielen eingesetzt (aus der Gateway-Konfiguration bzw. Vaultwarden),
     nie im Repo.
   - **Probelauf** des kompletten Ablaufs in einer Test-VM auf dem Anker (Kabelnetz statt WLAN).
2. **Sichern** — Portal-Dateien, `/etc/anydesk/`, Home-Ordner nach
   `ProDesk:/mnt/data_family/backups/surface-20260922/`, **vom ProDesk aus abgeholt** (Server → IoT ist
   erlaubt, umgekehrt nicht). Rücklesen prüfen (Dateianzahl + Prüfsummen).
3. **Fern-Installation (Weg A)**
   - Ubuntu-24.04-Desktop-Abbild + Antwortdatei auf die Surface-Platte.
   - GRUB-Eintrag, der das Abbild per Loopback startet (`toram`, damit die Platte frei wird) und
     `autoinstall` mit der lokalen Antwortdatei setzt.
   - **Speicherfrage, im Probelauf zu messen:** Reichen 8 GB RAM für `toram` mit dem Desktop-Abbild nicht,
     liegt das Abbild stattdessen auf einer eigenen 8-GB-Partition am Plattenende, die die Antwortdatei
     ausdrücklich stehen lässt. Die Entscheidung fällt im Probelauf, nicht am Surface.
   - Aktivierung **einmalig** per `grub-reboot`, dann Neustart.
   - Nach der Installation: WLAN, SSH-Schlüssel, danach `frawo-surface-setup.sh`.
4. **Abnahme** (Abschnitt 4), Protokoll in Odoo, Gegenprüfung durch Jarvis.

**Weg B (Rückfall):** derselbe Inhalt auf einem USB-Stick (≥ 8 GB, echter Stick). Vor Ort: Stick über
USB-C einstecken, beim Einschalten **Leiser-Taste** halten.

### 3. Fehlerfälle

| Fall | Folge | Vorkehrung |
|---|---|---|
| Abbild startet nicht | nichts verloren | Starteintrag gilt nur einmal — nächster Start = altes System |
| Installation bricht ab | Surface startet nicht | Weg B, gleiche Antwortdatei |
| WLAN kommt nach Installation nicht hoch | Surface nicht erreichbar | USB-C-Netzwerkadapter anstecken → Kabelnetz per DHCP |
| Einrichtungsskript scheitert | halb eingerichtet | Skript ist wiederholbar (idempotent), erneut ausführen |

### 4. Abnahme — erst dann ist Teil 1 fertig

- [ ] SSH als `frawo` per Schlüssel; Passwort-Anmeldung abgewiesen
- [ ] `tailscale debug prefs` → `RouteAll: false`; `ip route get 10.1.0.112` → über `10.4.0.1`
- [ ] Vom Surface erreichbar: Odoo `:8069`, Home Assistant `:8123`, Grafana `:3000`
- [ ] Nach Neustart: automatische Anmeldung `anzeige`, Home Control im Vollbild
- [ ] Bildschirmtastatur erscheint beim Antippen eines Textfelds
- [ ] AnyDesk erreichbar
- [ ] Prometheus meldet das Messziel Surface als `up`
- [ ] Wolfs Sichtprüfung vor Ort

## Nicht Teil dieses Entwurfs

- Inhalte von HOME CONTROL, RADIO CONTROL, MONITOR (Teile 2–4)
- Umzug des Portals auf einen Server (Teil 2)
- Die Host-Firewall des Anker lässt das gesamte IoT-Netz `10.4.0.0/24` auf alle Dienste
  (`cluster.fw` Zeile 9, fälschlich „CT/VM-Netz“) — eigener Sicherheitspunkt, gehört zu M1/M5
