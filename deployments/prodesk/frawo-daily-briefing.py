#!/usr/bin/env python3
"""
Taeglicher Kurz-Tagesplan fuer Wolf per Telegram. Schaut auf offene
Fristen, neue Eingang/Inbox-Dokumente und den heutigen Kalender (inkl.
IHL-Arbeitsblock), laesst Gemini die 3 wichtigsten Dinge des Tages
herausziehen und schickt das per Telegram. Laeuft frueh morgens per
systemd-Timer auf stock-pve. Siehe OPERATIONS/PAPERLESS_OPERATIONS.md
bzw. Odoo-Aufgabe zum Tagesplan-Bot.
"""
import json
import os
import subprocess
import urllib.error
import urllib.request
import xmlrpc.client
from datetime import datetime, timedelta

ODOO_URL = "http://10.1.0.112:8069"
ODOO_DB = "FraWo_GbR"
ODOO_USER = os.environ["ODOO_USER"]
ODOO_PASS = os.environ["ODOO_PASS"]
WOLF_USER_ID = 6

GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]
GEMINI_MODEL = "gemini-3.5-flash-lite"

TELEGRAM_TOKEN_FILE = "/root/.telegram-alarm"   # #1965 Bot FraWo Alerts
TELEGRAM_CHAT_ID = "-1003382562014"   # #1965 Kanal FraWo Info (stumm)


def odoo():
    common = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/common")
    uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASS, {})
    models = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/object")
    return uid, models


def fetch_context(uid, models):
    now = datetime.now()
    horizon = (now + timedelta(days=5)).strftime("%Y-%m-%d")
    # Nicht weiter als 21 Tage zurueck: alte, aus Dokumenten extrahierte
    # oder laengst ueberholte Projekt-Phasen-Fristen sollen die
    # Priorisierung nicht mit Jahre altem Rauschen zumuellen.
    not_before = (now - timedelta(days=21)).strftime("%Y-%m-%d")
    yesterday = (now - timedelta(days=2)).strftime("%Y-%m-%d 00:00:00")

    open_stage_ids = models.execute_kw(
        ODOO_DB, uid, ODOO_PASS, 'project.task.type', 'search',
        [[['name', 'not in', ['✅ Erledigt', '🗑️ Abgebrochen', 'Erledigt', 'Abgebrochen']]]],
    )

    deadline_tasks = models.execute_kw(
        ODOO_DB, uid, ODOO_PASS, 'project.task', 'search_read',
        [[
            ['user_ids', 'in', [WOLF_USER_ID]],
            ['stage_id', 'in', open_stage_ids],
            ['date_deadline', '!=', False],
            ['date_deadline', '<=', horizon],
            ['date_deadline', '>=', not_before],
        ]],
        {'fields': ['name', 'date_deadline', 'project_id', 'priority'], 'limit': 40, 'order': 'date_deadline asc'},
    )

    inbox_tasks = models.execute_kw(
        ODOO_DB, uid, ODOO_PASS, 'project.task', 'search_read',
        [[
            ['project_id', '=', 32],
            ['stage_id', 'in', open_stage_ids],
            ['create_date', '>=', yesterday],
        ]],
        {'fields': ['name', 'create_date'], 'limit': 20, 'order': 'create_date desc'},
    )

    today_start = now.strftime("%Y-%m-%d 00:00:00")
    today_end = now.strftime("%Y-%m-%d 23:59:59")
    calendar_today = models.execute_kw(
        ODOO_DB, uid, ODOO_PASS, 'calendar.event', 'search_read',
        [[
            ['user_id', '=', WOLF_USER_ID],
            ['start', '>=', today_start],
            ['start', '<=', today_end],
        ]],
        {'fields': ['name', 'start', 'stop'], 'limit': 20, 'order': 'start asc'},
    )

    return deadline_tasks, inbox_tasks, calendar_today


