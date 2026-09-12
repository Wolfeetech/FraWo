#!/usr/bin/env bash
# Wiederherstellungstest fuer die Odoo-Sicherung (Anker-Fassung).
#
# Warum: Bis zum 28.07.2026 wurde nie geprueft, ob aus einer Sicherung
# tatsaechlich wieder eine funktionierende Datenbank wird. Wir wussten nur,
# dass die Datei LESBAR ist. Das ist ein Unterschied wie zwischen
# "das Ersatzrad ist im Kofferraum" und "das Ersatzrad passt".
#
# Portiert auf proxmox-anker am 12.09.2026 nach ProDesk-Ausfall (Task #1391).
#
# Was passiert:
#   1. Der juengste Dump in CT140 (/var/backups/odoo/FraWo_GbR_*.sql.gz) wird ermittelt.
#   2. Eine WEGWERF-Datenbank (FraWo_Wiederherstellungstest) wird angelegt.
#   3. Der Dump wird per zcat | psql in die Test-DB eingespielt.
#   4. Zeilenzahlen wichtiger Tabellen werden gegen die Produktivdatenbank geprueft.
#   5. Stichprobe auf echten Inhalt (Firmenname ID 1, Tabellenanzahl).
#   6. Die Wegwerf-Datenbank wird per trap immer restlos entfernt.
#   7. Prometheus-Metriken werden atomar geschrieben.
#
# SICHERHEIT: Der Zielname ist fest verdrahtet und wird vor jedem Schritt
# gegen den Produktivnamen geprueft. Das Skript bricht sofort ab, bevor es
# die Produktivdatenbank auch nur anfassen koennte.

set -uo pipefail
export PATH="/usr/sbin:/usr/bin:/sbin:/bin"

CTID=140
PGC="frawotech-db-1"
PROD="FraWo_GbR"
TEST="FraWo_Wiederherstellungstest"
DUMPDIR="/var/backups/odoo"
LOGFILE="/var/log/odoo-restore-test.log"
TEXTFILE_DIR="/var/lib/node_exporter/textfile_collector"
METRIK="$TEXTFILE_DIR/odoo_restore_test.prom"

# --- Sicherheitssperre ------------------------------------------------------
if [ "$TEST" = "$PROD" ] || [ -z "$TEST" ]; then
    echo "ABBRUCH: Sicherheitspruefung fehlgeschlagen: Testname '$TEST' ungueltig." >&2
    exit 1
fi

psql_prod() { pct exec "$CTID" -- docker exec "$PGC" psql -U odoo -d "$PROD" -tAc "$1" 2>/dev/null; }
psql_test() { pct exec "$CTID" -- docker exec "$PGC" psql -U odoo -d "$TEST" -tAc "$1" 2>/dev/null; }
psql_adm()  { pct exec "$CTID" -- docker exec "$PGC" psql -U odoo -d postgres -c "$1" 2>/dev/null; }

aufraeumen() {
    echo ""
    echo "Raeume auf..."
    psql_adm "DROP DATABASE IF EXISTS \"$TEST\";" >/dev/null 2>&1 || true
    echo "  Wegwerf-Datenbank $TEST entfernt."
}
trap aufraeumen EXIT

echo "=== Wiederherstellungstest Odoo $(date '+%Y-%m-%d %H:%M:%S') ==="
echo ""

# 1. Neuesten Dump in CT140 finden
DUMP=$(pct exec "$CTID" -- bash -c "ls -t $DUMPDIR/${PROD}_*.sql.gz 2>/dev/null | head -1" || true)
if [ -z "$DUMP" ]; then
    echo "ABBRUCH: Keine Sicherungsdatei in CT140:$DUMPDIR gefunden!"
    exit 1
fi

DUMP_GROESSE=$(pct exec "$CTID" -- bash -c "du -h '$DUMP' | cut -f1" || true)
echo "Getestete Datei: $(basename "$DUMP") ($DUMP_GROESSE)"
echo ""

# 2. Zahlen der Produktivdatenbank vorab auslesen
echo "Lese Vergleichswerte aus der Produktivdatenbank ($PROD)..."
declare -A VORHER
TABELLEN_LISTE="res_partner project_task account_move product_template res_users mail_message"
for t in $TABELLEN_LISTE; do
    COUNT=$(psql_prod "SELECT COUNT(*) FROM $t;")
    VORHER[$t]="${COUNT:-0}"
    printf '  %-18s %s Zeilen\n' "$t" "${VORHER[$t]}"
done
echo ""

