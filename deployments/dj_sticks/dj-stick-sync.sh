#!/bin/bash
# FraWo - DJ-Stick automatische Sicherung
# Angelegt 19.08.2026.
#
# WOZU
# Wolf nimmt als DJ mehrere USB-Sticks mit auf Tour. Steckt er einen davon
# an den ProDesk, soll der Inhalt automatisch zu Google Drive gesichert
# werden - ohne Zeittakt-Abfrage, nur wenn wirklich ein Stick reinkommt.
#
# ERKENNUNG vs. BENENNUNG bewusst getrennt (Wolfs Wunsch, 19.08.2026):
#   - Erkennung "ist das einer von unseren Sticks?" laeuft ueber eine
#     unsichtbare Markierungsdatei ".frawo-dj-stick" im Wurzelverzeichnis.
#   - Der Name des Sicherungsordners ist einfach der Datenträgername
#     (Volume-Label), den Wolf frei waehlt (Show, Datum, Sender - egal was).
#
# Aufgerufen von dj-stick-sync@.service mit dem Kernel-Geraetenamen
# (z.B. "sdb1") als erstem Argument, ausgeloest durch die udev-Regel
# 99-dj-stick.rules bei jedem neu angesteckten USB-Datentraeger.
set -uo pipefail

DEV_NAME="${1:?Geraetename fehlt, z.B. sdb1}"
DEV="/dev/${DEV_NAME}"
MARKER=".frawo-dj-stick"
TMP_MNT="/mnt/dj-stick-tmp-${DEV_NAME}"
LOG=/var/log/dj-stick-sync.log
GDRIVE_ROOT="gdrive:Stockenweiler/dj_sticks"

log() { echo "$(date '+%Y-%m-%d %H:%M:%S') [$DEV_NAME] $*" >> "$LOG"; }

# Nur echte USB-Datentraeger, keine internen Platten
if ! udevadm info --query=property --name="$DEV" 2>/dev/null | grep -q '^ID_BUS=usb$'; then
    exit 0
fi

# Bekannte, nicht relevante USB-Geraete ueberspringen (per Datentraeger-UUID,
# nicht per wackligem Laufwerksbuchstaben - siehe Fallen-Tabelle in NOW.md)
DEV_UUID="$(blkid -s UUID -o value "$DEV" 2>/dev/null || true)"
case "$DEV_UUID" in
    76E8-CACF) exit 0 ;;  # gefaelschter Stick (Odoo #881) - nie relevant
esac

mkdir -p "$TMP_MNT"
if ! mount -o ro "$DEV" "$TMP_MNT" 2>>"$LOG"; then
    log "konnte nicht eingehaengt werden, uebersprungen"
    rmdir "$TMP_MNT" 2>/dev/null
    exit 0
fi

if [ ! -f "$TMP_MNT/$MARKER" ]; then
    log "keine Markierungsdatei gefunden - kein DJ-Stick, ignoriert"
    umount "$TMP_MNT"
    rmdir "$TMP_MNT" 2>/dev/null
    exit 0
fi

LABEL="$(blkid -s LABEL -o value "$DEV" 2>/dev/null)"
LABEL="${LABEL:-unbenannt-$DEV_NAME}"

log "DJ-Stick erkannt: '$LABEL' - starte Sicherung nach $GDRIVE_ROOT/$LABEL"
/usr/bin/rclone copy "$TMP_MNT" "$GDRIVE_ROOT/$LABEL" \
    --transfers=4 --checkers=8 \
    --exclude "System Volume Information/**" \
    --exclude '$RECYCLE.BIN/**' \
    --exclude ".Trashes/**" \
    --log-file="$LOG" --log-level INFO

RC=$?
umount "$TMP_MNT"
rmdir "$TMP_MNT" 2>/dev/null

if [ $RC -eq 0 ]; then
    log "Sicherung von '$LABEL' abgeschlossen"
else
    log "FEHLER bei Sicherung von '$LABEL' (Exitcode $RC)"
fi
exit $RC
