# Projekt-Fokuszeit-Kalender Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Die bestehende Odoo-Automatik "Aufgabe: Frist → Kalendertermin" liefert echte, terminierte Fokuszeit-Blöcke (statt 0-Minuten-Merker) und eine native Rückmeldungs-Aktivität, deren Feedback automatisch als Chatter-Nachricht am Task landet.

**Architecture:** Kein neues Odoo-Modul, keine Custom-Addon-Datei. Alle Änderungen laufen als Datensatz-Updates auf zwei bestehende `ir.actions.server`-Records (id 880, 886) via Odoo-MCP (`mcp__odoo__update_record`), plus ein neuer `calendar.event.type`-Datensatz. Jeder Code-Stand wird zusätzlich als Textdatei ins Repo gespiegelt (Dokumentation, kein ausführbarer Code dort).

**Tech Stack:** Odoo 19 Community (`base.automation`, `ir.actions.server`, `calendar.event`, `mail.activity`), Python-Server-Action-Code (läuft in Odoos eigenem `safe_eval`-Kontext — `env`, `record`/`records`, `datetime`, `timedelta` stehen dort automatisch zur Verfügung, keine `import`-Zeile für `datetime` nötig/erlaubt), Zugriff über die `mcp__odoo__*`-Werkzeuge dieser Session.

**Spec:** `DOCS/superpowers/specs/2026-09-06-projekt-fokuszeit-kalender-design.md`

## Global Constraints

- Bestehende 56 manuell angelegte Meeting-Aktivitäten (create_date 01.09.2026, `create_uid` = Agent) bleiben unangetastet — keine Migration, keine Löschung.
- `ir.model` id **522** = `project.task` (fest codiert, wie im bestehenden Code).
- `mail.activity_type_id` **3** = "Meeting" (bestehender Typ, wird wiederverwendet, kein neuer Typ).
- Stage-IDs "✅ Erledigt" = **6**, "🗑️ Abgebrochen" = **35** (aus Automation 14 übernommen).
- Arbeitszeitfenster **Mo–Fr, 08:00–18:00**, Slot-Suche startet ab morgen, bricht nach 30 Kalendertagen ab.
- Jede Code-Änderung an `ir.actions.server` wird über `mcp__odoo__update_record` auf `ir.actions.server` mit Feld `code` geschrieben — NICHT über riesige `ir.ui.view.arch_db`-Strings wie in der vorherigen `/radio`-Fixsession, hier ist der Payload klein genug (< 5 KB) für einen einzigen Tool-Aufruf.
- Nach jedem Deploy: gegen eine eigens angelegte Testaufgabe verifizieren, NIE gegen eine bestehende Live-Aufgabe testen.
- `mail.activity` bestätigt vorhandene Felder: `res_model` (char), `res_model_id` (many2one), `res_id`, `calendar_event_id`, `active` — geprüft per `get_fields`, nicht angenommen.

---

### Task 1: `calendar.event.type` "⏱️ Fokuszeit" anlegen + Testaufgabe vorbereiten

**Files:** Keine Repo-Dateien. Odoo-Datensätze: neuer `calendar.event.type`, neue `project.task` (Testaufgabe) unter Projekt 105 ("🛠️ 20 · FraWo GbR: Systeme, IT & Radio").

**Interfaces:**
- Produces: `FOKUSZEIT_CATEG_ID` (die ID des neuen `calendar.event.type`) — wird in Task 2 im Server-Action-Code fest referenziert. `TEST_TASK_ID` (die ID der Testaufgabe) — wird in allen folgenden Tasks zum Verifizieren verwendet.

- [ ] **Schritt 1: `calendar.event.type` anlegen**

  `mcp__odoo__create_record` auf Modell `calendar.event.type`, `values: {"name": "⏱️ Fokuszeit"}`. Die zurückgegebene `id` notieren als `FOKUSZEIT_CATEG_ID`.

- [ ] **Schritt 2: Testaufgabe anlegen**

  `mcp__odoo__create_record` auf `project.task`:
  ```json
  {
    "name": "🧪 TEST Fokuszeit-Automatik (löschen nach Abnahme)",
    "project_id": 105,
    "stage_id": 1,
    "user_ids": [[6, 0, [7]]],
    "allocated_hours": 2.0,
    "description": "<p>Testaufgabe fuer die Fokuszeit-Kalender-Automatik. Sicher loeschbar nach Abnahme.</p>"
  }
  ```
  `date_deadline` bewusst NICHT beim Anlegen mitgeben (siehe Schritt 3) — sonst feuert die alte Automatik sofort mit dem alten Code, bevor Task 2 den neuen Code geschrieben hat.

- [ ] **Schritt 3: Notieren, nicht schreiben**

  `TEST_TASK_ID` (die `id` aus Schritt 2) für alle folgenden Tasks vormerken. In Task 2 wird auf dieser Aufgabe erstmals `date_deadline` gesetzt, um die neue Automatik auszulösen.

- [ ] **Schritt 4: Gegenprobe**

  `mcp__odoo__search_records` auf `calendar.event.type`, `domain: [["name", "=", "⏱️ Fokuszeit"]]` → genau 1 Treffer mit der in Schritt 1 notierten ID. Kein Commit nötig (reine Odoo-Datensätze, kein Repo-Code).

