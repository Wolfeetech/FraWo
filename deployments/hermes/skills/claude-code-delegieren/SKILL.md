---
name: claude-code-delegieren
description: Größere Analyse-, Text- oder Code-Aufträge an Claude Code (Wolfs Claude-Abo) weitergeben, wenn sie mehrere Schritte, viele Dateien oder lange Ausarbeitung brauchen. Nicht für kurze Fragen.
---

# An Claude Code weitergeben

Du (Hermes) denkst mit Codex. Für **große Ausarbeitungen** nutzt du zusätzlich Wolfs Claude-Abo über das offizielle Programm Claude Code. Es läuft auf diesem Rechner (CT160) und hat **keinen** Zugang zu Servern, nur zum Repo-Klon `~/FraWo` (lesen).

## Wann

- **Weitergeben:** Konzepte, Angebote, längere Texte, Code-Entwürfe, Repo-Analysen über viele Dateien, Zweitmeinung zu einem Review.
- **Nicht weitergeben:** kurze Antworten, Odoo-Abfragen (die machst du selbst mit dem Odoo-Werkzeug), alles, was Server ändern würde.

## Wie

```bash
cd ~/FraWo && git pull -q 2>/dev/null
timeout 1200 claude-abo -p "<Auftrag, vollständig, auf Deutsch, mit 'Fertig, wenn …'>" \
  --permission-mode plan --output-format text 2>&1 | tail -200
```

- `--permission-mode plan`: Claude Code darf nur lesen und planen, nichts ausführen oder ändern.
- `claude-abo` holt den Abo-Schlüssel selbst aus `~/.hermes/.env`. Gib ihn **nie** aus.
- Antwortet Claude Code mit Limit- oder Anmeldefehler (`usage limit`, `401`, `rate limit`), dann erledige den Auftrag selbst und sag Wolf in einem Satz, dass Claude gerade nicht verfügbar war.

## Danach

- Das Ergebnis **nicht ungeprüft** weiterreichen. Lies es, kürze es auf das Wesentliche und prüfe Behauptungen gegen Odoo bzw. das Repo.
- Wolf bekommt die Kurzfassung. Langes kommt als Kommentar an die passende Odoo-Aufgabe, mit dem Hinweis „ausgearbeitet mit Claude Code“.
