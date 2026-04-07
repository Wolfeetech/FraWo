qm guest exec 220 -- docker exec odoo_db_1 psql -U odoo -d FraWo_GbR -c "DELETE FROM ir_attachment WHERE url LIKE '/web/content/%' OR name ILIKE '%assets%';"
qm guest exec 220 -- docker restart odoo_web_1
