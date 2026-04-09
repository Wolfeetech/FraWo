#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "${ROOT_DIR}/scripts/inventory_remote.sh"

TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
REPORT_DIR="${ROOT_DIR}/artifacts/pbs_rebuild_contract/${TIMESTAMP}"
JSON_REPORT="${REPORT_DIR}/contract_check.json"
MD_REPORT="${REPORT_DIR}/report.md"
CONTRACT_FILE="${PBS_REBUILD_CONTRACT_FILE:-${ROOT_DIR}/manifests/pbs_rebuild/device_contract.json}"

mkdir -p "${REPORT_DIR}"

read_hostvar() {
  local key="$1"
  python3 - <<'PY' "${ROOT_DIR}/ansible/inventory/host_vars/proxmox.yml" "$key"
import sys
import yaml

path = sys.argv[1]
key = sys.argv[2]
with open(path, "r", encoding="utf-8") as handle:
    data = yaml.safe_load(handle)
print(data[key])
PY
}

DATSTORE_MOUNT_PATH="$(read_hostvar proxmox_pbs_datastore_mount_path)"
STORAGE_ID="$(read_hostvar proxmox_pbs_data_storage_id)"

block_json="$(run_proxmox_remote "lsblk -J -b -d -o PATH,SIZE,TYPE,TRAN,RM,HOTPLUG,FSTYPE,LABEL,MOUNTPOINT,MODEL,SERIAL")"
block_json_file="$(mktemp)"
trap 'rm -f "${block_json_file}"' EXIT
printf '%s\n' "${block_json}" > "${block_json_file}"

python3 - <<'PY' "${CONTRACT_FILE}" "${JSON_REPORT}" "${MD_REPORT}" "${block_json_file}" "${DATSTORE_MOUNT_PATH}" "${STORAGE_ID}"
import json
import sys
from pathlib import Path

contract_path = Path(sys.argv[1])
json_report = Path(sys.argv[2])
md_report = Path(sys.argv[3])
block_json_path = Path(sys.argv[4])
datastore_mount_path = sys.argv[5]
storage_id = sys.argv[6]

devices = json.loads(block_json_path.read_text(encoding="utf-8")).get("blockdevices", [])

if contract_path.exists():
    contract = json.loads(contract_path.read_text(encoding="utf-8"))
else:
    contract = {}

boot_contract = contract.get("boot_usb", {})
datastore_contract = contract.get("datastore_device", {})

def normalize_str(value):
    return str(value or "").strip()

def normalize_bool(value):
    return bool(value)

def find_by_serial(serial):
    serial = normalize_str(serial)
    if not serial:
        return None
    for device in devices:
        if normalize_str(device.get("serial")) == serial:
            return device
    return None

def gib_from_bytes(value):
    try:
        return round(int(value) / (1024 ** 3), 2)
    except Exception:
        return 0.0

def device_view(device):
    if not device:
        return None
    return {
        "path": device.get("path") or "",
        "size_gib": gib_from_bytes(device.get("size") or 0),
        "fstype": normalize_str(device.get("fstype")),
        "label": normalize_str(device.get("label")),
        "mountpoint": normalize_str(device.get("mountpoint")),
        "model": normalize_str(device.get("model")),
        "serial": normalize_str(device.get("serial")),
        "transport": normalize_str(device.get("tran")),
    }

boot_serial = normalize_str(boot_contract.get("serial"))
datastore_serial = normalize_str(datastore_contract.get("serial"))
boot_device = find_by_serial(boot_serial)
datastore_device = find_by_serial(datastore_serial)

boot_min_gib = float(boot_contract.get("min_gib") or 0)
boot_max_gib = float(boot_contract.get("max_gib") or 0)
datastore_min_gib = float(datastore_contract.get("min_gib") or 0)
boot_allow_destroy = normalize_bool(boot_contract.get("allow_destroy"))
datastore_allow_destroy = normalize_bool(datastore_contract.get("allow_destroy"))
datastore_allow_reformat = normalize_bool(datastore_contract.get("allow_reformat_existing_filesystem"))

approved_by = normalize_str(contract.get("approved_by"))
approved_at = normalize_str(contract.get("approved_at"))
change_ticket = normalize_str(contract.get("change_ticket"))

findings = []

if not boot_serial:
    findings.append("Boot USB serial is not approved in the device contract.")
if not datastore_serial:
    findings.append("Datastore device serial is not approved in the device contract.")
if not approved_by or not approved_at:
    findings.append("Device contract is missing operator approval metadata.")

if boot_serial and not boot_device:
    findings.append(f"Approved boot USB serial `{boot_serial}` is not currently visible on Proxmox.")
if datastore_serial and not datastore_device:
    findings.append(f"Approved datastore serial `{datastore_serial}` is not currently visible on Proxmox.")

if boot_device:
    boot_size_gib = gib_from_bytes(boot_device.get("size") or 0)
    if boot_size_gib == 0:
        findings.append("Approved boot USB is visible but reports zero capacity / no medium.")
    if boot_min_gib and boot_size_gib < boot_min_gib:
        findings.append(f"Approved boot USB is only `{boot_size_gib} GiB`, below the required `{boot_min_gib} GiB`.")
    if boot_max_gib and boot_size_gib > boot_max_gib:
        findings.append(f"Approved boot USB is `{boot_size_gib} GiB`, above the expected max `{boot_max_gib} GiB`.")
    if normalize_str(boot_device.get("tran")) != "usb":
        findings.append("Approved boot device is not reported as USB transport.")

