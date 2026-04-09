#!/usr/bin/env python3
import argparse
import json
from datetime import date
from pathlib import Path


ALLOWED_STATUSES = {"pending", "passed", "failed", "waived"}


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Update one manual evidence entry in manifests/release_mvp_gate/manual_checks.json"
    )
    parser.add_argument("--id", required=True, help="Check id to update")
    parser.add_argument("--status", required=True, choices=sorted(ALLOWED_STATUSES))
    parser.add_argument("--evidence", default=None, help="Short evidence text")
    parser.add_argument(
        "--last-verified",
        default=None,
        help="Verification date in YYYY-MM-DD format",
    )
    parser.add_argument(
        "--file",
        default="manifests/release_mvp_gate/manual_checks.json",
        help="Path to manual checks JSON",
    )
    args = parser.parse_args()

    path = Path(args.file)
    data = json.loads(path.read_text(encoding="utf-8"))
    checks = data.get("checks", [])

    for check in checks:
        if check.get("id") == args.id:
            check["status"] = args.status
            if args.last_verified is not None:
                check["last_verified"] = args.last_verified
            elif args.status != "pending" and not check.get("last_verified"):
                check["last_verified"] = date.today().isoformat()

            if args.evidence is not None:
                check["evidence"] = args.evidence
            path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
            print(f"updated_id={args.id}")
            print(f"updated_status={args.status}")
            print(f"updated_file={path}")
            return 0

    print(f"error=manual_check_id_not_found:{args.id}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
