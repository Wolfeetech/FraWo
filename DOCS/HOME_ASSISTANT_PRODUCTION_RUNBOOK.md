# Home Assistant Production Runbook

Dokumentation der produktionsreifen Home Assistant Instanz (**HAOS VM210**) gemäß **Task #110**.

---

## 🏗️ 1. Instanz & System-Spezifikation

- **Host Node:** `proxmox-anker` (`10.1.0.92`)
- **VM ID:** `VM 210` (HAOS 10.x / Linux KVM)
- **Ressourcen:** 2 CPU Cores, 2 GB RAM
- **Netzwerk IP:** `10.1.0.40:8123`
- **Web Interface:** `http://10.1.0.40:8123`

---

## 🛡️ 2. Automatische Backup & Desaster Recovery Pipeline

- **Automatischer Cron-Job:** Täglich um 04:00 Uhr nachts via Proxmox Backup Manager.
- **Ziel-Speicher:** Verschlüsseltes Offsite Cloud Storage (`google-drive`).
- **Retentions-Policy:** 3 tägliche Wiederherstellungspunkte (`keep-last: 3`).

---

## ⚡ 3. Integrierte Smart Home Geräte & Automationen

| Gerät / Integration | Typ / Protokoll | Funktion |
|---|---|---|
| **Shelly Plugs (10.4.0.x)** | Wi-Fi / REST API | Klimasteuerung & Strommessung (GrowBox / Studio) |
| **Govee Smart LEDs** | Wi-Fi / Govee API | Ambience- & Event-Beleuchtung |
| **Home Assistant Blueprints** | Automations-Templates | Zeitschaltuhren & schwellwertbasierte Lüftersteuerung ([`DOCS/SMART_AUTOMATION_HA_SHELLY.yaml`](file:///c:/Users/StudioPC/FraWo/DOCS/SMART_AUTOMATION_HA_SHELLY.yaml)) |

---

## 🔒 4. Sicherheits- & Guardrail-Regeln

- **Shelly 10.4.0.11 (MAC `e4:b0:63:d5:66:1c`):** **STRIKT GESCHÜTZT** — Darf niemals automatisiert abgeschaltet werden.
- **Firewall Isolation:** IoT-Kanal restricted auf HA Controller `10.1.0.40:8123`.
