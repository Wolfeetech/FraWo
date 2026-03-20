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
- UI-basierte Erstkonfiguration ist moeglich

## Verifizierter Ist-Stand

- `toolbox-media-check` ist gruen
- `media.hs27.internal` liefert aktuell `HTTP 302`
- `192.168.2.20:8096` liefert aktuell `HTTP 302`
- `100.99.206.128:8449` liefert aktuell `HTTP 302`
- systemd-Service fuer den Medienstack ist `enabled` und `active`
- die Bibliotheks-Stammverzeichnisse sind auf der Toolbox angelegt

## Naechster Operativer Schritt

- Jellyfin im Browser einmal initialisieren
- den ersten Admin anlegen
- die vorbereiteten Bibliotheken anbinden
- danach die ersten Thomson-/Google-TV-Clients verbinden
