# Storage Node Operations

## Zweck

`CT 110 storage-node` ist die zentrale Source of Truth fuer gemeinsame Medien- und spaeter Dokumentenpfade.

## Zugriff

- IP: `192.168.2.30`
- SMB: `\\192.168.2.30\Media` und `\\192.168.2.30\Documents`
- kanonischer Musikpfad: `\\192.168.2.30\Media\yourparty_Libary`

## Normalbetrieb

- SMB bleibt der produktive Standardpfad
- Medien nicht wieder auf lokale USB-Zwischenpfade verteilen
- Schreibrechte nur bewusst erweitern

## T?gliche Checks

- Share erreichbar
- `yourparty_Libary` sichtbar
- Jellyfin und AzuraCast sehen denselben Bestand
- keine Read-Only- oder Dateisystemfehler

## Nie tun

- nicht wieder auf alte USB-Quellen zurueckfallen
- nicht als VM-Disk-Storage missbrauchen

## Eskalation

- bei Mount- oder Sichtbarkeitsproblemen zuerst SMB, Mounts und Host-Bind-Mounts pr?fen
