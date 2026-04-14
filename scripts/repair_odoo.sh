cat <<EOF > /opt/homeserver2027/stacks/odoo/odoo.conf
[options]
smtp_server = smtp.strato.de
smtp_port = 587
smtp_user = webmaster@frawo-tech.de
smtp_password = Frawo0426!!
smtp_ssl = True
email_from = noreply@frawo-tech.de
from_filter = noreply@frawo-tech.de
proxy_mode = True
db_host = 172.21.0.2
db_user = odoo
db_password = odoo
db_name = FraWo_Live
list_db = True
EOF
docker restart odoo_web_1