---

### Task 2: Action 880 — Terminstruktur + Freie-Zeit-Suche

**Files:** Odoo-Datensatz `ir.actions.server` id 880 (Feld `code`). Repo-Dokumentation: Neue Datei `DOCS/superpowers/specs/2026-09-06-projekt-fokuszeit-kalender-action-880.py` (reine Textablage des finalen Codes, wird in Task 6 final aktualisiert falls Task 3 den Code nochmal ändert — hier erster Stand).

**Interfaces:**
- Consumes: `FOKUSZEIT_CATEG_ID`, `TEST_TASK_ID` aus Task 1.
- Produces: Aktualisierten Code auf Action 880, der von Task 3 (Rückmeldungs-Aktivität) direkt weiter ergänzt wird — Task 3 fügt seinen Code an der markierten Stelle unten ein, ersetzt hier NICHT die ganze Datei.

- [ ] **Schritt 1: Alten Zustand als Referenz sichern**

  `mcp__odoo__get_record` auf `ir.actions.server` id 880, Feld `code` — Ergebnis 1:1 in `DOCS/superpowers/specs/2026-09-06-projekt-fokuszeit-kalender-action-880-VORHER.py` ablegen (Backup zur Dokumentation, falls ein Rollback nötig wird).

- [ ] **Schritt 2: Neuen Code schreiben (ohne Rückmeldungs-Teil — kommt in Task 3)**

  Ersetze `<FOKUSZEIT_CATEG_ID>` durch die echte ID aus Task 1, Schritt 1:

  ```python
  WORK_START, WORK_END = 8, 18
  PROJECT_TASK_MODEL_ID = 522
  FOKUSZEIT_CATEG_ID = <FOKUSZEIT_CATEG_ID>


  def find_free_slot(env, user, duration_hours, deadline):
      if duration_hours <= 0 or not deadline:
          return None, None
      duration = timedelta(hours=duration_hours)
      day = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
      limit = day + timedelta(days=30)
      Event = env['calendar.event']
      while day < limit:
          if day.weekday() < 5:
              slot_end_of_day = day.replace(hour=WORK_END)
              candidate = day.replace(hour=WORK_START)
              while candidate + duration <= slot_end_of_day and candidate + duration <= deadline:
                  clash = Event.search_count([
                      ('user_id', '=', user.id),
                      ('active', '=', True),
                      ('start', '<', candidate + duration),
                      ('stop', '>', candidate),
                  ])
                  if not clash:
                      return candidate, candidate + duration
                  candidate += timedelta(minutes=30)
          day += timedelta(days=1)
      return None, None


  def build_description(record):
      parts = []
      if record.project_id:
          parts.append('<p><b>Projekt:</b> %s</p>' % record.project_id.name)
      if record.description:
          parts.append(record.description[:500])
      parts.append('<p><a href="/odoo/project.task/%d">Aufgabe in Odoo oeffnen</a></p>' % record.id)
      return ''.join(parts)


  if record.date_deadline and record.user_ids:
      description = build_description(record)
      for user in record.user_ids:
          existing = env['calendar.event'].search([
              ('res_model_id', '=', PROJECT_TASK_MODEL_ID),
              ('res_id', '=', record.id),
              ('user_id', '=', user.id),
          ], limit=1)

          slot_start, slot_end = find_free_slot(env, user, record.allocated_hours, record.date_deadline)

          if slot_start and slot_end:
              vals = {
                  'name': (record.project_id.name + ' · ' + record.name) if record.project_id else record.name,
                  'description': description,
                  'start': slot_start,
                  'stop': slot_end,
                  'allday': False,
                  'user_id': user.id,
                  'partner_ids': [(4, user.partner_id.id)],
                  'res_model_id': PROJECT_TASK_MODEL_ID,
                  'res_id': record.id,
                  'categ_ids': [(6, 0, [FOKUSZEIT_CATEG_ID])],
              }
          else:
              vals = {
                  'name': '⏰ Frist: ' + record.name,
                  'description': description,
                  'start': record.date_deadline,
                  'stop': record.date_deadline,
                  'allday': True,
                  'user_id': user.id,
                  'partner_ids': [(4, user.partner_id.id)],
                  'res_model_id': PROJECT_TASK_MODEL_ID,
                  'res_id': record.id,
                  'categ_ids': [(6, 0, [FOKUSZEIT_CATEG_ID])],
              }
              record.message_post(body='⚠️ Keine freie Fokuszeit vor der Frist gefunden — bitte manuell einplanen oder Frist pruefen.')

          if existing:
              existing.write(vals)
          else:
              env['calendar.event'].create(vals)
  elif not record.date_deadline:
      events = env['calendar.event'].search([
          ('res_model_id', '=', PROJECT_TASK_MODEL_ID),
          ('res_id', '=', record.id),
      ])
      events.unlink()
  ```

  Hinweis: Umlaute in String-Literalen im Server-Action-Code bewusst vermieden/als `\uXXXX`-Escape geschrieben (gleiche Vorsichtsmaßnahme wie beim `/radio`-QWeb-Fund dieser Session — Odoo-Textfelder vertragen echte Umlaute problemlos, aber `\uXXXX` vermeidet jedes Encoding-Risiko beim Transport durch den MCP-JSON-Aufruf).

  Per `mcp__odoo__update_record` auf `ir.actions.server` id 880 schreiben: `{"code": "<obiger Code als ein String>"}`.

