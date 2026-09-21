#!/bin/sh
# FraWo · Laedt die Prometheus-Konfiguration neu UND weist nach, dass es wirkte.
#
# Hintergrund: Ein Neuladen scheitert bei dieser Anlage gern lautlos - der Dienst
# bleibt "active", die Aenderung ist aber nicht geladen. Deshalb prueft dieses
# Skript hinterher an der Schnittstelle nach, statt dem Rueckgabewert zu glauben.
#
# Odoo-Aufgabe #1521.  Aufruf:  prometheus-neu-laden.sh
# Rueckgabewert: 0 = geladen und nachgewiesen, 1 = Problem

set -u
P=http://127.0.0.1:9090

echo "=== 1. Konfiguration pruefen ==="
if command -v promtool >/dev/null 2>&1; then
    if ! promtool check config /etc/prometheus/prometheus.yml >/dev/null 2>&1; then
        echo "  FEHLER in der Konfiguration - NICHT neu geladen:"
        promtool check config /etc/prometheus/prometheus.yml 2>&1 | tail -8 | sed 's/^/    /'
        exit 1
    fi
    echo "  Konfiguration in Ordnung"
else
    echo "  promtool fehlt - ueberspringe die Vorpruefung"
fi

# Regeldateien zaehlen, VOR dem Laden
VORHER=$(wget -qO- "${P}/api/v1/rules" 2>/dev/null \
         | grep -o '"name":"[^"]*"' | wc -l)
echo "  Regelgruppen vorher: ${VORHER}"

echo ""
echo "=== 2. Neu laden ==="
if wget -qO- --post-data='' "${P}/-/reload" >/dev/null 2>&1; then
    echo "  ueber die Schnittstelle angestossen"
elif systemctl reload prometheus 2>/dev/null; then
    echo "  ueber systemctl reload angestossen"
elif pkill -HUP prometheus 2>/dev/null; then
    echo "  ueber Signal angestossen"
else
    echo "  KEIN Weg zum Neuladen gefunden"
    exit 1
fi

sleep 4

echo ""
echo "=== 3. Nachweis: ist es wirklich geladen? ==="

# a) Antwortet der Dienst ueberhaupt?
if ! wget -qO- "${P}/-/healthy" >/dev/null 2>&1; then
    echo "  🔴 Prometheus antwortet nicht mehr - Neustart pruefen!"
    exit 1
fi
echo "  Dienst antwortet"

# b) Meldet er einen Ladefehler?
FEHLER=$(wget -qO- "${P}/api/v1/status/config" 2>/dev/null | grep -c 'error' || true)
[ "${FEHLER}" -gt 0 ] && echo "  ⚠ Konfigurations-Schnittstelle meldet einen Fehler"

# c) Wurden die Regeln neu eingelesen?
NACHHER=$(wget -qO- "${P}/api/v1/rules" 2>/dev/null \
          | grep -o '"name":"[^"]*"' | wc -l)
echo "  Regelgruppen nachher: ${NACHHER}"

# d) Zeitpunkt der letzten erfolgreichen Konfiguration
ERFOLG=$(wget -qO- "${P}/api/v1/query?query=prometheus_config_last_reload_successful" 2>/dev/null \
         | grep -o '"value":\[[^]]*\]' | grep -o '"[01]"' | tr -d '"')
if [ "${ERFOLG:-0}" = "1" ]; then
    echo "  ✅ prometheus_config_last_reload_successful = 1"
else
    echo "  🔴 prometheus_config_last_reload_successful = ${ERFOLG:-unbekannt}"
    echo "     Die Konfiguration wurde NICHT uebernommen."
    exit 1
fi

if [ "${NACHHER}" -lt "${VORHER}" ]; then
    echo "  ⚠ Es sind weniger Regeln geladen als vorher (${VORHER} → ${NACHHER})."
    echo "    Das kann gewollt sein - bitte pruefen."
fi

echo ""
echo "Fertig. Geladen und nachgewiesen."
exit 0
