cd /opt/homeserver2027/stacks/odoo
docker-compose exec -T db psql -U odoo -d FraWo_GbR -c "SELECT key FROM ir_ui_view WHERE key LIKE '%custom%' OR key LIKE '%css%'"
