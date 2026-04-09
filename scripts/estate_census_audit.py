#!/usr/bin/env python3
"""Build a single current-state census for the whole reachable Homeserver estate."""

from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_DIR = ROOT / "artifacts" / "estate_census"
REPORT_JSON = ARTIFACT_DIR / "latest_report.json"
REPORT_MD = ARTIFACT_DIR / "latest_report.md"

PROXMOX_ANKER = "100.69.179.87"
STOCK_PVE = "100.91.20.116"

TAILSCALE_FRONTDOORS = [
    {
        "name": "vaultwarden",
        "url": "http://100.99.206.128:8442/alive",
        "ok_codes": ["200"],
        "note": "Vaultwarden mobile/frontdoor health",
    },
    {
        "name": "home_assistant",
        "url": "http://100.99.206.128:8443/",
        "ok_codes": ["200"],
        "note": "Home Assistant mobile/frontdoor",
    },
    {
        "name": "odoo",
        "url": "http://100.99.206.128:8444/web/login",
        "ok_codes": ["200"],
        "note": "Odoo mobile/frontdoor",
    },
    {
        "name": "nextcloud",
        "url": "http://100.99.206.128:8445/",
        "ok_codes": ["200", "302"],
        "note": "Nextcloud mobile/frontdoor",
    },
    {
        "name": "paperless",
        "url": "http://100.99.206.128:8446/accounts/login/",
        "ok_codes": ["200"],
        "note": "Paperless mobile/frontdoor",
    },
    {
        "name": "portal",
        "url": "http://100.99.206.128:8447/",
        "ok_codes": ["200"],
        "note": "Portal mobile/frontdoor",
    },
    {
        "name": "radio",
        "url": "http://100.99.206.128:8448/",
        "ok_codes": ["200", "302"],
        "note": "Radio mobile/frontdoor",
    },
    {
        "name": "media",
        "url": "http://100.99.206.128:8449/",
        "ok_codes": ["200", "302"],
        "note": "Media mobile/frontdoor",
    },
]

STOCK_PUBLIC_HOSTS = [
    "https://home.prinz-stockenweiler.de",
    "https://papierkram.prinz-stockenweiler.de/dashboard",
    "https://cloud.prinz-stockenweiler.de/apps/dashboard/",
    "https://pve.prinz-stockenweiler.de",
]


def run_cmd(argv: list[str], timeout: int = 30, input_text: str | None = None) -> tuple[int, str, str]:
    completed = subprocess.run(
        argv,
        input=input_text,
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )
    return completed.returncode, completed.stdout.strip(), completed.stderr.strip()


def run_ps(command: str, timeout: int = 30) -> tuple[int, str, str]:
    return run_cmd(["powershell.exe", "-NoProfile", "-Command", command], timeout=timeout)


def curl_probe(url: str, insecure: bool = False, timeout: int = 8) -> dict[str, object]:
    argv = ["curl.exe"]
    if insecure:
        argv.append("-k")
    argv.extend(
        [
            "-s",
            "-S",
            "-o",
            "NUL",
            "-w",
            "%{http_code} %{remote_ip} %{time_total}",
            "--max-time",
            str(timeout),
            url,
        ]
    )
    code, out, err = run_cmd(argv, timeout=timeout + 2)
    parts = out.split()
    http_code = parts[0] if parts else "000"
    remote_ip = parts[1] if len(parts) > 1 else ""
    time_total = parts[2] if len(parts) > 2 else ""
    return {
        "url": url,
        "curl_exit_code": code,
        "http_code": http_code,
        "remote_ip": remote_ip,
        "time_total": time_total,
        "stderr": err,
    }


def ssh_script(host: str, script: str, *, relaxed_hostkey: bool = False, timeout: int = 60) -> tuple[int, str, str]:
    argv = ["ssh", "-o", "BatchMode=yes"]
    if relaxed_hostkey:
        argv.extend(["-o", "StrictHostKeyChecking=no", "-o", "UserKnownHostsFile=NUL"])
    argv.extend([f"root@{host}", "bash", "-s"])
    return run_cmd(argv, timeout=timeout, input_text=script.replace("\r\n", "\n"))


