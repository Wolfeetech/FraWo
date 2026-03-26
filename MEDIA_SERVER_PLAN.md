# Media Server Plan

## Ziel

Dieses Dokument beschreibt den produktiven Medienpfad fuer Homeserver 2027.

Ziel ist ein sauberer, gemeinsamer Medienbestand fuer:

- Jellyfin auf `CT 100 toolbox`
- AzuraCast auf `raspberry_pi_radio`
- Windows- und Admin-Clients ueber SMB/UNC

## Aktueller Standard

- Plattform fuer Wiedergabe: `CT 100 toolbox`
- Software: `Jellyfin`
- Interne URL: `http://media.hs27.internal`
- Direkte LAN-URL fuer TV-Apps: `http://192.168.2.20:8096`
- Mobiler Tailscale-Pfad: `http://100.99.206.128:8449`
- Kanonische Musikquelle: `\192.168.2.30\Media\yourparty_Libary`
- Toolbox-Mount-Ziel: `/srv/media-library/music-network/yourparty_Libary`

## Warum Jellyfin

- gute Android-TV-/Google-TV-Unterstuetzung
- sinnvoller interner Wiedergabepfad ohne Public Edge
- klare Trennung zu AzuraCast als Radiosystem

## Trennung zu Radio

- `AzuraCast` auf `radio-node` bleibt fuer Radio, AutoDJ und Sendelogik zustaendig
- `Jellyfin` auf `toolbox` ist fuer On-Demand-Medienwiedergabe
- beide Systeme sollen denselben SMB-Medienbestand lesen, aber nicht dieselbe Anwendungslogik teilen

## Verbindliche Bibliotheksstruktur

### Toolbox lokal
- `/srv/media-library/movies`
- `/srv/media-library/shows`
- `/srv/media-library/music`
- `/srv/media-library/homevideos`
- `/srv/media-library/music-network/yourparty_Libary`

### Zentraler SMB-Pfad
- `\192.168.2.30\Media\yourparty_Libary\clean`
- `\192.168.2.30\Media\yourparty_Libary\curated`
- `\192.168.2.30\Media\yourparty_Libary\favorites`
- `\192.168.2.30\Media\yourparty_Libary\incoming`
- `\192.168.2.30\Media\yourparty_Libary\quarantine`

## Verifizierter Ist-Stand

- `media.hs27.internal` liefert `HTTP 302 -> /web/`
- `192.168.2.20:8096` liefert `HTTP 302 -> /web/`
- `100.99.206.128:8449` liefert `HTTP 302 -> /web/`
- Jellyfin-Startup-Wizard ist abgeschlossen
- Jellyfin-Profile `Wolf`, `Franz` und `TV Wohnzimmer` sind vorhanden
- der Medienstack auf `CT 100 toolbox` ist aktiv
- der Storage-Node `CT 110` ist live auf `192.168.2.30`
- das Share `\192.168.2.30\Media` ist erreichbar und `yourparty_Libary` existiert
- die aktive Jellyfin-Bibliothek ist jetzt `Musik Netzwerk` auf dem SMB-Pfad `/media/music-network/yourparty_Libary`
- der alte lokale Bootstrap-Bestand `bootstrap-radio-usb` ist auf `CT 100` entfernt

## Operativer Restblock

1. Jellyfin-Zugaenge in den Bitwarden Cloud uebernehmen.
2. Thomson-/Google-TV-Clients anbinden.
3. Optional PIN-Login fuer `Wolf` und `Franz` spaeter direkt im Jellyfin-UI setzen.

## Operative Checks

- Toolbox-SMB-Ziel: `scripts/toolbox_media_sync_check.sh`
- Radio-/AzuraCast-SMB-Ziel: `scripts/rpi_radio_network_music_check.sh`
- Laufende USB->SMB-Migration: `scripts/media_migration_status.sh`
