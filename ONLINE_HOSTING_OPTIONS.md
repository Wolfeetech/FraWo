# Online Hosting Options

## Ziel

Externe Online-Ressourcen werden in zwei Klassen getrennt betrachtet:

- Backup / Cold Storage
- kleiner Public-Web-/Edge-Knoten

Ein kompletter oeffentlicher Spiegel der internen Plattform ist aktuell nicht Zielbild.

## Klasse 1 - Backup / Cold Storage

Empfohlener erster Schritt:

- Hetzner Storage Box `BX11`
  - `1 TB`
  - ab `3.20 EUR/Monat`
- Hetzner Storage Box `BX21`
  - `5 TB`
  - ab `10.90 EUR/Monat`

Einsatz:

- kalte Backups
- exportierte Archive
- spaeter moegliche Offsite-Kopien

## Klasse 1b - Google Drive / Google Workspace als spaeterer Zusatzpfad

Nicht als Primaerspeicher, sondern nur als spaetere Zusatzoption:

- Benutzerablage ueber `Nextcloud External Storage`
- oder Export-/Archivpfad ueber `rclone`

Professioneller Einsatz fuer euch:

- nur fuer ausgewaehlte Exportdaten
- nicht fuer VM-Disks
- nicht fuer Datenbanken
- nicht fuer PBS als primaeren Datastore

## Klasse 2 - Public Web / Edge Node

Empfohlene Groessenordnung:

- Hetzner `CCX13`
  - `2 vCPU`
  - `8 GB RAM`
  - `80 GB SSD`
  - `11.99 EUR/Monat`
- Hetzner `CCX23`
  - `4 vCPU`
  - `16 GB RAM`
  - `160 GB SSD`
  - `23.99 EUR/Monat`

Einsatz:

- Website
- spaeter gehaerteter Public Edge
- Monitoring / Reverse Proxy / schlanke Public-Dienste

## Default-Empfehlung

1. externer Backup-Pfad zuerst
2. kleiner Public-Web-/Edge-Server zweitens
3. `Google Drive` spaeter nur als Zusatzpfad fuer Export/Archiv
4. keine komplette Oeffnung der internen Plattform nach aussen

## Nicht empfohlen als erster Schritt

- voller Public-Mirror von Nextcloud, Paperless, Odoo, HA, PBS und Adminflaechen
- zweiter komplexer Produktionsstack ohne saubere Release-Gates