def build_prompt(deadline_tasks, inbox_tasks, calendar_today):
    today_str = datetime.now().strftime("%A, %d.%m.%Y")
    lines = [f"Heute ist {today_str}.", "", "Offene Aufgaben mit Frist (naechste Tage, ueberfaellige zuerst):"]
    for t in deadline_tasks:
        proj = t['project_id'][1] if t['project_id'] else "?"
        lines.append(f"- [{t['id']}] {t['name']} (Frist {t['date_deadline']}, Projekt: {proj})")
    lines.append("")
    lines.append("Neue Dokumente im Eingang (letzte 2 Tage):")
    for t in inbox_tasks:
        lines.append(f"- [{t['id']}] {t['name']}")
    lines.append("")
    lines.append("Heutiger Kalender:")
    for e in calendar_today:
        lines.append(f"- {e['start']}–{e['stop']}: {e['name']}")

    return "\n".join(lines)


def call_gemini(context_text):
    prompt = f"""Du bist Wolfs persönlicher Tagesplaner (FraWo GbR). Hier ist der
aktuelle Stand aus Odoo:

{context_text}

Schreibe eine KURZE Telegram-Nachricht auf Deutsch (max. 6-8 Zeilen,
keine Ueberschriften, kein Markdown-Fett) mit:
1. Die 3 wichtigsten Dinge, um die sich Wolf HEUTE kümmern sollte
   (Priorität: überfällige Fristen > neue Mahnungen/Inkasso im Eingang >
   nahe Fristen). Wenn er laut Kalender einen Arbeitsblock (z.B.
   Inselhalle) hat, erwähne kurz dass GbR-Sachen erst danach drankommen.
2. Wenn nichts wirklich dringend ist, sag das auch ehrlich kurz.
Kein Grussformel, keine Signatur, direkt zur Sache."""
    url = (f"https://generativelanguage.googleapis.com/v1beta/models/"
           f"{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}")
    body = json.dumps({
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.3},
    }).encode()
    req = urllib.request.Request(url, data=body, method="POST")
    req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, timeout=45) as r:
        resp = json.loads(r.read().decode())
    return resp["candidates"][0]["content"]["parts"][0]["text"].strip()


def monday_ihl_reminder(uid, models):
    """Montags: wenn fuer diese Woche noch keine Inselhalle-Zeiten im
    Kalender stehen, aktiv nachfragen statt ein festes Muster anzunehmen
    (IHL-Dienstplan wechselt woechentlich, siehe Absprache 21.08.2026)."""
    now = datetime.now()
    if now.weekday() != 0:  # 0 = Montag
        return None
    week_start = now.strftime("%Y-%m-%d 00:00:00")
    week_end = (now + timedelta(days=5)).strftime("%Y-%m-%d 00:00:00")
    existing = models.execute_kw(
        ODOO_DB, uid, ODOO_PASS, 'calendar.event', 'search_count',
        [[
            ['user_id', '=', WOLF_USER_ID],
            ['name', 'ilike', 'Inselhalle'],
            ['start', '>=', week_start],
            ['start', '<', week_end],
        ]],
    )
    if existing:
        return None
    return ("📋 Wie sind deine Inselhalle-Zeiten diese Woche laut Dienstplan? "
            "Sag mir kurz Bescheid, dann trage ich sie ein.")


def send_telegram(text):
    with open(TELEGRAM_TOKEN_FILE) as f:
        token = f.read().strip().strip('"')
    result = subprocess.run(
        ["curl", "-s", "--max-time", "20",
         "-d", f"chat_id={TELEGRAM_CHAT_ID}", "-d", "disable_notification=true",
         "--data-urlencode", f"text=[Morgenbriefing] ☀️ Dein Tag:\n\n{text}",
         f"https://api.telegram.org/bot{token}/sendMessage"],
        capture_output=True, text=True,
    )
    print(result.stdout[:300], result.stderr[:300])


def main():
    uid, models = odoo()
    deadline_tasks, inbox_tasks, calendar_today = fetch_context(uid, models)
    context_text = build_prompt(deadline_tasks, inbox_tasks, calendar_today)
    print("=== Kontext ===")
    print(context_text)
    try:
        summary = call_gemini(context_text)
    except Exception as e:
        print(f"Gemini-Fehler: {e}")
        summary = "Automatische Zusammenfassung heute nicht verfuegbar. Bitte kurz selbst in Odoo nachsehen."
    reminder = monday_ihl_reminder(uid, models)
    if reminder:
        summary = f"{summary}\n\n{reminder}"

    print("=== Nachricht ===")
    print(summary)
    send_telegram(summary)


if __name__ == "__main__":
    main()