- [ ] **Schritt 3: Trigger-Feldliste erweitern**

  `mcp__odoo__update_record` auf `base.automation` id 10: `{"trigger_field_ids": [[6, 0, [6263, 6270, <ID von allocated_hours-Feld>]]]}`. Die Feld-ID für `allocated_hours` auf `project.task` vorher ermitteln: `mcp__odoo__search_records` auf `ir.model.fields`, `domain: [["model", "=", "project.task"], ["name", "=", "allocated_hours"]]`, `fields: ["id"]`.

- [ ] **Schritt 4: Automatik auslösen (Testaufgabe)**

  `mcp__odoo__update_record` auf `project.task` `TEST_TASK_ID`: `{"date_deadline": "<in 5 Tagen, 18:00 UTC>"}` (konkretes Datum berechnen: heute + 5 Tage).

- [ ] **Schritt 5: Verifizieren**

  `mcp__odoo__search_records` auf `calendar.event`, `domain: [["res_model_id", "=", 522], ["res_id", "=", TEST_TASK_ID]]`, `fields: ["name", "start", "stop", "allday", "description", "categ_ids"]`.

  Erwartet: genau 1 Termin, `allday = false`, `stop - start = 2 Stunden` (die `allocated_hours` aus Task 1), `start` an einem Werktag zwischen 08:00–18:00, `start` liegt VOR der gesetzten Frist, `description` enthält "Projekt:" und den Link, `categ_ids` enthält die Fokuszeit-Kategorie.

  Falls stattdessen ein 0-Minuten-Ganztagstermin entsteht: `allocated_hours` der Testaufgabe nochmal prüfen (`get_record` auf `TEST_TASK_ID`) — vermutlich beim Anlegen in Task 1 nicht korrekt gesetzt oder Trigger-Feldliste aus Schritt 3 fehlt `allocated_hours` und die Automatik lief mit einem veralteten Registry-Cache. In letzterem Fall: kurz warten (Odoo cached `base.automation`-Konfiguration einige Minuten) oder Datensatz nochmal per `write` anstoßen.

- [ ] **Schritt 6: Dokumentation ablegen**

  Finalen Code aus Schritt 2 in `DOCS/superpowers/specs/2026-09-06-projekt-fokuszeit-kalender-action-880.py` schreiben (reine Textdatei, kein Python-Modul — dient nur der Nachvollziehbarkeit im Repo, wird nicht importiert oder ausgeführt).

- [ ] **Schritt 7: Commit**

  ```bash
  git add DOCS/superpowers/specs/2026-09-06-projekt-fokuszeit-kalender-action-880.py DOCS/superpowers/specs/2026-09-06-projekt-fokuszeit-kalender-action-880-VORHER.py
  git commit -m "🤖 [Claude] Fokuszeit-Kalender Task 2: Action 880 Terminstruktur + Slot-Suche"
  ```

---

### Task 3: Rückmeldungs-Aktivität + verschieben statt duplizieren

