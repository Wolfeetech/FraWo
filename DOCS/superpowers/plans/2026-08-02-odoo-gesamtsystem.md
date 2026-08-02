# Odoo als lebendiges Betriebssystem — Umsetzungsplan

> **Für ausführende Agenten:** ERFORDERLICHE UNTER-SKILL: `superpowers:executing-plans`, Aufgabe für Aufgabe. Schritte nutzen Checkbox-Syntax (`- [ ]`).

**Ziel:** Odoo hört auf, ein Ablageort zu sein, in dem man alles zusammensuchen muss. Stattdessen: Ein Auftrag zieht Projekt, Aufgaben, Termine und Stunden hinter sich her — und der Agent kann per Chatter und Telegram angewiesen werden.

**Architektur:** Alles mit Bordmitteln von Odoo 19 Community. Keine Lizenz, keine Zusatzmodule, kein lokales Sprachmodell. Der Ablauf trägt sich selbst über `base_automation`; der Agent hängt per Webhook daran.

**Technik:** Odoo 19 Community in CT140 auf dem ProDesk · `sale_project`, `sale_timesheet`, `hr_timesheet`, `base_automation`, `crm`, `maintenance` — alle installiert · OpenClaw-Gateway auf CT150 (Anker) für Telegram · MCP-Zugriff auf 19 Modelle

---

## Ausgangslage (02.08.2026 in der Datenbank gemessen)

| Was | Zustand | Bewertung |
|---|---|---|
| Geteilte Phasen (Backlog → Erledigt) | 6 Stück, 25–30 Projekte | ✅ **funktioniert** |
| „🔍 Review & Quality Gate" | **21 eigene Objekte** | 🔴 der eine echte Strukturfehler |
| Aufgaben in „🚀 In Arbeit" | **1** (bei 143 im Backlog) | 🔴 Ablauf wird nicht gelebt |
| Offene Aufgaben mit Sollstunden | **38 von 190** | 🔴 Fortschritt bleibt zwangsläufig leer |
| Zeiteinträge insgesamt | **34** | 🔴 Zeiterfassung überall an, nirgends benutzt |
| Aufträge mit Projekt verknüpft | **4 von 12** | 🔴 Kette zerrissen |
| Projekte mit Kunde | **5 von 24** | 🔴 |
| Aufgaben mit Kunde | **8 von 685** | 🔴 |
| Automatisierungsregeln | **3** | 🔴 praktisch ungenutzt |
| Aktivitäten | 167, **alle von Hand** | 🔴 |
| Webhooks (rein und raus) | **vorhanden** | ✅ **geprüft, Agent möglich** |

**Die Diagnose in einem Satz:** Nicht die Struktur ist kaputt — sie ist nur leer und unverbunden.

## Globale Randbedingungen

- **Produktivsystem.** Vor jeder Aufgabe eine Sicherung, zu jeder Aufgabe ein Rückweg. Nichts löschen, was sich archivieren lässt.
- **`stage_id` hat `ondelete='restrict'`** — eine Phase lässt sich **nicht** löschen, solange Aufgaben darauf zeigen. Immer erst umhängen, dann löschen.
- **`progress` ist ein Rechenfeld:** `(effective_hours + subtask_effective_hours) / allocated_hours`, sonst `0`. Es gibt keinen anderen Weg zur Fortschrittsanzeige als Sollstunden zu setzen.
- **Kein lokales Sprachmodell.** Am 01.08. gemessen: 373 CPU-Minuten für null Ergebnisse — und das war Einbettung, die billige Aufgabe. Anker und ProDesk haben je 5–6 GB frei. Das Gateway spricht bereits mit Anthropic und GitHub Copilot; Sprachverstehen ist gelöst.
- **Reihenfolge ist Absicht.** Aufgabe 5 (Agent) zuletzt: Ein Agent, der in ein unverbundenes System schreibt, beschleunigt nur das Durcheinander.
- Befehle als `ssh stock-pve "pct exec 140 -- docker exec frawotech-db-1 psql -U odoo -d FraWo_GbR -c \"<SQL>\""` oder über die Odoo-Oberfläche, wo angegeben.

