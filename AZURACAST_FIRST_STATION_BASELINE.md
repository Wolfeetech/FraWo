# AzuraCast First Station Baseline

## Ziel

Dieses Dokument haelt die verbindlichen Basiswerte fuer die erste produktive interne AzuraCast-Station auf dem `radio-node` fest.

Stand heute:

- der AzuraCast-Grundsetup ist abgeschlossen
- `http://radio.hs27.internal` liefert die Login-Seite
- die Status-API ist live
- die erste Station existiert jetzt als `FraWo - Funk` mit Shortcode `frawo-funk`
- `GET /api/nowplaying` liefert bereits einen laufenden Track
- ein direkt am Pi steckendes USB-Medium ist als erste Musikquelle eingebunden
- das Host-Medienlayout auf dem Pi ist bereits vorbereitet:
  - `/srv/radio-library/incoming`, `music`, `playlists`
  - `/srv/radio-assets/ids`, `jingles`, `shows`, `staging`, `sweepers`

## Verbindliches Profil fuer die erste Station

### Systemweite Basis

- Site Name: `FRAWO Studio Radio`
- Site Base URL: `http://radio.hs27.internal`
- Zeitzone: `Europe/Zurich`
- oeffentliche Ziel-URL spaeter: `https://radio.frawo.studio`

Wichtig:

- Bis zum echten Public-Edge-Rollout bleibt die interne URL `http://radio.hs27.internal` kanonisch.
- Erst mit Domain, TLS und Edge-Rollout wird auf `https://radio.frawo.studio` umgestellt.

### Erste Station

- Live-Station Name: `FraWo - Funk`
- Live-Shortcode: `frawo-funk`
- Website URL intern: `http://radio.hs27.internal`
- Time Zone: `Europe/Zurich`
- AutoDJ: `enabled`
- Broadcasting Frontend: `Icecast`
- Station Backend: `Liquidsoap`
- Public Pages: `enabled`
- Public Listed on Directories / YP: `disabled`

### Port-Strategie

- Fuer die erste Station die von AzuraCast automatisch vorgeschlagenen Ports uebernehmen.
- Auf dem Pi-Ressourcenprofil keine manuellen Sonderport-Schemata erzwingen.
- Spaeter bei Public Edge nur ueber `radio.frawo.studio`, nicht ueber rohe Port-Bookmarks arbeiten.

## Low-Resource-Regeln nach dem Stationsaufbau

Diese Regeln sind auf dem kleinen Pi Pflicht:

1. `ReplayGain` nicht on-the-fly berechnen lassen.
2. `AutoCue` zuerst deaktiviert lassen.
3. `Audio Post-Processing` zuerst deaktiviert lassen.
4. Keine zweite Station anlegen, solange die erste Station noch nicht stabil unter Last laeuft.
5. Medien nicht unkontrolliert auf die Root-Disk hochladen, sondern ueber den kuratierten USB-/spaeteren `RadioLibrary`- und `RadioAssets`-Pfad fuehren.

## Medienstruktur fuer die erste Betriebsphase

Die erste Station arbeitet in der ersten Betriebsphase mit drei kuratierten Host-Pfaden:

- aktueller Live-Importpfad
  - `/srv/radio-library/music-usb/yourparty.radio`
  - direkt angeschlossener USB-Musikbestand fuer die erste Betriebsphase

- `RadioLibrary`
  - Songs, aus denen Playlists gebaut werden
  - spaeterer kuratierter Kanon fuer den eigentlichen Musikbestand
- `RadioAssets`
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
- der aktuelle USB-Musikpfad ist in AzuraCast sichtbar und AutoDJ liefert einen echten Titel
- die Low-Ressource-Regeln in der Station eingehalten sind

## Quellen

- AzuraCast Docker Installation:
  - https://www.azuracast.com/docs/getting-started/installation/docker/
- AzuraCast Settings:
  - https://www.azuracast.com/docs/getting-started/settings/
- AzuraCast Optimizing:
  - https://www.azuracast.com/docs/help/optimizing/