# 3. Wegwerf-Datenbank vorbereiten
echo "Lege Wegwerf-Datenbank an: $TEST"
psql_adm "DROP DATABASE IF EXISTS \"$TEST\";" >/dev/null 2>&1 || true
psql_adm "CREATE DATABASE \"$TEST\" OWNER odoo;" >/dev/null 2>&1

DB_CHECK=$(pct exec "$CTID" -- docker exec "$PGC" psql -U odoo -d postgres -tAc "SELECT 1 FROM pg_database WHERE datname='$TEST';" 2>/dev/null || true)
if [ "$DB_CHECK" != "1" ]; then
    echo "ABBRUCH: Wegwerf-Datenbank liess sich nicht anlegen!"
    exit 1
fi

# 4. Dump einspielen
echo "Spiele Sicherung per zcat in $TEST ein (Dauer ca. 1 Minute)..."
pct exec "$CTID" -- bash -c "zcat '$DUMP' | docker exec -i '$PGC' psql -U odoo -d '$TEST' -q"
RC=$?
echo "  Import beendet mit Exit-Code: $RC"

# 5. Tabellen vergleichen
echo ""
echo "Vergleiche wiederhergestellte Daten mit Produktivdatenbank:"
printf '  %-18s %10s %10s   %s\n' "Tabelle" "Produktiv" "Wiederher." "Ergebnis"
printf '  %-18s %10s %10s   %s\n' "------------------" "----------" "----------" "--------"

ABWEICHUNGEN=0
GEPRUEFT=0
for t in $TABELLEN_LISTE; do
    N=$(psql_test "SELECT COUNT(*) FROM $t;")
    P=${VORHER[$t]:-0}
    GEPRUEFT=$((GEPRUEFT + 1))
    
    # Plausibilitätsprüfung: Tabelle muss existieren, Zeilenzahl > 0 und plausibel nahe am Produktivstand (Dump von heute Nacht)
    if [ -z "$N" ] || [ "$N" -le 0 ]; then
        printf '  %-18s %10s %10s   FEHLT/LEER\n' "$t" "$P" "${N:--}"
        ABWEICHUNGEN=$((ABWEICHUNGEN + 1))
    elif [ "$N" -eq "$P" ]; then
        printf '  %-18s %10s %10s   exakt gleich\n' "$t" "$P" "$N"
    elif [ "$N" -le "$P" ] && [ "$N" -ge $(( P > 100 ? P - 100 : 1 )) ]; then
        printf '  %-18s %10s %10s   gleich/plausibel\n' "$t" "$P" "$N"
    else
        printf '  %-18s %10s %10s   ABWEICHUNG\n' "$t" "$P" "$N"
        ABWEICHUNGEN=$((ABWEICHUNGEN + 1))
    fi
done

# 6. Stichprobe auf echten Inhalt
echo ""
echo "Stichprobe auf tatsaechlichen Inhalt:"
FIRMA=$(psql_test "SELECT name FROM res_partner WHERE id=1;")
echo "  Firmenname aus der Wiederherstellung: ${FIRMA:-(leer)}"
TABELLEN=$(psql_test "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public';")
echo "  Tabellen insgesamt in Test-DB: ${TABELLEN:-0}"

# 7. Gesamtergebnis
echo ""
if [ "$ABWEICHUNGEN" -eq 0 ] && [ "$FIRMA" = "FraWo GbR" ] && [ "${TABELLEN:-0}" -ge 700 ] && [ "$RC" -eq 0 ]; then
    echo "ERGEBNIS: BESTANDEN - aus der Sicherung entsteht eine vollstaendige Datenbank."
    ERG=1
else
    echo "ERGEBNIS: DURCHGEFALLEN - Fehler oder Abweichungen festgestellt."
    ERG=0
fi

# 8. Prometheus-Metrik
if [ -d "$TEXTFILE_DIR" ]; then
    TMP_METRIK="$METRIK.tmp.$$"
    {
        echo "# HELP frawo_odoo_restore_test_ok Wiederherstellungstest bestanden (1) oder nicht (0)."
        echo "# TYPE frawo_odoo_restore_test_ok gauge"
        echo "frawo_odoo_restore_test_ok $ERG"
        echo "# HELP frawo_odoo_restore_test_timestamp_seconds Zeitpunkt des letzten Wiederherstellungstests."
        echo "# TYPE frawo_odoo_restore_test_timestamp_seconds gauge"
        echo "frawo_odoo_restore_test_timestamp_seconds $(date +%s)"
    } > "$TMP_METRIK"
    chmod 644 "$TMP_METRIK"
    mv "$TMP_METRIK" "$METRIK"
    echo "Metrik aktualisiert: $METRIK"
fi

[ "$ERG" -eq 1 ] || exit 1

