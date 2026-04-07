# Proxmox Operations

## Zweck

Proxmox ist die Hypervisor-Basis. Hier werden VMs, LXCs, Storage und Snapshots verwaltet.

## Zugriff

- prim?r: `https://192.168.2.10:8006`
- Host: `proxmox-anker`
- nicht ?ffentlich freigeben

## Normalbetrieb

- nur VMs/LXCs gezielt starten, stoppen oder warten
- Storage-Auslastung vor riskanten Aktionen pr?fen
- Snapshots nur bewusst und kurzlebig nutzen
- Restore-Tests sauber von Produktion trennen

## T?gliche Checks

- Host erreichbar
- `local-lvm` nicht kritisch voll
- `local` nicht kritisch voll
- produktive VMs/LXCs laufen
- keine unerwarteten `io-error`-Zust?nde

## Nie tun

- keine dauerhafte Snapshot-Sammlung stehen lassen
- keine Test-VMs mit Produktions-IP starten
- keine Admin-Freigabe nach au?en

## Eskalation

- bei `io-error`, Thinpool-Druck oder Storage-Alarm erst Storage pr?fen, dann Apps
