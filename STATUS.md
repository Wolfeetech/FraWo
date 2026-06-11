# FraWo GbR — Aktueller Status

> ⚠️ **VERALTET in Teilen. Für den ECHTEN Live-Stand → [`NOW.md`](NOW.md) lesen (verifiziert 2026-06-11).**
> Die ✅-Tabelle unten zeigt teils Dienste grün (Radio/Navidrome/Vaultwarden), die aktuell **DOWN** sind (Anker im Emergency-Mode). Nicht als aktuell vertrauen.

> Stand: 2026-06-05 | Vollständige Roadmap: ROADMAP.md

## Dienste (alle frawo.tech)

| Dienst | URL | Status |
|--------|-----|--------|
| Odoo 17 | https://frawo.tech | ✅ |
| Nextcloud | https://cloud.frawo.tech | ✅ |
| Grafana | https://status.frawo.tech | ✅ |
| Radio | https://funk.frawo.tech | ✅ (Anker) |
| Navidrome | https://navidrome.frawo.tech | ✅ (Anker) |
| HomeAssistant | https://ha.frawo.tech | ⚙️ Setup ausstehend |
| Paperless | intern :8011 | ✅ |
| n8n | intern :5678 | ✅ |
| Qdrant | intern :6333 | ✅ (gesichert) |

## Infra

| Node | IP Tailscale | Rolle |
|------|-------------|-------|
| frawo-docker-1 | 100.94.32.41 | Docker primär + CF Tunnel |
| proxmox-anker | 100.69.179.87 | HA, PBS, Radio, Navidrome |
| stockenweiler-pve | 100.91.20.116 | HP ProDesk, Upload läuft |

## Offene Punkte (Wolf)

- [ ] ha.frawo.tech einrichten (Browser, 3 Min)
- [ ] Canton CT2000 Tweeter einbauen (Lieferung 08.-11.06.)
- [ ] HP ProDesk Upload abwarten (~384 GB total, 9% done)
- [ ] Franz Bienert Nachname verifizieren
- [ ] Passwörter in Vaultwarden eintragen

## Letzte Änderungen

- Kanban: 30 → 7 Stages (sauber)
- Firewall: DOCKER-USER gesetzt, rpcbind gestoppt
- Alle Logins: @frawo-tech.de → @frawo.tech
- Cloudflare Tunnel: HA-Failover auf frawo-docker-1
- Equipment: Canton CT2000 in Maintenance-Register

## Update 2026-06-05 Abend

### Abgeschlossen
- Radio-Voting live: vote/votes Endpoints verifiziert, Frontend v3 deployed
- Radio-Backend neu gebaut (community Router Prefix /api/v1/community korrekt)
- Firewall: DOCKER-USER gesetzt, rpcbind gestoppt
- Alle Logins: @frawo-tech.de → @frawo.tech (0 alte Referenzen)
- Roadmap: 5-Phasen-Plan in GitHub + Odoo Epics T481-T485
- Kanban: 30 → 7 Stages
- Cloudflare Tunnel HA: Failover-Connector auf frawo-docker-1

### Blockiert (Wolf nötig)
- Nextcloud Filestore Transfer: SSH-Key auf VM300 (10.4.0.21) einrichten
- HA-Setup: ha.frawo.tech → Account anlegen (3 Min)

## Update 2026-06-06 Morgen
- 3 n8n Workflows: frawo-tech.de → frawo.tech gefixt
- Franz: Internal User (Admin-Rechte entfernt)
- T168 Haftpflicht + T167 Geschäftskonto dokumentiert
- SOUL.md aktualisiert (Klausi)
- GrowBox: kein Backlog mehr

## Update 2026-06-06
- CI: FRAWO_CI_GUIDELINES.md in SSOT (Purple #a855f7, Forest #0d4d4d, Inter, Sharp Corners)
- funk.frawo.tech: auf offizielle CI umgestellt
- Odoo Website: CI bereits aktiv (21k chars Custom CSS)
- N26 + Qonto Journals in Odoo
- GrowBox: 7 Stages, 20 Pflanzen, kein Backlog
- Business: CRM DE, Services, Templates
- Tasks: Haftpflicht/Qonto/N26 als Wolf-Tasks eingetragen

## Update 2026-06-11 Nacht (Antigravity Agent)
- **Anker-Ausfall & Diagnostik:** Der Proxmox-Anker (`100.69.179.87`) ist offline. Im UCG (UniFi Cloud Gateway) wurde der Host mit der IP `10.3.0.25` auf VLAN 103 (Radio-DMZ) erkannt. Wegen falschem VLAN und fehlendem Datenpfad war er remote komplett isoliert (100% Packet Loss).
- **Hard-Reboot & USB-Bereinigung:** Der Benutzer hat alle USB-Geräte (inkl. der fehlerhaften `ssd2tb`) abgezogen und einen manuellen Hard-Reboot durchgeführt.
- **Monitoring:** Ein automatisches Monitoring prüft nun alle 5 Minuten die Erreichbarkeit und dokumentiert jeden Status-Check direkt in Odoo (Task 547 und 274).
- **Odoo Sync:** Die Board-Spalten und Masterplan-Tasks wurden erfolgreich via `scripts/business/odoo_ssot_sync.py` abgeglichen.

