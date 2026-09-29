#!/usr/bin/env bash
# FraWo Backup-TÜV (ProDesk) — prüft täglich die auf diesem Knoten
# verantworteten Sicherungen. Odoo läuft seit September 2026 auf dem Anker;
# dessen lokale, Offsite- und Cloud-Sicherungen werden ausschließlich dort
# geprüft, damit eine migrierte Altinstanz hier keine Fehlalarme erzeugt.
#
# Warum es das gibt (27./28.07.2026):
# An einem einzigen Tag kamen drei kaputte Sicherungen ans Licht, die alle
# jahrelang „Erfolg" gemeldet hatten:
#   • Odoo-Backup     — schrieb wochenlang 0-Byte-Dateien (pct fehlte im PATH)
#   • Radio-Backup    — schrieb nie eine Datei, meldete "BACKUP COMPLETE"
#   • frawo-db-backup — legte 12 Nächte lang leere Ordner an, systemd sagte OK
# Dazu eine Musikbibliothek von 478 GB ganz ohne Sicherung.
#
# Gemeinsame Ursache: Überwacht wurde, OB ETWAS LÄUFT — nicht, OB ETWAS
# HERAUSKOMMT. Ein Exit-Code 0 beweist nichts.
#
# Dieses Skript stellt deshalb an jede Sicherung vier Fragen:
#   1. Gibt es überhaupt eine Datei?
#   2. Ist sie grösser als null und plausibel gross?
#   3. Ist sie jung genug?
#   4. Lässt sie sich LESEN? (formatabhängig, das ist der eigentliche Test)
#
# Ergebnis geht als Prometheus-Metrik raus und als Klartext-Bericht.
# Rückgabewert 1, sobald eine Prüfung durchfällt.

set -uo pipefail
export PATH="/usr/sbin:/usr/bin:/sbin:/bin"

BERICHT=/var/log/frawo-backup-tuev.log
TEXTFILE_DIR=/var/lib/node_exporter/textfile_collector
METRIK="$TEXTFILE_DIR/backup_tuev.prom"
ANKER=10.1.0.92

# Cron und manuelle Aufrufe dürfen nicht parallel laufen. Der Lock verhindert
# überlappende Netzwerk-/Cloudprüfungen, ohne einen bestehenden Lauf abzuräumen.
exec 9>/run/lock/frawo-backup-tuev.lock
if ! flock -n 9; then
    echo "FraWo Backup-TÜV läuft bereits; zweiter Aufruf wird übersprungen." >&2
    exit 75
fi

GEPRUEFT=0
DURCHGEFALLEN=0
ZEILEN=""

melde() {
    echo "$1" | tee -a "$BERICHT"
}

# metrik NAME WERT — sammelt Prometheus-Zeilen ein
metrik() {
    ZEILEN="${ZEILEN}frawo_backup_tuev{pruefung=\"$1\"} $2"$'\n'
}

# pruefe NAME ERGEBNIS BESCHREIBUNG
pruefe() {
    local name="$1" ok="$2" text="$3"
    GEPRUEFT=$((GEPRUEFT + 1))
    if [ "$ok" = "1" ]; then
        melde "  BESTANDEN  $name — $text"
        metrik "$name" 1
    else
        melde "  DURCHGEFALLEN  $name — $text"
        metrik "$name" 0
        DURCHGEFALLEN=$((DURCHGEFALLEN + 1))
    fi
}

# --- Hilfsfunktion: neueste Datei eines Musters -----------------------------
neueste() {
    ls -t $1 2>/dev/null | head -1
}

alter_stunden() {
    local f="$1"
    [ -f "$f" ] || { echo 99999; return; }
    echo $(( ( $(date +%s) - $(stat -c %Y "$f") ) / 3600 ))
}

: > "$BERICHT"
melde "=== FraWo Backup-TÜV  $(date '+%Y-%m-%d %H:%M') ==="
melde ""

# --- 1. Radio (AzuraCast) ---------------------------------------------------
F=$(neueste "/mnt/data_family/backups/azuracast/azuracast-*.tar.gz")
if [ -z "$F" ]; then
    pruefe "radio_backup" 0 "keine Datei vorhanden"
else
    SZ=$(stat -c%s "$F"); ALT=$(alter_stunden "$F")
    if [ "$SZ" -lt 5000000 ]; then
        pruefe "radio_backup" 0 "nur $((SZ/1024/1024)) MB — zu klein"
    elif [ "$ALT" -gt 26 ]; then
        pruefe "radio_backup" 0 "$ALT Stunden alt"
    elif ! tar tzf "$F" 2>/dev/null | grep -q 'db\.sql'; then
        pruefe "radio_backup" 0 "Archiv enthält keinen Datenbank-Abzug"
    else
        pruefe "radio_backup" 1 "$((SZ/1024/1024)) MB, $ALT h alt, db.sql enthalten"
    fi
