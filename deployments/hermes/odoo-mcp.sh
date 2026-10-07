#!/bin/sh
# Odoo-MCP fuer Hermes (#1965): Schluessel nur aus ~/.hermes/.env, nie in config.yaml oder Prozessargumenten.
ODOO_API_KEY=$(sed -n "s/^ODOO_API_KEY=//p" $HOME/.hermes/.env)
export ODOO_API_KEY ODOO_URL=http://10.1.0.112:8069 ODOO_DB=FraWo_GbR
exec $HOME/.hermes/tools/uv-0.12.3-linux-x64/uv tool run mcp-server-odoo
