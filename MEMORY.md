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

## Kanonische Topologie (Produktion)

| ID | Typ | Dienst | Rolle | Ziel-IP | Betriebsmodell |
| --- | --- | --- | --- | --- | --- |
| 100 | CT | Toolbox | Docker, Caddy, Tailscale, DNS, Public Edge | 10.1.0.20 | LXC (DEFEKT/DISK LOST) |
| 200 | VM | Nextcloud | Cloud & Files | 10.1.0.21 | dedizierte VM |
| 210 | VM | HAOS | Smart Home | 10.1.0.24 | dedizierte HAOS-VM |
| 220 | VM | Odoo | Business ERP | 10.1.0.22 | dedizierte VM |
| 230 | VM | Paperless | DMS | 10.1.0.23 | dedizierte VM |
| 240 | VM | PBS | Backup Server | 192.168.2.25 | dedizierte VM (Interim) |
| 110 | CT | Storage | NFS/SMB Data Node | 10.1.0.30 | CT 110 |

## Netzwerk & Freigaben

- Router: **UCG-Ultra** (10.1.0.1) -> Primäres Gateway
- Fallback: Vodafone Easy Box (192.168.2.1)
- DNS: AdGuard Home (CT 100) on 10.1.0.20
- VPN: Tailscale
- **Public Edge**: [https://protocol-panel-cove-little.trycloudflare.com](https://protocol-panel-cove-little.trycloudflare.com) (Alpha)
- Frontdoors (intern): `*.hs27.internal` via Caddy (10.1.0.20)

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

### 2026-04-14: Anker Blackout & Emergency Recovery (The "Wolf.EE" Incident)
- Master node "Anker" crashed due to USB stick (Wolf.EE) failure, causing kernel panic.
- "Stockenweiler" node isolated safely. Thermal panic resolved by disabling `anker-music` NFS mount.
- "Anker" recovered and booted cleanly. Key VMs (200, 210, 220, 230) survived perfectly.
- CRITICAL: `CT 100 toolbox` lost its raw disk image during the crash. Cloudflare, Caddy, and Tailscale routing died.
- Quick Fix: Established direct NAT routing on Anker (`iptables` PREROUTING port 8069 to `10.1.0.22`) to bring Odoo back online locally.
- Notiz: PBS-Instanz auf Anker wird stillgelegt; PBS Stockenweiler (109) übernimmt exklusiv.

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
