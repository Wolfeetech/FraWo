# FraWo GbR — Aktueller Status

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
