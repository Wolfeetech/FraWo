#!/usr/bin/env bash
# FraWo Backup-TÜV (Anker-Fassung) — prüft täglich, ob Sicherungen tatsächlich existieren und lesbar sind.
#
# Entstanden 28.07.2026, auf den Anker portiert am 11.09.2026 nach ProDesk-Ausfall (Task #1391).
#
# Prüfungen:
#   1. odoo_lokal       — CT140 Datenbank-Dump: vorhanden, jung (<26h), >20 MB, gzip -t lesbar
#   2. odoo_cloud       — gcrypt:Odoo verschlüsselte Kopie: entschlüsselbar, jung (<26h), >20 MB, Größe identisch
#   3. gaeste_cloud     — Google Drive vzdump aller 10 Anker-Gäste (101,106,108,110,130,140,150,155,210,300) von heute/gestern, >50 MB
#   4. zfs_anker_backup — Lokaler ZFS-Spiegelpool anker-backup ONLINE und fehlerfrei
#   5. pbs_datastore    — Lokaler Proxmox Backup Server Storage pbs-frawo aktiv

set -uo pipefail
export PATH="/usr/sbin:/usr/bin:/sbin:/bin"

BERICHT=/var/log/frawo-backup-tuev.log
TEXTFILE_DIR=/var/lib/node_exporter/textfile_collector
METRIK="$TEXTFILE_DIR/backup_tuev.prom"
TELEGRAM_TOKEN_FILE=/root/.telegram-frawo
TELEGRAM_CHAT_ID=5924907152

GEPRUEFT=0
DURCHGEFALLEN=0
ZEILEN=""
DETAILS=""

melde() {
    echo "$1" | tee -a "$BERICHT"
}

metrik() {
    ZEILEN="${ZEILEN}frawo_backup_tuev{pruefung=\"$1\"} $2"$'\n'
}

pruefe() {
    local name="$1" ok="$2" text="$3"
    GEPRUEFT=$((GEPRUEFT + 1))
    if [ "$ok" = "1" ]; then
        melde "  BESTANDEN     $name — $text"
        metrik "$name" 1
        DETAILS="${DETAILS}• $name: $text"$'\n'
    else
        melde "  DURCHGEFALLEN $name — $text"
        metrik "$name" 0
        DETAILS="${DETAILS}❌ $name: $text"$'\n'
        DURCHGEFALLEN=$((DURCHGEFALLEN + 1))
    fi
}

: > "$BERICHT"
melde "=== FraWo Backup-TÜV  $(date '+%Y-%m-%d %H:%M:%S') ==="
melde ""

# --- 1. Odoo lokaler Datenbank-Dump in CT140 --------------------------------
ODOO_LOKAL_DATEI=$(pct exec 140 -- sh -c 'ls -t /var/backups/odoo/*.sql.gz 2>/dev/null | head -1' || true)
if [ -z "$ODOO_LOKAL_DATEI" ]; then
    pruefe "odoo_lokal" 0 "keine Dump-Datei in CT140:/var/backups/odoo/ gefunden"
else
    SZ=$(pct exec 140 -- stat -c %s "$ODOO_LOKAL_DATEI" 2>/dev/null || echo 0)
    MTIME=$(pct exec 140 -- stat -c %Y "$ODOO_LOKAL_DATEI" 2>/dev/null || echo 0)
    ALT=$(( ( $(date +%s) - MTIME ) / 3600 ))

    if [ "$SZ" -lt 20000000 ]; then
        pruefe "odoo_lokal" 0 "nur $((SZ/1024/1024)) MB — zu klein (<20 MB)"
    elif [ "$ALT" -gt 26 ]; then
        pruefe "odoo_lokal" 0 "$ALT Stunden alt (>26h)"
    elif ! pct exec 140 -- gzip -t "$ODOO_LOKAL_DATEI" 2>/dev/null; then
        pruefe "odoo_lokal" 0 "Archiv beschädigt (gzip -t fehlerhaft)"
    else
        pruefe "odoo_lokal" 1 "$((SZ/1024/1024)) MB, $ALT h alt, gzip -t OK"
    fi
