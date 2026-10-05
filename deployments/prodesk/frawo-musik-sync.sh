#!/bin/bash
# Sichert die produktive Musikbibliothek vom ProDesk auf den ZFS-Pool des Ankers.
# Quelle: Odoo #1457. Die Arbeitsbereiche Inbox, _STAGING_RAW und Quarantine
# gehoeren nicht zur freigegebenen Bibliothek und enthalten bekannte defekte
# Altdateien; sie werden bewusst nicht als erfolgreiche Bibliothek gesichert.
set -uo pipefail

QUELLE="/mnt/music_hdd/"
ZIEL_HOST="root@10.1.0.92"
ZIEL_PFAD="/anker-backup/musik/"
LOG="/var/log/frawo-musik-sync.log"

echo "=== Start $(date '+%F %T') ===" >> "$LOG"
nice -n 19 ionice -c3 rsync -rlt --partial --bwlimit=40000 \
  --exclude 'Quarantine/' \
  --exclude 'Inbox/' \
  --exclude '_STAGING_RAW/' \
  --stats \
  "$QUELLE" "${ZIEL_HOST}:${ZIEL_PFAD}" >> "$LOG" 2>&1
RC=$?

if [ "$RC" -eq 0 ] || [ "$RC" -eq 24 ]; then
    ssh -o StrictHostKeyChecking=no "$ZIEL_HOST" \
      "date +%s > ${ZIEL_PFAD}.letzter-sync" 2>/dev/null
    SSH_RC=$?
    if [ "$SSH_RC" -ne 0 ]; then
        RC=$SSH_RC
    fi
fi

if [ "$RC" -eq 0 ] || [ "$RC" -eq 24 ]; then
    echo "=== Ende $(date '+%F %T') - erfolgreich (RC=$RC) ===" >> "$LOG"
    exit 0
else
    echo "=== Ende $(date '+%F %T') - FEHLGESCHLAGEN (Code $RC) ===" >> "$LOG"
    exit "$RC"
fi
