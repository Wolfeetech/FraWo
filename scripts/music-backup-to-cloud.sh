#!/usr/bin/env bash
# Sichert die Musikbibliothek nach Google Drive — gedrosselt, damit die
# Leitung tagsüber frei bleibt.
#
# Anlass (27./28.07.2026): Die Musikbibliothek hat keine Sicherung.
#   - /mnt/music_hdd (478 GB) hängt als Bind-Mount mp0 in CT120. Proxmox
#     sichert Bind-Mounts standardmässig NICHT mit — die PBS-Sicherung von
#     CT120 ist nur 6,2 GB gross, also nur das Betriebssystem.
#   - In Google Drive lagen bisher nur 9,2 GB (534 Dateien, Stand Juni).
#   - Dazu kamen 85 GB, die ausschliesslich auf einer nicht eingebundenen
#     USB-Platte lagen (2102 von 2104 Titeln gab es nirgends sonst).
#
# Laufzeit: Bei rund 2 MB/s Upload dauert der Erstlauf für 478 GB etwa drei
# Tage reine Übertragungszeit. Deshalb gedrosselt und über mehrere Nächte:
# tagsüber 512 KB/s (bleibt unbemerkt), nachts volle Geschwindigkeit.
# rclone überspringt bereits Hochgeladenes, der Lauf setzt also einfach fort.
#
# WICHTIG: --drive-chunk-size 64M nicht entfernen — ohne diesen Wert ist der
# Upload achtmal langsamer (gemessen: 0,25 statt 2,04 MB/s).
#
# Bewusst `copy` statt `sync`: löscht niemals etwas am Ziel.

set -euo pipefail
export PATH="/usr/sbin:/usr/bin:/sbin:/bin"

LOCK=/var/run/music-backup-to-cloud.lock
LOG_PREFIX="[$(date '+%Y-%m-%d %H:%M')]"

# Nicht zweimal gleichzeitig starten — der Lauf dauert Stunden bis Tage.
exec 9>"$LOCK"
if ! flock -n 9; then
    echo "$LOG_PREFIX Läuft bereits, dieser Aufruf wird übersprungen."
    exit 0
fi

RCLONE_OPTS=(
    --drive-chunk-size 64M
    --drive-upload-cutoff 64M
    --transfers 2
    --checkers 8
    --retries 3
    --low-level-retries 10
    --bwlimit "07:00,512k 23:00,off"
    --exclude ".Trash*/**"
    --exclude "System Volume Information/**"
    --exclude "**/.DS_Store"
    --stats 30m
    --stats-one-line
)

sync_dir() {
    local src="$1" dest="$2" label="$3"
    if [ ! -d "$src" ]; then
        echo "$LOG_PREFIX $label: Quelle $src fehlt — übersprungen"
        return 0
    fi
    echo "$LOG_PREFIX $label: gleiche $src ab"
    rclone copy "$src" "$dest" "${RCLONE_OPTS[@]}"
    echo "$LOG_PREFIX $label: fertig"
}

# Zuerst die geretteten Einzelstücke — die gab es nur einmal.
sync_dir /mnt/music_hdd/_RETTUNG_yourparty_radio_20260727 \
         gdrive:FraWo_Musik/yourparty_radio "Gerettete Radio-Library"

# Danach die grosse Bibliothek.
sync_dir /mnt/music_hdd \
         gdrive:FraWo_Musik/music_hdd "Hauptbibliothek"

# --- Zustand ans Monitoring melden ---------------------------------------
TEXTFILE_DIR=/var/lib/node_exporter/textfile_collector
if [ -d "$TEXTFILE_DIR" ]; then
    METRIC="$TEXTFILE_DIR/music_cloud_backup.prom"
    REMOTE_BYTES=$(rclone size gdrive:FraWo_Musik --json 2>/dev/null \
                   | grep -o '"bytes":[0-9]*' | cut -d: -f2 || echo 0)
    cat > "$METRIC.tmp" <<METRICS
# HELP frawo_music_cloud_backup_last_success_timestamp_seconds Zeitpunkt des letzten vollstaendigen Musik-Abgleichs.
# TYPE frawo_music_cloud_backup_last_success_timestamp_seconds gauge
frawo_music_cloud_backup_last_success_timestamp_seconds $(date +%s)
# HELP frawo_music_cloud_backup_bytes Aktuell in der Cloud liegende Musikmenge.
# TYPE frawo_music_cloud_backup_bytes gauge
frawo_music_cloud_backup_bytes ${REMOTE_BYTES:-0}
METRICS
    mv "$METRIC.tmp" "$METRIC"
fi

echo "$LOG_PREFIX Musik-Abgleich abgeschlossen"
