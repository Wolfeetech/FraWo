#!/bin/bash
# Prometheus-Konfiguration neu einlesen — angelegt 29.07.2026
#
# WARUM ES DAS GIBT — bitte lesen, bevor jemand wieder systemctl benutzt:
#
#   "pct exec 150 -- systemctl reload prometheus" SCHEITERT in diesem
#   Container. Die Fehlermeldung lautet:
#     Failed to set up mount namespacing: /run/systemd/unit-root/dev:
#     No such file or directory
#     Control process exited, code=exited, status=226/NAMESPACE
#
#   Ursache: Die Dienstdatei kapselt ihre Hilfsbefehle (PrivateDevices und
#   Verwandte). In einem LXC-Container kann systemd diese Kapselung für den
#   Reload-Befehl nicht aufbauen. Der Hauptprozess läuft davon unbeeindruckt
#   weiter — der Dienst bleibt "active".
#
#   Und genau das ist die Falle: Der Befehl scheitert, Prometheus läuft
#   weiter, und wer nicht genau hinsieht, hält seine Änderung für aktiv.
#   Sie ist es nicht. Am 29.07.2026 sind so zwei Alarmregeln beinahe
#   unbemerkt liegengeblieben.
#
# Dieses Skript macht stattdessen dreierlei:
#   1. prüft die Konfiguration, BEVOR etwas passiert
#   2. schickt das Signal direkt an den Prozess (das tut reload auch)
#   3. prüft am Messwert nach, ob das Einlesen wirklich geklappt hat
#
# Aufruf auf dem ProDesk:  /usr/local/bin/prometheus-neu-laden.sh

set -uo pipefail
export PATH="/usr/sbin:/usr/bin:/sbin:/bin"

CTID=150
ZIEL=10.1.0.35

echo "1) Konfiguration prüfen"
if ! pct exec "$CTID" -- promtool check config /etc/prometheus/prometheus.yml >/dev/null 2>&1; then
    echo "   FEHLER: Die Konfiguration ist fehlerhaft. Es wird nichts eingelesen."
    pct exec "$CTID" -- promtool check config /etc/prometheus/prometheus.yml 2>&1 | sed 's/^/   /'
    exit 1
fi
echo "   in Ordnung"

VORHER=$(curl -s --max-time 10 "http://${ZIEL}:9090/metrics" 2>/dev/null \
         | grep '^prometheus_config_last_reload_success_timestamp_seconds' \
         | awk '{printf "%.0f", $2}')

echo "2) Signal an den Prozess schicken"
if ! pct exec "$CTID" -- pkill -HUP -x prometheus; then
    echo "   FEHLER: Prozess nicht gefunden. Läuft Prometheus überhaupt?"
    exit 1
fi

# Kurz Zeit geben. Prometheus liest die Regeldateien beim Signal neu ein.
sleep 5

echo "3) Nachprüfen, ob es wirklich geklappt hat"
OK=$(curl -s --max-time 10 "http://${ZIEL}:9090/metrics" 2>/dev/null \
     | grep '^prometheus_config_last_reload_successful' | awk '{print $2}')
NACHHER=$(curl -s --max-time 10 "http://${ZIEL}:9090/metrics" 2>/dev/null \
          | grep '^prometheus_config_last_reload_success_timestamp_seconds' \
          | awk '{printf "%.0f", $2}')

if [ "${OK:-0}" != "1" ]; then
    echo "   FEHLER: Prometheus meldet ein fehlgeschlagenes Einlesen."
    echo "   Protokoll ansehen: pct exec $CTID -- journalctl -u prometheus -n 20"
    exit 1
fi

if [ "${NACHHER:-0}" = "${VORHER:-0}" ]; then
    echo "   WARNUNG: Der Zeitstempel hat sich nicht geändert."
    echo "   Möglicherweise wurde gar nichts neu eingelesen. Bitte prüfen:"
    echo "   curl -s http://${ZIEL}:9090/api/v1/rules | grep -o '\"name\":\"[^\"]*\"'"
    exit 1
fi

# grep -c zaehlt ZEILEN, und die Antwort ist eine einzige lange Zeile. Es
# muessen die Treffer gezaehlt werden, nicht die Zeilen — sonst steht hier
# immer "1".
ANZAHL=$(curl -s --max-time 10 "http://${ZIEL}:9090/api/v1/rules" 2>/dev/null \
         | grep -o '"name":"' | wc -l)
echo "   erfolgreich eingelesen, $ANZAHL Regeln aktiv"
