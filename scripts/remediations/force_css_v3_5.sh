#!/bin/bash
# Force CSS v3.5 Update via Odoo Shell

CSS_FILE="/c/WORKSPACE/FraWo/Codex/website/frawo_custom_css.css"

# Read CSS content
CSS_CONTENT=$(cat "$CSS_FILE")

# Create Python command to update Odoo
PYTHON_CMD="import odoo; env = odoo.api.Environment(odoo.registry('FraWo_GbR'), 1, {}); website = env['website'].search([], limit=1); website.write({'custom_code_head': '''<style>${CSS_CONTENT}</style>'''}); env.cr.commit(); print('CSS updated!')"

# Execute on Odoo container via SSH
ssh root@100.69.179.87 "pct exec 220 -- su - odoo -s /bin/bash -c 'cd /usr/lib/python3/dist-packages && python3 -c \"$PYTHON_CMD\"'"
