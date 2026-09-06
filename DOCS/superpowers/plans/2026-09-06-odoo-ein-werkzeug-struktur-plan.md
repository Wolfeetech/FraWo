# Odoo Ein-Werkzeug: Struktur-Grundlage (4 Spuren & Projekt-Rahmen) — Plan & Umsetzung

> **Dokumentation der Umsetzung** gemäß Spec `DOCS/superpowers/specs/2026-09-06-odoo-ein-werkzeug-ki-schicht-design.md` (Abschnitt 2).
> Stand: **06.09.2026** — live in Odoo umgesetzt und verifiziert.

---

## 1. Ausgangslage

- Odoo legte bei Auftragsbestätigung (z.B. Auftrag `S00036`) automatisch ein eigenes `project.project` an, da auf Dienstleistungs-Produkten `service_tracking = 'task_in_project'` gesetzt war.
- Dadurch fragmentierte die Aufgabenverwaltung in viele Mini-Projekte statt des festen 4-Hauptprojekte-Rahmens.
- Reine Abrechnungspositionen (*Rabatt*, *Versand*, *Anfahrt*) erzeugten teils leere/überflüssige Aufgaben.
- Es fehlte eine einfache, quer über alle Projekte einheitliche Filterung nach den 4 Arbeitsarten (*Event/Verleih*, *Dienstleistung*, *Bauvorhaben*, *Intern*).

---

## 2. Umgesetzte Maßnahmen

### 2.1 4 Spuren-Tags (`project.tags`) angelegt
Vier zentrale Spuren-Tags wurden in Odoo erstellt und farblich gekennzeichnet:
- **`🎪 Event/Verleih`** (ID `149`, Color `11`)
- **`🧑‍🔧 Dienstleistung`** (ID `150`, Color `10`)
- **`🔨 Bauvorhaben`** (ID `151`, Color `3`)
- **`🏢 Intern`** (ID `152`, Color `4`)

### 2.2 Projekt-Wildwuchs abgeschaltet (`product.template`)
Alle 21 Dienstleistungs-Produkte wurden bereinigt:
- **`service_tracking = 'no'` (3 Produkte):**
  - `Rabatt` (ID 7)
  - `Versand` (ID 27)
  - `Anfahrt & Transport (Grundpauschale)` (ID 6)
- **`service_tracking = 'task_global_project'` → Projekt #104 (💼 10 · FraWo GbR: Aufträge & Events) (12 Produkte):**
  - `Fachkraft VT — Tagessatz (8 Std.)` (ID 153)
  - `Veranstaltungspauschale (Ganztag)` (ID 168)
  - `Veranstaltungspauschale (Halbtag)` (ID 167)
  - `Technik-Leistung Pauschale (nach Aufwand)` (ID 154)
  - `Helfertätigkeiten Tagessatz` (ID 2)
  - `Audio-Recording & REW Einmessung` (ID 240)
  - `DSP-Programmierung & bimodale Einmessung` (ID 82)
  - `Systeminstallation vor Ort` (ID 81)
  - `Wolfmix W1` (ID 28)
  - `Aufbau/Abbau (pro Stunde)` (ID 169)
  - `Helfertätigkeiten & Auf/Abbau (Stundenbasis)` (ID 5)
  - `Techniker-Stunde Veranstaltungstechnik (VT)` (ID 166)
- **`service_tracking = 'task_global_project'` → Projekt #105 (🛠️ 20 · FraWo GbR: Systeme, IT & Radio) (6 Produkte):**
  - `Stundensatz IT, Automation & Digitales (Wolf)` (ID 230)
  - `Smart-Home & Automation Einrichtung` (ID 156)
  - `Homeserver & Cloud-Setup` (ID 157)
  - `Website-Pflege & SEO-Service` (ID 244)
  - `IT-Support & Server-Setup` (ID 148)
  - `Medienproduktion (Stundensatz)` (ID 151)

**Gegenprobe:** 0 Produkte verbleiben mit `task_in_project` oder `project_only`.

### 2.3 Projekt #108 (`S00036`) konsolidiert
- Die beiden Aufgaben (#1216 Fachkraft VT, #1217 Anfahrt) wurden in Projekt #104 überführt.
- Tag `🧑‍🔧 Dienstleistung` wurde an beiden Aufgaben hinterlegt.
- Das leere Einmal-Projekt #108 wurde archiviert (`active = False`).

---

## 3. Verifikation

- `odoo_get_projects`: Zeigt nur noch die festen Kernprojekte (104, 105, 106, 107, 109, 32, 110).
- `project.task`: Aufgaben 1216 und 1217 liegen in Projekt 104 (`stage_id = 6`, `tag_ids = [150]`).
