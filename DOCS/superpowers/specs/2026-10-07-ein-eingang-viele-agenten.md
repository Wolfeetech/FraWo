# Ein Eingang, viele Agenten: Arbeitsanweisung rein, der passende Agent setzt um

Stand 07.10.2026 · Claude · Odoo #1966 · baut auf #1965 (Kanäle, Hermes-Pilot) auf

**Wolf 07.10.:** „Ich will nicht ständig am PC zwischen den Anbietern wechseln … Arbeitsanweisung kommt in den Raum, die Agenten (Codex, Claude, Antigravity, Ollama) schauen selbstständig, wer am geeignetsten ist, und setzen um … nur noch über Telegram oder Open WebUI einschicken.“

## 1. Ist-Zustand: warum es holprig ist

| Problem | Folge |
|---|---|
| Jeder Agent hat seine eigene Oberfläche (Claude Code am StudioPC, Codex, Antigravity-IDE, Jarvis/Telegram, Open WebUI) | Wolf ist der Verteiler und muss am PC sitzen |
| Es gibt keine Warteschlange. Odoo ist Aufgaben-SSOT, aber kein Agent holt sich dort selbst Arbeit ab | Aufträge bleiben liegen, bis Wolf eine Sitzung öffnet |
| Claude und Codex laufen nur interaktiv auf Wolfs Rechner. Die Sicherheitssperre verlangt dann `!`-Befehle von Wolf | Wolf tippt Befehle ab, die ein Agent vorbereitet hat |
| Peer-Review läuft über @-Erwähnungen an Jarvis | Fällt Jarvis aus (#1964), hängt alles |
| Zugangsdaten verstreut | gelöst seit #1931 (Vaultwarden agent@) |
| Kanäle vermischt | gelöst seit #1965 |

## 2. Soll-Bild

```
 Wolf ──► Telegram (Hermes) ─┐
      ──► Open WebUI ────────┼──► 1 EINGANG: Auftrag als Odoo-Aufgabe (Projekt 50, Stage „Neu“)
      ──► Odoo direkt ───────┘          │  Felder: Ziel, Fertig-wenn, Risiko, Freigabe nötig?
                                          ▼
                              2 VERTEILER (Regeln zuerst, KI nur bei Unklarheit)
                                 setzt Schlagwort „🔒 <Agent>“ + Prüfer
                                          ▼
     ┌────────────┬──────────────┬───────────────┬────────────────┐
     │ Claude     │ Codex        │ Ollama        │ Antigravity     │
     │ headless   │ headless     │ lokal         │ nur interaktiv  │
     │ (Server)   │ (Server)     │ (OptiPlex/    │ (Wolf/IDE)      │
     │            │              │  StudioPC)    │                 │
     └────────────┴──────────────┴───────────────┴────────────────┘
                                          ▼
                              3 ERGEBNIS + NACHWEIS im Odoo-Chatter
                              4 AUTOMATISCHES REVIEW durch einen ANDEREN Agenten
                              5 Rückmeldung an Wolf: Telegram „FraWo Info“ (fertig) bzw.
                                Freigabe-Knopf „Ja/Nein“, wenn etwas Riskantes ansteht
```

### Wer kann was im Hintergrund (Stand der Technik 10/2026)

| Agent | ohne Wolf am PC? | Stärke | Einsatz |
|---|---|---|---|
| **Claude Code** | ja, `claude -p` bzw. Agent SDK, headless auf einem Server, eigener Arbeitsordner und Rechte-Regeln | Server, Skripte, Odoo-Logik, Analysen, lange Aufgaben | Hauptarbeiter Infrastruktur und Backend |
| **Codex** | ja, `codex exec` headless mit Wolfs Abo | Code, Reviews, schnelle Umsetzungen | Zweitarbeiter und **Prüfer** für Claude-Arbeit |
| **Ollama** (lokal) | ja | billig, privat, schnell, aber schwach | Einordnen, Zusammenfassen, Formulieren (Alarme, Briefing). **Nie** Umsetzung |
| **Antigravity** | **nein**, IDE ohne Hintergrundbetrieb | Web/Frontend mit Wolf zusammen | nur auf ausdrücklichen Wunsch, nicht im Automatik-Pool |
| **Hermes/Jarvis** | ja | Telegram, Cron, Gedächtnis | **Empfang und Verteiler**, Rückfragen an Wolf, kein Bauen |

### Verteil-Regeln (deterministisch, die KI entscheidet nur den Rest)

| Auftragsart (Stichwort/Projekt) | Ausführer | Prüfer |
|---|---|---|
| Server, Netz, Backup, Monitoring, Odoo-Datenpflege | Claude | Codex |
| Website, Frontend, Code-Feature | Codex | Claude |
| Recherche, Angebote, Texte | Claude | Wolf (Stichprobe) |
| Einordnen, Zusammenfassen, Briefing | Ollama | – |
| Unklar | Verteiler fragt Wolf mit **einer** Telegram-Frage und 2–3 Knöpfen | – |

### Sicherheitsgrenzen (bleiben hart)

- Hintergrund-Agenten haben eigene, enge Rechte: ein Server-Konto je Agent, Secrets nur über `agent@` und Vaultwarden, eine Erlaubt-Liste je Aufgabenart.
- **Freigabe per Telegram-Knopf** vor:
  - Löschen
  - Neustart von Kernservern
  - Firewall- und Netzänderungen
  - Geld
  - Nachrichten an Dritte

  Ersetzt die heutigen `!`-Befehle.
- Shelly 10.4.0.11 und die Liste der Roten Linien aus AGENTS.md gelten auch für Hintergrund-Agenten. Sie stehen technisch in deren Rechte-Regeln.
- Jeder Lauf schreibt Start, Ergebnis und Kosten in den Chatter. Kein stiller Lauf.

## 3. Umsetzung in Stufen

| Stufe | Inhalt | Dauer |
|---|---|---|
| 0 | Aufräumen (diese Woche): Kanäle ✅, Jarvis reparieren bzw. Hermes-Pilot (#1964/#1965), Drive/Paperless/Nextcloud fertig | läuft |
| 1 | **Eingang:** Hermes nimmt Aufträge aus Telegram an und legt sie strukturiert in Odoo an. Open WebUI bekommt dafür ein Werkzeug „Auftrag an FraWo“ | 2–3 Tage |
| 2 | **Arbeiter-Rechner:** eigener Container „agent-runner“ (OptiPlex) mit Claude Code headless und Codex CLI, Rechte-Regeln, Repo-Klon, Odoo-MCP, `frawo-secret` | 2 Tage |
| 3 | **Verteiler:** Odoo-Automatik bzw. Hermes-Cron holt neue Aufträge, setzt den Ausführer nach Regeltabelle und startet den Lauf. Ein Auftrag läuft zur Zeit pro Agent | 2 Tage |
| 4 | **Freigabe-Knöpfe** in Telegram (Ja/Nein) für riskante Schritte, und automatisches Kreuz-Review | 2 Tage |
| 5 | Probebetrieb 1 Woche mit Messgrößen (Durchlaufzeit, Nacharbeit, Kosten, Fehlläufe), danach Regeln nachschärfen | 1 Woche |

**Kosten:** Claude und Codex laufen über die vorhandenen Abos bzw. den API-Schlüssel. Das neue Risiko ist ein Abo-Limit, wenn viele Aufträge parallel laufen. Deshalb gilt die Regel „ein Auftrag pro Agent gleichzeitig“, und Ollama übernimmt alles Leichte.

## 4. Ehrliche Grenzen

- **Antigravity** lässt sich nicht im Hintergrund betreiben. Dafür bleibt es bei „Wolf öffnet es bei Bedarf“.
- Hintergrund-Agenten **ohne** Freigabe-Knopf dürfen nichts Riskantes. Manche Aufgaben brauchen also weiterhin ein kurzes „Ja“ von Wolf, dann aber per Knopf am Handy statt per PC.
- Die Qualität hängt am Auftrag. Der Eingang fragt deshalb immer nach „Fertig, wenn …“, notfalls mit einer Rückfrage.
