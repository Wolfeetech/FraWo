#!/usr/bin/env bash
set -euo pipefail

payload="$(curl --silent --show-error --fail --max-time 10 http://portal.hs27.internal/status.json)"

PAYLOAD="${payload}" python3 - <<'PY'
import json
import os
import sys

data = json.loads(os.environ["PAYLOAD"])
services = data.get("services", [])
healthy = int(data.get("healthy_services", 0))
total = int(data.get("total_services", 0))
platform_core = data.get("platform_core", "unknown")

print(f"portal_status_platform_core={platform_core}")
print(f"portal_status_healthy_services={healthy}")
print(f"portal_status_total_services={total}")

for service in services:
    key = service.get("key", "unknown")
    status = service.get("status", "unknown")
    code = service.get("http_code", "000")
    print(f"portal_status_{key}={status}")
    print(f"portal_status_{key}_http={code}")

if total > 0 and healthy == total and platform_core == "ok":
    print("toolbox_portal_status_ready=yes")
    print("recommendation=portal_status_snapshot_is_green")
else:
    print("toolbox_portal_status_ready=no")
    print("recommendation=inspect_portal_status_snapshot_and_underlying_services")
PY
