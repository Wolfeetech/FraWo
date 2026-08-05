# HA Stockenweiler (Eltern) — Geräte-Einbindung Phase 1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Die 18 im Alopri-Netz gefundenen Geräte (15 Shelly + 3 Cast) werden in der Home-Assistant-Instanz der Eltern (`homeassistant_stocki`, VM360, `10.1.0.248`) identifiziert; nur die von Wolf bestätigten Eltern-Geräte werden benannt, einem Bereich zugeordnet und mit dem Label `Eltern` versehen — alles andere (Lotti/ELW, Container) bleibt draußen.

**Architecture:** Browser-Automatisierung (claude-in-chrome) gegen die HA-Weboberfläche für Integration-Setup und Area/Label-Zuweisung, da die verfügbare HA-MCP-Schnittstelle nur Entity-Steuerung, keine Config-Flows bietet. Zwischenergebnisse landen in einem maschinenlesbaren Manifest im Repo (Konvention wie `manifests/stockenweiler/site_inventory.json`), damit der Stand jederzeit nachvollziehbar ist.

**Tech Stack:** Home Assistant Web-UI, claude-in-chrome (Browser-Steuerung), `mcp__homeassistant_stocki__*` (Verifikation via GetLiveContext), Git (FraWo-Repo).

## Global Constraints

- Nur Geräte einbinden, die Wolf nach Shelly-Cloud-Abgleich explizit als „Eltern" bestätigt (Spec Abschnitt 3).
- Keine Automationen bauen — nur Einbindung/Benennung/Gruppierung (Spec Abschnitt 8).
- Kein Zugangsdaten-/Token-Klartext in Commits (Repo ist öffentlich).
- Nichts an Lotti-/ELW- oder Container-Geräten anfassen oder recherchieren.
- Arbeit erfolgt in einem neuen Chrome-Tab; bestehende Wolf-Sessions/Tabs bleiben unangetastet.

---

## Vorbereitung (vor Task 1)

Repo-Klon liegt unter `/tmp/FraWo-fresh` (frisch geklont am 2026-08-05, main-Branch aktuell). Falls eine neue Session diesen Plan ausführt: zuerst `git pull` in diesem Verzeichnis, um sicherzustellen, dass `NOW.md` und die Spec noch aktuell sind.

Referenzdokument: `DOCS/superpowers/specs/2026-08-05-ha-stockenweiler-eltern-design.md`

Die 18 Ziel-IPs stehen in `NOW.md`, Abschnitt „Alopri-Anbindung": 15× Shelly (`.61 .62 .64 .65 .72 .73 .78 .152 .171 .178 .189 .191 .193 .195 .198`), 3× Cast-fähige Geräte (`.161 .167 .170`), alle im Subnetz `192.168.178.0/24`.

---

### Task 1: Manifest-Grundgerüst anlegen

**Files:**
- Create: `manifests/stockenweiler/eltern_ha_devices.json`

**Interfaces:**
- Produces: JSON-Struktur mit einem Eintrag pro Ziel-IP, Feldern `ip`, `assumed_type` (`shelly`/`cast`), `ha_device_id` (leer, wird in Task 2 gefüllt), `shelly_cloud_name` (leer, wird in Task 3 gefüllt), `party` (leer, wird in Task 3 gefüllt: `eltern`/`lotti`/`container`/`unbekannt`), `ha_area` (leer, wird in Task 5 gefüllt), `ha_label` (leer, wird in Task 5 gefüllt), `status` (`pending`/`identified`/`confirmed_eltern`/`excluded`/`done`).

- [ ] **Schritt 1: Manifest-Datei mit den 18 Einträgen anlegen**

