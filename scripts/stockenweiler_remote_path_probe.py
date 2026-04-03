#!/usr/bin/env python3
"""Collect a read-only remote-path truth snapshot for Stockenweiler."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from datetime import datetime
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
OUTPUT_ROOT = ROOT_DIR / "artifacts" / "stockenweiler_inventory"


def run_command(command: list[str], timeout: int = 20) -> dict[str, object]:
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
    except Exception as exc:  # pragma: no cover - environment dependent
        return {
            "returncode": 999,
            "stdout": "",
            "stderr": str(exc),
            "command": command,
        }


def load_tailscale_status() -> dict[str, object]:
    result = run_command(["tailscale", "status", "--json"], timeout=20)
    if result["returncode"] != 0:
        return {
            "status_ok": False,
            "backend_state": "",
            "health": [],
            "self_dns_name": "",
            "self_ips": [],
            "visible_primary_routes": [],
            "stockenweiler_subnet_route_present": False,
            "error": str(result["stderr"]).strip() or "tailscale status failed",
        }

    data = json.loads(str(result["stdout"]))
    visible_primary_routes: list[str] = []
    stockenweiler_subnet_route_present = False
    for peer in data.get("Peer", {}).values():
        dns_name = str(peer.get("DNSName", "")).rstrip(".")
        for route in peer.get("PrimaryRoutes") or []:
            rendered = f"{route} via {dns_name or 'unknown-peer'}"
            visible_primary_routes.append(rendered)
            if route == "192.168.178.0/24":
                stockenweiler_subnet_route_present = True

    return {
        "status_ok": True,
        "backend_state": data.get("BackendState", ""),
        "health": data.get("Health", []) or [],
        "self_dns_name": data.get("Self", {}).get("DNSName", ""),
        "self_ips": data.get("Self", {}).get("TailscaleIPs", []) or [],
        "visible_primary_routes": visible_primary_routes,
        "stockenweiler_subnet_route_present": stockenweiler_subnet_route_present,
        "error": "",
    }


def load_tailscale_prefs() -> dict[str, object]:
    result = run_command(["tailscale", "debug", "prefs"], timeout=20)
    if result["returncode"] != 0:
        return {"prefs_ok": False, "route_all": None, "corp_dns": None, "error": str(result["stderr"]).strip()}
    data = json.loads(str(result["stdout"]))
    return {
        "prefs_ok": True,
        "route_all": data.get("RouteAll"),
        "corp_dns": data.get("CorpDNS"),
        "error": "",
    }


def probe_ssh(target: str) -> dict[str, object]:
    result = run_command(
        [
            "ssh",
            "-o",
            "BatchMode=yes",
            "-o",
            "StrictHostKeyChecking=no",
            "-o",
            "ConnectTimeout=8",
            target,
            "echo stockenweiler_remote_probe_ok",
        ],
        timeout=20,
    )
    status = "reachable" if result["returncode"] == 0 else "unreachable"
    return {
        "target": target,
        "status": status,
        "stdout": str(result["stdout"]).strip(),
        "stderr": str(result["stderr"]).strip(),
        "returncode": result["returncode"],
    }


def read_text(path: Path) -> str:
    for encoding in ("utf-8", "utf-16", "utf-16-le", "cp1252"):
        try:
            return path.read_text(encoding=encoding)
        except Exception:
            continue
    return path.read_text(encoding="utf-8", errors="replace")


def parse_anydesk(base_dir: Path) -> dict[str, object]:
    appdata_dir = Path.home() / "AppData" / "Roaming" / "AnyDesk"
    programdata_dir = Path.home().drive and Path(Path.home().drive + "\\") / "ProgramData" / "AnyDesk"
    if not appdata_dir.exists():
        return {
            "installed": False,
            "roster_ids": [],
            "permission_profile_ids": [],
            "history_ids": [],
            "candidate_remote_ids": [],
        }

    roster_ids: set[str] = set()
    permission_profile_ids: set[str] = set()
    history_ids: set[str] = set()

    user_conf = appdata_dir / "user.conf"
    if user_conf.exists():
        text = read_text(user_conf)
        match = re.search(r"^ad\.roster\.items=(.+)$", text, re.MULTILINE)
        if match:
            for item in match.group(1).split(";"):
                number = item.split(",", 1)[0].strip()
                if re.fullmatch(r"\d{6,}", number):
                    roster_ids.add(number)
        match = re.search(r"^ad\.security\.permission_profiles\.address_to_profile=(.+)$", text, re.MULTILINE)
        if match:
            for item in match.group(1).split(";"):
                number = item.split(":", 1)[0].strip()
                if re.fullmatch(r"\d{6,}", number):
                    permission_profile_ids.add(number)

    trace_paths = [
        appdata_dir / "ad.trace",
        Path(str(programdata_dir)) / "connection_trace.txt",
        Path(str(programdata_dir)) / "ad_svc.trace",
    ]
    for path in trace_paths:
        if not path.exists():
            continue
        text = read_text(path)
        for _, number in re.findall(r"(Token|User|Passwd)\s+(\d{6,})", text):
            history_ids.add(number)
        for number in re.findall(r"request: .* \((\d{6,})\)", text):
            history_ids.add(number)
        for number in re.findall(r'Connecting to "?(\d{6,})"?', text):
            history_ids.add(number)

    candidate_remote_ids = sorted(roster_ids | permission_profile_ids | history_ids)
    return {
        "installed": True,
        "roster_ids": sorted(roster_ids),
        "permission_profile_ids": sorted(permission_profile_ids),
        "history_ids": sorted(history_ids),
        "candidate_remote_ids": candidate_remote_ids,
    }


def build_observations(
    tailscale_status: dict[str, object],
    tailscale_prefs: dict[str, object],
    ssh_probe: dict[str, object],
    anydesk: dict[str, object],
) -> list[str]:
    observations: list[str] = []
    if tailscale_status.get("backend_state"):
        observations.append(f"Tailscale backend is `{tailscale_status['backend_state']}` on StudioPC.")
    if tailscale_prefs.get("route_all") is False:
        observations.append("StudioPC currently has `RouteAll=false`, so advertised subnet routes are not automatically accepted.")
    visible_routes = tailscale_status.get("visible_primary_routes", []) or []
    if visible_routes:
        observations.append(f"Visible Tailscale primary routes are currently limited to: {', '.join(visible_routes)}.")
    else:
        observations.append("No Tailscale primary routes are currently visible in local status.")
    if not tailscale_status.get("stockenweiler_subnet_route_present"):
        observations.append("No Stockenweiler subnet route `192.168.178.0/24` is currently visible in local Tailscale status.")
    if ssh_probe.get("status") == "reachable":
        observations.append(f"SSH to `{ssh_probe['target']}` is currently reachable from StudioPC.")
    else:
        observations.append(f"Direct SSH to `{ssh_probe['target']}` is still unreachable from the current workstation context.")
    if anydesk.get("installed"):
        observations.append(
            f"AnyDesk is installed locally and exposes `{len(anydesk.get('candidate_remote_ids', []))}` recovered remote-ID candidates, but they are not yet mapped to live Stockenweiler device names."
        )
    return observations


def markdown_report(
    generated_at: str,
    tailscale_status: dict[str, object],
    tailscale_prefs: dict[str, object],
    ssh_probe: dict[str, object],
    anydesk: dict[str, object],
    observations: list[str],
) -> str:
    lines = [
        "# Stockenweiler Remote Path Probe",
        "",
        f"- generated_at: `{generated_at}`",
        "",
        "## Summary",
        "",
    ]
    for item in observations:
        lines.append(f"- {item}")

    lines.extend(
        [
            "",
            "## Tailscale",
            "",
            f"- backend_state: `{tailscale_status.get('backend_state', '-')}`",
            f"- self_dns_name: `{tailscale_status.get('self_dns_name', '-')}`",
            f"- self_ips: {', '.join(f'`{ip}`' for ip in tailscale_status.get('self_ips', [])) or '`-`'}",
            f"- route_all: `{tailscale_prefs.get('route_all', '-')}`",
            f"- corp_dns: `{tailscale_prefs.get('corp_dns', '-')}`",
            f"- stockenweiler_subnet_route_present: `{tailscale_status.get('stockenweiler_subnet_route_present', False)}`",
            "",
            "### Health",
            "",
        ]
    )
    for item in tailscale_status.get("health", []) or []:
        lines.append(f"- {item}")
    if not (tailscale_status.get("health", []) or []):
        lines.append("- none")

    lines.extend(["", "### Visible Primary Routes", ""])
    for item in tailscale_status.get("visible_primary_routes", []) or []:
        lines.append(f"- {item}")
    if not (tailscale_status.get("visible_primary_routes", []) or []):
        lines.append("- none")

    lines.extend(
        [
            "",
            "## SSH Probe",
            "",
            f"- target: `{ssh_probe.get('target', '-')}`",
            f"- status: `{ssh_probe.get('status', '-')}`",
        ]
    )
    if ssh_probe.get("stdout"):
        lines.append(f"- stdout: `{ssh_probe.get('stdout', '-')}`")
    if ssh_probe.get("stderr"):
        lines.append(f"- stderr: `{ssh_probe.get('stderr', '-')}`")

    lines.extend(
        [
            "",
            "## AnyDesk",
            "",
            f"- installed: `{anydesk.get('installed', False)}`",
            f"- roster_ids: {', '.join(f'`{item}`' for item in anydesk.get('roster_ids', [])) or '`-`'}",
            f"- permission_profile_ids: {', '.join(f'`{item}`' for item in anydesk.get('permission_profile_ids', [])) or '`-`'}",
            f"- history_ids: {', '.join(f'`{item}`' for item in anydesk.get('history_ids', [])) or '`-`'}",
        ]
    )

    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Read-only remote path probe for Stockenweiler.")
    parser.add_argument("--ssh-target", default="stock-pve", help="SSH target or alias for the Stockenweiler Proxmox host.")
    parser.add_argument(
        "--output",
        default=str(OUTPUT_ROOT / "latest_remote_path_probe.md"),
        help="Markdown report output path.",
    )
    args = parser.parse_args()

    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    json_path = output_path.with_suffix(".json")

    tailscale_status = load_tailscale_status()
    tailscale_prefs = load_tailscale_prefs()
    ssh_probe = probe_ssh(args.ssh_target)
    anydesk = parse_anydesk(ROOT_DIR)
    observations = build_observations(tailscale_status, tailscale_prefs, ssh_probe, anydesk)

    payload = {
        "generated_at": generated_at,
        "tailscale_status": tailscale_status,
        "tailscale_prefs": tailscale_prefs,
        "ssh_probe": ssh_probe,
        "anydesk": anydesk,
        "observations": observations,
    }
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    output_path.write_text(
        markdown_report(generated_at, tailscale_status, tailscale_prefs, ssh_probe, anydesk, observations),
        encoding="utf-8",
    )

    print(f"stockenweiler_remote_path_probe_report={output_path.as_posix()}")
    print(f"stockenweiler_remote_path_probe_json={json_path.as_posix()}")
    print(f"stockenweiler_remote_path_probe_tailscale_backend={tailscale_status.get('backend_state', '')}")
    print(f"stockenweiler_remote_path_probe_stockenweiler_route_present={tailscale_status.get('stockenweiler_subnet_route_present', False)}")
    print(f"stockenweiler_remote_path_probe_ssh_status={ssh_probe.get('status', '')}")
    print(f"stockenweiler_remote_path_probe_anydesk_candidate_count={len(anydesk.get('candidate_remote_ids', []))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
