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

# Git identity (persistent via volume)
git config --global user.name "ServAssi" 2>/dev/null || true
git config --global user.email "agent@frawo.tech" 2>/dev/null || true
git config --global init.defaultBranch main 2>/dev/null || true
git config --global pull.rebase false 2>/dev/null || true

# Clone FraWo repo if not present (needs GitHub deploy key)
if [ ! -d /root/.openclaw/FraWo/.git ]; then
  git clone git@github.com:Wolfeetech/FraWo.git /root/.openclaw/FraWo 2>/dev/null || true
fi

# gh CLI: auth via SSH (no PAT needed if deploy key is set)
if command -v gh >/dev/null 2>&1 && [ ! -f /root/.config/gh/config.yml ]; then
  gh config set git_protocol ssh 2>/dev/null || true
  gh config set prompt disabled 2>/dev/null || true
fi

if [ -n "${AZURACAST_API_KEY}" ] && ! openclaw mcp show azuracast >/dev/null 2>&1; then
  openclaw mcp add azuracast \
    --command python3 \
    --arg /app/mcp_azuracast.py \
    --env "AZURACAST_URL=${AZURACAST_URL:-http://10.1.0.38}" \
    --env "AZURACAST_API_KEY=${AZURACAST_API_KEY}" \
    --env "AZURACAST_STATION_ID=${AZURACAST_STATION_ID:-1}" \
    --no-probe || true
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
# WICHTIG: Dieser Cron ist READ-ONLY. Er darf KEINE Odoo-Stages ändern.
# Nur suchen und Telegram-Notification senden. Wolf entscheidet selbst.
if ! openclaw cron list 2>/dev/null | grep -q "odoo-agent-poll"; then
  openclaw cron add \
    --name odoo-agent-poll \
    --every 1h \
    --model 'anthropic/claude-haiku-4-5-20251001' \
    --thinking off \
    --session isolated \
    --timeout-seconds 30 \
    --announce \
    --channel telegram \
    --to 5924907152 \
    --message 'READONLY-TASK: Prüfe Odoo auf offene Tasks mit Tag DevOps-Agent (Tag-ID 75) und stage_id=1 (Backlog). Nutze NUR search_records auf project.task mit domain [["tag_ids","in",[75]],["stage_id","=",1]]. Kein Ergebnis = sofort stoppen, kein Output. Bei Ergebnissen: Sende NUR eine Telegram-Nachricht mit den Task-Namen und IDs. VERBOTEN: update_record, stage ändern, create_record, post_message. Du darfst AUSSCHLIESSLICH lesen und Telegram senden.' || true
fi

wait $GW_PID
