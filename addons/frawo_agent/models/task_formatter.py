from odoo import api, models

HANDWERK = [
    "schrank", "gehäuse", "gehause", "holz", "montier", "verkabel", "löten",
    "loten", "tweeter", "frequenzweiche", "subwoofer", "einbauen", "säubern",
    "werkstatt", "bestückung", "patchplan", "lieferung", "🔨", "🛠️",
    "ständerwand", "wand", "regal", "tisch", "bank", "kabelkanal", "lackier",
]
DEVOPS = [
    "docker", "tailscale", "exporter", "prometheus", "grafana", "vlan", "dhcp",
    "shelly", "backup", "watchdog", "rclone", "cloudflare", "tunnel", "mount",
    "container", "script", "skript", "api", "n8n", "automat", "🤖",
    "[fundament]", "[ha]", "[backup]", "[integration]", "[security]", "[wartung]",
    "pve", "proxmox", "linux", "debian", "systemd", "ucg", "unifi", "wireguard",
]

PROMPT_WOLF = """Du bist technischer Projekt-Dokumentar für FraWo. Formuliere die \
folgende Aufgabe kurz und präzise auf Deutsch. Halte dich strikt an die Fakten \
aus dem Titel. Erfinde KEINE Geschichten, keine Namen und keine Ursachen. \
Wo Details fehlen, formuliere sie als offene Frage mit „(zu klären)“.

Nutze GENAU diese Struktur:
<p><b>Aufgabenstellung:</b><br/>
Was getan werden soll (1-2 Sätze).</p>

<p><b>Offene Fragen:</b></p>
<ul>
<li>... (zu klären)</li>
<li>... (zu klären)</li>
</ul>

<p><b>Fertig wenn:</b><br/>
Prüfbares Ergebnis in einem Satz.</p>

Antworte NUR mit dieser HTML-Struktur, ohne Einleitung und ohne Markdown-Codeblock.

Aufgabe: %s"""

PROMPT_FRANZ = """Du schreibst für einen Handwerker (Zimmermann). Formuliere die \
Aufgabe KURZ auf Deutsch, alles auf einen Blick, KEIN IT-Fachjargon. Erfinde keine \
falschen Verfahren (z.B. niemals Holz verschweißen).

Nutze GENAU diese Struktur:
<p>🔨 <b>Was zu tun ist:</b><br/>
Was getan werden soll (1 Zeile).</p>

<p>📐 <b>Maße / Material:</b></p>
<ul>
<li>Maße vor Ort prüfen / Material zu klären</li>
</ul>

<p>✅ <b>Fertig wenn:</b><br/>
Prüfbares Ergebnis in 1 Zeile.</p>

<p>💬 <b>Warum:</b><br/>
Kurzer Nutzen in 1 Satz.</p>

Antworte NUR mit dieser HTML-Struktur, ohne Einleitung und ohne Markdown-Codeblock.

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
