#!/bin/bash
# FraWo · Beobachtet den StudioPC über einen Neustart hinweg
#
# Zweck: Nachweisen, dass die KI nach einem Neustart OHNE Benutzeranmeldung
# antwortet. Der Beweis lässt sich nicht vom StudioPC selbst führen — dort
# läuft die Sitzung, die durch den Neustart verschwindet. Deshalb misst
# dieser Beobachter vom Anker aus und schreibt mit.
#
# Läuft auf dem Anker, protokolliert nach /var/log/frawo-studiopc-neustart.log
# Odoo-Aufgabe #1517

ZIEL="10.0.0.156"
PROTOKOLL="/var/log/frawo-studiopc-neustart.log"
DAUER_MIN=${1:-30}

ende=$(( $(date +%s) + DAUER_MIN * 60 ))
vorher_erreichbar=-1

{
  echo "=============================================================="
  echo "Beobachtung gestartet: $(date '+%Y-%m-%d %H:%M:%S %Z')"
  echo "Ziel: ${ZIEL}:11434  ·  Laufzeit: ${DAUER_MIN} Minuten"
  echo "=============================================================="
} >> "$PROTOKOLL"

while [ "$(date +%s)" -lt "$ende" ]; do
    # Antwortet die KI?
    code=$(timeout 6 curl -s -o /dev/null -m 5 -w "%{http_code}" \
             "http://${ZIEL}:11434/api/tags" 2>/dev/null)
    [ "$code" = "200" ] && jetzt=1 || jetzt=0

    # Nur Zustandswechsel protokollieren, nicht jede Messung.
    if [ "$jetzt" != "$vorher_erreichbar" ]; then
        ts=$(date '+%Y-%m-%d %H:%M:%S')
        if [ "$jetzt" = "1" ]; then
            # Wie viele Modelle? Beweist, dass es nicht nur ein offener Port ist.
            anzahl=$(timeout 8 curl -s -m 6 "http://${ZIEL}:11434/api/tags" 2>/dev/null \
                     | grep -o '"name"' | wc -l)
            echo "${ts}  KI ANTWORTET   (${anzahl} Modelle)" >> "$PROTOKOLL"
        else
            echo "${ts}  KI WEG         (HTTP ${code:-000})" >> "$PROTOKOLL"
        fi
        vorher_erreichbar=$jetzt
    fi
    sleep 10
done

{
  echo "Beobachtung beendet: $(date '+%Y-%m-%d %H:%M:%S')"
  echo ""
} >> "$PROTOKOLL"
