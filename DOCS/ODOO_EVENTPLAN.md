# Odoo-Eventplan aus bestehenden Draw.io-Vorlagen

Agenten-Runbook zu Odoo #1862. Quelle der Eventdaten bleibt Odoo; erzeugte Pläne
sind abgeleitete Momentaufnahmen, keine zusätzliche Aufgaben- oder Materialverwaltung.

## Ausführung

Python 3.10 oder neuer, keine zusätzlichen Python-Pakete nötig. Aus dem Repo:

```powershell
python scripts/odoo_eventplan.py --task 1628 --output Eventplan.drawio
python scripts/odoo_eventplan.py --task 1628 --output Eventplan.drawio --publish
```

`--task` liest Odoo. `--publish` schreibt zusätzlich einen privaten Anhang und
eine interne Notiz an genau diese Aufgabe. Zugang ausschließlich durch einen aus
Vaultwarden in den Prozess injizierten `ODOO_RPC_API_KEY` bzw. `ODOO_API_KEY`.
Keinen Schlüssel in Befehle, Dateien oder Chatter kopieren. Optional:
`ODOO_RPC_URL`, `ODOO_RPC_DB`, `ODOO_RPC_USER`; öffentliche URLs benötigen HTTPS.

Ein Agent mit Odoo-MCP, aber ohne injizierten XML-RPC-Schlüssel, kann die gleichen
Quellfelder über MCP lesen und eine lokale, temporäre JSON-Momentaufnahme verwenden:

```powershell
python scripts/odoo_eventplan.py --input event.json --output Eventplan.drawio
```

JSON-Felder: `task_id`, `project_name`, `event_date` (ISO-Datum oder null),
`location`, `technicians` (Namensliste), `order_name`, `order_state`, `items`.
Jede Position enthält `product_id`, `name`, `type`, `quantity`, `uom`.
Vor einer Veröffentlichung die Quelle erneut lesen. Keine dauerhaften Exporte als
zweite Wahrheit pflegen. Über MCP dieselbe stabile Anhang-Identität, Privatstatus
und Zurückleseprüfung wie im Skript verwenden; nicht bei jedem Lauf neu anlegen.

## Daten und Sicherheitsgrenzen

- Event-Kopfdaten aus Projekt und expliziten `Datum:`-/`Ort:`-Angaben der Aufgabe.
  Ein Abgabetermin ist **kein** Veranstaltungsdatum. Nicht belegbare Werte bleiben offen.
- Techniker aus der Aufgabenzuweisung; Koordinatoren mit `🤖` im Namen werden ausgeschlossen.
- Material aus dem verknüpften Verkaufsauftrag: Sachartikel, positive Bestellmengen,
  originale Einheit. Dienstleistungen, Anzahlungen und Abschnittszeilen werden nicht
  als Geräte eingeplant. Liefermengen/Reservierungen werden nicht behauptet.
- Die vier Originalvorlagen werden nicht verändert. Zusätzlich entsteht eine
  vollständige Materialseite. Namensregeln aktivieren bekannte Gerätefamilien;
  nicht zugeordnete Sachartikel bleiben vollständig auf der Materialseite sichtbar.
- Grüne Blöcke sind **Mengen-Gruppen**, keine einzelnen physischen Gerätepositionen.
  Raumaufteilung, Kabelwege, Anschlüsse, Strombelastung und Lautsprecher-Presets
  bleiben unbestätigt. Grau bedeutet Vorlage, nicht gebuchtes Material.
- DMX-Werte werden nicht geraten. Optional kann eine **einzeln aufgelöste** Position
  `dmx: {"universe": 1, "start": 20, "channels": 16}` enthalten. Grenzverletzungen,
  Überlappungen und mehr als ein Gerät pro expliziter Adresse werden abgewiesen.
  Der Odoo-Leser erfindet solche Angaben nicht aus Produktnamen.
- Nicht aufgelöste Kombi-Produkte und nicht bestätigte/fehlende Aufträge werden
  sichtbar gekennzeichnet. Ein generierter Plan ist keine technische Freigabe.
- Kein Dienst, Cron, Webhook, Bot, automatischer Massendurchlauf oder Server-Umbau.
  Ein bestehender Agent kann die Operation nach expliziter Auswahl eines Events ausführen.

## Veröffentlichung und Bearbeitung

Stabile Anhang-Identität: `res_model=project.task`, `res_id=<task_id>`,
`name=FraWo_Eventplan_<task_id>.auto.drawio`, `public=False`.
Vorhandene generierte Dateien werden aktualisiert; mehrdeutige Identitäten führen
zum Abbruch. Inhalt, Zuordnung und Privatstatus werden **am Ziel zurückgelesen**.
Der Plan selbst enthält die Quell-Aufgaben-ID; eine andere Zielaufgabe wird abgewiesen.
Ein SHA-256-Marker in der Notiz verhindert identische Wiederholungsnotizen.
Ein Abbruch zwischen Anhang und Notiz wird beim erneuten Lauf nachgeholt.
Keine parallelen Veröffentlichungen derselben Aufgabe starten.

Der Bearbeitungslink verwendet `https://frawo.tech/draw/#R...`, nicht einen
öffentlichen Odoo-Anhang. Das URL-Fragment enthält die vollständige Momentaufnahme
und gehört nicht in öffentliche Chats. Es wird nicht als HTTP-Query übertragen,
kann aber vom Editor und von Browser-Erweiterungen gelesen werden.
Offizielle Referenz: [Draw.io Location-Hash](https://www.drawio.com/docs/reference/supported-location-hash-properties/).

Bearbeitete Pläne **separat speichern und an dieselbe Aufgabe hängen**. Der
`*.auto.drawio`-Anhang ist die maschinell erzeugte Ausgangsversion und wird bei
erneuter Befüllung ersetzt. Der Link schreibt Änderungen nicht automatisch zurück
nach Odoo. Für eine echte Odoo-Bedienfläche oder bidirektionales Speichern ist
eine separat geprüfte Integration nötig; diese ist hier nicht eingebaut.

## Prüfung und Freigabe

```powershell
python -m pytest scripts/test_odoo_eventplan.py scripts/test_odoo_anhang.py -q -p no:cacheprovider
```

Abgedeckt: originale Vorlagen, Kopfdaten, Mengen, Sachartikel-Abgrenzung,
fehlende Angaben, Plaintext-Labels, DMX-Grenzen/Kollisionen, Link-Roundtrip,
deterministische Ausgabe, private/idempotente Anhang-Veröffentlichung,
Zurücklesefehler, falsche Zielaufgabe und unterbrochene Chatter-Zustellung.

Realer Abnahmefall: Event #1628 / S00057, 31.10.2026, Kressbronn, Wolf und Franz.
Der Auftrag enthält nur zwei Dienstleistungen. Erwartung: korrekte Kopfdaten,
**keine erfundene FraWo-Technik** aus der generischen Checkliste. Die Technik
stellt laut Eventbeschreibung der Auftraggeber.

Vor produktiver Freigabe: unabhängiger Agent prüft Code und echte Anhänge,
öffnet alle fünf Seiten im vorhandenen Draw.io-Editor und prüft mobile Darstellung
sowie PDF-Export. Automatisierte Tests beweisen nicht die Browser-Bedienbarkeit.
Odoo #1862 bleibt bis zum Review-OK in Arbeit. Der Zugang zum XML-RPC-Modus ist
zusätzlich auf dem späteren Ausführungsrechner zu prüfen; MCP-Veröffentlichung
ist kein Nachweis für einen dort vorhandenen API-Key.
