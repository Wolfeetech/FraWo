# Projekt → Fokuszeit-Kalender → Rückmeldung — Design

**Ziel:** Odoos bestehende, bereits aktive Automatik "Aufgabe: Frist →
Kalendertermin" (`base.automation` id 10, Server-Action id 880) wird
professionell ausgebaut: aus einem reinen 0-Minuten-Frist-Merker wird ein
echter, sauber strukturierter Fokuszeit-Termin (Dauer aus den geschätzten
Stunden der Aufgabe, automatisch in eine freie Zeit vor der Frist gelegt,
mit richtigen Odoo-Feldern statt Text im Titel). Nach dem Termin trägt
Wolf per Odoo-Bordmittel ("Aktivität erledigt + Rückmeldung") eine kurze
Notiz ein, die automatisch als Nachricht bei der Aufgabe erscheint.

**Nicht Teil dieses Specs (bewusst ausgeklammert, "Stufe 2"):** ein
automatisches Ableiten/Anlegen der nächsten Aufgabe aus der Rückmeldung.
Das erfordert echtes Verständnis des Rückmeldungstexts (Agent-Aufgabe,
kein deterministischer Automatismus) und wird erst angegangen, wenn
dieses Fundament sauber läuft. Dieses Spec deckt ausschließlich: (1)
sauberer Termin, (2) sauberer Rückmeldungsweg ins Projekt.

## 1. Ist-Zustand (geprüft, nicht vermutet, Stand 06.09.2026)

**`base.automation` id 10 "Aufgabe: Frist → Kalendertermin"** — Trigger
`on_create_or_write` auf die Felder `date_deadline` und `user_ids` von
`project.task`. Ruft Server-Action id 880 auf.

**`ir.actions.server` id 880** — aktueller Code:
```python
if record.date_deadline and record.user_ids:
    existing = env['calendar.event'].search([('res_model_id', '=', 522), ('res_id', '=', record.id)], limit=1)
    if existing:
        existing.write({'start': record.date_deadline, 'stop': record.date_deadline, 'allday': True})
    else:
        for user in record.user_ids:
            env['calendar.event'].create({
                'name': '⏰ Frist: ' + record.name,
                'start': record.date_deadline,
                'stop': record.date_deadline,
                'allday': True,
                'user_id': user.id,
                'partner_ids': [(4, user.partner_id.id)],
                'res_model_id': 522,
                'res_id': record.id,
            })
elif not record.date_deadline:
    env['calendar.event'].search([('res_model_id', '=', 522), ('res_id', '=', record.id)]).unlink()
```
(`ir.model` id 522 = `project.task`.)

Legt pro Assignee einen 0-Minuten-ganztägigen Kalendereintrag am
Fristtag an, betitelt `⏰ Frist: <Aufgabenname>`. Keine Beschreibung,
kein Ort, `allocated_hours` wird nicht angefasst.

**`base.automation` id 14 "FraWo: Aufgabe erledigt → Kalender
aufraeumen"** — Trigger `on_write`, Filter `stage_id in (6, 35)`
("✅ Erledigt" / "🗑️ Abgebrochen"). Ruft Server-Action id 886 auf, die
alle `calendar.event` mit `res_model = 'project.task'` und
`res_id = <task.id>` auf `active = False` setzt (archivieren, nicht
löschen). **Wichtig:** sucht über das Char-Feld `res_model`, nicht über
`res_model_id` — beide Felder werden von Odoo synchron gehalten, die
neue Logik muss weiterhin beide korrekt setzen (Action 880 setzt aktuell
nur `res_model_id`; das reicht, da `res_model` ein davon abgeleitetes
Feld ist — bestätigt durch Action 886, die darüber erfolgreich findet).

**Bereits vorhandene Felder, ungenutzt von der aktuellen Automatik:**
- `project.task.allocated_hours` (Float) — bei 518 Aufgaben bereits gepflegt.
- `calendar.event.description` (Html), `calendar.event.location` (Char).
- `mail.activity` mit `activity_type_id = 3` ("Meeting", category
  `meeting`) — 56 Stück existieren bereits auf `project.task`, alle mit
  gesetztem `calendar_event_id`, aber **manuell/einmalig durch den Agent
  am 01.09.2026 angelegt** (bulk `create_date`), nicht durch eine
  laufende Automatik. Odoo verknüpft eine `meeting`-Aktivität nur dann
  automatisch mit einem Kalendertermin, wenn sie über die UI
  ("Aktivität planen" → Typ Meeting) angelegt wird; serverseitig per
  Code müssen wir `calendar_event_id` selbst setzen.

