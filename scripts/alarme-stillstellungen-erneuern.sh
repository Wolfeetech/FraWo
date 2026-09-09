#!/bin/bash
# Stillstellungen im Alertmanager erneuern — 09.09.2026.
#
# ANLASS
# Am 07.09.2026 wurden nach dem ProDesk-Tod drei Pauschal-Stillstellungen
# gesetzt, die heute um 14:14 UTC ablaufen. In eine davon hatte ich selbst
# geschrieben: "vor Ablauf pruefen, nicht verlaengern ohne Pruefung."
# Das ist die Pruefung.
#
# WAS DIE PRUEFUNG ERGEBEN HAT
#
#   OdooBackupMetrikFehlt  war mit stillgestellt — und genau diese Sicherung
#                          ist seit dem 08.09. wieder in Betrieb. Gemessen am
#                          09.09.: letzter Erfolg 02:53, offsite bestaetigt,
#                          123,8 MB. Waere sie ausgefallen, haette der Alarm
#                          geschwiegen. Kommt NICHT wieder in die Stille.
#
#   CT106 (10.1.0.239)     WireGuard, war mitstillgestellt, antwortet aber
#                          wieder. Kommt NICHT wieder in die Stille.
#
#   10.1.0.128 / .52 /     ProDesk-Wirt und AdGuard-Master. Beide dauerhaft
#   stockenweiler-pve      weg. Eine Stillstellung ist hier das falsche
#                          Werkzeug — die Ziele gehoeren aus prometheus.yml
#                          entfernt. Bis dahin kurz stillgestellt, damit die
#                          Erinnerung daran nicht in Dauerlaerm untergeht.
#
#   Radio / Navidrome /    Echt ausgefallen, warten auf den OptiPlex.
#   HA-Eltern              Stillgestellt bis 23.09., Odoo #1357.
#
#   BackupTuevLaeuftNicht  Echte Luecke, nicht Folge des Ausfalls. Bewusst nur
#   Wiederherstellungs-    7 Tage stillgestellt: bis 16.09. muss der Backup-
#   testLaeuftNicht        TUEV wieder laufen, sonst wird es absichtlich laut.
#                          Das ist eine Frist, keine Unterdrueckung.
#
# Aufruf auf dem Anker. Wirkt sofort, nichts wird geloescht — die alten
# Stillstellungen laufen von selbst ab.

set -euo pipefail
AM="http://10.1.0.35:9093/api/v2/silences"

# Nur die Nummern ausfuehren, die in NUR stehen (Vorgabe: alle).
NUR="${NUR:-1 2 3 4}"

still() {
    local nr="$1" feld="$2" muster="$3" ende="$4" grund="$5"
    case " $NUR " in *" $nr "*) ;; *) return 0 ;; esac
    # In JSON ist \. KEINE gueltige Escape-Sequenz. Ein Regex-Backslash muss
    # deshalb verdoppelt werden, sonst antwortet der Alertmanager mit
    # "invalid character '.' in string escape code". Genau daran ist der
    # erste Lauf am 09.09.2026 gescheitert.
    local muster_json=${muster//\\/\\\\}
    local antwort
    antwort=$(curl -s -X POST "$AM" -H 'Content-Type: application/json' -d "{
        \"matchers\": [{\"name\":\"$feld\",\"value\":\"$muster_json\",\"isRegex\":true,\"isEqual\":true}],
        \"startsAt\": \"$(date -u +%Y-%m-%dT%H:%M:%S.000Z)\",
        \"endsAt\": \"$ende\",
        \"createdBy\": \"Claude Code (Agent)\",
        \"comment\": \"$grund\"
    }")
    echo "  $antwort"
    echo "    -> $feld =~ $muster"
    echo "    -> bis $ende"
    echo
}

echo "=== 1. Dienste, die echt ausgefallen sind und zurueckkommen sollen ======"
still 1 instance \
     '(10\.1\.0\.(38|94|248).*|https?://10\.1\.0\.(38|94|248).*|https://funk\.frawo\.tech.*)' \
     '2026-09-23T12:00:00.000Z' \
     'Radio (AzuraCast VM210), Navidrome CT120 und HA-Eltern VM360 lagen auf dem ProDesk und warten auf den OptiPlex. Odoo #1357. Am 23.09.2026 pruefen - nicht blind verlaengern.'

echo "=== 2. Ziele, die dauerhaft weg sind (Notnagel bis prometheus.yml sauber)"
still 2 instance \
     '(10\.1\.0\.(128|52).*|https?://10\.1\.0\.(128|52).*|stockenweiler-pve)' \
     '2026-09-23T12:00:00.000Z' \
     'ProDesk-Wirt und AdGuard-Master sind dauerhaft weg. RICHTIGE Loesung ist das Entfernen der Ziele aus prometheus.yml, nicht diese Stillstellung. Odoo #1357.'

echo "=== 3. Folgefehler des Radio-Ausfalls ==================================="
still 3 alertname \
     '(RadioBackupMetrikFehlt|VMCloudBackupMetrikFehlt|RadioStreamAus|TunnelStockenweilerUnbekannt)' \
     '2026-09-23T12:00:00.000Z' \
     'Folge des Radio-/ProDesk-Ausfalls. Bewusst OHNE OdooBackupMetrikFehlt - diese Sicherung laeuft seit 08.09. wieder und muss alarmieren duerfen. Odoo #1357.'

echo "=== 4. Echte Luecke, mit Frist statt Dauerstille ========================"
still 4 alertname \
     '(BackupTuevLaeuftNicht|WiederherstellungstestLaeuftNicht)' \
     '2026-09-16T12:00:00.000Z' \
     'KEINE Ausfallfolge, sondern eine echte Luecke: der Backup-TUEV prueft noch Pfade auf dem toten ProDesk. Nur 7 Tage still. Ist er bis 16.09.2026 nicht neu gebaut, wird es absichtlich wieder laut. Odoo #1389.'

echo "========================================================================"
echo "GEGENPROBE — was ist jetzt NICHT mehr stillgestellt und muss alarmieren:"
echo "  OdooBackupMetrikFehlt   (verschluesselte Cloud-Kopie, laeuft seit 08.09.)"
echo "  10.1.0.239 / CT106      (WireGuard, antwortet wieder)"
echo
echo "Aktive Stillstellungen nach dieser Aenderung:"
curl -s "$AM" | python3 -c '
import sys, json
for s in json.load(sys.stdin):
    if s["status"]["state"] != "active":
        continue
    print("  bis %s  %s" % (s["endsAt"][:16], s["comment"][:88]))
'
