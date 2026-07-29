#!/bin/bash
# Wache über die Überwachung — angelegt 29.07.2026
#
# Warum es das gibt:
# Alle Alarme laufen über Prometheus und Alertmanager in CT150. Fällt dieser
# Container aus, fällt damit auch jede Alarmierung aus — und niemand erfährt
# davon. Es herrscht einfach Stille, und Stille sieht aus wie "alles gut".
#
# Genau diese Sorte Fehler hat sich an diesem Tag zweimal gezeigt: drei
# Sicherungen, die Erfolg meldeten und nichts erzeugten, und ein zweites
# Überwachungssystem, das tagelang Rot stand, ohne dass es jemand sah.
#
# Deshalb läuft diese Wache auf dem ProDesk-WIRT, also ausserhalb des
# Containers, den sie beobachtet. Sie schickt im Ernstfall direkt eine
# Telegram-Nachricht, ohne den Alertmanager zu benutzen — der wäre in
# genau dem Moment ja ausgefallen.
#
# Der Zugangsschlüssel steht NICHT in dieser Datei (das Repo ist öffentlich),
# sondern in /root/.telegram-frawo mit Rechten 600.

set -uo pipefail
export PATH="/usr/sbin:/usr/bin:/sbin:/bin"

# Die Werte lassen sich beim Aufruf überschreiben. Das ist Absicht: Nur so
# kann man den Ernstfall proben, ohne die echte Überwachung anzuhalten.
# Probe des Ausfalls:
#   ZIEL=127.0.0.1 ZUSTAND=/tmp/wachtest METRIK=/dev/null \
#   TOKEN_DATEI=/nicht/vorhanden /usr/local/bin/monitoring-watchdog.sh
ZIEL="${ZIEL:-10.1.0.35}"
CHAT_ID="${CHAT_ID:-5924907152}"
TOKEN_DATEI="${TOKEN_DATEI:-/root/.telegram-frawo}"
ZUSTAND="${ZUSTAND:-/var/lib/frawo-watchdog}"
METRIK="${METRIK:-/var/lib/node_exporter/textfile_collector/monitoring_watchdog.prom}"

mkdir -p "$ZUSTAND"

melde_telegram() {
    [ -r "$TOKEN_DATEI" ] || return 1
    local token
    # Anfuehrungszeichen wegwerfen. Beim ersten Anlegen der Datei wurden sie
    # aus der YAML mit uebernommen, und Telegram antwortete mit "Not Found" —
    # ein Fehler, den man dem Namen nach nie beim Zugangsschluessel sucht.
    token=$(tr -d "'\"" < "$TOKEN_DATEI" | tr -d '[:space:]')
    curl -s --max-time 20 \
         -d "chat_id=${CHAT_ID}" \
         --data-urlencode "text=$1" \
         "https://api.telegram.org/bot${token}/sendMessage" >/dev/null 2>&1
}

# pruefe NAME URL ERWARTETER_CODE
pruefe() {
    local name="$1" url="$2"
    local code
    code=$(curl -s -o /dev/null -w '%{http_code}' --max-time 12 "$url" 2>/dev/null)
    [ "$code" = "200" ]
}

FEHLER=""
pruefe "Prometheus"   "http://${ZIEL}:9090/-/healthy"  || FEHLER="${FEHLER}Prometheus "
pruefe "Alertmanager" "http://${ZIEL}:9093/-/healthy"  || FEHLER="${FEHLER}Alertmanager "
pruefe "Grafana"      "http://${ZIEL}:3000/api/health" || FEHLER="${FEHLER}Grafana "

MARKE="$ZUSTAND/gestoert"

if [ -n "$FEHLER" ]; then
    # Erst beim zweiten Durchlauf melden. Ein einzelner Aussetzer waehrend
    # eines Neustarts soll nicht sofort das Telefon klingeln lassen.
    if [ -f "$MARKE" ]; then
        # Nur einmal melden, nicht bei jedem Durchlauf erneut.
        if [ ! -f "$MARKE.gemeldet" ]; then
            melde_telegram "🔴 ÜBERWACHUNG AUSGEFALLEN

Nicht erreichbar: ${FEHLER}
Betroffen ist CT150 (monitoring-stack, ${ZIEL}) auf dem ProDesk.

Das heisst: Ab jetzt kommen KEINE Alarme mehr — auch nicht, wenn etwas anderes ausfällt. Diese Nachricht kommt von einer getrennten Wache auf dem Wirtssystem.

Erste Schritte:
  pct status 150
  pct start 150"
            touch "$MARKE.gemeldet"
        fi
    else
        touch "$MARKE"
    fi
    WERT=0
else
    # Erholung melden, aber nur wenn vorher wirklich gemeldet wurde.
    if [ -f "$MARKE.gemeldet" ]; then
        melde_telegram "✅ Überwachung ist wieder da

Prometheus, Alertmanager und Grafana antworten wieder. Alarme laufen ab jetzt wieder normal."
    fi
    rm -f "$MARKE" "$MARKE.gemeldet"
    WERT=1
fi

if [ -d "$(dirname "$METRIK")" ]; then
    cat > "$METRIK.tmp" <<METRICS
# HELP frawo_monitoring_watchdog_ok Ueberwachung von aussen erreichbar (1 = ja).
# TYPE frawo_monitoring_watchdog_ok gauge
frawo_monitoring_watchdog_ok $WERT
# HELP frawo_monitoring_watchdog_last_run_timestamp_seconds Zeitpunkt des letzten Wachlaufs.
# TYPE frawo_monitoring_watchdog_last_run_timestamp_seconds gauge
frawo_monitoring_watchdog_last_run_timestamp_seconds $(date +%s)
METRICS
    mv "$METRIK.tmp" "$METRIK"
fi

if [ -n "$FEHLER" ]; then
    echo "$(date '+%Y-%m-%d %H:%M') GESTOERT: $FEHLER"
    exit 1
fi
echo "$(date '+%Y-%m-%d %H:%M') OK Prometheus, Alertmanager und Grafana antworten"
