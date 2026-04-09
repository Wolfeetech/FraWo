#!/usr/bin/env python3
from __future__ import annotations

import http.client
import sys
from urllib.parse import urlparse


APEX = "frawo-tech.de"
WWW = "www.frawo-tech.de"
REDIRECT_CODES = {301, 302, 307, 308}


def head_http(host: str) -> tuple[int | None, str, str]:
    try:
        conn = http.client.HTTPConnection(host, 80, timeout=10)
        conn.request("HEAD", "/", headers={"User-Agent": "Homeserver2027 Website Gate"})
        resp = conn.getresponse()
        status = resp.status
        location = resp.getheader("Location", "")
        server = resp.getheader("Server", "")
        conn.close()
        return status, location, server
    except Exception as exc:
        return None, str(exc), ""


def main() -> int:
    apex_status, apex_location, apex_server = head_http(APEX)
    www_status, www_location, www_server = head_http(WWW)

    apex_redirects_to_www = False
    if apex_status in REDIRECT_CODES and apex_location:
        try:
            parsed = urlparse(apex_location)
            apex_redirects_to_www = parsed.hostname == WWW
        except Exception:
            apex_redirects_to_www = False

    www_http_reachable = isinstance(www_status, int) and 200 <= www_status < 400
    status = "passed" if apex_redirects_to_www and www_http_reachable else "failed"

    print(f"apex_http_status={apex_status if apex_status is not None else 'error'}")
    print(f"apex_http_location={apex_location or '-'}")
    print(f"apex_http_server={apex_server or '-'}")
    print(f"www_http_status={www_status if www_status is not None else 'error'}")
    print(f"www_http_location={www_location or '-'}")
    print(f"www_http_server={www_server or '-'}")
    print(f"apex_redirects_to_www={'yes' if apex_redirects_to_www else 'no'}")
    print(f"www_http_reachable={'yes' if www_http_reachable else 'no'}")
    print(f"public_http_redirect_check_status={status}")

    return 0 if status == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
