#!/bin/bash
docker exec -u postgres odoo_db_1 psql -d FraWo_GbR -c "UPDATE ir_ui_view SET active = false WHERE key IN ('website.homepage', 'website.contactus', 'website.user_custom_css');"
