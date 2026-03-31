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
WORK_LANES_PATH = ROOT_DIR / "manifests" / "work_lanes" / "current_plan.json"
RELEASE_MVP_GATE_JSON_PATH = ROOT_DIR / "artifacts" / "release_mvp_gate" / "latest_release_mvp_gate.json"
PUBLIC_IPV6_REPORT_PATH = ROOT_DIR / "artifacts" / "public_ipv6_exposure_audit" / "latest_report.md"
WEBSITE_RELEASE_GATE_DIR = ROOT_DIR / "artifacts" / "website_release_gate"
PRODUCTION_GATE_DIR = ROOT_DIR / "artifacts" / "production_gate"
CONTROL_SURFACE_ACTIONS_PATH = ROOT_DIR / "manifests" / "control_surface" / "actions.json"
HOSTS_PATH = ROOT_DIR / "ansible" / "inventory" / "hosts.yml"


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
    lines.append(f"- `goal`: {format_task_value(task.get('goal'))}")
    lines.append(f"- `done_when`: {format_task_value(task.get('done_when'))}")
    lines.append(f"- `blocked_by`: {format_task_value(task.get('blocked_by'))}")
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

    lanes = sorted(work_lanes.get("lanes", []), key=lambda item: int(item.get("priority", 999)))
    tasks = sorted(work_lanes.get("tasks", []), key=lambda item: int(item.get("order", 999)))
    active_lane = next((lane for lane in lanes if lane.get("status") == "active"), None)
    manual_tasks = [task for task in tasks if task.get("manual")]
    side_tasks = [task for task in tasks if not task.get("manual")]
    ready_actions = [action for action in control_surface["actions"] if action.get("status") == "ready"]
    backlog_actions = [action for action in control_surface["actions"] if action.get("status") == "backlog"]
    ready_groups = sorted({str(action["group"]) for action in ready_actions})
    passed_manual, pending_manual = summarize_manual_checks(release_gate)
    codex_status_counter = count_codex_check_statuses(release_gate)

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