```json
{
  "version": 1,
  "site_name": "Stockenweiler",
  "scope": "Alopri-Netz-Scan 04.08.2026, nur Eltern-Geraete fuer homeassistant_stocki",
  "source_now_md_section": "Alopri-Anbindung (Eltern, Stockenweiler)",
  "devices": [
    { "ip": "192.168.178.61",  "assumed_type": "shelly", "ha_device_id": "", "shelly_cloud_name": "", "party": "", "ha_area": "", "ha_label": "", "status": "pending" },
    { "ip": "192.168.178.62",  "assumed_type": "shelly", "ha_device_id": "", "shelly_cloud_name": "", "party": "", "ha_area": "", "ha_label": "", "status": "pending" },
    { "ip": "192.168.178.64",  "assumed_type": "shelly", "ha_device_id": "", "shelly_cloud_name": "", "party": "", "ha_area": "", "ha_label": "", "status": "pending" },
    { "ip": "192.168.178.65",  "assumed_type": "shelly", "ha_device_id": "", "shelly_cloud_name": "", "party": "", "ha_area": "", "ha_label": "", "status": "pending" },
    { "ip": "192.168.178.72",  "assumed_type": "shelly", "ha_device_id": "", "shelly_cloud_name": "", "party": "", "ha_area": "", "ha_label": "", "status": "pending" },
    { "ip": "192.168.178.73",  "assumed_type": "shelly", "ha_device_id": "", "shelly_cloud_name": "", "party": "", "ha_area": "", "ha_label": "", "status": "pending" },
    { "ip": "192.168.178.78",  "assumed_type": "shelly", "ha_device_id": "", "shelly_cloud_name": "", "party": "", "ha_area": "", "ha_label": "", "status": "pending" },
    { "ip": "192.168.178.152", "assumed_type": "shelly", "ha_device_id": "", "shelly_cloud_name": "", "party": "", "ha_area": "", "ha_label": "", "status": "pending" },
    { "ip": "192.168.178.171", "assumed_type": "shelly", "ha_device_id": "", "shelly_cloud_name": "", "party": "", "ha_area": "", "ha_label": "", "status": "pending" },
    { "ip": "192.168.178.178", "assumed_type": "shelly", "ha_device_id": "", "shelly_cloud_name": "", "party": "", "ha_area": "", "ha_label": "", "status": "pending" },
    { "ip": "192.168.178.189", "assumed_type": "shelly", "ha_device_id": "", "shelly_cloud_name": "", "party": "", "ha_area": "", "ha_label": "", "status": "pending" },
    { "ip": "192.168.178.191", "assumed_type": "shelly", "ha_device_id": "", "shelly_cloud_name": "", "party": "", "ha_area": "", "ha_label": "", "status": "pending" },
    { "ip": "192.168.178.193", "assumed_type": "shelly", "ha_device_id": "", "shelly_cloud_name": "", "party": "", "ha_area": "", "ha_label": "", "status": "pending" },
    { "ip": "192.168.178.195", "assumed_type": "shelly", "ha_device_id": "", "shelly_cloud_name": "", "party": "", "ha_area": "", "ha_label": "", "status": "pending" },
    { "ip": "192.168.178.198", "assumed_type": "shelly", "ha_device_id": "", "shelly_cloud_name": "", "party": "", "ha_area": "", "ha_label": "", "status": "pending" },
    { "ip": "192.168.178.161", "assumed_type": "cast",   "ha_device_id": "", "shelly_cloud_name": "", "party": "", "ha_area": "", "ha_label": "", "status": "pending" },
    { "ip": "192.168.178.167", "assumed_type": "cast",   "ha_device_id": "", "shelly_cloud_name": "", "party": "", "ha_area": "", "ha_label": "", "status": "pending" },
    { "ip": "192.168.178.170", "assumed_type": "cast",   "ha_device_id": "", "shelly_cloud_name": "", "party": "", "ha_area": "", "ha_label": "", "status": "pending" }
  ]
}
```

- [ ] **Schritt 2: JSON-Syntax prüfen**

Run: `python -c "import json; json.load(open('manifests/stockenweiler/eltern_ha_devices.json'))" ` (im Repo-Root ausführen)
Expected: kein Fehler, kein Output.

