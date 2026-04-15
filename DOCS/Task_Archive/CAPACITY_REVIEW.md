# Homeserver 2027 Capacity Review

## Zweck

Diese Datei bewertet den aktuellen Proxmox-Host und die laufenden Instanzen nicht nur nach Soll-Konfiguration, sondern nach der echten Laufzeitlast. Ziel ist eine professionelle Groessenentscheidung fuer RAM, CPU, Disk und die naechsten Ausbauschritte.

Pruefdatum:
- `2026-03-18`

Pruefquelle:
- Proxmox Live-Status
- `qm config`
- `qm status --verbose`
- Gastabfragen per SSH und Docker-Stats

## Executive Summary

Die Infrastruktur ist lauffaehig, aber der Host ist der eigentliche Engpass:

- Host: `Intel Core i5-8500T`, `6` physische Kerne, `15 GiB` RAM
- Aktuelle Soll-Zuweisung:
  - `CT 100 toolbox`: `2 GiB`
  - `VM 200 nextcloud`: `4 GiB`
  - `VM 210 HAOS`: `4 GiB`
  - `VM 220 odoo`: `4 GiB`
  - `VM 230 paperless`: `4 GiB`
- Summe konfigurierte Gast-RAM-Zuweisung: `18 GiB`
- Das liegt ueber dem physischen Host-RAM und ist damit bereits ein kontrollierter Overcommit.

Die gute Nachricht:
- CPU ist aktuell nicht der limitierende Faktor.
- Disk ist aktuell noch kein akutes Engpassthema.
- Nextcloud und Odoo sind im jetzigen Zustand klar ueberdimensioniert.

Die schlechte Nachricht:
- PBS, groessere HAOS-Add-on-Nutzung, spaeter AzuraCast und ein professioneller Gateway-Rand werden auf diesem Host ohne disziplinierte RAM-Strategie oder Host-RAM-Upgrade eng.

## Live-Messung

### Host

- Host-RAM: `15 GiB`
- Host-used: ca. `10 GiB`
- Host-available: ca. `4.5 GiB`
- CPU: `6` Kerne, `1` Thread pro Kern
- Storage:
  - `local`: ca. `41%` belegt
  - `local-lvm`: ca. `19%` belegt

### CT 100 Toolbox

Konfiguration:
- `2 vCPU`
- `2048 MB` RAM
- `10 GB` Rootfs

Live-Last:
- Gast-RAM genutzt: ca. `135 MB`
- Docker-Container:
  - `caddy`: ca. `10 MB`
  - `adguard`: ca. `40 MB`
- Rootfs-Nutzung: ca. `3.2 GB`

Bewertung:
- fuer `Caddy + AdGuard + Tailscale` war `10 GB` urspruenglich ausreichend
- fuer den spaeteren Medienserver-/Jellyfin-Betrieb war `10 GB` Rootfs zu knapp

Ist-Update vom `2026-03-20`:
- `CT 100` wurde wegen des Jellyfin-Bootstrap-Imports inzwischen operativ auf effektiv `96G` Rootfs vergroessert
- der Ausloeser war ein echter Laufzeitfehler `No space left on device` waehrend des Pi->Toolbox-Mediensyncs

Empfehlung:
- Rootfs fuer `CT 100` nicht mehr unter `64-96 GB` planen, solange Jellyfin und bootstrap-/kurationsnahe Medienpfade dort laufen
- RAM auf `3072-4096 MB` spaeter neu bewerten, wenn mehr Medien-/Portal-/Edge-Dienste hinzukommen

### VM 200 Nextcloud

Konfiguration:
- `2 vCPU`
- `4096 MB` RAM
- `32 GB` Disk

Live-Last:
- QEMU-Runtime-RAM genutzt: ca. `1104 MB`
- Gast `free -h`: ca. `666 MB` genutzt, `2.8 GiB` frei
- Docker:
  - `nextcloud_app`: ca. `50 MB`
  - `mariadb`: ca. `111 MB`
  - `redis`: ca. `10 MB`
- Rootfs-Nutzung: ca. `4.3 GB`
- Datenvolumes:
  - `nextcloud_nextcloud`: ca. `781 MB`
  - `nextcloud_db`: ca. `155 MB`

Bewertung:
- fuer die aktuelle Last deutlich ueberdimensioniert
- CPU-Seite unkritisch
- `32 GB` Disk ist fuer den aktuellen Stand okay, aber fuer eine ernsthafte Dokumentenablage mittelfristig zu klein, wenn App und Daten zusammen auf derselben Systemdisk bleiben

Empfehlung:
- RAM in einem geplanten Wartungsfenster auf `2048 MB` reduzieren
- `2 vCPU` beibehalten
- mittelfristig separates Datenvolume oder Disk-Erweiterung auf `64-128 GB`, bevor echter Dokumentenwuchs einsetzt

### VM 220 Odoo

Konfiguration:
- `2 vCPU`
- `4096 MB` RAM
- `32 GB` Disk

Live-Last:
- QEMU-Runtime-RAM genutzt: ca. `1221 MB`
- Gast `free -h`: ca. `689 MB` genutzt, `2.6 GiB` frei
- Docker:
  - `odoo_web`: ca. `160 MB`
  - `postgres`: ca. `65 MB`
- Rootfs-Nutzung: ca. `4.0 GB`
- Datenvolumes:
  - `odoo_db-data`: ca. `184 MB`
  - `odoo_odoo-data`: ca. `31 MB`

Bewertung:
- fuer die aktuelle Last klar ueberdimensioniert
- CPU-Seite unkritisch
- `32 GB` Disk reicht derzeit

