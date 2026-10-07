# Kanäle trennen und Agent-Plattform prüfen (OpenClaw → Hermes?)

Stand 07.10.2026 · Claude · Odoo #1965 · Anlass Wolf: „Jarvis sendet seit Tagen kaum noch sinnvolle Nachrichten … mehrere Schnittstellen, klar klären welcher Kanal sendet … evtl. doch besser auf Hermes wechseln? Prüfen.“

## 1. Befund

### 1.1 Wer schreibt Wolf heute über Telegram

| Absender | Wo | Was | Wann |
|---|---|---|---|
| Jarvis (OpenClaw) | CT150 | Chat, Abendfragen, Antworten auf Odoo-Erwähnungen (`--deliver` an Telegram) | jederzeit |
| Alarm-Formatter | CT155 | Prometheus-Alarme (Ollama formuliert) | bei Alarm |
| monitoring-watchdog | Anker und ProDesk | Wächter, wenn Monitoring selbst ausfällt | bei Ausfall |
| Backup-TÜV | Anker | Sicherungsprüfung | täglich 08:00 bei Fehler |
| Morgenbriefing | ProDesk | `frawo-daily-briefing.py` | täglich 06:30 |
| Sendungs-Titelliste | ProDesk | Radio-Titellisten | nach Plan |
| Odoo-Addon `frawo_agent` | CT140 | Anker-Tracker | bei Ereignis |
| healthchecks.io | extern | Totmann-Schalter | bei Ausfall |

Alle landen im **selben Chat**, viele über denselben Bot (`@Frawo_bot`). Wolf kann weder sehen, wer schreibt, noch nach Wichtigkeit filtern. Ein dringender Alarm sieht genauso aus wie eine Plauderei von Jarvis.

### 1.2 Zustand Jarvis (#1964)

- Seit 05.10. 19:03 keine Beiträge mehr in Odoo. Die Erwähnungen kommen an (HTTP 200, „Agent triggered successfully“), aber es kommt nichts zurück.
- Im Log: 160 Modellaufrufe an das kleine lokale StudioPC-Modell, „fallbacks disabled by user model override“, unsinnige Werkzeugaufrufe (`video_generate`). Ein Sitzungs-Override hat Jarvis vermutlich vom Codex-Modell auf das lokale Modell gezwungen.
- Dauerbaustellen seit Juli: Kostenexplosion 500:1 (`contextInjection`), IPv6/Telegram-Aussetzer, Voll-Reload bei jedem `config set`, Agent-DB 509 MB (Mitte September 30 MB), Gateway-Token im Klartext (#1464).

## 2. Hermes Agent (Nous Research) gegen unseren Bedarf

Quellen: [hermes-agent.ai](https://hermes-agent.ai/), [Practitioner's Reference](https://blakecrosley.com/guides/hermes), [Review](https://dupple.com/reviews/hermes-agent). MIT-Lizenz, seit 02/2026, sehr aktive Entwicklung (v0.2x).

| Bedarf FraWo | OpenClaw heute | Hermes laut Doku |
|---|---|---|
| Codex-Abo (Wolfs ChatGPT-OAuth) | ja | ja (OAuth OpenAI Codex), dazu Claude Pro/Max und Copilot |
| Ollama lokal (OptiPlex/StudioPC) | ja | ja, **Achtung**: Kontext standardmäßig nur 4.096, `OLLAMA_CONTEXT_LENGTH` setzen |
| Telegram | ja, ein Bot | ja. **Profile pro Kanal** mit getrennter Konfiguration, Speicher und Secrets im selben Gateway |
| Geplante Aufgaben | Cron mit Nachholen nach Neustart (Abendfragen 13:51) | Cron, Lieferung an beliebigen Kanal, „Monitor-Modus“ ohne LLM-Aufruf, wenn sich nichts geändert hat |
| Odoo-Anbindung | eigener Webhook-Handler + Odoo-MCP | MCP voll, gleicher Odoo-MCP nutzbar |
| Secrets | Token im Klartext in `openclaw.json` | **Bitwarden-SecretSource**: Werte nie als Argument und nie gespeichert. Passt zu `agent@` in Vaultwarden (#1931) |
| Sicherheitsfreigaben | wenig | Freigabe gefährlicher Befehle durch zweites Modell, Schreibschutz für Gedächtnis- und Regeldateien |
| Umzug | – | `hermes claw migrate` übernimmt den OpenClaw-Bestand (30+ Kategorien) |
| Betrieb | Docker auf CT150 | Docker, Installer oder Nix. Python 3.11 + Node 26 |

**Risiken Hermes:** sehr junges, schnell wechselndes Projekt (Breaking Changes: pip abgekündigt, Node 26 Pflicht). Die Migration bringt den heutigen Wildwuchs mit (Gedächtnis, Crons), wenn man nicht bewusst aussortiert. Dazu ein neues Werkzeug mit Lernkurve für alle Agenten.

## 3. Empfehlung

**Beides trennen: Kanäle sofort ordnen, Plattform per Pilot entscheiden. Kein Big-Bang.**

### Schritt A: Kanäle trennen (unabhängig von der Plattform, 1 Tag)

| Kanal | Inhalt | Regel |
|---|---|---|
| 🔴 **FraWo Alarm** (eigener Bot, Benachrichtigung laut) | Alertmanager, Watchdog, Backup-TÜV, healthchecks | nur Handlungsbedarf, Entwarnung im selben Faden |
| 📋 **FraWo Info** (Telegram-Kanal, stumm) | Morgenbriefing, Titellisten, Tracker | lesen, wann es passt |
| 💬 **Jarvis** (Chat-Bot) | Gespräch, Fragen an Wolf | nur Jarvis, keine Maschinenmeldungen |
| 🗂️ **Odoo-Chatter** | Arbeitsnachweise, Reviews unter Agenten | nie nach Telegram spiegeln |

Jede automatische Nachricht beginnt mit dem Absender (`[Backup-TÜV]`, `[Alarm]` …). Der Bot-Token je Kanal liegt in Vaultwarden (`agent@`).

### Schritt B: Jarvis sofort stabilisieren

Sitzungs-Override zurücksetzen, sodass wieder das Default-Modell Codex `gpt-5.6-sol` gilt. Danach eine Testerwähnung in Odoo. Das klärt, ob der Rest überhaupt ein Plattformproblem ist.

### Schritt C: Hermes-Pilot (1 Woche, parallel)

- **Aufbau:** Neuer Container (oder Profil auf CT150), Codex-OAuth (Login nur Wolf), Odoo-MCP, Bitwarden-SecretSource über `agent@`. **Nicht** migrieren, sondern frisch mit genau zwei Aufgaben:
  1. Peer-Reviews in Odoo
  2. Morgenbriefing in den Info-Kanal
- **Messgrößen gegen OpenClaw:**
  - Antwortquote auf Erwähnungen
  - Anteil sinnvoller Antworten (Wolf-Urteil)
  - Fehlläufe
  - Kosten bzw. Abo-Verbrauch
  - Wartungsaufwand
- **Entscheidung nach 7 Tagen:**
  - **Hermes ersetzt Jarvis:** dann Migration der übrigen Aufgaben, bewusst ausgesucht.
  - **Oder:** Hermes kommt weg und OpenClaw wird aufgeräumt.

## 4. Was Wolf entscheiden muss

1. Kanäle trennen wie in Schritt A (zwei neue Bots/Kanäle anlegen, das macht Wolf in Telegram per @BotFather)?
2. Hermes-Pilot nach Schritt C freigeben (Codex-Login macht Wolf)?