---

## Aufgabe 1: Die 21 Review-Phasen zu einer zusammenführen

**Warum zuerst:** Solange „Review & Quality Gate" 21 verschiedene Dinge sind, ist keine projektübergreifende Auswertung möglich. Und es ist der einzige echte Strukturfehler — schnell behoben, sofort spürbar.

**Schnittstellen:**
- Liefert: eine geteilte Review-Phase, auf die sich Aufgabe 2 (Automatisierung) beziehen kann.

- [ ] **Schritt 1: Sicherung ziehen**

```sh
ssh stock-pve "pct exec 140 -- /usr/local/bin/odoo-sql-backup.sh"
ssh stock-pve "ls -lh /mnt/data_family/odoo-sql-dumps/ | tail -3"
```
Erwartet: frische Datei, **Größe deutlich über 1 MB**. Bei 0 Bytes abbrechen — genau dieser blinde Fleck hat den wochenlangen Sicherungsausfall verursacht.

- [ ] **Schritt 2: Ist-Zustand festhalten**

```sql
SELECT s.id, (SELECT count(*) FROM project_task_type_rel r WHERE r.type_id=s.id) AS projekte,
       (SELECT count(*) FROM project_task t WHERE t.stage_id=s.id AND t.active) AS aufgaben
FROM project_task_type s WHERE s.name->>'en_US' = '🔍 Review & Quality Gate' ORDER BY s.id;
```
Ergebnis wegschreiben. Erwartet: 21 Zeilen, zusammen 10 Aufgaben.

- [ ] **Schritt 3: Die niedrigste ID als Ziel bestimmen und alle Projekte anhängen**

```sql
WITH ziel AS (SELECT min(id) AS id FROM project_task_type WHERE name->>'en_US' = '🔍 Review & Quality Gate')
INSERT INTO project_task_type_rel (type_id, project_id)
SELECT (SELECT id FROM ziel), r.project_id
FROM project_task_type_rel r
JOIN project_task_type s ON s.id = r.type_id
WHERE s.name->>'en_US' = '🔍 Review & Quality Gate'
  AND r.type_id <> (SELECT id FROM ziel)
ON CONFLICT DO NOTHING;
```

- [ ] **Schritt 4: Aufgaben auf die Zielphase umhängen**

```sql
WITH ziel AS (SELECT min(id) AS id FROM project_task_type WHERE name->>'en_US' = '🔍 Review & Quality Gate')
UPDATE project_task SET stage_id = (SELECT id FROM ziel)
WHERE stage_id IN (SELECT id FROM project_task_type WHERE name->>'en_US' = '🔍 Review & Quality Gate')
  AND stage_id <> (SELECT id FROM ziel);
```
Erwartet: `UPDATE 10` (oder die in Schritt 2 gezählte Zahl).

- [ ] **Schritt 5: Reihenfolge und Einklappen setzen**

Die Review-Phase gehört zwischen „In Arbeit" (3) und „Blockiert" (4), also Reihenfolge 4 — und darf **nicht** eingeklappt sein, sonst gilt sie als abgeschlossen.
```sql
UPDATE project_task_type SET sequence = 4, fold = false
WHERE id = (SELECT min(id) FROM project_task_type WHERE name->>'en_US' = '🔍 Review & Quality Gate');
UPDATE project_task_type SET sequence = 5 WHERE id = 5;
UPDATE project_task_type SET sequence = 6 WHERE id = 6;
UPDATE project_task_type SET sequence = 7 WHERE id = 35;
```

- [ ] **Schritt 6: Die 20 leeren Duplikate löschen**

