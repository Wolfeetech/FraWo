#!/bin/bash
# Odoo Agent-Queue-Metriken für Prometheus erfassen — angelegt 18.09.2026 (Odoo #1467)
#
# Liest den Status der Agent-Queue direkt aus der PostgreSQL-Datenbank
# in CT140 und schreibt ihn in das Textfile-Collector-Verzeichnis von
# node_exporter auf dem Anker-Wirt.
#
# Enthält Zähler für:
# - queued: Aufgaben, die auf Bearbeitung durch den Agenten warten
# - error: Aufgaben mit Fehlern bei der Bearbeitung
# - done: erfolgreich verarbeitete Aufgaben
# - skip: übersprungene Aufgaben
#
# Sowie einen Zeitstempel des letzten Laufs, damit Prometheus per absent()
# oder Alter prüfen kann, ob die Messung selbst noch stattfindet.

set -uo pipefail
export PATH="/usr/sbin:/usr/bin:/sbin:/bin"

CT="${CT:-140}"
DB_CONTAINER="${DB_CONTAINER:-frawotech-db-1}"
DB_NAME="${DB_NAME:-FraWo_GbR}"
DB_USER="${DB_USER:-odoo}"
TEXTFILE_DIR="${TEXTFILE_DIR:-/var/lib/node_exporter/textfile_collector}"
METRIK="${METRIK:-$TEXTFILE_DIR/odoo_queue.prom}"
TMP="${METRIK}.tmp.$$"

cleanup() {
    rm -f "$TMP"
}
trap cleanup EXIT

# 1. Zähler aus PostgreSQL ermitteln
SQL="SELECT coalesce(agent_state, 'unset'), count(id) FROM project_task WHERE active GROUP BY agent_state;"
ROHWERTE=$(pct exec "$CT" -- docker exec -i "$DB_CONTAINER" psql -U "$DB_USER" -d "$DB_NAME" -t -A -c "$SQL" 2>/dev/null)

if [ $? -ne 0 ] || [ -z "$ROHWERTE" ]; then
    echo "FEHLER: Konnte Queue-Status aus CT$CT/$DB_CONTAINER nicht lesen." >&2
    exit 1
fi

QUEUED=0
ERRORS=0
DONE=0
SKIP=0
UNSET=0

while IFS='|' read -r STATE COUNT; do
    [ -n "$STATE" ] || continue
    case "$STATE" in
        queued) QUEUED="$COUNT" ;;
        error)  ERRORS="$COUNT" ;;
        done)   DONE="$COUNT" ;;
        skip)   SKIP="$COUNT" ;;
        unset)  UNSET="$COUNT" ;;
    esac
done <<< "$ROHWERTE"

JETZT=$(date +%s)

# 2. Metrik atomar schreiben
mkdir -p "$TEXTFILE_DIR"
cat > "$TMP" <<METRIKEN
# HELP frawo_odoo_agent_queue_length Anzahl Aufgaben in der Agent-Warteschlange (Status queued).
# TYPE frawo_odoo_agent_queue_length gauge
frawo_odoo_agent_queue_length $QUEUED

# HELP frawo_odoo_agent_queue_errors Anzahl Aufgaben im Fehlerzustand der Queue (Status error).
# TYPE frawo_odoo_agent_queue_errors gauge
frawo_odoo_agent_queue_errors $ERRORS

# HELP frawo_odoo_agent_queue_done Anzahl vom Agenten erfolgreich bearbeiteter Aufgaben.
# TYPE frawo_odoo_agent_queue_done gauge
frawo_odoo_agent_queue_done $DONE

# HELP frawo_odoo_agent_queue_letzter_lauf_timestamp_seconds Zeitpunkt der letzten Queue-Prüfung.
# TYPE frawo_odoo_agent_queue_letzter_lauf_timestamp_seconds gauge
frawo_odoo_agent_queue_letzter_lauf_timestamp_seconds $JETZT
METRIKEN

chmod 644 "$TMP"
mv "$TMP" "$METRIK"
exit 0
