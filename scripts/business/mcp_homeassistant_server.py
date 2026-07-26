#!/usr/bin/env python3
"""
MCP Server for Home Assistant (FraWo Main HA - 10.1.0.40:8123)
Exposes Home Assistant REST API as MCP tools for use in Antigravity IDE.

Environment Variables / Config:
  HA_URL   - e.g. http://10.1.0.40:8123
  HA_TOKEN - Long-Lived Access Token
"""

import os
import sys
import json
import urllib.request
import urllib.parse
from pathlib import Path

# Load .env if present
_env_file = Path("C:/Users/StudioPC/.ai-tools-shared/.env")
if _env_file.exists():
    for line in _env_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, _, v = line.partition("=")
            os.environ.setdefault(k.strip(), v.strip())

HA_URL = os.environ.get("HA_URL", "http://10.1.0.40:8123")
HA_TOKEN = os.environ.get("HA_TOKEN", "")

def ha_request(endpoint, method="GET", data=None):
    url = f"{HA_URL}/api/{endpoint.lstrip('/')}"
    headers = {
        "Authorization": f"Bearer {HA_TOKEN}",
        "Content-Type": "application/json"
    }
    body = json.dumps(data).encode('utf-8') if data else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except Exception as e:
        return {"error": str(e)}

def handle_ha_get_states(args):
    states = ha_request("states")
    if isinstance(states, dict) and "error" in states:
        return f"HA API Error: {states['error']}"
    
    domain_filter = args.get("domain")
    lines = []
    for s in states:
        entity_id = s.get("entity_id", "")
        if domain_filter and not entity_id.startswith(domain_filter):
            continue
        name = s.get("attributes", {}).get("friendly_name", entity_id)
        state = s.get("state", "unknown")
        lines.append(f"{entity_id} | {name} | {state}")
    
    return "\n".join(lines[:100]) if lines else "No matching HA entities found."

def handle_ha_call_service(args):
    domain = args.get("domain")
    service = args.get("service")
    service_data = args.get("service_data", {})
    endpoint = f"services/{domain}/{service}"
    res = ha_request(endpoint, method="POST", data=service_data)
    return json.dumps(res, indent=2)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        print(f"Connecting to HA at {HA_URL}...")
        res = ha_request("")
        print("API Status:", res)
