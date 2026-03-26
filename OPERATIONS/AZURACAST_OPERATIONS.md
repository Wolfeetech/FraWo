# AzuraCast Operations

## Zweck

AzuraCast ist der interne Radio-Betrieb auf dem Raspberry Pi.

## Zugriff

- `http://radio.hs27.internal/login`
- Station: `FraWo - Funk`
- Shortcode: `frawo-funk`

## Normalbetrieb

- SMB-Musikpfad bleibt die produktive Quelle
- genau eine stabile Station zuerst sauber betreiben
- Radio-Assets und Musikpfade klar getrennt halten

## T?gliche Checks

- Login erreichbar
- `GET /api/nowplaying` liefert Daten
- Station ist online
- SMB-Medienpfad im Container sichtbar

## Nie tun

- keine zweite Station vor sauberem Stabilitaetsnachweis
- keine Root-Disk als Hauptmedienquelle nutzen

## Eskalation

- bei Radioausfall zuerst Pi-Ressourcen, SMB-Mount und AzuraCast-Container pr?fen
