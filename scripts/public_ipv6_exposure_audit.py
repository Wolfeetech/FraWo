from __future__ import annotations

import datetime as dt
import pathlib
import shlex
import socket
import subprocess
from typing import Iterable


REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
ARTIFACT_ROOT = REPO_ROOT / "artifacts" / "public_ipv6_exposure_audit"

TARGETS = [
    {
        "name": "nextcloud",
        "discover_cmd": 'ssh hs27-nextcloud "ip -6 addr show scope global | awk \'/inet6 2a/{print $2}\' | cut -d/ -f1 | head -n1"',
        "ports": [22, 80],
    },
    {
        "name": "odoo",
        "discover_cmd": 'ssh hs27-odoo "ip -6 addr show scope global | awk \'/inet6 2a/{print $2}\' | cut -d/ -f1 | head -n1"',
        "ports": [22, 8069],
    },
    {
        "name": "paperless",
        "discover_cmd": 'ssh hs27-paperless "ip -6 addr show scope global | awk \'/inet6 2a/{print $2}\' | cut -d/ -f1 | head -n1"',
        "ports": [22, 8000],
    },
    {
        "name": "vaultwarden",
        "suffix": "be24:11ff:fe0f:4d8c",
        "ports": [22, 8080],
    },
    {
        "name": "storage-node",
        "suffix": "be24:11ff:fe68:2bc1",
        "ports": [22, 139, 445],
    },
    {
        "name": "homeassistant",
        "suffix": "be24:11ff:fed5:ba30",
        "ports": [22, 8123],
    },
]


def run_shell(command: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        shell=True,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )


def discover_ipv6(command: str) -> tuple[str | None, str | None]:
    result = run_shell(command)
    if result.returncode != 0:
        return None, f"discover_failed rc={result.returncode} stderr={result.stderr.strip()}"
    lines = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    if not lines:
        return None, "no_global_ipv6_reported"
    return lines[0], None


def discover_public_prefix() -> tuple[str | None, str | None]:
    last_error = "no_prefix_probe_targets"
    for target in TARGETS:
        command = target.get("discover_cmd")
        if not command:
            continue
        ipv6, error = discover_ipv6(command)
        if ipv6:
            hextets = ipv6.split(":")
            if len(hextets) >= 4:
                return ":".join(hextets[:4]), None
        last_error = error or "unable_to_extract_prefix"
    return None, last_error


def check_port(host: str, port: int, timeout: float = 3.0) -> tuple[bool, str]:
    try:
        with socket.socket(socket.AF_INET6, socket.SOCK_STREAM) as sock:
            sock.settimeout(timeout)
            sock.connect((host, port, 0, 0))
        return True, "open"
    except OSError as exc:
        return False, exc.__class__.__name__


def render_tsv(rows: Iterable[dict[str, str]]) -> str:
    header = ["target", "ipv6", "port", "status", "detail"]
    lines = ["\t".join(header)]
    for row in rows:
        lines.append("\t".join(row[key] for key in header))
    return "\n".join(lines) + "\n"


def render_md(timestamp: str, rows: list[dict[str, str]]) -> str:
    blocked = [row for row in rows if row["status"] == "open"]
    lines = [
        "# Public IPv6 Exposure Audit",
        "",
        f"- timestamp: `{timestamp}`",
        f"- total_checks: `{len(rows)}`",
        f"- open_checks: `{len(blocked)}`",
        "",
        "| Target | IPv6 | Port | Status | Detail |",
        "| --- | --- | ---: | --- | --- |",
    ]
    for row in rows:
        lines.append(
            f"| {row['target']} | {row['ipv6']} | {row['port']} | {row['status']} | {row['detail']} |"
        )
    if blocked:
        lines.extend(["", "## Open Findings", ""])
        for row in blocked:
            lines.append(
                f"- `{row['target']}` exposes `{row['ipv6']}:{row['port']}` (`{row['detail']}`)"
            )
    else:
        lines.extend(["", "## Open Findings", "", "- none"])
    return "\n".join(lines) + "\n"


def main() -> int:
    timestamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = ARTIFACT_ROOT / timestamp
    out_dir.mkdir(parents=True, exist_ok=True)

    rows: list[dict[str, str]] = []
    prefix, prefix_error = discover_public_prefix()
    for target in TARGETS:
        if "discover_cmd" in target:
            ipv6, discover_error = discover_ipv6(target["discover_cmd"])
        else:
            ipv6 = f"{prefix}:{target['suffix']}" if prefix else None
            discover_error = None if ipv6 else (prefix_error or "prefix_discovery_failed")
        if not ipv6:
            rows.append(
                {
                    "target": target["name"],
                    "ipv6": "-",
                    "port": "-",
                    "status": "unknown",
                    "detail": discover_error or "unknown",
                }
            )
            continue
        for port in target["ports"]:
            is_open, detail = check_port(ipv6, port)
            rows.append(
                {
                    "target": target["name"],
                    "ipv6": ipv6,
                    "port": str(port),
                    "status": "open" if is_open else "closed",
                    "detail": detail,
                }
            )

    summary_tsv = out_dir / "summary.tsv"
    report_md = out_dir / "report.md"
    summary_tsv.write_text(render_tsv(rows), encoding="utf-8")
    report_md.write_text(render_md(timestamp, rows), encoding="utf-8")

    latest_dir = ARTIFACT_ROOT
    (latest_dir / "latest.txt").write_text(timestamp + "\n", encoding="utf-8")
    (latest_dir / "latest_summary.tsv").write_text(summary_tsv.read_text(encoding="utf-8"), encoding="utf-8")
    (latest_dir / "latest_report.md").write_text(report_md.read_text(encoding="utf-8"), encoding="utf-8")

    open_count = sum(1 for row in rows if row["status"] == "open")
    print(f"public_ipv6_exposure_audit_dir={out_dir}")
    print(f"public_ipv6_total_checks={len(rows)}")
    print(f"public_ipv6_open_checks={open_count}")
    print(f"public_ipv6_latest_report={report_md}")
    return 1 if open_count else 0


if __name__ == "__main__":
    raise SystemExit(main())
