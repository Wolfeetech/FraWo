#!/usr/bin/env bash
# Hermes-Ausweichkette (Odoo #1966, Wolf 07.10.): Codex -> Claude (ueber GitHub Copilot) -> Sparbetrieb.
# Von Wolf am StudioPC:  ! bash C:/Users/StudioPC/FraWo/deployments/hermes/copilot_stufe_einrichten.sh
set -uo pipefail
ssh -o BatchMode=yes root@10.1.0.227 'pct exec 160 -- su - hermes -c "
set -e
gh auth status 2>&1 | grep -E \"Logged in|not logged\" | head -1
C=~/.hermes/config.yaml
cp -p \$C \$C.bak-20261007c
if ! grep -q \"provider: copilot\" \$C; then
  sed -i \"s#^fallback_providers:#fallback_providers:\n  - provider: copilot\n    model: claude-sonnet-5#\" \$C
fi
export HERMES_DISABLE_TELEMETRY=1
~/.local/bin/hermes fallback list 2>&1 | grep -E \"Primary|^ +[0-9]\\.\"
echo \"--- Test Claude ueber Copilot:\"
cd ~/FraWo && timeout 180 ~/.local/bin/hermes --provider copilot -m claude-sonnet-5 -z \"Antworte exakt mit: Claude via Copilot OK\" 2>&1 | tail -1
"'
ssh -o BatchMode=yes root@10.1.0.227 'pct exec 160 -- systemctl restart hermes-gateway && echo "Hermes neu gestartet"'
