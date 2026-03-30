#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

REQUIRED_KEYS = {
    "id": str,
    "label": str,
    "group": str,
    "audience": str,
    "target_url": str,
    "target_kind": str,
    "requires_login": bool,
    "status": str,
    "verified": bool,
}
ALLOWED_STATUSES = {"ready", "verify", "backlog"}


def load_manifest(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_manifest(payload: dict) -> dict:
    errors: list[str] = []
    actions = payload.get("actions")
    if not isinstance(actions, list):
        return {"errors": ["actions must be a list"], "actions": []}

    ids: list[str] = []
    for index, action in enumerate(actions):
        if not isinstance(action, dict):
            errors.append(f"action[{index}] must be an object")
            continue

        for key, expected_type in REQUIRED_KEYS.items():
            value = action.get(key)
            if not isinstance(value, expected_type):
                errors.append(f"action[{index}].{key} must be {expected_type.__name__}")

        status = action.get("status")
        if status not in ALLOWED_STATUSES:
            errors.append(f"action[{index}].status must be one of {sorted(ALLOWED_STATUSES)}")

        if action.get("status") == "ready" and not action.get("target_url"):
            errors.append(f"action[{index}] ready actions require a target_url")

        ids.append(action.get("id", f"missing-{index}"))

    duplicate_ids = sorted(action_id for action_id, count in Counter(ids).items() if count > 1)
    for duplicate_id in duplicate_ids:
        errors.append(f"duplicate action id: {duplicate_id}")

    ready_actions = [action for action in actions if action.get("status") == "ready"]
    ready_groups = sorted({action.get("group", "") for action in ready_actions})
    return {
        "errors": errors,
        "actions": actions,
        "ready_actions": ready_actions,
        "ready_groups": ready_groups,
    }


def write_report(result: dict, output_path: Path) -> None:
    lines = [
        "# Control Surface Actions Report",
        "",
        f"Actions total: `{len(result['actions'])}`",
        f"Ready actions: `{len(result['ready_actions'])}`",
        f"Ready groups: `{', '.join(result['ready_groups']) or '-'}`",
        "",
        "## Errors",
        "",
    ]

    if result["errors"]:
        for error in result["errors"]:
            lines.append(f"- `{error}`")
    else:
        lines.append("- none")

    lines.extend(["", "## Ready Actions", ""])
    if result["ready_actions"]:
        for action in result["ready_actions"]:
            lines.append(
                f"- `{action['group']}` / `{action['label']}` -> `{action['target_url']}` "
                f"(login_required=`{str(action['requires_login']).lower()}`)"
            )
    else:
        lines.append("- none")

    output_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate manifests/control_surface/actions.json")
    parser.add_argument(
        "--manifest",
        default="manifests/control_surface/actions.json",
        help="Relative path to the control surface actions manifest.",
    )
    parser.add_argument(
        "--report",
        default="",
        help="Optional markdown report output path.",
    )
    args = parser.parse_args()

    workspace = Path(__file__).resolve().parent.parent
    manifest_path = workspace / args.manifest
    if not manifest_path.exists():
        print(f"control_surface_actions_error=missing_manifest:{manifest_path}")
        return 1

    payload = load_manifest(manifest_path)
    result = validate_manifest(payload)

    print(f"control_surface_actions_manifest={manifest_path.as_posix()}")
    print(f"control_surface_actions_total={len(result['actions'])}")
    print(f"control_surface_ready_count={len(result['ready_actions'])}")
    print(f"control_surface_ready_groups={','.join(result['ready_groups']) or '-'}")
    print(f"control_surface_error_count={len(result['errors'])}")
    print(
        "control_surface_actions_check_status="
        + ("green" if not result["errors"] else "red")
    )

    if args.report:
        report_path = workspace / args.report
        report_path.parent.mkdir(parents=True, exist_ok=True)
        write_report(result, report_path)
        print(f"report_path={report_path.as_posix()}")

    return 0 if not result["errors"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
