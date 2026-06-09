cd /opt/homeserver2027/stacks/odoo
docker-compose exec -T db psql -U odoo -d FraWo_GbR -c "SELECT id, name, domain FROM website"
