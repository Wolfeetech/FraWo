#!/bin/sh
set -e

mkdir -p /root/.openclaw

if [ ! -f /root/.openclaw/openclaw.json ]; then
  cp /app/openclaw.default.json /root/.openclaw/openclaw.json
fi

if [ -n "${ODOO_API_KEY}" ] && ! openclaw mcp show odoo >/dev/null 2>&1; then
  openclaw mcp add odoo \
    --command /root/.local/bin/uvx \
    --arg mcp-server-odoo \
    --env "ODOO_URL=${ODOO_URL:-http://10.1.0.112:8069}" \
    --env "ODOO_DB=${ODOO_DB:-FraWo_GbR}" \
    --env "ODOO_API_KEY=${ODOO_API_KEY}" \
    --no-probe || true
fi

# Start gateway in background, register cron job once ready, then wait
openclaw gateway &
GW_PID=$!

# Wait for gateway to be ready (max 30s)
for i in $(seq 1 30); do
  if openclaw gateway health >/dev/null 2>&1; then
    break
  fi
  sleep 1
done

# Register Odoo poll cron job if not present
if ! openclaw cron list 2>/dev/null | grep -q "odoo-agent-poll"; then
  openclaw cron add \
    --name odoo-agent-poll \
    --every 3m \
    --message 'Prüfe Odoo auf offene Tasks mit Tag DevOps-Agent (Tag-ID 75, stage_id in [1,3]). Nutze das Odoo-MCP-Tool search_records auf project.task. Führe lösbare Tasks aus und melde Wolf per Telegram. Keine Tasks = kein Output.' \
    --channel telegram \
    --to 5924907152 \
    --timeout-seconds 240 \
    --session isolated \
    --announce || true
fi

wait $GW_PID
