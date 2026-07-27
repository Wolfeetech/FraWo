#!/usr/bin/env bash
# Lädt die VM-Sicherungen des ProDesk in die Cloud (Google Drive).
#
# Warum: Die VMs 210 (AzuraCast) und 360 (Home Assistant Eltern) wurden bisher
# nur nach /mnt/data_family/proxmox_backups gesichert — auf eine Platte im
# selben Rechner. Fällt der ProDesk aus, wären Original und Sicherung zusammen
# weg. Der PBS auf dem Anker schied als Ziel aus: dort sind nur 43 GB frei,
# VM 210 allein braucht 33 GB. Google Drive hat rund 3 TB frei.
#
# WICHTIG — die Tempo-Falle (gemessen am 27.07.2026):
#   rclone lädt mit Voreinstellungen (8-MB-Blöcke) nur mit ~0,25 MB/s zu Google
#   Drive hoch. Die Leitung schafft aber 2,4 MB/s. Mit --drive-chunk-size 64M
#   sind es 2,0 MB/s — achtmal schneller. Diese Parameter sind der Grund,
#   warum Cloud-Sicherungen hier überhaupt praktikabel sind. Nicht entfernen.
#
# Zeitbedarf damit: VM 360 (~10 GB) rund 85 Minuten, VM 210 (~33 GB) rund
# 4,5 Stunden. Deshalb: die kleine VM täglich, die grosse einmal wöchentlich.
# AzuraCast hat zusätzlich eine eigene tägliche Datenbanksicherung (42 MB) mit
# Offsite-Kopie — das VM-Abbild dient nur der kompletten Wiederherstellung.

set -euo pipefail
export PATH="/usr/sbin:/usr/bin:/sbin:/bin"

SRC=/mnt/data_family/proxmox_backups/dump
REMOTE=gdrive:FraWo-ProDesk-VMs
DAILY_VMID=360
WEEKLY_VMID=210
WEEKLY_DAY=7          # 7 = Sonntag
KEEP_REMOTE=3

# Ohne diese Werte dauert der Upload das Achtfache (siehe Kopf).
RCLONE_OPTS=(
    --drive-chunk-size 64M
    --drive-upload-cutoff 64M
    --checkers 8
    --transfers 2
    --retries 3
    --low-level-retries 10
    --stats-one-line
)

upload_newest() {
    local vmid="$1"
    local newest
    newest=$(ls -t "$SRC"/vzdump-qemu-"$vmid"-*.vma.zst 2>/dev/null | head -1 || true)

    if [ -z "$newest" ]; then
        echo "WARNUNG: keine lokale Sicherung für VM $vmid gefunden"
        return 1
    fi

    local name size
    name=$(basename "$newest")
    size=$(stat -c%s "$newest")

    # Schon oben? Dann nicht erneut hochladen.
    if rclone lsf "$REMOTE/" 2>/dev/null | grep -qx "$name"; then
        echo "VM $vmid: $name liegt bereits in der Cloud"
        return 0
    fi

    echo "VM $vmid: lade $name hoch ($((size / 1024 / 1024)) MB)"
    rclone copy "$newest" "$REMOTE/" "${RCLONE_OPTS[@]}"

    # Übertragung gegen die Quelle prüfen — eine Datei in der Cloud ist noch
    # kein Backup, solange die Grösse nicht stimmt.
    local remote_size
    remote_size=$(rclone size "$REMOTE/$name" --json 2>/dev/null | grep -o '"bytes":[0-9]*' | cut -d: -f2)
    if [ "$remote_size" != "$size" ]; then
        echo "FEHLER: VM $vmid — Grösse in der Cloud ($remote_size) weicht ab ($size)"
        return 1
    fi

    echo "VM $vmid: hochgeladen und geprüft"
    return 0
}

prune_remote() {
    local vmid="$1"
    # Nur die jüngsten KEEP_REMOTE Stände je VM behalten.
    rclone lsf "$REMOTE/" 2>/dev/null \
        | grep "^vzdump-qemu-${vmid}-" \
        | sort -r \
        | tail -n +$((KEEP_REMOTE + 1)) \
        | while read -r old; do
            echo "entferne alten Stand aus der Cloud: $old"
            rclone delete "$REMOTE/$old" 2>/dev/null || true
          done
}

OK_DAILY=0
OK_WEEKLY=0

if upload_newest "$DAILY_VMID"; then
    OK_DAILY=1
    prune_remote "$DAILY_VMID"
fi

if [ "$(date +%u)" = "$WEEKLY_DAY" ]; then
    if upload_newest "$WEEKLY_VMID"; then
        OK_WEEKLY=1
        prune_remote "$WEEKLY_VMID"
    fi
else
    echo "VM $WEEKLY_VMID: heute nicht dran (nur sonntags)"
    OK_WEEKLY=1
fi

# --- Zustand ans Monitoring melden ---------------------------------------
TEXTFILE_DIR=/var/lib/node_exporter/textfile_collector
if [ -d "$TEXTFILE_DIR" ] && [ "$OK_DAILY" = "1" ]; then
    METRIC="$TEXTFILE_DIR/vm_cloud_backup.prom"
    cat > "$METRIC.tmp" <<METRICS
# HELP frawo_vm_cloud_backup_last_success_timestamp_seconds Zeitpunkt der letzten erfolgreichen VM-Sicherung in die Cloud.
# TYPE frawo_vm_cloud_backup_last_success_timestamp_seconds gauge
frawo_vm_cloud_backup_last_success_timestamp_seconds $(date +%s)
METRICS
    mv "$METRIC.tmp" "$METRIC"
fi

if [ "$OK_DAILY" = "1" ] && [ "$OK_WEEKLY" = "1" ]; then
    echo "OK $(date '+%Y-%m-%d %H:%M') Cloud-Sicherung abgeschlossen"
else
    echo "FEHLER $(date '+%Y-%m-%d %H:%M') Cloud-Sicherung unvollständig"
    exit 1
fi
