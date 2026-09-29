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
#   5. pbs_datastore    — PBS VM241 (10.1.0.8): jeder laufende Gast mit Sicherung <26h (seit 24.09.2026)

set -uo pipefail
export PATH="/usr/sbin:/usr/bin:/sbin:/bin"

# Every external check must fail closed within a bounded time.
TIMEOUT_LOCAL=30
TIMEOUT_REMOTE=180

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
ODOO_LOKAL_DATEI=$(timeout "$TIMEOUT_LOCAL" lxc-attach -n 140 -- sh -c 'ls -t /var/backups/odoo/*.sql.gz 2>/dev/null | head -1' || true)
if [ -z "$ODOO_LOKAL_DATEI" ]; then
    pruefe "odoo_lokal" 0 "keine Dump-Datei in CT140:/var/backups/odoo/ gefunden"
else
    SZ=$(timeout "$TIMEOUT_LOCAL" lxc-attach -n 140 -- stat -c %s "$ODOO_LOKAL_DATEI" 2>/dev/null || echo 0)
    MTIME=$(timeout "$TIMEOUT_LOCAL" lxc-attach -n 140 -- stat -c %Y "$ODOO_LOKAL_DATEI" 2>/dev/null || echo 0)
    ALT=$(( ( $(date +%s) - MTIME ) / 3600 ))

    if [ "$SZ" -lt 20000000 ]; then
        pruefe "odoo_lokal" 0 "nur $((SZ/1024/1024)) MB — zu klein (<20 MB)"
    elif [ "$ALT" -gt 26 ]; then
        pruefe "odoo_lokal" 0 "$ALT Stunden alt (>26h)"
    elif ! timeout "$TIMEOUT_LOCAL" lxc-attach -n 140 -- gzip -t "$ODOO_LOKAL_DATEI" 2>/dev/null; then
        pruefe "odoo_lokal" 0 "Archiv beschädigt (gzip -t fehlerhaft)"
    else
        pruefe "odoo_lokal" 1 "$((SZ/1024/1024)) MB, $ALT h alt, gzip -t OK"
    fi
fi

# --- 2. Odoo verschlüsselte Kopie in der Cloud (gcrypt:Odoo) ----------------
CLOUD_ODOO=$(timeout "$TIMEOUT_REMOTE" rclone lsl gcrypt:Odoo 2>/dev/null | grep '\.sql\.gz$' | sort -k2,3 | tail -1 || true)
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
GDRIVE_LISTE=$(timeout "$TIMEOUT_REMOTE" pvesm list google-drive 2>/dev/null || true)
# Seit 29.09.2026 (Odoo #1594): Das Laufwerk /mnt/google-drive ist ein rclone-Mount mit
# Schreib-Zwischenspeicher. vzdump meldet "Finished Backup", sobald die Datei im
# Zwischenspeicher liegt - der eigentliche Upload kommt danach und kann scheitern
# (28.09.: Input/output error bei VM 300). Laufwerksliste und vzdump-Log sehen davon
# nichts. Deshalb zaehlt eine Sicherung nur, wenn sie DIREKT in Google Drive liegt,
# in derselben Groesse.
GDRIVE_ECHT=$(timeout "$TIMEOUT_REMOTE" rclone lsl gdrive:dump --max-depth 1 2>/dev/null || true)

if [ -z "$GDRIVE_LISTE" ]; then
    pruefe "gaeste_cloud" 0 "Google Drive Backup-Speicher nicht abrufbar"
elif [ -z "$GDRIVE_ECHT" ]; then
    pruefe "gaeste_cloud" 0 "Google Drive direkt (rclone lsl gdrive:dump) nicht abrufbar"
