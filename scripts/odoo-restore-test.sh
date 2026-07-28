#!/usr/bin/env bash
# Wiederherstellungstest fuer die Odoo-Sicherung.
#
# Warum: Bis zum 28.07.2026 wurde nie geprueft, ob aus einer Sicherung
# tatsaechlich wieder eine funktionierende Datenbank wird. Wir wussten nur,
# dass die Datei LESBAR ist (pg_restore --list). Das ist ein Unterschied wie
# zwischen "das Ersatzrad ist im Kofferraum" und "das Ersatzrad passt".
#
# Was passiert:
#   1. Der juengste Dump wird in eine WEGWERF-Datenbank eingespielt.
#   2. Die Zeilenzahlen wichtiger Tabellen werden gegen die Produktivdatenbank
#      verglichen.
#   3. Die Wegwerf-Datenbank wird wieder geloescht.
#
# SICHERHEIT: Der Zielname ist fest verdrahtet und wird vor jedem Schritt
# gegen den Produktivnamen geprueft. Das Skript bricht ab, bevor es die
# Produktivdatenbank auch nur anfassen koennte.

set -uo pipefail
export PATH="/usr/sbin:/usr/bin:/sbin:/bin"

CTID=140
PGC=frawotech-db-1
PROD=FraWo_GbR
TEST=FraWo_Wiederherstellungstest
DUMPDIR=/mnt/data_family/odoo-sql-dumps

# --- Sicherheitssperre ------------------------------------------------------
if [ "$TEST" = "$PROD" ]; then
    echo "ABBRUCH: Testdatenbank traegt den Produktivnamen."
    exit 1
fi

psql_prod() { pct exec "$CTID" -- docker exec "$PGC" psql -U odoo -d "$PROD" -tAc "$1" 2>/dev/null; }
psql_test() { pct exec "$CTID" -- docker exec "$PGC" psql -U odoo -d "$TEST" -tAc "$1" 2>/dev/null; }
psql_adm()  { pct exec "$CTID" -- docker exec "$PGC" psql -U odoo -d postgres -tAc "$1" 2>/dev/null; }

aufraeumen() {
    echo ""
    echo "Raeume auf..."
    psql_adm "DROP DATABASE IF EXISTS \"$TEST\";" >/dev/null 2>&1
    pct exec "$CTID" -- docker exec "$PGC" rm -f /tmp/restore_test.dump 2>/dev/null
    pct exec "$CTID" -- rm -f /tmp/restore_test.dump 2>/dev/null
    rm -f /tmp/restore_test.dump 2>/dev/null
    echo "  Wegwerf-Datenbank entfernt."
}
trap aufraeumen EXIT

echo "=== Wiederherstellungstest Odoo  $(date '+%Y-%m-%d %H:%M') ==="
echo ""

DUMP=$(ls -t "$DUMPDIR"/${PROD}-*.dump 2>/dev/null | head -1)
if [ -z "$DUMP" ]; then
    echo "ABBRUCH: keine Sicherung gefunden."
    exit 1
fi
echo "Getestete Datei: $(basename "$DUMP") ($(du -h "$DUMP" | cut -f1))"
echo ""

# --- 1. Zahlen der Produktivdatenbank merken -------------------------------
echo "Lese Vergleichswerte aus der Produktivdatenbank..."
declare -A VORHER
for t in res_partner project_task account_move product_template res_users mail_message; do
    VORHER[$t]=$(psql_prod "SELECT COUNT(*) FROM $t;")
    printf '  %-18s %s Zeilen\n' "$t" "${VORHER[$t]:-?}"
done
echo ""

# --- 2. Dump in den Container bringen --------------------------------------
echo "Uebertrage die Sicherung in den Datenbank-Container..."
cp "$DUMP" /tmp/restore_test.dump
pct push "$CTID" /tmp/restore_test.dump /tmp/restore_test.dump >/dev/null 2>&1
pct exec "$CTID" -- docker cp /tmp/restore_test.dump "$PGC":/tmp/restore_test.dump >/dev/null 2>&1

