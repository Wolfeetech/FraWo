#!/usr/bin/env bash
# FraWo — verschlüsselte Odoo-Kopie in die Cloud (Anker-Fassung)
#
# Warum es das gibt (08.09.2026):
# Bis zum Tod des ProDesk lief auf ihm /usr/local/bin/odoo-sql-backup.sh und
# schob die Odoo-Datenbank stündlich verschlüsselt nach gcrypt:Odoo. Mit dem
# Rechner ist auch dieser Weg gestorben — letzte verschlüsselte Kopie:
# 07.09.2026 04:15. Seither ging die Datenbank nur noch als Teil des
# nächtlichen Container-Abzugs nach Google Drive, und zwar UNVERSCHLÜSSELT.
# Das widerspricht der Hausregel aus DOCS/VERSCHLUESSELUNG.md:
# „lokal unverschlüsselt, Cloud verschlüsselt".
#
# Dieses Skript stellt den verschlüsselten Weg wieder her — auf dem Anker,
# mit dem dort bereits vorhandenen Schlüssel (/root/.frawo-crypt-pw + -salt).
#
# Bewusste Entscheidungen:
#  • Es wird KEIN zweiter Datenbankabzug erzeugt. CT140 schreibt bereits
#    täglich um 03:30 nach /var/backups/odoo. Diesen Abzug holen wir ab.
#    Zweimal dumpen hiesse doppelte Last auf der Datenbank ohne Gegenwert.
#  • Geprüft wird das ERGEBNIS, nicht der Ablauf: Alter, Grösse, und ob die
#    Datei nach dem Hochladen in der Cloud wirklich mit gleicher Grösse liegt.
#    Ein Rückgabewert 0 beweist nichts — das war die Lehre vom 27.07.2026.
#  • Metriken heissen exakt wie die des Vorgängers, damit die bestehenden
#    Alarmregeln (deployments/monitoring/rules/frawo_odoo_backup.yml) und das
#    Dashboard ohne Änderung weiterfunktionieren.

set -uo pipefail
export PATH="/usr/sbin:/usr/bin:/sbin:/bin"

CTID=140
QUELLE_IM_CT="/var/backups/odoo"
ZIEL="gcrypt:Odoo"
ARBEIT="/anker-backup/odoo-cloud-tmp"
METRIK_DIR="/var/lib/node_exporter/textfile_collector"
METRIK="${METRIK_DIR}/odoo_backup.prom"
LOG="/var/log/frawo-odoo-cloud.log"
BEHALTEN=7
MINDESTGROESSE=20000000     # 20 MB — darunter ist der Abzug kaputt
MAXALTER_STUNDEN=26

ERFOLG=0
GROESSE=0
OFFSITE=0

melde() {
    echo "$(date '+%Y-%m-%d %H:%M:%S')  $*" | tee -a "$LOG"
}

# Metriken werden IMMER geschrieben, auch im Fehlerfall — sonst schlägt
# statt „Backup kaputt" nur „Metrik fehlt" an und man sucht am falschen Ende.
schreibe_metriken() {
    mkdir -p "$METRIK_DIR"
    local tmp="${METRIK}.$$"
    {
        echo "# HELP frawo_odoo_backup_last_success_timestamp_seconds Zeitpunkt der letzten erfolgreichen verschluesselten Cloud-Kopie"
        echo "# TYPE frawo_odoo_backup_last_success_timestamp_seconds gauge"
        if [ "$ERFOLG" = "1" ]; then
            echo "frawo_odoo_backup_last_success_timestamp_seconds $(date +%s)"
        elif [ -f "$METRIK" ]; then
            # Bei Fehlschlag den alten Zeitstempel erhalten, damit die Regel
            # „seit 26 h kein Erfolg" korrekt altert statt zurueckzuspringen.
            grep '^frawo_odoo_backup_last_success_timestamp_seconds ' "$METRIK" || echo "frawo_odoo_backup_last_success_timestamp_seconds 0"
        else
            echo "frawo_odoo_backup_last_success_timestamp_seconds 0"
        fi
        echo "# HELP frawo_odoo_backup_size_bytes Groesse des zuletzt uebertragenen Datenbankabzugs"
        echo "# TYPE frawo_odoo_backup_size_bytes gauge"
        echo "frawo_odoo_backup_size_bytes ${GROESSE}"
        echo "# HELP frawo_odoo_backup_offsite_ok Kopie liegt verschluesselt in der Cloud und hat die erwartete Groesse"
        echo "# TYPE frawo_odoo_backup_offsite_ok gauge"
        echo "frawo_odoo_backup_offsite_ok ${OFFSITE}"
    } > "$tmp"
    mv "$tmp" "$METRIK"      # atomar, damit der node_exporter nie eine halbe Datei liest
}

