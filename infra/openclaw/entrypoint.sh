#!/bin/sh
set -e

mkdir -p /root/.openclaw

# Seed config on first boot (volume is empty)
if [ ! -f /root/.openclaw/openclaw.json ]; then
  cp /app/openclaw.default.json /root/.openclaw/openclaw.json
fi

# Add Odoo MCP server on first boot (idempotent)
if [ -n "${ODOO_API_KEY}" ] && ! openclaw mcp show odoo >/dev/null 2>&1; then
  openclaw mcp add odoo \
    --command /root/.local/bin/uvx \
    --arg mcp-server-odoo \
    --env "ODOO_URL=${ODOO_URL:-http://10.1.0.112:8069}" \
    --env "ODOO_DB=${ODOO_DB:-FraWo_GbR}" \
    --env "ODOO_API_KEY=${ODOO_API_KEY}" \
    --no-probe || true
fi

exec openclaw gateway
