# UCG Portal Pilot Runbook

## Ziel

Dieses Dokument beschreibt den ersten **gated runtime**-Pilot fuer den laufenden UCG-Uebergang.

Der Pilot ist bewusst klein:

- nur `portal`
- nur der Toolbox-/Frontdoor-Pfad
- keine Kern-Business-Dienste
- keine Public-, DNS- oder Firewall-Mischchanges im selben Fenster

## Scope

Der Pilot dient dazu, den ersten kontrollierten Service-Uebergang im bestehenden UCG-Zielbild zu validieren.

Er ist **nicht**:

- die allgemeine Proxmox-VLAN-Trunk-Migration
- kein Move von `Odoo`, `Nextcloud`, `Paperless`, `Vaultwarden`, `HA`
- kein Public-Edge-Cutover
- kein gleichzeitiger Router-/Firewall-Umbau

## Pflicht-Gate vor Runtime

Vor jeder aendernden Ausfuehrung muss zuerst dieser read-only Nachweis gruen sein:

```powershell
python "C:\WORKSPACE\PROJEKTE\Active\FraWo\scripts\portal_ucg_pilot_preflight.py"
```

Erwartung:

- `ready_for_gated_runtime_change=true`
- Report: `artifacts/ucg_portal_pilot_preflight/latest_report.md`

## Freeze-Regeln

Waerend des Piloten gleichzeitig **nicht** tun:

- keine UCG-Firewall-Regeln aendern
- keine DNS-/Hostname-Aenderungen
- keine Public-Domain-/TLS-Aenderungen
- keine parallelen Service-Moves
- keine Storage-/PBS-Arbeiten

## Runtime-Fenster

### 1. Snapshot sichern

- Snapshot fuer `CT 100 toolbox` erstellen
- Rueckweg vorher klar benennen

### 2. Nur den Portal-Pfad anfassen

- nur die Runtime-Aenderung anwenden, die fuer den ersten Toolbox-/Portal-Uebergang im bestehenden UCG-Zielbild noetig ist
- keine Nebenarbeiten am selben Host mitnehmen

### 3. Sofort verifizieren

Direkt nach der Aenderung pruefen:

```powershell
python "C:\WORKSPACE\PROJEKTE\Active\FraWo\scripts\portal_ucg_pilot_preflight.py"
python "C:\WORKSPACE\PROJEKTE\Active\FraWo\scripts\estate_census_audit.py"
```

Erwartung:

- `http://100.99.206.128:8447/` -> `200`
- `http://100.99.206.128:8447/status.json` -> `200`, `platform_core=ok`, `healthy=7/7`
- `http://portal.hs27.internal/` -> `200`
- Estate-Census bleibt `frontdoors_ok=8/8`

### 4. SSOT direkt nachziehen

```powershell
python "C:\WORKSPACE\PROJEKTE\Active\FraWo\scripts\generate_ai_server_handoff.py"
python "C:\WORKSPACE\PROJEKTE\Active\FraWo\scripts\document_ownership_check.py"
```

## Rollback

Rollback sofort, wenn eine dieser Bedingungen eintritt:

- `portal` nicht mehr `200`
- `status.json` nicht mehr gruen
- andere Frontdoors regressieren
- interner Hostname `portal.hs27.internal` bricht weg

Rollback-Reihenfolge:

1. letzte Toolbox-/Portal-Aenderung rueckgaengig machen
2. falls noetig Snapshot von `CT 100` zurueckrollen
3. `portal_ucg_pilot_preflight.py` erneut laufen lassen
4. `estate_census_audit.py` erneut laufen lassen

## Definition of Done

Der Pilot ist erfolgreich, wenn:

- `portal` als erster UCG-Pilot ohne Seiteneffekte durchgelaufen ist
- `frontdoors_ok=8/8` gruen bleibt
- der Rueckbaupfad sichtbar funktioniert haette
- die naechste Runtime-Stufe danach weiter bei `Odoo` und nicht bei ad hoc Nebenthemen startet

## Naechster Schritt nach Erfolg

Wenn `portal` stabil bleibt:

1. `media`
2. optional `radio`
3. erst danach `Odoo -> Nextcloud -> Paperless`
