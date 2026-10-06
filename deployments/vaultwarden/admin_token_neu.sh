#!/usr/bin/env bash
# Vaultwarden: neues Admin-Token setzen und das alte agent@-Konto (07/2026, Passwort unbekannt) loeschen.
# Odoo #1931. Von Wolf am StudioPC zu starten:
#   ! bash C:/Users/StudioPC/FraWo/deployments/vaultwarden/admin_token_neu.sh
# Das neue Token landet nur in der Desktop-Datei "Vaultwarden-Admin-Token.txt" (dann in Vaultwarden ablegen).
set -euo pipefail
HIER=$(cd "$(dirname "$0")" && pwd)
TOK=$(python -c "import secrets; print(secrets.token_urlsafe(36))")
scp -q "$HIER/vw_admin_token_im_ct108.sh" root@10.1.0.92:/tmp/vw_admin.sh
printf '%s\n' "$TOK" | ssh -o BatchMode=yes root@10.1.0.92 'pct push 108 /tmp/vw_admin.sh /root/vw_admin.sh && pct exec 108 -- bash /root/vw_admin.sh; rm -f /tmp/vw_admin.sh; pct exec 108 -- rm -f /root/vw_admin.sh'
printf 'Vaultwarden Admin-Token (neu gesetzt am %s, Odoo #1931)\r\n\r\nAdresse: https://vault.frawo.tech/admin\r\nToken:   %s\r\n\r\nBitte in Vaultwarden ablegen (Eintrag "Vaultwarden Admin-Token") und diese Datei loeschen.\r\n' "$(date +%d.%m.%Y)" "$TOK" > "/c/Users/StudioPC/Desktop/Vaultwarden-Admin-Token.txt"
unset TOK
curl -s -m10 -o /dev/null -w "vault.frawo.tech: %{http_code}\n" https://vault.frawo.tech/alive
echo "Fertig. Neues Token: Desktop-Datei Vaultwarden-Admin-Token.txt"
