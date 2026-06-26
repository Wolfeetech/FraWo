#!/bin/sh
set -e

mkdir -p /root/.openclaw

if [ ! -f /root/.openclaw/openclaw.json ]; then
  cp /app/openclaw.default.json /root/.openclaw/openclaw.json
fi

# SSH-Key im persistenten Volume speichern
mkdir -p /root/.openclaw/ssh
chmod 700 /root/.openclaw/ssh
if [ ! -f /root/.openclaw/ssh/id_ed25519 ]; then
  ssh-keygen -t ed25519 -C "openclaw@frawo.tech" -f /root/.openclaw/ssh/id_ed25519 -N ""
fi
ln -sfn /root/.openclaw/ssh /root/.ssh

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
    --every 15m \
    --model 'anthropic/claude-haiku-4-5-20251001' \
    --thinking off \
    --session isolated \
    --timeout-seconds 90 \
    --announce \
    --channel telegram \
    --to 5924907152 \
    --message 'Prüfe Odoo auf neue Tasks im Backlog (stage_id=1) mit Tag DevOps-Agent (Tag-ID 75). Nutze search_records auf project.task mit domain [["tag_ids","in",[75]],["stage_id","=",1]]. Kein Task = sofort aufhören, KEIN Output. Wenn Tasks: sofort stage_id=3 + post_message Übernommen, erledigen, stage_id=6 + Telegram-Zusammenfassung.' || true
fi

wait $GW_PID
