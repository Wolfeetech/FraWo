#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_DIR = ROOT / "artifacts" / "platform_health"
REPORT_JSON = ARTIFACT_DIR / "latest_report.json"
REPORT_MD = ARTIFACT_DIR / "latest_report.md"
SSH_CONFIG_PATH = ROOT / "Codex" / "ssh_config"
DEFAULT_TOOLBOX_FRONTDOOR_IP = "100.82.26.53"

ANKER_SSH_TARGET = "root@100.69.179.87"
ANKER_NODE = "proxmox-anker"
STOCK_SSH_TARGET = "stock-pve"
STOCK_NODE = "pve"

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


TOOLBOX_FRONTDOOR_IP = current_toolbox_frontdoor_ip()

TAILSCALE_FRONTDOORS = {
    "vaultwarden": f"http://{TOOLBOX_FRONTDOOR_IP}:8442/alive",
    "home_assistant": f"http://{TOOLBOX_FRONTDOOR_IP}:8443/",
    "odoo": f"http://{TOOLBOX_FRONTDOOR_IP}:8444/web/login",
    "nextcloud": f"http://{TOOLBOX_FRONTDOOR_IP}:8445/",
    "paperless": f"http://{TOOLBOX_FRONTDOOR_IP}:8446/accounts/login/",
    "portal": f"http://{TOOLBOX_FRONTDOOR_IP}:8447/",
    "radio": f"http://{TOOLBOX_FRONTDOOR_IP}:8448/",
    "media": f"http://{TOOLBOX_FRONTDOOR_IP}:8449/",
}

ANKER_DIRECT_CHECKS = {
    "odoo_direct": "http://10.1.0.22:8069/web/login",
    "nextcloud_direct": "http://10.1.0.21/",
    "paperless_direct": "http://10.1.0.23/accounts/login/",
    "ha_direct": "http://10.1.0.24:8123/",
}


def run_cmd(argv: list[str], timeout: int = 60, input_text: str | None = None) -> tuple[int, str, str]:
    completed = subprocess.run(
        argv,
        input=input_text,
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )
    return completed.returncode, completed.stdout.strip(), completed.stderr.strip()


def ssh_script(target: str, script: str, timeout: int = 120) -> tuple[int, str, str]:
    argv = ["ssh", "-o", "BatchMode=yes", target, "bash", "-s"]
    return run_cmd(argv, timeout=timeout, input_text=script.replace("\r\n", "\n"))


def ssh_json(target: str, script: str, timeout: int = 120) -> dict[str, object]:
    code, out, err = ssh_script(target, script, timeout=timeout)
    if code != 0 or not out:
        return {"ok": False, "stderr": err or out}
    try:
        payload = json.loads(out)
    except json.JSONDecodeError:
        return {"ok": False, "stderr": f"invalid_json: {out[:300]}"}
    if isinstance(payload, dict):
        payload["ok"] = True
        return payload
    return {"ok": True, "value": payload}


def ssh_text(target: str, script: str, timeout: int = 60) -> tuple[bool, str]:
    code, out, err = ssh_script(target, script, timeout=timeout)
    return code == 0, (out or err)