Erst jetzt möglich, weil keine Aufgabe mehr darauf zeigt:
```sql
DELETE FROM project_task_type
WHERE name->>'en_US' = '🔍 Review & Quality Gate'
  AND id <> (SELECT min(id) FROM project_task_type WHERE name->>'en_US' = '🔍 Review & Quality Gate')
  AND NOT EXISTS (SELECT 1 FROM project_task t WHERE t.stage_id = project_task_type.id);
```
Erwartet: `DELETE 20`. Schlägt es fehl, hängt noch eine Aufgabe dran — Schritt 4 wiederholen.

- [ ] **Schritt 7: Ergebnis messen**

```sql
SELECT s.name->>'en_US' AS phase, s.sequence, s.fold,
       (SELECT count(*) FROM project_task_type_rel r WHERE r.type_id=s.id) AS projekte
FROM project_task_type s WHERE s.user_id IS NULL
  AND (SELECT count(*) FROM project_task_type_rel r WHERE r.type_id=s.id) > 5
ORDER BY s.sequence;
```
Erwartet: **sieben** Zeilen in der Reihenfolge Backlog → In Planung → In Arbeit → Review → Blockiert → Erledigt → Abgebrochen. Review mit ~21 Projekten.

- [ ] **Schritt 8: Rückweg**

Falls etwas schiefgeht: Sicherung aus Schritt 1 zurückspielen. Der Eingriff ist auf `project_task_type`, `project_task_type_rel` und `project_task.stage_id` begrenzt.

---

## Aufgabe 2: Aktivitäten automatisch erzeugen

**Warum:** „Nächste Aktivität muss ich immer noch manuell anlegen." 167 Aktivitäten existieren, jede von Hand. Odoo kann das selbst.

**Schnittstellen:**
- Verbraucht: die geteilte Review-Phase aus Aufgabe 1.
- Liefert: Aktivitätstypen, auf die sich Aufgabe 5 (Agent) beziehen kann.

- [ ] **Schritt 1: Eigene Aktivitätstypen anlegen**

Menü: **Einstellungen → Diskussion → Aktivitätstypen → Neu**. Vier Typen mit Standardfristen:

| Name | `delay_count` / `delay_unit` | Zweck |
|---|---|---|
| Angebot nachfassen | 7 Tage | nach Angebotsversand |
| Technik-Check vor Termin | 3 Tage | vor Veranstaltung |
| Rückgabe prüfen | 1 Tag | nach Verleih |
| Rechnung stellen | 3 Tage | nach Abschluss |

- [ ] **Schritt 2: Kette einrichten**

Bei „Angebot nachfassen": `chaining_type = trigger`, `triggered_next_type_id` = ein zweiter Typ „Angebot nachfassen (2. Versuch)" mit `delay_count = 14`. Damit erzeugt das Abhaken der ersten Aktivität automatisch die zweite.

- [ ] **Schritt 3: Regel — Aufgabe geht in Review**

