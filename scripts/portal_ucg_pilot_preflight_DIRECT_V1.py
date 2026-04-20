#!/usr/bin/env python3
"""Collect a read-only preflight snapshot for the first UCG portal pilot."""

from __future__ import annotations

import json
import subprocess
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_DIR = ROOT / "artifacts" / "ucg_portal_pilot_preflight"
REPORT_JSON = ARTIFACT_DIR / "latest_report.json"
REPORT_MD = ARTIFACT_DIR / "latest_report.md"
UCG_ARCH_PATH = ROOT / "UCG_NETWORK_ARCHITECTURE.md"


def now_local() -> str:
    return datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M:%S")


def http_probe(url: str, timeout: int = 10) -> dict[str, object]:
    try:
        with urllib.request.urlopen(url, timeout=timeout) as response:
            body = response.read().decode("utf-8", errors="replace")
            return {
                "ok": True,
                "url": url,
                "http_code": response.getcode(),
                "body": body,
                "error": "",
            }
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        return {
            "ok": False,
            "url": url,
            "http_code": exc.code,
            "body": body,
            "error": str(exc),
        }
    except Exception as exc:
        return {
            "ok": False,
            "url": url,
            "http_code": 0,
            "body": "",
            "error": str(exc),
        }


def ssh_probe(target: str, command: str) -> dict[str, object]:
    completed = subprocess.run(
        ["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=8", target, command],
        capture_output=True,
        text=True,
        check=False,
    )
    lines = [line.strip() for line in completed.stdout.splitlines() if line.strip()]
    return {
        "target": target,
        "ok": completed.returncode == 0,
        "stdout_lines": lines,
        "stderr": completed.stderr.strip(),
    }


def ssh_capture(target: str, command: str) -> dict[str, object]:
    completed = subprocess.run(
        ["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=8", target, command],
        capture_output=True,
        text=True,
        check=False,
    )
    return {
        "target": target,
        "ok": completed.returncode == 0,
        "stdout": completed.stdout.strip(),
        "stderr": completed.stderr.strip(),
    }


def documentation_check() -> dict[str, object]:
    text = UCG_ARCH_PATH.read_text(encoding="utf-8") if UCG_ARCH_PATH.exists() else ""
    has_pilot_section = "### `portal`-Pilot-Preflight" in text
    has_snapshot_rule = "Snapshot-/Rollback-Pfad" in text
    has_verify_rule = "estate_census" in text and "AI_SERVER_HANDOFF.md" in text
    return {
        "ok": has_pilot_section and has_snapshot_rule and has_verify_rule,
        "has_pilot_section": has_pilot_section,
        "has_snapshot_rule": has_snapshot_rule,
        "has_verify_rule": has_verify_rule,
    }