def curl_probe(url: str, timeout: int = 8) -> dict[str, object]:
    argv = [
        "curl.exe",
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
    code, out, err = run_cmd(argv, timeout=timeout + 2)
    parts = out.split()
    return {
        "url": url,
        "curl_exit_code": code,
        "http_code": parts[0] if parts else "000",
        "remote_ip": parts[1] if len(parts) > 1 else "",
        "time_total": parts[2] if len(parts) > 2 else "",
        "stderr": err,
    }


def remote_http_code(target: str, url: str) -> str:
    ok, out = ssh_text(target, f"curl -s -o /dev/null -w '%{{http_code}}' --max-time 8 '{url}'")
    return out.strip() if ok and out.strip() else "000"


def load_node_status(target: str, node: str) -> dict[str, object]:
    return ssh_json(target, f"pvesh get /nodes/{node}/status --output-format json")


def load_storages(target: str, node: str) -> list[dict[str, object]]:
    payload = ssh_json(target, f"pvesh get /nodes/{node}/storage --output-format json")
    if payload.get("ok") and isinstance(payload.get("value"), list):
        return payload["value"]  # type: ignore[index]
    if payload.get("ok") and isinstance(payload, dict) and isinstance(payload.get("value"), list):
        return payload.get("value", [])  # type: ignore[return-value]
    if payload.get("ok") and isinstance(payload.get("storage"), str):
        return [payload]  # type: ignore[list-item]
    if payload.get("ok") and isinstance(payload.get("value"), dict):
        return [payload["value"]]  # type: ignore[index]
    if payload.get("ok") and isinstance(payload, dict) and any(isinstance(v, list) for v in payload.values()):
        for value in payload.values():
            if isinstance(value, list):
                return value  # type: ignore[return-value]
    return payload.get("value", []) if isinstance(payload.get("value"), list) else []


def load_resources(target: str, node: str) -> list[dict[str, object]]:
    payload = ssh_json(target, "pvesh get /cluster/resources --type vm --output-format json")
    values: list[dict[str, object]] = []
    raw = payload.get("value") if payload.get("ok") else None
    if isinstance(raw, list):
        values = [item for item in raw if isinstance(item, dict)]
    elif payload.get("ok") and isinstance(payload, dict):
        if isinstance(payload.get("value"), list):
            values = [item for item in payload["value"] if isinstance(item, dict)]  # type: ignore[index]
    return [item for item in values if item.get("node") == node]


def load_selected_pct_configs(target: str, vmids: list[int]) -> dict[str, dict[str, str]]:
    result: dict[str, dict[str, str]] = {}
    for vmid in vmids:
        ok, out = ssh_text(target, f"pct config {vmid}")
        if not ok:
            result[str(vmid)] = {"error": out}
            continue
        data: dict[str, str] = {}
        for line in out.splitlines():
            if ":" not in line:
                continue
            key, value = line.split(":", 1)
            key = key.strip()
            if key in {"rootfs", "mp0", "mp1", "net0", "hostname"}:
                data[key] = value.strip()
        result[str(vmid)] = data
    return result


def bytes_to_gib(value: object) -> float:
    try:
        return round(int(value) / (1024 ** 3), 2)
    except (TypeError, ValueError):
        return 0.0


def percent(numerator: object, denominator: object) -> float:
    try:
        numerator_i = int(numerator)
        denominator_i = int(denominator)
    except (TypeError, ValueError):
        return 0.0
    if denominator_i <= 0:
        return 0.0
    return round((numerator_i / denominator_i) * 100, 1)


def summarize_storage(items: list[dict[str, object]]) -> list[dict[str, object]]:
    result = []
    for item in items:
        result.append(
            {
                "storage": item.get("storage"),
                "type": item.get("type"),
                "active": bool(item.get("active")),
                "enabled": bool(item.get("enabled", 1)),
                "shared": bool(item.get("shared", 0)),
                "used_gib": bytes_to_gib(item.get("used", 0)),
                "avail_gib": bytes_to_gib(item.get("avail", 0)),
                "total_gib": bytes_to_gib(item.get("total", 0)),
                "used_pct": round(float(item.get("used_fraction", 0)) * 100, 1) if item.get("total") else 0.0,
                "content": item.get("content", ""),
            }
        )
    return sorted(result, key=lambda entry: (not entry["active"], -entry["used_pct"]))


def summarize_resources(items: list[dict[str, object]]) -> list[dict[str, object]]:
    result = []
    for item in items:
        result.append(
            {
                "vmid": item.get("vmid"),
                "name": item.get("name"),
                "type": item.get("type"),
                "status": item.get("status"),
                "cpu": round(float(item.get("cpu", 0)) * 100, 1),
                "mem_used_gib": bytes_to_gib(item.get("mem", 0)),
                "mem_max_gib": bytes_to_gib(item.get("maxmem", 0)),
                "mem_used_pct": percent(item.get("mem", 0), item.get("maxmem", 0)),
                "disk_used_gib": bytes_to_gib(item.get("disk", 0)),
                "disk_max_gib": bytes_to_gib(item.get("maxdisk", 0)),
                "disk_used_pct": percent(item.get("disk", 0), item.get("maxdisk", 0)),
                "uptime_seconds": int(item.get("uptime", 0) or 0),
            }
        )
    return sorted(result, key=lambda entry: (entry["type"], int(entry["vmid"])))


def host_summary(node_status: dict[str, object], fallback_hostname: str) -> dict[str, object]:
    memory = node_status.get("memory", {}) if isinstance(node_status.get("memory"), dict) else {}
    swap = node_status.get("swap", {}) if isinstance(node_status.get("swap"), dict) else {}
    rootfs = node_status.get("rootfs", {}) if isinstance(node_status.get("rootfs"), dict) else {}
    return {
        "hostname": node_status.get("hostname") or fallback_hostname,
        "pve_version": node_status.get("pveversion", "unknown"),
        "loadavg": node_status.get("loadavg", []),
        "memory_used_gib": bytes_to_gib(memory.get("used", 0)),
        "memory_total_gib": bytes_to_gib(memory.get("total", 0)),
        "memory_used_pct": percent(memory.get("used", 0), memory.get("total", 0)),
        "swap_used_gib": bytes_to_gib(swap.get("used", 0)),
        "swap_total_gib": bytes_to_gib(swap.get("total", 0)),
        "swap_used_pct": percent(swap.get("used", 0), swap.get("total", 0)),
        "rootfs_used_gib": bytes_to_gib(rootfs.get("used", 0)),
        "rootfs_total_gib": bytes_to_gib(rootfs.get("total", 0)),
        "rootfs_used_pct": percent(rootfs.get("used", 0), rootfs.get("total", 0)),
    }


def top_pressure(resources: list[dict[str, object]], *, field: str, threshold: float) -> list[dict[str, object]]:
    filtered = [item for item in resources if item.get("status") == "running" and float(item.get(field, 0)) >= threshold]
    return sorted(filtered, key=lambda item: float(item.get(field, 0)), reverse=True)


def classify_blockers(
    anker_host: dict[str, object],
    anker_storages: list[dict[str, object]],
    stock_host: dict[str, object],
    stock_storages: list[dict[str, object]],
    anker_resources: list[dict[str, object]],
    stock_resources: list[dict[str, object]],
    direct_checks: dict[str, str],
    frontdoor_checks: dict[str, dict[str, object]],
) -> tuple[list[str], list[str], list[str]]:
    blockers: list[str] = []
    optimization: list[str] = []
    strategic: list[str] = []

    if float(stock_host.get("swap_used_pct", 0)) > 50:
        blockers.append(
            f"Stockenweiler host is under real memory pressure: swap used `{stock_host.get('swap_used_gib', 0)} GiB` / `{stock_host.get('swap_total_gib', 0)} GiB`."
        )
    for storage in stock_storages:
        if storage.get("active") and float(storage.get("used_pct", 0)) >= 80:
            blockers.append(
                f"Stockenweiler storage `{storage.get('storage')}` is at `{storage.get('used_pct')}%` and should not receive new backup or migration load yet."
            )
    for storage in anker_storages:
        if storage.get("storage") in {"pbs-interim", "pbs-usb"} and not storage.get("active"):
            blockers.append(f"Anker PBS path `{storage.get('storage')}` is not active; backup consolidation is still not green.")
    if next((item for item in anker_resources if item.get("vmid") == 240 and item.get("status") != "running"), None):
        blockers.append("VM 240 PBS is still stopped, so there is no current green dedicated PBS runtime on Anker.")
    if direct_checks.get("odoo_direct") != "200":
        blockers.append(f"Odoo direct runtime is not green from Anker host: HTTP `{direct_checks.get('odoo_direct', '000')}`.")
    if frontdoor_checks.get("odoo", {}).get("http_code") != "200":
        blockers.append(f"Odoo frontdoor is not green from StudioPC: HTTP `{frontdoor_checks.get('odoo', {}).get('http_code', '000')}`.")

    low_util_guests = [
        item
        for item in anker_resources
        if item.get("status") == "running" and float(item.get("mem_used_pct", 0)) <= 30 and float(item.get("mem_max_gib", 0)) >= 1
    ]
    for item in sorted(low_util_guests, key=lambda entry: float(entry.get("mem_max_gib", 0)), reverse=True)[:3]:
        optimization.append(
            f"Anker guest `{item.get('name')}` (`{item.get('vmid')}`) runs at only `{item.get('mem_used_pct')}%` RAM use and is a later rightsizing candidate."
        )

    high_mem_stock = top_pressure(stock_resources, field="mem_used_pct", threshold=85)
    for item in high_mem_stock[:4]:
        optimization.append(
            f"Stockenweiler guest `{item.get('name')}` (`{item.get('vmid')}`) is at `{item.get('mem_used_pct')}%` RAM use and should be reviewed before adding workloads."
        )

    radio_names = {str(item.get("name")) for item in stock_resources if item.get("status") == "running"}
    if {"azuracast-vm", "radio-wordpress-prod", "mariadb-server", "radio-api"}.issubset(radio_names):
        strategic.append(
            "Stockenweiler still carries a fragmented legacy yourparty stack across VM 210 azuracast-vm, CT 207 radio-wordpress-prod, CT 208 mariadb-server, and CT 211 radio-api."
        )
    strategic.append(
        "Odoo is runtime-green, but production-ready should mean a defined module/profile rollout, customer portal scope, backup/restore path, and mail/identity workflow, not only HTTP 200."
    )
    strategic.append(
        "Best-fit product model is Odoo as CRM/portal/business shell around radio, while AzuraCast remains the media engine rather than the master identity system for listeners."
    )
    strategic.append(
        "Home Assistant should stay separated per household first; later integration should expose selected entities only, not merge both households into one HA runtime."
    )
    strategic.append(
        "Before thinning Stockenweiler, capture the essential yourparty payload into Rothkreuz: AzuraCast station config, WordPress content, MariaDB data, and radio API/config."
    )
    return blockers, optimization, strategic


def build_report() -> dict[str, object]:
    anker_node_status = load_node_status(ANKER_SSH_TARGET, ANKER_NODE)
    stock_node_status = load_node_status(STOCK_SSH_TARGET, STOCK_NODE)
    anker_storages_raw = load_storages(ANKER_SSH_TARGET, ANKER_NODE)
    stock_storages_raw = load_storages(STOCK_SSH_TARGET, STOCK_NODE)
    anker_resources_raw = load_resources(ANKER_SSH_TARGET, ANKER_NODE)
    stock_resources_raw = load_resources(STOCK_SSH_TARGET, STOCK_NODE)
    stock_pct_configs = load_selected_pct_configs(STOCK_SSH_TARGET, [120, 207, 211])

    anker_storages = summarize_storage(anker_storages_raw)
    stock_storages = summarize_storage(stock_storages_raw)
    anker_resources = summarize_resources(anker_resources_raw)
    stock_resources = summarize_resources(stock_resources_raw)
    anker_host = host_summary(anker_node_status, ANKER_NODE)
    stock_host = host_summary(stock_node_status, STOCK_NODE)

    direct_checks = {name: remote_http_code(ANKER_SSH_TARGET, url) for name, url in ANKER_DIRECT_CHECKS.items()}
    frontdoor_checks = {name: curl_probe(url) for name, url in TAILSCALE_FRONTDOORS.items()}

    blockers, optimization, strategic = classify_blockers(
        anker_host,
        anker_storages,
        stock_host,
        stock_storages,
        anker_resources,
        stock_resources,
        direct_checks,
        frontdoor_checks,
    )

    odoo_frontdoor = frontdoor_checks.get("odoo", {})
    odoo_assessment = {
        "runtime_green": direct_checks.get("odoo_direct") == "200" and odoo_frontdoor.get("http_code") == "200",
        "direct_http_code": direct_checks.get("odoo_direct", "000"),
        "frontdoor_http_code": odoo_frontdoor.get("http_code", "000"),
        "assessment": "runtime_green_but_production_profile_pending",
        "production_ready_next": [
            "Freeze the exact Odoo product scope: CRM, invoicing, sales, project, helpdesk/customer portal only if intentionally needed.",
            "Define the portal/user model and mail workflow before onboarding external customers.",
            "Keep restore-proof and backup path visible; PBS is still not fully green.",
        ],
    }

    azuracast_assessment = {
        "anker_runtime_role": "frawo_hobby_media_engine",
        "listener_binding_recommendation": "Use Odoo for CRM, website, portal, newsletters, sponsors, and supporter flows; keep AzuraCast as streaming/schedule/metadata engine.",
        "legacy_stockenweiler_components": [
            "VM 210 azuracast-vm",
            "CT 207 radio-wordpress-prod",
            "CT 208 mariadb-server",
            "CT 211 radio-api",
        ],
        "before_thinning_stock": [
            "Export AzuraCast station configuration and media references.",
            "Capture WordPress content and relevant plugins/themes.",
            "Dump MariaDB data for the radio/web stack.",
            "Preserve the radio API/config payload and dependency notes.",
        ],
    }

    report = {
        "generated_at": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
        "access_paths": {
            "anker_management": ANKER_SSH_TARGET,
            "stock_management": STOCK_SSH_TARGET,
            "tailscale_frontdoor": TOOLBOX_FRONTDOOR_IP,
        },
        "summary": {
            "top_priority_issue": blockers[0] if blockers else "none",
            "blocker_count": len(blockers),
            "optimization_count": len(optimization),
            "strategic_count": len(strategic),
            "odoo_runtime_green": bool(odoo_assessment["runtime_green"]),
            "frontdoors_ok": sum(1 for item in frontdoor_checks.values() if item.get("http_code") in {"200", "302"}),
            "frontdoors_total": len(frontdoor_checks),
        },
        "anker": {
            "host": anker_host,
            "storages": anker_storages,
            "resources": anker_resources,
            "direct_checks": direct_checks,
        },
        "stockenweiler": {
            "host": stock_host,
            "storages": stock_storages,
            "resources": stock_resources,
            "selected_pct_configs": stock_pct_configs,
        },
        "frontdoors": frontdoor_checks,
        "blockers": blockers,
        "optimization_candidates": optimization,
        "strategic_recommendations": strategic,
        "odoo_assessment": odoo_assessment,
        "azuracast_assessment": azuracast_assessment,
        "recommended_next_order": [
            "Keep Anker stable; do not start broad migrations while PBS and Stockenweiler pressure remain open.",
            "Define the Odoo production profile and customer portal scope before calling it production-ready.",
            "Capture the essential yourparty payload from Stockenweiler into Rothkreuz before deleting or thinning radio/web components.",
            "Only after payload capture: retire duplicated Stockenweiler radio/web/api roles stepwise.",
            "Keep Home Assistant separated per household; integrate selected entities later via the management bridge.",
        ],
    }
    return report


def render_md(report: dict[str, object]) -> str:
    lines: list[str] = []
    summary = report.get("summary", {})
    anker = report.get("anker", {})
    stock = report.get("stockenweiler", {})
    anker_host = anker.get("host", {}) if isinstance(anker, dict) else {}
    stock_host = stock.get("host", {}) if isinstance(stock, dict) else {}
    odoo = report.get("odoo_assessment", {}) if isinstance(report.get("odoo_assessment"), dict) else {}
    azura = report.get("azuracast_assessment", {}) if isinstance(report.get("azuracast_assessment"), dict) else {}

    lines.append("# Platform Health Audit")
    lines.append("")
    lines.append(f"- Generated at: `{report.get('generated_at', 'unknown')}`")
    lines.append(f"- Anker management path: `{report.get('access_paths', {}).get('anker_management', '-')}`")
    lines.append(f"- Stockenweiler management path: `{report.get('access_paths', {}).get('stock_management', '-')}`")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- Top priority issue: {summary.get('top_priority_issue', 'none')}")
    lines.append(f"- Frontdoors green: `{summary.get('frontdoors_ok', 0)}` / `{summary.get('frontdoors_total', 0)}`")
    lines.append(f"- Odoo runtime green: `{str(odoo.get('runtime_green', False)).lower()}`")
    lines.append(f"- Blockers: `{summary.get('blocker_count', 0)}` / optimization candidates: `{summary.get('optimization_count', 0)}` / strategic recommendations: `{summary.get('strategic_count', 0)}`")
    lines.append("")
    lines.append("## Anker Host")
    lines.append("")
    lines.append(f"- Host: `{anker_host.get('hostname', '-')}` / `{anker_host.get('pve_version', '-')}`")
    lines.append(f"- Memory used: `{anker_host.get('memory_used_gib', 0)} GiB` / `{anker_host.get('memory_total_gib', 0)} GiB` (`{anker_host.get('memory_used_pct', 0)}%`) ")
    lines.append(f"- Rootfs used: `{anker_host.get('rootfs_used_gib', 0)} GiB` / `{anker_host.get('rootfs_total_gib', 0)} GiB` (`{anker_host.get('rootfs_used_pct', 0)}%`) ")
    lines.append(f"- Swap used: `{anker_host.get('swap_used_gib', 0)} GiB` / `{anker_host.get('swap_total_gib', 0)} GiB` (`{anker_host.get('swap_used_pct', 0)}%`) ")
    lines.append("- Storages:")
    for storage in anker.get("storages", [])[:5]:
        lines.append(
            f"  - `{storage.get('storage')}` `{storage.get('type')}` active=`{str(storage.get('active', False)).lower()}` used=`{storage.get('used_pct', 0)}%`"
        )
    lines.append("")
    lines.append("## Stockenweiler Host")
    lines.append("")
    lines.append(f"- Host: `{stock_host.get('hostname', '-')}` / `{stock_host.get('pve_version', '-')}`")
    lines.append(f"- Memory used: `{stock_host.get('memory_used_gib', 0)} GiB` / `{stock_host.get('memory_total_gib', 0)} GiB` (`{stock_host.get('memory_used_pct', 0)}%`) ")
    lines.append(f"- Rootfs used: `{stock_host.get('rootfs_used_gib', 0)} GiB` / `{stock_host.get('rootfs_total_gib', 0)} GiB` (`{stock_host.get('rootfs_used_pct', 0)}%`) ")
    lines.append(f"- Swap used: `{stock_host.get('swap_used_gib', 0)} GiB` / `{stock_host.get('swap_total_gib', 0)} GiB` (`{stock_host.get('swap_used_pct', 0)}%`) ")
    lines.append("- Storages:")
    for storage in stock.get("storages", [])[:6]:
        lines.append(
            f"  - `{storage.get('storage')}` `{storage.get('type')}` active=`{str(storage.get('active', False)).lower()}` used=`{storage.get('used_pct', 0)}%`"
        )
    lines.append("")
    lines.append("## Runtime Notes")
    lines.append("")
    lines.append(f"- Odoo direct HTTP: `{odoo.get('direct_http_code', '000')}` / frontdoor HTTP: `{odoo.get('frontdoor_http_code', '000')}`")
    lines.append(f"- Odoo assessment: `{odoo.get('assessment', '-')}`")
    lines.append(f"- AzuraCast role: `{azura.get('anker_runtime_role', '-')}`")
    lines.append(f"- Listener binding recommendation: {azura.get('listener_binding_recommendation', '-')}")
    lines.append("")
    lines.append("## Stockenweiler Legacy yourparty Payload")
    lines.append("")
    for item in azura.get("legacy_stockenweiler_components", []):
        lines.append(f"- {item}")
    lines.append("")
    lines.append("## Blockers")
    lines.append("")
    for item in report.get("blockers", []):
        lines.append(f"- {item}")
    lines.append("")
    lines.append("## Optimization Candidates")
    lines.append("")
    for item in report.get("optimization_candidates", []):
        lines.append(f"- {item}")
    lines.append("")
    lines.append("## Strategic Recommendations")
    lines.append("")
    for item in report.get("strategic_recommendations", []):
        lines.append(f"- {item}")
    lines.append("")
    lines.append("## Recommended Next Order")
    lines.append("")
    for item in report.get("recommended_next_order", []):
        lines.append(f"- {item}")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    report = build_report()
    REPORT_JSON.write_text(json.dumps(report, indent=2), encoding="utf-8")
    REPORT_MD.write_text(render_md(report), encoding="utf-8")
    print(str(REPORT_MD))


if __name__ == "__main__":
    main()
