#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "${ROOT_DIR}/scripts/inventory_remote.sh"

TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
REPORT_DIR="${ROOT_DIR}/artifacts/pbs_device_inventory/${TIMESTAMP}"
JSON_REPORT="${REPORT_DIR}/devices.json"
MD_REPORT="${REPORT_DIR}/report.md"

mkdir -p "${REPORT_DIR}"

block_json="$(
  run_proxmox_remote "lsblk -J -b -o NAME,PATH,TYPE,TRAN,RM,HOTPLUG,SIZE,FSTYPE,LABEL,UUID,MOUNTPOINT,MODEL,SERIAL,PKNAME"
)"
udev_text="$(
  run_proxmox_remote "for dev in /dev/sd?; do echo '=== '\"\$dev\"' ==='; udevadm info --query=property --name \"\$dev\" 2>/dev/null | sed -n '1,40p'; echo; done"
)"

block_json_file="$(mktemp)"
udev_text_file="$(mktemp)"
trap 'rm -f "${block_json_file}" "${udev_text_file}"' EXIT
printf '%s\n' "${block_json}" > "${block_json_file}"
printf '%s\n' "${udev_text}" > "${udev_text_file}"

python3 - <<'PY' "${block_json_file}" "${udev_text_file}" "${JSON_REPORT}" "${MD_REPORT}"
import json
import re
import sys
from pathlib import Path

block_json_path = Path(sys.argv[1])
udev_text_path = Path(sys.argv[2])
json_report = Path(sys.argv[3])
md_report = Path(sys.argv[4])

blockdevices = json.loads(block_json_path.read_text(encoding="utf-8")).get("blockdevices", [])
udev_text = udev_text_path.read_text(encoding="utf-8", errors="replace")

visible = []

for dev in blockdevices:
    if dev.get("type") != "disk":
        continue
    path = str(dev.get("path") or "")
    name = str(dev.get("name") or "")
    size_bytes = int(dev.get("size") or 0)
    visible.append(
        {
            "path": path,
            "name": name,
            "transport": str(dev.get("tran") or "").strip(),
            "removable": str(dev.get("rm") or "").strip(),
            "hotplug": str(dev.get("hotplug") or "").strip(),
            "size_bytes": size_bytes,
            "size_gib": round(size_bytes / (1024 ** 3), 2) if size_bytes else 0.0,
            "fstype": str(dev.get("fstype") or "").strip(),
            "label": str(dev.get("label") or "").strip(),
            "mountpoint": str(dev.get("mountpoint") or "").strip(),
            "model": str(dev.get("model") or "").strip(),
            "serial": str(dev.get("serial") or "").strip(),
        }
    )

for item in visible:
    pattern = rf"=== {re.escape(item['path'])} ===(.*?)(?:\n=== |\Z)"
    match = re.search(pattern, udev_text, flags=re.S)
    props = {}
    if match:
      for line in match.group(1).splitlines():
          if "=" in line:
              key, value = line.split("=", 1)
              props[key.strip()] = value.strip()
    item["udev"] = {
        "id_model": props.get("ID_MODEL", ""),
        "id_serial": props.get("ID_SERIAL", ""),
        "id_serial_short": props.get("ID_SERIAL_SHORT", ""),
        "id_bus": props.get("ID_BUS", ""),
        "id_usb_driver": props.get("ID_USB_DRIVER", ""),
    }
    issues = []
    if item["transport"] == "usb" and item["size_bytes"] == 0:
        issues.append("no_medium_or_zero_capacity")
    if item["transport"] == "usb" and item["fstype"]:
        issues.append("has_existing_filesystem")
    if item["transport"] == "usb" and item["mountpoint"]:
        issues.append("mounted")
    if item["transport"] == "usb" and item["size_gib"] >= 500:
        issues.append("large_usb_device_handle_with_care")
    item["issues"] = issues

report = {"devices": visible}
json_report.write_text(json.dumps(report, indent=2), encoding="utf-8")

lines = [
    "# PBS Device Inventory",
    "",
    "Non-destructive snapshot of visible block devices on Proxmox.",
    "",
]

for item in visible:
    lines.append(f"## {item['path'] or item['name']}")
    lines.append("")
    lines.append(f"- Transport: `{item['transport'] or 'unknown'}`")
    lines.append(f"- Size: `{item['size_gib']} GiB`")
    lines.append(f"- Model: `{item['model'] or 'unknown'}`")
    lines.append(f"- Serial: `{item['serial'] or 'unknown'}`")
    lines.append(f"- Filesystem: `{item['fstype'] or 'none'}`")
    lines.append(f"- Label: `{item['label'] or 'none'}`")
    lines.append(f"- Mountpoint: `{item['mountpoint'] or 'none'}`")
    lines.append(f"- Udev serial: `{item['udev']['id_serial_short'] or item['udev']['id_serial'] or 'unknown'}`")
    if item["issues"]:
        lines.append(f"- Issues: `{', '.join(item['issues'])}`")
    else:
        lines.append("- Issues: `none`")
    lines.append("")

md_report.write_text("\n".join(lines), encoding="utf-8")

print(f"pbs_device_inventory_json={json_report}")
print(f"pbs_device_inventory_report={md_report}")
PY
