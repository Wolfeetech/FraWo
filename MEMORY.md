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
- Operator-Rechner (Workstation): `wolf-ZenBook` (100.76.249.126)
- Shared Frontend: `surface-go-frontend` (192.168.2.154 / 100.106.67.127)
- **Review & Control Node**: `wolf_surface` (DESKTOP-7LMP02S, 100.79.103.59)
- **Toolbox Tailscale-IP**: `100.82.26.53` (Confirmed active after rebuild; old entry `100.99.206.128` is dead)
- **WolfStudioPC Remote Reality (2026-04-15)**: `wolfstudiopc` is online in the tailnet at `100.98.31.60` and SMB is reachable, but `SSH` on port `22` is still closed.
- Radio-Node: `radio-node` (192.168.2.155 / 100.64.23.77), ARM64 Raspberry Pi 4
- PBS: `VM 240` (192.168.2.25), Interim-Datastore auf 64GB USB-Stick

## Kanonische Topologie (Produktion)

| ID | Typ | Dienst | Rolle | Ziel-IP | Betriebsmodell |
| --- | --- | --- | --- | --- | --- |
| 100 | CT | Toolbox | Docker, Ansible, Caddy, Tailscale, DNS | **10.1.0.20** | local storage (bypass LVM) |
| 200 | VM | Nextcloud | Cloud & Files | **10.1.0.21** | dedizierte VM |
| 210 | VM | HAOS | Smart Home | **10.1.0.24** | dedizierte HAOS-VM |
| 220 | VM | Odoo | Business ERP | **10.1.0.22** | dedizierte VM |
| 230 | VM | Paperless | DMS | **10.1.0.23** | dedizierte VM |
| 240 | VM | PBS | Backup Server | `192.168.2.25` | **DEGRADED / INACTIVE** – Neuaufsetzen geplant nach Kernstack-Stabilisierung |
| 110 | CT | Storage | NFS/SMB Data Node | **10.1.0.30** | CT 110 |

## Netzwerk & Freigaben

- Router: **UCG-Ultra** (10.1.0.1) -> Primäres Gateway (**aktiv**)
- Fallback: Vodafone Easy Box (192.168.2.1) -> Legacy-Segment (Haushalt/IoT)
- DNS: AdGuard Home (CT 100) on **10.1.0.20**
- VPN: Tailscale
- **Public Edge**: Cloudflare Tunnel (Alpha, nicht produktiv)
- Frontdoors (intern): `*.hs27.internal` via Caddy (**10.1.0.20**)

## Architekturentscheidungen & Business Logic

- **Isolation**: Jede Business-App (Odoo, Nextcloud, Paperless) in eigener VM.
- **Data Bridge**: Nextcloud/Paperless Bridge via WebDAV/FS-Sync alle 5 Min.
- **Backup**: Taegliche Backups via PBS (VM 240) + Proxmox-Local (local-lvm).
- **Remediation History**: Detaillierte Drifts und Fixes aus Maerz/April 2026 sind archiviert in `DOCS/HISTORY_REMEDIATIONS_2026.md`.
- **Website Rule**: Codex ist Single-Writer fuer Odoo-Views (Anti-Split-Brain).
- **Surface Strategy**: `wolf_surface` dient als reiner Kontroll-Knoten. Hier erfolgen keine Code-Mutationen am Kern-Estate ohne expliziten Grund. Fokus: Browser-Abnahme, Log-Review und Backup-Drills.

## Aktuelle Arbeitsauftraege (Auszug)

1. `NETWORK_INVENTORY.md` Finalisierung (Unknown Clients mapping).
2. Website: Release des professionellen Macher-Designs (Lane B).
3. Radio-Library Kuration (USB -> Local Library).
4. Media Server Migration (CT 100 Rebuild follow-up).
5. Professional AI Agent Network Governance (Active).

## Aktiver Status 2026-04-14 (Restored)

- **Infrastruktur**: STABIL. Wiederherstellung nach System-Crash abgeschlossen.
- **Toolbox (CT 100)**: Restauriert (Clean-Room Rebuild). Läuft nun auf `local` (Directory-Storage), um LVM-Thin-Pool Blockaden zu umgehen. IP: `10.1.0.20`.
- **Control Portal**: Live und erreichbar unter `10.1.0.20`.
- **System-Haertung**: NTFS-Laufwerk `sda2` ist als defekt markiert und wird im Betrieb gemieden.
- **AI Agent Network**: Rollenverteilung (`INFRASTRUCTURE_ADMIN`, `CONTENT_MANAGER`) etabliert. OpenClaw (Hostinger) ist über dedizierte, secure SSH-Keys angebunden und proaktiv einsatzbereit.

## Aktive Operator-Aktionen

- [ ] `AKTION VON DIR ERFORDERLICH:` In Tailscale Admin den restricted nameserver fuer `hs27.internal` auf `100.82.26.53` setzen oder lokal den vorbereiteten NRPT-Helfer in erhoehter PowerShell ausfuehren.
- [ ] `AKTION VON DIR ERFORDERLICH:` Public Edge finalisieren: Cloudflare Tunnel + DNS fuer `frawo-tech.de` / `www.frawo-tech.de` auf `VM220` aktivieren (Runbook: `DOCS/Handover/CLOUDFLARE_TUNNEL_FINALIZATION.md`).
- [ ] `AKTION VON DIR ERFORDERLICH:` `radio-node` physisch pruefen und wieder online bringen; aktuell keine Antwort auf `192.168.2.155`, `100.64.23.77` oder `:8448`.
- [ ] `AKTION VON DIR ERFORDERLICH:` Auf `wolfstudiopc` `OpenSSH Server` einschalten oder eine lokale Admin-Session bereitstellen; erst dann ist der Studio-PC als repo-basierter Admin-Pfad sauber steuerbar.
- [ ] Windows-GUI-Updates spaeter kontrolliert abschliessen, nachdem die blockierenden Prozesse bewusst geschlossen wurden.
- [x] Easy-Box-Geraete autoritativ zuordnen (.141-.144) -> in NETWORK_INVENTORY.md den Family-Phones zugeordnet.

## Chronologische Logs (Auszug)

### 2026-04-19 (FraWo_GbR Transition): Odoo Shape-Up completed. Database renamed from `FraWo_Live_V2` to `FraWo_GbR`. Website domain `www.frawo-tech.de` and proxy mode active. Manual bootstrap backup created on VM 220.

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
