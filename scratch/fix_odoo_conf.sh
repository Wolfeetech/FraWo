#!/bin/bash
cat <<EOF > /opt/homeserver2027/stacks/odoo/odoo.conf
[options]
admin_passwd = Winselhalle!!
smtp_server = smtp.strato.de
smtp_port = 587
smtp_user = webmaster@frawo-tech.de
smtp_password = Frawo0426!!
smtp_ssl = True
email_from = noreply@frawo-tech.de
from_filter = noreply@frawo-tech.de
proxy_mode = True
x_frame_options = False
EOF
cd /opt/homeserver2027/stacks/odoo
docker compose restart web
