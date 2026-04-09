#!/usr/bin/env python3
import argparse
import json
from datetime import datetime
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Safely prefill the PBS rebuild device contract with serials only."
    )
    parser.add_argument("--boot-serial", default="", help="Approved boot USB serial")
    parser.add_argument("--datastore-serial", default="", help="Approved datastore device serial")
    parser.add_argument("--approved-by", default="", help="Operator name to record")
    parser.add_argument("--change-ticket", default="", help="Optional ticket or change reference")
    parser.add_argument(
        "--contract",
        default="manifests/pbs_rebuild/device_contract.json",
        help="Path to the contract file",
    )
    parser.add_argument(
        "--write",
        action="store_true",
        help="Actually write the contract file. Without this flag, prints the resulting JSON only.",
    )
    args = parser.parse_args()

    contract_path = Path(args.contract)
    if contract_path.exists():
        contract = json.loads(contract_path.read_text(encoding="utf-8"))
    else:
        contract = {
            "boot_usb": {},
            "datastore_device": {},
        }

    boot_usb = contract.setdefault("boot_usb", {})
    datastore = contract.setdefault("datastore_device", {})

    boot_usb["serial"] = args.boot_serial.strip()
    datastore["serial"] = args.datastore_serial.strip()

    # Keep destructive approvals explicitly false during prefill.
    boot_usb["allow_destroy"] = False
    datastore["allow_destroy"] = False
    datastore["allow_reformat_existing_filesystem"] = False

    contract["approved_by"] = args.approved_by.strip()
    contract["approved_at"] = datetime.now().isoformat(timespec="seconds") if args.approved_by.strip() else ""
    contract["change_ticket"] = args.change_ticket.strip()

    rendered = json.dumps(contract, indent=2) + "\n"

    if args.write:
        contract_path.parent.mkdir(parents=True, exist_ok=True)
        contract_path.write_text(rendered, encoding="utf-8")
        print(f"pbs_contract_prefill_written={contract_path}")
    else:
        print(rendered, end="")

    print("pbs_contract_prefill_note=destructive approvals remain false until manually elevated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
