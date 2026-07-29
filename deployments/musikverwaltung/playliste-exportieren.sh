#!/bin/bash
# FraWo — Playlisten aus der zentralen Musikverwaltung erzeugen
# Angelegt 29.07.2026. Läuft in CT120.
#
# ===========================================================================
# WOZU
# ===========================================================================
# Eine Kuration, drei Ziele: derselbe Auswahlbefehl erzeugt eine Liste, die
# Rekordbox, Mixxx und der Sender gleichermassen lesen können. Man pflegt an
# einer Stelle statt an dreien.
#
# ===========================================================================
# AUFRUF
# ===========================================================================
#   ./playliste-exportieren.sh <name> '<auswahl>'
#
# Die Auswahl ist eine beets-Abfrage. Beispiele:
#
#   ./playliste-exportieren.sh warmup       'genre:deep house length:240..600'
#   ./playliste-exportieren.sh peaktime     'genre:techno length:300..900'
#   ./playliste-exportieren.sh dekmantel    'label:Dekmantel'
#   ./playliste-exportieren.sh bowie        'artist:Bowie'
#   ./playliste-exportieren.sh neu-2026     'added:2026-01..'
#   ./playliste-exportieren.sh lange-sets   'length:2400..'
#
# Mehrere Bedingungen werden mit Leerzeichen verknüpft (UND).
# Ein Minus davor kehrt sie um:  'genre:house -genre:tech house'
#
# ===========================================================================
# WARUM M3U8 UND NICHT ETWAS ANDERES
# ===========================================================================
# Eine .m3u8-Datei ist im Kern eine Liste von Dateipfaden mit UTF-8-Kodierung.
# Rekordbox und Mixxx lesen sie beide direkt ein, ohne Umweg und ohne
# Zusatzprogramm. Voraussetzung ist nur, dass die Musik für beide unter
# demselben Pfad erreichbar ist — bei uns über die Netzwerkfreigabe.
#
# Für Rekordbox gibt es zusätzlich das eigene XML-Format, das auch Cue-Punkte,
# BPM und Tonart transportiert. Das lohnt erst, wenn diese Werte gepflegt
# sind; solange sie fehlen, bringt es nichts gegenüber einer Pfadliste.

set -uo pipefail

NAME="${1:-}"
AUSWAHL="${2:-}"
ZIEL="${ZIEL:-/mnt/music/_playlisten}"
# Pfad, unter dem die Musik auf dem Windows-Rechner erscheint. Rekordbox und
# Mixxx laufen dort, nicht hier — deshalb müssen die Pfade übersetzt werden.
WIN_BASIS="${WIN_BASIS:-M:}"
LINUX_BASIS=/mnt/music

if [ -z "$NAME" ] || [ -z "$AUSWAHL" ]; then
    echo "Aufruf: $0 <name> '<auswahl>'"
    echo
    echo "Beispiele:"
    echo "  $0 warmup    'genre:deep house length:240..600'"
    echo "  $0 dekmantel 'label:Dekmantel'"
    echo "  $0 lange-sets 'length:2400..'"
    exit 1
fi

mkdir -p "$ZIEL"

# --- Auswahl treffen -------------------------------------------------------
# Erst zählen. Eine leere Playlist ist ein Fehler, kein Ergebnis — genau die
# Sorte stiller Fehlschlag, die man sonst erst beim Auflegen merkt.
ANZAHL=$(beet ls -f '$path' $AUSWAHL 2>/dev/null | wc -l)

if [ "$ANZAHL" -eq 0 ]; then
    echo "FEHLER: Die Auswahl '$AUSWAHL' trifft keinen einzigen Titel."
    echo "Prüfen mit:  beet ls $AUSWAHL"
    exit 1
fi

DAUER=$(beet ls -f '$length' $AUSWAHL 2>/dev/null \
        | awk '{s+=$1} END {printf "%.1f", s/3600}')

# --- Für Linux/Sender ------------------------------------------------------
# ACHTUNG bei der Dauer: beets gibt "$length" als 10:02 aus, das M3U-Format
# erwartet aber GANZE SEKUNDEN. Ein "10:02" liest ein Player als 10 Sekunden.
# Deshalb wird hier umgerechnet. Aufgefallen beim ersten Testexport.
LINUX_DATEI="$ZIEL/${NAME}.m3u8"
{
    echo "#EXTM3U"
    echo "#PLAYLIST:$NAME"
    beet ls -f '${length}|${artist} - ${title}|${path}' $AUSWAHL 2>/dev/null \
      | awk -F'|' '{
          n = split($1, t, ":")
          sek = (n == 3) ? t[1]*3600 + t[2]*60 + t[3] : (n == 2) ? t[1]*60 + t[2] : t[1]
          printf "#EXTINF:%d,%s\n%s\n", sek, $2, $3
        }'
} > "$LINUX_DATEI"

# --- Für Rekordbox und Mixxx auf dem Windows-Rechner -----------------------
# Pfade übersetzen und auf Backslash umstellen, sonst findet Windows nichts.
WIN_DATEI="$ZIEL/${NAME}_windows.m3u8"
sed "s|^${LINUX_BASIS}|${WIN_BASIS}|; s|/|\\\\|g; s|^#EXTM3U\\\\|#EXTM3U|; s|^#PLAYLIST:|#PLAYLIST:|" \
    "$LINUX_DATEI" \
  | sed 's|^#EXTINF:\(.*\)|#EXTINF:\1|' > "$WIN_DATEI"

echo "Playliste \"$NAME\" erzeugt"
echo "  Titel:   $ANZAHL"
echo "  Dauer:   $DAUER Stunden"
echo "  Für den Sender / Linux:      $LINUX_DATEI"
echo "  Für Rekordbox und Mixxx:     $WIN_DATEI"
echo
echo "In Rekordbox: Datei > Playlist importieren > die _windows-Datei wählen."
echo "In Mixxx:     Rechtsklick auf Playlists > Playlist importieren."
