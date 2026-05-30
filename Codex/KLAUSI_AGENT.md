# Klausi — FraWo Jarvis Agent
**Stand: 2026-05-30**

## Setup

- **Platform:** OpenClaw v2026.5.27 auf frawo-docker-1 (TS: 100.94.32.41)
- **Bot:** @ServAssi_bot (Token in Vaultwarden: Telegram Bot — ServAssi)
- **Owner:** Wolf Prinz (Telegram ID: 5924907152)
- **Modell:** openai/gpt-4o (Primär) | openai/gpt-4o-mini (Fallback)
- **Service:** systemd user service (`~/.config/systemd/user/openclaw.service`)

## Odoo-Zugriff

Odoo ist KEINE lokale Installation — Web-App über XML-RPC:
```
URL: https://frawo-tech.de/xmlrpc/2/
DB:  FraWo_GbR | UID: 6
```

Fertiges Query-Script: `~/.openclaw/workspace/odoo_query.py`
```bash
python3 ~/workspace/odoo_query.py open_tasks   # Offene Tasks
python3 ~/workspace/odoo_query.py today        # Fällige Tasks
```

## Bekannte Einschränkungen

- Kein direkter SSH zu PVE (Tailscale SSH braucht Browser-Auth-Genehmigung)
- 10.4.0.x nicht direkt erreichbar — nur über frawo-tech.de oder Tailscale-IPs
- Anthropic API ohne Guthaben (console.anthropic.com/billing)

## Frühere Bot-Probleme (gelöst)

| Problem | Ursache | Fix |
|---------|---------|-----|
| 409 Conflict | StudioPC hatte Scheduled Tasks | Deaktiviert (OpenClaw-Agent, OpenClaw-Telegram-Bridge) |
| Falsches Telegram-Konto | Flo's Account gepairt | Neuer Bot @ServAssi_bot mit Wolf's Account |
| "Odoo Installationspfad nicht gefunden" | Bot suchte odoo-bin lokal | SOUL.md: XML-RPC Anleitung + Script |
| gpt-4o-mini zu schwach | Modell kann XML-RPC nicht selbst herleiten | Auf gpt-4o upgraded |

## Nächste Schritte

1. Anthropic Credits aufladen → Claude Sonnet als Primär
2. Tailscale Subnet Route approven (admin.tailscale.com)
3. n8n Track-Rating Webhook testen
4. Email-Channel (agent@frawo-tech.de) aktivieren
