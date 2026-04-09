#!/usr/bin/env python3
from __future__ import annotations

import http.client
import ssl
import sys


HOSTS = ["frawo-tech.de", "www.frawo-tech.de"]


def head_https(host: str) -> tuple[int | None, str]:
    context = ssl.create_default_context()
    try:
        conn = http.client.HTTPSConnection(host, 443, timeout=12, context=context)
        conn.request("HEAD", "/", headers={"User-Agent": "Homeserver2027 Website Gate"})
        resp = conn.getresponse()
        status = resp.status
        conn.close()
        return status, ""
    except Exception as exc:
        return None, str(exc)


def main() -> int:
    results: dict[str, tuple[int | None, str]] = {host: head_https(host) for host in HOSTS}
    ok_hosts = []

    for host, (status, error) in results.items():
        if status is not None and 200 <= status < 400:
            ok_hosts.append(host)
        print(f"{host}_https_status={status if status is not None else 'error'}")
        print(f"{host}_https_error={error or '-'}")

    passed = len(ok_hosts) == len(HOSTS)
    print(f"public_https_check_status={'passed' if passed else 'failed'}")

    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
