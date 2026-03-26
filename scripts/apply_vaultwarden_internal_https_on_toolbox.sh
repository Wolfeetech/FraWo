#!/usr/bin/env bash
set -euo pipefail

STACK_DIR="/opt/homeserver2027/stacks/toolbox-network"
CADDYFILE="${STACK_DIR}/Caddyfile"
ADGUARD="${STACK_DIR}/adguard/conf/AdGuardHome.yaml"

python3 - <<'PY'
from pathlib import Path

caddy = Path('/opt/homeserver2027/stacks/toolbox-network/Caddyfile')
cfg = caddy.read_text()
block = """
https://vault.hs27.internal {
  tls internal
  reverse_proxy 192.168.2.26:8080
}
"""
if 'https://vault.hs27.internal' not in cfg:
    if not cfg.endswith('\n'):
        cfg += '\n'
    cfg += '\n' + block.strip() + '\n'
    caddy.write_text(cfg)

adguard = Path('/opt/homeserver2027/stacks/toolbox-network/adguard/conf/AdGuardHome.yaml')
text = adguard.read_text()
needle = "  - domain: vault.hs27.internal\n    answer: 192.168.2.20\n"
if 'domain: vault.hs27.internal' not in text:
    marker = "  - domain: radio.hs27.internal\n    answer: 192.168.2.20\n"
    if marker in text:
        text = text.replace(marker, marker + needle)
        adguard.write_text(text)
PY

systemctl restart homeserver-compose-toolbox-network.service
sleep 5
curl -kI https://vault.hs27.internal
curl -fsS http://192.168.2.26:8080/alive