def get_local_network() -> dict[str, object]:
    code, out, err = run_ps(
        r"""
$ips = Get-NetIPAddress -AddressFamily IPv4 |
  Where-Object { $_.IPAddress -notlike '169.254*' -and $_.IPAddress -notlike '127*' } |
  Select-Object InterfaceAlias,IPAddress,PrefixLength
$dns = Get-DnsClientServerAddress -AddressFamily IPv4 |
  Select-Object InterfaceAlias,ServerAddresses
[PSCustomObject]@{
  ip_addresses = $ips
  dns_servers = $dns
} | ConvertTo-Json -Depth 5
"""
    )
    if code != 0 or not out:
        return {"ok": False, "stderr": err, "ip_addresses": [], "dns_servers": []}
    payload = json.loads(out)
    return {
        "ok": True,
        "ip_addresses": payload.get("ip_addresses", []) or [],
        "dns_servers": payload.get("dns_servers", []) or [],
    }


def get_tailscale_status() -> dict[str, object]:
    code, out, err = run_cmd(["tailscale", "status", "--json"], timeout=20)
    if code != 0 or not out:
        return {"ok": False, "stderr": err, "backend_state": "unknown", "peers": []}
    payload = json.loads(out)
    peers = []
    for peer in payload.get("Peer", {}).values():
        peers.append(
            {
                "dns_name": str(peer.get("DNSName", "")).rstrip("."),
                "online": bool(peer.get("Online")),
                "tailscale_ips": peer.get("TailscaleIPs", []) or [],
                "primary_routes": peer.get("PrimaryRoutes", []) or [],
            }
        )
    peers.sort(key=lambda item: item["dns_name"])
    return {
        "ok": True,
        "backend_state": payload.get("BackendState", "unknown"),
        "self": {
            "dns_name": str(payload.get("Self", {}).get("DNSName", "")).rstrip("."),
            "tailscale_ips": payload.get("Self", {}).get("TailscaleIPs", []) or [],
        },
        "peer_count": len(peers),
        "peers": peers,
        "health": payload.get("Health", []) or [],
    }


def probe_anker() -> dict[str, object]:
    script = r'''
python3 - <<'PY'
import json, re, subprocess

def sh(cmd):
    completed = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=False)
    return completed.stdout.strip(), completed.stderr.strip(), completed.returncode

def parse_rows(raw, kind):
    rows = []
    for line in raw.splitlines():
        stripped = line.strip()
        if not stripped or not stripped[0].isdigit():
            continue
        parts = stripped.split()
        if kind == 'pct' and len(parts) >= 3:
            rows.append({'vmid': int(parts[0]), 'status': parts[1], 'name': parts[-1]})
        if kind == 'qm' and len(parts) >= 3:
            rows.append({'vmid': int(parts[0]), 'name': parts[1], 'status': parts[2]})
    return rows

hostname, _, _ = sh('hostname')
pveversion, _, _ = sh('pveversion | head -1')
vmbr0, _, _ = sh('ip -4 addr show vmbr0')
routes, _, _ = sh('ip route')
pct_list, _, _ = sh('pct list')
qm_list, _, _ = sh('qm list')
router_active, _, _ = sh('systemctl is-active hs27-transition-router.service 2>/dev/null || true')
router_enabled, _, _ = sh('systemctl is-enabled hs27-transition-router.service 2>/dev/null || true')
toolbox_cfg, _, _ = sh('pct config 100')
storage_cfg, _, _ = sh('pct config 110')

http_checks = {}
for name, url in {
    'nextcloud': 'http://10.1.0.21/',
    'odoo': 'http://10.1.0.22:8069/web/login',
    'paperless': 'http://10.1.0.23/accounts/login/',
    'haos': 'http://10.1.0.24:8123/',
    'vaultwarden': 'http://10.1.0.26:8080/alive',
}.items():
    out, _, _ = sh(f"curl -s -o /dev/null -w '%{{http_code}}' --max-time 4 {url}")
    http_checks[name] = out or '000'

data = {
    'reachable': True,
    'hostname': hostname,
    'pve_version': pveversion,
    'vmbr0_ipv4': re.findall(r'inet (\S+)', vmbr0),
    'routes': [line for line in routes.splitlines() if line.strip()],
    'transition_router_service': {'enabled': router_enabled or 'unknown', 'active': router_active or 'unknown'},
    'containers': parse_rows(pct_list, 'pct'),
    'vms': parse_rows(qm_list, 'qm'),
    'toolbox_onboot': 'onboot: 1' in toolbox_cfg,
    'storage_node_onboot': 'onboot: 1' in storage_cfg,
    'legacy_http_checks': http_checks,
}
print(json.dumps(data))
PY
'''
    code, out, err = ssh_script(PROXMOX_ANKER, script, timeout=60)
    if code != 0 or not out:
        return {"reachable": False, "stderr": err}
    return json.loads(out)


