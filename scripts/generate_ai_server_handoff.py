#!/usr/bin/env python3
"""Generate a single-file AI handoff for current Homeserver 2027 planning."""

from __future__ import annotations

import json
import re
import subprocess
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Iterable

import yaml


ROOT_DIR = Path(__file__).resolve().parents[1]
OUTPUT_PATH = ROOT_DIR / "AI_SERVER_HANDOFF.md"
AI_BOOTSTRAP_CONTEXT_PATH = ROOT_DIR / "AI_BOOTSTRAP_CONTEXT.md"
OPS_HOME_PATH = ROOT_DIR / "OPS_HOME.md"
OPERATOR_TODO_QUEUE_PATH = ROOT_DIR / "OPERATOR_TODO_QUEUE.md"
MARRIAGE_PLAN_PATH = ROOT_DIR / "ANKER_STOCKENWEILER_MARRIAGE_PLAN.md"
AI_OPERATING_MODEL_PATH = ROOT_DIR / "AI_OPERATING_MODEL.md"
WORK_LANES_PATH = ROOT_DIR / "manifests" / "work_lanes" / "current_plan.json"
RELEASE_MVP_GATE_JSON_PATH = ROOT_DIR / "artifacts" / "release_mvp_gate" / "latest_release_mvp_gate.json"
PUBLIC_IPV6_REPORT_PATH = ROOT_DIR / "artifacts" / "public_ipv6_exposure_audit" / "latest_report.md"
WEBSITE_RELEASE_GATE_DIR = ROOT_DIR / "artifacts" / "website_release_gate"
PRODUCTION_GATE_DIR = ROOT_DIR / "artifacts" / "production_gate"
CONTROL_SURFACE_ACTIONS_PATH = ROOT_DIR / "manifests" / "control_surface" / "actions.json"
HOSTS_PATH = ROOT_DIR / "ansible" / "inventory" / "hosts.yml"
STOCKENWEILER_INVENTORY_PATH = ROOT_DIR / "manifests" / "stockenweiler" / "site_inventory.json"
STOCKENWEILER_PVE_PROBE_PATH = ROOT_DIR / "artifacts" / "stockenweiler_inventory" / "latest_pve_storage_probe.json"
STOCKENWEILER_WG_INVENTORY_PATH = ROOT_DIR / "artifacts" / "stockenweiler_inventory" / "latest_wireguard_inventory.json"
CONTROL_PLANE_REPORT_PATH = ROOT_DIR / "artifacts" / "control_plane" / "latest_report.json"
ESTATE_CENSUS_REPORT_PATH = ROOT_DIR / "artifacts" / "estate_census" / "latest_report.json"
PLATFORM_HEALTH_REPORT_PATH = ROOT_DIR / "artifacts" / "platform_health" / "latest_report.json"
CICD_DELIVERY_FACTORY_REPORT_PATH = ROOT_DIR / "artifacts" / "cicd_delivery_factory" / "latest_report.md"
CICD_DELIVERY_FACTORY_PREFLIGHT_PATH = ROOT_DIR / "artifacts" / "cicd_delivery_factory" / "latest_preflight.json"
PORTAL_UCG_PILOT_PREFLIGHT_PATH = ROOT_DIR / "artifacts" / "ucg_portal_pilot_preflight" / "latest_report.json"
COOLIFY_MANAGEMENT_HOST_AUDIT_PATH = ROOT_DIR / "artifacts" / "coolify_management_host" / "latest_report.json"
STORAGE_OPTIMIZATION_REPORT_PATH = ROOT_DIR / "artifacts" / "storage_optimization" / "latest_report.json"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def format_mtime(path: Path) -> str:
    return datetime.fromtimestamp(path.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")


def run_git(*args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=ROOT_DIR,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return ""
    return result.stdout.strip()


def count_git_dirty_files() -> int:
    output = run_git("status", "--short")
    if not output:
        return 0
    return len([line for line in output.splitlines() if line.strip()])


def extract_section(markdown: str, heading: str) -> list[str]:
    lines = markdown.splitlines()
    capture = False
    collected: list[str] = []
    prefix = f"## {heading}"
    for line in lines:
        if line.startswith("## "):
            if capture:
                break
            capture = line.strip() == prefix
            continue
        if capture:
            collected.append(line)
    while collected and not collected[0].strip():
        collected.pop(0)
    while collected and not collected[-1].strip():
        collected.pop()
    return collected


def extract_bullets(markdown: str, heading: str) -> list[str]:
    lines = extract_section(markdown, heading)
    bullets: list[str] = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("- "):
            bullets.append(stripped[2:].strip())
    return bullets


def latest_gate_file(parent: Path, filename: str) -> Path | None:
    candidates = [path / filename for path in parent.iterdir() if path.is_dir() and (path / filename).exists()]
    if not candidates:
        return None
    return max(candidates, key=lambda path: path.parent.name)


def parse_gate_markdown(path: Path | None) -> dict[str, object]:
    if path is None or not path.exists():
        return {"path": None, "decision": "unknown", "blocked_reasons": []}
    text = read_text(path)
    decision_match = re.search(r"Decision:\s*`([^`]+)`", text)
    blocked_reasons: list[str] = []
    in_blocked = False
    for line in text.splitlines():
        if line.startswith("## "):
            in_blocked = line.strip() == "## Blocked Reasons"
            continue
        if in_blocked and line.strip().startswith("- "):
            blocked_reasons.append(line.strip()[2:].strip())
    return {
        "path": path,
        "decision": decision_match.group(1) if decision_match else "unknown",
        "blocked_reasons": blocked_reasons,
    }


def load_release_mvp_gate() -> dict[str, object]:
    return json.loads(read_text(RELEASE_MVP_GATE_JSON_PATH))


def load_work_lanes() -> dict[str, object]:
    return json.loads(read_text(WORK_LANES_PATH))


def load_control_surface() -> dict[str, object]:
    return json.loads(read_text(CONTROL_SURFACE_ACTIONS_PATH))


def load_inventory_host_count() -> int:
    inventory = yaml.safe_load(read_text(HOSTS_PATH))

    def collect_hosts(node: object) -> int:
        count = 0
        if isinstance(node, dict):
            hosts = node.get("hosts")
            if isinstance(hosts, dict):
                count += len(hosts)
            for value in node.values():
                count += collect_hosts(value)
        elif isinstance(node, list):
            for value in node:
                count += collect_hosts(value)
        return count

    return collect_hosts(inventory)


def load_json(path: Path) -> dict[str, object]:
    if not path.exists():
        return {}
    return json.loads(read_text(path))


def parse_public_ipv6_report(path: Path) -> dict[str, object]:
    text = read_text(path)
    timestamp_match = re.search(r"- timestamp: `([^`]+)`", text)
    total_match = re.search(r"- total_checks: `([^`]+)`", text)
    open_match = re.search(r"- open_checks: `([^`]+)`", text)
    open_findings: list[str] = []
    capture = False
    for line in text.splitlines():
        if line.startswith("## "):
            capture = line.strip() == "## Open Findings"
            continue
        if capture and line.strip().startswith("- "):
            open_findings.append(line.strip()[2:].strip())
    return {
        "timestamp": timestamp_match.group(1) if timestamp_match else "unknown",
        "total_checks": int(total_match.group(1)) if total_match else 0,
        "open_checks": int(open_match.group(1)) if open_match else 0,
        "open_findings": open_findings,
    }


def summarize_manual_checks(release_gate: dict[str, object]) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    checks = release_gate.get("manual_checks", [])
    if not isinstance(checks, list):
        return [], []
    passed = [item for item in checks if isinstance(item, dict) and item.get("status") == "passed"]
    pending = [item for item in checks if isinstance(item, dict) and item.get("status") != "passed"]
    return passed, pending


def count_codex_check_statuses(release_gate: dict[str, object]) -> Counter:
    checks = release_gate.get("critical_codex_checks", [])
    counter: Counter = Counter()
    if isinstance(checks, list):
        for item in checks:
            if isinstance(item, dict):
                counter[str(item.get("status", "unknown"))] += 1
    return counter


def shorten_reason(text: str) -> str:
    return text.replace("critical MVP manual evidence not green: ", "").replace("critical website manual evidence not green: ", "").replace("critical website Codex check not green: ", "")


def render_bullets(lines: Iterable[str], indent: str = "- ") -> str:
    rendered = [f"{indent}{line}" for line in lines]
    return "\n".join(rendered) if rendered else f"{indent}none"


def format_task_value(value: object) -> str:
    if isinstance(value, list):
        return ", ".join(f"`{item}`" for item in value) if value else "`none`"
    if value in (None, ""):
        return "`none`"
    return str(value)


def render_task_card(task: dict[str, object]) -> list[str]:
    lines = [f"### `{task['id']}`", ""]
    lines.append(f"- `status`: `{task.get('status', 'unknown')}`")
    lines.append(f"- `lane`: {format_task_value(task.get('lane'))}")
    if task.get("change_class") is not None:
        lines.append(f"- `change_class`: {format_task_value(task.get('change_class'))}")
    lines.append(f"- `goal`: {format_task_value(task.get('goal'))}")
    lines.append(f"- `done_when`: {format_task_value(task.get('done_when'))}")
    lines.append(f"- `blocked_by`: {format_task_value(task.get('blocked_by'))}")
    if task.get("preflight_checks") is not None:
        lines.append(f"- `preflight_checks`: {format_task_value(task.get('preflight_checks'))}")
    if task.get("rollback_plan") is not None:
        lines.append(f"- `rollback_plan`: {format_task_value(task.get('rollback_plan'))}")
    if task.get("verification_commands") is not None:
        lines.append(f"- `verification_commands`: {format_task_value(task.get('verification_commands'))}")
    if task.get("last_verified_at") is not None:
        lines.append(f"- `last_verified_at`: {format_task_value(task.get('last_verified_at'))}")
    lines.append(f"- `next_operator_action`: {format_task_value(task.get('next_operator_action'))}")
    lines.append(f"- `next_codex_action`: {format_task_value(task.get('next_codex_action'))}")
    return lines


def main() -> int:
    ai_bootstrap_text = read_text(AI_BOOTSTRAP_CONTEXT_PATH)
    ops_home_text = read_text(OPS_HOME_PATH)
    release_gate = load_release_mvp_gate()
    work_lanes = load_work_lanes()
    website_gate = parse_gate_markdown(latest_gate_file(WEBSITE_RELEASE_GATE_DIR, "website_release_gate.md"))
    production_gate = parse_gate_markdown(latest_gate_file(PRODUCTION_GATE_DIR, "production_gate.md"))
    ipv6_report = parse_public_ipv6_report(PUBLIC_IPV6_REPORT_PATH)
    control_surface = load_control_surface()
    stockenweiler_inventory = load_json(STOCKENWEILER_INVENTORY_PATH)
    stockenweiler_pve_probe = load_json(STOCKENWEILER_PVE_PROBE_PATH)
    stockenweiler_wg_inventory = load_json(STOCKENWEILER_WG_INVENTORY_PATH)
    control_plane_report = load_json(CONTROL_PLANE_REPORT_PATH)
    estate_census_report = load_json(ESTATE_CENSUS_REPORT_PATH)
    platform_health_report = load_json(PLATFORM_HEALTH_REPORT_PATH)
    cicd_preflight = load_json(CICD_DELIVERY_FACTORY_PREFLIGHT_PATH)
    portal_pilot_preflight = load_json(PORTAL_UCG_PILOT_PREFLIGHT_PATH)
    coolify_mgmt_audit = load_json(COOLIFY_MANAGEMENT_HOST_AUDIT_PATH)
    storage_optimization_report = load_json(STORAGE_OPTIMIZATION_REPORT_PATH)

    lanes = sorted(work_lanes.get("lanes", []), key=lambda item: int(item.get("priority", 999)))
    tasks = sorted(work_lanes.get("tasks", []), key=lambda item: int(item.get("order", 999)))
    operating_model = work_lanes.get("operating_model", {})
    active_lane = next((lane for lane in lanes if lane.get("status") == "active"), None)
    manual_tasks = [task for task in tasks if task.get("manual")]
    side_tasks = [task for task in tasks if not task.get("manual")]
    ready_actions = [action for action in control_surface["actions"] if action.get("status") == "ready"]
    backlog_actions = [action for action in control_surface["actions"] if action.get("status") == "backlog"]
    ready_groups = sorted({str(action["group"]) for action in ready_actions})
    passed_manual, pending_manual = summarize_manual_checks(release_gate)
    codex_status_counter = count_codex_check_statuses(release_gate)
    stock_endpoints = stockenweiler_inventory.get("endpoints", [])
    stock_blockers = stockenweiler_inventory.get("current_blockers", [])
    stock_access = stockenweiler_inventory.get("access_model", {})
    stock_visible_summary = stockenweiler_inventory.get("browser_visible_host_check_summary", {})
    stock_public_truth = stockenweiler_inventory.get("public_truth_check_summary", {})
    stock_remote_path = stockenweiler_inventory.get("remote_path_probe_summary", {})
    stock_management_bridge = stockenweiler_inventory.get("management_bridge_summary", {})
    stock_probe_status = stockenweiler_pve_probe.get("probe_status", "unknown")
    stock_probe_target = stockenweiler_pve_probe.get("target", "unknown")
    stock_wg_reachable = stockenweiler_wg_inventory.get("reachable", False)
    estate_summary = estate_census_report.get("summary", {})
    platform_summary = platform_health_report.get("summary", {})
    estate_frontdoors = estate_census_report.get("frontdoors", [])
    estate_blockers = estate_census_report.get("blockers", [])
    estate_recommended_next = estate_census_report.get("recommended_next_order", [])
    estate_transition_sequence = estate_census_report.get("transition_sequence", [])

    branch = run_git("rev-parse", "--abbrev-ref", "HEAD") or "unknown"
    dirty_count = count_git_dirty_files()
    inventory_host_count = load_inventory_host_count()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    estate_bullets = extract_bullets(ai_bootstrap_text, "Estate In One Screen")
    service_bullets = extract_bullets(ai_bootstrap_text, "Service And Page Map")
    rules_bullets = extract_bullets(ai_bootstrap_text, "Access And Secret Rules")
    next_reads = [line.strip()[2:].strip() for line in extract_section(ops_home_text, "Jetzt zuerst lesen") if line.strip().startswith("- ")]

    website_source_path = website_gate["path"]
    production_source_path = production_gate["path"]
    website_blockers = [shorten_reason(item) for item in website_gate["blocked_reasons"][:6]]
    lines: list[str] = []
    lines.append("# AI Server Handoff")
    lines.append("")
    lines.append("Automatisch generierter Ein-Datei-Handoff fuer den aktuellen Homeserver-Stand.")
    lines.append("Keine Secrets. Keine Passwoerter. Diese Datei ist dafuer gedacht, sie direkt an eine andere KI zu geben.")
    lines.append("")
    lines.append("## Nutzung")
    lines.append("")
    lines.append("- Primaerer Read-First fuer eine andere KI: diese Datei")
    lines.append("- Wenn tieferer Repo-Kontext noetig ist: `INTRODUCTION_PROMPT.md`, `OPS_HOME.md`, `OPERATOR_TODO_QUEUE.md`")
    lines.append("- Diese Datei neu erzeugen mit: `python scripts/generate_ai_server_handoff.py`")
    lines.append("")
    lines.append("## Generierung")
    lines.append("")
    lines.append(f"- Generated at: `{now}`")
    lines.append(f"- Workspace root: `{ROOT_DIR}`")
    lines.append(f"- Git branch: `{branch}`")
    lines.append(f"- Pending git changes: `{dirty_count}`")
    lines.append(f"- Managed hosts in inventory: `{inventory_host_count}`")
    lines.append("")
    lines.append("## Source Freshness")
    lines.append("")
    lines.append(f"- `AI_BOOTSTRAP_CONTEXT.md`: `{format_mtime(AI_BOOTSTRAP_CONTEXT_PATH)}`")
    lines.append(f"- `OPS_HOME.md`: `{format_mtime(OPS_HOME_PATH)}`")
    lines.append(f"- `OPERATOR_TODO_QUEUE.md`: `{format_mtime(OPERATOR_TODO_QUEUE_PATH)}`")
    lines.append(f"- `manifests/work_lanes/current_plan.json`: `{format_mtime(WORK_LANES_PATH)}`")
    lines.append(f"- `artifacts/release_mvp_gate/latest_release_mvp_gate.json`: `{format_mtime(RELEASE_MVP_GATE_JSON_PATH)}`")
    lines.append(f"- `artifacts/public_ipv6_exposure_audit/latest_report.md`: `{format_mtime(PUBLIC_IPV6_REPORT_PATH)}`")
    if ESTATE_CENSUS_REPORT_PATH.exists():
        lines.append(f"- `artifacts/estate_census/latest_report.json`: `{format_mtime(ESTATE_CENSUS_REPORT_PATH)}`")
    if PORTAL_UCG_PILOT_PREFLIGHT_PATH.exists():
        lines.append(f"- `artifacts/ucg_portal_pilot_preflight/latest_report.json`: `{format_mtime(PORTAL_UCG_PILOT_PREFLIGHT_PATH)}`")
    if website_source_path:
        lines.append(f"- `{website_source_path.relative_to(ROOT_DIR)}`: `{format_mtime(website_source_path)}`")
    if production_source_path:
        lines.append(f"- `{production_source_path.relative_to(ROOT_DIR)}`: `{format_mtime(production_source_path)}`")
    lines.append(f"- `manifests/control_surface/actions.json`: `{format_mtime(CONTROL_SURFACE_ACTIONS_PATH)}`")
    lines.append("")
    lines.append("## Estate Snapshot")
    lines.append("")
    lines.append(render_bullets(estate_bullets))
    lines.append("")
    lines.append("## Core Service Map")
    lines.append("")
    lines.append(render_bullets(service_bullets))
    lines.append("")
    lines.append("## Current Release State")
    lines.append("")
    if active_lane:
        lines.append(f"- Active delivery lane: `{active_lane['label']}`")
    lines.append(f"- Business MVP gate: `{release_gate['decision']}`")
    lines.append(f"- Business MVP critical Codex checks: `passed={codex_status_counter.get('passed', 0)}` / `non-passed={sum(v for k, v in codex_status_counter.items() if k != 'passed')}`")
    lines.append(f"- Business MVP manual checks: `passed={len(passed_manual)}` / `pending_or_failed={len(pending_manual)}`")
    lines.append(f"- Public website gate: `{website_gate['decision']}`")
    lines.append(f"- Production certification gate: `{production_gate['decision']}`")
    lines.append(f"- Public IPv6 exposure audit: `open_checks={ipv6_report['open_checks']}` / `total_checks={ipv6_report['total_checks']}`")
    lines.append("")
    lines.append("## AI Operating Model")
    lines.append("")
    if operating_model:
        lines.append(f"- Model: `{operating_model.get('name', 'unknown')}`")
        lines.append(f"- Autonomy: `{operating_model.get('autonomy', 'unknown')}`")
        lines.append(f"- Primary end state: `{operating_model.get('primary_end_state', 'unknown')}`")
        agent_split = operating_model.get("agent_split", {})
        if isinstance(agent_split, dict):
            lines.append(
                f"- Roles: `codex={agent_split.get('codex', '-')}` / `gemini={agent_split.get('gemini', '-')}` / `operator={agent_split.get('operator', '-')}`"
            )
        execution_loop = operating_model.get("execution_loop", [])
        if execution_loop:
            lines.append(f"- Execution loop: `{', '.join(str(item) for item in execution_loop)}`")
        stop_categories = operating_model.get("mandatory_stop_categories", [])
        if stop_categories:
            lines.append("- Mandatory stop categories:")
            for item in stop_categories:
                lines.append(f"  - `{item}`")
    else:
        lines.append("- none")
    lines.append("")
    lines.append("## Control Plane Snapshot")
    lines.append("")
    if control_plane_report:
        lines.append(f"- Workspace Pyrefly disabled: `{str(control_plane_report.get('workspace_pyrefly_disabled', False)).lower()}`")
        lines.append(f"- Pyrefly process present: `{str(control_plane_report.get('pyrefly_process_present', False)).lower()}`")
        lines.append(f"- Stale ssh helpers: `{control_plane_report.get('stale_ssh_count', 0)}`")
        lines.append(f"- Stale mail powershell: `{control_plane_report.get('stale_mail_powershell_count', 0)}`")
        tailscale_report = control_plane_report.get("tailscale", {})
        if isinstance(tailscale_report, dict):
            lines.append(
                f"- Tailscale backend: `{tailscale_report.get('backend_state', 'unknown')}` / stockenweiler route visible `{tailscale_report.get('stockenweiler_route_present', False)}`"
            )
        lines.append(f"- ssh stock-pve: `{control_plane_report.get('ssh_stock_pve', {}).get('status', 'unknown')}`")
        lines.append(f"- Local WireGuard VPN service running: `{str(control_plane_report.get('wireguard_vpn_running', False)).lower()}`")
        lines.append("- Important split: local StudioPC WireGuard is legacy/recovery only; it is not the same thing as a later professional site-to-site WireGuard between UCG and Stockenweiler.")
        for item in control_plane_report.get("observations", [])[:3]:
            lines.append(f"- {item}")
    else:
        lines.append("- No control-plane audit artifact yet.")
    lines.append("")
    lines.append("## Estate Census Snapshot")
    lines.append("")
    if estate_census_report:
        lines.append(f"- Generated at: `{estate_census_report.get('generated_at', 'unknown')}`")
        lines.append(
            f"- Tailscale peers: online `{estate_summary.get('online_tailscale_peers', 0)}` / offline `{estate_summary.get('offline_tailscale_peers', 0)}` / routed `{estate_summary.get('routed_tailscale_peers', 0)}`"
        )
        lines.append(
            f"- Running estate nodes: anker containers `{estate_summary.get('anker_running_containers', 0)}`, anker VMs `{estate_summary.get('anker_running_vms', 0)}`, stock containers `{estate_summary.get('stock_running_containers', 0)}`, stock VMs `{estate_summary.get('stock_running_vms', 0)}`"
        )
        lines.append(
            f"- Working toolbox frontdoors: `{estate_summary.get('frontdoors_ok', 0)}` / `{estate_summary.get('frontdoors_total', 0)}`; Stockenweiler public legacy hosts green `{estate_summary.get('stock_public_ok', 0)}` / `{estate_summary.get('stock_public_total', 0)}`"
        )
        local_network = estate_census_report.get("local_network", {})
        if isinstance(local_network, dict):
            local_ips = local_network.get("ip_addresses", [])
            if local_ips:
                lines.append(
                    f"- Local active IPv4 interfaces: `{', '.join(f"{item.get('InterfaceAlias', '-')}: {item.get('IPAddress', '-')}/{item.get('PrefixLength', '-')}`".strip('`') for item in local_ips[:4])}`"
                )
        degraded_frontdoors = [item for item in estate_frontdoors if item.get("status") != "ok"]
        if degraded_frontdoors:
            lines.append("- Degraded frontdoors:")
            for item in degraded_frontdoors[:3]:
                lines.append(f"  - `{item.get('name', '-')}` -> HTTP `{item.get('http_code', '000')}` via `{item.get('url', '-')}`")
        if estate_blockers:
            lines.append("- Current estate blockers:")
            for item in estate_blockers[:5]:
                lines.append(f"  - {item}")
        if estate_recommended_next:
            lines.append("- Current working order:")
            for item in estate_recommended_next[:3]:
                lines.append(f"  - {item}")
        if estate_transition_sequence:
            lines.append("- Canonical Anker transition sequence:")
            for item in estate_transition_sequence[:5]:
                lines.append(f"  - {item}")
    else:
        lines.append("- No estate census artifact yet.")
    lines.append("")
    lines.append("## Platform Health Snapshot")
    lines.append("")
    if platform_health_report:
        lines.append(f"- Generated at: `{platform_health_report.get('generated_at', 'unknown')}`")
        lines.append(f"- Top priority issue: {platform_summary.get('top_priority_issue', 'none')}")
        lines.append(
            f"- Frontdoors green: `{platform_summary.get('frontdoors_ok', 0)}` / `{platform_summary.get('frontdoors_total', 0)}`; Odoo runtime green `{str(platform_summary.get('odoo_runtime_green', False)).lower()}`"
        )
        anker_host = platform_health_report.get('anker', {}).get('host', {})
        stock_host = platform_health_report.get('stockenweiler', {}).get('host', {})
        if isinstance(anker_host, dict):
            lines.append(
                f"- Anker host: RAM `{anker_host.get('memory_used_gib', 0)} / {anker_host.get('memory_total_gib', 0)} GiB`, rootfs `{anker_host.get('rootfs_used_pct', 0)}%`, swap `{anker_host.get('swap_used_pct', 0)}%`"
            )
        if isinstance(stock_host, dict):
            lines.append(
                f"- Stockenweiler host: RAM `{stock_host.get('memory_used_gib', 0)} / {stock_host.get('memory_total_gib', 0)} GiB`, rootfs `{stock_host.get('rootfs_used_pct', 0)}%`, swap `{stock_host.get('swap_used_pct', 0)}%`"
            )
        blockers = platform_health_report.get('blockers', [])
        if blockers:
            lines.append("- Current blockers:")
            for item in blockers[:4]:
                lines.append(f"  - {item}")
        recommendations = platform_health_report.get('recommended_next_order', [])
        if recommendations:
            lines.append("- Recommended next order:")
            for item in recommendations[:4]:
                lines.append(f"  - {item}")
    else:
        lines.append("- No platform health artifact yet.")
    lines.append("")
    lines.append("## CI/CD Snapshot")
    lines.append("")
    if CICD_DELIVERY_FACTORY_REPORT_PATH.exists():
        lines.append("- Delivery factory status: `defined_not_deployed`")
        if cicd_preflight:
            summary = cicd_preflight.get("summary", {})
            lines.append(f"- Safe scope now: `{summary.get('safe_scope_now', 'unknown')}`")
            lines.append(
                f"- Verified start state: workflows `{cicd_preflight.get('workflow_file_count', 0)}`, Dockerfiles `{cicd_preflight.get('dockerfile_count', 0)}`, ready apps `{summary.get('factory_ready_app_count', 0)}`"
            )
            open_prereq = cicd_preflight.get("open_prerequisites", [])
            if open_prereq:
                lines.append(f"- Open factory prerequisites: `{len(open_prereq)}`")
        lines.append("- CD controller role: `Coolify as delivery-only layer`")
        lines.append("- Registry contract: `GHCR v1` for `ghcr.io/wolfeetech/frawo/radio-player-frontend`")
        lines.append("- Env/secret contract: `dev/prod env examples plus future Coolify webhook secret names`")
        lines.append("- Coolify host contract: `dedicated internal Anker management node preferred; toolbox only temporary fallback`")
        lines.append("- First deploy bundle: `deployment/factory/apps/radio-player-frontend/compose.yaml`")
        if coolify_mgmt_audit:
            lines.append(f"- Management-node recommendation: `{coolify_mgmt_audit.get('recommendation', '-')}`")
        if storage_optimization_report:
            lines.append("- Storage pressure snapshot: `artifacts/storage_optimization/latest_report.md`")
        lines.append("- Dev/Prod model: `develop -> dev`, `main/tag -> prod`")
        lines.append("- Backup/Restore rule: `stateless public = redeploy`, `stateful internal = PBS/VM restore plus app-native data restore`")
        lines.append("- Factory report: `artifacts/cicd_delivery_factory/latest_report.md`")
    else:
        lines.append("- No CI/CD delivery factory report yet.")
    lines.append("")
    lines.append("## UCG Pilot Snapshot")
    lines.append("")
    if portal_pilot_preflight:
        lines.append(f"- Pilot: `{portal_pilot_preflight.get('pilot', 'portal')}`")
        lines.append(
            f"- Ready for gated runtime change: `{str(portal_pilot_preflight.get('ready_for_gated_runtime_change', False)).lower()}`"
        )
        lines.append(f"- Recommendation: `{portal_pilot_preflight.get('recommendation', '-')}`")
        lines.append("- Runtime runbook: `UCG_PORTAL_PILOT_RUNBOOK.md`")
        summary = portal_pilot_preflight.get('portal_frontdoor', {}).get('status_payload_summary', {})
        lines.append(
            f"- Portal status snapshot: platform_core `{summary.get('platform_core', '-')}`, healthy `{summary.get('healthy_services', 0)}` / `{summary.get('total_services', 0)}`"
        )
        for item in portal_pilot_preflight.get('checks', [])[:4]:
            lines.append(f"  - `{item.get('id', '-')}` -> `{'ok' if item.get('ok') else 'fail'}` / {item.get('evidence', '-')}")
    else:
        lines.append("- No portal pilot preflight artifact yet.")
    lines.append("")
    lines.append("## Current Lane Model")
    lines.append("")
    for lane in lanes:
        lines.append(f"- `{lane['label']}` -> `{lane['status']}`")
        lines.append(f"  - goal: {lane['goal']}")
    lines.append("")
    lines.append("## Business MVP Blockers")
    lines.append("")
    if pending_manual:
        for item in pending_manual:
            lines.append(f"- `{item['id']}`: `{item['status']}`")
            lines.append(f"  - {item['evidence']}")
    else:
        lines.append("- none")
    lines.append("")
    lines.append("## Public Website Release State")
    lines.append("")
    lines.append("- This track is separate from the internal business MVP.")
    if website_source_path:
        lines.append(f"- Latest website gate source: `{website_source_path.relative_to(ROOT_DIR)}`")
    if website_blockers:
        lines.append("- Current blocked reasons:")
        for blocker in website_blockers:
            lines.append(f"  - {blocker}")
    else:
        lines.append("- No blocked reasons parsed.")
    lines.append("")
    lines.append("## Security Posture Snapshot")
    lines.append("")
    lines.append(f"- Latest public IPv6 re-audit timestamp: `{ipv6_report['timestamp']}`")
    lines.append(f"- Public IPv6 direct exposure findings open: `{ipv6_report['open_checks']}`")
    if ipv6_report["open_findings"] and ipv6_report["open_findings"] != ["none"]:
        for finding in ipv6_report["open_findings"]:
            lines.append(f"- Open finding: {finding}")
    else:
        lines.append("- Verified closed in the current audit: direct public IPv6 checks for `nextcloud`, `odoo`, `paperless`, `vaultwarden`, `storage-node`, `homeassistant`.")
    lines.append("- Important limitation: this is risk reduction, not a promise of zero risk.")
    lines.append("- Public edge and TLS are still not in a final green release state.")
    lines.append("")
    lines.append("## Stockenweiler Snapshot")
    lines.append("")
    lines.append("- Lane state remains `watch`; no live rollout, no site marriage, no site-to-site VPN.")
    lines.append(f"- Primary remote access model: `{stock_access.get('primary_remote_access', '-')}` / fallback `{stock_access.get('fallback_remote_access', '-')}`")
    lines.append(f"- Stockenweiler endpoints currently modeled: `{len(stock_endpoints)}`")
    lines.append(f"- Current Stockenweiler blockers: `{len(stock_blockers)}`")
    lines.append("- Current direction:")
    lines.append("  - parents' scan folders stay local first")
    lines.append("  - later document automation should use a separate Stockenweiler Paperless DB")
    lines.append("  - radio is later hosted on the most stable hardware, not by ideology of site")
    lines.append("  - Stockenweiler PVE HDDs are only a future PBS/storage complement candidate")
    if isinstance(stock_public_truth, dict) and stock_public_truth.get("findings"):
        lines.append(f"- Public truth / DynDNS split: dyn-dns-like `{stock_public_truth.get('dyn_dns_like_count', 0)}`")
        for item in stock_public_truth.get("current_mapping_observations", [])[:3]:
            lines.append(f"  - {item}")
    if isinstance(stock_remote_path, dict) and stock_remote_path:
        lines.append(
            f"- Remote path truth: tailscale `{stock_remote_path.get('tailscale_backend_state', '-')}`, route_all `{stock_remote_path.get('tailscale_route_all', '-')}`, stockenweiler route visible `{stock_remote_path.get('stockenweiler_subnet_route_present', '-')}`"
        )
        lines.append(
            f"  - ssh `{stock_remote_path.get('ssh_pve_target', '-')}` is `{stock_remote_path.get('ssh_pve_status', '-')}`; AnyDesk candidates `{stock_remote_path.get('anydesk_candidate_count', 0)}`"
        )
        for item in stock_remote_path.get("observations", [])[:2]:
            lines.append(f"  - {item}")
    if isinstance(stock_management_bridge, dict) and stock_management_bridge:
        lines.append(
            f"- Management bridge: state `{stock_management_bridge.get('current_state', '-')}`, target `{stock_management_bridge.get('primary_candidate', '-')}`"
        )
        lines.append(
            f"  - fallback `{stock_management_bridge.get('fallback_path', '-')}` / direct local WG reachable `{stock_management_bridge.get('local_direct_wireguard_reachable', '-')}`"
        )
        lines.append("  - architecture note: current admin bridge is Tailscale-first, but the later permanent site bridge may become native WireGuard between UCG and Stockenweiler after read-only inventory of the existing Stockenweiler WG topology")
        lines.append(f"  - next operator action: {stock_management_bridge.get('next_operator_action', '-')}")
    if stockenweiler_wg_inventory:
        lines.append(
            f"- Existing WireGuard truth: reachable `{str(stock_wg_reachable).lower()}`, server `{stockenweiler_wg_inventory.get('server_profile', {}).get('address', '-')}` on port `{stockenweiler_wg_inventory.get('server_profile', {}).get('listen_port', '-')}`, client profiles `{len(stockenweiler_wg_inventory.get('client_profiles', []))}`"
        )
        for item in stockenweiler_wg_inventory.get("conclusions", [])[:2]:
            lines.append(f"  - {item}")
    if isinstance(stock_visible_summary, dict) and stock_visible_summary.get("findings"):
        lines.append(
            f"- Visible legacy host check: reachable `{stock_visible_summary.get('currently_reachable_count', 0)}` / broken `{stock_visible_summary.get('currently_broken_count', 0)}`"
        )
        for item in stock_visible_summary.get("operator_relevant_observations", [])[:3]:
            lines.append(f"  - {item}")
    lines.append(f"- Latest Stockenweiler PVE read-only probe: `{stock_probe_status}` on target `{stock_probe_target}`")
    if stock_probe_status != "reachable":
        stderr = str(stockenweiler_pve_probe.get("stderr", "")).strip()
        if stderr:
            lines.append(f"- Latest probe failure: `{stderr}`")
    lines.append("")
    lines.append("## Surface Control V1")
    lines.append("")
    lines.append(f"- Ready actions: `{len(ready_actions)}`")
    lines.append(f"- Ready groups: `{', '.join(ready_groups)}`")
    for action in ready_actions:
        lines.append(f"- `{action['label']}` -> `{action['target_url']}`")
    if backlog_actions:
        lines.append("- Backlog-only actions remain hidden:")
        for action in backlog_actions:
            lines.append(f"  - `{action['label']}` (`{action['group']}`)")
    lines.append("")
    lines.append("## Access And Secret Rules")
    lines.append("")
    lines.append(render_bullets(rules_bullets))
    lines.append("")
    lines.append("## Current Operator Queue")
    lines.append("")
    if manual_tasks:
        for task in manual_tasks:
            lines.extend(render_task_card(task))
            lines.append("")
    else:
        lines.append("- none")
        lines.append("")
    lines.append("## Visible Side Strands")
    lines.append("")
    if side_tasks:
        for task in side_tasks:
            lines.extend(render_task_card(task))
            lines.append("")
    else:
        lines.append("- none")
        lines.append("")
    lines.append("## Recommended Next Planning Order")
    lines.append("")
    for task in manual_tasks:
        lines.append(f"- First close `{task['id']}` in `{task['lane']}`.")
    for task in side_tasks:
        lines.append(f"- Keep `{task['id']}` visible in `{task['lane']}` without promoting it into active delivery.")
    lines.append("")
    lines.append("## Canonical Files To Read Next")
    lines.append("")
    if AI_OPERATING_MODEL_PATH.exists():
        lines.append("- `AI_OPERATING_MODEL.md`")
    if MARRIAGE_PLAN_PATH.exists():
        lines.append("- `ANKER_STOCKENWEILER_MARRIAGE_PLAN.md`")
    lines.append(render_bullets(next_reads[:12]))
    lines.append("")
    lines.append("## Generator Notes")
    lines.append("")
    lines.append("- This file is generated from current source-of-truth docs and latest gate/audit artifacts.")
    lines.append("- If a source file is older than the newest hardening change, prefer the fresher artifact listed in `Source Freshness`.")
    lines.append("- For runtime operations, do not invent credentials or provider-side state that is not visible in the cited sources.")

    OUTPUT_PATH.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    print(f"output_path={OUTPUT_PATH}")
    print(f"business_mvp_decision={release_gate['decision']}")
    print(f"website_decision={website_gate['decision']}")
    print(f"production_decision={production_gate['decision']}")
    print(f"surface_ready_actions={len(ready_actions)}")
    print(f"ipv6_open_checks={ipv6_report['open_checks']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
