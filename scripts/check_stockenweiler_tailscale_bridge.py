#!/usr/bin/env python3
"""Check the current Tailscale bridge readiness for Stockenweiler."""

from __future__ import annotations

import json
import subprocess
from datetime import datetime
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT_DIR / "artifacts" / "stockenweiler_inventory"


def run(command: list[str], timeout: int = 20) -> dict[str, object]:
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
        )
        return {
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "command": command,
        }
    except Exception as exc:
        return {
            "returncode": 999,
            "stdout": "",
            "stderr": str(exc),
            "command": command,
        }


def parse_json_output(result: dict[str, object]) -> dict[str, object] | None:
    if result["returncode"] != 0 or not str(result["stdout"]).strip():
        return None
    try:
        return json.loads(str(result["stdout"]))
    except Exception:
        return None


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    local_status = parse_json_output(run(["tailscale", "status", "--json"], timeout=20))
    local_prefs = parse_json_output(run(["tailscale", "debug", "prefs"], timeout=20))
    remote_status = parse_json_output(
        run(
            [
                "ssh",
                "-o",
                "BatchMode=yes",
                "-o",
                "LogLevel=ERROR",
                "stock-pve",
                "timeout 8 tailscale status --json",
            ],
            timeout=20,
        )
    )
    remote_prefs = parse_json_output(
        run(
            [
                "ssh",
                "-o",
                "BatchMode=yes",
                "-o",
                "LogLevel=ERROR",
                "stock-pve",
                "timeout 8 tailscale debug prefs",
            ],
            timeout=20,
        )
    )

    local_routes = []
    local_route_present = False
    local_accept_routes_enabled = bool((local_prefs or {}).get("RouteAll", False))
    if local_status:
        for peer in (local_status.get("Peer") or {}).values():
            dns_name = str(peer.get("DNSName", "")).rstrip(".")
            for route in peer.get("PrimaryRoutes") or []:
                local_routes.append(f"{route} via {dns_name or 'unknown-peer'}")
                if route == "192.168.178.0/24":
                    local_route_present = True

    auth_url = ""
    backend_state = ""
    current_tailnet = ""
    advertised_routes = []
    remote_route_configured = False
    if remote_status:
        backend_state = str(remote_status.get("BackendState", ""))
        auth_url = str(remote_status.get("AuthURL", "") or "")
        tailnet = remote_status.get("CurrentTailnet") or {}
        current_tailnet = str(tailnet.get("MagicDNSSuffix", "") or "")
        self_data = remote_status.get("Self") or {}
        advertised_routes = [str(x) for x in (self_data.get("AllowedIPs") or []) if str(x).startswith("192.168.")]
    if remote_prefs:
        remote_route_configured = "192.168.178.0/24" in [str(x) for x in (remote_prefs.get("AdvertiseRoutes") or [])]

    if backend_state == "Running" and current_tailnet == "tail150400.ts.net" and local_route_present:
        route_health = "ready"
        bridge_state = "ready"
    elif backend_state == "Running" and current_tailnet == "tail150400.ts.net" and remote_route_configured and not local_route_present:
        route_health = "approval_pending"
        bridge_state = "route_approval_pending"
    elif auth_url or backend_state == "NeedsLogin":
        route_health = "login_pending"
        bridge_state = "login_pending"
    else:
        route_health = "pending"
        bridge_state = "pending"

    payload = {
        "generated_at": generated_at,
        "local_stockenweiler_route_present": local_route_present,
        "local_visible_primary_routes": local_routes,
        "local_accept_routes_enabled": local_accept_routes_enabled,
        "remote_backend_state": backend_state,
        "remote_current_tailnet": current_tailnet,
        "remote_auth_url": auth_url,
        "remote_route_configured": remote_route_configured,
        "remote_advertised_routes": advertised_routes,
        "bridge_state": bridge_state,
        "route_health": route_health,
    }

    json_path = OUTPUT_DIR / "latest_tailscale_bridge_check.json"
    md_path = OUTPUT_DIR / "latest_tailscale_bridge_check.md"
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")

    lines = [
        "# Stockenweiler Tailscale Bridge Check",
        "",
        f"- generated_at: `{generated_at}`",
        f"- bridge_state: `{bridge_state}`",
        f"- remote_backend_state: `{backend_state or '-'}`",
        f"- remote_current_tailnet: `{current_tailnet or '-'}`",
        f"- local_stockenweiler_route_present: `{local_route_present}`",
        f"- local_accept_routes_enabled: `{local_accept_routes_enabled}`",
        f"- remote_route_configured: `{remote_route_configured}`",
        "",
        "## Observations",
        "",
    ]
    if auth_url:
        lines.append(f"- Login still pending via `{auth_url}`.")
    if backend_state == "Running":
        lines.append("- Stockenweiler pve Tailscale backend is running.")
    elif backend_state:
        lines.append(f"- Stockenweiler pve Tailscale backend is `{backend_state}`.")
    else:
        lines.append("- Stockenweiler pve Tailscale backend state could not be read.")
    if bridge_state == "route_approval_pending":
        lines.append("- stockenweiler-pve is already joined to tail150400 and configured to advertise `192.168.178.0/24`, but the subnet route is not visible locally yet.")
        lines.append("- The remaining blocker is route approval/distribution in Tailscale admin, not another login on stockenweiler-pve.")
    if local_routes:
        for item in local_routes:
            lines.append(f"- visible local primary route: `{item}`")
    else:
        lines.append("- No Stockenweiler route is visible yet in the local tailnet route table.")

    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"stockenweiler_tailscale_bridge_check_report={md_path.as_posix()}")
    print(f"stockenweiler_tailscale_bridge_check_json={json_path.as_posix()}")
    print(f"stockenweiler_tailscale_bridge_state={bridge_state}")
    print(f"stockenweiler_tailscale_bridge_auth_url={auth_url}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
