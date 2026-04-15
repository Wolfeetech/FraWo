# Google Drive Integration Plan

## Ziel

Diese Datei legt fest, wie `Google Drive` bzw. `Google Workspace`-Speicher spaeter sauber in die Plattform eingebunden werden kann.

## Ausgangspunkt

- `Google Drive` ist fuer euch **kein** Primrspeicher.
- `Google Drive` ist fuer euch spaeter ein moeglicher:
  - Offsite-Archivpfad
  - Exportziel fuer ausgewaehlte Daten
  - Benutzernahe Zusatzablage in `Nextcloud`

## Wichtige Grenze

Nicht sinnvoll fuer:

- Proxmox-VM-Disks
- Datenbanken
- PBS-Datastore als Primaerspeicher
- latenzkritische Live-Mounts im Produktionspfad

## Professioneller Einsatz fuer eure Groesse

### Option A - Benutzernahe Einbindung in Nextcloud

Ziel:

- `Google Drive` als zusaetzliche Benutzerablage innerhalb `Nextcloud`

Technischer Pfad:

- Nextcloud `External Storage` App
- Google-Drive-Backend nur fuer bewusst freigegebene Benutzer oder Admin-Mounts

Geeignet fuer:

- persoenliche Dateien
- Teilen einzelner Ordner
- Zugriff ueber das bekannte Nextcloud-Interface

Nicht geeignet fuer:

- systemische Serverbackups
- VM-/Container-Daten

### Option B - Systemischer Export ueber `rclone`

Ziel:

- ausgewaehlte Archive oder Exportsaetze nach `Google Drive` spiegeln

Technischer Pfad:

- `rclone`-Remote fuer Google Drive / Google Workspace
- zeitgesteuerte Exporte aus:
  - Dokumentenarchiv
  - ausgewaehlten Medienarchiven
  - dedizierten Offsite-Exportpfaden

Geeignet fuer:

- kalte oder warme Offsite-Kopien
- manuell oder zeitgesteuert erzeugte Exportsaetze

Nicht geeignet fuer:

- Live-Dateisystem als Produktionsquelle

## Empfehlung fuer FRAWO

Die professionelle Reihenfolge ist:

1. jetzt **nicht** in den produktiven Primrpfad einbauen
2. erst nach Release und nach Mail-/Secret-Standard
3. zuerst als `rclone`-Exportziel fuer ausgewaehlte Offsite-Kopien
4. spaeter optional als `Nextcloud External Storage` fuer Benutzeroberflaechen

## Wenn bereits `2 TB` Google-Speicher vorhanden ist

Dann ist der sinnvolle Einsatz:

- nicht als Ersatz fuer `CT 110`
- nicht als Ersatz fuer PBS
- sondern als zusaetzliche Offsite-/Cloud-Ablage fuer ausgewaehlte Exportdaten

## Definition of Done

Google Drive ist erst dann professionell integriert, wenn:

1. klar ist, ob es Benutzerablage oder Offsite-Exportziel ist
2. keine Produktionsdaten exklusiv nur dort liegen
3. `rclone`- oder Nextcloud-Konfiguration dokumentiert ist
4. Wiederherstellung eines Beispiel-Exports praktisch getestet wurde

## Default

- vor dem ersten stabilen Release kein produktiver Google-Drive-Pfad
- spaeter zuerst `rclone` fuer Export/Archiv
- `Nextcloud External Storage` nur fuer bewusst freigegebene Benutzerfluesse
