#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "${ROOT_DIR}/scripts/inventory_remote.sh"

TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
REPORT_DIR="${ROOT_DIR}/artifacts/pbs_storage_audit/${TIMESTAMP}"
JSON_REPORT="${REPORT_DIR}/audit.json"
MD_REPORT="${REPORT_DIR}/report.md"

mkdir -p "${REPORT_DIR}"

read_pbs_hostvar() {
  local key="$1"
  python3 - <<'PY' "$ROOT_DIR/ansible/inventory/host_vars/pbs.yml" "$key"
import sys
import yaml

path = sys.argv[1]
key = sys.argv[2]
with open(path, 'r', encoding='utf-8') as handle:
    data = yaml.safe_load(handle)
print(data[key])
PY
}

PBS_PROXMOX_STORAGE_ID="$(read_pbs_hostvar pbs_proxmox_storage_id)"

block_json="$(
  run_proxmox_remote "lsblk -J -b -o NAME,PATH,TYPE,TRAN,SIZE,FSTYPE,LABEL,UUID,MOUNTPOINT,MODEL,SERIAL,PKNAME"
)"
df_root_line="$(run_proxmox_remote "df -B1 / | awk 'NR==2 {print \$2\" \"\$3\" \"\$4}'")"
df_local_line="$(run_proxmox_remote "df -B1 /var/lib/vz | awk 'NR==2 {print \$2\" \"\$3\" \"\$4}'")"
pvesm_status="$(run_proxmox_remote "pvesm status")"
vm240_config="$(run_proxmox_remote "qm config 240 2>/dev/null || true")"
block_json_file="$(mktemp)"
trap 'rm -f "${block_json_file}"' EXIT
printf '%s\n' "${block_json}" > "${block_json_file}"

python3 - <<'PY' "${JSON_REPORT}" "${MD_REPORT}" "${df_root_line}" "${df_local_line}" "${pvesm_status}" "${vm240_config}" "${block_json_file}" "${PBS_PROXMOX_STORAGE_ID}"
import json
import sys
from pathlib import Path

json_report = Path(sys.argv[1])
md_report = Path(sys.argv[2])
df_root_line = sys.argv[3]
df_local_line = sys.argv[4]
pvesm_status = sys.argv[5]
vm240_config = sys.argv[6]
block_json_file = Path(sys.argv[7])
pbs_target_storage_id = sys.argv[8]
block_data = json.loads(block_json_file.read_text(encoding="utf-8"))

def parse_df(line: str):
    total, used, free = [int(x) for x in line.split()]
    return {
        "total_bytes": total,
        "used_bytes": used,
        "free_bytes": free,
        "free_gib": round(free / (1024 ** 3), 2),
        "used_percent": round((used / total) * 100, 2) if total else 0.0,
    }

devices = block_data.get("blockdevices", [])
rootfs = parse_df(df_root_line)
localfs = parse_df(df_local_line)

raw_usb_candidates = []
data_bearing_usb_ssd_candidates = []
dedicated_backup_partitions = []

for dev in devices:
    if dev.get("type") != "disk":
        continue
    path = dev.get("path") or ""
    size = int(dev.get("size") or 0)
    tran = dev.get("tran") or ""
    label = dev.get("label") or ""
    fstype = dev.get("fstype") or ""
    mountpoint = dev.get("mountpoint") or ""
    model = (dev.get("model") or "").strip()
    serial = (dev.get("serial") or "").strip()

    if tran == "usb" and 50 * 1024**3 <= size <= 70 * 1024**3 and not fstype and not label and not mountpoint:
        raw_usb_candidates.append(
            {
                "path": path,
                "size_gib": round(size / (1024**3), 2),
                "model": model,
                "serial": serial,
            }
        )

    if tran == "usb" and size >= 500 * 1024**3:
        data_bearing_usb_ssd_candidates.append(
            {
                "path": path,
                "size_gib": round(size / (1024**3), 2),
                "label": label,
                "fstype": fstype,
                "mountpoint": mountpoint,
                "model": model,
                "serial": serial,
            }
        )

    if fstype in {"ext4", "xfs"} and size >= 200 * 1024**3 and path not in {"/dev/mapper/pve-root"}:
        dedicated_backup_partitions.append(
            {
                "path": path,
                "size_gib": round(size / (1024**3), 2),
                "label": label,
                "mountpoint": mountpoint,
                "model": model,
                "serial": serial,
            }
        )

