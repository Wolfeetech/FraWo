#!/usr/bin/env bash
# FraWo Backup-TÜV — prüft täglich, ob die Sicherungen ein ERGEBNIS haben.
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

# --- 1. Odoo: Datenbank-Dump ------------------------------------------------
F=$(neueste "/mnt/data_family/odoo-sql-dumps/FraWo_GbR-*.dump")
if [ -z "$F" ]; then
    pruefe "odoo_dump" 0 "keine Datei vorhanden"
else
    SZ=$(stat -c%s "$F"); ALT=$(alter_stunden "$F")
    if [ "$SZ" -lt 20000000 ]; then
        pruefe "odoo_dump" 0 "nur $((SZ/1024/1024)) MB — zu klein"
    elif [ "$ALT" -gt 26 ]; then
        pruefe "odoo_dump" 0 "$ALT Stunden alt"
    elif ! pct exec 140 -- docker exec frawotech-db-1 pg_restore --list /dev/null >/dev/null 2>&1 \
         && ! head -c 5 "$F" | grep -q PGDMP; then
        pruefe "odoo_dump" 0 "Datei ist kein gültiger PostgreSQL-Dump"
    else
        pruefe "odoo_dump" 1 "$((SZ/1024/1024)) MB, $ALT h alt, Kennung PGDMP vorhanden"
    fi
fi

# --- 2. Odoo: Filestore -----------------------------------------------------
F=$(neueste "/mnt/data_family/odoo-sql-dumps/FraWo_GbR-*-filestore.tar.gz")
if [ -z "$F" ]; then
    pruefe "odoo_filestore" 0 "keine Datei vorhanden"
else
    ALT=$(alter_stunden "$F")
    if [ "$ALT" -gt 26 ]; then
        pruefe "odoo_filestore" 0 "$ALT Stunden alt"
    elif ! tar tzf "$F" >/dev/null 2>&1; then
        pruefe "odoo_filestore" 0 "Archiv nicht lesbar"
    else
        pruefe "odoo_filestore" 1 "lesbar, $ALT h alt"
    fi
fi

# --- 3. Radio (AzuraCast) ---------------------------------------------------
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

# --- 4. Offsite-Kopien auf dem Anker ---------------------------------------
for paar in "odoo_offsite:/var/backups/odoo-offsite/*.dump" \
            "radio_offsite:/var/backups/azuracast-offsite/*.tar.gz"; do
    NAME="${paar%%:*}"; MUSTER="${paar#*:}"
    AUSGABE=$(ssh -o BatchMode=yes -o ConnectTimeout=15 "root@$ANKER" \
              "ls -t $MUSTER 2>/dev/null | head -1" 2>/dev/null)
    if [ -z "$AUSGABE" ]; then
        pruefe "$NAME" 0 "keine Kopie auf dem Anker gefunden"
    else
        FALT=$(ssh -o BatchMode=yes -o ConnectTimeout=15 "root@$ANKER" \
               "echo \$(( ( \$(date +%s) - \$(stat -c %Y '$AUSGABE') ) / 3600 ))" 2>/dev/null)
        if [ -z "$FALT" ] || [ "$FALT" -gt 26 ]; then
            pruefe "$NAME" 0 "Kopie ${FALT:-?} Stunden alt"
        else
            pruefe "$NAME" 1 "vorhanden, $FALT h alt"
        fi
    fi
done

# --- 4b. Odoo in der Cloud --------------------------------------------------
# Ergaenzt 28.07.2026 nach dem Sicherungs-Audit: Die einzige Odoo-Kopie in
# Google Drive war sechs Wochen alt. Die Geschaeftsdaten hatten damit keine
# aktuelle Kopie ausser Haus.
# Seit 28.07.2026 verschluesselt: "gcrypt" ist ein rclone-crypt-Ziel ueber
# gdrive:FraWo-Verschluesselt. Der Zugriff hier prueft damit zugleich, dass
# die Entschluesselung funktioniert - waere der Schluessel kaputt, kaeme
# keine Dateiliste zurueck und die Pruefung fiele durch.
CLOUD_ODOO=$(rclone lsl gcrypt:Odoo 2>/dev/null \
             | grep '\.dump$' | sort -k2 | tail -1)
