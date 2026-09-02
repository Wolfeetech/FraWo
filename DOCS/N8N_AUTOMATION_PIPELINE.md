# n8n — Stand 02.09.2026

> Ersetzt die alte Fassung (verwies auf IP `10.1.0.110` und drei Workflows,
> die inzwischen inaktiv sind — beides überholt).

## Instanz

CT110 (stockenweiler-pve), Docker `docker compose` unter `/opt/n8n/`, intern
`http://10.1.0.100:5678`, extern `https://n8n.frawo.tech`. Datenbank: SQLite
(`/opt/n8n/data/database.sqlite`), kein Postgres.

**Version:** seit 02.09.2026 fest auf `1.123.76` gepinnt (vorher `:latest`
im Compose-File, dadurch monatelang nicht neu gezogen — real lief 1.122.5).
Bewusst **nicht** auf n8n 2.x gesprungen: 2.0 ist ein Breaking-Change-Major
(Task Runners laufen ab 2.0 nicht mehr im Hauptcontainer, Code-Nodes
brauchen einen separaten `n8nio/runners`-Container). Die aktive
Spesen-Pipeline (siehe unten) nutzt einen Code-Node — der 2.0-Umstieg ist
ein eigenes, noch nicht terminiertes Vorhaben.

## Workflows (Stand 02.09.2026, per DB geprüft)

| Workflow | Aktiv | Typ |
|---|---|---|
| ⚡ Paperless-ngx → Odoo hr.expense Auto-Pipeline | ✅ | Webhook → Code → HTTP (Odoo JSON-RPC) |
| MTV Track Voting | ✅ | Cron (alle 3 Min.) → HTTP an Odoo `/radio/api/vote-winner` |
| Radio Steering Automation | ❌ | — |
| High Rating Notification | ❌ | — |
| Server Watchdog | ❌ | — |

🔴 **Bekannter Fehler, unabhängig vom Versions-Update (bereits vor dem
02.09.2026 kaputt, per Backup-Vergleich bestätigt):** Der Webhook der
Paperless→Odoo-Pipeline (`POST /webhook/paperless-expense`) ist **nicht
registriert** — `webhook_entity` in der DB war schon vor dem Update leer.
Bei Aktivierung schreibt n8n einen fehlerhaften zusammengesetzten Pfad
(`<workflowId>/<Node-Name>/<path>` statt nur `<path>`) — Ursache vermutlich
eine sehr alte, nie über die Editor-UI neu gespeicherte Workflow-Version
(bekanntes n8n-Verhalten: Aktivierung per API/CLI registriert Webhooks
teils falsch, nur ein echtes Speichern im Editor berechnet den Pfad neu).
**Fix:** Workflow einmal in der n8n-UI (`https://n8n.frawo.tech`, Login
`wolf@frawo.tech`) öffnen und speichern (auch ohne inhaltliche Änderung) —
das erzwingt eine korrekte Neu-Registrierung. Ohne dieses Login konnte der
Agent den Fix nicht selbst durchführen. **Bis dahin: Belege aus Paperless
lösen KEINE Odoo-Spesenbuchung aus**, die Pipeline lief vermutlich noch nie.

Sicherung vor dem Update liegt unter `/opt/n8n/data.backup-20260902`
(CT110) — Rückweg bei Problemen.

## Bekannte Stolperfalle

Compose-File nutzte `image: n8nio/n8n:latest` ohne Auto-Update-Mechanismus
(kein Watchtower) — dadurch lief die Instanz unbemerkt Monate hinter der
aktuellen `latest`, bis die n8n-UI selbst den Rückstand anzeigte. Jetzt auf
festen Tag gepinnt — künftige Updates sind ein bewusster Schritt
(Tag in `/opt/n8n/docker-compose.yml` ändern, `docker compose pull && up -d`),
kein stiller Drift mehr.
