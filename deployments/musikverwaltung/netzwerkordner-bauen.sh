#!/bin/bash
# FraWo — Netzwerkordner zum Durchklicken bauen
# Angelegt 29.07.2026. Läuft in CT120.
#
# ===========================================================================
# WOZU
# ===========================================================================
# Wolf: "außerdem wünsche ich mir noch das ganze besser kontrollieren zu
#        können über die netzwerkordner"
#
# Die Musik liegt gewachsen in Ordnern wie "Ranger_07.26/Artists/..." oder
# "Library/DISCO, HOUSE, GARAGE HOUSE, RNB_SWING, ELECTRO, SYNTH-POP/...".
# Zum Kuratieren taugt das nicht.
#
# Dieses Skript legt daneben eine zweite Sicht an, nach Genre und Label
# sortiert — als VERWEISE, nicht als Kopien. Es entsteht kein einziges
# zusätzliches Byte Musik, und keine Datei existiert doppelt.
#
# ===========================================================================
# WARUM VERWEISE UND NICHT KOPIEN
# ===========================================================================
# Kopien wären der naheliegende Weg und wären falsch:
#   - die Bibliothek würde sich verdoppeln (420 GB -> 840 GB)
#   - die stündliche Cloud-Sicherung lüde alles nochmal hoch
#   - und man hätte genau das, was heute mühsam beseitigt wurde: Doubletten
#
# Ein Verweis ist ein Eintrag im Verzeichnis, der auf die echte Datei zeigt.
# Windows sieht im Explorer eine ganz normale Datei.
#
# Wichtig: Die Verweise sind RELATIV und bleiben innerhalb der Freigabe.
# Samba folgt solchen Verweisen standardmässig; nur Verweise, die aus der
# Freigabe hinauszeigen, wären blockiert ("wide links"). Deshalb relativ.
#
# ===========================================================================
# AUFRUF
# ===========================================================================
#   ./netzwerkordner-bauen.sh            baut neu auf
#
# Läuft beliebig oft. Die Ordner werden vorher geleert, damit gelöschte oder
# umsortierte Titel nicht als Leichen zurückbleiben.

set -uo pipefail

BASIS=/mnt/music
GENRE_DIR="$BASIS/_nach_Genre"
LABEL_DIR="$BASIS/_nach_Label"
LABEL_MINDEST=10

sicher() {
    # Dateinamen für Windows entschärfen: \ / : * ? " < > | sind dort verboten.
    echo "$1" | tr '\\/:*?"<>|' '_________' | cut -c1-120
}

# Die 16 kanonischen Genres. Alles andere landet in _Sonstige.
#
# Warum diese Liste hier nochmal steht: Die Vereinheitlichung
# (genres-vereinheitlichen.py) lässt Angaben unangetastet, die weder zuordenbar
# noch erkennbarer Müll sind — "France", "XDJ-RX", "Game", "Blues". Das ist
# dort richtig so: lieber stehenlassen als falsch einsortieren.
#
# Für die Ordneransicht wäre es aber Unsinn. Aus 16 übersichtlichen Ordnern
# würden 80, und genau das war das Problem, das wir lösen wollten. Deshalb
# hier die Klappe: Was nicht auf der Liste steht, kommt nach _Sonstige und
# kann von dort in Ruhe einsortiert werden.
ist_kanonisch() {
    case "$1" in
        House|Techno|Trance|Bass|Disco|"Funk & Soul"|"Indie & Wave"|\
        "Hip Hop"|Reggae|Jazz|Rock|Pop|Soundtrack|Ambient|Electronic|DJ-Sets)
            return 0 ;;
        *) return 1 ;;
    esac
}

echo "=== Alte Sicht entfernen ==="
rm -rf "$GENRE_DIR" "$LABEL_DIR"
mkdir -p "$GENRE_DIR" "$LABEL_DIR"
echo "  erledigt"

echo
echo "=== Nach Genre ==="
ANZ_G=0
beet ls -f '${genre}|${albumartist}|${album}|${artist}|${title}|${path}' 2>/dev/null \
| while IFS='|' read -r genre aartist album artist title pfad; do
    [ -n "$genre" ] || continue
    [ -f "$pfad" ] || continue
    endung="${pfad##*.}"
    if ist_kanonisch "$genre"; then
        g=$(sicher "$genre")
    else
        g="_Sonstige"
    fi
    # Album-Ebene mit hinein, damit Alben zusammenbleiben — das war der
    # ganze Punkt der Genre-Vereinheitlichung.
    if [ -n "$album" ]; then
        unter="$GENRE_DIR/$g/$(sicher "${aartist:-$artist}") - $(sicher "$album")"
    else
        unter="$GENRE_DIR/$g/_Einzeltitel"
    fi
    mkdir -p "$unter" 2>/dev/null
    ziel="$unter/$(sicher "$artist - $title").$endung"
    # Relativer Verweis: von $unter aus zurück zur Basis, dann zur Datei.
    rel=$(realpath --relative-to="$unter" "$pfad" 2>/dev/null)
    [ -n "$rel" ] && ln -sf "$rel" "$ziel" 2>/dev/null && ANZ_G=$((ANZ_G+1))
done
echo "  Genres: $(ls -1 "$GENRE_DIR" 2>/dev/null | wc -l)"
echo "  Verweise: $(find "$GENRE_DIR" -type l 2>/dev/null | wc -l)"

echo
echo "=== Nach Label (ab $LABEL_MINDEST Titeln) ==="
beet ls -f '${label}' 2>/dev/null | grep -v '^$' | sort | uniq -c | sort -rn \
  | awk -v m="$LABEL_MINDEST" '$1 >= m {$1=""; sub(/^ /,""); print}' > /tmp/labels.txt
echo "  Labels mit genug Material: $(wc -l < /tmp/labels.txt)"

while IFS= read -r label; do
    [ -n "$label" ] || continue
    l=$(sicher "$label")
    unter="$LABEL_DIR/$l"
    mkdir -p "$unter" 2>/dev/null
    beet ls -f '${artist}|${title}|${path}' "label:$label" 2>/dev/null \
    | while IFS='|' read -r artist title pfad; do
        [ -f "$pfad" ] || continue
        endung="${pfad##*.}"
        ziel="$unter/$(sicher "$artist - $title").$endung"
        rel=$(realpath --relative-to="$unter" "$pfad" 2>/dev/null)
        [ -n "$rel" ] && ln -sf "$rel" "$ziel" 2>/dev/null
    done
done < /tmp/labels.txt
echo "  Verweise: $(find "$LABEL_DIR" -type l 2>/dev/null | wc -l)"

echo
echo "=== Ergebnis ==="
echo "  Im Explorer unter M:\\ sichtbar:"
echo "    _nach_Genre\\   — nach Genre, Alben bleiben zusammen"
echo "    _nach_Label\\   — nach Plattenlabel"
echo "    _playlisten\\   — fertige Listen für Rekordbox und Mixxx"
echo
du -sh "$GENRE_DIR" "$LABEL_DIR" 2>/dev/null | sed 's/^/  /'
echo "  (nur Verweise — die Musik liegt weiterhin genau einmal auf der Platte)"
