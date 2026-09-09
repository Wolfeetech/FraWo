#!/bin/bash
# Umzug der Wache ueber die Ueberwachung auf den Anker — 09.09.2026.
#
# WARUM
# Die Wache lief auf dem HP ProDesk. Der ist am 07.09.2026 gestorben, und mit
# ihm die Wache. Zwei Tage lang gab es damit KEINE Aufsicht ueber die
# Ueberwachung — und niemand hat es gemerkt, weil die zugehoerige Prometheus-
# Regel auf "Zeitstempel zu alt" prueft. Fehlt die Kennzahl ganz, hat diese
# Regel nichts zu vergleichen und schweigt.
#
# Dieses Skript stellt beides wieder her:
#   1. die Wache selbst, auf dem Anker-Wirt (ausserhalb von CT155)
#   2. die ergaenzte Prometheus-Regel mit absent(), die kuenftig anschlaegt,
#      WEIL die Kennzahl fehlt — nicht erst, wenn sie alt ist
#
# EHRLICHE EINORDNUNG ZU REGEL 2
# Die Wache sitzt jetzt auf demselben Rechner wie der Container, den sie
# beobachtet. Das ist schwaecher als vorher (ProDesk beobachtete Anker) und
# faengt nur den Ausfall der Dienste ab, nicht den des ganzen Wirts. Solange
# es nur einen lebenden Knoten gibt, geht es nicht besser. Den Totalausfall
# des Ankers muss die externe Cloudflare-Benachrichtigung abdecken — die ist
# weiterhin offen und braucht Wolfs Login.
#
# VORAUSSETZUNG, die dieses Skript NICHT erledigen kann
#   /root/.telegram-frawo mit dem Bot-Schluessel, Rechte 600.
#   Der Schluessel liegt in Vaultwarden. Er stand nur auf dem ProDesk und ist
#   mit ihm verloren gegangen. Ohne ihn laeuft die Wache zwar und liefert die
#   Kennzahl (die Prometheus-Regeln greifen also), sie kann aber im Ernstfall
#   nicht funken.
#
# Aufruf auf dem Anker als root. Alles ist umkehrbar, siehe Fusszeile.

set -euo pipefail

DATUM=$(date +%Y%m%d)
QUELLE_SKRIPT=/tmp/monitoring-watchdog.sh
QUELLE_REGEL=/tmp/frawo_watchdog.yml
ZIEL_SKRIPT=/usr/local/bin/monitoring-watchdog.sh
CRON=/etc/cron.d/frawo-wache

echo "=== 1. Wache installieren ==============================================="
[ -r "$QUELLE_SKRIPT" ] || { echo "FEHLER: $QUELLE_SKRIPT fehlt"; exit 1; }

if [ -e "$ZIEL_SKRIPT" ]; then
    cp -a "$ZIEL_SKRIPT" "${ZIEL_SKRIPT}.bak-${DATUM}"
    echo "  vorhandene Fassung gesichert: ${ZIEL_SKRIPT}.bak-${DATUM}"
fi
install -m 750 "$QUELLE_SKRIPT" "$ZIEL_SKRIPT"
echo "  installiert: $ZIEL_SKRIPT"

install -d -m 755 /var/lib/frawo-watchdog
install -d -m 755 /var/lib/node_exporter/textfile_collector

echo
echo "=== 2. Alle 10 Minuten laufen lassen ===================================="
# Bewusst /etc/cron.d statt der root-Crontab: eine Datei, die man sieht,
# sichern und umbenennen kann. Am 20.08.2026 hat ein Formatfehler in der
# root-Crontab vier Tage lang ALLE Cron-Jobs stillgelegt.
cat > "$CRON" <<'CRONTAB'
# Wache ueber die Ueberwachung (CT155). Angelegt 09.09.2026.
# Abschalten: mv /etc/cron.d/frawo-wache /root/frawo-wache.deaktiviert-JJJJMMTT
SHELL=/bin/bash
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
*/10 * * * * root /usr/local/bin/monitoring-watchdog.sh >> /var/log/monitoring-watchdog.log 2>&1
CRONTAB
chmod 644 "$CRON"
echo "  angelegt: $CRON"

echo
echo "=== 3. Einen Lauf sofort ausloesen und nachmessen ======================="
# Regel 1: nicht dem Exit-Code glauben, sondern das Ergebnis am Ziel pruefen.
"$ZIEL_SKRIPT" || echo "  (Rueckgabewert != 0 — unten steht, ob die Kennzahl trotzdem da ist)"

METRIK=/var/lib/node_exporter/textfile_collector/monitoring_watchdog.prom
if [ -s "$METRIK" ]; then
    echo "  Kennzahl geschrieben:"
    sed 's/^/    /' "$METRIK"
else
    echo "  🔴 Kennzahl NICHT geschrieben — hier nicht weitermachen, erst klaeren."
fi

echo
echo "=== 4. Prometheus-Regel mit absent() nachziehen ========================="
if [ -r "$QUELLE_REGEL" ]; then
    pct push 155 "$QUELLE_REGEL" /tmp/frawo_watchdog.yml
    pct exec 155 -- bash -c '
        ZIEL=$(ls /etc/prometheus/rules/frawo_watchdog.yml 2>/dev/null || echo /etc/prometheus/frawo_watchdog.yml)
        [ -e "$ZIEL" ] && cp -a "$ZIEL" "${ZIEL}.bak-'"${DATUM}"'"
        cp /tmp/frawo_watchdog.yml "$ZIEL"
        promtool check rules "$ZIEL"
    '
    echo "  Regel geprueft und abgelegt. Neu laden:"
    echo "    pct exec 155 -- /usr/local/bin/prometheus-neu-laden.sh"
else
    echo "  uebersprungen — $QUELLE_REGEL fehlt"
fi

echo
echo "========================================================================"
echo "NOCH ZU TUN (nicht automatisierbar):"
echo "  Telegram-Schluessel aus Vaultwarden holen und ablegen:"
echo "    printf '%s' '<TOKEN>' > /root/.telegram-frawo && chmod 600 /root/.telegram-frawo"
echo "  Danach einmal proben:"
echo "    ZIEL=127.0.0.1 ZUSTAND=/tmp/wachtest METRIK=/dev/null $ZIEL_SKRIPT"
echo "    (muss eine Telegram-Nachricht ausloesen — sonst stimmt der Schluessel nicht)"
echo
echo "RUECKWEG:"
echo "  mv $CRON /root/frawo-wache.deaktiviert-${DATUM}"
echo "  rm $ZIEL_SKRIPT"
echo "========================================================================"
