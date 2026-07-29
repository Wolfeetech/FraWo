#!/bin/bash
# FraWo — Nachtmodus für den ProDesk
# Angelegt 29.07.2026.
#
# ===========================================================================
# WOZU
# ===========================================================================
# Wolf: "bitte aber auch zwischen 22 und 6 uhr künftig eine art nachtmodus...
#        bei möglichst wenig Geräuschen"
#
# Der ProDesk steht im Wohnbereich. Nachts stören zwei Dinge:
#   1. der Lüfter, angetrieben von der Prozessortemperatur
#   2. die mechanische USB-Festplatte, wenn die Cloud-Sicherung liest
#
# ===========================================================================
# WAS DER NACHTMODUS TUT
# ===========================================================================
# 1. TAKTREGELUNG auf "powersave"
#    Gemessen am 29.07.2026: Der Knoten lief auf "performance" mit 3,6 GHz
#    und 74-76 Grad. Powersave lässt den Takt bei Bedarf sinken — das ist
#    der grösste Hebel gegen Lüfterlärm, weil weniger Wärme entsteht, die
#    weggekühlt werden muss.
#
#    Der Sendebetrieb leidet nicht: Ein Radiostream braucht wenig Rechenzeit,
#    und powersave taktet bei Last weiterhin hoch — nur nicht dauerhaft.
#
# 2. LÜFTER auf Automatik
#    Falls tagsüber der Maximalmodus gesetzt wurde, wird er zurückgenommen.
#
# 3. HINTERGRUNDARBEIT auf niedrigste Priorität
#    Sicherungen und Musikverwaltung bekommen die niedrigste Prozessor- und
#    Plattenpriorität. Sie laufen weiter, drängeln aber nicht.
#
# WAS BEWUSST NICHT ABGESCHALTET WIRD
# Die nächtlichen Sicherungen (Odoo 02:15, Radio 03:00, PBS 03:30). Die sind
# kurz und wichtig — sie abzuschalten hiesse, Ruhe gegen Datensicherheit zu
# tauschen. Das wäre der falsche Handel.
#
# ===========================================================================
# AUFRUF
# ===========================================================================
#   nachtmodus.sh an     ab 22:00
#   nachtmodus.sh aus    ab 06:00
#   nachtmodus.sh status

set -uo pipefail
export PATH="/usr/sbin:/usr/bin:/sbin:/bin"

HP_PWM=/sys/class/hwmon/hwmon1/pwm1_enable
MARKE=/run/frawo-nachtmodus

takt_setzen() {
    local ziel="$1" n=0
    for g in /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor; do
        [ -w "$g" ] && echo "$ziel" > "$g" 2>/dev/null && n=$((n+1))
    done
    echo "  Taktregelung auf \"$ziel\" ($n Kerne)"
}

hintergrund_drosseln() {
    local n=0
    for muster in beet rclone vzdump pg_dump; do
        for p in $(pgrep -x "$muster" 2>/dev/null); do
            renice -n 19 -p "$p" >/dev/null 2>&1
            ionice -c3 -p "$p" >/dev/null 2>&1
            n=$((n+1))
        done
    done
    echo "  $n Hintergrundprozesse auf niedrigste Priorität"
}

temperatur() {
    local t
    t=$(cat /sys/class/hwmon/hwmon2/temp1_input 2>/dev/null)
    [ -n "$t" ] && echo "  Prozessor: $((t/1000)) Grad"
}

case "${1:-status}" in
  an)
    echo "=== Nachtmodus AN ==="
    takt_setzen powersave
    if [ -w "$HP_PWM" ]; then
        echo 2 > "$HP_PWM" 2>/dev/null
        echo "  Lüfter auf Automatik"
    fi
    hintergrund_drosseln
    touch "$MARKE"
    temperatur
    ;;
  aus)
    echo "=== Nachtmodus AUS ==="
    takt_setzen performance
    rm -f "$MARKE"
    temperatur
    ;;
  status)
    if [ -f "$MARKE" ]; then echo "  Nachtmodus: AN"; else echo "  Nachtmodus: aus"; fi
    echo "  Taktregelung: $(cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor 2>/dev/null)"
    printf '  Takt jetzt:   %.1f GHz\n' \
        "$(awk '{print $1/1000000}' /sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq 2>/dev/null)"
    [ -r "$HP_PWM" ] && echo "  Lüfterschalter: $(cat "$HP_PWM")  (0 = Maximum, 2 = Automatik)"
    temperatur
    ;;
  *)
    echo "Aufruf: $0 an | aus | status"
    exit 1
    ;;
esac