def probe_stockenweiler() -> dict[str, object]:
    script = r'''
python3 - <<'PY'
import json, re, subprocess

def sh(cmd):
    completed = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=False)
    return completed.stdout.strip(), completed.stderr.strip(), completed.returncode

def parse_rows(raw, kind):
    rows = []
    for line in raw.splitlines():
        stripped = line.strip()
        if not stripped or not stripped[0].isdigit():
            continue
        parts = stripped.split()
        if kind == 'pct' and len(parts) >= 3:
            rows.append({'vmid': int(parts[0]), 'status': parts[1], 'name': parts[-1]})
        if kind == 'qm' and len(parts) >= 3:
            rows.append({'vmid': int(parts[0]), 'name': parts[1], 'status': parts[2]})
    return rows

def parse_storage(raw):
    rows = []
    for line in raw.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith('Name'):
            continue
        parts = stripped.split()
        if len(parts) < 3:
            continue
        row = {'name': parts[0], 'type': parts[1], 'status': parts[2]}
        if len(parts) >= 7:
            row['used_percent'] = parts[-1]
        rows.append(row)
    return rows

hostname, _, _ = sh('hostname')
pveversion, _, _ = sh('pveversion | head -1')
vmbr0, _, _ = sh('ip -4 addr show vmbr0')
tailscale0, _, _ = sh('ip -4 addr show tailscale0 2>/dev/null || true')
pct_list, _, _ = sh('pct list')
qm_list, _, _ = sh('qm list')
storage, _, _ = sh('pvesm status')

data = {
    'reachable': True,
    'hostname': hostname,
    'pve_version': pveversion,
    'vmbr0_ipv4': re.findall(r'inet (\S+)', vmbr0),
    'tailscale_ipv4': re.findall(r'inet (\S+)', tailscale0),
    'containers': parse_rows(pct_list, 'pct'),
    'vms': parse_rows(qm_list, 'qm'),
    'storages': parse_storage(storage),
}
print(json.dumps(data))
PY
'''
    code, out, err = ssh_script(STOCK_PVE, script, relaxed_hostkey=True, timeout=60)
    if code != 0 or not out:
        return {"reachable": False, "stderr": err}
    return json.loads(out)


def classify_frontdoor(item: dict[str, object]) -> str:
    http_code = str(item.get("http_code", "000"))
    ok_codes = [str(code) for code in item.get("ok_codes", [])]
    if http_code in ok_codes:
        return "ok"
    if http_code != "000":
        return "degraded"
    return "down"


