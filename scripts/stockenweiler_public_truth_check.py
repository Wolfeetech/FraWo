#!/usr/bin/env python3
"""Check visible public DNS and HTTPS truth for Stockenweiler legacy hosts."""

from __future__ import annotations

import argparse
import json
import socket
import ssl
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
INVENTORY_PATH = ROOT_DIR / "manifests" / "stockenweiler" / "site_inventory.json"
OUTPUT_ROOT = ROOT_DIR / "artifacts" / "stockenweiler_inventory"


def probe_dns(host: str) -> dict[str, object]:
    result: dict[str, object] = {"host": host, "resolved": False, "canonical_name": "", "addresses": [], "error": ""}
    try:
        canonical, aliases, addresses = socket.gethostbyname_ex(host)
        result["resolved"] = True
        result["canonical_name"] = canonical
        result["addresses"] = addresses
        return result
    except OSError as exc:
        result["error"] = str(exc)
        return result


def probe_https(url: str) -> dict[str, object]:
    request = urllib.request.Request(url, headers={"User-Agent": "HS27-Stockenweiler-PublicTruth/1.0"})
    try:
        with urllib.request.urlopen(
            request,
            timeout=10,
            context=ssl._create_unverified_context(),
        ) as response:
            body = response.read(5000).decode("utf-8", "replace")
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
                "error_type": "",
                "error": "",
            }
    except urllib.error.HTTPError as exc:
        return {
            "reachable": True,
            "status": exc.code,
            "final_url": exc.geturl(),
            "title": "",
            "error_type": "http_error",
            "error": str(exc),
        }
    except Exception as exc:  # pragma: no cover - network dependent
        error_text = str(exc)
        error_type = "other"
        lowered = error_text.lower()
        if "timed out" in lowered:
            error_type = "timeout"
        elif "ssl" in lowered or "tls" in lowered or "handshake" in lowered:
            error_type = "tls_error"
        elif "getaddrinfo failed" in lowered or "name or service not known" in lowered:
            error_type = "dns_fail"
        return {
            "reachable": False,
            "status": "",
            "final_url": "",
            "title": "",
            "error_type": error_type,
            "error": error_text,
        }


def markdown_report(generated_at: str, results: list[dict[str, object]]) -> str:
    lines = [
        "# Stockenweiler Public Truth Check",
        "",
        f"- generated_at: `{generated_at}`",
        "",
    ]
    for item in results:
        lines.append(f"## `{item['service']}`")
        lines.append("")
        lines.append(f"- host: `{item['host']}`")
        lines.append(f"- public_url: `{item['public_url']}`")
        dns = item["dns"]
        lines.append(f"- dns_resolved: `{dns['resolved']}`")
        if dns.get("canonical_name"):
            lines.append(f"- canonical_name: `{dns['canonical_name']}`")
        addresses = dns.get("addresses", [])
        if addresses:
            lines.append(f"- addresses: {', '.join(f'`{addr}`' for addr in addresses)}")
        if dns.get("error"):
            lines.append(f"- dns_error: `{dns['error']}`")
        https = item["https"]
        lines.append(f"- https_reachable: `{https['reachable']}`")
        if https.get("status") != "":
            lines.append(f"- https_status: `{https['status']}`")
        if https.get("final_url"):
            lines.append(f"- final_url: `{https['final_url']}`")
        if https.get("title"):
            lines.append(f"- title: `{https['title']}`")
        if https.get("error_type"):
            lines.append(f"- error_type: `{https['error_type']}`")
        if https.get("error"):
            lines.append(f"- error: `{https['error']}`")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Check visible public DNS and HTTPS truth for Stockenweiler.")
    parser.add_argument("--inventory", default=str(INVENTORY_PATH), help="Stockenweiler inventory path")
    parser.add_argument(
        "--output",
        default=str(OUTPUT_ROOT / "latest_public_truth_check.md"),
        help="Markdown output path",
    )
    args = parser.parse_args()

    inventory_path = Path(args.inventory)
    data = json.loads(inventory_path.read_text(encoding="utf-8"))
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    json_path = output_path.with_suffix(".json")

    services = []
    for item in data.get("legacy_service_map", []):
        public_url = str(item.get("legacy_public_url", "")).strip()
        if not public_url.startswith("https://"):
            continue
        parsed = urllib.parse.urlparse(public_url)
        host = parsed.hostname or ""
        services.append(
            {
                "service": item.get("service", "-"),
                "host": host,
                "public_url": public_url,
                "dns": probe_dns(host),
                "https": probe_https(public_url),
            }
        )

    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    payload = {"generated_at": generated_at, "results": services}
    json_text = json.dumps(payload, indent=2, ensure_ascii=True)
    json_path.write_text(json_text + "\n", encoding="utf-8")
    output_path.write_text(markdown_report(generated_at, services), encoding="utf-8")

    dyn_dns_like = 0
    for item in services:
        canonical = str(item["dns"].get("canonical_name", ""))
        if canonical and canonical != item["host"]:
            dyn_dns_like += 1

    print(f"stockenweiler_public_truth_check_report={output_path.as_posix()}")
    print(f"stockenweiler_public_truth_check_json={json_path.as_posix()}")
    print(f"stockenweiler_public_truth_check_service_count={len(services)}")
    print(f"stockenweiler_public_truth_check_dyn_dns_like_count={dyn_dns_like}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
