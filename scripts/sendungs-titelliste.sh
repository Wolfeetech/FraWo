#!/bin/bash
# FraWo Funk — Titelliste einer Sendung erzeugen
# Angelegt 29.07.2026. Läuft auf dem ProDesk.
#
# ===========================================================================
# WOZU
# ===========================================================================
# Odoo #323 sah einen KI-gestützten "Show Notes Generator" vor. Die
# Bestandsaufnahme am 29.07.2026 ergab, dass die Grundlage dafür fehlt:
#
#   - der dort genannte n8n-Arbeitsablauf 90aGBe2m EXISTIERT NICHT
#   - es ist kein KI-Zugang hinterlegt (nur httpHeaderAuth, pineconeApi)
#
# Er müsste also neu gebaut werden, plus Zugang, plus laufende Kosten je
# Sendung.
#
# Für ein DJ-Set ist das aber ohnehin der Umweg. Was Hörer bei einem Set
# wollen, ist die TITELLISTE — und die steht bereits vollständig in der
# Sendedatenbank. Kein KI-Dienst, keine Kosten, keine Halluzinationen.
#
# (Ein Sprach-zu-Text-Werkzeug wie Whisper hilft hier ebenfalls nicht: In
# einem DJ-Set wird nicht gesprochen. Sinnvoll wird das erst, wenn es
# moderierte Sendungen gibt.)
#
# ===========================================================================
# AUFRUF
# ===========================================================================
#   sendungs-titelliste.sh                    letzte 4 Stunden
#   sendungs-titelliste.sh 8                  letzte 8 Stunden
#   sendungs-titelliste.sh 4 --telegram       zusätzlich per Telegram schicken
#
# Ausgabe eignet sich direkt zum Einfügen bei Mixcloud, SoundCloud oder in
# einen Beitrag.

set -uo pipefail
export PATH="/usr/sbin:/usr/bin:/sbin:/bin"

STUNDEN="${1:-4}"
TELEGRAM=0
[ "${2:-}" = "--telegram" ] && TELEGRAM=1

SQL="/tmp/titelliste-$$.sql"
ERG="/tmp/titelliste-$$.txt"

# ZWEI FEHLER AUS DEM ERSTEN ANLAUF, hier festgehalten damit sie nicht
# wiederkommen:
#
# 1. timestamp_start ist ein DATETIME, kein Unix-Zeitstempel. FROM_UNIXTIME()
#    lieferte deshalb durchgehend NULL — die Uhrzeit blieb leer.
#
# 2. Der Umweg über station_media war unnötig UND falsch: Nur 591 von 9161
#    Zeilen haben überhaupt eine media_id, der Rest lief auf "Unbekannt".
#    song_history führt Künstler und Titel selbst.
cat > "$SQL" <<SQLENDE
SELECT
  DATE_FORMAT(h.timestamp_start, '%H:%i') AS zeit,
  COALESCE(NULLIF(TRIM(h.artist), ''), '') AS kuenstler,
  COALESCE(NULLIF(TRIM(h.title),  ''), h.text) AS titel
FROM song_history h
WHERE h.station_id = 1
  AND h.timestamp_start IS NOT NULL
  AND h.timestamp_start > NOW() - INTERVAL ${STUNDEN} HOUR
ORDER BY h.timestamp_start ASC;
SQLENDE

scp -q -o StrictHostKeyChecking=no "$SQL" root@10.1.0.38:/tmp/tl.sql 2>/dev/null
ssh -o StrictHostKeyChecking=no root@10.1.0.38 \
    'docker cp /tmp/tl.sql azuracast:/tmp/tl.sql' >/dev/null 2>&1

qm guest exec 210 -- docker exec azuracast sh -c \
  'mariadb -u$MYSQL_USER -p$MYSQL_PASSWORD $MYSQL_DATABASE -N < /tmp/tl.sql > /tmp/tl.txt 2>&1' >/dev/null 2>&1

ROH=$(qm guest exec 210 -- docker exec azuracast cat /tmp/tl.txt 2>/dev/null \
      | grep -oE '"out-data" : ".*"' | sed 's/"out-data" : "//; s/"$//')

if [ -z "$ROH" ]; then
    echo "Keine Titel in den letzten $STUNDEN Stunden gefunden."
    rm -f "$SQL"
    exit 1
fi

{
    echo "FraWo Funk — Titelliste"
    echo "$(date '+%d.%m.%Y'), letzte $STUNDEN Stunden"
    echo
    # Steht kein Künstler getrennt da, enthält das Titelfeld bereits die
    # ganze Zeile ("Künstler - Album - Titel"). Dann nicht künstlich einen
    # Gedankenstrich davorsetzen.
    printf '%b' "$ROH" | awk -F'\t' 'NF>=3 {
        if ($2 == "") printf "%s  %s\n", $1, $3
        else          printf "%s  %s — %s\n", $1, $2, $3
    }'
    echo
    echo "funk.frawo.tech"
} > "$ERG"

ANZAHL=$(grep -cE '^[0-9]{2}:[0-9]{2}' "$ERG")
cat "$ERG"
echo
echo "($ANZAHL Titel)"

if [ "$TELEGRAM" -eq 1 ] && [ -r /root/.telegram-frawo ]; then
    T=$(tr -d "'\"" < /root/.telegram-frawo | tr -d '[:space:]')
    curl -s --max-time 25 -d "chat_id=5924907152" \
         --data-urlencode "text=$(cat "$ERG")" \
         "https://api.telegram.org/bot${T}/sendMessage" >/dev/null 2>&1 \
      && echo "per Telegram verschickt"
fi

rm -f "$SQL" "$ERG"
