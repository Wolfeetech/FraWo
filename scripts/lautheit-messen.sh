#!/bin/bash
# Misst die Lautheit einer Stichprobe aus der Radio-Bibliothek.
# Angelegt 29.07.2026 — Entscheidungsgrundlage, ob sich die Angleichung lohnt.
#
# Gemessen wird LUFS (Loudness Units Full Scale) nach EBU R128 — der Standard,
# nach dem auch Spotify, YouTube und der Rundfunk normalisieren. Je Datei
# werden 90 Sekunden aus der Mitte analysiert; das reicht fuer eine
# belastbare Schaetzung und geht schnell.
#
# Referenzwerte: Spotify -14 LUFS, Rundfunk -23 LUFS, Club-Master oft -6.

set -uo pipefail
export PATH="/usr/sbin:/usr/bin:/sbin:/bin"

ANZAHL="${1:-20}"
QUELLE=/mnt/music_hdd
ERG=/tmp/lautheit-stichprobe.txt

: > "$ERG"

find "$QUELLE" -type f \( -name '*.mp3' -o -name '*.flac' \) 2>/dev/null \
  | grep -v '_RETTUNG' \
  | shuf -n "$ANZAHL" \
  | while IFS= read -r f; do
      # -ss 60: eine Minute ueberspringen (Intros sind oft leiser)
      # -t 90:  90 Sekunden analysieren
      L=$(ffmpeg -nostdin -hide_banner -ss 60 -t 90 -i "$f" \
            -af ebur128 -f null - 2>&1 \
          | grep -A4 'Integrated loudness' \
          | grep -oE 'I:\s+-?[0-9.]+ LUFS' \
          | grep -oE '\-?[0-9.]+' | head -1)
      if [ -n "$L" ]; then
        printf '%s\t%s\n' "$L" "$(basename "$f" | cut -c1-52)" >> "$ERG"
      fi
    done

echo "=== Gemessene Dateien: $(wc -l < "$ERG") ==="
echo
sort -n "$ERG" | awk -F'\t' '{printf "  %7.1f LUFS  %s\n", $1, $2}'
echo
awk -F'\t' '
  { v[NR]=$1; s+=$1 }
  END {
    n=NR
    if (n==0) { print "  keine Messwerte"; exit }
    # sortieren fuer Median
    for(i=1;i<=n;i++) for(j=i+1;j<=n;j++) if(v[i]>v[j]){t=v[i];v[i]=v[j];v[j]=t}
    printf "  Leiseste:  %6.1f LUFS\n", v[1]
    printf "  Lauteste:  %6.1f LUFS\n", v[n]
    printf "  Median:    %6.1f LUFS\n", v[int((n+1)/2)]
    printf "  Mittel:    %6.1f LUFS\n", s/n
    printf "  SPANNE:    %6.1f dB\n", v[n]-v[1]
  }' "$ERG"
