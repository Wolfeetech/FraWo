# Radio Operations Standard

## Zweck

Dieses Dokument beschreibt den verbindlichen Betriebsstandard fuer den internen Radio-Betrieb auf `radio-node`.

Es ist bewusst operativ gehalten:

- was heute live ist
- was als temporaerer Zustand geduldet wird
- was als naechster professionelle Schritt folgt

## Aktueller Live-Stand

- Host: `radio-node`
- LAN-IP: `192.168.2.155`
- Tailscale-IP: `100.64.23.77`
- Interne Radio-URL: `http://radio.hs27.internal`
- Mobile Interims-Frontdoor: `http://100.99.206.128:8448`
- Software: `AzuraCast`
- Erste Station:
  - Name: `FraWo - Funk`
  - Shortcode: `frawo-funk`

## Aktueller Betriebsmodus

- Das Radio ist intern live.
- Die erste Station spielt bereits aus dem direkt am Pi angeschlossenen USB-Musikbestand.
- Die Admin-/Control-Flaeche ist aktuell die normale AzuraCast-Login-Seite:
  - `http://radio.hs27.internal/login`

## Geduldeter Uebergangszustand

Der aktuell am Pi steckende USB-Stick ist **nur eine Bootstrap-Musikquelle**.

Das ist im Moment okay, weil:

- der Sender dadurch sofort nutzbar ist
- der Musikbestand schon real abgespielt wird
- der Pi nicht auf eine leere Library zeigt

Das ist **nicht** der Endzustand, weil:

- USB-Sticks mechanisch und betrieblich fragiler sind
- der kuratierte Zielbestand noch nicht sauber getrennt ist
- `RadioLibrary` und `RadioAssets` noch nicht aus dem Rohbestand abgeleitet sind

## Verbindliche Zielstruktur

### RadioLibrary

Unter `/srv/radio-library` liegt der spaetere kuratierte Musikbestand.

Verbindliche Unterstruktur:

- `incoming`
- `music`
- `playlists`

### RadioAssets

Unter `/srv/radio-assets` liegen nicht-musikalische Betriebsinhalte.

Verbindliche Unterstruktur:

- `ids`
- `jingles`
- `shows`
- `staging`
- `sweepers`

## Betriebsregeln

1. Die USB-Quelle bleibt nur solange die Live-Hauptquelle, bis der erste kuratierte Bestand sauber uebernommen ist.
2. Neue Musik wird nicht blind direkt in AzuraCast gekippt, sondern erst sortiert:
   - Rohmaterial -> `incoming`
   - kuratierte Songs -> `music`
   - Verpackung/Elemente -> `RadioAssets`
3. AzuraCast bleibt fuer Playlists, AutoDJ und Sendelogik zustaendig, nicht fuer unstrukturierte Archivpflege.
4. Surface-Frontend und spaetere interne Monitorseiten sollen zwei getrennte Radio-Pfade anbieten:
   - `Radio` = Hoeren / oeffentliche Stationsseite
   - `Radio Control` = AzuraCast-Login / Bedienoberflaeche

## Naechste professionelle Schritte

1. USB-Musikbestand fachlich sichten.
2. Kuration nach `RadioLibrary` und `RadioAssets` beginnen.
3. Mindestens eine saubere Default-Playlist definieren.
4. Jingles / IDs / Sweepers separat ablegen.
5. Erst danach ueber einen spaeteren Wechsel auf SSD- oder Netz-Medienpfad entscheiden.

## Check-Standard

Der schnelle Betriebscheck fuer den Radio-Node ist:

```bash
make radio-ops-check
```

Der Check soll bestaetigen:

- Radio intern erreichbar
- Radio-Control erreichbar
- `nowplaying` liefert Daten
- mindestens eine Station vorhanden
- Station ist online oder klar nachvollziehbar im Betriebszustand