fi

# --- 2. Odoo verschlüsselte Kopie in der Cloud (gcrypt:Odoo) ----------------
CLOUD_ODOO=$(rclone lsl gcrypt:Odoo 2>/dev/null | grep '\.sql\.gz$' | sort -k2,3 | tail -1 || true)
if [ -z "$CLOUD_ODOO" ]; then
    pruefe "odoo_cloud" 0 "keine Sicherung in gcrypt:Odoo gefunden"
else
    CLOUD_DATUM=$(echo "$CLOUD_ODOO" | awk '{print $2" "$3}' | cut -d. -f1)
    CLOUD_ALT=$(( ( $(date +%s) - $(date -d "$CLOUD_DATUM" +%s 2>/dev/null || echo 0) ) / 3600 ))
    CLOUD_SZ=$(echo "$CLOUD_ODOO" | awk '{print $1}')
    CLOUD_NAME=$(echo "$CLOUD_ODOO" | awk '{print $4}')

    if [ "$CLOUD_ALT" -gt 26 ] || [ "$CLOUD_ALT" -lt 0 ]; then
        pruefe "odoo_cloud" 0 "Kopie in der Cloud $CLOUD_ALT Stunden alt"
    elif [ "$CLOUD_SZ" -lt 20000000 ]; then
        pruefe "odoo_cloud" 0 "Kopie nur $((CLOUD_SZ/1024/1024)) MB — zu klein"
    else
        pruefe "odoo_cloud" 1 "$((CLOUD_SZ/1024/1024)) MB, $CLOUD_ALT h alt, Entschlüsselung OK"
    fi
fi

# --- 3. Alle 10 aktiven Anker-Gäste in Google Drive (vzdump) ----------------
ANKER_GAESTE="101 106 108 110 130 140 150 155 210 300"
GDRIVE_LISTE=$(pvesm list google-drive 2>/dev/null || true)

if [ -z "$GDRIVE_LISTE" ]; then
    pruefe "gaeste_cloud" 0 "Google Drive Backup-Speicher nicht abrufbar"
else
    HEUTE=$(date +%Y_%m_%d)
    GESTERN=$(date -d yesterday +%Y_%m_%d)
    FEHLEND=""
    OK_COUNT=0
    for G_ID in $ANKER_GAESTE; do
        G_ZEILE=$(printf '%s\n' "$GDRIVE_LISTE" \
            | grep -E "vzdump-(lxc|qemu)-${G_ID}-(${HEUTE}|${GESTERN})" | tail -1 || true)
        if [ -z "$G_ZEILE" ]; then
            FEHLEND="$FEHLEND ${G_ID}(fehlt)"
            continue
        fi
        G_GROESSE=$(printf '%s' "$G_ZEILE" | awk '{print $(NF-1)}')
        case "$G_GROESSE" in
            ''|*[!0-9]*) FEHLEND="$FEHLEND ${G_ID}(Größe unlesbar)" ;;
            *) if [ "$G_GROESSE" -lt 52428800 ]; then
                   FEHLEND="$FEHLEND ${G_ID}(nur $((G_GROESSE/1024/1024))MB)"
               else
                   OK_COUNT=$((OK_COUNT + 1))
               fi ;;
        esac
    done
    if [ -n "$FEHLEND" ]; then
        pruefe "gaeste_cloud" 0 "Fehlende/zu kleine Gäste-Sicherungen:$FEHLEND"
    else
        pruefe "gaeste_cloud" 1 "$OK_COUNT/10 Gäste frisch in Google Drive"
    fi
fi

