#!/bin/bash
# Nextcloud absichern (Odoo #1930). Laeuft auf VM300.
set -euo pipefail
O="docker exec -u www-data nextcloud_app_1 php occ"
docker exec nextcloud_app_1 cp -p /var/www/html/config/config.php /var/www/html/config/config.php.bak-20261006
# Adressen: nur noch die echte Domain + LAN-IP
$O config:system:delete trusted_domains
$O config:system:set trusted_domains 0 --value=cloud.frawo.tech
$O config:system:set trusted_domains 1 --value=10.1.0.21
$O config:system:set trusted_domains 2 --value=localhost
$O config:system:set overwrite.cli.url --value=https://cloud.frawo.tech
# Vertrauenswuerdige Proxys: nur der Cloudflare-Tunnel (CT140), NICHT das IoT-Netz
$O config:system:delete trusted_proxies
$O config:system:set trusted_proxies 0 --value=10.1.0.112
$O config:system:set forwarded_for_headers 0 --value=HTTP_X_FORWARDED_FOR
$O config:system:set auth.bruteforce.protection.enabled --value=true --type=boolean
# Oeffentliche Links: nur mit Passwort, Standard-Ablauf 30 Tage
$O config:app:set core shareapi_enforce_links_password --value=yes
$O config:app:set core shareapi_default_expire_date --value=yes
$O config:app:set core shareapi_expire_after_n_days --value=30
# Zwei-Faktor fuer Admins erzwingen (Einrichtung wird beim naechsten Login verlangt)
$O twofactorauth:enforce --on --group=admin
$O config:system:get trusted_domains | tr '\n' ' '; echo
$O config:system:get trusted_proxies | tr '\n' ' '; echo
$O twofactorauth:enforce