abbruch() {
    melde "FEHLGESCHLAGEN: $*"
    schreibe_metriken
    rm -rf "$ARBEIT"
    exit 1
}

melde "=== Start ==="

command -v rclone >/dev/null || abbruch "rclone nicht gefunden"
rclone listremotes 2>/dev/null | grep -q '^gcrypt:$' \
    || abbruch "rclone-Ziel gcrypt: fehlt — siehe DOCS/VERSCHLUESSELUNG.md"

# --- 1. Neuesten Abzug im Container finden ---------------------------------
DATEI=$(pct exec "$CTID" -- sh -c "ls -t ${QUELLE_IM_CT}/*.sql.gz 2>/dev/null | head -1")
[ -n "$DATEI" ] || abbruch "kein Datenbankabzug in CT${CTID}:${QUELLE_IM_CT}"
NAME=$(basename "$DATEI")

# --- 2. Alter und Grösse prüfen, BEVOR etwas hochgeladen wird --------------
MTIME=$(pct exec "$CTID" -- stat -c %Y "$DATEI" 2>/dev/null)
[ -n "$MTIME" ] || abbruch "Zeitstempel von $NAME nicht lesbar"
ALTER=$(( ( $(date +%s) - MTIME ) / 3600 ))
GROESSE=$(pct exec "$CTID" -- stat -c %s "$DATEI" 2>/dev/null)
[ -n "$GROESSE" ] || GROESSE=0

[ "$ALTER" -le "$MAXALTER_STUNDEN" ] \
    || abbruch "$NAME ist $ALTER Stunden alt — der Abzug in CT${CTID} laeuft nicht mehr"
[ "$GROESSE" -ge "$MINDESTGROESSE" ] \
    || abbruch "$NAME hat nur $((GROESSE/1024/1024)) MB — zu klein, vermutlich Teilabbruch"

melde "Abzug gefunden: $NAME, $((GROESSE/1024/1024)) MB, $ALTER h alt"

# --- 3. Aus dem Container holen --------------------------------------------
mkdir -p "$ARBEIT"
pct pull "$CTID" "$DATEI" "${ARBEIT}/${NAME}" 2>/dev/null \
    || abbruch "pct pull von $NAME fehlgeschlagen"
LOKAL=$(stat -c %s "${ARBEIT}/${NAME}" 2>/dev/null || echo 0)
[ "$LOKAL" = "$GROESSE" ] \
    || abbruch "Grösse nach dem Herausholen weicht ab ($LOKAL statt $GROESSE)"

# --- 4. Verschlüsselt hochladen --------------------------------------------
rclone copyto "${ARBEIT}/${NAME}" "${ZIEL}/${NAME}" --drive-chunk-size 64M 2>>"$LOG" \
    || abbruch "Hochladen nach ${ZIEL} fehlgeschlagen"

# --- 5. Am ZIEL gegenprüfen — das ist der eigentliche Test ------------------
# Die Datei muss in der Cloud liegen UND entschluesselbar sein. Kaeme der
# Schluessel abhanden, gaebe rclone hier keine Groesse zurueck.
CLOUD=$(rclone lsl "${ZIEL}/${NAME}" 2>/dev/null | awk '{print $1}')
if [ "$CLOUD" = "$GROESSE" ]; then
    OFFSITE=1
    ERFOLG=1
    melde "In der Cloud bestaetigt: ${NAME}, $((CLOUD/1024/1024)) MB"
else
    abbruch "Kopie in der Cloud fehlt oder hat abweichende Groesse (${CLOUD:-keine} statt $GROESSE)"
fi

# --- 6. Alte Kopien aufräumen ----------------------------------------------
# Absichtlich NACH der Bestaetigung: erst wenn die neue Kopie nachweislich
# liegt, wird eine alte weggeworfen.
ALTE=$(rclone lsf "${ZIEL}" 2>/dev/null | grep '\.sql\.gz$' | sort | head -n -"${BEHALTEN}")
for f in $ALTE; do
    rclone deletefile "${ZIEL}/${f}" 2>>"$LOG" && melde "alte Kopie entfernt: $f"
done

rm -rf "$ARBEIT"
schreibe_metriken
melde "=== Fertig, erfolgreich ==="
exit 0