# --- 3. Wegwerf-Datenbank anlegen und einspielen ---------------------------
echo "Lege Wegwerf-Datenbank an: $TEST"
psql_adm "DROP DATABASE IF EXISTS \"$TEST\";" >/dev/null 2>&1
psql_adm "CREATE DATABASE \"$TEST\" OWNER odoo;" >/dev/null 2>&1

if [ "$(psql_adm "SELECT 1 FROM pg_database WHERE datname='$TEST';")" != "1" ]; then
    echo "ABBRUCH: Wegwerf-Datenbank liess sich nicht anlegen."
    exit 1
fi

echo "Spiele die Sicherung ein... (das dauert etwas)"
pct exec "$CTID" -- docker exec "$PGC" pg_restore -U odoo -d "$TEST" --no-owner --no-privileges /tmp/restore_test.dump > /tmp/restore_out.txt 2>&1
RC=$?
WARNUNGEN=$(grep -ci 'error' /tmp/restore_out.txt 2>/dev/null || echo 0)
echo "  Rueckgabewert: $RC, Meldungen mit 'error': $WARNUNGEN"
rm -f /tmp/restore_out.txt

# --- 4. Vergleich -----------------------------------------------------------
echo ""
echo "Vergleiche wiederhergestellte Daten mit der Produktivdatenbank:"
echo ""
printf '  %-18s %10s %10s   %s\n' "Tabelle" "Produktiv" "Wiederher." "Ergebnis"
printf '  %-18s %10s %10s   %s\n' "------------------" "----------" "----------" "--------"

ABWEICHUNGEN=0
GEPRUEFT=0
for t in res_partner project_task account_move product_template res_users mail_message; do
    N=$(psql_test "SELECT COUNT(*) FROM $t;")
    P=${VORHER[$t]:-}
    GEPRUEFT=$((GEPRUEFT + 1))
    if [ -z "$N" ]; then
        printf '  %-18s %10s %10s   FEHLT\n' "$t" "$P" "-"
        ABWEICHUNGEN=$((ABWEICHUNGEN + 1))
    elif [ "$N" = "$P" ]; then
        printf '  %-18s %10s %10s   gleich\n' "$t" "$P" "$N"
    else
        printf '  %-18s %10s %10s   ABWEICHUNG\n' "$t" "$P" "$N"
        ABWEICHUNGEN=$((ABWEICHUNGEN + 1))
    fi
done

# --- 5. Stichprobe auf echten Inhalt ---------------------------------------
echo ""
echo "Stichprobe auf tatsaechlichen Inhalt:"
FIRMA=$(psql_test "SELECT name FROM res_partner WHERE id=1;")
echo "  Firmenname aus der Wiederherstellung: ${FIRMA:-(leer)}"
TABELLEN=$(psql_test "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public';")
echo "  Tabellen insgesamt: ${TABELLEN:-?}"

# --- Ergebnis ---------------------------------------------------------------
echo ""
if [ "$ABWEICHUNGEN" -eq 0 ] && [ -n "$FIRMA" ] && [ "$RC" -eq 0 ]; then
    echo "ERGEBNIS: BESTANDEN - aus der Sicherung wird wieder eine vollstaendige Datenbank."
    ERG=1
else
    echo "ERGEBNIS: DURCHGEFALLEN - $ABWEICHUNGEN von $GEPRUEFT Tabellen weichen ab."
    ERG=0
fi

# --- Metrik fuers Monitoring ------------------------------------------------
TEXTFILE_DIR=/var/lib/node_exporter/textfile_collector
if [ -d "$TEXTFILE_DIR" ]; then
    M="$TEXTFILE_DIR/odoo_restore_test.prom"
    {
        echo "# HELP frawo_odoo_restore_test_ok Wiederherstellungstest bestanden (1) oder nicht (0)."
        echo "# TYPE frawo_odoo_restore_test_ok gauge"
        echo "frawo_odoo_restore_test_ok $ERG"
        echo "# HELP frawo_odoo_restore_test_timestamp_seconds Zeitpunkt des letzten Wiederherstellungstests."
        echo "# TYPE frawo_odoo_restore_test_timestamp_seconds gauge"
        echo "frawo_odoo_restore_test_timestamp_seconds $(date +%s)"
    } > "$M.tmp"
    mv "$M.tmp" "$M"
fi

[ "$ERG" -eq 1 ] || exit 1
