#!/bin/bash
# FraWo - Neuen DJ-Stick fuer die automatische Sicherung vorbereiten
# Angelegt 19.08.2026.
#
# BENUTZUNG (Stick vorher einstecken und einhaengen, z.B. unter /media/...):
#   dj-stick-vorbereiten.sh /media/wolf/MEIN-STICK-NAME
#
# Legt nur die unsichtbare Markierungsdatei an, damit der Server den Stick
# kuenftig automatisch erkennt. Der sichtbare Name des Sticks (Volume-Label)
# bleibt Wolfs freie Wahl - vorher schon beim Formatieren vergeben.
set -euo pipefail

ZIEL="${1:?Bitte den Einhängepfad des Sticks angeben, z.B. /media/wolf/MEIN-STICK}"

if [ ! -d "$ZIEL" ]; then
    echo "FEHLER: '$ZIEL' existiert nicht oder ist kein eingehaengter Stick."
    exit 1
fi

touch "$ZIEL/.frawo-dj-stick"
echo "Fertig. '$ZIEL' wird jetzt beim naechsten Anstecken automatisch gesichert."
echo "Datentraegername (wird als Ordnername bei Google Drive verwendet):"
lsblk -no LABEL "$(findmnt -n -o SOURCE --target "$ZIEL")" 2>/dev/null || echo "  (nicht ermittelbar, aber egal - Name wurde beim Formatieren vergeben)"
