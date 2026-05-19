# Radio Operations SSOT

> [!IMPORTANT]
> **Dies ist die verbindliche Runtime-SSOT für Radio/AzuraCast.**
> Alle operativen Radio-Entscheidungen müssen von diesem Dokument ausgehen.

**Owner:** Radio Operations  
**Last reviewed in repo:** 2026-05-19  
**Verification mode:** Daily health gate (go/no-go)

---

## 1) Scope (bindend)

Dieses Dokument ist die einzige operative Wahrheit für:
- Runtime-Status der Primärstation
- Go/No-Go Freigabe im Tagesbetrieb
- Priorisierte Sofortmaßnahmen bei Drift
- Verbindliche Referenzen auf aktive Radio-Runbooks

Nicht bindend sind historische Snapshots und alte Statusberichte.

---

## 2) Operating Model (One-Station-First)

- Primärstation ist das einzige Produktionsziel.
- Legacy/zweite Station wird nur als kontrollierter Migrationspfad behandelt.
- Keine Produktiventscheidung auf Basis historischer Statusdateien.

---

## 3) Daily Health Gate (verbindlich)

Daily gate ausführen:

```bash
make radio-daily-health-gate
# optional mit Zielhost:
make radio-daily-health-gate TARGET_HOST=100.64.23.77
```

**Go-Kriterien:**
- `rpi_radio_ready_for_azuracast=yes`
- `rpi_azuracast_service_ready=yes`
- `radio_operations_ready=yes`
- KPI-Ampel grün:
  - UI erreichbar
  - nowplaying erreichbar
  - Station online
  - Media-Mount sichtbar
  - Storage nicht kritisch

Wenn ein Kriterium fehlschlägt: **NO-GO** bis zur Behebung.

---

## 4) Canonical Radio References

- Betrieb: `/home/runner/work/FraWo/FraWo/OPERATIONS/AZURACAST_OPERATIONS.md`
- Daily checks:
  - `/home/runner/work/FraWo/FraWo/scripts/rpi_radio_readiness_check.sh`
  - `/home/runner/work/FraWo/FraWo/scripts/rpi_azuracast_service_check.sh`
  - `/home/runner/work/FraWo/FraWo/scripts/radio_operations_check.sh`
  - `/home/runner/work/FraWo/FraWo/scripts/radio_daily_health_gate.sh`
- Inventory source: `/home/runner/work/FraWo/FraWo/ansible/inventory/hosts.yml`

---

## 5) Drift Policy

- Historische Radio-Dokumente bleiben als Referenz erhalten, sind aber **nicht** entscheidungsführend.
- Jedes historische Dokument muss auf diese SSOT-Datei verweisen.
- Bei Widerspruch gilt immer dieses Dokument + aktueller Daily-Gate-Output.

---

## 6) Current Repo Action State

- Sprint 1: SSOT-Konsolidierung im Repo aktiv
- Sprint 2: Daily health gate als Standardpfad aktiv
- Sprint 3/4 (Credential Rotation, Player-Produktivabnahme): operativ nachgelagert
