#!/usr/bin/env bash
# Naechtliches Rueckschreiben der Radio-Redaktionsurteile nach beets (CT120).
#
# Laeuft auf dem ProDesk-Wirt (stock-pve), NICHT in CT120 selbst: CT120 hat
# keinen eigenen node_exporter, der Wirt schon (textfile_collector unter
# /var/lib/node_exporter/textfile_collector). Gleiches Muster wie das
# bestehende /usr/local/bin/odoo-sql-backup.sh (Repo: scripts/odoo-sql-backup.sh):
# `pct exec` ins Ziel, Metrik danach lokal am Wirt schreiben. Vorteil: kein
# zusaetzlicher Dienst in CT120 noetig, Prometheus scrapet den Wirt ohnehin
# schon fuer alle anderen Backup-TUEV-Metriken.
#
# Das eigentliche Skript liegt in CT120 unter
# /opt/musikredaktion/rueckschreiben.py (Repo-Kopie:
# deployments/musikredaktion/rueckschreiben.py) und sichert die beets-DB
# SELBST vor jedem echten Schreibvorgang (sqlite3 Online-Backup-API) -- hier
# wird nichts zusaetzlich gesichert.
#
# Odoo-Aufgabe #1090, Jarvis-Vorgabe Nachricht 22101 (30.09./01.10.2026):
# systemd-Service/-Timer 05:30 Europe/Berlin, flock, Persistent=true,
# Ergebniskennzahl mit Staleness-/Fehleralarm.
#
# Aufruf: frawo-musikredaktion-rueckschreiben.sh [--probe]
#   --probe: nur rechnen/anzeigen (an rueckschreiben.py durchgereicht),
#            schreibt NIE eine Metrik -- ein Probelauf ist kein Erfolg im
#            Sinne der Staleness-Pruefung und soll den letzten echten
#            Erfolgszeitstempel nicht verdecken.
#
# Der flock-Lock wird NICHT hier im Skript gesetzt, sondern bereits in der
# systemd-ExecStart-Zeile (`flock -n ... dieses-Skript`) -- damit deckt der
# Lock wirklich die gesamte Ausfuehrung ab, inklusive des allerersten
# pct-exec-Aufrufs.

set -uo pipefail
export PATH="/usr/sbin:/usr/bin:/sbin:/bin"

CTID=120
TEXTFILE_DIR=/var/lib/node_exporter/textfile_collector
# Zwei getrennte Dateien, bewusst:
#   ..._erfolg.prom   -> JEDEN echten Lauf ueberschrieben (1/0), fuer den
#                        schnellen "Service fehlgeschlagen"-Alarm.
#   ..._stand.prom    -> NUR bei Erfolg ueberschrieben, damit ein
#                        fehlgeschlagener Lauf die zuletzt bekannten guten
#                        Werte (Zeitstempel/geschrieben/offen) nicht loescht
#                        -- sonst wuerde die Staleness-Regel durch einen
#                        einzelnen Fehlschlag sofort auf "Metrik fehlt"
#                        umspringen, statt sauber nach 26h zu greifen.
METRIC_ERFOLG="$TEXTFILE_DIR/musikredaktion_rueckschreiben_erfolg.prom"
METRIC_STAND="$TEXTFILE_DIR/musikredaktion_rueckschreiben_stand.prom"

PROBE=0
[ "${1:-}" = "--probe" ] && PROBE=1

ARGS=()
[ "$PROBE" = "1" ] && ARGS+=(--probe)

AUSGABE=$(pct exec "$CTID" -- python3 /opt/musikredaktion/rueckschreiben.py "${ARGS[@]}" 2>&1)
CODE=$?

echo "$AUSGABE"

if [ "$PROBE" = "1" ]; then
    echo "PROBE-Lauf -- keine Metrik geschrieben (Exit $CODE)."
    exit "$CODE"
fi

# Erwartete Zeilen aus rueckschreiben.py (main()):
#   "Export-Zeilen: 123, Titel gesamt: 45, zugeordnet: 40, offen: 5"
#   "geschrieben: 12 Titel"                      (nur bei echtem Lauf)
GESCHRIEBEN=$(printf '%s\n' "$AUSGABE" | sed -n 's/^geschrieben: \([0-9][0-9]*\) Titel$/\1/p')
OFFEN=$(printf '%s\n' "$AUSGABE" | sed -n \
    's/^Export-Zeilen: [0-9][0-9]*, Titel gesamt: [0-9][0-9]*, zugeordnet: [0-9][0-9]*, offen: \([0-9][0-9]*\)$/\1/p')

if [ "$CODE" -eq 0 ] && [ -n "$GESCHRIEBEN" ] && [ -n "$OFFEN" ]; then
    ERFOLG=1
else
    ERFOLG=0
    echo "FEHLER: Lauf fehlgeschlagen oder Ausgabe nicht auswertbar (Exit $CODE)." >&2
fi

if [ -d "$TEXTFILE_DIR" ]; then
    cat > "$METRIC_ERFOLG.tmp" <<METRICS
# HELP frawo_musikredaktion_rueckschreiben_erfolg 1 = letzter Lauf erfolgreich, 0 = fehlgeschlagen.
# TYPE frawo_musikredaktion_rueckschreiben_erfolg gauge
frawo_musikredaktion_rueckschreiben_erfolg $ERFOLG
METRICS
    mv "$METRIC_ERFOLG.tmp" "$METRIC_ERFOLG"

    if [ "$ERFOLG" = "1" ]; then
        cat > "$METRIC_STAND.tmp" <<METRICS
# HELP frawo_musikredaktion_rueckschreiben_letzter_erfolg_timestamp_seconds Zeitpunkt des letzten erfolgreichen Rueckschreibens.
# TYPE frawo_musikredaktion_rueckschreiben_letzter_erfolg_timestamp_seconds gauge
frawo_musikredaktion_rueckschreiben_letzter_erfolg_timestamp_seconds $(date +%s)
# HELP frawo_musikredaktion_rueckschreiben_geschrieben Anzahl tatsaechlich geschriebener Titel im letzten erfolgreichen Lauf.
# TYPE frawo_musikredaktion_rueckschreiben_geschrieben gauge
frawo_musikredaktion_rueckschreiben_geschrieben $GESCHRIEBEN
# HELP frawo_musikredaktion_rueckschreiben_offen Anzahl nicht eindeutig zuordenbarer Titel im letzten erfolgreichen Lauf.
# TYPE frawo_musikredaktion_rueckschreiben_offen gauge
frawo_musikredaktion_rueckschreiben_offen $OFFEN
METRICS
        mv "$METRIC_STAND.tmp" "$METRIC_STAND"
    fi
fi

exit "$CODE"
