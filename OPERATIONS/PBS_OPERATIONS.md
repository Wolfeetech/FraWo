# PBS Operations

## Zweck

`VM 240 pbs` ist der Proxmox-Backup-Server fuer den Backup- und Restore-Standard.

## Zugriff

- `192.168.2.25:8007`
- Proxmox-Storage: `pbs-interim`

## Normalbetrieb

- taegliche Jobs laufen lassen
- Restore-Drills regelmaessig nachweisen
- interimistische USB-Storage-Grenzen im Blick behalten

## T?gliche Checks

- PBS erreichbar
- Datastore aktiv
- letzter Backup-Lauf erfolgreich
- Restore-Proof weiterhin reproduzierbar

## Nie tun

- nicht als finalen Langzeitspeicher missverstehen
- keine Backup-Fenster mitten im Arbeitstag starten

## Eskalation

- bei Backup-Fehlern zuerst Datastore, USB-Backing und Proxmox-Storage-Einbindung pr?fen
