# Jellyfin Operations

## Zweck

Jellyfin ist der interne Medienserver fuer Musik und spaeter weitere Medien.

## Zugriff

- `http://media.hs27.internal`
- intern direkt `192.168.2.20:8096`

## Normalbetrieb

- SMB-Bibliothek ist die produktive Medienquelle
- Benutzerprofile `Wolf`, `Franz`, `TV Wohnzimmer` bleiben getrennt
- neue Clients bewusst hinzuf?gen

## T?gliche Checks

- UI erreichbar
- Bibliothek sichtbar
- Wiedergabe auf Testclient funktioniert
- keine Rueckfaelle auf alte lokale Bootstrap-Pfade

## Nie tun

- keine Medien wieder lokal am Toolbox-Container verteilen
- keine unkontrollierten Scan-/Pfadwechsel im Live-Betrieb

## Eskalation

- bei fehlenden Medien zuerst SMB-Sichtbarkeit und Bind-Mount pr?fen