def build_report() -> dict[str, object]:
    local_network = get_local_network()
    tailscale = get_tailscale_status()
    anker = probe_anker()
    stockenweiler = probe_stockenweiler()

    frontdoors = []
    for item in TAILSCALE_FRONTDOORS:
        probe = curl_probe(item["url"])
        probe.update({"name": item["name"], "ok_codes": item["ok_codes"], "note": item["note"]})
        probe["status"] = classify_frontdoor(probe)
        frontdoors.append(probe)

    stock_public = []
    for url in STOCK_PUBLIC_HOSTS:
        probe = curl_probe(url, insecure=False)
        probe["status"] = "ok" if probe["http_code"] not in {"000", "400", "500", "502", "503", "504"} else "broken"
        stock_public.append(probe)

    online_peers = [peer for peer in tailscale.get("peers", []) if peer.get("online")]
    offline_peers = [peer for peer in tailscale.get("peers", []) if not peer.get("online")]
    routed_peers = [peer for peer in tailscale.get("peers", []) if peer.get("primary_routes")]
    local_ips = local_network.get("ip_addresses", []) if isinstance(local_network, dict) else []
    local_dns = local_network.get("dns_servers", []) if isinstance(local_network, dict) else []
    local_active_dns = [item for item in local_dns if item.get("ServerAddresses")]
    legacy_vpn_interfaces = [item for item in local_ips if str(item.get("InterfaceAlias", "")).lower() == "vpn"]

    usable_now = {
        "management_paths": [
            "ssh root@100.69.179.87 (proxmox-anker)",
            "ssh root@100.91.20.116 (stockenweiler-pve)",
            "Tailscale peer toolbox.tail150400.ts.net / 100.99.206.128",
        ],
        "service_paths": [item["url"] for item in frontdoors if item["status"] == "ok"],
    }

    blockers: list[str] = []
    if any(item["name"] == "home_assistant" and item["status"] != "ok" for item in frontdoors):
        blockers.append("Home Assistant mobile/frontdoor is still degraded and returns HTTP 400 through toolbox.")
    blockers.append("StudioPC direct access to legacy guest 192.168.2.x is not the working path during the UCG transition because the same subnet exists on two different L2 domains.")
    if legacy_vpn_interfaces:
        blockers.append("StudioPC still has a legacy local WireGuard VPN interface active (`VPN` / `10.0.0.2`), which keeps old Stockenweiler assumptions alive and adds operator confusion.")
    if stockenweiler.get("reachable"):
        inactive = [item["name"] for item in stockenweiler.get("storages", []) if item.get("status") != "active"]
        if inactive:
            blockers.append(f"Stockenweiler has inactive storage targets: {', '.join(inactive)}.")
    broken_public = [item["url"] for item in stock_public if item["status"] != "ok"]
    if broken_public:
        blockers.append(f"Stockenweiler public legacy endpoints are still broken: {', '.join(broken_public)}.")
    offline_peer_names = [peer["dns_name"] for peer in offline_peers]
    if offline_peer_names:
        blockers.append(f"Some expected Tailscale peers are offline: {', '.join(offline_peer_names)}.")

    recommended_next_order = [
        "Treat Tailscale as the only professional operator path; stop depending on direct StudioPC-to-legacy 192.168.2.x reachability during migration.",
        "Freeze the current working transition state: Proxmox on 10.1.0.92, toolbox frontdoors 8/8 green, guests still isolated behind the transition router.",
        "Use the existing published UCG VLAN schema as the target network model; do not reopen subnet design unless the SSOT itself changes.",
        "Use a low-risk pilot service after the subnet decision, then migrate business services one by one behind the stable frontdoor names.",
        "Normalize Stockenweiler access and storage facts before any site-marriage or shared-storage work.",
    ]

    transition_sequence = [
        "Freeze the current working control plane and keep Tailscale/frontdoor access as the canonical operator path.",
        "Use `UCG_NETWORK_ARCHITECTURE.md` as the binding target VLAN/subnet model and focus only on service-to-VLAN adoption plus runtime cutover order.",
        "Keep DNS and browser entrypoints target-agnostic; users should prefer toolbox frontdoors and hs27.internal names instead of direct guest IPs.",
        "Run one low-risk pilot move first, preferably a non-business-critical endpoint such as portal, media, or radio pathing.",
        "After the pilot is green, migrate the core business services in order: Odoo, Nextcloud, Paperless.",
        "Move Home Assistant only after the business trio is stable on the new model.",
        "Revisit Vaultwarden only with explicit rollback and maintenance discipline because it is security-critical.",
        "Handle PBS and any storage redesign last, after networking and service naming are stable.",
    ]

    return {
        "generated_at": datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M:%S"),
        "local_network": local_network,
        "tailscale": tailscale,
        "anker": anker,
        "stockenweiler": stockenweiler,
        "frontdoors": frontdoors,
        "stock_public": stock_public,
        "usable_now": usable_now,
        "blockers": blockers,
        "recommended_next_order": recommended_next_order,
        "transition_sequence": transition_sequence,
        "summary": {
            "local_ipv4_interfaces": len(local_ips),
            "local_active_dns_sets": len(local_active_dns),
            "online_tailscale_peers": len(online_peers),
            "offline_tailscale_peers": len(offline_peers),
            "routed_tailscale_peers": len(routed_peers),
            "anker_running_containers": len([row for row in anker.get("containers", []) if row.get("status") == "running"]),
            "anker_running_vms": len([row for row in anker.get("vms", []) if row.get("status") == "running"]),
            "stock_running_containers": len([row for row in stockenweiler.get("containers", []) if row.get("status") == "running"]),
            "stock_running_vms": len([row for row in stockenweiler.get("vms", []) if row.get("status") == "running"]),
            "frontdoors_ok": len([item for item in frontdoors if item.get("status") == "ok"]),
            "frontdoors_total": len(frontdoors),
            "stock_public_ok": len([item for item in stock_public if item.get("status") == "ok"]),
            "stock_public_total": len(stock_public),
        },
    }


