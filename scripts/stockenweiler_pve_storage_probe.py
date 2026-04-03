#!/usr/bin/env python3
"""Collect a read-only Proxmox/storage truth snapshot for Stockenweiler."""

from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
OUTPUT_ROOT = ROOT_DIR / "artifacts" / "stockenweiler_inventory"


def run_ssh(target: str) -> dict[str, object]:
    remote_script = "\n".join(
        [
            "set -u",
            "echo '===HOST==='",
            "timeout 5 bash -lc '(hostnamectl --static 2>/dev/null || hostname) | head -n 1' || true",
            "echo '===PVEVERSION==='",
            "timeout 5 pveversion 2>/dev/null || true",
            "echo '===LSBLK==='",
            "timeout 5 cat /proc/partitions 2>/dev/null || true",
            "echo '===FINDMNT==='",
            "timeout 5 df -hT 2>/dev/null || true",
            "echo '===PVESM==='",
            "timeout 10 pvesm status 2>/dev/null || true",
            "",
        ]
    )
    command = [
        "ssh",
        "-o",
        "BatchMode=yes",
        "-o",
        "StrictHostKeyChecking=no",
        "-o",
        "ConnectTimeout=8",
        target,
        "bash -s",
    ]
    result = subprocess.run(
        command,
        input=remote_script.encode("utf-8"),
        capture_output=True,
        timeout=20,
    )
    return {
        "returncode": result.returncode,
        "stdout": result.stdout.decode("utf-8", errors="replace"),
        "stderr": result.stderr.decode("utf-8", errors="replace"),
        "command": command,
    }


def parse_sections(stdout: str) -> dict[str, str]:
    sections = {
        "host": "",
        "pveversion": "",
        "lsblk": "",
        "findmnt": "",
        "pvesm": "",
    }
    current: str | None = None
    mapping = {
        "===HOST===": "host",
        "===PVEVERSION===": "pveversion",
        "===LSBLK===": "lsblk",
        "===FINDMNT===": "findmnt",
        "===PVESM===": "pvesm",
    }
    for line in stdout.splitlines():
        stripped = line.strip()
        if stripped in mapping:
            current = mapping[stripped]
            continue
        if current:
            sections[current] += line + "\n"
    return {key: value.rstrip() for key, value in sections.items()}


def markdown_report(
    target: str,
    generated_at: str,
    probe_status: str,
    sections: dict[str, str],
    stderr: str,
) -> str:
    lines = [
        "# Stockenweiler PVE Storage Probe",
        "",
        f"- generated_at: `{generated_at}`",
        f"- target: `{target}`",
        f"- probe_status: `{probe_status}`",
        "",
        "## Summary",
        "",
    ]
    if probe_status == "reachable":
        lines.extend(
            [
                f"- host: `{sections.get('host', '-') or '-'}`",
                f"- pveversion: `{(sections.get('pveversion', '') or '-').splitlines()[0] if sections.get('pveversion') else '-'}`",
                "- read-only truth captured for host identity, block devices, mounted filesystems, and `pvesm status`",
            ]
        )
    else:
        lines.extend(
            [
                "- remote host was not reachable from the current workstation context",
                "- this is still useful because it preserves a timestamped failed-attempt record instead of leaving the gap undocumented",
            ]
        )

    if stderr.strip():
        lines.extend(["", "## SSH Error", "", "```text", stderr.rstrip(), "```"])

    for title, key in (
        ("Host", "host"),
        ("PVE Version", "pveversion"),
        ("Block Devices", "lsblk"),
        ("Filesystem Usage", "findmnt"),
        ("PVE Storage", "pvesm"),
    ):
        content = sections.get(key, "").strip()
        lines.extend(["", f"## {title}", ""])
        if content:
            fence = "json" if key == "lsblk" and content.startswith("{") else "text"
            lines.extend([f"```{fence}", content, "```"])
        else:
            lines.append("- no data")

    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Read-only PVE/storage probe for Stockenweiler.")
    parser.add_argument(
        "--target",
        default="pve",
        help="SSH target or alias for the Stockenweiler Proxmox host.",
    )
    parser.add_argument(
        "--output",
        default=str(OUTPUT_ROOT / "latest_pve_storage_probe.md"),
        help="Markdown report output path.",
    )
    args = parser.parse_args()

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    json_path = output_path.with_suffix(".json")

    ssh_result = run_ssh(args.target)
    sections = parse_sections(str(ssh_result["stdout"]))
    probe_status = "reachable" if ssh_result["returncode"] == 0 else "unreachable"

    payload = {
        "generated_at": timestamp,
        "target": args.target,
        "probe_status": probe_status,
        "returncode": ssh_result["returncode"],
        "stderr": ssh_result["stderr"],
        "sections": sections,
    }
    json_text = json.dumps(payload, indent=2, ensure_ascii=True)
    json_path.write_text(json_text + "\n", encoding="utf-8")
    output_path.write_text(
        markdown_report(args.target, timestamp, probe_status, sections, str(ssh_result["stderr"])),
        encoding="utf-8",
    )

    print(f"stockenweiler_pve_storage_probe_target={args.target}")
    print(f"stockenweiler_pve_storage_probe_status={probe_status}")
    print(f"stockenweiler_pve_storage_probe_report={output_path.as_posix()}")
    print(f"stockenweiler_pve_storage_probe_json={json_path.as_posix()}")
    return 0 if probe_status == "reachable" else 1


if __name__ == "__main__":
    raise SystemExit(main())
