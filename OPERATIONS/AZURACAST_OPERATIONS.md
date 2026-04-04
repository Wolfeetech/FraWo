# AzuraCast Operations

## Zweck

AzuraCast ist der Radio- und Streaming-Betrieb.

Strategisch ist AzuraCast die Medien-Engine, nicht das zentrale Business-Identitaetssystem.

## Zugriff

- `http://radio.hs27.internal/login`
- Station: `FraWo - Funk`
- Shortcode: `frawo-funk`

## Aktueller Betriebsstand

- Radio ist intern erreichbar
- `nowplaying` liefert Daten
- SMTP ist fuer AzuraCast noch nicht fertig, weil der aktuelle Restblocker der SSH-Zugang zu `raspberry_pi_radio` ist
- Mailstandard dafuer bleibt trotzdem derselbe App-SMTP-Pfad wie fuer `Vaultwarden`, `Nextcloud`, `Paperless` und `Odoo`
- die eigentliche Legacy-`yourparty`-Last liegt derzeit noch teilweise in Stockenweiler und muss vor einem Abbau dort bewusst gesichert werden

## Normalbetrieb

- SMB-Musikpfad bleibt die produktive Quelle
- genau eine stabile Station zuerst sauber betreiben
- Radio-Assets und Musikpfade klar getrennt halten
- Odoo kann spaeter Website, CRM, Sponsor-/Partnerkontakte, Newsletter und eventuelle Supporter-Flows liefern; AzuraCast bleibt Stream-, Schedule- und Metadaten-Engine

## Taegliche Checks

- Login erreichbar
- `GET /api/nowplaying` liefert Daten
- Station ist online
- SMB-Medienpfad im Container sichtbar
- SMTP erst als gruen markieren, wenn der Pi wieder per SSH administrierbar ist und die App-Konfiguration sichtbar steht

## Nie tun

- keine zweite Station vor sauberem Stabilitaetsnachweis
- keine Root-Disk als Hauptmedienquelle nutzen
- keine Listener- oder Community-Logik zuerst an AzuraCast festtackern, wenn Odoo dieselbe Rolle als Business-/Portal-Schale sauberer abbildet

## Stockenweiler Legacy-Payload vor Abbau sichern

- `VM 210 azuracast-vm`
- `CT 207 radio-wordpress-prod`
- `CT 208 mariadb-server`
- `CT 211 radio-api`

Diese Payload zuerst nach Rothkreuz inventarisieren und sichern, erst danach duerfen Komponenten in Stockenweiler ausgeduennt werden.

## Eskalation

- bei Radioausfall zuerst Pi-Ressourcen, SMB-Mount und AzuraCast-Container pruefen
- bei offenem SMTP-Status zuerst den SSH-Zugang zu `raspberry_pi_radio` reparieren
