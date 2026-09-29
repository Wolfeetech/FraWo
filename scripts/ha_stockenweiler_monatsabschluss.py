# 🤖 [Claude] 29.09.2026, Odoo #1587 — Monatsabschluss Strom HA Stockenweiler (VM360), NUR LESEN.
# Rechnet den Verbrauch je Partei direkt aus der HA-Langzeitstatistik (Feld "sum", gleicht Zaehler-
# Neustarts aus) fuer einen festen Zeitraum – unabhaengig von den utility_meter-Monatszaehlern,
# die im September 2026 durch eine falsche Kalibrierung ~8-10 % zu niedrig lagen.
#
# Aufruf (StudioPC):
#   B=$(sed "s/__MONAT__/2026-09/" scripts/ha_stockenweiler_monatsabschluss.py | base64 -w0)
#   ssh -i ~/.ssh/pve_ed25519 root@10.1.0.128 "qm guest exec 360 --timeout 90 -- docker exec homeassistant \
#       python3 -c \"import base64;exec(base64.b64decode('$B'))\"" | python -c "import json,sys;print(json.load(sys.stdin)['out-data'])"
import sqlite3, datetime
from zoneinfo import ZoneInfo

MONAT = '__MONAT__'                       # z. B. 2026-09
TZ = ZoneInfo('Europe/Berlin')
j, m = map(int, MONAT.split('-'))
von = datetime.datetime(j, m, 1, tzinfo=TZ)
bis = datetime.datetime(j + (m == 12), m % 12 + 1, 1, tzinfo=TZ)
T0, T1 = von.timestamp(), bis.timestamp()

PARTEIEN = {
    'Lotti (Einliegerwohnung)': ['sensor.licht_flur_bad_energie', 'sensor.herd_energie', 'sensor.kuche_energie', 'sensor.wohnung_energie'],
    'Container (FraWo)': ['sensor.container_licht_total_energy', 'sensor.server_total_energy', 'sensor.container_studio_total_energy'],
    'Familie Prinz (Einzelgeraete)': ['sensor.buro_vater_shelly_mac_windows_shelly_total_energy', 'sensor.shelly_gefrierschrank_total_energy',
        'sensor.keller_pumpe_shelly_keller_pumpe_shelly_total_energy', 'sensor.shellyplugsg3_8cbfeaa03e04_energy',
        'sensor.shellyplugsg3_e4b063d84240_energy', 'sensor.shellyplugsg3_8cbfeaa3ace8_total_energy',
        'sensor.routerschrank_shelly_routerschrank_shelly_total_energy', 'sensor.wohnkuche_tv_sauna_wohnkuche_total_energy'],
    'Erzeugung BKW Container (Einspeisung in Lottis Kreis)': ['sensor.balkonkraftwerk_returned_energy'],
    'Erzeugung BKW Growatt (Garten)': ['sensor.outdoor_balkonkraftwerk_shelly_gen_3_growatt_balkonkraftwerk_returned_energy'],
}
db = sqlite3.connect('file:/config/home-assistant_v2.db?mode=ro', uri=True)

def summe_bis(mid, t):
    r = db.execute("select sum, start_ts from statistics where metadata_id=? and start_ts < ? order by start_ts desc limit 1", (mid, t)).fetchone()
    return r

jetzt = datetime.datetime.now(TZ).timestamp()
teil = T1 > jetzt
print("Zeitraum %s bis %s%s" % (von.strftime('%d.%m.%Y %H:%M'), bis.strftime('%d.%m.%Y %H:%M'),
                                 "  ⚠️ NOCH NICHT ABGESCHLOSSEN (Teilwert)" if teil else ""))
for partei, quellen in PARTEIEN.items():
    gesamt, fehlt = 0.0, []
    for q in quellen:
        mid = db.execute("select id from statistics_meta where statistic_id=?", (q,)).fetchone()
        a = summe_bis(mid[0], T0) if mid else None
        b = summe_bis(mid[0], T1) if mid else None
        if not a or not b or a[0] is None or b[0] is None:
            fehlt.append(q); continue
        # Luecke pruefen: letzte Statistikzeile vor Monatsbeginn darf nicht aelter als 3 h sein
        if T0 - a[1] > 3 * 3600:
            fehlt.append(q + ' (Luecke vor Monatsbeginn)'); continue
        gesamt += b[0] - a[0]
    if fehlt:
        print("  %-52s %13s   NICHT VERWENDBAR – fehlt: %s" % (partei, '—', ', '.join(fehlt)))
    else:
        print("  %-52s %9.2f kWh" % (partei, gesamt))