## 2. Neues Verhalten von Action 880

### 2.1 Terminstruktur (statt Text im Titel)

| Feld | Inhalt |
|---|---|
| `name` | `<Projektname> · <Aufgabenname>` (kurz, lesbar) |
| `description` | HTML: Projekt (Link), Aufgaben-Beschreibung (gekürzt auf ~500 Zeichen), Link zur Aufgabe (`/odoo/project.task/<id>`), Liste weiterer Zuständiger falls mehrere |
| `location` | leer (FraWo-Aufgaben haben aktuell kein separates Orts-Feld auf `project.task`; falls sich das ändert, hier nachziehen) |
| `start` / `stop` | siehe 2.2 (Slot-Suche) statt `date_deadline`/`date_deadline` |
| `allday` | `False`, außer kein Slot gefunden (siehe 2.3) |
| `user_id`, `partner_ids`, `res_model_id`, `res_id` | wie bisher, pro Assignee |
| `categ_ids` | neues Tag `⏱️ Fokuszeit` (via `calendar.event.type`, einmalig anzulegen) — macht die automatisch erzeugten Termine im Kalender optisch von echten Meetings unterscheidbar |

**Update-Fall (Termin existiert schon, z.B. Frist geändert):** läuft
durch dieselbe Slot-Suche (2.2) und denselben Feldsatz wie die
Neu-Erzeugung — die alte Kurzschluss-Logik ("bei Existenz nur `start`/
`stop` auf den Fristtag setzen, ganztägig") entfällt ersatzlos. Es gibt
ab jetzt nur noch einen Code-Pfad für "Termin fehlt" vs. "Termin
vorhanden, Werte neu berechnen und schreiben".

### 2.2 Freie-Zeit-Suche

Arbeitszeitfenster (Default, anpassbar): **Mo–Fr, 08:00–18:00**,
Terminlänge = `record.allocated_hours` Stunden (kein Slot bei
`allocated_hours <= 0` → siehe 2.3).

Algorithmus: ab **morgen** (heute + 1 Tag) vorwärts nach dem
**ersten** freien Block der passenden Länge suchen, der komplett vor
`date_deadline` endet. Frei = keine Überschneidung mit bestehenden
`calendar.event`-Einträgen desselben `user_id` im geprüften Zeitraum.
Suche bricht nach 30 Kalendertagen ab (Sicherheitsgrenze).

Vorbereitend (einmalig, Teil des Implementierungsschritts, nicht der
Automatik selbst): ein `calendar.event.type`-Datensatz "⏱️ Fokuszeit"
anlegen; dessen ID wird danach fest im Action-Code referenziert (analog
zu `res_model_id = 522`, das ebenfalls fest codiert ist).

```python
from datetime import datetime, timedelta

WORK_START, WORK_END = 8, 18

def find_free_slot(env, user, duration_hours, deadline):
    if duration_hours <= 0 or not deadline:
        return None, None
    duration = timedelta(hours=duration_hours)
    day = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
    limit = day + timedelta(days=30)
    Event = env['calendar.event']
    while day < limit:
        if day.weekday() < 5:  # Mo-Fr
            slot_start = day.replace(hour=WORK_START)
            slot_end_of_day = day.replace(hour=WORK_END)
            candidate = slot_start
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
```

### 2.3 Kein Slot gefunden

Passiert, wenn: `allocated_hours` nicht gepflegt, oder Frist zu nah /
Kalender zu voll. Fallback: **altes Verhalten beibehalten** — 0-Minuten
Ganztags-Merker am Fristtag, plus eine Chatter-Notiz an der Aufgabe
("⚠️ Keine freie Fokuszeit vor der Frist gefunden — bitte manuell
einplanen oder Frist prüfen."), damit es nicht lautlos untergeht.

### 2.4 Rückmeldungs-Aktivität

Zusätzlich zum Kalendertermin legt Action 880 eine `mail.activity` an
(nur wenn ein echter Slot gefunden wurde, 2.2):

```python
env['mail.activity'].create({
    'res_model_id': 522,
    'res_id': record.id,
    'activity_type_id': 3,  # Meeting
    'summary': 'Rückmeldung: ' + record.name,
    'date_deadline': slot_end.date(),
    'user_id': user.id,
    'calendar_event_id': new_event.id,
})
```
Fällig am Tag des Termin-Endes. Wolf sieht sie in seiner
Aktivitäten-Übersicht, klickt nach dem Termin auf "Erledigt", trägt eine
Rückmeldung ein — Odoo postet das automatisch als Nachricht am Task
(Standardverhalten von `mail.activity.action_feedback`, keine eigene
Wizard-Logik nötig).

Bei Terminverschiebung (Task-Write mit neuer `date_deadline`, Slot muss
neu gesucht werden): bestehenden Termin UND die noch offene
Rückmeldungs-Aktivität aktualisieren statt Duplikate anzulegen — Action
sucht zuerst nach vorhandenem `calendar.event` (wie bisher), bei Treffer
wird dessen verknüpfte offene `mail.activity` (`calendar_event_id` = der
gefundene Termin, `active = True`) mitverschoben statt neu erzeugt.

### 2.5 Aufräumen (Action 886) erweitern

Zusätzlich zum bisherigen Archivieren der Kalendertermine: alle noch
offenen (`active = True`, nicht erledigt) `mail.activity`-Rückmeldungen
zur Aufgabe ebenfalls schließen (`action_feedback(feedback='Aufgabe
erledigt/abgebrochen, Rückmeldung entfällt.')`), damit keine
Karteileichen in Wolfs Aktivitäten-Übersicht liegen bleiben.

## 3. Edge Cases

| Fall | Verhalten |
|---|---|
| Mehrere Assignees | Wie bisher: ein eigener Termin + eigene Rückmeldungs-Aktivität pro Person, jede mit eigener Slot-Suche |
| `allocated_hours` nachträglich geändert | Trigger-Feldliste der Automation 10 muss um `allocated_hours` erweitert werden, sonst wird kein neuer Slot gesucht |
| Frist liegt in der Vergangenheit | Bestehendes Verhalten unverändert (Slot-Suche würde ohnehin keinen passenden Block vor der Frist finden → Fallback 2.3) |
| Aufgabe ohne Projekt | `description` lässt den Projekt-Teil einfach weg |
| Frist entfernt | Wie bisher: Termin UND jetzt zusätzlich die verknüpfte offene Rückmeldungs-Aktivität werden entfernt |

## 4. Abnahmekriterien

- Neue/geänderte Aufgabe mit Frist + `allocated_hours` + Assignee →
  Kalendertermin mit korrekter Dauer, in freier Zeit vor der Frist,
  mit gefüllter Beschreibung, plus eine fällige Rückmeldungs-Aktivität
  zum Terminende.
- Aufgabe ohne `allocated_hours` → weiterhin der bisherige 0-Minuten-
  Merker (kein Bruch für die 518 bestehenden Fälle mit und ohne Stunden).
- Aktivität als erledigt markiert mit Text → Text erscheint als Nachricht
  am Task (nativer Odoo-Test, keine Zusatzlogik).
- Aufgabe → Stage Erledigt/Abgebrochen → Termin UND Rückmeldungs-
  Aktivität werden geschlossen/archiviert, nichts bleibt offen hängen.
- Bestehende 56 manuell angelegte Meeting-Aktivitäten bleiben unberührt
  (Migration betrifft nur künftige Automatik-Läufe).

## 5. Testplan (vor Live-Schaltung)

1. Testaufgabe mit Frist in 5 Tagen, `allocated_hours = 2`, einem
   Assignee anlegen → Termin + Rückmeldungs-Aktivität prüfen.
2. Frist auf +10 Tage ändern → Termin verschiebt sich, keine Dopplung.
3. `allocated_hours` auf 0 setzen → Fallback-Merker + Warnhinweis prüfen.
4. Aktivität erledigt markieren mit Testtext → Nachricht am Task prüfen.
5. Task auf Stage 6 setzen → Termin archiviert, Aktivität geschlossen.
6. Kalender eines Assignees mit vollem Terminkalender testen → Suche
   muss über mehrere Tage weiterlaufen statt Slot ins Wochenende/außerhalb
   Arbeitszeit zu legen.

Alle Tests laufen gegen eine Kopie/Testaufgabe, nicht gegen echte
Live-Aufgaben, bevor die Automatik scharf geschaltet wird.