def storage_status_line(storage_id: str):
    for line in pvesm_status.splitlines():
        if line.strip().startswith(storage_id):
            return line
    return ""

pbs_usb_line = storage_status_line("pbs-usb")
pbs_target_line = storage_status_line(pbs_target_storage_id)
pbs_usb_active = " active" in f" {pbs_usb_line} "
pbs_target_active = " active" in f" {pbs_target_line} "
vm240_uses_pbs_usb = "pbs-usb:" in vm240_config

findings = []
if rootfs["free_gib"] < 8:
    findings.append(f"Proxmox root has only {rootfs['free_gib']} GiB free.")
if not raw_usb_candidates:
    findings.append("No clean 64GB-class USB rebuild stick is currently visible.")
if data_bearing_usb_ssd_candidates:
    findings.append("The visible USB SSD carries an existing data-bearing filesystem and must not be reformatted blindly.")
if not dedicated_backup_partitions:
    findings.append("No dedicated ext4/xfs backup partition suitable for PBS storage is visible.")
if vm240_uses_pbs_usb and not pbs_usb_active:
    findings.append("VM 240 still points to disabled pbs-usb storage.")

recommendation = "blocked_wait_for_clean_hardware"
if raw_usb_candidates and dedicated_backup_partitions and rootfs["free_gib"] >= 8:
    recommendation = "storage_ready_for_controlled_pbs_rebuild"

report = {
    "rootfs": rootfs,
    "localfs": localfs,
    "raw_usb_candidates": raw_usb_candidates,
    "data_bearing_usb_ssd_candidates": data_bearing_usb_ssd_candidates,
    "dedicated_backup_partitions": dedicated_backup_partitions,
    "pbs_usb_active": pbs_usb_active,
    "pbs_target_storage_id": pbs_target_storage_id,
    "pbs_target_active": pbs_target_active,
    "vm240_uses_pbs_usb": vm240_uses_pbs_usb,
    "findings": findings,
    "recommendation": recommendation,
}

json_report.write_text(json.dumps(report, indent=2), encoding="utf-8")

lines = [
    "# PBS Storage Audit",
    "",
    f"Recommendation: `{recommendation}`",
    "",
    "## Core Facts",
    "",
    f"- Proxmox root free: `{rootfs['free_gib']} GiB`",
    f"- `/var/lib/vz` free: `{localfs['free_gib']} GiB`",
    f"- `pbs-usb` active: `{str(pbs_usb_active).lower()}`",
    f"- configured PBS target `{pbs_target_storage_id}` active: `{str(pbs_target_active).lower()}`",
    f"- `VM 240` points to `pbs-usb`: `{str(vm240_uses_pbs_usb).lower()}`",
    "",
    "## Findings",
    "",
]
if findings:
    lines.extend([f"- {item}" for item in findings])
else:
    lines.append("- none")

lines.extend(["", "## Raw 64GB USB Candidates", ""])
if raw_usb_candidates:
    lines.extend(
        [
            f"- `{item['path']}` `{item['size_gib']} GiB` model=`{item['model']}` serial=`{item['serial']}`"
            for item in raw_usb_candidates
        ]
    )
else:
    lines.append("- none")

lines.extend(["", "## Data-Bearing USB SSD Candidates", ""])
if data_bearing_usb_ssd_candidates:
    lines.extend(
        [
            f"- `{item['path']}` `{item['size_gib']} GiB` fstype=`{item['fstype'] or 'unknown'}` label=`{item['label'] or 'none'}` model=`{item['model']}` serial=`{item['serial']}`"
            for item in data_bearing_usb_ssd_candidates
        ]
    )
else:
    lines.append("- none")

lines.extend(["", "## Dedicated Backup Partitions", ""])
if dedicated_backup_partitions:
    lines.extend(
        [
            f"- `{item['path']}` `{item['size_gib']} GiB` label=`{item['label'] or 'none'}` mount=`{item['mountpoint'] or 'none'}`"
            for item in dedicated_backup_partitions
        ]
    )
else:
    lines.append("- none")

md_report.write_text("\n".join(lines), encoding="utf-8")

print(f"pbs_storage_audit_json={json_report}")
print(f"pbs_storage_audit_report={md_report}")
print(f"pbs_storage_recommendation={recommendation}")
PY
