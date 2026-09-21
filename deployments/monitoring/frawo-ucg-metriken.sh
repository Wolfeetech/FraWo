#!/bin/bash
# FraWo · Liest Messwerte vom UniFi-Gateway und legt sie für Prometheus ab.
#
# Warum es das gibt: Am 21.09.2026 hat das Gateway stundenlang gesendet und
# fast nichts zurückbekommen (11 kB/s raus, 73 B/s rein) - niemand hat es
# gemerkt, weil das Gateway als einziges Gerät der Anlage gar nicht überwacht
# wurde. Ausgerechnet das, dessen Ausfall alles lahmlegt.
#
# Kein neuer Dienst, keine neue Anmeldung: ein Skript wie der Verbund-Wächter,
# abgelegt über den Textdatei-Sammler, den node_exporter ohnehin liest.
# Aufgabe M2 aus Odoo-Vorhaben #1523.
#
# Aufruf über frawo-ucg-metriken.timer, alle 60 s.
# Schlüssel: /etc/frawo/unifi.env mit  FRAWO_UNIFI_KEY=...   (chmod 600)

set -u
GW="${FRAWO_UNIFI_GW:-10.1.0.1}"
ZIEL="/var/lib/node_exporter/textfile_collector/frawo_ucg.prom"
TMP="${ZIEL}.$$"

[ -r /etc/frawo/unifi.env ] && . /etc/frawo/unifi.env
KEY="${FRAWO_UNIFI_KEY:-}"

trap 'rm -f "$TMP"' EXIT

schreibe_ausfall() {
    {
        echo "# HELP frawo_ucg_erreichbar Antwortet die Gateway-Schnittstelle (1 = ja)"
        echo "# TYPE frawo_ucg_erreichbar gauge"
        echo "frawo_ucg_erreichbar 0"
        echo "# HELP frawo_ucg_letzte_messung_zeitstempel Zeitpunkt der letzten Messung"
        echo "# TYPE frawo_ucg_letzte_messung_zeitstempel gauge"
        echo "frawo_ucg_letzte_messung_zeitstempel $(date +%s)"
    } > "$TMP"
    mv "$TMP" "$ZIEL"
}

if [ -z "$KEY" ]; then
    echo "FEHLER: kein Schlüssel. /etc/frawo/unifi.env anlegen." >&2
    schreibe_ausfall
    exit 2
fi

ROH=$(curl -s -k -m 20 -H "X-API-KEY: ${KEY}" \
      "https://${GW}/proxy/network/api/s/default/stat/device" 2>/dev/null)

if [ -z "$ROH" ]; then
    schreibe_ausfall
    exit 1
fi

printf '%s' "$ROH" | python3 -c '
import json, sys, time

try:
    daten = json.load(sys.stdin).get("data", [])
except Exception:
    print("frawo_ucg_erreichbar 0")
    print("frawo_ucg_letzte_messung_zeitstempel %d" % time.time())
    raise SystemExit

gw = next((d for d in daten if d.get("type") == "ugw" or d.get("model") == "UDRULT"), None)
if gw is None:
    print("frawo_ucg_erreichbar 0")
    print("frawo_ucg_letzte_messung_zeitstempel %d" % time.time())
    raise SystemExit

aus = []
def m(name, hilfe, typ, wert, labels=""):
    aus.append("# HELP %s %s" % (name, hilfe))
    aus.append("# TYPE %s %s" % (name, typ))
    aus.append("%s%s %s" % (name, labels, wert))

def z(v, standard=0.0):
    try: return float(v)
    except (TypeError, ValueError): return standard

m("frawo_ucg_erreichbar", "Antwortet die Gateway-Schnittstelle (1 = ja)", "gauge", 1)
m("frawo_ucg_bereit", "Gateway meldet betriebsbereit (state 1)", "gauge",
  1 if gw.get("state") == 1 else 0)
m("frawo_ucg_laufzeit_sekunden", "Laufzeit des Gateways", "gauge", int(z(gw.get("uptime"))))

