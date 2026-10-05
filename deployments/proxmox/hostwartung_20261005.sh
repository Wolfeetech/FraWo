#!/usr/bin/env bash
# Proxmox-Hostwartung ohne Neustarts - Odoo #1911, vorbereitet von Claude am 05.10.2026.
# Start (Wolf, am StudioPC):  bash C:/Users/StudioPC/FraWo/deployments/proxmox/hostwartung_20261005.sh
#
# Befunde (gemessen 05.10.):
#  Anker    - Cron /etc/cron.d/lvm_exporter schreibt jede Minute "Successfully wrote ..." -> Cron verschickt
#             jede Minute eine Mail. Postfix-Relay (Brevo) hat seit 06.07. keine Zugangsdaten -> keine Mail
#             geht raus, ~7.600 haengen in der Warteschlange und werden jede Minute erneut versucht.
#  OptiPlex - /etc/aliases.db fehlt -> lokale Zustellung scheitert.
#           - ollama-firewall.service scheitert bei jedem Start und tut nichts. Ollama ist laengst ueber
#             cluster.fw freigegeben (nur CT150, CT110, Monitoring). Die alte Unit wuerde ganze /24-Netze
#             oeffnen, falls sie je wieder laeuft -> abschalten ist sicherer als reparieren.
#  ProDesk  - fstab-Eintrag //10.1.0.94/radio -> /mnt/radio_rw: Diese Freigabe gibt es auf CT120 nicht mehr
#             (heute: music, documents, scans, playlists, sender), nichts verwendet den Pfad.
#
# Jeder Schritt sichert vorher (*.bak-20261005). Keine Neustarts, kein Shelly.
set -euo pipefail
ssh_() { ssh -o BatchMode=yes "root@$1" "$2" 2>&1 | grep -v Authorized || true; }

echo "== 1/4 Anker: Cron leise stellen (Fehler kommen weiter durch)"
ssh_ 10.1.0.92 'cp -pn /etc/cron.d/lvm_exporter /root/lvm_exporter.cron.bak-20261005
sed -i -E "s#^(\* \* \* \* \* root /usr/local/bin/lvm_exporter_cron.py)\$#\1 >/dev/null#" /etc/cron.d/lvm_exporter
cat /etc/cron.d/lvm_exporter'

echo "== 2/4 Anker: aufgestaute Cron-Mails + deren Ruecklaeufer aus der Warteschlange entfernen"
echo "   (nur Betreff 'Cron <root@proxmox-anker> /usr/local/bin/lvm_exporter_cron.py' bzw."
echo "    'Undelivered Mail Returned to Sender'; vzdump-Meldungen bleiben. Liste: /root/queue-loeschen-20261005.txt)"
ssh_ 10.1.0.92 'for id in $(mailq | awk "/^[0-9A-F]+/{print \$1}" | tr -d "*!"); do
  postcat -hq "$id" 2>/dev/null | grep -q -E "^Subject: (Cron <root@proxmox-anker> /usr/local/bin/lvm_exporter_cron.py|Undelivered Mail Returned to Sender)" && echo "$id"
done > /root/queue-loeschen-20261005.txt
echo "   zu entfernen: $(wc -l < /root/queue-loeschen-20261005.txt)"
postsuper -d - < /root/queue-loeschen-20261005.txt 2>&1 | tail -1
mailq | tail -1'

echo "== 3/4 OptiPlex: Alias-Datenbank bauen, alte Ollama-Firewall-Unit abschalten"
ssh_ 10.1.0.227 'newaliases && ls -la /etc/aliases.db
systemctl cat ollama-firewall.service > /root/ollama-firewall.service.bak-20261005
systemctl disable --now ollama-firewall.service; systemctl reset-failed ollama-firewall.service || true
postqueue -f
iptables -S PVEFW-HOST-IN | grep 11434'

echo "== 4/4 ProDesk: toten radio_rw-Eintrag in fstab auskommentieren"
ssh_ 10.1.0.128 'cp -pn /etc/fstab /etc/fstab.bak-20261005
sed -i -E "s|^(//10\.1\.0\.94/radio /mnt/radio_rw .*)$|# 05.10.2026 #1911: Freigabe radio gibt es auf CT120 nicht mehr, nirgends verwendet\n# \1|" /etc/fstab
grep -n -A1 "#1911" /etc/fstab
systemctl daemon-reload; systemctl stop mnt-radio_rw.automount 2>/dev/null || true; systemctl reset-failed mnt-radio_rw.mount 2>/dev/null || true'

echo "== Kontrolle: fehlgeschlagene Units je Host"
for h in 10.1.0.92 10.1.0.128 10.1.0.227; do echo "-- $h"; ssh_ $h 'systemctl --failed --no-legend --plain'; done
echo "fertig - Ergebnis bitte Claude zeigen"
