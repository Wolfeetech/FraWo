#!/usr/bin/env bash
# Tägliche Sicherung der AzuraCast-Radiostation (VM 210) — läuft auf dem ProDesk-Host.
#
# Historie: Die Vorgängerfassung (backup-azuracast.sh, 25.11.2025) war gleich
# dreifach kaputt und hat trotzdem jede Nacht "=== BACKUP COMPLETE ===" ins Log
# geschrieben:
#   1. `qm` ohne absoluten Pfad → im Cron-PATH nicht vorhanden, Aufruf scheiterte.
#   2. Kein `set -e` → der Fehler wurde übergangen und Erfolg gemeldet.
#   3. Selbst bei funktionierendem `qm` wäre nichts Brauchbares entstanden:
#      `qm guest exec ... > datei.sql` schreibt die JSON-Hülle der Guest-Agent-
#      Antwort in die Datei, nicht das SQL. Zudem hiess der referenzierte
#      Container `azuracast_database_1`, den es in dieser Installation gar
#      nicht gibt (monolithischer `azuracast`-Container).
# Ergebnis: Es existierte kein einziges Radio-Backup.
#
# Diese Fassung nutzt das mitgelieferte offizielle Werkzeug
# (`docker.sh backup ... --exclude-media`). Mediendateien bleiben bewusst
# aussen vor — sie liegen auf dem Samba-Fileserver (CT120, //10.1.0.94/music
# und /radio) und werden dort gesichert. Gesichert wird die Datenbank samt
# Stations-, Playlist- und Nutzerkonfiguration.
#
# Laufzeit rund 15 Sekunden, der Stream läuft dabei ungestört weiter.

set -euo pipefail
export PATH="/usr/sbin:/usr/bin:/sbin:/bin"

VM_HOST=10.1.0.38
DIR=/mnt/data_family/backups/azuracast
RETENTION_DAYS=14
MIN_BYTES=5000000
REMOTE_TMP=/var/azuracast/nightly-backup.tar.gz

TS=$(date +%Y%m%d-%H%M)
OUT="$DIR/azuracast-${TS}.tar.gz"
TMP="$OUT.part"

mkdir -p "$DIR"

remote() {
    ssh -o BatchMode=yes -o ConnectTimeout=15 "root@$VM_HOST" "$@"
}

cleanup() {
    rm -f "$TMP"
    remote "rm -f '$REMOTE_TMP'" 2>/dev/null || true
}
trap cleanup EXIT

# --- 1. Backup in der VM erzeugen ----------------------------------------
remote "rm -f '$REMOTE_TMP'; cd /var/azuracast && ./docker.sh backup '$REMOTE_TMP' --exclude-media" >/dev/null

# --- 2. Auf den Host holen ------------------------------------------------
scp -q -o BatchMode=yes -o ConnectTimeout=15 "root@$VM_HOST:$REMOTE_TMP" "$TMP"

SZ=$(stat -c%s "$TMP")
if [ "$SZ" -lt "$MIN_BYTES" ]; then
    echo "FEHLER: Backup zu klein ($SZ Byte) — nicht übernommen"
    exit 1
fi

# Eine Datei mit Inhalt ist noch kein Backup: Archiv muss lesbar sein und den
# Datenbank-Abzug enthalten.
if ! tar tzf "$TMP" >/dev/null 2>&1; then
    echo "FEHLER: Archiv ist nicht lesbar — nicht übernommen"
    exit 1
fi
if ! tar tzf "$TMP" 2>/dev/null | grep -q 'db\.sql'; then
    echo "FEHLER: Archiv enthält keinen Datenbank-Abzug (db.sql) — nicht übernommen"
    exit 1
fi

mv "$TMP" "$OUT"

# --- 3. Offsite-Kopie auf den Anker-Knoten --------------------------------
OFFSITE_HOST=10.1.0.92
OFFSITE_DIR=/var/backups/azuracast-offsite
OFFSITE_OK=nein

offsite_ssh() {
    ssh -o BatchMode=yes -o ConnectTimeout=15 "root@$OFFSITE_HOST" "$@"
}

if offsite_ssh "mkdir -p '$OFFSITE_DIR'" 2>/dev/null \
   && scp -q -o BatchMode=yes -o ConnectTimeout=15 "$OUT" "root@$OFFSITE_HOST:$OFFSITE_DIR/" 2>/dev/null; then
    LOCAL_SUM=$(md5sum "$OUT" | cut -d' ' -f1)
    REMOTE_SUM=$(offsite_ssh "md5sum '$OFFSITE_DIR/$(basename "$OUT")'" 2>/dev/null | cut -d' ' -f1)
    if [ -n "$REMOTE_SUM" ] && [ "$LOCAL_SUM" = "$REMOTE_SUM" ]; then
        OFFSITE_OK=ja
        offsite_ssh "find '$OFFSITE_DIR' -name 'azuracast-*.tar.gz' -mtime +$RETENTION_DAYS -delete" 2>/dev/null || true
    else
        echo "WARNUNG: Offsite-Prüfsumme weicht ab"
    fi
else
    echo "WARNUNG: Offsite-Kopie nach $OFFSITE_HOST fehlgeschlagen"
fi

# --- 4. Aufräumen ---------------------------------------------------------
find "$DIR" -name 'azuracast-*.tar.gz' -mtime "+$RETENTION_DAYS" -delete

# --- 5. Zustand ans Monitoring melden -------------------------------------
TEXTFILE_DIR=/var/lib/node_exporter/textfile_collector
if [ -d "$TEXTFILE_DIR" ]; then
    METRIC="$TEXTFILE_DIR/azuracast_backup.prom"
    OFFSITE_VAL=0
    [ "$OFFSITE_OK" = "ja" ] && OFFSITE_VAL=1
    cat > "$METRIC.tmp" <<METRICS
# HELP frawo_azuracast_backup_last_success_timestamp_seconds Zeitpunkt der letzten erfolgreichen Radio-Sicherung.
# TYPE frawo_azuracast_backup_last_success_timestamp_seconds gauge
frawo_azuracast_backup_last_success_timestamp_seconds $(date +%s)
# HELP frawo_azuracast_backup_size_bytes Groesse der letzten Radio-Sicherung.
# TYPE frawo_azuracast_backup_size_bytes gauge
frawo_azuracast_backup_size_bytes $(stat -c%s "$OUT")
# HELP frawo_azuracast_backup_offsite_ok Offsite-Kopie erfolgreich und pruefsummengleich.
# TYPE frawo_azuracast_backup_offsite_ok gauge
frawo_azuracast_backup_offsite_ok $OFFSITE_VAL
METRICS
    mv "$METRIC.tmp" "$METRIC"
fi

echo "OK $(date '+%Y-%m-%d %H:%M') Radio=$(du -h "$OUT" | cut -f1) Offsite=$OFFSITE_OK"
