#!/bin/bash
# WireGuard-Tunnel überwachen — angelegt 26.08.2026
#
# Warum es das gibt:
# Der Tunnel wg1 verbindet Rothkreuz mit dem Heimnetz der Eltern in
# Stockenweiler. Er war schon einmal wochenlang tot, ohne dass es jemand
# merkte. Aufgefallen ist es erst indirekt daran, dass 23 von 27
# Home-Assistant-Geräten auf "unavailable" standen — niemand hat auf den
# Tunnel geschaut, weil nichts auf ihn hingewiesen hat.
#
# Der Grund ist eine Eigenheit von WireGuard: Den Hostnamen der Gegenstelle
# (die MyFRITZ-Adresse der Eltern-Fritzbox) löst wg NUR BEIM START auf.
# Bekommt die Fritzbox nach einer Zwangstrennung eine neue IP, sendet wg
# stur weiter an die alte. Der Dienst bleibt "active", die Schnittstelle
# bleibt "up", das Log bleibt still. Nur der Handshake bleibt aus.
#
# Deshalb wird hier NICHT geprüft, ob der Dienst läuft, sondern ob der
# letzte Handshake noch frisch ist. Am Ergebnis messen, nicht am Vorgang.
#
# Bewusst KEIN Alarm auf wg0: Das ist Wolfs Fernzugang vom StudioPC, der
# ist die meiste Zeit legitim aus. Die Metrik wird trotzdem geschrieben,
# damit man sie im Dashboard nachsehen kann — nur die Alarmregel lässt
# wg0 aus. Sonst hätte man Dauerlärm, und Dauerlärm bringt einem bei,
# Alarme wegzuklicken.

set -uo pipefail
export PATH="/usr/sbin:/usr/bin:/sbin:/bin"

# Die Werte lassen sich beim Aufruf überschreiben. Das ist Absicht: Nur so
# lässt sich der Ernstfall proben, ohne die echte Überwachung anzufassen.
# Probe mit künstlich altem Handshake:
#   METRIK=/tmp/wg-probe.prom /usr/local/bin/wireguard-tunnel-pruefen.sh
CT="${CT:-106}"
METRIK="${METRIK:-/var/lib/node_exporter/textfile_collector/wireguard.prom}"
SCHWELLE="${SCHWELLE:-300}"

JETZT=$(date +%s)

# Klarnamen statt Schlüsselfragmente. Im Alarm soll stehen, WOHIN der Tunnel
# geht — nicht, wie sein öffentlicher Schlüssel anfängt.
klarname() {
    case "$1" in
        wg0) echo "studiopc-fernzugang" ;;
        wg1) echo "alopri-stockenweiler" ;;
        *)   echo "$1" ;;
    esac
}

zeilen_alter=""
zeilen_ok=""
schnittstellen=0

schnittstellen_liste=$(pct exec "$CT" -- wg show interfaces 2>/dev/null | tr -s ' \t' '\n')

for iface in $schnittstellen_liste; do
    [ -n "$iface" ] || continue
    schnittstellen=$((schnittstellen + 1))
    name=$(klarname "$iface")

    # "wg show <iface> dump": Zeile 1 beschreibt die Schnittstelle selbst,
    # ab Zeile 2 folgt je eine Gegenstelle. Feld 5 ist der Zeitstempel des
    # letzten Handshakes, 0 heisst "noch nie zustande gekommen".
    while IFS=$'\t' read -r _pub _psk _endp _ips hs _rest; do
        case "${hs:-}" in
            ''|*[!0-9]*) continue ;;
        esac

        if [ "$hs" -eq 0 ]; then
            # Noch nie verbunden. -1 statt einer riesigen Zahl, damit man im
            # Dashboard "nie" von "lange her" unterscheiden kann.
            a=-1
            f=0
        else
            a=$((JETZT - hs))
            if [ "$a" -lt "$SCHWELLE" ]; then f=1; else f=0; fi
        fi

        zeilen_alter="${zeilen_alter}frawo_wireguard_handshake_alter_sekunden{interface=\"${iface}\",gegenstelle=\"${name}\"} ${a}"$'\n'
        zeilen_ok="${zeilen_ok}frawo_wireguard_gegenstelle_ok{interface=\"${iface}\",gegenstelle=\"${name}\"} ${f}"$'\n'
    done < <(pct exec "$CT" -- wg show "$iface" dump 2>/dev/null | tail -n +2)
done

# Atomar schreiben. Ein halb geschriebenes .prom bringt den Exporter dazu,
# die ganze Datei zu verwerfen — dann stünde die Überwachung still, ohne
# dass jemand etwas sieht. Genau der Fehler, den diese Prüfung verhindern soll.
TMP=$(mktemp "${METRIK}.XXXXXX") || exit 1
trap 'rm -f "$TMP"' EXIT

{
    echo "# HELP frawo_wireguard_handshake_alter_sekunden Alter des letzten Handshakes in Sekunden (-1 = noch nie zustande gekommen)."
    echo "# TYPE frawo_wireguard_handshake_alter_sekunden gauge"
    printf '%s' "$zeilen_alter"
    echo "# HELP frawo_wireguard_gegenstelle_ok 1 = Handshake juenger als die Schwelle."
    echo "# TYPE frawo_wireguard_gegenstelle_ok gauge"
    printf '%s' "$zeilen_ok"
    echo "# HELP frawo_wireguard_schnittstellen Anzahl gefundener WireGuard-Schnittstellen."
    echo "# TYPE frawo_wireguard_schnittstellen gauge"
    echo "frawo_wireguard_schnittstellen ${schnittstellen}"
    echo "# HELP frawo_wireguard_letzter_lauf_timestamp_seconds Zeitpunkt des letzten Laufs dieser Pruefung."
    echo "# TYPE frawo_wireguard_letzter_lauf_timestamp_seconds gauge"
    echo "frawo_wireguard_letzter_lauf_timestamp_seconds ${JETZT}"
} > "$TMP"

chmod 644 "$TMP"
mv -f "$TMP" "$METRIK"
trap - EXIT

exit 0
