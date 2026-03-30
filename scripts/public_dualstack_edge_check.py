#!/usr/bin/env python3
from __future__ import annotations

import re
import subprocess
import sys


APEX = "frawo-tech.de"
WWW = "www.frawo-tech.de"


def probe_http(host: str, family: str) -> tuple[str | None, str]:
    flag = "-4" if family == "ipv4" else "-6"
    completed = subprocess.run(
        ["curl.exe", flag, "-I", "--max-time", "12", f"http://{host}"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    output = (completed.stdout or "") + (completed.stderr or "")
    match = re.search(r"HTTP/\S+\s+(\d{3})", output)
    return (match.group(1) if match else None, output.strip())


def main() -> int:
    apex_v4_status, apex_v4_detail = probe_http(APEX, "ipv4")
    www_v4_status, www_v4_detail = probe_http(WWW, "ipv4")
    apex_v6_status, apex_v6_detail = probe_http(APEX, "ipv6")
    www_v6_status, www_v6_detail = probe_http(WWW, "ipv6")

    apex_v4_ok = apex_v4_status == "308"
    www_v4_ok = www_v4_status == "200"
    apex_v6_ok = apex_v6_status == "308"
    www_v6_ok = www_v6_status == "200"

    ipv4_ok = apex_v4_ok and www_v4_ok
    ipv6_ok = apex_v6_ok and www_v6_ok
    passed = ipv4_ok and ipv6_ok

    print(f"apex_ipv4_http_status={apex_v4_status or 'error'}")
    print(f"www_ipv4_http_status={www_v4_status or 'error'}")
    print(f"apex_ipv6_http_status={apex_v6_status or 'error'}")
    print(f"www_ipv6_http_status={www_v6_status or 'error'}")
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
