import xmlrpc.client
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SSH_CONFIG_PATH = ROOT / "Codex" / "ssh_config"
DEFAULT_TOOLBOX_FRONTDOOR_IP = "100.82.26.53"


def current_toolbox_frontdoor_ip() -> str:
    try:
        text = SSH_CONFIG_PATH.read_text(encoding="utf-8")
    except OSError:
        return DEFAULT_TOOLBOX_FRONTDOOR_IP

    in_toolbox_block = False
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        lower = line.lower()
        if lower.startswith("host "):
            hosts = line.split()[1:]
            in_toolbox_block = "toolbox" in hosts
            continue
        if in_toolbox_block and lower.startswith("hostname "):
            parts = line.split(None, 1)
            if len(parts) == 2 and parts[1].strip():
                return parts[1].strip()
    return DEFAULT_TOOLBOX_FRONTDOOR_IP


URL = f"http://{current_toolbox_frontdoor_ip()}:8444"

common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(URL))
try:
    dbs = common.list()
    print(f"Databases found: {dbs}")
except Exception as e:
    print(f"Error listing databases: {e}")
    sys.exit(1)