def build_report() -> dict[str, object]:
    portal_frontdoor = http_probe("http://100.82.26.53:8447/")
    portal_status = http_probe("http://100.82.26.53:8447/status.json")
    portal_internal = http_probe("http://100.82.26.53/")
    portal_internal_status = http_probe("http://100.82.26.53/status.json")
    anker_ssh = ssh_probe("root@100.69.179.87", "hostname; pveversion | head -1")
    stock_ssh = ssh_probe("stock-pve", "hostname; pveversion | head -1")
    toolbox_target_ip = ssh_capture(
        "root@100.69.179.87",
        "pct exec 100 -- sh -lc \"ip -4 addr show dev eth0 | grep -F '10.1.0.20/24'\"",
    )
    portal_target_status = ssh_capture(
        "root@100.69.179.87",
        "pct exec 100 -- sh -lc \"curl -fsS -H 'Host: 100.82.26.53' http://10.1.0.20/status.json\"",
    )
    doc = documentation_check()

    status_payload: dict[str, object] = {}
    if portal_status["http_code"] == 200 and portal_status["body"]:
        try:
            status_payload = json.loads(str(portal_status["body"]))
        except json.JSONDecodeError:
            status_payload = {}

    healthy_services = int(status_payload.get("healthy_services", 0) or 0)
    total_services = int(status_payload.get("total_services", 0) or 0)
    platform_core = str(status_payload.get("platform_core", "unknown"))
    portal_status_green = portal_status["http_code"] == 200 and total_services > 0 and healthy_services == total_services and platform_core == "ok"
    portal_target_payload: dict[str, object] = {}
    if portal_target_status["ok"] and portal_target_status["stdout"]:
        try:
            portal_target_payload = json.loads(str(portal_target_status["stdout"]))
        except json.JSONDecodeError:
            portal_target_payload = {}
    target_platform_core = str(portal_target_payload.get("platform_core", "unknown"))
    target_healthy_services = int(portal_target_payload.get("healthy_services", 0) or 0)
    target_total_services = int(portal_target_payload.get("total_services", 0) or 0)
    portal_target_green = (
        portal_target_status["ok"]
        and target_total_services > 0
        and target_healthy_services == target_total_services
        and target_platform_core == "ok"
    )

    checks = [
        {
            "id": "portal_frontdoor_http",
            "ok": portal_frontdoor["http_code"] == 200,
            "evidence": f"HTTP {portal_frontdoor['http_code']} via {portal_frontdoor['url']}",
        },
        {
            "id": "portal_frontdoor_status_json",
            "ok": portal_status_green,
            "evidence": f"HTTP {portal_status['http_code']}, platform_core={platform_core}, healthy={healthy_services}/{total_services}",
        },
        {
            "id": "portal_internal_hostname",
            "ok": portal_internal["http_code"] == 200,
            "evidence": f"HTTP {portal_internal['http_code']} via {portal_internal['url']}",
        },
        {
            "id": "portal_internal_status_json",
            "ok": portal_internal_status["http_code"] == 200,
            "evidence": f"HTTP {portal_internal_status['http_code']} via {portal_internal_status['url']}",
        },
        {
            "id": "anker_management_ssh",
            "ok": anker_ssh["ok"],
            "evidence": "; ".join(anker_ssh["stdout_lines"]) if anker_ssh["stdout_lines"] else anker_ssh["stderr"],
        },
        {
            "id": "stock_management_ssh",
            "ok": stock_ssh["ok"],
            "evidence": "; ".join(stock_ssh["stdout_lines"]) if stock_ssh["stdout_lines"] else stock_ssh["stderr"],
        },
        {
            "id": "pilot_documentation_present",
            "ok": doc["ok"],
            "evidence": f"pilot_section={doc['has_pilot_section']} snapshot_rule={doc['has_snapshot_rule']} verify_rule={doc['has_verify_rule']}",
        },
        {
            "id": "toolbox_target_ip_alias_active",
            "ok": toolbox_target_ip["ok"],
            "evidence": toolbox_target_ip["stdout"] or toolbox_target_ip["stderr"],
        },
        {
            "id": "portal_target_ip_vhost_status_json",
            "ok": portal_target_green,
            "evidence": f"platform_core={target_platform_core}, healthy={target_healthy_services}/{target_total_services}",
        },
    ]

    ready = all(bool(item["ok"]) for item in checks)
    runtime_active = toolbox_target_ip["ok"] and portal_target_green
    return {
        "generated_at": now_local(),
        "pilot": "portal",
        "change_class": "read_only",
        "ready_for_gated_runtime_change": ready,
        "runtime_alias_active": runtime_active,
        "checks": checks,
        "portal_frontdoor": {
            "root": {k: v for k, v in portal_frontdoor.items() if k != "body"},
            "status_json": {k: v for k, v in portal_status.items() if k != "body"},
            "status_payload_summary": {
                "platform_core": platform_core,
                "healthy_services": healthy_services,
                "total_services": total_services,
            },
        },
        "portal_internal": {
            "root": {k: v for k, v in portal_internal.items() if k != "body"},
            "status_json": {k: v for k, v in portal_internal_status.items() if k != "body"},
        },
        "portal_target_ip": {
            "target_ip": "10.1.0.20",
            "alias_probe": {k: v for k, v in toolbox_target_ip.items() if k != "target"},
            "status_payload_summary": {
                "platform_core": target_platform_core,
                "healthy_services": target_healthy_services,
                "total_services": target_total_services,
            },
        },
        "management_paths": {
            "anker": anker_ssh,
            "stockenweiler": stock_ssh,
        },
        "documentation": doc,
        "recommendation": (
            "portal_pilot_runtime_green"
            if runtime_active and ready
            else (
                "portal_pilot_preflight_green_waiting_for_gated_runtime_change"
                if ready
                else "fix_preflight_findings_before_any_runtime_portal_cutover"
            )
        ),
    }


def write_outputs(report: dict[str, object]) -> None:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_JSON.write_text(json.dumps(report, indent=2), encoding="utf-8")

    lines = [
        "# UCG Portal Pilot Preflight",
        "",
        f"- generated_at: `{report.get('generated_at', 'unknown')}`",
        f"- pilot: `{report.get('pilot', 'portal')}`",
        f"- change_class: `{report.get('change_class', 'read_only')}`",
        f"- ready_for_gated_runtime_change: `{str(report.get('ready_for_gated_runtime_change', False)).lower()}`",
        f"- runtime_alias_active: `{str(report.get('runtime_alias_active', False)).lower()}`",
        f"- recommendation: `{report.get('recommendation', '-')}`",
        "",
        "## Checks",
        "",
    ]

    for item in report.get("checks", []):
        state = "ok" if item.get("ok") else "fail"
        lines.append(f"- `{item.get('id', '-')}` -> `{state}` / {item.get('evidence', '-')}")

    summary = report.get("portal_frontdoor", {}).get("status_payload_summary", {})
    lines.extend(
        [
            "",
            "## Portal Status Summary",
            "",
            f"- platform_core: `{summary.get('platform_core', '-')}`",
            f"- healthy_services: `{summary.get('healthy_services', 0)}` / `{summary.get('total_services', 0)}`",
            f"- frontdoor_root_http: `{report.get('portal_frontdoor', {}).get('root', {}).get('http_code', 0)}`",
            f"- internal_root_http: `{report.get('portal_internal', {}).get('root', {}).get('http_code', 0)}`",
            f"- target_ip: `{report.get('portal_target_ip', {}).get('target_ip', '-')}`",
            f"- target_platform_core: `{report.get('portal_target_ip', {}).get('status_payload_summary', {}).get('platform_core', '-')}`",
            f"- target_healthy_services: `{report.get('portal_target_ip', {}).get('status_payload_summary', {}).get('healthy_services', 0)}` / `{report.get('portal_target_ip', {}).get('status_payload_summary', {}).get('total_services', 0)}`",
        ]
    )

    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    report = build_report()
    write_outputs(report)
    print(f"report_json={REPORT_JSON}")
    print(f"report_md={REPORT_MD}")
    print(f"ready_for_gated_runtime_change={str(report['ready_for_gated_runtime_change']).lower()}")
    print(f"recommendation={report['recommendation']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
