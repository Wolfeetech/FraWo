#!/usr/bin/env python3
"""Probe legacy Stockenweiler access paths from the current workstation."""

from __future__ import annotations

import argparse
import json
import socket
import ssl
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
DEFAULT_INVENTORY = ROOT_DIR / "manifests" / "stockenweiler" / "site_inventory.json"
OUTPUT_ROOT = ROOT_DIR / "artifacts" / "stockenweiler_inventory"


def probe_dns(host: str) -> dict[str, object]:
    try:
        infos = socket.getaddrinfo(host, None)
    except OSError as exc:
        return {"host": host, "resolved": False, "addresses": [], "dns_error": str(exc)}

    addresses: list[str] = []
    for info in infos:
        address = info[4][0]
        if address not in addresses:
            addresses.append(address)
    return {"host": host, "resolved": True, "addresses": addresses, "dns_error": ""}


def probe_http(url: str) -> dict[str, object]:
    request = urllib.request.Request(url, headers={"User-Agent": "HS27-Stockenweiler-Probe/1.0"})
    try:
        with urllib.request.urlopen(request, timeout=10, context=ssl._create_unverified_context()) as response:
            body = response.read(4000).decode("utf-8", "replace")
            title = ""
            lower = body.lower()
            if "<title>" in lower and "</title>" in lower:
                start = lower.index("<title>") + 7
                end = lower.index("</title>", start)
                title = body[start:end].strip()
            return {
                "reachable": True,
                "status": getattr(response, "status", 200),
                "final_url": response.geturl(),
                "title": title,
                "error": "",
            }
    except Exception as exc:  # pragma: no cover - network dependent
        return {
            "reachable": False,
            "status": "",
            "final_url": "",
            "title": "",
            "error": str(exc),
        }


def main() -> int:
    parser = argparse.ArgumentParser(description="Probe legacy Stockenweiler public access paths.")
    parser.add_argument("--inventory", default=str(DEFAULT_INVENTORY), help="Path to the Stockenweiler inventory JSON")
    parser.add_argument(
        "--report",
        default=str(OUTPUT_ROOT / "legacy_access_probe.md"),
        help="Markdown report path",
    )
    args = parser.parse_args()

    inventory_path = Path(args.inventory)
    if not inventory_path.exists():
        print(f"stockenweiler_legacy_probe_error=missing_inventory:{inventory_path}")
        return 1

    data = json.loads(inventory_path.read_text(encoding="utf-8"))
    services = data.get("legacy_service_map", [])

    results: list[dict[str, object]] = []
    for service in services:
        public_url = str(service.get("legacy_public_url", "")).strip()
        if not public_url:
            continue
        parsed = urllib.parse.urlparse(public_url if "://" in public_url else f"//{public_url}", scheme="")
        host = parsed.hostname or public_url.split(":")[0]
        dns = probe_dns(host)
        http = {"reachable": False, "status": "", "final_url": "", "title": "", "error": ""}
        if public_url.startswith("http://") or public_url.startswith("https://"):
            http = probe_http(public_url)
        results.append(
            {
                "service": service.get("service", "-"),
                "legacy_public_url": public_url,
                "local_url": service.get("local_url", ""),
                "source": service.get("source", ""),
                "dns": dns,
                "http": http,
            }
        )

    decision = "legacy_access_candidates_present" if results else "no_legacy_access_candidates"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_path = OUTPUT_ROOT / f"legacy_access_probe_{timestamp}.json"
    md_path = Path(args.report)
    latest_json = OUTPUT_ROOT / "latest_legacy_access_probe.json"
    latest_md = OUTPUT_ROOT / "latest_legacy_access_probe.md"
    md_path.parent.mkdir(parents=True, exist_ok=True)

    payload = {
        "decision": decision,
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "inventory": str(inventory_path),
        "results": results,
    }
    json_text = json.dumps(payload, indent=2, ensure_ascii=True)
    json_path.write_text(json_text + "\n", encoding="utf-8")
    latest_json.write_text(json_text + "\n", encoding="utf-8")

    lines = [
        "# Stockenweiler Legacy Access Probe",
        "",
        f"Decision: `{decision}`",
        "",
        f"Inventory: `{inventory_path.as_posix()}`",
        "",
    ]
    for item in results:
        dns = item["dns"]
        http = item["http"]
        lines.append(f"## `{item['service']}`")
        lines.append("")
        lines.append(f"- legacy_public_url: `{item['legacy_public_url']}`")
        lines.append(f"- local_url: `{item['local_url']}`")
        lines.append(f"- dns_resolved: `{dns['resolved']}`")
        if dns["addresses"]:
            for address in dns["addresses"]:
                lines.append(f"  - address: `{address}`")
        if dns["dns_error"]:
            lines.append(f"- dns_error: `{dns['dns_error']}`")
        if http["status"] != "" or http["error"]:
            lines.append(f"- http_reachable: `{http['reachable']}`")
            if http["status"] != "":
                lines.append(f"- http_status: `{http['status']}`")
            if http["final_url"]:
                lines.append(f"- final_url: `{http['final_url']}`")
            if http["title"]:
                lines.append(f"- title: `{http['title']}`")
            if http["error"]:
                lines.append(f"- http_error: `{http['error']}`")
        lines.append("")

    markdown = "\n".join(lines).rstrip() + "\n"
    md_path.write_text(markdown, encoding="utf-8")
    latest_md.write_text(markdown, encoding="utf-8")

    print(f"stockenweiler_legacy_probe_report={md_path.as_posix()}")
    print(f"stockenweiler_legacy_probe_result_count={len(results)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
