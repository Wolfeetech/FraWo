#!/usr/bin/env python3
"""Validate and summarize the Stockenweiler support inventory."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path


def build_report(data: dict, inventory_path: Path, status_counts: Counter[str], issues: list[str]) -> str:
    external_domain = data.get("external_domain", {})
    access_model = data.get("access_model", {})
    current_known_facts = data.get("current_known_facts", {})
    legacy_conflicts = data.get("legacy_conflicts_to_revalidate", [])

    lines = [
        "# Stockenweiler Inventory Report",
        "",
        f"Inventory source: `{inventory_path.as_posix()}`",
        "",
        "## Canonical Domain",
        "",
        f"- canonical: `{external_domain.get('canonical', '-')}`",
        f"- legacy: {', '.join(f'`{item}`' for item in external_domain.get('legacy', [])) or '-' }",
        "",
        "## Access Model",
        "",
        f"- primary remote access: `{access_model.get('primary_remote_access', '-')}`",
        f"- fallback remote access: `{access_model.get('fallback_remote_access', '-')}`",
        f"- WAN admin exposure allowed: `{access_model.get('wan_admin_exposure_allowed', '-')}`",
        f"- site-to-site VPN allowed: `{access_model.get('site_to_site_vpn_allowed', '-')}`",
        "",
        "## Current Known Facts",
        "",
    ]

    router = current_known_facts.get("router", {})
    proxmox = current_known_facts.get("proxmox_host", {})
    ha = current_known_facts.get("home_assistant", {})
    printer = current_known_facts.get("printer_scanner", {})
    magenta = current_known_facts.get("magenta_tv", {})
    facts = [
        ("router", router.get("friendly_name", "-"), router.get("ip", "-")),
        ("proxmox", proxmox.get("friendly_name", "-"), proxmox.get("ip", "-")),
        ("home_assistant", ha.get("friendly_name", "-"), ha.get("ip", "-")),
        ("printer_scanner", printer.get("friendly_name", "-"), printer.get("ip", "-")),
        ("magenta_tv", magenta.get("friendly_name", "-"), magenta.get("ip", "-")),
    ]
    for key, name, ip in facts:
        lines.append(f"- `{key}`: `{name}` @ `{ip}`")

    lines.extend(
        [
            "",
        "## Endpoint Status Counts",
        "",
    ]
    )
    for status, count in sorted(status_counts.items()):
        lines.append(f"- `{status}`: `{count}`")

    lines.extend(["", "## Issues", ""])
    if issues:
        for issue in issues:
            lines.append(f"- {issue}")
    else:
        lines.append("- none")

    lines.extend(["", "## Legacy Conflicts To Revalidate", ""])
    if legacy_conflicts:
        for conflict in legacy_conflicts:
            lines.append(
                f"- `{conflict.get('topic', '-')}`: best guess `{conflict.get('current_best_guess', '-')}`, conflicting legacy `{conflict.get('conflicting_legacy_value', '-')}`"
            )
    else:
        lines.append("- none")

    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate and summarize manifests/stockenweiler/site_inventory.json")
    parser.add_argument(
        "--inventory",
        default="manifests/stockenweiler/site_inventory.json",
        help="Path to the Stockenweiler inventory JSON",
    )
    parser.add_argument(
        "--report",
        help="Optional markdown report output path",
    )
    args = parser.parse_args()

    inventory_path = Path(args.inventory)
    if not inventory_path.exists():
        print(f"stockenweiler_inventory_error=missing_inventory:{inventory_path}")
        return 1

    data = json.loads(inventory_path.read_text(encoding="utf-8"))

    issues: list[str] = []
    external_domain = data.get("external_domain", {})
    access_model = data.get("access_model", {})
    endpoints = data.get("endpoints", [])
    legacy_conflicts = data.get("legacy_conflicts_to_revalidate", [])
    status_counts = Counter(item.get("status", "unknown") for item in endpoints)

    canonical_domain = external_domain.get("canonical", "")
    if canonical_domain != "online-prinz.de":
        issues.append("canonical external domain is not online-prinz.de")
    if access_model.get("primary_remote_access") != "tailscale":
        issues.append("primary remote access is not tailscale")
    if access_model.get("fallback_remote_access") != "anydesk":
        issues.append("fallback remote access is not anydesk")
    if access_model.get("wan_admin_exposure_allowed") is not False:
        issues.append("WAN admin exposure must remain disabled")
    if access_model.get("site_to_site_vpn_allowed") is not False:
        issues.append("site-to-site VPN must remain disabled in V1")
    if not endpoints:
        issues.append("no endpoints defined in inventory")

    pending_inventory_count = status_counts.get("pending_inventory", 0)
    needs_revalidation_count = status_counts.get("legacy_fact_needs_revalidation", 0)
    legacy_conflict_count = len(legacy_conflicts)
    structural_status = "passed" if not issues else "failed"

    print(f"inventory_path={inventory_path.as_posix()}")
    print(f"stockenweiler_external_domain={canonical_domain or '-'}")
    print(f"stockenweiler_legacy_domain_count={len(external_domain.get('legacy', []))}")
    print(f"stockenweiler_endpoint_count={len(endpoints)}")
    print(f"stockenweiler_pending_inventory_count={pending_inventory_count}")
    print(f"stockenweiler_revalidation_count={needs_revalidation_count}")
    print(f"stockenweiler_legacy_conflict_count={legacy_conflict_count}")
    print(f"stockenweiler_inventory_check_status={structural_status}")

    if args.report:
        report_path = Path(args.report)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(
            build_report(data, inventory_path, status_counts, issues),
            encoding="utf-8",
        )
        print(f"stockenweiler_inventory_report={report_path.as_posix()}")

    return 0 if structural_status == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
