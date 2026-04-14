# MASTER SINGLE SOURCE OF TRUTH (SSOT)

> [!IMPORTANT]
> **Dies ist die einzige und maßgebliche Knowledge Base für Homeserver 2027.**
> Jegliche technische Wahrheit über das FraWo-Estate wird ausschließlich hier und im Canonical Upstream (`https://github.com/Wolfeetech/FraWo`) gepflegt.

## Status

- Status: **MASTER SSOT ACTIVE**
- Canonical Upstream: [https://github.com/Wolfeetech/FraWo](https://github.com/Wolfeetech/FraWo) (Established 2026-04-13)
- Dokumenttyp: zentrale Knowledge Base / RAG-Index
- Gueltig ab: 2026-03-17
- Merge-Regel: aeltere Artefakte nur konfliktfrei uebernehmen; bei Konflikten gewinnt dieses Dokument
- Legacy-Session-Cleanup: abgeschlossen, nur dieser Workspace bleibt erhalten
- Workspace-Name: `Homeserver 2027 Ops Workspace`

## Verifizierte Basisfakten

- Hardware: Lenovo ThinkCentre M920q (i5-8500T, 15 GB RAM)
- Host: Proxmox VE auf lokalem NVMe-Storage
- Studio-PC: `WOLFSTUDIOPC` (192.168.2.162)
- Operator-Rechner: `wolf-ZenBook` (100.76.249.126)
- Shared Frontend: `surface-go-frontend` (192.168.2.154 / 100.106.67.127)
- Radio-Node: `radio-node` (192.168.2.155 / 100.64.23.77), ARM64 Raspberry Pi 4
- PBS: `VM 240` (192.168.2.25), Interim-Datastore auf 64GB USB-Stick

## Kanonische Topologie

| ID | Typ | Dienst | Rolle | Ziel-IP | Betriebsmodell |
| --- | --- | --- | --- | --- | --- |
| 100 | CT | Toolbox | Docker, Ansible, Caddy, Tailscale, DNS | 192.168.2.20 | LXC, Rebuild erlaubt |
| 200 | VM | Nextcloud | Collaboration & Docs | 192.168.2.21 | dedizierte VM |
| 210 | VM | HAOS | Smart Home | 192.168.2.24 | dedizierte HAOS-VM |
| 220 | VM | Odoo | ERP/CRM | 192.168.2.22 | dedizierte VM |
| 230 | VM | Paperless | DMS | 192.168.2.23 | dedizierte VM |
| 240 | VM | PBS | Backup Server | 192.168.2.25 | dedizierte VM |

## Netzwerk & Freigaben

- Router: Vodafone Easy Box (192.168.2.1) -> Transition zu UCG-Ultra (10.1.0.1)
- DNS: AdGuard Home (CT 100)
- VPN: Tailscale (Subnet Router 192.168.2.0/24 auf CT 100)
- Frontdoors (intern): `*.hs27.internal` via Caddy
- Frontdoors (mobile): `100.99.206.128:8443-8449` (Tailscale limited)

## Architekturentscheidungen & Business Logic

- **Isolation**: Jede Business-App (Odoo, Nextcloud, Paperless) in eigener VM.
- **Data Bridge**: Nextcloud/Paperless Bridge via WebDAV/FS-Sync alle 5 Min.
- **Backup**: Taegliche Backups via PBS (VM 240) + Proxmox-Local (local-lvm).
- **Remediation History**: Detaillierte Drifts und Fixes aus Maerz/April 2026 sind archiviert in `DOCS/HISTORY_REMEDIATIONS_2026.md`.
- **Website Rule**: Codex ist Single-Writer fuer Odoo-Views (Anti-Split-Brain).

## Aktuelle Arbeitsauftraege (Auszug)

1. `NETWORK_INVENTORY.md` Finalisierung (Unknown Clients mapping).
2. PBS-Target-Storage Erweiterung (Off-USB).
3. Radio-Library Kuration (USB -> Local Library).
4. Media Server Client Rollout (TV/Browser).
5. Public Edge Architektur (Go-Live Planning).

## Aktive Operator-Aktionen

- [ ] Radio/Media: Kuration der Bibliothek (Lane E)
- [ ] Website: Go-Live Vorbereitung (Lane B)
- [ ] Proxmox-Root-SSH-Key hinterlegen (AKTION VON DIR ERFORDERLICH)
- [ ] Easy-Box-Geraete autoritativ zuordnen (.141-.144)

## Chronologische Logs (Auszug)

### 2026-04-12: Repo Optimization
- Clutter-Cleanup: Alle Root-Scripts in `scripts/remediations`, `archive`, `research`, `business`, `tools` verschoben.
- Documentation Pruning: Remediation-History aus `MEMORY.md` extrahiert.
- Masterplan Baseline: Stabiler Git-Stand fuer Workspace-Handoff.

### 2026-04-10: Website Finalization
- Odoo Visual-Finish: Editorial Cards, Service Grid und Kontaktseiten-Fix live.
- Meta-Cleanups: SEOTitles und og:url/website_id Drifts behoben.

### 2026-04-09: Infrastructure Recovery
- Nextcloud IP-Conflict Fix (VM 200 drift auf .24).
- Odoo Intake Bridge live (agent@frawo-tech.de -> Project 21).
- Jellyfin V1 live auf CT 100.
