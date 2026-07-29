#!/bin/bash
# Sicherung der PBS-Konfiguration — angelegt 29.07.2026
#
# Warum es das gibt:
# Proxmox meldet ueber "pve_not_backed_up", dass VM 240 (PBS-FraWo auf dem
# Anker) in keinem Sicherungsplan steht. Das ist erst einmal richtig so — ein
# Sicherungsserver sichert sich nicht sinnvoll in sich selbst.
#
# Die Luecke liegt woanders: In /etc/proxmox-backup stehen die Datastores,
# Benutzer, Rechte, Sync- und Prune-Auftraege und die Zertifikate. Geht die
# VM verloren, sind die eigentlichen Sicherungsdaten zwar noch auf der Platte,
# aber niemand weiss mehr, wie der Server sie verwaltet hat. Der Wiederaufbau
# waere Rateraten. Die Datei ist 56 KB gross — es gibt keinen Grund, sie nicht
# zu sichern.
#
# Ablauf: Der ProDesk holt sich das Verzeichnis per SSH als Archiv, prueft es
# und legt zusaetzlich eine verschluesselte Kopie in der Cloud ab.

set -euo pipefail
export PATH="/usr/sbin:/usr/bin:/sbin:/bin"

PBS_HOST=10.1.0.7
DIR=/mnt/data_family/pbs-config
CLOUD_ZIEL=gcrypt:PBS-Konfiguration
AUFBEWAHRUNG_TAGE=30
MIN_BYTES=5000
TS=$(date +%Y%m%d-%H%M)
OUT="$DIR/pbs-config-${TS}.tar.gz"
TMP="$OUT.part"
METRIC=/var/lib/node_exporter/textfile_collector/pbs_config_backup.prom

mkdir -p "$DIR"

# Erst in eine .part-Datei schreiben. Sonst liegt bei einem Abbruch eine
# halbe Datei mit richtigem Namen da und sieht aus wie eine gute Sicherung —
# genau der Fehler, der die Odoo-Sicherung wochenlang wertlos gemacht hat.
ssh -o ConnectTimeout=15 -o BatchMode=yes "root@$PBS_HOST" \
    "tar czf - -C /etc proxmox-backup" > "$TMP"

GROESSE=$(stat -c%s "$TMP")
if [ "$GROESSE" -lt "$MIN_BYTES" ]; then
    echo "FEHLER: Archiv nur $GROESSE Bytes, erwartet mindestens $MIN_BYTES" >&2
    rm -f "$TMP"
    exit 1
fi

# Die entscheidende Frage ist nicht, ob eine Datei da ist, sondern ob man sie
# lesen kann und ob das Wesentliche drinsteckt.
if ! tar tzf "$TMP" >/dev/null 2>&1; then
    echo "FEHLER: Archiv ist nicht lesbar" >&2
    rm -f "$TMP"
    exit 1
fi
if ! tar tzf "$TMP" 2>/dev/null | grep -q 'proxmox-backup/datastore.cfg'; then
    echo "FEHLER: datastore.cfg fehlt im Archiv" >&2
    rm -f "$TMP"
    exit 1
fi

mv "$TMP" "$OUT"

# Verschluesselte Kopie ausser Haus. 56 KB — das kostet nichts und ist im
# Ernstfall der Unterschied zwischen Wiederaufbau und Raten.
CLOUD_OK=nein
CLOUD_VAL=0
if rclone copy "$OUT" "$CLOUD_ZIEL/" --quiet 2>/dev/null; then
    FERN=$(rclone size "$CLOUD_ZIEL/$(basename "$OUT")" --json 2>/dev/null \
           | grep -oE '"bytes":[0-9]+' | cut -d: -f2)
    if [ "${FERN:-0}" = "$(stat -c%s "$OUT")" ]; then
        CLOUD_OK=ja
        CLOUD_VAL=1
    fi
fi

find "$DIR" -name 'pbs-config-*.tar.gz' -mtime "+$AUFBEWAHRUNG_TAGE" -delete 2>/dev/null || true
rclone delete "$CLOUD_ZIEL/" --min-age "${AUFBEWAHRUNG_TAGE}d" --quiet 2>/dev/null || true

if [ -d "$(dirname "$METRIC")" ]; then
    cat > "$METRIC.tmp" <<METRICS
# HELP frawo_pbs_config_backup_last_success_timestamp_seconds Zeitpunkt der letzten erfolgreichen PBS-Konfigurationssicherung.
# TYPE frawo_pbs_config_backup_last_success_timestamp_seconds gauge
frawo_pbs_config_backup_last_success_timestamp_seconds $(date +%s)
# HELP frawo_pbs_config_backup_size_bytes Groesse des letzten Konfigurationsarchivs.
# TYPE frawo_pbs_config_backup_size_bytes gauge
frawo_pbs_config_backup_size_bytes $(stat -c%s "$OUT")
# HELP frawo_pbs_config_backup_cloud_ok Verschluesselte Kopie in der Cloud vorhanden und groessengleich.
# TYPE frawo_pbs_config_backup_cloud_ok gauge
frawo_pbs_config_backup_cloud_ok $CLOUD_VAL
METRICS
    mv "$METRIC.tmp" "$METRIC"
fi

echo "OK $(date '+%Y-%m-%d %H:%M') Groesse=$(du -h "$OUT" | cut -f1) Cloud=$CLOUD_OK"
