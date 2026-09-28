#!/bin/bash
# 🤖 [Claude] 28.09.2026, Odoo #1595 — Abrechnung aus der Projektmappe.
# Aufruf:  bash abrechnung_lauf.sh test      -> spielt alles durch, setzt IMMER zurueck
#          bash abrechnung_lauf.sh speichern -> wie test; nur wenn alles gruen: Einrichtung speichern
cd "$(dirname "$0")"
case "$1" in test) C=False ;; speichern) C=True ;; *) echo "test oder speichern"; exit 1 ;; esac
B=$(sed "s/__COMMIT__/$C/" 2026-09-28_abrechnung_projektmappe.py | base64 -w0)
ssh anker-pve "pct exec 140 -- docker exec frawotech-odoo-1 sh -c 'echo $B | base64 -d > /tmp/einr.py && odoo shell -c /etc/odoo/odoo.conf -d FraWo_GbR --no-http --db_host \"\$HOST\" --db_user \"\$USER\" --db_password \"\$PASSWORD\" < /tmp/einr.py 2>&1 | grep -vE \" INFO | WARNING \" | grep -E \"^(OK|FAIL|Automat|Projekt|Aufgaben|Rechn|TEST|COMMIT|KEIN)|Error:\"; rm -f /tmp/einr.py'"
