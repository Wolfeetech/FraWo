#!/bin/bash
cat <<EOF > /opt/homeserver2027/stacks/odoo/odoo.conf
[options]
admin_passwd = ${ODOO_MASTER_PASSWD:?required}
smtp_server = smtp.strato.de
smtp_port = 587
smtp_user = webmaster@frawo-tech.de
smtp_password = ${SMTP_PASSWORD:?required}
smtp_ssl = True
email_from = noreply@frawo-tech.de
from_filter = noreply@frawo-tech.de
proxy_mode = True
x_frame_options = False
EOF
cd /opt/homeserver2027/stacks/odoo
docker compose restart web