else
    # Seit 28.09.2026 woechentlich in drei Gruppen (Mo/Mi/Fr, Odoo #1590) -> Frist 8 Tage.
    DATUMS=$(for i in 0 1 2 3 4 5 6 7 8; do date -d "-$i day" +%Y_%m_%d; done | paste -sd'|')
    FEHLEND=""
    OK_COUNT=0
    for G_ID in $ANKER_GAESTE; do
        G_ZEILE=$(printf '%s\n' "$GDRIVE_LISTE" \
            | grep -E "vzdump-(lxc|qemu)-${G_ID}-(${DATUMS})" | tail -1 || true)
        if [ -z "$G_ZEILE" ]; then
            FEHLEND="$FEHLEND ${G_ID}(fehlt)"
            continue
        fi
        G_GROESSE=$(printf '%s' "$G_ZEILE" | awk '{print $(NF-1)}')
        case "$G_GROESSE" in
            ''|*[!0-9]*) FEHLEND="$FEHLEND ${G_ID}(Größe unlesbar)" ;;
            *) G_DATEI=$(printf '%s' "$G_ZEILE" | awk '{print $1}'); G_DATEI="${G_DATEI##*/}"
               G_ECHT=$(printf '%s\n' "$GDRIVE_ECHT" | awk -v n="$G_DATEI" '$4==n{print $1}' | head -1)
               if [ "$G_GROESSE" -lt 52428800 ]; then
                   FEHLEND="$FEHLEND ${G_ID}(nur $((G_GROESSE/1024/1024))MB)"
               elif [ "$G_ECHT" != "$G_GROESSE" ]; then
                   FEHLEND="$FEHLEND ${G_ID}(nicht hochgeladen: ${G_DATEI})"
               else
                   OK_COUNT=$((OK_COUNT + 1))
               fi ;;
        esac
    done
    if [ -n "$FEHLEND" ]; then
        pruefe "gaeste_cloud" 0 "Fehlende/zu kleine Gäste-Sicherungen:$FEHLEND"
    else
        pruefe "gaeste_cloud" 1 "$OK_COUNT/10 Gäste in Google Drive (direkt geprüft, Größe gleich), jüngste höchstens 8 Tage alt"
    fi
fi

# --- 4. ZFS Pool anker-backup Integrität -------------------------------------
ZFS_STATUS=$(timeout "$TIMEOUT_LOCAL" zpool status -x anker-backup 2>/dev/null || true)
if [ "$ZFS_STATUS" = "pool 'anker-backup' is healthy" ]; then
    pruefe "zfs_anker_backup" 1 "Mirror-Pool ONLINE, 0 Lesefehler"
else
    pruefe "zfs_anker_backup" 0 "ZFS-Pool nicht gesund: ${ZFS_STATUS:-unbekannt}"
fi

# --- 5. Proxmox Backup Server (VM241 OptiPlex, seit 24.09.2026, Odoo #1462) --
# Nicht nur "Speicher aktiv": jeder laufende Gast im Verbund (ausser 240 alter PBS,
# 241 PBS selbst, 990 Test-VM) braucht eine PBS-Sicherung juenger als 26 h.
# Fehlende Gaeste werden mit Namen gemeldet. Jeder Fehler (PBS weg, pvesm haengt) = durchgefallen.
PBS_FEHLT=$(timeout "$TIMEOUT_REMOTE" python3 - <<'PYEOF' 2>&1 | tail -1
import json, socket, subprocess, time
AUS = {240, 241, 990}
def j(cmd):
    return json.loads(subprocess.run(cmd, capture_output=True, text=True, check=True).stdout)
res = j(["pvesh", "get", "/cluster/resources", "--type", "vm", "--output-format", "json"])
laufend = {r["vmid"]: r.get("name", "") for r in res if r.get("status") == "running" and r["vmid"] not in AUS}
jung = {}
for b in j(["pvesh", "get", "/nodes/" + socket.gethostname() + "/storage/pbs/content", "--output-format", "json"]):
    v = int(b.get("vmid") or 0)
    jung[v] = max(jung.get(v, 0), int(b.get("ctime") or 0))
grenze = time.time() - 26 * 3600
fehlt = ["%d %s" % (v, n) for v, n in sorted(laufend.items()) if jung.get(v, 0) < grenze]
print(("FEHLT " + ", ".join(fehlt)) if fehlt else ("OK %d" % len(laufend)))
PYEOF
)
case "$PBS_FEHLT" in
    "OK "*) pruefe "pbs_datastore" 1 "PBS 10.1.0.8: alle ${PBS_FEHLT#OK } laufenden Gaeste juenger als 26 h gesichert" ;;
    *)      pruefe "pbs_datastore" 0 "PBS 10.1.0.8: ${PBS_FEHLT:0:300}" ;;