if datastore_device:
    datastore_size_gib = gib_from_bytes(datastore_device.get("size") or 0)
    if datastore_size_gib == 0:
        findings.append("Approved datastore device is visible but reports zero capacity.")
    if datastore_min_gib and datastore_size_gib < datastore_min_gib:
        findings.append(f"Approved datastore device is only `{datastore_size_gib} GiB`, below the required `{datastore_min_gib} GiB`.")
    if normalize_str(datastore_device.get("fstype")) and not datastore_allow_reformat:
        findings.append("Approved datastore device already has a filesystem and reformat is not approved in the contract.")
    mountpoint = normalize_str(datastore_device.get("mountpoint"))
    if mountpoint and mountpoint != datastore_mount_path:
        findings.append(f"Approved datastore device is mounted at `{mountpoint}`, not at the expected PBS path `{datastore_mount_path}`.")

if boot_serial and datastore_serial and boot_serial == datastore_serial:
    findings.append("Boot USB and datastore device serials are identical; roles must be separated.")

if boot_serial and not boot_allow_destroy:
    findings.append("Boot USB destructive approval is still false in the device contract.")
if datastore_serial and not datastore_allow_destroy:
    findings.append("Datastore destructive approval is still false in the device contract.")

recommendation = "blocked_wait_for_explicit_device_contract"
if boot_serial and datastore_serial and approved_by and approved_at:
    recommendation = "blocked_wait_for_visible_hardware"
if not findings:
    recommendation = "ready_for_guarded_pbs_datastore_prepare"

report = {
    "contract_path": str(contract_path),
    "datastore_mount_path": datastore_mount_path,
    "storage_id": storage_id,
    "boot_usb": {
        "serial": boot_serial,
        "allow_destroy": boot_allow_destroy,
        "min_gib": boot_min_gib,
        "max_gib": boot_max_gib,
        "resolved_device": device_view(boot_device),
    },
    "datastore_device": {
        "serial": datastore_serial,
        "allow_destroy": datastore_allow_destroy,
        "allow_reformat_existing_filesystem": datastore_allow_reformat,
        "min_gib": datastore_min_gib,
        "resolved_device": device_view(datastore_device),
    },
    "approved_by": approved_by,
    "approved_at": approved_at,
    "change_ticket": change_ticket,
    "findings": findings,
    "recommendation": recommendation,
}

json_report.write_text(json.dumps(report, indent=2), encoding="utf-8")

lines = [
    "# PBS Rebuild Contract Check",
    "",
    f"Recommendation: `{recommendation}`",
    "",
    "## Contract",
    "",
    f"- Contract file: `{contract_path}`",
    f"- Approved by: `{approved_by or 'missing'}`",
    f"- Approved at: `{approved_at or 'missing'}`",
    f"- Change ticket: `{change_ticket or 'missing'}`",
    f"- Expected datastore mount: `{datastore_mount_path}`",
    f"- Proxmox storage ID: `{storage_id}`",
    "",
    "## Boot USB",
    "",
    f"- Approved serial: `{boot_serial or 'missing'}`",
    f"- Destructive approval: `{str(boot_allow_destroy).lower()}`",
    f"- Allowed size range: `{boot_min_gib}` - `{boot_max_gib}` GiB",
]

boot_view = device_view(boot_device)
if boot_view:
    lines.extend(
        [
            f"- Visible path: `{boot_view['path']}`",
            f"- Visible size: `{boot_view['size_gib']} GiB`",
            f"- Transport: `{boot_view['transport'] or 'unknown'}`",
            f"- Filesystem: `{boot_view['fstype'] or 'none'}`",
            f"- Label: `{boot_view['label'] or 'none'}`",
        ]
    )
else:
    lines.append("- Visible device: `not found`")

lines.extend(["", "## Datastore Device", ""])
lines.extend(
    [
        f"- Approved serial: `{datastore_serial or 'missing'}`",
        f"- Destructive approval: `{str(datastore_allow_destroy).lower()}`",
        f"- Reformat existing filesystem approved: `{str(datastore_allow_reformat).lower()}`",
        f"- Minimum size: `{datastore_min_gib}` GiB",
    ]
)

datastore_view = device_view(datastore_device)
if datastore_view:
    lines.extend(
        [
            f"- Visible path: `{datastore_view['path']}`",
            f"- Visible size: `{datastore_view['size_gib']} GiB`",
            f"- Filesystem: `{datastore_view['fstype'] or 'none'}`",
            f"- Label: `{datastore_view['label'] or 'none'}`",
            f"- Mountpoint: `{datastore_view['mountpoint'] or 'none'}`",
            f"- Model: `{datastore_view['model'] or 'unknown'}`",
        ]
    )
else:
    lines.append("- Visible device: `not found`")

lines.extend(["", "## Findings", ""])
if findings:
    lines.extend([f"- {item}" for item in findings])
else:
    lines.append("- none")

md_report.write_text("\n".join(lines), encoding="utf-8")

print(f"pbs_rebuild_contract_json={json_report}")
print(f"pbs_rebuild_contract_report={md_report}")
print(f"pbs_rebuild_contract_recommendation={recommendation}")
PY
