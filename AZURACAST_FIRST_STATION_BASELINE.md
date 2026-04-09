# AzuraCast First Station Baseline

## Ziel

Dieses Dokument haelt die verbindlichen Basiswerte fuer die erste produktive interne AzuraCast-Station auf dem `radio-node` fest.

Stand heute:

- der AzuraCast-Grundsetup ist abgeschlossen
- `http://radio.hs27.internal` liefert die Login-Seite
- der persoenliche Super-Administrator ist `wolf@frawo-tech.de`
- die Status-API ist live
- die erste Station existiert als `FraWo - Funk` mit Shortcode `frawo-funk`
- `GET /api/nowplaying` liefert bereits einen laufenden Track
- die Station ist live online und AutoDJ spielt aus der SMB-Bibliothek
- das Host-Medienlayout auf dem Pi ist vorbereitet:
  - `/srv/radio-library/incoming`, `music`, `playlists`
  - `/srv/radio-assets/ids`, `jingles`, `shows`, `staging`, `sweepers`
- der produktive Zielpfad fuer Musik ist jetzt der SMB-Mount:
  - `/srv/radio-library/music-network/yourparty_Libary`
- die SMB-Integrationschecks laufen von diesem Admin-PC reproduzierbar ueber den Proxmox-/Toolbox-Fallback
- die USB-Quellbibliothek ist vollstaendig in die SMB-Zielbibliothek gespiegelt

## Verbindliches Profil fuer die erste Station

### Systemweite Basis

- Site Name: `FRAWO Studio Radio`
- Site Base URL: `http://radio.hs27.internal`
- Zeitzone: `Europe/Zurich`
- oeffentliche Ziel-URL spaeter: `https://radio.frawo-tech.de`

### Erste Station

- Live-Station Name: `FraWo - Funk`
- Live-Shortcode: `frawo-funk`
- Website URL intern: `http://radio.hs27.internal`
- Time Zone live: `UTC`
- Zielwert spaeter: `Europe/Zurich`
- AutoDJ: `enabled`
- Broadcasting Frontend: `Icecast`
- Station Backend: `Liquidsoap`
- Public Pages: `enabled`
- Public Listed on Directories / YP: `disabled`

## Low-Resource-Regeln nach dem Stationsaufbau

1. `ReplayGain` nicht on-the-fly berechnen lassen.
2. `AutoCue` zuerst deaktiviert lassen.
3. `Audio Post-Processing` zuerst deaktiviert lassen.
4. Keine zweite Station anlegen, solange die erste Station noch nicht stabil unter Last laeuft.
5. Medien nicht unkontrolliert auf die Root-Disk hochladen, sondern ueber den zentralen SMB-Pfad und die kuratierten `RadioLibrary`-/`RadioAssets`-Pfade fuehren.

## Medienstruktur fuer die erste Betriebsphase

Die erste Station arbeitet mit drei klaren Medienpfaden:

- Live-Importpfad:
  - `/srv/radio-library/music-network/yourparty_Libary`
- `RadioLibrary`:
  - Songs, aus denen Playlists gebaut werden
  - lokaler Arbeits- und Kurationspfad auf dem Pi
- `RadioAssets`:
  - Jingles
  - IDs
  - Sweepers
  - vorbereitete Sendungen

## Definition of Done

Die erste Stationsbasis gilt als sauber, wenn:

- `radio.hs27.internal` auf die Login-Seite oder das Dashboard fuehrt
- genau eine Station `FraWo - Funk` existiert
- `GET /api/status` liefert `200`
- `GET /api/nowplaying` liefert mindestens einen Stationseintrag
- der SMB-Musikpfad ist in AzuraCast sichtbar und AutoDJ liefert einen echten Titel
- der USB-Bestand ist vollstaendig auf die SMB-Zielbibliothek gespiegelt
- die Low-Ressource-Regeln in der Station eingehalten sind
- der alte USB-Zwischenpfad ist nicht mehr produktive Source of Truth
