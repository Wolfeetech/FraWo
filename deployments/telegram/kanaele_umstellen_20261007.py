#!/usr/bin/env python3
"""Telegram-Kanaele trennen (Odoo #1965). Laeuft auf Anker bzw. ProDesk: python3 - <host> < diese_datei
Alarm (laut, Direktchat Wolf) = Bot FraWo Alerts, Token /root/.telegram-alarm
Info  (stumm, Kanal FraWo Info) = gleicher Bot, Chat -1003382562014, disable_notification
Jarvis behaelt @Frawo_bot (/root/.telegram-frawo) - kein Maschinen-Absender mehr dort.
Sicherung je Datei: <datei>.bak-20261007-kanaele
"""
import shutil, sys, os

INFO = "-1003382562014"
host = sys.argv[1]


def patch(pfad, ersetzungen):
    if not os.path.exists(pfad):
        print("fehlt:", pfad); return
    s = open(pfad, encoding="utf-8").read()
    neu = s
    for alt, ers in ersetzungen:
        if alt not in neu:
            print("  NICHT gefunden in", pfad, "->", alt[:60]); continue
        neu = neu.replace(alt, ers, 1)
    if neu != s:
        b = pfad + ".bak-20261007-kanaele"
        if not os.path.exists(b):
            shutil.copy2(pfad, b)
        open(pfad, "w", encoding="utf-8").write(neu)
        print("umgestellt:", pfad)


# Waechter (Anker + ProDesk): Alarm-Bot, Absender vorne
patch("/usr/local/bin/monitoring-watchdog.sh", [
    ('TOKEN_DATEI="${TOKEN_DATEI:-/root/.telegram-frawo}"', 'TOKEN_DATEI="${TOKEN_DATEI:-/root/.telegram-alarm}"   # #1965 Alarm-Bot'),
    ('--data-urlencode "text=$1"', '--data-urlencode "text=[Wächter $(hostname)] $1"'),
])

if host == "anker":
    # Backup-TUeV: gruen -> Info-Kanal stumm, Fehler -> Alarm laut
    p = "/usr/local/bin/frawo-backup-tuev.sh"
    patch(p, [
        ("TELEGRAM_TOKEN_FILE=/root/.telegram-frawo", "TELEGRAM_TOKEN_FILE=/root/.telegram-alarm   # #1965 Alarm-Bot\nTELEGRAM_INFO_ID=" + INFO),
    ])
    s = open(p, encoding="utf-8").read()
    if "TG_ZIEL=" not in s:
        s = s.replace('        if [ "$DURCHGEFALLEN" -eq 0 ]; then\n            TG_TEXT=',
                      '        if [ "$DURCHGEFALLEN" -eq 0 ]; then\n            TG_ZIEL="$TELEGRAM_INFO_ID"; TG_STUMM=true   # gruen: stumm in FraWo Info\n            TG_TEXT=', 1)
        s = s.replace('        else\n            TG_TEXT="🚨 [FraWo Backup-TÜV WARNUNG]',
                      '        else\n            TG_ZIEL="$TELEGRAM_CHAT_ID"; TG_STUMM=false   # Fehler: laut an Wolf\n            TG_TEXT="🚨 [FraWo Backup-TÜV WARNUNG]', 1)
        s = s.replace('             -d "chat_id=${TELEGRAM_CHAT_ID}" \\\n             --data-urlencode "text=${TG_TEXT}" \\',
                      '             -d "chat_id=${TG_ZIEL:-$TELEGRAM_CHAT_ID}" -d "disable_notification=${TG_STUMM:-false}" \\\n             --data-urlencode "text=${TG_TEXT}" \\', 1)
        open(p, "w", encoding="utf-8").write(s)
        print("Ziel je Ergebnis gesetzt:", p)

if host == "prodesk":
    # Morgenbriefing -> Info-Kanal stumm
    patch("/usr/local/bin/frawo-daily-briefing.py", [
        ('TELEGRAM_TOKEN_FILE = "/root/.telegram-frawo"', 'TELEGRAM_TOKEN_FILE = "/root/.telegram-alarm"   # #1965 Bot FraWo Alerts'),
        ('TELEGRAM_CHAT_ID = "5924907152"', 'TELEGRAM_CHAT_ID = "' + INFO + '"   # #1965 Kanal FraWo Info (stumm)'),
        ('"-d", f"chat_id={TELEGRAM_CHAT_ID}",', '"-d", f"chat_id={TELEGRAM_CHAT_ID}", "-d", "disable_notification=true",'),
        ('f"text=☀️ Dein Tag:\\n\\n{text}"', 'f"text=[Morgenbriefing] ☀️ Dein Tag:\\n\\n{text}"'),
    ])
    # Sendungs-Titelliste -> Info-Kanal stumm
    patch("/usr/local/bin/sendungs-titelliste.sh", [
        ('[ -r /root/.telegram-frawo ]; then\n    T=$(tr -d "\'\\"" < /root/.telegram-frawo',
         '[ -r /root/.telegram-alarm ]; then\n    T=$(tr -d "\'\\"" < /root/.telegram-alarm'),
        ('-d "chat_id=5924907152"', '-d "chat_id=' + INFO + '" -d "disable_notification=true"'),
        ('--data-urlencode "text=$(cat "$ERG")"', '--data-urlencode "text=[Radio-Titelliste] $(cat "$ERG")"'),
    ])