Menü: **Einstellungen → Technisch → Automatisierung → Automatisierungsregeln → Neu** (Entwicklermodus nötig).
- Modell: `project.task`
- Auslöser: **`on_stage_set`** („Stage is set to"), Phase = die Review-Phase aus Aufgabe 1
- Aktion: **Create Activity** (`next_activity`)
  - `activity_type_id` = „Rückgabe prüfen"
  - `activity_summary` = „Ergebnis abnehmen"
  - `activity_date_deadline_range` = 2, `activity_date_deadline_range_type` = `days`
  - `activity_user_type` = `specific`, `activity_user_id` = Wolf

⚠ **Nicht als gesichert behandeln:** `activity_user_type = generic` mit `activity_user_field_name` erwartet ein Feld, das auf **einen** Benutzer zeigt. Auf `project.task` heißt das Feld `user_ids` und ist eine **Mehrfachzuweisung** — ob Odoo damit umgehen kann, ist ungeprüft. Deshalb hier zunächst der feste Benutzer. Wer `generic` will, probiert es an einer Testaufgabe aus, bevor die Regel scharf geschaltet wird.

- [ ] **Schritt 4: Regel — Aufgabe geht in Blockiert**

Gleiche Stelle, zweite Regel:
- Auslöser `on_stage_set`, Phase = „🛑 Blockiert"
- Aktion **Create Activity**: Typ „Angebot nachfassen", Text „Blocker prüfen — ist er noch echt?", Frist **7 Tage**

**Begründung:** Am 27.07. waren 3 von 5 blockierten P0-Aufgaben längst erledigt — die Blocker-Texte waren Momentaufnahmen. Diese Regel sorgt dafür, dass jeder Blocker nach einer Woche noch einmal angefasst wird.

- [ ] **Schritt 5: Prüfen, dass es greift**

Eine Testaufgabe anlegen, in Review schieben, nachsehen:
```sql
SELECT a.summary, a.date_deadline, t.name FROM mail_activity a
JOIN project_task t ON t.id = a.res_id AND a.res_model = 'project.task'
ORDER BY a.create_date DESC LIMIT 3;
```
Erwartet: die eben erzeugte Aktivität. **Kommt nichts, ist die Regel nicht aktiv** — nicht weitermachen.

---

## Aufgabe 3: Fortschritt sichtbar machen

**Warum:** Die Anzeige ist nicht kaputt, sie hat keine Daten. `progress` rechnet `(effective_hours + subtask_effective_hours) / allocated_hours`. Ohne Sollstunden immer 0.

- [ ] **Schritt 1: Betroffene Aufgaben zählen**

```sql
SELECT p.name->>'en_US' AS projekt, count(*) AS ohne_sollstunden
FROM project_task t JOIN project_task_type s ON s.id=t.stage_id JOIN project_project p ON p.id=t.project_id
WHERE t.active AND NOT s.fold AND coalesce(t.allocated_hours,0)=0
GROUP BY 1 ORDER BY 2 DESC;
```

- [ ] **Schritt 2: Grundwert setzen — bewusst grob**

**Nicht** jede Aufgabe einzeln schätzen. Ein grober Wert, der später verfeinert wird, ist besser als gar keiner:
```sql
UPDATE project_task SET allocated_hours = 2
WHERE active AND coalesce(allocated_hours,0) = 0
  AND stage_id IN (SELECT id FROM project_task_type WHERE NOT coalesce(fold,false));
```

**Begründung:** Zwei Stunden als Vorgabe machen den Fortschritt sofort sichtbar. Wer eine Aufgabe anfasst, korrigiert den Wert nebenbei. Perfekte Schätzungen für 152 Aufgaben aufzustellen, würde niemand durchhalten.

- [ ] **Schritt 3: Prüfen**

```sql
SELECT count(*) FILTER (WHERE allocated_hours>0) AS mit_soll,
       count(*) FILTER (WHERE progress>0) AS mit_fortschritt, count(*) AS gesamt
FROM project_task t JOIN project_task_type s ON s.id=t.stage_id WHERE t.active AND NOT s.fold;
```
Erwartet: `mit_soll` = `gesamt`. `mit_fortschritt` bleibt zunächst niedrig — das steigt erst, wenn Stunden gebucht werden.

- [ ] **Schritt 4: Regel — Sollstunden bei neuen Aufgaben vorbelegen**

Automatisierungsregel: Modell `project.task`, Auslöser **`on_create`**, Aktion **Update Record**: `allocated_hours = 2`, nur wenn leer. Damit bleibt die Lücke geschlossen.

---

## Aufgabe 4: Die Kette verbinden — Auftrag zieht alles hinter sich her

**Warum:** Das ist der Kern des Wunsches „nicht nur ein Projekt anlegen, sondern die komplette Bürokratie". Odoo kann das ab Werk, es ist nur nicht eingestellt.

- [ ] **Schritt 1: Dienstleistungsprodukte auf automatische Projektanlage stellen**

Menü: **Verkauf → Produkte → Produkte**, je Produkt Reiter *Verkauf*, Feld **„Bei Auftrag erstellen"** (`service_tracking`):

| Produkt | Wert | Wirkung |
|---|---|---|
| `SRV-FACHKRAFT-TAG` | `task_in_project` | neues Projekt + Aufgabe je Auftrag |
| `SRV-HELFER-H` | `task_global_project` | Aufgabe im bestehenden Projekt |
| `SRV-TECHNIK-NV` | `task_in_project` | neues Projekt + Aufgabe |
| `FW-021` / `FW-020` Veranstaltungspauschale | `task_in_project` | neues Projekt + Aufgabe |

- [ ] **Schritt 2: Abrechnung nach geleisteten Stunden**

Bei denselben Produkten: **Abrechnungspolitik** = „Nach erfasster Zeit" (`service_policy = delivered_timesheet`). Damit wandern gebuchte Stunden automatisch als Liefermenge auf den Auftrag und von dort auf die Rechnung.

- [ ] **Schritt 3: Prüfen mit einem Testauftrag**

Neuen Verkaufsauftrag mit `SRV-FACHKRAFT-TAG` anlegen und bestätigen.
```sql
SELECT so.name AS auftrag, p.name->>'en_US' AS projekt, t.name AS aufgabe
FROM sale_order so LEFT JOIN project_project p ON p.id = so.project_id
LEFT JOIN project_task t ON t.project_id = p.id
ORDER BY so.id DESC LIMIT 3;
```
Erwartet: Projekt **und** Aufgabe automatisch entstanden. Testauftrag danach abbrechen.

- [ ] **Schritt 4: Kunde auf bestehende Projekte nachtragen**

19 von 24 Projekten haben keinen Kunden. Bei den Kundenprojekten (Sutter-Gartenfest, WP-Stockenweiler-3, Inselhalle, S000xx) über die Oberfläche nachtragen — interne Projekte (P0 Infrastruktur, Masterplan) brauchen keinen.

- [ ] **Schritt 5: Regel — Kunde vom Projekt auf die Aufgabe vererben**

Automatisierungsregel: Modell `project.task`, Auslöser **`on_create`**, Aktionstyp **„Python-Code ausführen"** (nicht „Update Record" — das kann keine Werte aus einem verknüpften Datensatz ziehen):
```python
for record in records:
    if not record.partner_id and record.project_id.partner_id:
        record.partner_id = record.project_id.partner_id
```
Behebt „8 von 685 Aufgaben haben einen Kunden" für alles Neue.