- [ ] **Schritt 3: Commit**

```bash
git add manifests/stockenweiler/eltern_ha_devices.json
git commit -m "docs: Manifest-Grundgeruest fuer Eltern-HA-Geraete-Einbindung"
```

---

### Task 2: Geräte über die HA-Oberfläche identifizieren (Browser-Automatisierung)

**Files:**
- Modify: `manifests/stockenweiler/eltern_ha_devices.json` (Felder `ha_device_id`, `status` je Eintrag)

**Interfaces:**
- Consumes: Manifest aus Task 1.
- Produces: für jeden Eintrag entweder `status: "identified"` + `ha_device_id` gesetzt (Integration erfolgreich, Gerät antwortet), oder `status: "unreachable"` (Integration schlägt fehl — Gerät offline/falsche IP, wird notiert und übersprungen, kein Blocker für die restlichen 17).

- [ ] **Schritt 1: Vor-Zustand erfassen (Baseline)**

Vor jeder Änderung den aktuellen Entity-Bestand von `homeassistant_stocki` zählen, um später die Differenz zu sehen:

Tool-Aufruf: `mcp__homeassistant_stocki__GetLiveContext` mit `domain: ["switch", "media_player"]`
Ergebnis (Anzahl Zeilen) notieren als Baseline-Zahl in einem Kommentar im nächsten Commit.

- [ ] **Schritt 2: Chrome öffnen, HA-Startseite ansteuern**

Per claude-in-chrome: neuen Tab öffnen, zu `http://10.1.0.248:8123/config/integrations/dashboard` navigieren. Falls Login nötig: Wolf bitten, sich einmalig anzumelden (kein Passwort im Chat).

- [ ] **Schritt 3: Für jede Shelly-IP (15 Stück) die Integration hinzufügen**

