#!/usr/bin/env python3
"""Render a concise operator brief from the Stockenweiler inventory."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a concise Stockenweiler support brief.")
    parser.add_argument(
        "--inventory",
        default="manifests/stockenweiler/site_inventory.json",
        help="Path to the Stockenweiler inventory JSON",
    )
    parser.add_argument(
        "--output",
        default="artifacts/stockenweiler_inventory/support_brief.md",
        help="Where to write the generated markdown brief",
    )
    args = parser.parse_args()

    inventory_path = Path(args.inventory)
    if not inventory_path.exists():
        print(f"stockenweiler_support_brief_error=missing_inventory:{inventory_path}")
        return 1

    data = json.loads(inventory_path.read_text(encoding="utf-8"))
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    domain = data.get("external_domain", {}).get("canonical", "-")
    access = data.get("access_model", {})
    facts = data.get("current_known_facts", {})
    targets = data.get("first_support_targets", [])
    conflicts = data.get("legacy_conflicts_to_revalidate", [])

    lines = [
        "# Stockenweiler Support Brief",
        "",
        f"- site: `{data.get('site_name', '-')}`",
        f"- support label: `{data.get('support_label', '-')}`",
        f"- canonical external name: `{domain}`",
        f"- primary remote access: `{access.get('primary_remote_access', '-')}`",
        f"- fallback remote access: `{access.get('fallback_remote_access', '-')}`",
        f"- WAN admin exposure allowed: `{access.get('wan_admin_exposure_allowed', '-')}`",
        "",
        "## First Support Targets",
        "",
    ]
    for target in targets:
        lines.append(f"- {target}")

    lines.extend(
        [
            "",
            "## Current Known Local Facts",
            "",
            f"- Router: `{facts.get('router', {}).get('friendly_name', '-')}` @ `{facts.get('router', {}).get('ip', '-')}`",
            f"- Proxmox: `{facts.get('proxmox_host', {}).get('friendly_name', '-')}` @ `{facts.get('proxmox_host', {}).get('ip', '-')}`",
            f"- Home Assistant: `{facts.get('home_assistant', {}).get('friendly_name', '-')}` @ `{facts.get('home_assistant', {}).get('ip', '-')}`",
            f"- Printer: `{facts.get('printer_scanner', {}).get('friendly_name', '-')}` @ `{facts.get('printer_scanner', {}).get('ip', '-')}`",
            f"- MagentaTV: `{facts.get('magenta_tv', {}).get('friendly_name', '-')}` @ `{facts.get('magenta_tv', {}).get('ip', '-')}`",
            "",
            "## Do Not Do",
            "",
            "- do not expose admin paths to the internet",
            "- do not build site-to-site VPN in V1",
            "- do not mix the Stockenweiler LAN into the FraWo production LAN",
            "",
            "## Legacy Conflicts To Revalidate",
            "",
        ]
    )

    if conflicts:
        for conflict in conflicts:
            lines.append(
                f"- `{conflict.get('topic', '-')}`: best guess `{conflict.get('current_best_guess', '-')}`, conflicting legacy `{conflict.get('conflicting_legacy_value', '-')}`"
            )
    else:
        lines.append("- none")

    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"stockenweiler_support_brief={output_path.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
