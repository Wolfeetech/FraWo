#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_DIR = ROOT / "artifacts" / "coolify_management_host"
REPORT_JSON = ARTIFACT_DIR / "latest_report.json"
REPORT_MD = ARTIFACT_DIR / "latest_report.md"
TARGET = "root@100.69.179.87"
NODE = "proxmox-anker"


def ssh(cmd: str, timeout: int = 30) -> str:
    result = subprocess.run(["ssh", TARGET, cmd], capture_output=True, text=True, timeout=timeout, check=False)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip() or f"ssh failed: {cmd}")
    return result.stdout.strip()


def main() -> None:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    hostname = ssh("hostname")
    pveversion = ssh("pveversion")
    status = json.loads(ssh(f"pvesh get /nodes/{NODE}/status --output-format json"))
    storage = json.loads(ssh(f"pvesh get /nodes/{NODE}/storage --output-format json"))
    resources = json.loads(ssh("pvesh get /cluster/resources --type vm --output-format json"))

    local_lvm = next((item for item in storage if item.get("storage") == "local-lvm"), {})
    local_dir = next((item for item in storage if item.get("storage") == "local"), {})
    toolbox = next((item for item in resources if item.get("vmid") == 100), {})

    mem_available = int(status.get("memory", {}).get("available", 0))
    local_lvm_avail = int(local_lvm.get("avail", 0))
    local_dir_avail = int(local_dir.get("avail", 0))

    recommended = {
        "kind": "lxc",
        "suggested_vmid": 130,
        "name": "coolify-mgmt",
        "vcpus": 2,
        "memory_mb": 2048,
        "rootfs_gb": 24,
        "storage": "local-lvm",
        "network": "internal_management_non_dmz",
    }

    fits = {
        "memory_ok": mem_available >= 3 * 1024 * 1024 * 1024,
        "local_lvm_ok": local_lvm_avail >= 30 * 1024 * 1024 * 1024,
        "local_dir_ok": local_dir_avail >= 20 * 1024 * 1024 * 1024,
    }
    toolbox_ok = bool(toolbox) and toolbox.get("status") == "running" and int(toolbox.get("mem", 0)) < 700 * 1024 * 1024

    payload = {
        "generated_at": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
        "target": TARGET,
        "hostname": hostname,
        "pveversion": pveversion,
        "memory_available_bytes": mem_available,
        "local_lvm_avail_bytes": local_lvm_avail,
        "local_dir_avail_bytes": local_dir_avail,
        "toolbox_running": bool(toolbox),
        "toolbox_temporary_fallback_ok": toolbox_ok,
        "recommended_management_node": recommended,
        "fit_checks": fits,
        "recommendation": "dedicated_internal_anker_management_node" if fits["memory_ok"] and fits["local_lvm_ok"] else "do_not_place_coolify_yet",
        "rejected_targets": [
            "proxmox_anker_host_itself",
            "stock_pve",
            "dmz_nodes",
            "surface_go_frontend_while_unstable",
        ],
        "next_gated_step": "create_dedicated_internal_management_ct_or_vm_on_anker",
    }
    REPORT_JSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    gib = 1024 ** 3
    lines = [
        "# Coolify Management Host Audit",
        "",
        f"- Generated at: `{payload['generated_at']}`",
        f"- Target: `{TARGET}`",
        f"- Host: `{hostname}`",
        f"- Version: `{pveversion}`",
        f"- Memory available: `{mem_available / gib:.2f} GiB`",
        f"- local-lvm free: `{local_lvm_avail / gib:.2f} GiB`",
        f"- local dir free: `{local_dir_avail / gib:.2f} GiB`",
        f"- Toolbox temporary fallback ok: `{str(toolbox_ok).lower()}`",
        f"- Recommendation: `{payload['recommendation']}`",
        "",
        "## Recommended Node",
        "",
        f"- kind: `{recommended['kind']}`",
        f"- suggested_vmid: `{recommended['suggested_vmid']}`",
        f"- name: `{recommended['name']}`",
        f"- vcpus: `{recommended['vcpus']}`",
        f"- memory_mb: `{recommended['memory_mb']}`",
        f"- rootfs_gb: `{recommended['rootfs_gb']}`",
        f"- storage: `{recommended['storage']}`",
        f"- network: `{recommended['network']}`",
        "",
        "## Fit Checks",
        "",
        f"- memory_ok: `{str(fits['memory_ok']).lower()}`",
        f"- local_lvm_ok: `{str(fits['local_lvm_ok']).lower()}`",
        f"- local_dir_ok: `{str(fits['local_dir_ok']).lower()}`",
        "",
        "## Rejected Targets",
        "",
    ]
    for item in payload["rejected_targets"]:
        lines.append(f"- `{item}`")
    lines.extend([
        "",
        "## Next Gated Step",
        "",
        f"- `{payload['next_gated_step']}`",
    ])
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(str(REPORT_MD))


if __name__ == "__main__":
    main()
