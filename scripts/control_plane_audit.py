#!/usr/bin/env python3
"""Collect a reproducible control-plane status snapshot for the StudioPC workspace."""

from __future__ import annotations

import json
import subprocess
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_DIR = ROOT / "artifacts" / "control_plane"
REPORT_JSON = ARTIFACT_DIR / "latest_report.json"
REPORT_MD = ARTIFACT_DIR / "latest_report.md"


def run_ps(command: str) -> tuple[int, str, str]:
    completed = subprocess.run(
        ["powershell", "-NoProfile", "-Command", command],
        capture_output=True,
        text=True,
        check=False,
    )
    return completed.returncode, completed.stdout.strip(), completed.stderr.strip()


def run_cmd(argv: list[str]) -> tuple[int, str, str]:
    completed = subprocess.run(
        argv,
        capture_output=True,
        text=True,
        check=False,
    )
    return completed.returncode, completed.stdout.strip(), completed.stderr.strip()


def get_process_rows() -> list[dict[str, str]]:
    code, out, _ = run_ps(
        r"""
$threshold = (Get-Date).AddHours(-1)
Get-Process |
  Where-Object { $_.ProcessName -in @('ssh','powershell','pyrefly') } |
  ForEach-Object {
    $created = $null
    $commandLine = $null
    try { $created = $_.StartTime } catch {}
    try { $commandLine = (Get-CimInstance Win32_Process -Filter ("ProcessId = " + $_.Id)).CommandLine } catch {}
    [PSCustomObject]@{
      name = ($_.ProcessName + '.exe')
      process_id = $_.Id
      creation_date = if ($created) { $created.ToString('s') } else { '' }
      older_than_1h = if ($created) { $created -lt $threshold } else { $false }
      command_line = $commandLine
    }
  } | ConvertTo-Json -Depth 4
"""
    )
    if code != 0 or not out:
        return []
    parsed = json.loads(out)
    if isinstance(parsed, dict):
        return [parsed]
    return parsed


def get_services() -> list[dict[str, str]]:
    code, out, _ = run_ps(
        r"""
Get-Service |
  Where-Object { $_.Name -like 'WireGuard*' -or $_.Name -like 'Tailscale*' } |
  Select-Object @{Name='Status';Expression={$_.Status.ToString()}},Name,DisplayName |
  ConvertTo-Json -Depth 3
"""
    )
    if code != 0 or not out:
        return []
    parsed = json.loads(out)
    if isinstance(parsed, dict):
        return [parsed]
    return parsed


def get_tailscale_summary() -> dict[str, object]:
    code, out, err = run_cmd(["tailscale", "status", "--json"])
    summary: dict[str, object] = {
        "cli_ok": code == 0,
        "stderr": err,
        "backend_state": "unknown",
        "self_dns_name": "",
        "self_ips": [],
        "stockenweiler_route_present": False,
        "peer_count": 0,
        "route_warning_present": False,
    }
    if code != 0 or not out:
        return summary
    payload = json.loads(out)
    self_info = payload.get("Self", {})
    peers = payload.get("Peer", {})
    health = payload.get("Health", []) or []
    summary["backend_state"] = self_info.get("Online") and "Running" or "Offline"
    summary["self_dns_name"] = self_info.get("DNSName", "")
    summary["self_ips"] = self_info.get("TailscaleIPs", []) or []
    summary["peer_count"] = len(peers)
    summary["route_warning_present"] = any("accept-routes is false" in str(item) for item in health)
    for peer in peers.values():
        for route in peer.get("PrimaryRoutes", []) or []:
            if str(route) == "192.168.178.0/24":
                summary["stockenweiler_route_present"] = True
    return summary


def get_ssh_probe() -> dict[str, object]:
    code, out, err = run_cmd(
        ["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=8", "stock-pve", "hostname; pveversion | head -1"]
    )
    lines = [line.strip() for line in out.splitlines() if line.strip()]
    return {
        "status": "reachable" if code == 0 else "unreachable",
        "stdout": lines,
        "stderr": err,
    }


