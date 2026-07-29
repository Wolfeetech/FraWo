#!/bin/bash
# Misst die Lautheit des SENDESIGNALS über mehrere Minuten.
# Angelegt 29.07.2026.
#
# Der entscheidende Test: Nicht was in Dateien oder Datenbanken steht, sondern
# was tatsächlich aus dem Sender kommt. Bleibt die Lautheit über einen
# Titelwechsel hinweg gleich, arbeitet die Angleichung. Springt sie um
# mehrere dB, tut sie es nicht.
#
# Gemessen wird direkt am Sender (10.1.0.38:8000), nicht über Cloudflare.

set -uo pipefail
export PATH="/usr/sbin:/usr/bin:/sbin:/bin"

DAUER="${1:-360}"
FENSTER=20
AUFNAHME=/tmp/sendemitschnitt.mp3

echo "Nehme $DAUER Sekunden vom Sender auf..."
ffmpeg -nostdin -hide_banner -loglevel error \
       -t "$DAUER" -i http://10.1.0.38:8000/radio.mp3 \
       -c copy -y "$AUFNAHME" 2>/dev/null

GROESSE=$(stat -c%s "$AUFNAHME" 2>/dev/null || echo 0)
if [ "$GROESSE" -lt 100000 ]; then
    echo "FEHLER: Aufnahme zu klein ($GROESSE Bytes)."
    exit 1
fi
echo "Aufnahme: $(du -h "$AUFNAHME" | cut -f1)"
echo

echo "=== Lautheit je ${FENSTER}-Sekunden-Fenster ==="
N=$(( DAUER / FENSTER ))
: > /tmp/fenster.txt
for i in $(seq 0 $((N-1))); do
    START=$(( i * FENSTER ))
    L=$(ffmpeg -nostdin -hide_banner -ss "$START" -t "$FENSTER" -i "$AUFNAHME" \
          -af ebur128 -f null - 2>&1 \
        | grep -A4 'Integrated loudness' \
        | grep -oE 'I:\s+-?[0-9.]+ LUFS' | grep -oE '\-?[0-9.]+' | head -1)
    [ -n "$L" ] || continue
    echo "$L" >> /tmp/fenster.txt
    BAR=$(awk -v v="$L" 'BEGIN{n=int((v+30)*1.5); if(n<0)n=0; if(n>45)n=45; s=""; for(i=0;i<n;i++)s=s"#"; print s}')
    printf '  %5.1f LUFS  %s\n' "$L" "$BAR"
done

echo
awk '{v[NR]=$1; s+=$1}
 END{
   n=NR; if(n==0){print "  keine Messwerte"; exit}
   for(i=1;i<=n;i++)for(j=i+1;j<=n;j++)if(v[i]>v[j]){t=v[i];v[i]=v[j];v[j]=t}
   printf "  Leiseste Stelle: %6.1f LUFS\n", v[1]
   printf "  Lauteste Stelle: %6.1f LUFS\n", v[n]
   printf "  Mittel:          %6.1f LUFS\n", s/n
   printf "  SPANNE:          %6.1f dB\n", v[n]-v[1]
   print ""
   if (v[n]-v[1] < 3.5) print "  BEWERTUNG: gleichmaessig - die Angleichung arbeitet."
   else if (v[n]-v[1] < 6) print "  BEWERTUNG: leichte Schwankung - vertretbar, aber nicht optimal."
   else print "  BEWERTUNG: deutliche Spruenge - die Angleichung arbeitet NICHT."
 }' /tmp/fenster.txt

rm -f "$AUFNAHME"