fi

# --- 2. Radio-Offsite-Kopie auf dem Anker -----------------------------------
for paar in "radio_offsite:/var/backups/azuracast-offsite/*.tar.gz"; do
    NAME="${paar%%:*}"; MUSTER="${paar#*:}"
    AUSGABE=$(timeout 30 ssh -o BatchMode=yes -o ConnectTimeout=15 "root@$ANKER" \
              "ls -t $MUSTER 2>/dev/null | head -1" 2>/dev/null)
    if [ -z "$AUSGABE" ]; then
        pruefe "$NAME" 0 "keine Kopie auf dem Anker gefunden"
    else
        FALT=$(timeout 30 ssh -o BatchMode=yes -o ConnectTimeout=15 "root@$ANKER" \
               "echo \$(( ( \$(date +%s) - \$(stat -c %Y '$AUSGABE') ) / 3600 ))" 2>/dev/null)
        if [ -z "$FALT" ] || [ "$FALT" -gt 26 ]; then
            pruefe "$NAME" 0 "Kopie ${FALT:-?} Stunden alt"
        else
            pruefe "$NAME" 1 "vorhanden, $FALT h alt"
        fi
    fi
done

# --- 3. VM-Sicherungen lokal (vzdump) --------------------------------------
# Seit 29.09.2026 (#1588): Auftrag "prodesk-lokal-woche" sichert 360 + 220 sonntags
# 03:00 nach hdd-backup. Die taegliche Abdeckung liefert pbs_datastore (Anker-TUeV).
# Grenze 8 Tage = eine Woche plus ein Tag Puffer.
for VMID in 360 220; do
    F=$(neueste "/mnt/data_family/proxmox_backups/dump/vzdump-qemu-${VMID}-*.vma.zst")
    if [ -z "$F" ]; then
        pruefe "vm${VMID}_lokal" 0 "keine Sicherung vorhanden"
    else
        SZ=$(stat -c%s "$F"); ALT=$(alter_stunden "$F")
        if [ "$ALT" -gt 192 ]; then
            pruefe "vm${VMID}_lokal" 0 "$ALT Stunden alt (Grenze 192)"
        elif [ "$SZ" -lt 100000000 ]; then
            pruefe "vm${VMID}_lokal" 0 "nur $((SZ/1024/1024)) MB - zu klein"
        else
            pruefe "vm${VMID}_lokal" 1 "$((SZ/1024/1024/1024)) GB, $ALT h alt"
        fi
    fi
done

# --- 4. VM-Sicherung in der Cloud ------------------------------------------
# Vorher nur "Datei vorhanden" - bestand deshalb 10 Tage mit einer Kopie vom 19.09.
# Jetzt: juengste Datei je VM, Alter aus dem Zeitstempel in rclone lsl.
LISTE=$(timeout 120 rclone lsl gdrive:FraWo-ProDesk-VMs 2>/dev/null)
for VMID in 360 220; do
    Z=$(printf '%s\n' "$LISTE" | grep "vzdump-qemu-${VMID}-" | sort -k2,3 | tail -1)
    if [ -z "$Z" ]; then
        pruefe "vm${VMID}_cloud" 0 "keine Sicherung in der Cloud"
        continue
    fi
    TS=$(date -d "$(echo "$Z" | awk '{print $2" "substr($3,1,8)}')" +%s 2>/dev/null || echo 0)
    ALT=$(( ( $(date +%s) - TS ) / 3600 ))
    SZ=$(echo "$Z" | awk '{print $1}')
    if [ "$TS" -eq 0 ] || [ "$ALT" -gt 192 ]; then
        pruefe "vm${VMID}_cloud" 0 "juengste Cloud-Kopie $ALT Stunden alt (Grenze 192)"
    elif [ "$SZ" -lt 100000000 ]; then
        pruefe "vm${VMID}_cloud" 0 "nur $((SZ/1024/1024)) MB - zu klein"
    else
        pruefe "vm${VMID}_cloud" 1 "$((SZ/1024/1024/1024)) GB, $ALT h alt"
    fi
done

# --- Ergebnis ---------------------------------------------------------------
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

[ "$DURCHGEFALLEN" -eq 0 ] || exit 1