Empfehlung:
- RAM in einem geplanten Wartungsfenster auf `2048 MB` reduzieren
- `2 vCPU` beibehalten
- keine Plattform-Ummodellierung, solange der Stack stabil ist

### VM 230 Paperless

Konfiguration:
- `2 vCPU`
- `4096 MB` RAM
- `32 GB` Disk

Live-Last:
- QEMU-Runtime-RAM genutzt: ca. `1926 MB`
- Gast `free -h`: ca. `1.3 GiB` genutzt, `2.0 GiB` frei
- Docker:
  - `paperless_webserver`: ca. `656 MB`
  - `paperless_tika`: ca. `227 MB`
  - `paperless_db`: ca. `47 MB`
  - `paperless_broker`: ca. `14 MB`
  - `gotenberg`: ca. `7 MB`
- Rootfs-Nutzung: ca. `5.4 GB`

Bewertung:
- derzeit noch okay dimensioniert
- OCR-, Tika- und PDF-Konvertierungsjobs koennen Lastspitzen erzeugen
- `32 GB` Disk reicht aktuell, ist aber fuer echte Archiv-Nutzung eher ein Startwert als ein professioneller Endzustand

Empfehlung:
- RAM vorerst bei `4096 MB` belassen
- `2 vCPU` beibehalten
- mittelfristig separates Datenvolume oder Disk-Erweiterung auf mindestens `64 GB`, besser mehr nach Dokumentenaufkommen

### VM 210 Home Assistant OS

Konfiguration:
- `2 vCPU`
- `4096 MB` RAM
- `32 GB` Disk

Live-Last:
- QEMU-Runtime-RAM genutzt: ca. `3686 MB`
- freie Gast-RAM laut Agent nur noch ca. `217 MB`
- Disk-Schreiblast deutlich hoeher als bei den Business-VMs

Bewertung:
- das ist aktuell die am engsten dimensionierte VM
- `4096 MB` sind nicht zu viel, sondern eher die Unterkante fuer den eingeschlagenen HAOS-Weg
- mit spaeteren Add-ons oder USB-Integrationen steigt der Bedarf eher weiter

Empfehlung:
- keinesfalls verkleinern
- aktuell bei `4096 MB` belassen
- spaeter auf `6144 MB` erhoehen, wenn Host-RAM vergroessert wurde oder andere VMs vorher sauber verkleinert wurden

## Strategische Bewertung

### Was sofort optimierbar ist

Die beste kurzfristige Optimierung ist nicht CPU-Tuning, sondern RAM-Rechtgroessen:

- `VM 200 nextcloud`: `4096 -> 2048 MB`
- `VM 220 odoo`: `4096 -> 2048 MB`

Das spart zusammen `4096 MB` konfigurierte Gast-RAM-Zuweisung und schafft Luft fuer:
- Proxmox selbst
- HAOS-Wachstum
- den spaeteren PBS-Betrieb

### Was bewusst noch nicht angefasst werden sollte

- `VM 210 HAOS` nicht verkleinern
- `VM 230 paperless` derzeit nicht verkleinern
- keine Umstellung laufender stabiler Business-VMs von `i440fx` auf `q35` nur fuer kosmetische Vereinheitlichung
- keine voreilige CPU-Reduktion von `2 vCPU` auf `1 vCPU`; die CPU ist nicht der Engpass und Burst-Reserven sind sinnvoll

### Was der eigentliche Professionalitaets-Hebel ist

Der Host-RAM ist der groesste strukturelle Engpass. Fuer einen dauerhaft professionellen Zielzustand ist ein RAM-Upgrade der wirksamste naechste Hardware-Schritt.

Zielbild:
- Host-RAM mittelfristig auf `32 GB`

Das bringt:
- sauberere Reserve fuer HAOS
- realistischeren PBS-Betrieb
- mehr Ruhe fuer Paperless-OCR-Spitzen
- Luft fuer Toolbox-Ausbau inklusive AzuraCast

## Empfohlene Zielgroessen

Kurzfristig auf aktuellem Host:

- `CT 100 toolbox`: `2 GB` RAM, `10 GB` Rootfs
- `VM 200 nextcloud`: `2 GB` RAM, `32 GB` Disk
- `VM 210 HAOS`: `4 GB` RAM, `32 GB` Disk
- `VM 220 odoo`: `2 GB` RAM, `32 GB` Disk
- `VM 230 paperless`: `4 GB` RAM, `32 GB` Disk

Mittelfristig professioneller:

- `CT 100 toolbox`: `2-4 GB` RAM, `20-32 GB` Rootfs vor AzuraCast
- `VM 200 nextcloud`: `2-4 GB` RAM, separates Datenvolume oder `64-128 GB+`
- `VM 210 HAOS`: `4-6 GB` RAM
- `VM 220 odoo`: `2-4 GB` RAM
- `VM 230 paperless`: `4 GB` RAM, separates Datenvolume oder `64 GB+`
- `VM 240 PBS`: erst nach separatem Backup-Storage und bevorzugt nach Host-RAM-Entspannung

## Operative Empfehlung

Reihenfolge:

1. `VM 200` und `VM 220` in einem Wartungsfenster auf `2048 MB` RAM reduzieren.
2. Danach einen kompletten Drift-, Funktions- und Backup-Check fahren.
3. Erst dann PBS und weitere Ausbaupfade weiterziehen.
4. Host-RAM-Upgrade als mittelfristigen Professionalitaets-Meilenstein in den Masterplan aufnehmen.

## Entscheidung

Fazit:
- ja, die aktuelle Konfiguration laesst sich optimieren
- nein, nicht durch grossen Plattform-Umbau
- die richtige Optimierung ist gezieltes Rightsizing bei Nextcloud und Odoo, waehrend HAOS und Paperless bewusst konservativ bleiben
