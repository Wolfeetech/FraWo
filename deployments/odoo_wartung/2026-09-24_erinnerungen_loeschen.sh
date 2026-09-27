#!/bin/bash
# 🤖 [Claude] 24.09.2026 — 30 automatische Erinnerungen leise loeschen (26 bei Wolf, 4 bei Alois)
# Freigabe Wolf 24.09.2026. Ablauf: Probelauf (Rollback) -> nur wenn 30/30 gefunden und 0 Meldungen -> echter Lauf.
# Aufruf am StudioPC:  bash C:/Users/StudioPC/FraWo/deployments/odoo_wartung/2026-09-24_erinnerungen_loeschen.sh
cd "$(dirname "$0")"
PY=2026-09-24_erinnerungen_loeschen.py

lauf() {
  B64=$(sed "s/__COMMIT__/$1/" "$PY" | base64 -w0)
  ssh anker-pve "pct exec 140 -- docker exec frawotech-odoo-1 sh -c 'echo $B64 | base64 -d > /tmp/akt.py && odoo shell -c /etc/odoo/odoo.conf -d FraWo_GbR --no-http --db_host \"\$HOST\" --db_user \"\$USER\" --db_password \"\$PASSWORD\" < /tmp/akt.py 2>&1 | grep -E \"gefunden|danach|COMMIT|ROLLBACK|Error|Abweichung|Unerwartet\"; rm -f /tmp/akt.py'"
}

echo "== Probelauf (aendert nichts)"
P=$(lauf False); echo "$P"
if echo "$P" | grep -q "gefunden: 30 von 30" && echo "$P" | grep -q "neue Meldungen: 0" && echo "$P" | grep -q ROLLBACK; then
  echo "== Probelauf sauber - echter Lauf"
  lauf True
else
  echo "Probelauf nicht sauber - NICHTS geloescht. Ausgabe bitte Claude zeigen."
  exit 1
fi
