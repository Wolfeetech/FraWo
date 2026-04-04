# Coolify Management Node Spec

## Rolle

Dedizierter interner Management-Knoten fuer spaeteren `Coolify`-Betrieb.

Nicht Teil davon:

- kein Public-Webnode
- kein DMZ-Knoten
- kein Hypervisor-Host selbst
- kein Stockenweiler-v1-Controller

## Faktische Empfehlung v1

Empfohlener Zielpfad:

- Plattform: `LXC` oder kleine `VM` auf `Anker`
- bevorzugte erste Wahl: `CT 130 coolify-mgmt`
- Standort: `Anker`
- Netzwerk: internes Management-Segment, nicht DMZ
- Zugriff: `Tailscale` und interner Adminpfad

## Empfohlene Groesse

- vCPU: `2`
- RAM: `2048 MB`
- Rootfs: `24 GB`
- Storage: `local-lvm`

## Warum diese Wahl

- `proxmox-anker` selbst bleibt Hypervisor und nicht App-Controller
- `toolbox` bleibt lieber Frontdoor-/Routing-Knoten und nur temporärer Fallback
- `stock-pve` ist aktuell Druckpunkt und kein sauberer Controller-Ort
- `surface-go-frontend` ist noch nicht stabil genug

## Backup- und Restore-Haltung

- Proxmox-Backup sichtbar halten
- App-Daten und Controller-Konfiguration spaeter exportierbar halten
- kein produktionskritischer Single-UI-Zustand ohne Repo-/Export-Pfad

## Gated Step

Die echte Erstellung bleibt `gated_infra`.
