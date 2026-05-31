# OpenClaw AI Gateway — Setup-Dokumentation
**Stand: 2026-05-30 | frawo-docker-1**

## Übersicht

OpenClaw ist ein selbst-gehosteter AI-Agent-Gateway auf frawo-docker-1 (Stockenweiler).
Er empfängt Nachrichten via Telegram (@Frawo_ClawBot) und führt Aktionen über Skills aus.

## Installation

```bash
# Node.js 22.22.3 (user-level, kein sudo nötig)
# ~/opt/node/bin/ im PATH (in ~/.bashrc)

npm install -g openclaw   # v2026.5.27
```

## Systemd Service

```
~/.config/systemd/user/openclaw.service
ExecStart: /home/wolf/opt/node/bin/openclaw gateway
Restart: on-failure, RestartSec: 10
```

```bash
systemctl --user start/stop/restart/status openclaw.service
journalctl --user -u openclaw.service -n 30
```

## Konfiguration

`~/.openclaw/openclaw.json` — keine Credentials hier speichern, alle Keys im Vault.

```json
{
  "gateway": { "mode": "local", "port": 19000 },
  "plugins": { "entries": { "anthropic": {}, "openai": {} } },
  "agents": {
    "defaults": {
      "model": {
        "primary": "openai/gpt-4o",
        "fallbacks": ["anthropic/claude-haiku-4-5-20251001"]
      }
    }
  },
  "channels": {
    "telegram": {
      "enabled": true,
      "dmPolicy": "pairing"
    }
  }
}
```

## Modelle

| Modell | Rolle | Auth |
|--------|-------|------|
| openai/gpt-4o | Primär | API Key (Vault: OpenAI API Key) |
| anthropic/claude-haiku-4-5 | Fallback | API Key (Vault: Anthropic API Key) |

## Telegram Channel

- Bot: @Frawo_ClawBot
- Owner: Wolf (Telegram ID 5410536762)
- Pairing: `openclaw pairing approve telegram <CODE>`

## Bekannte Einschränkungen

- Anthropic API: Guthaben nötig (console.anthropic.com → Billing)
- sudo auf frawo-docker-1 unbekannt → nsenter Docker-Workaround für Root-Ops
- Odoo-Skill noch nicht installiert (nächster Schritt)

## Nächste Schritte

1. Odoo-Skill installieren: `npx clawhub install odoo-erp-connector`
2. n8n Workflow: AzuraCast → Show Notes Generator
3. Email Channel: agent@frawo-tech.de via IMAP/SMTP
