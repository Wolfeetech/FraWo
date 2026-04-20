#!/usr/bin/env python3
from __future__ import annotations

import re
import shutil
import subprocess
import sys
from urllib.parse import urlparse


APEX = "frawo-tech.de"
WWW = "www.frawo-tech.de"
REDIRECT_CODES = {301, 302, 307, 308}


def resolve_curl_binary() -> str:
    for candidate in ("curl.exe", "curl"):
        if shutil.which(candidate):
            return candidate
    raise FileNotFoundError("curl_binary_not_found")


CURL_BIN = resolve_curl_binary()


def probe_http(host: str, family: str) -> tuple[str | None, str, str]:
    flag = "-4" if family == "ipv4" else "-6"
    completed = subprocess.run(
        [CURL_BIN, flag, "-sS", "-I", "--max-time", "12", f"http://{host}"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    output = (completed.stdout or "") + (completed.stderr or "")
    match = re.search(r"HTTP/\S+\s+(\d{3})", output)
    status = match.group(1) if match else None
    location_match = re.search(r"(?im)^location:\s*(.+?)\s*$", output)
    location = location_match.group(1) if location_match else ""
    return status, location, output.strip()


def is_redirect_to_https_www(status: str | None, location: str) -> bool:
    if status is None:
        return False
    try:
        status_code = int(status)
    except ValueError:
        return False
    if status_code not in REDIRECT_CODES:
        return False
    if not location:
        return False
    parsed = urlparse(location)
    return parsed.scheme == "https" and parsed.hostname == WWW


def main() -> int:
    apex_v4_status, apex_v4_location, apex_v4_detail = probe_http(APEX, "ipv4")
    www_v4_status, www_v4_location, www_v4_detail = probe_http(WWW, "ipv4")
    apex_v6_status, apex_v6_location, apex_v6_detail = probe_http(APEX, "ipv6")
    www_v6_status, www_v6_location, www_v6_detail = probe_http(WWW, "ipv6")

    apex_v4_ok = is_redirect_to_https_www(apex_v4_status, apex_v4_location)
    apex_v6_ok = is_redirect_to_https_www(apex_v6_status, apex_v6_location)

    def www_ok(status: str | None) -> bool:
        if status is None:
            return False
        try:
            status_code = int(status)
        except ValueError:
            return False
        return 200 <= status_code < 400

    www_v4_ok = www_ok(www_v4_status)
    www_v6_ok = www_ok(www_v6_status)

    ipv4_ok = apex_v4_ok and www_v4_ok
    ipv6_ok = apex_v6_ok and www_v6_ok
    passed = ipv4_ok and ipv6_ok

    print(f"apex_ipv4_http_status={apex_v4_status or 'error'}")
    print(f"www_ipv4_http_status={www_v4_status or 'error'}")
    print(f"apex_ipv6_http_status={apex_v6_status or 'error'}")
    print(f"www_ipv6_http_status={www_v6_status or 'error'}")
    print(f"apex_ipv4_location={apex_v4_location or '-'}")
    print(f"www_ipv4_location={www_v4_location or '-'}")
    print(f"apex_ipv6_location={apex_v6_location or '-'}")
    print(f"www_ipv6_location={www_v6_location or '-'}")
    print(f"apex_ipv4_redirects_to_https_www={'yes' if apex_v4_ok else 'no'}")
    print(f"apex_ipv6_redirects_to_https_www={'yes' if apex_v6_ok else 'no'}")
    print(f"ipv4_edge_ready={'yes' if ipv4_ok else 'no'}")
    print(f"ipv6_edge_ready={'yes' if ipv6_ok else 'no'}")
    print(f"apex_ipv4_detail={apex_v4_detail or '-'}")
    print(f"www_ipv4_detail={www_v4_detail or '-'}")
    print(f"apex_ipv6_detail={apex_v6_detail or '-'}")
    print(f"www_ipv6_detail={www_v6_detail or '-'}")
    print(f"public_dualstack_edge_check_status={'passed' if passed else 'failed'}")

    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
