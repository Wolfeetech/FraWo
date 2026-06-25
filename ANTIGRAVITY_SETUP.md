# Antigravity-Setup für OpenClaw-Entwicklung

## Workspace
- Pfad: `C:\Users\StudioPC\Workspace\FraWo` (dauerhafter Clone — nicht löschen)
- Gemeinsame Konventionen und Sicherheitsregeln: `AGENT_ONBOARDING.md`

## OpenClaw-Container

| | |
|---|---|
| Host | CT150, `anker-pve` |
| IP | 10.1.0.31 |
| SSH-Alias | `openclaw-ct` |
| Port | 19000 |

```bash
# Container verwalten
ssh openclaw-ct "cd /opt/openclaw && docker compose logs -f"
ssh openclaw-ct "cd /opt/openclaw && docker compose restart"
ssh openclaw-ct "cd /opt/openclaw && docker compose up -d --build"   # nach Dockerfile-Änderungen
```

## MCP-Verbindung zu Odoo
Gleicher Server/Key wie in Claude Code (`.claude.json` Eintrag `"odoo"`).

## Code-Struktur

```
infra/openclaw/
├── Dockerfile          # node:22-slim + python3 + uv + mcp-server-odoo
├── entrypoint.sh       # init: config seeden, Odoo-MCP registrieren, gateway starten
├── docker-compose.yml
├── openclaw.json       # Basis-Config (Model, Channels, Plugins)
├── .env                # Secrets (gitignored)
└── .env.example        # Template
```

## Telegram-Bot
- Bot: `@ServAssi_bot`
- Neues Pairing: Nachricht an Bot → Pairing-Code erscheint → auf openclaw-ct approven:
  ```bash
  ssh openclaw-ct "docker exec openclaw openclaw pairing approve telegram <CODE>"
  ```
