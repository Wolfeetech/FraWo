#!/bin/bash
# FraWo — verbliebene Doubletten in Quarantäne räumen
# Angelegt 29.07.2026. Läuft in CT120.
#
# ===========================================================================
# REGEL
# ===========================================================================
# Je Künstler und Titel bleibt die Datei mit der HÖCHSTEN Bitrate. Alle
# anderen wandern in einen Quarantäne-Ordner — verschoben, nicht gelöscht.
#
# Warum Bitrate und nicht Länge oder Datum:
# Die Doubletten stammen nachweislich von der defekten USB-Platte aus
# Odoo #881, die "bei jedem Lesen andere Daten liefert". Erkennbar daran,
# dass dieselbe Aufnahme in identischer Länge, aber mit völlig
# unterschiedlichen Bitraten vorliegt:
#
#   Junior Fairplay - Sugar Puss, alle 7:03 lang:
#     889 kbps, 889 kbps, 1 kbps, 780 kbps, 889 kbps
#
# Eine FLAC-Datei mit 1 kbps kann es nicht geben — FLAC ist verlustfrei.
# Die niedrige Bitrate IST der Schaden. Die höchste Bitrate ist damit
# zuverlässig die intakte Fassung.
#
# ===========================================================================
# SICHERHEIT
# ===========================================================================
# - Ohne --anwenden wird nur angezeigt, was passieren würde.
# - Verschoben wird in _QUARANTAENE_Doubletten_<datum>, unter Beibehaltung
#   des ursprünglichen Pfades. Jede Datei ist damit rückverfolgbar und
#   zurückholbar.
# - Die Sicherung schliesst _QUARANTAENE_* aus, es entsteht also kein
#   Cloud-Upload.
# - NACH dem Lauf müssen die Sender-Playlisten neu aufgebaut werden
#   (kuration-tagesablauf.sql), sonst zeigen sie auf verschobene Dateien.

set -uo pipefail

ANWENDEN=0
[ "${1:-}" = "--anwenden" ] && ANWENDEN=1

QUAR="/mnt/music/_QUARANTAENE_Doubletten_$(date +%Y%m%d)"
LISTE=/tmp/doubletten-liste.txt
PROTOKOLL=/tmp/doubletten-verschoben.txt

beet duplicates -f '$artist|$title|$bitrate|$path' 2>/dev/null > "$LISTE"

if [ ! -s "$LISTE" ]; then
    echo "Keine Doubletten gefunden."
    exit 0
fi

# Je Gruppe die höchste Bitrate ermitteln und alle anderen sammeln.
# awk-Feldtrenner ist |, Bitrate steht als "889kbps" -> Zahl herauslösen.
awk -F'|' '
{
    gruppe = tolower($1) "|" tolower($2)
    br = $3; gsub(/[^0-9]/, "", br); br += 0
    pfad = $4
    if (!(gruppe in best) || br > best[gruppe]) {
        best[gruppe] = br
        bestpfad[gruppe] = pfad
    }
    n[gruppe]++
    alle[gruppe] = alle[gruppe] pfad "\n"
    bitrate[pfad] = br
}
END {
    for (g in alle) {
        split(alle[g], p, "\n")
        for (i in p) {
            if (p[i] != "" && p[i] != bestpfad[g])
                printf "%d\t%s\n", bitrate[p[i]], p[i]
        }
    }
}' "$LISTE" | sort -n > /tmp/zu-verschieben.txt

ANZAHL=$(wc -l < /tmp/zu-verschieben.txt)
if [ "$ANZAHL" -eq 0 ]; then
    echo "Nichts zu verschieben."
    exit 0
fi

echo "=== $ANZAHL Dateien wuerden in Quarantaene wandern ==="
echo
echo "Die zehn schlechtesten (Bitrate zuerst):"
head -10 /tmp/zu-verschieben.txt | while IFS=$'\t' read -r br p; do
    printf '  %6s kbps  %s\n' "$br" "$(echo "$p" | sed 's|/mnt/music/||' | cut -c1-72)"
done
echo
echo "Davon technisch unmoeglich (FLAC unter 200 kbps):"
awk -F'\t' '$1 < 200 && $1 > 0' /tmp/zu-verschieben.txt | wc -l | sed 's/^/  /'

if [ "$ANWENDEN" -ne 1 ]; then
    echo
    echo "Nichts verschoben. Mit --anwenden ausfuehren."
    exit 0
fi

echo
echo "=== Verschiebe nach $QUAR ==="
mkdir -p "$QUAR"
: > "$PROTOKOLL"
OK=0; FEHLER=0
while IFS=$'\t' read -r br p; do
    rel="${p#/mnt/music/}"
    ziel="$QUAR/$rel"
    mkdir -p "$(dirname "$ziel")" 2>/dev/null
    if mv "$p" "$ziel" 2>/dev/null; then
        echo -e "${br}\t${p}\t${ziel}" >> "$PROTOKOLL"
        OK=$((OK+1))
    else
        FEHLER=$((FEHLER+1))
    fi
done < /tmp/zu-verschieben.txt

echo "  verschoben: $OK"
echo "  Fehler:     $FEHLER"
echo "  Protokoll:  $PROTOKOLL"
echo
echo "Aus der Verwaltung entfernen:"
beet remove -f "path::_QUARANTAENE_Doubletten_" 2>/dev/null
echo "  erledigt"
echo
echo "WICHTIG: Jetzt die Sender-Playlisten neu aufbauen, sonst zeigen sie"
echo "auf verschobene Dateien:"
echo "  kuration-tagesablauf.sql und general-rotation-fuellen.sql erneut einspielen,"
echo "  danach azuracast_cli azuracast:radio:restart 1"