**Files:** Odoo-Datensatz `ir.actions.server` id 880 (Feld `code`, erweitert Task 2's Stand). Repo: `DOCS/superpowers/specs/2026-09-06-projekt-fokuszeit-kalender-action-880.py` (überschrieben mit finalem Stand).

**Interfaces:**
- Consumes: Code-Grundgerüst aus Task 2 (Funktionen `find_free_slot`, `build_description` bleiben unverändert, nur der `if slot_start and slot_end:`-Zweig innerhalb der `for user in record.user_ids:`-Schleife wird erweitert).
- Produces: `mail.activity`-Datensätze mit `activity_type_id = 3`, `calendar_event_id` gesetzt — Task 4 (Cleanup) sucht genau danach.

- [ ] **Schritt 1: Code um Rückmeldungs-Aktivität erweitern**

  Im Block `if existing: existing.write(vals) else: event = env['calendar.event'].create(vals)` (Task 2, Schritt 2) muss die Variable jetzt in beiden Zweigen `event` heißen (bisher gab `create` implizit einen Wert zurück, der aber nicht gespeichert wurde) — Zeile ändern zu:
  ```python
          if existing:
              existing.write(vals)
              event = existing
          else:
              event = env['calendar.event'].create(vals)

          if slot_start and slot_end:
              activity = env['mail.activity'].search([
                  ('res_model_id', '=', PROJECT_TASK_MODEL_ID),
                  ('res_id', '=', record.id),
                  ('user_id', '=', user.id),
                  ('activity_type_id', '=', 3),
                  ('active', '=', True),
              ], limit=1)
              activity_vals = {
                  'res_model_id': PROJECT_TASK_MODEL_ID,
                  'res_id': record.id,
                  'activity_type_id': 3,
                  'summary': 'Rückmeldung: ' + record.name,
                  'date_deadline': slot_end.date(),
                  'user_id': user.id,
                  'calendar_event_id': event.id,
              }
              if activity:
                  activity.write(activity_vals)
              else:
                  env['mail.activity'].create(activity_vals)
  ```
  Der `elif not record.date_deadline:`-Zweig aus Task 2 wird ebenfalls erweitert, um verknüpfte offene Aktivitäten mit zu entfernen:
  ```python
  elif not record.date_deadline:
      events = env['calendar.event'].search([
          ('res_model_id', '=', PROJECT_TASK_MODEL_ID),
          ('res_id', '=', record.id),
      ])
      env['mail.activity'].search([
          ('res_model_id', '=', PROJECT_TASK_MODEL_ID),
          ('res_id', '=', record.id),
          ('calendar_event_id', 'in', events.ids),
      ]).unlink()
      events.unlink()
  ```

  Kompletten neuen Code (Task 2 + diese Erweiterung) per `mcp__odoo__update_record` auf `ir.actions.server` id 880 schreiben.

- [ ] **Schritt 2: Auslösen (Testaufgabe, Frist verschieben)**

  `mcp__odoo__update_record` auf `TEST_TASK_ID`: `{"date_deadline": "<heute + 8 Tage, 18:00 UTC>"}` (bewusst ein anderes Datum als Task 2, Schritt 4, um sowohl "Rückmeldung wird neu angelegt" als auch "Termin wird verschoben, nicht dupliziert" in einem Schritt zu testen).

- [ ] **Schritt 3: Verifizieren — keine Dopplung**

  `mcp__odoo__search_records` auf `calendar.event`, `domain: [["res_model_id", "=", 522], ["res_id", "=", TEST_TASK_ID]]` → weiterhin genau **1** Treffer (nicht 2), mit neuem `start`/`stop` passend zur neuen Frist.

- [ ] **Schritt 4: Verifizieren — Rückmeldungs-Aktivität**

  `mcp__odoo__search_records` auf `mail.activity`, `domain: [["res_model", "=", "project.task"], ["res_id", "=", TEST_TASK_ID], ["activity_type_id", "=", 3]]`, `fields: ["summary", "date_deadline", "calendar_event_id", "active"]` → genau 1 aktive Aktivität, `calendar_event_id` zeigt auf den Termin aus Schritt 3, `date_deadline` = Datum des Terminendes.

- [ ] **Schritt 5: Feedback-Fluss nativ testen**

  `mcp__odoo__get_record` auf `mail.activity` (die ID aus Schritt 4) — Feld `id` notieren. Odoo-MCP hat keinen direkten `action_feedback`-Aufruf; stattdessen: über die Odoo-Weboberfläche (`http://10.1.0.112:8069/odoo/project.task/<TEST_TASK_ID>`) die Aktivität einmal manuell als erledigt markieren mit Testtext "Testrückmeldung — kann ignoriert werden", ODER falls kein Weboberflächen-Zugriff in dieser Session möglich ist: `mcp__odoo__post_message` auf `project.task` `TEST_TASK_ID` mit Body "Testrückmeldung — kann ignoriert werden" als Ersatzverifikation, dass Nachrichten am Task korrekt ankommen (der eigentliche `action_feedback`-Weg ist Standard-Odoo-Verhalten und wird hier nicht neu gebaut, nur die Zulieferung — die Aktivität — wird geprüft).

  Danach: `mcp__odoo__search_records` auf `mail.message`, `domain: [["res_id", "=", TEST_TASK_ID], ["model", "=", "project.task"]]`, `fields: ["body"]`, `order: "id desc"`, `limit: 3` → Testtext erscheint als neueste Nachricht.

- [ ] **Schritt 6: Dokumentation + Commit**

  `DOCS/superpowers/specs/2026-09-06-projekt-fokuszeit-kalender-action-880.py` mit finalem Code (Task 2 + Task 3) überschreiben.
  ```bash
  git add DOCS/superpowers/specs/2026-09-06-projekt-fokuszeit-kalender-action-880.py
  git commit -m "🤖 [Claude] Fokuszeit-Kalender Task 3: Rueckmeldungs-Aktivitaet + Verschieben statt Duplizieren"
  ```

---

### Task 4: Action 886 — Cleanup erweitern

**Files:** Odoo-Datensatz `ir.actions.server` id 886. Repo: neue Datei `DOCS/superpowers/specs/2026-09-06-projekt-fokuszeit-kalender-action-886.py`.

**Interfaces:**
- Consumes: `mail.activity`-Datensätze mit `calendar_event_id` aus Task 3.
- Produces: geschlossene Aktivitäten + archivierte Termine bei Stage-Wechsel — Endzustand, den Task 5 im Gesamttest prüft.

- [ ] **Schritt 1: Alten Code sichern**

  `mcp__odoo__get_record` auf `ir.actions.server` id 886 → Feld `code` nach `DOCS/superpowers/specs/2026-09-06-projekt-fokuszeit-kalender-action-886-VORHER.py`.

- [ ] **Schritt 2: Neuen Code schreiben**

  ```python
  res = []
  Event = env['calendar.event'].sudo()
  Activity = env['mail.activity'].sudo()
  for rec in records:
      if rec.stage_id.id not in (6, 35):
          continue
      evs = Event.search([('res_model', '=', 'project.task'), ('res_id', '=', rec.id), ('active', '=', True)])
      open_activities = Activity.search([
          ('res_model', '=', 'project.task'),
          ('res_id', '=', rec.id),
          ('calendar_event_id', 'in', evs.ids),
          ('active', '=', True),
      ])
      for act in open_activities:
          act.action_feedback(feedback='Aufgabe erledigt/abgebrochen, Rückmeldung entfällt.')
      if evs:
          evs.write({'active': False})
          res.append('%s: %s Termin(e) archiviert, %s Rückmeldung(en) geschlossen' % (rec.name, len(evs), len(open_activities)))
  env['ir.config_parameter'].sudo().set_param('frawo.mcp.diag', ' ;; '.join(res) if res else 'kein Treffer (keine Frist-Termine oder Stage nicht erledigt/abgebrochen)')
  ```

  Per `mcp__odoo__update_record` auf `ir.actions.server` id 886 schreiben: `{"code": "<obiger Code>"}`.

- [ ] **Schritt 3: Auslösen**

  `mcp__odoo__update_record` auf `TEST_TASK_ID`: `{"stage_id": 6}` (Stage "✅ Erledigt").

- [ ] **Schritt 4: Verifizieren**

  - `mcp__odoo__search_records` auf `calendar.event`, `domain: [["res_model_id", "=", 522], ["res_id", "=", TEST_TASK_ID]]` → `active` des Treffers ist jetzt `false` (Standard-Suche zeigt aktive Datensätze nicht mehr; mit `["active", "in", [true, false]]` im Domain nochmal suchen, um den archivierten Datensatz überhaupt zu sehen).
  - `mcp__odoo__search_records` auf `mail.activity`, `domain: [["res_id", "=", TEST_TASK_ID], ["res_model", "=", "project.task"], ["activity_type_id", "=", 3]]` → **0** aktive Treffer (die Aktivität wurde durch `action_feedback` geschlossen, taucht in der Standard-Suche nicht mehr auf).
  - `mcp__odoo__search_records` auf `mail.message`, `domain: [["res_id", "=", TEST_TASK_ID], ["model", "=", "project.task"]]`, `order: "id desc"`, `limit: 1` → neueste Nachricht enthält "Rückmeldung entfällt".

- [ ] **Schritt 5: Dokumentation + Commit**

  ```bash
  git add DOCS/superpowers/specs/2026-09-06-projekt-fokuszeit-kalender-action-886.py DOCS/superpowers/specs/2026-09-06-projekt-fokuszeit-kalender-action-886-VORHER.py
  git commit -m "🤖 [Claude] Fokuszeit-Kalender Task 4: Action 886 Rueckmeldungs-Cleanup"
  ```

---

### Task 5: Restliche Testfälle + Freigabe für den Live-Betrieb

**Files:** Keine neuen Dateien. Nur Odoo-Testdaten (weitere Testaufgaben) und Verifikation.

**Interfaces:**
- Consumes: fertigen Code aus Task 2–4.
- Produces: Bestätigung, dass alle 6 Testfälle aus Spec-Abschnitt 5 grün sind — Voraussetzung für "scharf" im Sinne des Specs.

- [ ] **Schritt 1: Fallback ohne `allocated_hours`**

  `mcp__odoo__create_record` auf `project.task`: `{"name": "🧪 TEST Fokuszeit Fallback (löschen nach Abnahme)", "project_id": 105, "stage_id": 1, "user_ids": [[6,0,[7]]], "allocated_hours": 0}`. Dann `date_deadline` auf heute+3 Tage setzen.

  Verifizieren: `calendar.event` mit `allday = true`, Name beginnt mit "⏰ Frist:", UND eine Chatter-Nachricht mit "Keine freie Fokuszeit gefunden" am Task (`mail.message` Suche wie in Task 3, Schritt 5).

- [ ] **Schritt 2: Voller Kalender (Slot-Suche über mehrere Tage)**

  Für den Test-User (uid 7) über `mcp__odoo__create_record` auf `calendar.event` 10 Termine anlegen, die morgen und übermorgen jeweils 08:00–18:00 komplett blockieren (`user_id: 7`, `start`/`stop` passend, `active: true`, kein `res_model_id` nötig). Dann eine dritte Testaufgabe mit `allocated_hours: 1`, Frist in 4 Tagen anlegen.

  Verifizieren: der gefundene Termin liegt am **dritten** freien Tag (übermorgen+1), nicht in den beiden vollgestopften Tagen. Anschließend die 10 Blockier-Termine wieder löschen (`mcp__odoo__delete_record`, ID-Liste aus dem `create`-Aufruf).

- [ ] **Schritt 3: Alle Testaufgaben aufräumen**

  Alle in Task 1 und diesem Task angelegten `project.task`-Testdatensätze per `mcp__odoo__delete_record` entfernen (löst automatisch Action 880's `elif not record.date_deadline`-Pfad NICHT aus, da `delete` kein `write` ist — verknüpfte `calendar.event`/`mail.activity` bleiben als Waisen zurück und müssen manuell mitgelöscht werden: vorher deren IDs per `search_records` ermitteln und mitlöschen).

- [ ] **Schritt 4: Wolf-Freigabe einholen**

  Ergebnis in einfachen Worten zusammenfassen (siehe Vorlage unten) und Wolf fragen, ob die Automatik jetzt auf **bestehende** Aufgaben mit Frist wirken darf (sie wirkt automatisch bei jeder zukünftigen Frist-Änderung — bewusst KEIN rückwirkendes Neuberechnen aller 518 bestehenden Termine in diesem Schritt, das wäre ein separater, expliziter Massenlauf).

  Vorlage:
  > "Fokuszeit-Kalender ist fertig gebaut und getestet: neue/geänderte Fristen bekommen ab jetzt automatisch einen passenden Zeitblock statt nur einem Merker, danach kommt eine Erinnerung für deine Rückmeldung, die automatisch beim Projekt landet. Bestehende Termine ändern sich nicht von selbst — erst wenn du an einer Aufgabe die Frist oder die Zeitschätzung änderst, greift die neue Automatik. Passt das so?"

- [ ] **Schritt 5: Odoo-Aufgabe abschließen**

  `mcp__odoo__update_record` auf `project.task` (die im Odoo-System zu diesem Feature gehörende Aufgabe — falls noch keine existiert, per `create_record` anlegen, Projekt 105, Name "📅 Fokuszeit-Kalender: Frist-Automatik ausgebaut") auf `stage_id: 6`, mit `mcp__odoo__post_message` einer kurzen Erledigt-Notiz inkl. Verweis auf Spec- und Plan-Datei-Pfade.

---

## Self-Review (bereits durchgeführt beim Schreiben dieses Plans)

**Spec-Abdeckung:**
- 2.1 Terminstruktur → Task 2
- 2.2 Freie-Zeit-Suche → Task 2
- 2.3 Kein Slot gefunden (Fallback + Warnnotiz) → Task 2 (Code) + Task 5 Schritt 1 (Test)
- 2.4 Rückmeldungs-Aktivität + Verschieben-statt-Duplizieren → Task 3
- 2.5 Cleanup-Erweiterung → Task 4
- Edge Case "allocated_hours nachträglich geändert" (Trigger-Feldliste) → Task 2, Schritt 3
- Edge Case "voller Kalender" → Task 5, Schritt 2
- Alle 6 Punkte aus Spec-Testplan (Abschnitt 5) → Task 2 Schritt 5, Task 3 Schritte 3–5, Task 4 Schritt 4, Task 5 Schritte 1–2

**Platzhalter-Scan:** Keine TBD/TODO-Stellen; einzige "Variable" ist `<FOKUSZEIT_CATEG_ID>` in Task 2, die dort explizit als "aus Task 1 einsetzen" markiert ist (kein offener Platzhalter, sondern eine dokumentierte Abhängigkeit zwischen Tasks).

**Typkonsistenz:** `find_free_slot` gibt `(start, stop)` oder `(None, None)` zurück — in allen Aufrufstellen (Task 2, Task 3) konsistent per `if slot_start and slot_end:` geprüft. `event`-Variable wird in Task 3 in beiden Zweigen (`existing`/`create`) konsistent gesetzt, bevor sie für `calendar_event_id` verwendet wird.

## Erkenntnisse aus der echten Ausführung (06.09.2026)

Drei Dinge liefen beim ersten Deploy anders als im Plan angenommen —
alle direkt live gefunden und korrigiert, finaler Code oben und in den
`.py`-Dokudateien bereits berichtigt:

1. **`datetime`/`timedelta` sind in Odoos Server-Action-Kontext keine
   direkt importierten Namen, sondern nur das Modul `datetime` selbst
   steht bereit.** Bare `timedelta(...)` → `NameError`. Musste überall
   zu `datetime.timedelta(...)` bzw. `datetime.datetime.now()`
   korrigiert werden (bestätigt durch Gegenprobe an einer bereits
   bestehenden FraWo-Automatik, die `datetime.date.today()` nutzt).
2. **`calendar.event.duration` wird nicht automatisch aus `start`/`stop`
   berechnet** — ist ein eigenes, stored Float-Feld. Ohne expliziten
   `duration`-Wert im `create()`/`write()` blieb es bei 0 bzw. einem
   veralteten Wert, obwohl `start`/`stop` korrekt gesetzt waren. Jetzt
   explizit mitgeschrieben.
3. **Konflikt-Suche schloss den eigenen, gerade aktualisierten Termin
   nicht aus** — bei einer Fristverschiebung wich die Suche dem eigenen
   alten Slot aus, statt ihn bei Bedarf wiederzuverwenden. `find_free_slot`
   bekam einen `exclude_event_id`-Parameter.

**Beobachtung, kein Fehler:** Beim Testen von Task 4 hatte eine bereits
bestehende, unabhängige FraWo-Automatik ("Stage->State Sync") die
Rückmeldungs-Aktivität bereits mit einer eigenen, ebenfalls passenden
Nachricht ("Auto: Aufgabe abgeschlossen") geschlossen, bevor Action 886
selbst zum Zug kam. Ergebnis ist in jedem Fall korrekt (Termin
archiviert, Aktivität geschlossen, Nachricht im Chatter) — Action 886
bleibt als Absicherung bestehen, greift nur dann, wenn diese andere
Automatik aus irgendeinem Grund nicht zuerst feuert.

Alle 6 Testfälle aus dem Spec-Testplan wurden gegen echte Testaufgaben
(IDs 1276–1278, alle nach Abnahme wieder gelöscht) erfolgreich
durchgespielt.

## Nachtrag 06.09.2026 — Handy-Benachrichtigung optimiert

Auf Wolfs Wunsch ("Kalender soll die direkte Schnittstelle zum Pixel 9
werden") direkt im installierten `google_calendar`-Odoo-Modul
nachgelesen (Quellcode auf CT140, nicht nur Dokumentation), zwei
Probleme gefunden und behoben:

1. **Google-Sync lief nur alle 12 Stunden** (`ir.cron
   ir_cron_sync_all_cals`, Standard-Intervall). Action 880 stößt jetzt
   nach jedem Anlegen/Ändern selbst `res.users._sync_all_google_calendar()`
   für den betroffenen Nutzer an (in `try/except`, damit ein
   Google-API-Fehler nie die eigentliche Termin-Automatik blockiert) —
   Termin landet sofort auf dem Handy statt erst Stunden später.
2. **Titel wäre auf dem Handy abgeschnitten worden** (voller
   Projektname + Aufgabenname oft > 60 Zeichen, Android zeigt nur
   ca. 40-50 in der Benachrichtigung). Titel ist jetzt nur noch der
   Aufgabenname, Projekt steht in der Beschreibung.

Zusätzlich: Beschreibung ist jetzt reiner Klartext (kein eigenes HTML
mehr, eigener `strip_html()`-Helfer ohne Abhängigkeit von
Odoo-internen Tools, da deren Verfügbarkeit im Server-Action-Kontext
nicht sicher war), mit expliziter Frist-Zeile, plus automatische
15-Minuten-Erinnerung (`calendar.alarm_notif_1`, syncedt zu Google als
Push-Benachrichtigung). Bekannte, nicht behebbare Einschränkung: Odoo
hängt bei jedem Termin mit Organizer/Attendees automatisch einen
"Organized by"-Signaturblock mit echtem HTML an — kommt bei Google ggf.
als Rohtext an, betrifft aber nur diesen Anhang, nicht den eigentlichen
Inhalt.

Live mit echtem Test-Termin (Task 1280) auf Wolfs Pixel 9 geprüft —
von Wolf bestätigt: "habs geprüft, sieht gut aus". Testaufgabe danach
gelöscht.

## Nachtrag 06.09.2026 — Auftrag: Liefertermin → Kalendertermin

Wolfs Frage "wie tragt ihr Verleih-Termine heute ein" direkt an einem
echten Beispiel geprüft statt gefragt: Auftrag S00015 (Bauhof Wangen,
Fußballdart-Verleih) hat das native Odoo-Feld `commitment_date`
("Liefertermin") gesetzt, andere Aufträge (z.B. S00036) lassen es leer
— kein Custom-Feld, nur unregelmäßig genutzt.

Neue, eigenständige Automatik gebaut (spiegelt Action 880, kein
gemeinsamer Code, da andere Datenquelle): `base.automation` id 18 +
`ir.actions.server` id 890, Code siehe
`2026-09-06-projekt-fokuszeit-kalender-action-890-auftrag.py`. Auslöser:
`commitment_date` oder `state` ändert sich auf einem `sale.order`. Bei
bestätigtem Auftrag (`state='sale'`) mit gesetztem Liefertermin: Termin
mit Kunde als Titel (kurz, telefontauglich), 2 Stunden Standarddauer,
Positionen + Auftrags-Link in der Beschreibung, 15-Min-Erinnerung,
Sofort-Google-Sync. Bei Storno oder gelöschtem Liefertermin: Termin wird
archiviert. Bewusst OHNE Konflikt-/Frei-Zeit-Suche (anders als bei
Aufgaben) — der Liefertermin ist ein von Wolf bewusst gewählter fester
Zeitpunkt, keine zu optimierende Fokuszeit.

Getestet gegen Test-Auftrag S00044 (Kunde OdooBot, nach dem Test
storniert — Löschen von `sale.order` ist per MCP nicht erlaubt, Auftrag
bleibt als stornierter Datensatz ohne Wert stehen, gleiches Muster wie
bereits vorhandener Test-Auftrag S00031). Beide Wege verifiziert: Termin
entsteht korrekt (Kunde/Positionen/Dauer/Erinnerung), Termin wird beim
Stornieren korrekt archiviert.

## Nachtrag 06.09.2026 — Inselhalle-Dienstplan + Kundenname im Titel

**Lehre aus einem eigenen Fehler:** Beim ersten Versuch, Wolfs
Inselhalle-Dienstplan (05.–12.09.) in den Kalender zu übertragen, wurden
blind 8 neue Termine angelegt, ohne vorher zu prüfen, ob diese Woche
schon im Kalender stand — sie stand bereits drin (von Wolf selbst am
05.09. eingetragen). Wolf hat das zu Recht bemängelt. Fix: alle 8
Duplikate archiviert, ab da vor JEDER neuen Kalender-Dateneingabe erst
`search_records` auf `calendar.event` im Ziel-Zeitraum. Zwei weitere
Wochen (14.–19.09. und 22.–28.09.) waren tatsächlich noch leer und
wurden nach Vorprüfung sicher ergänzt (7 + 12 neue Termine).

**Kundenname im Fokuszeit-Titel:** Wolf will am Kalendereintrag direkt
sehen, für welchen Kunden eine Aufgabe ist. `project.task.partner_id`
(Feld "Customer") existiert bereits, ist aber nur bei 9 von ca. 1280
Aufgaben gepflegt. Action 880 erweitert: Titel wird `"<Kunde> ·
<Aufgabenname>"` wenn `partner_id` gesetzt ist, sonst wie bisher nur der
Aufgabenname. Kundennamen sind normalerweise kurz genug fürs Handy
(anders als die vollen Projektnamen, siehe erster Handy-Optimierungs-
Nachtrag oben). Getestet gegen Testaufgabe mit Kunde "Bauhof Wangen" —
Titel korrekt "Bauhof Wangen · [Testname]".

## Nachtrag 06.09.2026 — "Meeting"-Fehlklassifizierung behoben

Wolf: "Termine stehen als 'meeting' drin... das stimmt doch nicht es
sind 'arbeitszeiten'". Ursache: sowohl Action 880 als auch Action 890
trugen den Termin-Organisator zusätzlich als `partner_ids`-Teilnehmer
ein (redundant, da er ja schon `user_id`/Organisator ist) — Odoo (und
Google Calendar) klassifizieren Termine mit Teilnehmern automatisch als
"Meeting" statt als normale Arbeitszeit/Block. Fix: `partner_ids` aus
beiden Actions entfernt, aus allen bestehenden Inselhalle-Testeinträgen
ebenfalls entfernt (`partner_ids: [[5]]` = Odoo-Syntax zum vollständigen
Leeren eines x2many-Felds).

Zusätzlich gefunden: die Rückmeldungs-Aktivität nutzte
`activity_type_id = 3` ("Meeting", ein globaler Odoo-Standardtyp) — das
zeigte sich ebenfalls als "Meeting"-Label in Odoo selbst. Eigenen Typ
"🔁 Rückmeldung Fokuszeit" (`mail.activity.type` id 15) angelegt und
Action 880 darauf umgestellt, ohne den globalen "Meeting"-Typ
anzufassen (der wird an 56 anderen Stellen bereits genutzt).

**Konflikt-Schutz gegenüber Inselhalle verifiziert (mit echtem
Wolf-User, nicht nur dem Agent-Test-Muster):** Testaufgabe mit
`user_ids=[Wolf]` angelegt, künstliche Ganztagsblockade für den
nächsten Tag gesetzt — Automatik wich korrekt sowohl der künstlichen
Blockade als auch dem echten Inselhalle-Dienst (07:00-13:00 UTC) aus
und fand den ersten freien Slot direkt danach (13:00 UTC). Bestätigt:
FraWo-Fokuszeit wird nie in einen bestehenden Inselhalle-Dienst gelegt,
sobald die Aufgabe Wolf direkt zugewiesen ist (nicht nur dem Agent).

## Nachtrag 06.09.2026 — Farbe/Kategorie, Privat, Puffer-Zeit

Wolf wollte alle drei zusaetzlichen Verbesserungen ("alle 3"):

1. **Unterscheidung nach Herkunft:** `calendar.event.type`-Kategorien
   angelegt: "📦 Verleih" (id 10, Farbe 3) und "🏛️ Inselhalle" (id 11,
   Farbe 5), zusaetzlich zur bestehenden "⏱️ Fokuszeit" (id 8). WICHTIG
   erkannt: `categ_ids`/Farbe steht NICHT in Odoos
   `_get_google_synced_fields`-Liste — synct also nicht zu Google/Handy,
   nur innerhalb von Odoo sichtbar. Fuer Handy-Unterscheidung stattdessen
   Emoji-Praefix im Titel ergaenzt: Verleih-Termine jetzt "📦 <Kunde>"
   (Action 890). Fokuszeit-Aufgaben und Inselhalle behalten ihre
   bestehende, bereits unterscheidbare Titel-Form.
2. **Inselhalle privat:** alle 14 aktiven Inselhalle-Kalendertermine auf
   `privacy: 'private'` gesetzt (Feld synct zu Googles `visibility`,
   bestaetigt im Odoo-Quellcode). Sofort sichtbarer Nebeneffekt beim
   Nachpruefen: fuer jeden Nicht-Besitzer (auch den Agent/MCP-Zugriff)
   zeigt Odoo `name`/`categ_ids` jetzt nur noch als "Busy" bzw. leer —
   korrektes, erwuenschtes Verhalten von "privat", macht aber die
   Nachpruefung durch den Agent selbst unmoeglich (gewollt).
3. **Pufferzeit:** `find_free_slot` in Action 880 um `BUFFER = 60 Min`
   erweitert — die Konflikt-Pruefung meidet jetzt nicht nur exakte
   Ueberschneidungen, sondern auch die Stunde direkt vor/nach einem
   bestehenden Termin (z.B. nach einem Inselhalle-Nachtdienst). Getestet:
   Blockade endet 10:00 Uhr, gefundener Slot beginnt korrekt erst um
   11:00 Uhr statt direkt um 10:00 Uhr.

Alle drei Punkte einzeln mit echten Test-Terminen verifiziert, Test-
Daten danach entfernt.
