#!/usr/bin/env python3
from __future__ import annotations

import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT_DIR / "artifacts" / "public_edge_preview" / datetime.now().strftime("%Y%m%d_%H%M%S")
REPORT_MD = REPORT_DIR / "report.md"

ODDO_IP = "192.168.2.22"
ODDO_IPV6 = "2a00:1e:ef80:7c01:be24:11ff:feaa:bbcc"
PUBLIC_IPV4 = "92.211.33.54"


def run_probe(name: str, args: list[str]) -> dict[str, str]:
    header_path = REPORT_DIR / f"{name}.headers.txt"
    body_path = REPORT_DIR / f"{name}.body.txt"
    log_path = REPORT_DIR / f"{name}.log"

    completed = subprocess.run(
        args + ["-D", str(header_path), "-o", str(body_path)],
        cwd=ROOT_DIR,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )

    stdout = completed.stdout or ""
    stderr = completed.stderr or ""
    log_path.write_text(stdout + stderr, encoding="utf-8")
    headers = header_path.read_text(encoding="utf-8", errors="replace") if header_path.exists() else ""
    body = body_path.read_text(encoding="utf-8", errors="replace") if body_path.exists() else ""
    status_match = re.search(r"HTTP/\S+\s+(\d{3})", headers)
    status = status_match.group(1) if status_match else ""

    return {
        "name": name,
        "returncode": str(completed.returncode),
        "status": status,
        "headers": headers,
        "body": body,
        "log": str(log_path),
    }


def contains_all(text: str, patterns: list[str]) -> bool:
    return all(pattern in text for pattern in patterns)


def main() -> int:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    probes = {
        "internal_www_root": run_probe(
            "internal_www_root",
            [
                "curl.exe",
                "-sS",
                "--resolve",
                f"www.frawo-tech.de:80:{ODDO_IP}",
                "http://www.frawo-tech.de/",
            ],
        ),
        "internal_apex_redirect": run_probe(
            "internal_apex_redirect",
            [
                "curl.exe",
                "-sS",
                "--resolve",
                f"frawo-tech.de:80:{ODDO_IP}",
                "http://frawo-tech.de/",
            ],
        ),
        "internal_radio_player": run_probe(
            "internal_radio_player",
            [
                "curl.exe",
                "-sS",
                "--resolve",
                f"www.frawo-tech.de:80:{ODDO_IP}",
                "http://www.frawo-tech.de/radio/public/frawo-funk",
            ],
        ),
        "global_ipv6_www_root": run_probe(
            "global_ipv6_www_root",
            [
                "curl.exe",
                "-6",
                "-sS",
                "-H",
                "Host: www.frawo-tech.de",
                f"http://[{ODDO_IPV6}]/",
            ],
        ),
        "public_ipv4_hairpin": run_probe(
            "public_ipv4_hairpin",
            [
                "curl.exe",
                "-4",
                "-sS",
                "--connect-timeout",
                "10",
                "-H",
                "Host: www.frawo-tech.de",
                f"http://{PUBLIC_IPV4}/",
            ],
        ),
    }

    checks = [
        (
            "internal_www_root",
            probes["internal_www_root"]["status"] == "200"
            and contains_all(probes["internal_www_root"]["body"], ["Home | FraWo", "Radio hoeren"]),
            "Host www.frawo-tech.de on 192.168.2.22 should return 200 and the FraWo homepage with radio CTA.",
        ),
        (
            "internal_apex_redirect",
            probes["internal_apex_redirect"]["status"] == "308"
            and "Location: https://www.frawo-tech.de/" in probes["internal_apex_redirect"]["headers"],
            "Host frawo-tech.de on 192.168.2.22 should redirect to https://www.frawo-tech.de/.",
        ),
        (
            "internal_radio_player",
            probes["internal_radio_player"]["status"] == "200"
            and "FraWo - Funk - AzuraCast" in probes["internal_radio_player"]["body"],
            "Host www.frawo-tech.de on 192.168.2.22 /radio/public/frawo-funk should return the AzuraCast player.",
        ),
        (
            "global_ipv6_www_root",
            probes["global_ipv6_www_root"]["status"] == "200"
            and "Home | FraWo" in probes["global_ipv6_www_root"]["body"],
            "The global IPv6 of VM220 should already serve the FraWo homepage on HTTP with Host www.frawo-tech.de.",
        ),
    ]

    hairpin_ok = probes["public_ipv4_hairpin"]["status"] == "200"
    blocked_notes: list[str] = []
    if not hairpin_ok:
        blocked_notes.append(
            "public IPv4 hairpin to 92.211.33.54:80 still fails from StudioPC; likely no active router forward for 80/443 to VM220."
        )

    failed_checks = [name for name, ok, _ in checks if not ok]

    lines = [
        "# Public Edge Preview Check",
        "",
        f"Generated from `{Path(__file__).name}`.",
        "",
        f"- VM220 internal target: `{ODDO_IP}`",
        f"- VM220 global IPv6: `{ODDO_IPV6}`",
        f"- current public IPv4 observed from StudioPC: `{PUBLIC_IPV4}`",
        "",
        "## Result",
        "",
    ]

    if failed_checks:
        lines.append(f"- decision: `failed`")
        lines.append(f"- failed_checks: `{', '.join(failed_checks)}`")
    else:
        lines.append("- decision: `passed`")
        lines.append("- summary: `VM220 public-edge preview is healthy on internal Host-header preview and on direct global IPv6 HTTP.`")
    lines.append("")
    lines.append("## Probe Details")
    lines.append("")

    for name, ok, expectation in checks:
        probe = probes[name]
        lines.append(f"- `{name}`: `{'passed' if ok else 'failed'}`")
        lines.append(f"  expectation: {expectation}")
        lines.append(f"  observed_status: `{probe['status'] or 'none'}`")
        lines.append(f"  log: `{probe['log']}`")

    lines.append(f"- `public_ipv4_hairpin`: `{'passed' if hairpin_ok else 'failed'}`")
    lines.append("  expectation: direct HTTP to the current public IPv4 should only pass after router forwarding is active.")
    lines.append(f"  observed_status: `{probes['public_ipv4_hairpin']['status'] or 'none'}`")
    lines.append(f"  log: `{probes['public_ipv4_hairpin']['log']}`")
    lines.append("")
    lines.append("## Cutover Notes")
    lines.append("")

    if blocked_notes:
        for note in blocked_notes:
            lines.append(f"- {note}")
    else:
        lines.append("- no additional cutover note")

    REPORT_MD.write_text("\n".join(lines), encoding="utf-8")

    print(f"public_edge_preview_report_dir={REPORT_DIR}")
    print(f"public_edge_preview_report={REPORT_MD}")
    if blocked_notes:
        for note in blocked_notes:
            print(f"cutover_note={note}")
    return 0 if not failed_checks else 1


if __name__ == "__main__":
    raise SystemExit(main())