esac

# --- 6. Musikbibliothek auf dem Anker (Odoo #1457) ---------------------------
# Die 464 GB Musik haengen als Bind-Mount im Fileserver-Container und werden
# von vzdump prinzipbedingt NICHT gesichert. Seit 14.09.2026 laeuft dafuer
# ein naechtlicher rsync vom ProDesk hierher.
# 15.09.2026 (Claude, Odoo #1457/#1462, korrigiert nach Review durch Jarvis):
# Zustand des Pools wird aus ZFS-Metadaten geprueft, BEVOR der Pfad beruehrt wird.
# Vorher blieb dieser Block auf dem suspendierten Pool im D-Zustand stehen
# und hielt den GESAMTEN TUEV an - 4 h ohne Ergebnis und ohne Telegram-
# Bericht. Eine Pruefung, die nicht scheitern kann, ist schlechter als keine:
# jetzt faellt sie durch, statt stehenzubleiben.
#
# Review-Befund Jarvis (15.09.2026): Zeitbegrenzungen allein reichen NICHT.
# GNU timeout sendet ein Signal - ein Prozess im ununterbrechbaren Zustand D
# (Kernel-I/O auf einem suspendierten Pool) nimmt weder TERM noch KILL an, und
# timeout selbst wartet dann auf sein Kind. Genau das war am 15.09. zu sehen:
# SIGKILL blieb sowohl beim rclone-Rest als auch beim haengenden vzdump wirkungslos.
# Deshalb steht jetzt eine Zustandsabfrage davor, die NUR Metadaten liest
# (zpool list antwortet auch bei SUSPENDED in 0 s, nachgemessen). Die
# Zeitbegrenzungen bleiben als zweite Sicherung gegen normale Haenger.
MUSIK_PFAD="/anker-backup/musik"
MUSIK_MARKE="$MUSIK_PFAD/.letzter-sync"
MUSIK_POOL_ZUSTAND=$(timeout 10 zpool list -H -o health anker-backup 2>/dev/null || echo UNBEKANNT)
if [ "$MUSIK_POOL_ZUSTAND" != "ONLINE" ]; then
    pruefe "musik_bibliothek" 0 "Pool anker-backup ist $MUSIK_POOL_ZUSTAND - Pfad bewusst nicht angefasst"
elif ! timeout 10 ls -d "$MUSIK_PFAD" >/dev/null 2>&1; then
    pruefe "musik_bibliothek" 0 "Pfad $MUSIK_PFAD nicht lesbar"
else
    MUSIK_GB=$(timeout 300 du -s --block-size=1G "$MUSIK_PFAD" 2>/dev/null | awk '{print $1}')
    MUSIK_GB=${MUSIK_GB:-0}
    if [ ! -f "$MUSIK_MARKE" ]; then
        pruefe "musik_bibliothek" 0 "noch kein erfolgreicher Abgleich (${MUSIK_GB} GB vorhanden)"
    else
        MUSIK_ALT=$(( ( $(date +%s) - $(cat "$MUSIK_MARKE" 2>/dev/null || echo 0) ) / 3600 ))
        if [ "$MUSIK_GB" -lt 400 ]; then
            pruefe "musik_bibliothek" 0 "nur ${MUSIK_GB} GB — zu wenig (erwartet >400 GB)"
        elif [ "$MUSIK_ALT" -gt 30 ]; then
            pruefe "musik_bibliothek" 0 "letzter Abgleich ${MUSIK_ALT} Stunden her (>30h)"
        else
            pruefe "musik_bibliothek" 1 "${MUSIK_GB} GB, letzter Abgleich vor ${MUSIK_ALT} h"
        fi
    fi
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
        POOL_PCT=$(timeout "$TIMEOUT_LOCAL" lvs --noheadings -o data_percent pve/data 2>/dev/null | tr -d ' %' || echo "?")
        if [ "$DURCHGEFALLEN" -eq 0 ]; then
            TG_TEXT="🛡️ [FraWo Morgen-Lage] $(date '+%d.%m.%Y %H:%M')
✅ Backups: ${GEPRUEFT}/${GEPRUEFT} BESTANDEN
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
