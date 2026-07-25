# FraWo Agentic Infrastructure & System Skill Guide

Dieses Dokument dient als zentrale Wissensbasis für autonome KI-Agenten (OpenClaw, Antigravity, ServAssi) im FraWo-Netzwerk.

---

## 🏛️ 1. Netz- & Server-Topologie

| Host / Node | IP | Rolle / Container |
|---|---|---|
| **stockenweiler-pve** | `10.1.0.128` | Primary Compute (CT140 Odoo 19, CT120 Samba, VM210 AzuraCast Master, CT108 Vaultwarden, CT150 Monitoring) |
| **proxmox-anker** | `10.1.0.92` | Secondary HA & Backup (VM240 PBS, VM210 HAOS `10.1.0.40`, VM300 Nextcloud, CT150 OpenClaw) |
| **UniFi Gateway** | `10.1.0.1` | Core Router & Firewall |

---

## ⚡ 2. Kerndienste & API-Endpunkte

- **Odoo ERP:** `http://10.1.0.112:8069` (Live-Anbindung via ORM / JSON-RPC / SQL)
- **Anker Abrechnung:** `http://10.1.0.112:8069/anker/report/settlement`
- **Surface Kiosk:** `http://10.1.0.112:8069/kiosk`
- **FraWo Funk Radio:** `https://funk.frawo.tech` (AzuraCast API auf `10.1.0.38`, API Key in Vaultwarden)
- **OpenClaw Bot:** `@Frawo_bot` auf CT150 (Webhook Handler Port 19001)

---

## 🛡️ 3. Sicherheits- & Guardrail-Regeln

1. **Shelly 10.4.0.11 (MAC `e4:b0:63:d5:66:1c`):** **NIEMALS** automatisch schalten oder deaktivieren.
2. **Git Commit Standard:** Alle Änderungen immer im Format `type(scope): message` committen und auf `origin/main` pushen.
3. **Odoo Task Tracking:** Neue Tasks auf `stage_id=3` (In Bearbeitung) setzen, nach Verifikation auf `stage_id=6` (Erledigt).
