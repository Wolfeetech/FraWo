from odoo import api, models

HANDWERK = [
    "schrank", "gehäuse", "gehause", "holz", "montier", "verkabel", "löten",
    "loten", "tweeter", "frequenzweiche", "subwoofer", "einbauen", "säubern",
    "werkstatt", "bestückung", "patchplan", "lieferung", "🔨", "🛠️",
]
DEVOPS = [
    "docker", "tailscale", "exporter", "prometheus", "grafana", "vlan", "dhcp",
    "shelly", "backup", "watchdog", "rclone", "cloudflare", "tunnel", "mount",
    "container", "script", "skript", "api", "n8n", "automat", "🤖",
    "[fundament]", "[ha]", "[backup]", "[integration]", "[security]", "[wartung]",
]

PROMPT_WOLF = """Du bist technischer Projekt-Dokumentar. Formuliere die folgende \
Aufgabe professionell auf Deutsch, mit GENAU diesen Abschnitten als Markdown-\
Überschriften: **Problem**, **Impact**, **Root Cause**, **Definition of Done**, \
**Aufwand**, **Abhängigkeiten**. Sei knapp und sachlich. Erfinde keine Fakten; \
wo Infos fehlen, schreibe „(zu klären)". Antworte NUR mit der Dokumentation.

Aufgabe: %s"""

PROMPT_FRANZ = """Du schreibst für einen Handwerker (Zimmermann). Formuliere die \
Aufgabe KURZ auf Deutsch, alles auf einen Blick, KEIN IT-Fachjargon. Nutze GENAU \
dieses Format als Markdown:
🔨 <Was ist zu tun, 1 Zeile>

📐 Maße / Material:
- <konkrete Zahlen, Maße, Stückzahl, Material — falls unbekannt: „(Maß vor Ort)">

✅ Fertig wenn:
- <prüfbares Ergebnis, 1 Zeile>

💬 Warum:
- <kurze Begründung, 1-2 Sätze>

Antworte NUR mit dem ausgefüllten Format.

Aufgabe: %s"""


class TaskFormatter(models.AbstractModel):
    _name = "frawo.task.formatter"
    _description = "Rollen-Erkennung und Prompt-Bau"

    @api.model
    def detect_role(self, name):
        low = (name or "").lower()
        if any(k in low for k in HANDWERK):
            return "handwerk"
        if any(k in low for k in DEVOPS):
            return "devops"
        return "review"

    @api.model
    def build_prompt(self, name, role):
        if role == "handwerk":
            return PROMPT_FRANZ % name
        return PROMPT_WOLF % name
