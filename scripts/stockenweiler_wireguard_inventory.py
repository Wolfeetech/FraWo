#!/usr/bin/env python3
"""Read-only inventory of the existing Stockenweiler WireGuard server."""

from __future__ import annotations

import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_DIR = ROOT / "artifacts" / "stockenweiler_inventory"
REPORT_JSON = ARTIFACT_DIR / "latest_wireguard_inventory.json"
REPORT_MD = ARTIFACT_DIR / "latest_wireguard_inventory.md"
TARGET = "100.91.20.116"


def run_cmd(argv: list[str], timeout: int = 60) -> tuple[int, str, str]:
    completed = subprocess.run(
        argv,
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )
    return completed.returncode, completed.stdout.strip(), completed.stderr.strip()


def ssh(remote_command: str, timeout: int = 60) -> tuple[int, str, str]:
    return run_cmd(
        [
            "ssh",
            "-o",
            "ConnectTimeout=8",
            "-o",
            "StrictHostKeyChecking=no",
            "-o",
            "UserKnownHostsFile=NUL",
            f"root@{TARGET}",
            remote_command,
        ],
        timeout=timeout,
    )


def parse_pct_config(raw: str) -> dict[str, str]:
    data: dict[str, str] = {}
    for line in raw.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip()
    return data


def parse_server_profile(raw: str) -> dict[str, object]:
    result: dict[str, object] = {"allowed_ips": []}
    peer_count = 0
    for line in raw.splitlines():
        stripped = line.strip()
        if stripped == "[Peer]":
            peer_count += 1
        elif stripped.startswith("Address ="):
            result["address"] = stripped.split("=", 1)[1].strip()
        elif stripped.startswith("ListenPort ="):
            result["listen_port"] = stripped.split("=", 1)[1].strip()
        elif stripped.startswith("PostUp ="):
            result["post_up"] = stripped.split("=", 1)[1].strip()
        elif stripped.startswith("PostDown ="):
            result["post_down"] = stripped.split("=", 1)[1].strip()
        elif stripped.startswith("AllowedIPs ="):
            result.setdefault("allowed_ips", []).append(stripped.split("=", 1)[1].strip())
    result["peer_count"] = peer_count
    return result


def parse_wg_show(raw: str) -> dict[str, object]:
    peers: list[dict[str, str]] = []
    current: dict[str, str] | None = None
    interface: dict[str, str] = {}
    for line in raw.splitlines():
        stripped = line.rstrip()
        if stripped.startswith("interface:"):
            interface["name"] = stripped.split(":", 1)[1].strip()
            current = None
        elif stripped.strip().startswith("listening port:"):
            interface["listening_port"] = stripped.split(":", 1)[1].strip()
        elif stripped.startswith("peer:"):
            if current:
                peers.append(current)
            current = {"peer": "present"}
        elif current is not None and ":" in stripped:
            key, value = stripped.strip().split(":", 1)
            current[key.strip().replace(" ", "_")] = value.strip()
    if current:
        peers.append(current)
    return {"interface": interface, "peers": peers}


def parse_client_profiles(raw: str) -> list[dict[str, str]]:
    profiles: list[dict[str, str]] = []
    current: dict[str, str] | None = None
    for line in raw.splitlines():
        stripped = line.strip()
        if stripped.startswith("FILE:"):
            if current:
                profiles.append(current)
            path = stripped.removeprefix("FILE:")
            current = {"path": path, "name": Path(path).stem}
        elif current is not None and stripped.startswith("Address ="):
            current["address"] = stripped.split("=", 1)[1].strip()
        elif current is not None and stripped.startswith("Endpoint ="):
            current["endpoint"] = stripped.split("=", 1)[1].strip()
        elif current is not None and stripped.startswith("AllowedIPs ="):
            current["allowed_ips"] = stripped.split("=", 1)[1].strip()
    if current:
        profiles.append(current)
    return profiles