**Bestandsaufgaben nachziehen** — einmalig, nachdem Schritt 4 die Kunden an den Projekten gesetzt hat:
```sql
UPDATE project_task t SET partner_id = p.partner_id
FROM project_project p
WHERE p.id = t.project_id AND t.partner_id IS NULL AND p.partner_id IS NOT NULL AND t.active;
```

---

## Aufgabe 5: Der Agent — Chatter und Telegram

**Warum zuletzt:** Erst muss das System zusammenhängen. Ein Agent auf einem unverbundenen System macht das Durcheinander schneller, nicht kleiner.

**Am 02.08.2026 geprüft und bestätigt:** `webhook_url` auf `ir.actions.server` und `webhook_uuid` auf `base.automation` existieren in dieser Community-Instanz. Die Odoo-Doku führt Webhooks unter „Studio" (Enterprise) — der Code liegt aber im Basis-Framework.

- [ ] **Schritt 1: Dokumentationsrichtlinie schreiben, bevor irgendetwas automatisiert wird**

Als Odoo-Aufgabe in Projekt 1 (Masterplan), Titel „📐 Dokumentationsrichtlinie Chatter & Agent". Inhalt:

**Wohin was gehört:**
- **Chatter** = was passiert ist. Ereignisse, Entscheidungen, Messwerte. Nie Zustände.
- **Felder** = Zustände. Stunden, Fristen, Seriennummern, Zustand. Nie in den Namen, nie in die Prosa.
- **Notiz** = Dauerhaftes zum Objekt selbst. Betriebshinweise, offene Fragen.
- **Aktivität** = was als Nächstes zu tun ist, mit Frist und Person.

