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
    blockers = data.get("current_blockers", [])
    onboarding = data.get("first_live_onboarding", {})
    playbooks = data.get("first_support_playbooks", [])
    probe_summary = data.get("legacy_access_probe_summary", {})
    browser_bookmarks = data.get("recovered_browser_bookmarks", [])
    host_key_evidence = data.get("legacy_host_key_evidence", [])
    local_access_hints = data.get("recovered_local_access_hints", [])
    phase_2_backlog = data.get("phase_2_backlog", {})
    bridge_candidate = phase_2_backlog.get("management_plane_bridge_candidate", {})
    service_candidates = phase_2_backlog.get("service_consolidation_candidates", [])
    migration_blockers = phase_2_backlog.get("migration_blockers", [])
    rollback_requirements = phase_2_backlog.get("rollback_requirements", [])

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
            "## Current Blockers",
            "",
        ]
    )

    if blockers:
        for blocker in blockers:
            lines.append(f"- {blocker}")
    else:
        lines.append("- none")

    lines.extend(
        [
            "",
            "## Legacy Access Probe",
            "",
        ]
    )

    if probe_summary.get("findings"):
        lines.append(f"- source: `{probe_summary.get('source', '-')}`")
        for finding in probe_summary.get("findings", []):
            if finding.get("dns_resolved"):
                addresses = ", ".join(finding.get("addresses", [])) or "-"
                if "https_status" in finding or "title" in finding:
                    lines.append(
                        f"- `{finding.get('service', '-')}`: `{finding.get('host', '-')}` -> `{addresses}` / HTTPS `{finding.get('https_status', '-')}` / `{finding.get('title', '-')}`"
                    )
                else:
                    lines.append(
                        f"- `{finding.get('service', '-')}`: `{finding.get('host', '-')}` -> `{addresses}` (`{finding.get('notes', '-')}`)"
                    )
            else:
                lines.append(
                    f"- `{finding.get('service', '-')}`: `{finding.get('host', '-')}` unresolved (`{finding.get('notes', '-')}`)"
                )
    else:
        lines.append("- none")

    lines.extend(
        [
            "",
            "## Recovered Browser Bookmarks",
            "",
        ]
    )

    if browser_bookmarks:
        for item in browser_bookmarks:
            lines.append(
                f"- `{item.get('service', '-')}` via `{item.get('app', '-')}`: `{item.get('bookmark_name', '-')}` -> `{item.get('bookmark_url', '-')}`"
            )
    else:
        lines.append("- none")

    lines.extend(
        [
            "",
            "## Recovered Local Access Hints",
            "",
        ]
    )

    if local_access_hints:
        for item in local_access_hints:
            lines.append(
                f"- `{item.get('service', '-')}` via `{item.get('method', '-')}`: `{item.get('value', '-')}` using `{item.get('credential_hint', '-')}`"
            )
    else:
        lines.append("- none")

    lines.extend(
        [
            "",
            "## Legacy Host Key Evidence",
            "",
        ]
    )

    if host_key_evidence:
        for item in host_key_evidence:
            hosts = ", ".join(item.get("hosts", [])) or "-"
            lines.append(
                f"- `{item.get('subject', '-')}`: `{hosts}` / same_host_key `{item.get('same_host_key', '-')}`"
            )
    else:
        lines.append("- none")

    lines.extend(
        [
            "",
            "## First Live Onboarding",
            "",
        ]
    )

    for item in onboarding.get("collect_fields", []):
        lines.append(f"- collect: `{item}`")

    for item in onboarding.get("success_criteria", []):
        lines.append(f"- done when: {item}")

    lines.extend(
        [
            "",
            "## First Support Playbooks",
            "",
        ]
    )

    if playbooks:
        for playbook in playbooks:
            lines.append(f"- `{playbook.get('id', '-')}`: {playbook.get('goal', '-')}")
    else:
        lines.append("- none")

    lines.extend(
        [
            "",
            "## Phase 2 Backlog",
            "",
        ]
    )

    if bridge_candidate:
        lines.append(
            f"- management plane candidate: `{bridge_candidate.get('preferred_primary_path', '-')}` / fallback `{bridge_candidate.get('recovery_fallback', '-')}` / status `{bridge_candidate.get('status', '-')}`"
        )
        for item in bridge_candidate.get("not_before", []):
            lines.append(f"- not before: {item}")
        for item in bridge_candidate.get("must_not_do", []):
            lines.append(f"- must not do: {item}")
    else:
        lines.append("- management plane candidate missing")

    if service_candidates:
        lines.append("- service candidates:")
        for item in service_candidates:
            lines.append(
                f"  - `{item.get('service', '-')}` -> phase_2 `{item.get('phase_2_mode', '-')}`, phase_3 `{item.get('phase_3_candidate', '-')}`"
            )
    else:
        lines.append("- service candidates missing")

    if migration_blockers:
        lines.append("- migration blockers:")
        for item in migration_blockers:
            lines.append(f"  - {item}")
    else:
        lines.append("- migration blockers missing")

    if rollback_requirements:
        lines.append("- rollback requirements:")
        for item in rollback_requirements:
            lines.append(f"  - {item}")
    else:
        lines.append("- rollback requirements missing")

    lines.extend(
        [
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