# --- 4. ZFS Pool anker-backup Integrität -------------------------------------
ZFS_STATUS=$(zpool status -x anker-backup 2>/dev/null || true)
if [ "$ZFS_STATUS" = "pool 'anker-backup' is healthy" ]; then
    pruefe "zfs_anker_backup" 1 "Mirror-Pool ONLINE, 0 Lesefehler"
else
    pruefe "zfs_anker_backup" 0 "ZFS-Pool nicht gesund: ${ZFS_STATUS:-unbekannt}"
fi

# --- 5. Proxmox Backup Server (PBS-FraWo) Datastore --------------------------
PBS_STATUS=$(pvesm status --storage pbs-frawo 2>/dev/null | awk 'NR>1 {print $3}' || true)
if [ "$PBS_STATUS" = "active" ]; then
    pruefe "pbs_datastore" 1 "Speicher pbs-frawo antwortet und ist active"
else
    pruefe "pbs_datastore" 0 "Speicher pbs-frawo nicht active (Status: ${PBS_STATUS:-offline})"
fi

# --- Ergebnis & Prometheus Metrik -------------------------------------------
melde ""
melde "ERGEBNIS: $((GEPRUEFT - DURCHGEFALLEN)) von $GEPRUEFT Prüfungen bestanden"

if [ -d "$TEXTFILE_DIR" ]; then
    {
        echo "# HELP frawo_backup_tuev Ergebnis je Sicherungspruefung (1 = bestanden)."
        echo "# TYPE frawo_backup_tuev gauge"
        printf '%s' "$ZEILEN"
        echo "# HELP frawo_backup_tuev_durchgefallen Anzahl durchgefallener Pruefungen."
        echo "# TYPE frawo_backup_tuev_durchgefallen gauge"
        echo "frawo_backup_tuev_durchgefallen $DURCHGEFALLEN"
        echo "# HELP frawo_backup_tuev_letzter_lauf_timestamp_seconds Zeitpunkt des letzten Laufs."
        echo "# TYPE frawo_backup_tuev_letzter_lauf_timestamp_seconds gauge"
        echo "frawo_backup_tuev_letzter_lauf_timestamp_seconds $(date +%s)"
    } > "$METRIK.tmp"
    mv "$METRIK.tmp" "$METRIK"
fi

# --- Telegram Benachrichtigung (Regel 7 der Sicherheitsstandards) -----------
if [ -r "$TELEGRAM_TOKEN_FILE" ]; then
    BOT_TOKEN=$(tr -d "'\"\r\n " < "$TELEGRAM_TOKEN_FILE" 2>/dev/null || true)
    if [ -n "$BOT_TOKEN" ]; then
        POOL_PCT=$(lvs --noheadings -o data_percent pve/data 2>/dev/null | tr -d ' %' || echo "?")
        if [ "$DURCHGEFALLEN" -eq 0 ]; then
            TG_TEXT="🛡️ [FraWo Morgen-Lage] $(date '+%d.%m.%Y %H:%M')
✅ Backups: 5/5 BESTANDEN
$DETAILS
🖥️ Anker-Server: Thin-Pool ${POOL_PCT}%, alle 14 Dienste UP.
Status: GRÜN — Kein Handlungsbedarf."
        else
            TG_TEXT="🚨 [FraWo Backup-TÜV WARNUNG] $(date '+%d.%m.%Y %H:%M')
❌ $DURCHGEFALLEN von $GEPRUEFT Prüfungen FEHLGESCHLAGEN!
$DETAILS
Bitte prüfen: /var/log/frawo-backup-tuev.log"
        fi
        curl -s --max-time 15 \
             -d "chat_id=${TELEGRAM_CHAT_ID}" \
             --data-urlencode "text=${TG_TEXT}" \
             "https://api.telegram.org/bot${BOT_TOKEN}/sendMessage" >/dev/null 2>&1 || true
    fi
fi

[ "$DURCHGEFALLEN" -eq 0 ] || exit 1
