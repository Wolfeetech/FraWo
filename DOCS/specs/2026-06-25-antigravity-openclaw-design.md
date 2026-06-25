# Design: Antigravity-Workspace + OpenClaw-Relokation

**Stand: 2026-06-25. Ziel: Jarvis-Vision — OpenClaw als Multi-Channel-Orchestrator, der Arbeit an "Agent" delegiert.**

## Kontext

OpenClaw lief bisher auf `frawo-docker-1` (Stockenweiler, ~150kbit gedrosselt, faktisch abgeschrieben — "wird wohl nix mehr"). Die zugehörigen Odoo-Tasks #578/#127 sind veraltete Boilerplate-Einträge ohne echten Status. Antigravity (lokale IDE auf StudioPC, bereits installiert, aber nicht projektspezifisch konfiguriert) soll die Entwicklungsumgebung für OpenClaw werden.

## Architektur

```
Wolf ──Telegram──┐
                  ├──> OpenClaw (Docker-Container, anker-pve/ThinkCentre)
Odoo-Discuss ─────┘         Modell: GPT-5 primär, Claude-Haiku Fallback
                            │
                            ▼
                    Odoo project.task (Tag 🤖 Agent-Queue)
                            │
                            ▼
              frawo_agent-Cron (einfach) ODER Claude-Code-Session (komplex)
                            │
                            ▼
                  post_message Ergebnis → OpenClaw meldet an Wolf zurück
```

## Komponenten

### 1. OpenClaw-Container (neu, anker-pve)
- Neuer LXC-Container auf `anker-pve` (100.69.179.87) — gewählt wegen mehr RAM-Headroom (~9GB frei vs. ProDesk-RAM-Wand, bekanntes OOM-Risiko dort) und niedrigerer Risiko-Exposition (kein produktiver Geld-/Kundendienst dort).
- Docker statt nacktem npm-Install auf dem Host — eigenes minimales `Dockerfile` (`FROM node:22`, `npm install -g openclaw`), `docker-compose.yml` mit `restart: unless-stopped`. Konsistent mit der Docker-Compose-Konvention von CT140 (Odoo) und AzuraCast.
- Config (`openclaw.json`) als Volume gemountet, Secrets (GPT-5-Key, Telegram-Token) über `.env`-Datei außerhalb von Git, analog zu `.smbcreds`-Pattern anderswo im Estate.
- Modell-Config: `primary: openai/gpt-5` (oder aktuell verfügbares Top-Modell, exakte Modell-ID zur Implementierungszeit prüfen), `fallback: anthropic/claude-haiku-4-5`.
- Kanäle v1: Telegram (Bot @Frawo_ClawBot wiederverwenden, Token-Gültigkeit prüfen vor Neuanlage), Odoo-Discuss-Bot (neu zu bauen — kein bestehender Code gefunden trotz Erwähnung in #608), Odoo-Skill (Task erstellen/lesen über die bestehende Odoo-MCP-artige REST-API oder XML-RPC).

### 2. Odoo-Identität für OpenClaw
- Neuer Odoo-User **"🦞 OpenClaw"**, getrennt von "🤖 Agent" (UID 7). OpenClaw postet als Dispatcher/Channel-Layer, Agent postet als Ausführender. Verhindert Vermischung in der Activity-Historie.

### 3. Antigravity-Workspace
- Eigener **dauerhafter** lokaler Git-Clone von `Wolfeetech/FraWo` unter `C:\Users\StudioPC\Workspace\FraWo` (nicht die Wegwerf-Temp-Clones, die Claude-Code-Sessions pro Lauf anlegen) — Antigravity braucht einen stabilen Pfad für IDE-State/Extensions/Workspace-Settings.
- MCP-Verbindung auf Odoo (gleicher Server wie bei Claude Code, gleicher API-Key).
- SSH-Zugriff auf `anker-pve` für Container-Management (Alias existiert bereits: `anker-pve`/`pve-anker` in `~/.ssh/config`).
- Kurze `ANTIGRAVITY_SETUP.md` im Repo: Workspace-Pfad, SSH-Alias, Docker-Compose-Befehle für den OpenClaw-Container, Verweis auf `AGENT_ONBOARDING.md` für gemeinsame Konventionen/Sicherheitsregeln (keine Duplizierung).

## Datenfluss (v1)

1. Wolf schreibt OpenClaw via Telegram oder Odoo-Discuss.
2. OpenClaw (GPT-5) beantwortet Triviales direkt, oder legt einen `project.task` an (Tag 🤖 Agent-Queue, Owner OpenClaw-User).
3. Ausführung durch `frawo_agent`-Cron (einfache, klar definierte Fälle) ODER eine manuell gestartete Claude-Code-Session (komplexe/mehrstufige Arbeit) — **kein automatisches Anstoßen einer Session durch OpenClaw in v1**.
4. Ergebnis als `post_message` auf den Task.
5. OpenClaw pollt erledigte/zugewiesene Tasks alle 3 Minuten (analog `frawo_agent`-Cron-Intervall) und meldet sich bei Wolf zurück (Telegram und/oder Discuss, je nachdem woher die Anfrage kam).

## Sicherheit / Abhängigkeiten

- **Blocker:** GPT-5-/OpenAI-API-Key liegt nicht lokal vor (geprüft: `.env`, `.ai-tools-shared/.env`) — muss von Wolf bereitgestellt werden, Ablage in Vaultwarden, niemals ins Repo.
- Telegram-Bot-Token (@Frawo_ClawBot): vor Wiederverwendung Gültigkeit prüfen (Bot könnte seit Mai deaktiviert/token-rotiert sein).
- Container läuft auf Anker-Server-VLAN(101) wie HA/Vaultwarden — keine neue UCG-Firewall-Regel nötig (Server-VLAN hat bereits Internet+Odoo-Zugriff).
- Alle Sicherheitsregeln aus `AGENT_ONBOARDING.md` gelten unverändert für Tasks, die OpenClaw anlegt — Agent (Claude) wendet die gleiche Vorsicht an, unabhängig davon wer den Task erstellt hat (z. B. kritischer IT-Strom-Shelly).

## Out of Scope (v1)

- Automatisches Triggern von Claude-Code-Sessions durch OpenClaw (späterer Schritt).
- Email-Kanal (#335, ohnehin blockiert auf Strato-IMAP-Status).
- Migration von Stockenweiler-Restdiensten (separates Thema).

## Testing / Verifikation

- Smoke-Test nach Deployment: Telegram-Testnachricht → OpenClaw antwortet UND legt einen Test-Odoo-Task an (analog altem Demo-Task #520-Pattern).
- Discuss-Bot: Testnachricht in einem Odoo-Discuss-Kanal posten/lesen verifizieren.
- Dogfooding: Das Setup selbst als Odoo-Task tracken, bis verifiziert abgeschlossen.
