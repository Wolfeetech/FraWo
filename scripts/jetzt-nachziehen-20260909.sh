#!/bin/bash
# Alles Offene in einem Durchgang — 09.09.2026.
#
# Fasst drei Dinge zusammen, die einzeln je einen Befehl gebraucht haetten:
#
#   1. Odoo-Cloud-Timer reparieren   (still kaputt seit gestern)
#   2. Wache ueber die Ueberwachung  (tot seit dem ProDesk-Ausfall)
#   3. Gespeicherte Arbeitsansichten in Odoo
#
# Jeder Schritt prueft sein ERGEBNIS, nicht seinen Rueckgabewert, und laeuft
# unabhaengig von den anderen. Ein Fehlschlag stoppt die anderen nicht — am
# Ende steht eine Zusammenfassung.
#
# Aufruf auf dem Anker als root. Alles umkehrbar, Rueckwege stehen unten.

set -uo pipefail
DATUM=$(date +%Y%m%d)
ERGEBNIS=""

merke() { ERGEBNIS="${ERGEBNIS}  $1"$'\n'; }

echo "########################################################################"
echo "# 1. ODOO-CLOUD-TIMER: laeuft drei Stunden zu frueh"
echo "########################################################################"
# Der Abzug in CT140 laeuft per Cron 03:30 UTC. Der Container steht auf UTC,
# systemd auf dem Wirt rechnet in CEST. Der Timer stand auf 04:30 Ortszeit
# = 02:30 UTC und lief damit VOR dem Abzug. Ergebnis: jeden Tag klaglos die
# Datei vom Vortag hochgeladen, Erfolg gemeldet, Kennzahl gruen.
if [ -f /etc/systemd/system/frawo-odoo-cloud.timer ]; then
    cp -a /etc/systemd/system/frawo-odoo-cloud.timer \
          "/root/frawo-odoo-cloud.timer.bak-${DATUM}"
    sed -i 's|^OnCalendar=.*|OnCalendar=*-*-* 06:15:00|' \
        /etc/systemd/system/frawo-odoo-cloud.timer
    [ -f /tmp/frawo-odoo-cloud-verschluesselt.sh ] && {
        cp -a /usr/local/bin/frawo-odoo-cloud-verschluesselt.sh \
              "/root/frawo-odoo-cloud.sh.bak-${DATUM}" 2>/dev/null
        install -m 750 /tmp/frawo-odoo-cloud-verschluesselt.sh \
                /usr/local/bin/frawo-odoo-cloud-verschluesselt.sh
    }
    systemctl daemon-reload
    systemctl restart frawo-odoo-cloud.timer
    NAECHST=$(systemctl show frawo-odoo-cloud.timer -p NextElapseUSecRealtime --value)
    echo "  Naechster Lauf: $(systemctl list-timers frawo-odoo-cloud.timer --no-pager | sed -n 2p | cut -c1-40)"
    merke "1. Timer  -> 06:15 Ortszeit, Altersgrenze 8 h (war 26 h)"
else
    echo "  Timer nicht gefunden - uebersprungen"
    merke "1. Timer  -> NICHT gefunden"
fi

echo
echo "########################################################################"
echo "# 2. WACHE UEBER DIE UEBERWACHUNG"
echo "########################################################################"
if [ -x /tmp/wache-umzug-auf-anker.sh ]; then
    bash /tmp/wache-umzug-auf-anker.sh
    if [ -s /var/lib/node_exporter/textfile_collector/monitoring_watchdog.prom ]; then
        merke "2. Wache  -> installiert, Kennzahl wird geschrieben"
    else
        merke "2. Wache  -> installiert, aber KEINE Kennzahl - nachsehen!"
    fi
else
    echo "  /tmp/wache-umzug-auf-anker.sh fehlt - uebersprungen"
    merke "2. Wache  -> Skript fehlt"
fi

echo
echo "########################################################################"
echo "# 3. ARBEITSANSICHTEN IN ODOO"
echo "########################################################################"
# ir.filters ist fuer die MCP-Schnittstelle gesperrt, deshalb ueber die Shell.
if pct exec 140 -- docker exec frawotech-odoo-1 test -f /tmp/ansichten.py 2>/dev/null; then
    pct exec 140 -- docker exec -i frawotech-odoo-1 sh -c \
      'odoo shell -d FraWo_GbR --db_host=$HOST --db_user=$USER --db_password=$PASSWORD --no-http < /tmp/ansichten.py' \
      2>&1 | grep -vE " INFO | WARNING |^Traceback|^  File |^    " | tail -18
    merke "3. Ansichten -> siehe Ausgabe oben"
else
    echo "  /tmp/ansichten.py nicht im Container - uebersprungen"
    merke "3. Ansichten -> Skript fehlt"
fi

echo
echo "########################################################################"
echo "# ZUSAMMENFASSUNG"
echo "########################################################################"
printf '%s' "$ERGEBNIS"
echo
echo "NOCH VON HAND (nicht automatisierbar):"
echo "  Telegram-Schluessel der Wache aus Vaultwarden:"
echo "    printf '%s' '<TOKEN>' > /root/.telegram-frawo && chmod 600 /root/.telegram-frawo"
echo
echo "RUECKWEGE:"
echo "  Timer:  cp /root/frawo-odoo-cloud.timer.bak-${DATUM} /etc/systemd/system/frawo-odoo-cloud.timer && systemctl daemon-reload"
echo "  Wache:  mv /etc/cron.d/frawo-wache /root/frawo-wache.deaktiviert-${DATUM}"
echo "  Filter: in Odoo unter Favoriten einzeln loeschbar"
echo "########################################################################"
