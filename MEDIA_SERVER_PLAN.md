# Media Server Plan

## Ziel

Dieses Dokument beschreibt den pragmatischen Medienserver-V1 fuer Homeserver 2027.

Ziel ist nicht ein perfektes Endsystem in einem Schritt, sondern ein sofort nutzbarer Mehrwert:

- interner Medienserver
- Google-TV-/Thomson-kompatibler Wiedergabepfad
- sauber getrennt vom Radio-Betrieb auf dem Raspberry Pi

## Gewaehlter V1-Pfad

- Plattform: `CT 100 toolbox`
- Software: `Jellyfin`
- Interne URL: `http://media.hs27.internal`
- Direkte LAN-URL fuer TV-Apps: `http://192.168.2.20:8096`
- Mobiler Tailscale-Interimspfad: `http://100.99.206.128:8449`

## Warum Jellyfin

- gute Android-TV-/Google-TV-Unterstuetzung
- fuer Thomson-Geraete mit Google TV oder Android TV naheliegender Client-Pfad
- intern ohne Public Edge sinnvoll nutzbar
- trennt Medienwiedergabe sauber von AzuraCast

## TV-Integrationspfad

### Google TV / Android TV / Thomson mit Google TV

- Jellyfin-App auf dem TV installieren
- Server-Adresse lokal:
  - `http://192.168.2.20:8096`
- spaeter komfortabler:
  - `http://media.hs27.internal`

### Browser-Fallback

- jeder interne Client:
  - `http://media.hs27.internal`

## Bibliotheksstruktur

Host-Pfad auf der Toolbox:

- `/srv/media-library/movies`
- `/srv/media-library/shows`
- `/srv/media-library/music`
- `/srv/media-library/homevideos`

## Trennung zu Radio

- `AzuraCast` auf `radio-node` bleibt fuer Radio, AutoDJ und Sendelogik zustaendig
- `Jellyfin` auf `toolbox` ist nur fuer Medienwiedergabe
- spaeter koennen beide dieselbe kuratierte Dateibasis nutzen, aber nicht dieselbe Anwendungslogik

## Definition of Done fuer V1

- Jellyfin-Stack laeuft auf der Toolbox
- `media.hs27.internal` liefert die Jellyfin-Oberflaeche
- `192.168.2.20:8096` ist im LAN erreichbar
- mobile Tailscale-Frontdoor auf `:8449` funktioniert
- UI-basierte Erstkonfiguration ist abgeschlossen
- mindestens die Musikbibliothek ist an `/media/music` angebunden

## Verifizierter Ist-Stand

- `toolbox-media-check` ist gruen
- `toolbox-jellyfin-ui-check` bestaetigt jetzt:
  - `StartupWizardCompleted=true`
  - mindestens ein lokaler Benutzer ist in der Jellyfin-Datenbank vorhanden
  - die Musikbibliothek ist an `/media/music` angebunden
- `toolbox-music-scan-issues` liefert jetzt den ersten Qualitaetsbefund fuer den Bootstrap-Bestand:
  - `84` aktuelle `ffprobe`-Fehler im Jellyfin-Log
  - `2` wirklich verdaechtige Dateien
  - der Rest sind vor allem erwartbare Coverbilder und Sidecars
- `toolbox-music-curation-candidates` verdichtet diesen Befund auf den aktuellen Quarantaene-/Kurationspfad:
  - die urspruengliche Problemdatei wurde bereits nach `/srv/media-library/quarantine/bootstrap-review` verschoben
  - derzeit `0` echte Quarantaene-Kandidaten-Dateien
  - derzeit `9` harmlose Sidecars/Coverbilder
  - vorgeschlagener Zielpfad fuer harte Problemfaelle:
    - `/srv/media-library/quarantine/bootstrap-review`
- `toolbox-music-curated-layout` zeigt jetzt die naechste saubere Ausbaustufe:
  - Bootstrap-Bestand gefuellt
  - `curated` Starter-Auswahl live
  - `favorites` Starter-Auswahl live
  - `quarantine` enthaelt aktuell genau `1` verschobene Problemdatei
- neuer Auswahl-Workflow fuer die erste echte Kuration:
  - lokale Manifeste im Workspace:
    - `manifests/media/favorites_paths.txt`
    - `manifests/media/curated_paths.txt`
  - Kandidaten-Report:
    - `make toolbox-music-selection-seed-report`
  - idempotenter Sync:
    - `make toolbox-music-selection-sync`
  - aktueller Zustand: Starter-Manifeste sind in die Live-Manifeste uebernommen und per Sync materialisiert
- `media.hs27.internal` liefert aktuell `HTTP 302`
- `192.168.2.20:8096` liefert aktuell `HTTP 302`
- `100.99.206.128:8449` liefert aktuell `HTTP 302`
- systemd-Service fuer den Medienstack ist `enabled` und `active`
- die Bibliotheks-Stammverzeichnisse sind auf der Toolbox angelegt
- ein wiederholbarer Bootstrap-Sync vom Pi auf die Toolbox ist live:
  - Quelle: `wolf@100.64.23.77:/srv/radio-library/music-usb/yourparty.radio/`
  - Ziel: `/srv/media-library/music/bootstrap-radio-usb/`
  - Dienst: `homeserver2027-media-sync.service`
  - Timer: `homeserver2027-media-sync.timer`
  - schneller Check: `make toolbox-media-sync-check`
  - Fortschritts-Check: `make toolbox-media-bootstrap-progress`
  - Musikbestands-Report: `make toolbox-music-library-report`
- `CT 100 toolbox` wurde fuer diesen Import operativ vergroessert:
  - vorher: `10G` Rootfs, Import lief in `No space left on device`
  - jetzt: effektiv `96G` Rootfs mit wieder ausreichend Platz fuer den Bootstrap-Bestand
- `FRAWO Control` zeigt jetzt auch den laufenden Medienimport ueber `status.json`
- aktueller Musik-Befund aus dem laufenden Bootstrap:
  - Top-Level: `Contents`, `Music Locker Radio - Palms Trax (Mixed)`, `clean`
  - Formate bisher vor allem `mp3`, `flac`, `wav`
  - ein kleiner Rest an restriktiven Verzeichnisrechten bleibt sichtbar und ist der naechste technische Kurationspunkt

## Naechster Operativer Schritt

1. auf Thomson / Google TV die Jellyfin-App mit `http://192.168.2.20:8096` verbinden
2. parallel die Scan-/Kurationslage ueber `make toolbox-music-scan-issues`, `make toolbox-music-curation-candidates` und `make toolbox-music-curated-layout` im Blick behalten
3. den Starter-Stand in `favorites` und `curated` bei Bedarf ueber die Manifeste verfeinern
4. danach weitere Bibliotheken (`Movies`, `Shows`, `Homevideos`) nur bei echtem Bestand anbinden