def build_report() -> dict[str, object]:
    code, out, err = ssh("hostname; pveversion | head -1; echo ---; pct status 106; echo ---; pct config 106")
    if code != 0:
        return {
            "generated_at": datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M:%S"),
            "target": TARGET,
            "reachable": False,
            "stderr": err or out,
        }

    host_section, status_section, config_section = (out.split("---") + ["", ""])[:3]
    host_lines = [line.strip() for line in host_section.splitlines() if line.strip()]
    pct_config = parse_pct_config(config_section)

    _, server_profile_raw, _ = ssh(
        "pct exec 106 -- sh -lc \"grep -e '^Address' -e '^ListenPort' -e '^AllowedIPs' -e '^PostUp' -e '^PostDown' -e '^\\[Interface\\]' -e '^\\[Peer\\]' /etc/wireguard/wg0.conf\""
    )
    _, wg_show_raw, _ = ssh(
        "pct exec 106 -- sh -lc \"wg show | sed -E 's#(public key: ).*#\\1[REDACTED]#; s#(private key: ).*#\\1[REDACTED]#; s#(preshared key: ).*#\\1[REDACTED]#'\""
    )
    _, client_profiles_raw, _ = ssh(
        "pct exec 106 -- sh -lc 'for f in /etc/wireguard/clients/*.conf; do echo FILE:$f; grep -e \"^Address\" -e \"^AllowedIPs\" -e \"^Endpoint\" \"$f\"; echo ---; done'"
    )

    server_profile = parse_server_profile(server_profile_raw)
    wg_show = parse_wg_show(wg_show_raw)
    client_profiles = parse_client_profiles(client_profiles_raw)

    active_peers = [peer for peer in wg_show.get("peers", []) if peer.get("latest_handshake")]
    named_profiles = {profile.get("address"): profile.get("name") for profile in client_profiles}

    conclusions = [
        "CT 106 is a running dedicated WireGuard server in Stockenweiler.",
        f"The server currently listens on port {server_profile.get('listen_port', '?')} and serves the VPN subnet {server_profile.get('address', '?')}.",
        "This confirms that Stockenweiler already hosts an existing WireGuard server topology; the local StudioPC WireGuard profile is only one client path into that topology.",
        "For a future professional site bridge, Variant A (UCG as client to the existing Stockenweiler WireGuard server) is the lower-friction starting candidate because clients and subnet expectations already exist.",
        "Variant B (UCG as new WireGuard server and Stockenweiler as client) remains possible, but it would be a conscious migration/rebuild, not a continuation of the current topology.",
    ]

    return {
        "generated_at": datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M:%S"),
        "target": TARGET,
        "reachable": True,
        "hostname": host_lines[0] if host_lines else "unknown",
        "pve_version": host_lines[1] if len(host_lines) > 1 else "unknown",
        "ct_status": status_section.strip(),
        "ct_config": {
            "hostname": pct_config.get("hostname", ""),
            "net0": pct_config.get("net0", ""),
            "onboot": pct_config.get("onboot", ""),
        },
        "server_profile": server_profile,
        "wg_runtime": wg_show,
        "client_profiles": client_profiles,
        "active_peer_count": len(active_peers),
        "active_peer_profile_names": [
            named_profiles.get(peer.get("allowed_ips", ""), peer.get("allowed_ips", "unknown"))
            for peer in active_peers
        ],
        "conclusions": conclusions,
    }


def write_outputs(report: dict[str, object]) -> None:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_JSON.write_text(json.dumps(report, indent=2), encoding="utf-8")

    md = [
        "# Stockenweiler WireGuard Inventory",
        "",
        f"- generated_at: `{report.get('generated_at', 'unknown')}`",
        f"- target: `{report.get('target', TARGET)}`",
        f"- reachable: `{str(report.get('reachable', False)).lower()}`",
    ]

    if not report.get("reachable"):
        md.append(f"- stderr: `{report.get('stderr', '')}`")
        REPORT_MD.write_text("\n".join(md) + "\n", encoding="utf-8")
        return

    md.extend(
        [
            f"- host: `{report.get('hostname', '-')}` / `{report.get('pve_version', '-')}`",
            f"- ct106_status: `{report.get('ct_status', '-')}`",
            f"- ct106_net0: `{report.get('ct_config', {}).get('net0', '-')}`",
            f"- server_address: `{report.get('server_profile', {}).get('address', '-')}`",
            f"- listen_port: `{report.get('server_profile', {}).get('listen_port', '-')}`",
            f"- configured_peers: `{report.get('server_profile', {}).get('peer_count', 0)}`",
            f"- peers_with_runtime_handshake_info: `{report.get('active_peer_count', 0)}`",
            "",
            "## Known Client Profiles",
            "",
        ]
    )

    for profile in report.get("client_profiles", []):
        md.append(
            f"- `{profile.get('name', '-')}` -> address `{profile.get('address', '-')}`, endpoint `{profile.get('endpoint', '-')}`, allowed `{profile.get('allowed_ips', '-')}`"
        )

    md.extend(["", "## Runtime Peer Snapshot", ""])
    for peer in report.get("wg_runtime", {}).get("peers", []):
        md.append(
            f"- allowed `{peer.get('allowed_ips', '-')}` / endpoint `{peer.get('endpoint', '-')}` / latest_handshake `{peer.get('latest_handshake', '-')}` / transfer `{peer.get('transfer', '-')}`"
        )

    md.extend(["", "## Conclusions", ""])
    for item in report.get("conclusions", []):
        md.append(f"- {item}")

    REPORT_MD.write_text("\n".join(md) + "\n", encoding="utf-8")


def main() -> int:
    report = build_report()
    write_outputs(report)
    print(f"report_json={REPORT_JSON}")
    print(f"report_md={REPORT_MD}")
    print(f"reachable={str(report.get('reachable', False)).lower()}")
    if report.get("reachable"):
        print(f"listen_port={report.get('server_profile', {}).get('listen_port', '-')}")
        print(f"client_profiles={len(report.get('client_profiles', []))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