def build_report() -> dict[str, object]:
    processes = get_process_rows()
    services = get_services()
    tailscale = get_tailscale_summary()
    ssh_probe = get_ssh_probe()

    process_counts = Counter(row["name"] for row in processes)
    stale_ssh = [
        row for row in processes
        if row["name"] == "ssh.exe" and row.get("older_than_1h")
    ]
    stale_mail_pwsh = [
        row for row in processes
        if row["name"] == "powershell.exe" and "prove_strato_mail_model.ps1" in (row.get("command_line") or "")
    ]
    pyrefly_process_present = any(row["name"] == "pyrefly.exe" for row in processes)
    wg_vpn_running = any(
        service.get("Name") == "WireGuardTunnel$VPN" and service.get("Status") == "Running"
        for service in services
    )

    primary_paths = {
        "anker_admin_path": "LAN + SSH aliases via ~/.ssh/hs27_ops_ed25519",
        "stockenweiler_admin_path": "ssh stock-pve via toolbox-backed userspace WireGuard",
        "stockenweiler_target_path": "Tailscale subnet-router on stockenweiler-pve for 192.168.178.0/24",
    }

    return {
        "generated_at": datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M:%S"),
        "workspace_pyrefly_disabled": True,
        "pyrefly_process_present": pyrefly_process_present,
        "process_counts": dict(process_counts),
        "stale_ssh_count": len(stale_ssh),
        "stale_mail_powershell_count": len(stale_mail_pwsh),
        "tailscale": tailscale,
        "services": services,
        "wireguard_vpn_running": wg_vpn_running,
        "ssh_stock_pve": ssh_probe,
        "primary_paths": primary_paths,
        "observations": [
            "Primary Stockenweiler admin path is currently ssh stock-pve via toolbox-backed userspace WireGuard.",
            "Target professional bridge remains Tailscale subnet routing, not permanent dependence on the local stale Windows WireGuard tunnel.",
            "Workspace disables Pyrefly language services to avoid editor-side notify-file spam from a dead client.",
        ],
    }


def write_outputs(report: dict[str, object]) -> None:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_JSON.write_text(json.dumps(report, indent=2), encoding="utf-8")

    md = [
        "# Control Plane Audit",
        "",
        f"- generated_at: `{report['generated_at']}`",
        f"- workspace_pyrefly_disabled: `{str(report['workspace_pyrefly_disabled']).lower()}`",
        f"- pyrefly_process_present: `{str(report['pyrefly_process_present']).lower()}`",
        f"- stale_ssh_count: `{report['stale_ssh_count']}`",
        f"- stale_mail_powershell_count: `{report['stale_mail_powershell_count']}`",
        f"- tailscale_backend_state: `{report['tailscale']['backend_state']}`",
        f"- tailscale_stockenweiler_route_present: `{report['tailscale']['stockenweiler_route_present']}`",
        f"- ssh_stock_pve: `{report['ssh_stock_pve']['status']}`",
        f"- wireguard_vpn_running: `{str(report['wireguard_vpn_running']).lower()}`",
        "",
        "## Primary Paths",
        "",
        f"- anker_admin_path: `{report['primary_paths']['anker_admin_path']}`",
        f"- stockenweiler_admin_path: `{report['primary_paths']['stockenweiler_admin_path']}`",
        f"- stockenweiler_target_path: `{report['primary_paths']['stockenweiler_target_path']}`",
        "",
        "## Observations",
        "",
    ]
    for item in report["observations"]:
        md.append(f"- {item}")

    REPORT_MD.write_text("\n".join(md) + "\n", encoding="utf-8")


def main() -> int:
    report = build_report()
    write_outputs(report)
    print(f"report_json={REPORT_JSON}")
    print(f"report_md={REPORT_MD}")
    print(f"stale_ssh_count={report['stale_ssh_count']}")
    print(f"pyrefly_process_present={str(report['pyrefly_process_present']).lower()}")
    print(f"stock_pve_status={report['ssh_stock_pve']['status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
