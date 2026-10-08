#!/usr/bin/env python3
"""
FraWo Open WebUI Model Persona Sync
Synchronisiert die kuratierten FraWo-Fachassistenten und Basismodelle in die SQLite-Datenbank
von Open WebUI auf dem Server (OptiPlex 10.1.0.227).

Modelle:
- 📋 FraWo Task & Odoo Manager (GPU / StudioPC)
- ⚡ FraWo 24/7 Schnell-Assistent (OptiPlex)
- 💻 FraWo Code & IT-Architekt (GPU / StudioPC)
- 🧠 DeepSeek R1 Denk- & Analyse-Modell (GPU / StudioPC)
- 🎙️ FraWo Funk & Content-Kurator (GPU / StudioPC)
"""

import json
import sqlite3
import sys
import time

DB_PATH = "/var/lib/open-webui/data/webui.db"
USER_ID = "1bfd75ae-10c8-4d69-9f70-2c29281fa22a"  # Wolf (admin)

MODELS = [
    # --- Kuratierte FraWo Personas & Fach-Assistenten ---
    {
        "id": "frawo-task-odoo",
        "user_id": USER_ID,
        "base_model_id": "frawo-mitarbeiter:latest",
        "name": "📋 FraWo Task & Odoo Manager (GPU)",
        "params": json.dumps({
            "system": (
                "Du bist der FraWo Task & Odoo Manager. Deine Aufgabe ist es, Wolf bei der Organisation "
                "von Projekten, Odoo-Tickets und Arbeitsschritten zu unterstützen.\n\n"
                "Regeln:\n"
                "1. Halte dich an das FraWo Agenten-Protokoll: Tasks klar strukturieren, Definition of Done (DoD) definieren, Prioritäten setzen.\n"
                "2. Schlage pro Antwort 1 bis 3 konkrete, sofort umsetzbare nächste Schritte vor.\n"
                "3. Keine vagen Antworten: Wenn Informationen fehlen, frage präzise nach.\n"
                "4. Antworte auf Deutsch, präzise und professionell."
            )
        }),
        "meta": json.dumps({
            "description": "Odoo-Aufgaben, Projekt-Etappenziele, Definition of Done, Deadlines und strukturierte Aktionspläne.",
            "capabilities": {"vision": False, "citations": True},
            "suggestion_prompts": [
                {"content": "Erstelle ein Odoo-Ticket für ein neues Kundenprojekt mit DoD und Schritten"},
                {"content": "Wie strukturieren wir die anstehenden Event-Technik Aufgaben für dieses Wochenende?"},
                {"content": "Formuliere eine klare Aufgabenbeschreibung für die nächste Radio-Sendeplanung"}
            ],
            "tags": [{"name": "FraWo"}, {"name": "Produktivität"}]
        }),
        "is_active": 1,
    },
    {
        "id": "frawo-code-dev",
        "user_id": USER_ID,
        "base_model_id": "qwen2.5-coder:7b",
        "name": "💻 FraWo Code & IT-Architekt (GPU)",
        "params": json.dumps({
            "system": (
                "Du bist der leitende FraWo Code- & IT-Architekt. Du kennst die IT-Infrastruktur von FraWo "
                "(Proxmox auf OptiPlex 10.1.0.227, CT140 Web/Nginx/Tunnel, CT110 Odoo, CT130 AzuraCast, StudioPC mit RTX 4060, Docker, Cloudflare Tunnels).\n\n"
                "Regeln:\n"
                "1. Du schreibst sauberen, robusten Code (Python, Bash, JS, HTML/CSS, SQL).\n"
                "2. Achte auf Best Practices, Fehlerbehandlung und Sicherheit (keine Plaintext-Secrets in Dateien schreiben).\n"
                "3. Gib praxisfertigen, direkt lauffähigen Code mit kurzen, präzisen Erklärungen.\n"
                "4. Änderungen an Systemen immer sauber dokumentieren."
            )
        }),
        "meta": json.dumps({
            "description": "Entwicklung & DevOps: Python, Docker, Nginx, Proxmox, Bash, APIs, Fehlersuche und System-Architektur.",
            "capabilities": {"vision": False, "citations": True},
            "suggestion_prompts": [
                {"content": "Schreibe ein Python-Skript zur Abfrage der Odoo API"},
                {"content": "Optimiere die Nginx-Konfiguration für WebSockets und Streaming"},
                {"content": "Erstelle ein Bash-Skript für automatische Docker-Container Backups"}
            ],
            "tags": [{"name": "FraWo"}, {"name": "Entwicklung"}]
        }),
        "is_active": 1,
    },
    {
        "id": "frawo-fast-247",
        "user_id": USER_ID,
        "base_model_id": "frawo-mitarbeiter-fast:latest",
        "name": "⚡ FraWo 24/7 Schnell-Assistent (OptiPlex)",
        "params": json.dumps({
            "system": (
                "Du bist der FraWo 24/7 Schnell-Assistent. Du läufst dauerhaft auf dem FraWo-Server und bist jederzeit "
                "von unterwegs über Mobilgeräte erreichbar.\n\n"
                "Deine Stärken:\n"
                "- Extrem schnelle, prägnante Antworten\n"
                "- Memos formulieren, E-Mails entwerfen\n"
                "- Kurze Zusammenfassungen und Blitz-Recherchen\n"
                "- Antworte freundlich, direkt und ohne Umschweife auf Deutsch."
            )
        }),
        "meta": json.dumps({
            "description": "24/7 immer online auf dem Server: Schnelle Antworten, kurze Memos, E-Mails, Zusammenfassungen – auch wenn StudioPC offline ist.",
            "capabilities": {"vision": False, "citations": True},
            "suggestion_prompts": [
                {"content": "Entwirf eine kurze, freundliche Antwort auf eine Kundenanfrage bezüglich Tontechnik-Miete"},
                {"content": "Fasse mir diesen Text in 3 Stichpunkten zusammen"},
                {"content": "Schnelles Brainstorming: 5 griffige Titel für unsere nächste FraWo-Aktion"}
            ],
            "tags": [{"name": "FraWo"}, {"name": "24/7"}]
        }),
        "is_active": 1,
    },
    {
        "id": "frawo-denker-r1",
        "user_id": USER_ID,
        "base_model_id": "deepseek-r1:8b",
        "name": "🧠 DeepSeek R1 Denk- & Analyse-Modell (GPU)",
        "params": json.dumps({
            "system": (
                "Du bist das analytische Denkmodell von FraWo. Nutze tiefgehende logische Schlussfolgerungen, prüfe Randbedingungen, "
                "hinterfrage Annahmen und liefere gründlich durchdachte, fundierte Lösungen für schwierige Herausforderungen. "
                "Zeige deine Überlegungen transparent und fasse die finale Empfehlung klar zusammen."
            )
        }),
        "meta": json.dumps({
            "description": "Tiefes Denken & Reasoning: Komplexe Analysen, logische Probleme, schwierige Architekturentscheidungen und strategische Abwägungen.",
            "capabilities": {"vision": False, "citations": True},
            "suggestion_prompts": [
                {"content": "Analysiere die Vor- und Nachteile von zwei verschiedenen Backup-Strategien für FraWo"},
                {"content": "Finde den logischen Denkfehler in folgendem Systemablauf"},
                {"content": "Erstelle eine strukturierte Risikoanalyse für den Ausfall einzelner Proxmox-Container"}
            ],
            "tags": [{"name": "FraWo"}, {"name": "Reasoning"}]
        }),
        "is_active": 1,
    },
    {
        "id": "frawo-funk-content",
        "user_id": USER_ID,
        "base_model_id": "frawo-mitarbeiter:latest",
        "name": "🎙️ FraWo Funk & Content-Kurator (GPU)",
        "params": json.dumps({
            "system": (
                "Du bist der FraWo Funk & Content-Kurator. Du unterstützt Wolf und das FraWo-Team bei allem rund um "
                "FraWo Funk, Webradio (AzuraCast), Musikstile, Track-Metadaten, Moderation, Playlisten-Planung und "
                "zielgruppenrelevante Social Media Posts.\n\n"
                "Dein Stil:\n"
                "- Sympathisch, dynamisch, musikbegeistert und professionell\n"
                "- Kenntnis gängiger Genres (House, Techno, Trance, Drum&Bass, Chillout, Ambient)\n"
                "- Ansagen und Texte sind direkt sendebereit."
            )
        }),
        "meta": json.dumps({
            "description": "Radio & Medien: AzuraCast Playlisten, Musik-Tagging (Genres, BPM, Stimmung), Jingles, Moderationstexte und Social Media Postings.",
            "capabilities": {"vision": False, "citations": True},
            "suggestion_prompts": [
                {"content": "Schreibe eine lockere Moderationsansage für den Übergang zwischen zwei Tracks"},
                {"content": "Welche Subgenres passen zu einer melodischen Deep-House Sendung am Samstagabend?"},
                {"content": "Formuliere einen Social Media Post zur Ankündigung der neuen Live-Sendung auf FraWo Funk"}
            ],
            "tags": [{"name": "FraWo"}, {"name": "Radio"}]
        }),
        "is_active": 1,
    },
    # --- Bereinigung: Technische / doppelte Modelle ausblenden ---
    {
        "id": "nomic-embed-text:latest",
        "user_id": USER_ID,
        "base_model_id": None,
        "name": "nomic-embed-text:latest",
        "params": "{}",
        "meta": "{}",
        "is_active": 0,
    },
    {
        "id": "qwen2.5:3b",
        "user_id": USER_ID,
        "base_model_id": None,
        "name": "qwen2.5:3b",
        "params": "{}",
        "meta": "{}",
        "is_active": 0,
    },
    # --- Basismodelle mit sauberen Klarnamen versehen ---
    {
        "id": "frawo-mitarbeiter:latest",
        "user_id": USER_ID,
        "base_model_id": None,
        "name": "⚙️ FraWo Basis (Qwen 7B Mitarbeiter)",
        "params": "{}",
        "meta": json.dumps({
            "description": "Basismodell für FraWo mit allgemeinem Kontext (7B Qwen 2.5).",
        }),
        "is_active": 1,
    },
    {
        "id": "frawo-mitarbeiter-fast:latest",
        "user_id": USER_ID,
        "base_model_id": None,
        "name": "⚙️ FraWo Basis Fast (Qwen 3B Mitarbeiter)",
        "params": "{}",
        "meta": json.dumps({
            "description": "Leichtgewichtiges Basismodell für schnelle Textaufgaben (3B Qwen 2.5).",
        }),
        "is_active": 1,
    },
    {
        "id": "qwen2.5-coder:7b",
        "user_id": USER_ID,
        "base_model_id": None,
        "name": "⚙️ Qwen 2.5 Coder 7B (Rohmodell)",
        "params": "{}",
        "meta": json.dumps({
            "description": "Standard Code-Modell ohne spezielle FraWo-Instruktionen.",
        }),
        "is_active": 1,
    },
    {
        "id": "qwen2.5:7b",
        "user_id": USER_ID,
        "base_model_id": None,
        "name": "⚙️ Qwen 2.5 7B (Allgemein)",
        "params": "{}",
        "meta": json.dumps({
            "description": "Allgemeines 7B Sprachmodell von Alibaba Cloud.",
        }),
        "is_active": 1,
    }
]

