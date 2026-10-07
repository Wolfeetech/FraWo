#!/usr/bin/env bash
# Hermes-Pilot (CT160): eigener Odoo-API-Schluessel fuer Benutzer agent (UID 7), 90 Tage gueltig, einzeln widerrufbar.
# Odoo #1965. Von Wolf am StudioPC zu starten:
#   ! bash C:/Users/StudioPC/FraWo/deployments/hermes/odoo_schluessel_einrichten.sh
# Der Schluessel erscheint nirgends auf dem Bildschirm: Odoo -> Vaultwarden (agent@) -> ~hermes/.hermes/.env (600).
set -euo pipefail
HIER=$(cd "$(dirname "$0")" && pwd)
ANKER=root@10.1.0.92
OPTI=root@10.1.0.227

echo "1/3 Schluessel in Odoo erzeugen"
ssh -o BatchMode=yes $ANKER "pct exec 140 -- docker exec -i frawotech-odoo-1 sh -c 'umask 077; odoo shell --db_host \"\${HOST:-db}\" -r \"\$USER\" -w \"\$PASSWORD\" -d FraWo_GbR --no-http --log-level=warn 2>&1'" \
  < "$HIER/odoo_apikey.py" | grep -E "Benutzer|Schluessel erzeugt"

echo "2/3 In Vaultwarden ablegen und an Hermes uebergeben"
ssh -o BatchMode=yes $ANKER "pct exec 140 -- docker exec -u root frawotech-odoo-1 sh -c 'cat /tmp/hermes_odoo_key; rm -f /tmp/hermes_odoo_key'" \
 | ssh -o BatchMode=yes $OPTI 'umask 077; cat > /root/.hk; [ -s /root/.hk ] || { echo "FEHLER: kein Schluessel"; exit 1; }
     frawo-secret ablegen "Odoo API-Key agent (Hermes-Pilot CT160)" agent@frawo.tech http://10.1.0.112:8069 < /root/.hk | grep -E "abgelegt|aktualisiert"
     pct push 160 /root/.hk /tmp/hk --user 1000 --group 1000 --perms 600; shred -u /root/.hk
     pct exec 160 -- su - hermes -c "E=~/.hermes/.env; grep -v ^ODOO_API_KEY= \$E > \$E.neu || true; printf \"ODOO_API_KEY=%s\n\" \"\$(cat /tmp/hk)\" >> \$E.neu; mv \$E.neu \$E; chmod 600 \$E; shred -u /tmp/hk; grep -c ^ODOO_API_KEY= \$E"'

echo "3/3 Fertig. Claude richtet jetzt den Odoo-MCP in Hermes ein."
