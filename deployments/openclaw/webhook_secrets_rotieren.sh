#!/usr/bin/env bash
# Rotiert die drei Webhook-Secrets des Jarvis-Handlers (CT150, odoo-webhook.service) – Odoo #1917.
#
# Anlass 05.10.2026: FRAWO_ALERT_SECRET, FRAWO_TASK_SECRET und FRAWO_CHATTER_SECRET standen
# seit 12.09. in der oeffentlichen Git-Historie (github.com/Wolfeetech/FraWo).
#
# Verwender (vollstaendig, gemessen 05.10.):
#   ALERT   -> Alertmanager CT155: jetzt per credentials_file /etc/prometheus/servassi-hook.token
#   TASK    -> Odoo ir.config_parameter frawo_agent.servassi_webhook_secret (Addon frawo_agent)
#   CHATTER -> Odoo ir.actions.server 647 (webhook_url .../klausi-chatter/<secret>), /email-hook nutzt denselben
#
# Neue Werte werden hier erzeugt und nur per stdin an die Server gereicht - nie ausgegeben.
# Sicherungen: *.bak-20261005-rotation auf CT150 und CT155; Odoo-Altwerte ins Odoo-Log nicht geschrieben.
# Danach: Werte in Vaultwarden ablegen (Wolf) - Ablage siehe Odoo #1917.
set -euo pipefail
ANKER=root@10.1.0.92
CT150=root@10.1.0.31
neu() { python3 -c 'import secrets; print(secrets.token_urlsafe(24))' 2>/dev/null || python -c 'import secrets; print(secrets.token_urlsafe(24))'; }
A=$(neu); T=$(neu); C=$(neu)

echo "1/4 CT150: Handler-Env"
printf 'FRAWO_ALERT_SECRET=%s\nFRAWO_TASK_SECRET=%s\nFRAWO_CHATTER_SECRET=%s\n' "$A" "$T" "$C" | ssh -o BatchMode=yes "$CT150" '
set -e
f=/etc/frawo/ollama-chatter.env
cp -p "$f" "$f.bak-20261005-rotation"
python3 - "$f" <<"PY"
import sys
neu = dict(l.rstrip("\n").split("=", 1) for l in sys.stdin if "=" in l)
pfad = sys.argv[1]
zeilen = open(pfad).read().splitlines()
gesetzt = set()
for i, z in enumerate(zeilen):
    k = z.split("=", 1)[0]
    if k in neu:
        zeilen[i] = "%s=%s" % (k, neu[k]); gesetzt.add(k)
for k in neu:
    if k not in gesetzt:
        zeilen.append("%s=%s" % (k, neu[k]))
open(pfad, "w").write("\n".join(zeilen) + "\n")
print("   gesetzt:", sorted(neu))
PY
chmod 600 "$f"'

echo "2/4 CT155: Alertmanager auf credentials_file"
printf '%s' "$A" | ssh -o BatchMode=yes "$ANKER" 'pct exec 155 -- sh -c "
set -e
umask 077
cat > /etc/prometheus/servassi-hook.token
chown prometheus:prometheus /etc/prometheus/servassi-hook.token
chmod 0400 /etc/prometheus/servassi-hook.token
cp -p /etc/prometheus/alertmanager.yml /etc/prometheus/alertmanager.yml.bak-20261005-rotation
sed -i -E \"s#^(\s*)credentials: .*#\1credentials_file: /etc/prometheus/servassi-hook.token#\" /etc/prometheus/alertmanager.yml
amtool check-config /etc/prometheus/alertmanager.yml >/dev/null
systemctl reload prometheus-alertmanager
echo \"   alertmanager neu geladen\""'

echo "3/4 Odoo: Parameter + Aktion 647"
printf '%s\n%s\n' "$T" "$C" | ssh -o BatchMode=yes "$ANKER" 'pct exec 140 -- docker exec -i frawotech-odoo-1 sh -c "cat > /tmp/rot.txt; odoo shell -d FraWo_GbR --no-http --log-level=warn <<\"PY\"
t, c = open(\"/tmp/rot.txt\").read().split()
icp = env[\"ir.config_parameter\"].sudo()
icp.set_param(\"frawo_agent.servassi_webhook_secret\", t)
a = env[\"ir.actions.server\"].sudo().browse(647)
a.webhook_url = \"http://10.1.0.31:19001/klausi-chatter/\" + c
env.cr.commit()
print(\"   odoo: param + aktion 647 gesetzt\")
PY
rm -f /tmp/rot.txt"'

echo "4/4 CT150: Handler neu starten"
ssh -o BatchMode=yes "$CT150" 'systemctl restart odoo-webhook && sleep 2 && systemctl is-active odoo-webhook'
unset A T C
echo "fertig"
