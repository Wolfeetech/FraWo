#!/usr/bin/env bash
set -euo pipefail

SMTP_PASSWORD="${ODOO_SMTP_PASSWORD:?Setze ODOO_SMTP_PASSWORD vor dem Start.}"
DB_PASSWORD="${ODOO_DB_PASSWORD:?Setze ODOO_DB_PASSWORD vor dem Start.}"

cat <<EOF > /opt/homeserver2027/stacks/odoo/odoo.conf
[options]
smtp_server = smtp.strato.de
smtp_port = 587
smtp_user = webmaster@frawo-tech.de
smtp_password = ${SMTP_PASSWORD}
smtp_ssl = True
email_from = noreply@frawo-tech.de
from_filter = noreply@frawo-tech.de
proxy_mode = True
db_host = db
db_user = odoo
db_password = ${DB_PASSWORD}
db_name = FraWo_Live
list_db = True
EOF
docker restart odoo_web_1