**Wie man den Agenten anspricht** (im Chatter oder per Telegram):
- `@agent Seriennummer XYZ für Raspberry Pi 4` → trägt ein
- `@agent 3 Stunden Aufbau` → bucht Zeit auf die Aufgabe
- `@agent neuer Auftrag: <Kunde>, <Datum>, <Leistung>` → legt Kette an
- `@agent erledigt` → Phase auf Erledigt, Bericht zurück

**Was der Agent nie ohne Rückfrage tut:** löschen, Preise ändern, Rechnungen stellen, Fremdeigentum anfassen.

- [ ] **Schritt 2: Ausgehenden Webhook einrichten**

Automatisierungsregel: Modell `mail.message`, Auslöser **`on_create`**, Bedingung: Text enthält `@agent`.
Aktion **Send Webhook Notification** (`webhook`):
- `webhook_url` = die OpenClaw-Adresse auf CT150
- `webhook_field_ids` = `body`, `model`, `res_id`, `author_id`

- [ ] **Schritt 3: Gegenrichtung prüfen**

Der Agent schreibt bereits über MCP zurück — Zugriff auf 19 Modelle besteht seit 02.08.2026. Kein weiterer Aufbau nötig.

- [ ] **Schritt 4: Erst mit einem Chat testen**

Wie beim Gedächtnis-Recall: **ein** Projekt, **ein** Chat. Erst wenn zehn Anweisungen fehlerfrei durchlaufen, freigeben.

- [ ] **Schritt 5: Kosten messen**

```sh
ssh anker-pve "pct exec 150 -- docker logs --since 24h openclaw 2>&1 | grep -c 'model-fetch. start'"
ssh anker-pve "pct exec 150 -- docker logs --since 24h openclaw 2>&1 | grep -i 'usage limit' | tail -3"
```
Das Anthropic-Konto lief am 30.07. ins Limit. **Steht bei der zweiten Zeile etwas, sofort zurücknehmen.**

---

## Was bewusst NICHT gemacht wird

| Idee | Warum nicht |
|---|---|
| **Ollama / lokales Sprachmodell** | Am 01.08. gemessen: 373 CPU-Minuten, null Ergebnisse — und das war nur Einbettung. 5–6 GB frei je Knoten. Das Gateway spricht bereits mit Anthropic und Copilot. |
| **Qdrant / eigene Vektordatenbank** | Aufgabe #342 gilt als erledigt, das System existiert nicht mehr. Die lokale Suche im Gateway leistet dasselbe, kostenlos. |
| **RAG über Odoo-Inhalte** | Aufgaben, Geräte und Produkte sind strukturiert — eine Abfrage ist genauer und billiger als eine Ähnlichkeitssuche. RAG nur für Fließtext. |
| **Odoo-Vermietmodul (Enterprise)** | Bei 15 Verleihartikeln steht die Lizenz in keinem Verhältnis. |
| **Case-Verwaltung, Ersatzteil-Inventar, Rüstzeit je Gerät** | Extern recherchiert: bei dieser Größe Pflegeaufwand ohne Gegenwert. |
| **Die 66 persönlichen To-do-Phasen anfassen** | Legt Odoo pro Benutzer an. Normal. |

---

## Rückweg für den ganzen Plan

Jede Aufgabe beginnt mit einer Sicherung. Zurückspielen:
```sh
ssh stock-pve "ls -lh /mnt/data_family/odoo-sql-dumps/ | tail -5"
```
Automatisierungsregeln lassen sich einzeln deaktivieren (`active = false`), ohne die Daten anzufassen — das ist der schnellste Rückweg bei unerwartetem Verhalten.
