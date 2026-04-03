#!/usr/bin/env python3
"""Prepare the Stockenweiler pve host as a Tailscale subnet-router candidate."""

from __future__ import annotations

import json
import re
import subprocess
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_DIR = ROOT / "artifacts" / "stockenweiler_inventory"


def run(command: list[str], timeout: int = 30) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
    )


def ssh_stock_pve(command: str, timeout: int = 30) -> subprocess.CompletedProcess[str]:
    return run(
        [
            "ssh",
            "-o",
            "BatchMode=yes",
            "-o",
            "LogLevel=ERROR",
            "stock-pve",
            command,
        ],
        timeout=timeout,
    )


def parse_json(text: str) -> dict[str, object] | None:
    if not text.strip():
        return None
    try:
        return json.loads(text)
    except Exception:
        return None


def main() -> int:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)

    ensure_access = ROOT / "scripts" / "ensure_stockenweiler_toolbox_access.ps1"
    run(
        [
            "powershell",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(ensure_access),
        ],
        timeout=120,
    )

    baseline_script = "\n".join(
        [
            "cat > /etc/sysctl.d/90-stockenweiler-tailscale-router.conf <<'EOF'",
            "net.ipv4.ip_forward = 1",
            "net.ipv6.conf.all.forwarding = 1",
            "net.ipv6.conf.default.forwarding = 1",
            "EOF",
            "cat > /etc/systemd/system/stockenweiler-tailscale-vmbr0-gro.service <<'EOF'",
            "[Unit]",
            "Description=Persist vmbr0 UDP GRO tuning for Tailscale subnet routing",
            "After=network-online.target",
            "Wants=network-online.target",
            "",
            "[Service]",
            "Type=oneshot",
            "ExecStart=/usr/sbin/ethtool -K vmbr0 rx-udp-gro-forwarding on rx-gro-list off",
            "RemainAfterExit=yes",
            "",
            "[Install]",
            "WantedBy=multi-user.target",
            "EOF",
            "sysctl --system >/tmp/stockenweiler-sysctl.log 2>&1",
            "systemctl daemon-reload",
            "systemctl enable --now stockenweiler-tailscale-vmbr0-gro.service >/tmp/stockenweiler-gro.log 2>&1",
        ]
    )
    ssh_stock_pve(baseline_script, timeout=40)

    status_before = ssh_stock_pve("timeout 8 tailscale status --json", timeout=20)
    prefs_before = ssh_stock_pve("timeout 8 tailscale debug prefs", timeout=20)
    status_before_json = parse_json(status_before.stdout or "") or {}
    prefs_before_json = parse_json(prefs_before.stdout or "") or {}

    backend_state_before = str(status_before_json.get("BackendState", "") or "")
    tailnet_before = str(((status_before_json.get("CurrentTailnet") or {}).get("MagicDNSSuffix", "") or ""))
    auth_url = str(status_before_json.get("AuthURL", "") or "")
    advertise_routes_before = [str(x) for x in (prefs_before_json.get("AdvertiseRoutes") or [])]

    action_taken = "noop"
    up_result = subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr="")
    if backend_state_before == "Running" and tailnet_before == "tail150400.ts.net":
        action_taken = "already_joined_reused"
    elif auth_url:
        action_taken = "auth_pending_reused"
    else:
        action_taken = "tailscale_up_attempted"
        up_result = ssh_stock_pve(
            "timeout 25 tailscale up --reset --hostname stockenweiler-pve --accept-dns=false --ssh "
            "--advertise-routes=192.168.178.0/24 --json --timeout=20s",
            timeout=40,
        )

    status_after = ssh_stock_pve("timeout 8 tailscale status --json", timeout=20)
    prefs_after = ssh_stock_pve("timeout 8 tailscale debug prefs", timeout=20)

    status_after_json = parse_json(status_after.stdout or "") or {}
    prefs_after_json = parse_json(prefs_after.stdout or "") or {}

    up_text = (up_result.stdout or "") + (up_result.stderr or "")
    if not auth_url:
        match = re.search(r'https://login\.tailscale\.com/\S+', up_text)
        if match:
            auth_url = match.group(0)
    if not auth_url:
        auth_url = str(status_after_json.get("AuthURL", "") or "")

    backend_state_after = str(status_after_json.get("BackendState", "") or "")
    tailnet_after = str(((status_after_json.get("CurrentTailnet") or {}).get("MagicDNSSuffix", "") or ""))
    advertise_routes_after = [str(x) for x in (prefs_after_json.get("AdvertiseRoutes") or [])]

    payload = {
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "target": "stock-pve",
        "action_taken": action_taken,
        "backend_state_before": backend_state_before,
        "backend_state_after": backend_state_after,
        "current_tailnet_before": tailnet_before,
        "current_tailnet_after": tailnet_after,
        "advertise_routes_before": advertise_routes_before,
        "advertise_routes_after": advertise_routes_after,
        "auth_url": auth_url,
        "status_before_raw": (status_before.stdout or "") + (status_before.stderr or ""),
        "up_output_raw": up_text,
        "status_after_raw": (status_after.stdout or "") + (status_after.stderr or ""),
    }

    json_path = ARTIFACT_DIR / "latest_tailscale_bridge_prepare.json"
    md_path = ARTIFACT_DIR / "latest_tailscale_bridge_prepare.md"

    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")

    md_lines = [
        "# Stockenweiler Tailscale Bridge Prepare",
        "",
        f"- generated_at: {payload['generated_at']}",
        "- target: stock-pve",
        f"- action_taken: {action_taken}",
        f"- backend_state_before: {backend_state_before or '-'}",
        f"- backend_state_after: {backend_state_after or '-'}",
        f"- current_tailnet_before: {tailnet_before or '-'}",
        f"- current_tailnet_after: {tailnet_after or '-'}",
        f"- auth_url: {auth_url}",
        "",
        "## Notes",
        "",
        "- Stockenweiler pve is prepared as a Tailscale subnet-router candidate for 192.168.178.0/24.",
        "- IPv4/IPv6 forwarding baseline and vmbr0 UDP GRO tuning were applied before the rehome step.",
        "- The WireGuard recovery path via stock-pve remains the fallback while Tailscale rehome is pending.",
        "- The script is idempotent: it reuses an existing login or joined state instead of blindly resetting a working node.",
        "",
        "## tailscale up output",
        "",
        "```text",
        payload["up_output_raw"].rstrip(),
        "```",
        "",
        "## tailscale status after",
        "",
        "```text",
        payload["status_after_raw"].rstrip(),
        "```",
    ]
    md_path.write_text("\n".join(md_lines) + "\n", encoding="utf-8")

    print(f"stockenweiler_tailscale_bridge_prepare_report={md_path.as_posix()}")
    print(f"stockenweiler_tailscale_bridge_prepare_json={json_path.as_posix()}")
    print(f"stockenweiler_tailscale_bridge_prepare_auth_url={auth_url}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
