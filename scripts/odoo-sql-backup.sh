#!/usr/bin/env bash
# Täglicher Odoo-Backup (DB-Dump + Filestore) — läuft auf dem ProDesk-Host.
#
# Historie: Die Fassung vom 10.07.2026 rief `pct` ohne Pfad auf. Cron hat
# /usr/sbin nicht im PATH, deshalb brach das Skript bei `set -e` sofort ab —
# nachdem die Shell die Zieldatei per Umleitung bereits angelegt hatte.
# Ergebnis: jede Nacht eine 0-Byte-Datei, die Grössenprüfung wurde nie
# erreicht, und es gab wochenlang kein brauchbares Backup. Behoben am
# 27.07.2026: absoluter Pfad, PATH gesetzt, Schreiben in temporäre Datei,
# und der Filestore wird mitgesichert (Anhänge liegen nicht in der DB).

set -euo pipefail
export PATH="/usr/sbin:/usr/bin:/sbin:/bin"

DIR=/mnt/data_family/odoo-sql-dumps
CTID=140
DB=FraWo_GbR
RETENTION_DAYS=14
MIN_BYTES=1000000

mkdir -p "$DIR"
TS=$(date +%Y%m%d-%H%M)
OUT="$DIR/${DB}-${TS}.dump"
TMP="$OUT.part"
STORE="$DIR/${DB}-${TS}-filestore.tar.gz"
STORE_TMP="$STORE.part"

cleanup() {
    rm -f "$TMP" "$STORE_TMP"
}
trap cleanup EXIT

# --- 1. Datenbank ---------------------------------------------------------
pct exec "$CTID" -- docker exec frawotech-db-1 pg_dump -U odoo -Fc -d "$DB" > "$TMP"

SZ=$(stat -c%s "$TMP")
if [ "$SZ" -lt "$MIN_BYTES" ]; then
    echo "FEHLER: DB-Dump zu klein ($SZ Byte) — nicht übernommen"
    exit 1
fi
mv "$TMP" "$OUT"

# --- 2. Filestore (Anhänge, Bilder) --------------------------------------
pct exec "$CTID" -- tar czf - -C /var/lib/docker/volumes/frawotech_odoo-data/_data . > "$STORE_TMP"

STORE_SZ=$(stat -c%s "$STORE_TMP")
if [ "$STORE_SZ" -lt 1000 ]; then
    echo "FEHLER: Filestore-Archiv zu klein ($STORE_SZ Byte) — nicht übernommen"
    exit 1
fi
mv "$STORE_TMP" "$STORE"

# --- 3. Offsite-Kopie auf den Anker-Knoten --------------------------------
# Ohne diesen Schritt liegen Datenbank und Sicherung auf derselben Maschine —
# ein Plattenschaden am ProDesk nähme beides mit.
OFFSITE_HOST=10.1.0.92
OFFSITE_DIR=/var/backups/odoo-offsite
OFFSITE_OK=nein

offsite_ssh() {
    ssh -o BatchMode=yes -o ConnectTimeout=15 "root@$OFFSITE_HOST" "$@"
}

if offsite_ssh "mkdir -p '$OFFSITE_DIR'" 2>/dev/null; then
    if scp -q -o BatchMode=yes -o ConnectTimeout=15 "$OUT" "$STORE" \
            "root@$OFFSITE_HOST:$OFFSITE_DIR/" 2>/dev/null; then
        # Übertragung gegen die Quelle prüfen — eine vorhandene Datei ist
        # noch kein gültiges Backup (Lehre aus den 0-Byte-Dumps).
        LOCAL_SUM=$(md5sum "$OUT" | cut -d' ' -f1)
        REMOTE_SUM=$(offsite_ssh "md5sum '$OFFSITE_DIR/$(basename "$OUT")'" 2>/dev/null | cut -d' ' -f1)
        if [ -n "$REMOTE_SUM" ] && [ "$LOCAL_SUM" = "$REMOTE_SUM" ]; then
            OFFSITE_OK=ja
            offsite_ssh "find '$OFFSITE_DIR' -name '${DB}-*' -mtime +$RETENTION_DAYS -delete" 2>/dev/null || true
        else
            echo "WARNUNG: Offsite-Prüfsumme weicht ab — Kopie auf $OFFSITE_HOST unbrauchbar"
        fi
    else
        echo "WARNUNG: Offsite-Übertragung auf $OFFSITE_HOST fehlgeschlagen"
    fi
else
    echo "WARNUNG: Anker-Knoten $OFFSITE_HOST nicht erreichbar — keine Offsite-Kopie"
fi

# --- 4. Aufräumen ---------------------------------------------------------
find "$DIR" -name "${DB}-*.dump" -mtime "+$RETENTION_DAYS" -delete
find "$DIR" -name "${DB}-*-filestore.tar.gz" -mtime "+$RETENTION_DAYS" -delete
# Altlasten der defekten Fassung entfernen.
find "$DIR" -name "${DB}-*.dump" -size 0 -delete

echo "OK $(date '+%Y-%m-%d %H:%M') DB=$(du -h "$OUT" | cut -f1) Filestore=$(du -h "$STORE" | cut -f1) Offsite=$OFFSITE_OK"
