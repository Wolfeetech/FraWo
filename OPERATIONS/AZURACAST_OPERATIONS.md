# AzuraCast Operations

## Zweck

AzuraCast ist der interne Radio-Betrieb auf dem Raspberry Pi.

## Zugriff

- `http://radio.hs27.internal/login`
- Station: `FraWo - Funk`
- Shortcode: `frawo-funk`

## Aktueller Betriebsstand

- Radio ist intern erreichbar
- `nowplaying` liefert Daten
- SMTP ist fuer AzuraCast noch nicht fertig, weil der aktuelle Restblocker der SSH-Zugang zu `raspberry_pi_radio` ist
- Mailstandard dafuer bleibt trotzdem derselbe App-SMTP-Pfad wie fuer `Vaultwarden`, `Nextcloud`, `Paperless` und `Odoo`

## Normalbetrieb

- SMB-Musikpfad bleibt die produktive Quelle
- genau eine stabile Station zuerst sauber betreiben
- Radio-Assets und Musikpfade klar getrennt halten

## Taegliche Checks

- Login erreichbar
- `GET /api/nowplaying` liefert Daten
- Station ist online
- SMB-Medienpfad im Container sichtbar
- SMTP erst als gruen markieren, wenn der Pi wieder per SSH administrierbar ist und die App-Konfiguration sichtbar steht

## Nie tun

- keine zweite Station vor sauberem Stabilitaetsnachweis
- keine Root-Disk als Hauptmedienquelle nutzen

## Eskalation

- bei Radioausfall zuerst Pi-Ressourcen, SMB-Mount und AzuraCast-Container pruefen
- bei offenem SMTP-Status zuerst den SSH-Zugang zu `raspberry_pi_radio` reparieren
