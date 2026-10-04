#!/usr/bin/env bash
# FraWo Funk - Stuendlicher Server-Sync fuer Radio-Rotation & Hoerer-Bewertungen.
#
# Laeuft auf dem ProDesk-Wirt (stock-pve / 10.1.0.128):
# 1. Synchronisiert Hoerer-Bewertungen aus Odoo nach Beets (CT120).
# 2. Aktualisiert Playlist 871 (Power Rotation) in AzuraCast (VM 220).
# 3. Aktualisiert Playlist 869 (Best of the Week) in AzuraCast.
# 4. Schreibt Prometheus-Textfile-Metriken fuer Erfolgs- und Staleness-Ueberwachung.
#
# Odoo-Aufgabe #1647.

set -uo pipefail
export PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"

TEXTFILE_DIR=/var/lib/node_exporter/textfile_collector
METRIC_ERFOLG="$TEXTFILE_DIR/frawo_radio_rotation_sync_erfolg.prom"
METRIC_STAND="$TEXTFILE_DIR/frawo_radio_rotation_sync_stand.prom"
LOCK_FILE="/run/lock/frawo-radio-rotation-sync.lock"

# Lock execution to prevent overlapping syncs
exec 200>"$LOCK_FILE"
flock -n 200 || {
    echo "Sync laeuft bereits (Lock $LOCK_FILE aktiv) -- Abbruch."
    exit 0
}

SCRIPT_PATH="/usr/local/bin/frawo-radio-rotation-server-sync.py"
if [ ! -f "$SCRIPT_PATH" ]; then
    echo "FEHLER: $SCRIPT_PATH existiert nicht!" >&2
    exit 1
fi

AUSGABE=$(python3 "$SCRIPT_PATH" 2>&1)
CODE=$?

echo "$AUSGABE"

POWER_TRACKS=$(printf '%s\n' "$AUSGABE" | sed -n 's/^FRAWO_RADIO_SYNC_POWER=\([0-9][0-9]*\)$/\1/p')
BEETS_SYNCED=$(printf '%s\n' "$AUSGABE" | sed -n 's/^FRAWO_RADIO_SYNC_BEETS=\([0-9][0-9]*\)$/\1/p')
QUARANTINED=$(printf '%s\n' "$AUSGABE" | sed -n 's/^FRAWO_RADIO_SYNC_QUARANTINE=\([0-9][0-9]*\)$/\1/p')
SYNC_OK=$(printf '%s\n' "$AUSGABE" | sed -n 's/^FRAWO_RADIO_SYNC_OK=\([0-9][0-9]*\)$/\1/p')

if [ "$CODE" -eq 0 ] && [ "$SYNC_OK" = "1" ] && [ -n "$POWER_TRACKS" ]; then
    ERFOLG=1
else
    ERFOLG=0
    echo "FEHLER: Radio-Rotation-Sync fehlgeschlagen oder unvollstaendig (Exit $CODE)." >&2
fi

if [ -d "$TEXTFILE_DIR" ]; then
    cat > "$METRIC_ERFOLG.tmp" <<METRICS
# HELP frawo_radio_rotation_sync_erfolg 1 = letzter Lauf erfolgreich, 0 = fehlgeschlagen.
# TYPE frawo_radio_rotation_sync_erfolg gauge
frawo_radio_rotation_sync_erfolg $ERFOLG
METRICS
    mv "$METRIC_ERFOLG.tmp" "$METRIC_ERFOLG"

    if [ "$ERFOLG" = "1" ]; then
        cat > "$METRIC_STAND.tmp" <<METRICS
# HELP frawo_radio_rotation_sync_letzter_erfolg_timestamp_seconds Zeitpunkt des letzten erfolgreichen Sync-Laufs.
# TYPE frawo_radio_rotation_sync_letzter_erfolg_timestamp_seconds gauge
frawo_radio_rotation_sync_letzter_erfolg_timestamp_seconds $(date +%s)
# HELP frawo_radio_rotation_sync_power_tracks Anzahl aktiver Titel in der Power-Rotation (Playlist 871).
# TYPE frawo_radio_rotation_sync_power_tracks gauge
frawo_radio_rotation_sync_power_tracks $POWER_TRACKS
# HELP frawo_radio_rotation_sync_beets_synced Anzahl in Beets synchronisierter Titel.
# TYPE frawo_radio_rotation_sync_beets_synced gauge
frawo_radio_rotation_sync_beets_synced ${BEETS_SYNCED:-0}
# HELP frawo_radio_rotation_sync_quarantined_tracks Anzahl unterdrueckter/quarantaenisierter Titel.
# TYPE frawo_radio_rotation_sync_quarantined_tracks gauge
frawo_radio_rotation_sync_quarantined_tracks ${QUARANTINED:-0}
METRICS
        mv "$METRIC_STAND.tmp" "$METRIC_STAND"
    fi
fi

exit "$CODE"