def sync(db_path=DB_PATH):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    now = int(time.time())

    for m in MODELS:
        cur.execute(
            """
            INSERT INTO model (id, user_id, base_model_id, name, params, meta, is_active, updated_at, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                user_id=excluded.user_id,
                base_model_id=excluded.base_model_id,
                name=excluded.name,
                params=excluded.params,
                meta=excluded.meta,
                is_active=excluded.is_active,
                updated_at=excluded.updated_at
            """,
            (
                m["id"],
                m["user_id"],
                m["base_model_id"],
                m["name"],
                m["params"],
                m["meta"],
                m["is_active"],
                now,
                now,
            ),
        )

    pinned_str = "frawo-task-odoo,frawo-fast-247,frawo-code-dev,frawo-denker-r1,frawo-funk-content"
    order_list = [
        "frawo-task-odoo",
        "frawo-fast-247",
        "frawo-code-dev",
        "frawo-denker-r1",
        "frawo-funk-content",
        "frawo-mitarbeiter:latest",
        "frawo-mitarbeiter-fast:latest",
        "qwen2.5-coder:7b",
        "qwen2.5:7b"
    ]

    cur.execute(
        "UPDATE config SET value = ? WHERE key = 'ui.default_models'",
        (json.dumps("frawo-task-odoo"),)
    )
    cur.execute(
        "UPDATE config SET value = ? WHERE key = 'ui.default_pinned_models'",
        (json.dumps(pinned_str),)
    )
    cur.execute(
        "UPDATE config SET value = ? WHERE key = 'ui.model_order_list'",
        (json.dumps(order_list),)
    )

    ollama_urls = ["http://10.0.0.156:11434", "http://10.1.0.227:11434"]
    ollama_api_configs = {"0": {"enable": True}, "1": {"enable": True}}
    cur.execute(
        "UPDATE config SET value = ? WHERE key = 'ollama.base_urls'",
        (json.dumps(ollama_urls),)
    )
    cur.execute(
        "UPDATE config SET value = ? WHERE key = 'ollama.api_configs'",
        (json.dumps(ollama_api_configs),)
    )

    conn.commit()
    conn.close()
    print("Sync complete.")

if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else DB_PATH
    sync(path)