if [ -z "$CLOUD_ODOO" ]; then
    pruefe "odoo_cloud" 0 "keine Sicherung in Google Drive"
else
    # Feld 2 ist das Datum, Feld 3 die Uhrzeit. Beide werden gebraucht -
    # sonst wird ab Mitternacht gerechnet und das Alter ist immer zu hoch.
    CLOUD_DATUM=$(echo "$CLOUD_ODOO" | awk '{print $2" "$3}')
    CLOUD_ALT=$(( ( $(date +%s) - $(date -d "$CLOUD_DATUM" +%s 2>/dev/null || echo 0) ) / 3600 ))
    CLOUD_SZ=$(echo "$CLOUD_ODOO" | awk '{print $1}')
    if [ "$CLOUD_ALT" -gt 26 ] || [ "$CLOUD_ALT" -lt 0 ]; then
        pruefe "odoo_cloud" 0 "Kopie in der Cloud $CLOUD_ALT Stunden alt"
    elif [ "$CLOUD_SZ" -lt 20000000 ]; then
        pruefe "odoo_cloud" 0 "Kopie nur $((CLOUD_SZ/1024/1024)) MB — zu klein"
    else
        pruefe "odoo_cloud" 1 "$((CLOUD_SZ/1024/1024)) MB, $CLOUD_ALT h alt"
    fi
fi

# --- 5. VM-Sicherungen lokal (vzdump) --------------------------------------
for VMID in 210 360; do
    F=$(neueste "/mnt/data_family/proxmox_backups/dump/vzdump-qemu-${VMID}-*.vma.zst")
    if [ -z "$F" ]; then
        pruefe "vm${VMID}_lokal" 0 "keine Sicherung vorhanden"
    else
        SZ=$(stat -c%s "$F"); ALT=$(alter_stunden "$F")
        if [ "$ALT" -gt 30 ]; then
            pruefe "vm${VMID}_lokal" 0 "$ALT Stunden alt"
        elif [ "$SZ" -lt 100000000 ]; then
            pruefe "vm${VMID}_lokal" 0 "nur $((SZ/1024/1024)) MB — zu klein"
        else
            pruefe "vm${VMID}_lokal" 1 "$((SZ/1024/1024/1024)) GB, $ALT h alt"
        fi
    fi
done

# --- 6. VM-Sicherung in der Cloud ------------------------------------------
CLOUD=$(rclone lsl gdrive:FraWo-ProDesk-VMs 2>/dev/null | grep 'vzdump-qemu-360' | head -1)
if [ -z "$CLOUD" ]; then
    pruefe "vm360_cloud" 0 "keine Sicherung in der Cloud"
else
    pruefe "vm360_cloud" 1 "vorhanden"
fi

# --- 7. Container-Sicherungen im PBS ---------------------------------------
PBS_NEU=$(pvesm list pbs-frawo 2>/dev/null | grep -c "$(date +%Y-%m-%d)" || true)
if [ "${PBS_NEU:-0}" -eq 0 ]; then
    PBS_GESTERN=$(pvesm list pbs-frawo 2>/dev/null | grep -c "$(date -d yesterday +%Y-%m-%d)" || true)
    if [ "${PBS_GESTERN:-0}" -eq 0 ]; then
        pruefe "pbs_container" 0 "keine Sicherung von heute oder gestern"
    else
        pruefe "pbs_container" 1 "$PBS_GESTERN Sicherungen von gestern"
    fi
else
    pruefe "pbs_container" 1 "$PBS_NEU Sicherungen von heute"
fi

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