# --- Auslastung -------------------------------------------------------
st = gw.get("system-stats") or {}
m("frawo_ucg_cpu_prozent", "Prozessorauslastung des Gateways", "gauge", z(st.get("cpu")))
m("frawo_ucg_speicher_prozent", "Speicherauslastung des Gateways", "gauge", z(st.get("mem")))

# --- Temperatur (der eigentliche Grund fuer dieses Skript) -----------
temps = gw.get("temperatures") or []
if temps:
    aus.append("# HELP frawo_ucg_temperatur_celsius Temperatur im Gateway")
    aus.append("# TYPE frawo_ucg_temperatur_celsius gauge")
    for t in temps:
        name = str(t.get("name", "?")).replace("\\", "").replace(chr(34), "")
        aus.append("frawo_ucg_temperatur_celsius{sensor=\"%s\"} %s" % (name, z(t.get("value"))))
m("frawo_ucg_ueberhitzt", "Gateway meldet Ueberhitzung (1 = ja)", "gauge",
  1 if gw.get("overheating") else 0)

# --- WAN: das Zaehlerpaar, das den 21.09. erklaert hat ---------------
wan = gw.get("wan1") or {}
m("frawo_ucg_wan_up", "WAN-Anschluss aktiv (1 = ja)", "gauge", 1 if wan.get("up") else 0)
m("frawo_ucg_wan_adresse_vorhanden", "WAN hat eine Adresse (1 = ja)", "gauge",
  1 if wan.get("ip") else 0)
m("frawo_ucg_wan_latenz_ms", "Antwortzeit des WAN in Millisekunden", "gauge",
  z(wan.get("latency")))
m("frawo_ucg_wan_verfuegbarkeit_prozent", "Vom Gateway gemeldete WAN-Verfuegbarkeit",
  "gauge", z(wan.get("availability")))
m("frawo_ucg_wan_empfangene_bytes_total",
  "Vom WAN empfangene Bytes - gegen gesendete pruefen!", "counter",
  int(z(wan.get("rx_bytes"))))
m("frawo_ucg_wan_gesendete_bytes_total",
  "Ueber das WAN gesendete Bytes - gegen empfangene pruefen!", "counter",
  int(z(wan.get("tx_bytes"))))

# --- Anschluesse ------------------------------------------------------
ports = gw.get("port_table") or []
if ports:
    aus.append("# HELP frawo_ucg_port_up Anschluss hat Verbindung (1 = ja)")
    aus.append("# TYPE frawo_ucg_port_up gauge")
    aus.append("# HELP frawo_ucg_port_geschwindigkeit_mbit Ausgehandelte Geschwindigkeit")
    aus.append("# TYPE frawo_ucg_port_geschwindigkeit_mbit gauge")
    for p in ports:
        idx = p.get("port_idx")
        if idx is None: continue
        aus.append("frawo_ucg_port_up{port=\"%s\"} %d" % (idx, 1 if p.get("up") else 0))
        aus.append("frawo_ucg_port_geschwindigkeit_mbit{port=\"%s\"} %s"
                   % (idx, z(p.get("speed"))))

# --- Angemeldete Geraete ---------------------------------------------
m("frawo_ucg_geraete_gesamt", "Am Gateway angemeldete Geraete", "gauge",
  int(z(gw.get("num_sta"))))
m("frawo_ucg_geraete_gast", "Angemeldete Gastgeraete", "gauge",
  int(z(gw.get("guest-num_sta"))))

# --- Speicher im Geraet ----------------------------------------------
for s in (gw.get("storage") or []):
    groesse, belegt = z(s.get("size")), z(s.get("used"))
    if groesse > 0:
        name = str(s.get("name", "?")).replace(chr(34), "")
        aus.append("frawo_ucg_speicher_belegt_prozent{traeger=\"%s\"} %.1f"
                   % (name, belegt / groesse * 100))

m("frawo_ucg_letzte_messung_zeitstempel",
  "Zeitpunkt dieser Messung - schweigt das Skript, faellt es auf", "gauge",
  int(time.time()))

print("\n".join(aus))
' > "$TMP" 2>/dev/null

if [ -s "$TMP" ]; then
    mv "$TMP" "$ZIEL"
    chmod 644 "$ZIEL"
else
    schreibe_ausfall
    exit 1
fi
