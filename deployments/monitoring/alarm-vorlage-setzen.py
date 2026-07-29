#!/usr/bin/env python3
"""
FraWo — Telegram-Alarmvorlage mit Dashboard-Link
Angelegt 29.07.2026. Läuft in CT150.

WOZU
====
Wolf: "im falle das mir der bot auf telegram schreibt, soll bitte direkt der
link eben zu dem dashboard mitgeschickt werden, ich will in einem solchen
fall selbst schauen können was ist da los. bestenfalls am handy direkt über
den telegram alarm"

Bisher enthielt die Nachricht nur Text. Jetzt kommt der passende
Dashboard-Link mit — anklickbar, und über Tailscale auch unterwegs
erreichbar (CT150 hängt seit dem 29.07.2026 im Tailnet unter
100.100.115.80).

WARUM DIESES SKRIPT UND KEIN EINFACHES EINSPIELEN DER DATEI
In der alertmanager.yml steht der Telegram-Zugangsschlüssel. Die Datei darf
deshalb nicht ins Repo und nicht durch eine Kopie ersetzt werden — dieses
Skript tauscht ausschliesslich den Nachrichtenblock aus und lässt alles
andere unberührt.

WELCHER LINK MITGESCHICKT WIRD
Jede Alarmregel kann eine Anmerkung "dashboard" tragen. Fehlt sie, wird auf
den Überblick verwiesen. So bekommt man beim Sicherungs-Alarm das
Sicherungs-Dashboard und beim Temperatur-Alarm die Servermesswerte, ohne
dass jede Regel das wissen müsste.
"""

import re
import shutil
import sys
from datetime import date

DATEI = '/etc/prometheus/alertmanager.yml'
BASIS = 'http://100.100.115.80:3000'

VORLAGE = """        message: |-
          {{ if eq .Status "firing" }}🚨 ALARM{{ else }}✅ BEHOBEN{{ end }} · {{ .CommonLabels.severity }}
          {{ range .Alerts }}
          {{ .Annotations.summary }}

          {{ .Annotations.description }}

          📊 Live ansehen:
          {{ if .Annotations.dashboard }}{{ .Annotations.dashboard }}{{ else }}""" + BASIS + """/d/frawo-ueberblick{{ end }}
          {{ end }}"""


def main():
    with open(DATEI, encoding='utf-8') as f:
        inhalt = f.read()

    if 'Live ansehen' in inhalt:
        print('  Vorlage ist bereits gesetzt.')
        return 0

    sicherung = f'{DATEI}.vor-dashboard-link-{date.today():%Y%m%d}'
    shutil.copy2(DATEI, sicherung)
    print(f'  Sicherung: {sicherung}')

    # Den bestehenden message-Block finden: beginnt bei "message: |-" und
    # reicht bis zur naechsten Zeile, die weniger eingerueckt ist.
    muster = re.compile(
        r'^([ \t]*)message: \|-\n(?:\1[ \t].*\n|\n)*',
        re.MULTILINE
    )
    if not muster.search(inhalt):
        print('  FEHLER: Kein message-Block gefunden. Datei unveraendert.')
        return 1

    neu = muster.sub(VORLAGE + '\n', inhalt, count=1)

    with open(DATEI, 'w', encoding='utf-8') as f:
        f.write(neu)
    print('  Nachrichtenvorlage ersetzt.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