Für jede IP aus dem Manifest mit `assumed_type: "shelly"`: „Integration hinzufügen" klicken → „Shelly" auswählen → IP eintragen → bestätigen. HA zeigt nach Erfolg Modellname und Geräte-ID (MAC) an — diese Werte ins Manifest übernehmen (`ha_device_id`, `status: "identified"`). Schlägt die Verbindung fehl (Timeout/„nicht erreichbar"): `status: "unreachable"` setzen, mit nächster IP weitermachen.

- [ ] **Schritt 4: Für jede Cast-IP (3 Stück) die Integration hinzufügen**

Gleiches Vorgehen mit Integration „Google Cast", IP manuell eintragen (Auto-Discovery funktioniert vermutlich nicht durchs Tunnel, siehe Spec Abschnitt 2).

- [ ] **Schritt 5: Nach-Zustand prüfen**

Tool-Aufruf erneut: `mcp__homeassistant_stocki__GetLiveContext` mit `domain: ["switch", "media_player"]`
Expected: Anzahl Zeilen ist um die Anzahl der in Schritt 3+4 erfolgreich hinzugefügten Geräte gestiegen (nicht zwingend exakt 18, da manche Shelly-Modelle mehrere Entities pro Gerät erzeugen — Differenz ≥ Anzahl `status: "identified"`-Einträge).

- [ ] **Schritt 6: Commit**

```bash
git add manifests/stockenweiler/eltern_ha_devices.json
git commit -m "docs: Eltern-HA-Geraete identifiziert (Shelly+Cast Rohdaten)"
```

---

### Task 3: Wolf übergibt Shelly-Cloud-Abgleich (Partei-Zuordnung)

**Files:**
- Modify: `manifests/stockenweiler/eltern_ha_devices.json` (Felder `shelly_cloud_name`, `party`, `status`)

**Interfaces:**
- Consumes: Manifest mit `status: "identified"`-Einträgen aus Task 2.
- Produces: jeder `identified`-Eintrag bekommt `party` (`eltern`/`lotti`/`container`/`unbekannt`) und `shelly_cloud_name`; Status wechselt zu `confirmed_eltern` oder `excluded`.

- [ ] **Schritt 1: Rohliste an Wolf übergeben**

Die Liste aller `status: "identified"`-Einträge (IP + Modell + Geräte-ID) im Chat vorlegen — als einfache Tabelle, nicht als JSON (Wolf ist nicht technisch, siehe `feedback_wolf_communication_style` in Memory: einfache Sprache, direkte Fragen).

- [ ] **Schritt 2: Auf Wolfs Zuordnung warten**

Wolf gleicht über die Shelly-Cloud-App ab und nennt pro Gerät: Name/Zimmer + Partei (Eltern / Lotti / Container / weiß nicht). Antwort abwarten, keine Annahmen treffen.

- [ ] **Schritt 3: Manifest mit Wolfs Angaben aktualisieren**

Pro Eintrag: `shelly_cloud_name` und `party` setzen. `status` auf `confirmed_eltern` (wenn `party == "eltern"`) oder `excluded` (sonst, inkl. `unbekannt` — im Zweifel ausschließen, siehe Spec Abschnitt 3 „hart, sicherheitsrelevant").

- [ ] **Schritt 4: Commit**

```bash
git add manifests/stockenweiler/eltern_ha_devices.json
git commit -m "docs: Partei-Zuordnung Eltern-HA-Geraete nach Shelly-Cloud-Abgleich"
```

---

### Task 4: Nicht-Eltern-Integrationen wieder entfernen

**Files:**
- Modify: `manifests/stockenweiler/eltern_ha_devices.json` (Feld `status` → `done` für entfernte Einträge)

**Interfaces:**
- Consumes: Manifest-Einträge mit `status: "excluded"` aus Task 3.
- Produces: keine dieser Integrationen existiert mehr in `homeassistant_stocki`.

- [ ] **Schritt 1: Für jeden `excluded`-Eintrag die Integration in HA löschen**

Per claude-in-chrome: `http://10.1.0.248:8123/config/integrations/dashboard` → betroffene Integration suchen (per `ha_device_id`/IP) → Drei-Punkte-Menü → „Löschen". Grund: Abgrenzung aus Spec Abschnitt 3 gilt auch technisch, nicht nur organisatorisch — Lotti-/Container-Geräte sollen nicht mal unbenannt in der Eltern-Instanz herumliegen.

- [ ] **Schritt 2: Verifizieren, dass die Integration weg ist**

Tool-Aufruf: `mcp__homeassistant_stocki__GetLiveContext` mit `name: "<shelly_cloud_name des geloeschten Geraets>"`
Expected: leeres Ergebnis (keine Entity mehr gefunden).

- [ ] **Schritt 3: Manifest aktualisieren und committen**

`status` der entfernten Einträge auf `done` setzen.

```bash
git add manifests/stockenweiler/eltern_ha_devices.json
git commit -m "docs: Nicht-Eltern-Geraete aus homeassistant_stocki wieder entfernt"
```

---

### Task 5: Bestätigte Eltern-Geräte benennen, Bereich + Label setzen

**Files:**
- Modify: `manifests/stockenweiler/eltern_ha_devices.json` (Felder `ha_area`, `ha_label`, `status` → `done`)

**Interfaces:**
- Consumes: Manifest-Einträge mit `status: "confirmed_eltern"` aus Task 3.
- Produces: jedes Gerät hat in HA einen sprechenden Namen, einen der bestehenden Eltern-Bereiche (`Büro_Eltern`, `Wohnküche_Eltern`, `Buero_Controlroom_Eltern` — oder einen neuen, falls Wolfs Zuordnung keinem existierenden entspricht) und das Label `Eltern`.

- [ ] **Schritt 1: Für jeden `confirmed_eltern`-Eintrag Name + Bereich setzen**

Per claude-in-chrome: Gerät in `http://10.1.0.248:8123/config/devices/dashboard` öffnen → Namen auf `shelly_cloud_name`-Wert (oder eine klarere deutsche Bezeichnung, falls Wolf eine genannt hat) setzen → Bereich aus Dropdown wählen (bestehenden Eltern-Bereich passend zum genannten Zimmer, sonst neuen Bereich anlegen, z. B. `Küche_Eltern`).

- [ ] **Schritt 2: Label `Eltern` setzen**

Im selben Geräte-Dialog: Label-Feld → `Eltern` hinzufügen (Label anlegen, falls es noch nicht existiert).

- [ ] **Schritt 3: Schutzregel prüfen (Spec Abschnitt 5)**

Für jedes Gerät kurz mit Wolf klären: ist es sicherheits-/gesundheitsrelevant (z. B. Kühlschrank)? Falls ja: Notiz „nie automatisiert schalten" in der Gerätebeschreibung in HA hinterlegen.

- [ ] **Schritt 4: Verifizieren per Bereich**

Tool-Aufruf: `mcp__homeassistant_stocki__GetLiveContext` mit `area: "<gesetzter Bereich>"`
Expected: das neu zugeordnete Gerät erscheint in der Ergebnisliste dieses Bereichs.

- [ ] **Schritt 5: Manifest aktualisieren und committen**

```bash
git add manifests/stockenweiler/eltern_ha_devices.json
git commit -m "docs: Eltern-HA-Geraete benannt, Bereichen zugeordnet, Label Eltern gesetzt"
```

---

### Task 6: Abschluss dokumentieren

**Files:**
- Modify: `NOW.md` (Abschnitt „🔴 Offen" — Zeile „Alopri-Smart-Geräte ... innerhalb Home-Assistant hinzufügen" aktualisieren/entfernen)
- Modify: `manifests/stockenweiler/eltern_ha_devices.json` (`status` aller Eintrage sollte jetzt `done` sein)

**Interfaces:**
- Consumes: fertiges Manifest aus Task 5.
- Produces: `NOW.md` spiegelt den erledigten Stand wider; Phase-1-Definition-of-Done aus der Spec ist erfüllt.

- [ ] **Schritt 1: Alle Manifest-Einträge auf Endstatus prüfen**

Run: `python -c "import json; d=json.load(open('manifests/stockenweiler/eltern_ha_devices.json')); print([x for x in d['devices'] if x['status'] not in ('done', 'unreachable')])"`
Expected: leere Liste `[]`. `unreachable`-Einträge sind ein gültiger Endzustand (Gerät war beim Scan nicht erreichbar) — kurz an Wolf melden, aber kein Blocker. Alles andere (`pending`, `identified`, `confirmed_eltern`, `excluded`): offene Einträge mit Wolf klären, bevor dieser Task abgeschlossen wird.

- [ ] **Schritt 2: `NOW.md` aktualisieren**

Zeile in der Offen-Tabelle ersetzen durch eine kurze Erledigt-Notiz mit Datum und Verweis auf das Manifest (Format wie andere Einträge in `NOW.md`, siehe bestehende Konventionen im Dokument).

- [ ] **Schritt 3: Commit und Push**

```bash
git add NOW.md manifests/stockenweiler/eltern_ha_devices.json
git commit -m "docs: Phase 1 Eltern-HA-Geraete-Einbindung abgeschlossen"
git push https://Wolfeetech:$(git credential fill <<< $'protocol=https\nhost=github.com\n' | grep password | cut -d= -f2)@github.com/Wolfeetech/FraWo.git main
```

- [ ] **Schritt 4: Wolf kurz Bescheid geben**

Kurze Zusammenfassung im Chat: wie viele Geräte eingebunden, wie viele ausgeschlossen (mit Partei-Grund), wo die Doku liegt. Phasen 2–4 (Verbrauch, WP-Lastmanagement, Kiosk) bleiben eigene, spätere Brainstorming-Runden (Spec Abschnitt 7).