def write_outputs(report: dict[str, object]) -> None:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_JSON.write_text(json.dumps(report, indent=2), encoding="utf-8")

    summary = report["summary"]
    md = [
        "# Estate Census",
        "",
        f"- generated_at: `{report['generated_at']}`",
        f"- tailscale_backend_state: `{report['tailscale'].get('backend_state', 'unknown')}`",
        f"- local_ipv4_interfaces: `{summary['local_ipv4_interfaces']}`",
        f"- local_active_dns_sets: `{summary['local_active_dns_sets']}`",
        f"- online_tailscale_peers: `{summary['online_tailscale_peers']}`",
        f"- offline_tailscale_peers: `{summary['offline_tailscale_peers']}`",
        f"- routed_tailscale_peers: `{summary['routed_tailscale_peers']}`",
        f"- anker_running_containers: `{summary['anker_running_containers']}`",
        f"- anker_running_vms: `{summary['anker_running_vms']}`",
        f"- stock_running_containers: `{summary['stock_running_containers']}`",
        f"- stock_running_vms: `{summary['stock_running_vms']}`",
        f"- frontdoors_ok: `{summary['frontdoors_ok']}` / `{summary['frontdoors_total']}`",
        f"- stock_public_ok: `{summary['stock_public_ok']}` / `{summary['stock_public_total']}`",
        "",
        "## Usable Now",
        "",
    ]
    for item in report["usable_now"]["management_paths"]:
        md.append(f"- management: `{item}`")
    for item in report["usable_now"]["service_paths"]:
        md.append(f"- service: `{item}`")

    md.extend(["", "## Local Control Plane", ""])
    for item in report["local_network"].get("ip_addresses", []):
        md.append(
            f"- iface `{item.get('InterfaceAlias', '-')}` -> `{item.get('IPAddress', '-')}/{item.get('PrefixLength', '-')}`"
        )
    for item in report["local_network"].get("dns_servers", []):
        servers = item.get("ServerAddresses") or []
        if servers:
            md.append(f"- dns `{item.get('InterfaceAlias', '-')}` -> `{', '.join(str(server) for server in servers)}`")

    md.extend(["", "## Tailscale Peers", ""])
    for item in report["tailscale"].get("peers", []):
        routes = item.get("primary_routes") or []
        route_text = f" / routes `{', '.join(routes)}`" if routes else ""
        md.append(
            f"- `{item.get('dns_name', '-')}` -> online `{str(bool(item.get('online'))).lower()}` / ip `{', '.join(item.get('tailscale_ips', []))}`{route_text}"
        )

    md.extend(["", "## Frontdoors", ""])
    for item in report["frontdoors"]:
        md.append(f"- `{item['name']}` -> `{item['http_code']}` (`{item['status']}`) via `{item['url']}`")

    md.extend(["", "## Proxmox Anker", ""])
    if report["anker"].get("reachable"):
        md.append(f"- host: `{report['anker']['hostname']}` / `{report['anker']['pve_version']}`")
        md.append(f"- vmbr0_ipv4: `{', '.join(report['anker'].get('vmbr0_ipv4', []))}`")
        md.append(f"- transition_router: active `{report['anker']['transition_router_service'].get('active', '-')}` / enabled `{report['anker']['transition_router_service'].get('enabled', '-')}`")
        running_ct = [row['name'] for row in report['anker'].get('containers', []) if row.get('status') == 'running']
        running_vm = [row['name'] for row in report['anker'].get('vms', []) if row.get('status') == 'running']
        stopped_vm = [row['name'] for row in report['anker'].get('vms', []) if row.get('status') != 'running']
        md.append(f"- running_containers: `{', '.join(running_ct) or 'none'}`")
        md.append(f"- running_vms: `{', '.join(running_vm) or 'none'}`")
        md.append(f"- stopped_vms: `{', '.join(stopped_vm) or 'none'}`")
        for name, code in report['anker'].get('legacy_http_checks', {}).items():
            md.append(f"- internal_http_{name}: `{code}`")
    else:
        md.append(f"- unreachable: `{report['anker'].get('stderr', '')}`")

    md.extend(["", "## Stockenweiler", ""])
    if report["stockenweiler"].get("reachable"):
        md.append(f"- host: `{report['stockenweiler']['hostname']}` / `{report['stockenweiler']['pve_version']}`")
        md.append(f"- vmbr0_ipv4: `{', '.join(report['stockenweiler'].get('vmbr0_ipv4', []))}`")
        md.append(f"- tailscale_ipv4: `{', '.join(report['stockenweiler'].get('tailscale_ipv4', []))}`")
        running_ct = [row['name'] for row in report['stockenweiler'].get('containers', []) if row.get('status') == 'running']
        running_vm = [row['name'] for row in report['stockenweiler'].get('vms', []) if row.get('status') == 'running']
        md.append(f"- running_containers: `{', '.join(running_ct) or 'none'}`")
        md.append(f"- running_vms: `{', '.join(running_vm) or 'none'}`")
        for item in report['stockenweiler'].get('storages', []):
            extra = f" / used `{item['used_percent']}`" if item.get('used_percent') else ""
            md.append(f"- storage `{item['name']}`: `{item['status']}` ({item['type']}){extra}")
    else:
        md.append(f"- unreachable: `{report['stockenweiler'].get('stderr', '')}`")

    md.extend(["", "## Blockers", ""])
    for item in report["blockers"]:
        md.append(f"- {item}")

    md.extend(["", "## Recommended Next Order", ""])
    for item in report["recommended_next_order"]:
        md.append(f"- {item}")

    md.extend(["", "## Canonical Transition Sequence", ""])
    for item in report["transition_sequence"]:
        md.append(f"- {item}")

    REPORT_MD.write_text("\n".join(md) + "\n", encoding="utf-8")


def main() -> int:
    report = build_report()
    write_outputs(report)
    print(f"report_json={REPORT_JSON}")
    print(f"report_md={REPORT_MD}")
    print(f"frontdoors_ok={report['summary']['frontdoors_ok']}")
    print(f"frontdoors_total={report['summary']['frontdoors_total']}")
    print(f"anker_running_vms={report['summary']['anker_running_vms']}")
    print(f"stock_running_vms={report['summary']['stock_running_vms']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
