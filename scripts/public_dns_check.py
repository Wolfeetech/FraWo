#!/usr/bin/env python3
from __future__ import annotations

import sys
from typing import List

import dns.resolver


DOMAIN = "frawo-tech.de"
WWW_DOMAIN = "www.frawo-tech.de"


def lookup(name: str, rtype: str) -> List[str]:
    resolver = dns.resolver.Resolver()
    resolver.timeout = 4
    resolver.lifetime = 8
    try:
        return [answer.to_text().rstrip(".") for answer in resolver.resolve(name, rtype)]
    except Exception:
        return []


def main() -> int:
    apex_a = lookup(DOMAIN, "A")
    apex_aaaa = lookup(DOMAIN, "AAAA")
    www_cname = lookup(WWW_DOMAIN, "CNAME")
    www_a = lookup(WWW_DOMAIN, "A")
    www_aaaa = lookup(WWW_DOMAIN, "AAAA")

    apex_resolves = bool(apex_a or apex_aaaa)
    www_resolves = bool(www_cname or www_a or www_aaaa)
    www_points_to_apex = DOMAIN in www_cname if www_cname else False

    status = "passed" if apex_resolves and www_resolves else "failed"

    print(f"domain={DOMAIN}")
    print(f"www_domain={WWW_DOMAIN}")
    print(f"apex_a={','.join(apex_a) if apex_a else '-'}")
    print(f"apex_aaaa={','.join(apex_aaaa) if apex_aaaa else '-'}")
    print(f"www_cname={','.join(www_cname) if www_cname else '-'}")
    print(f"www_a={','.join(www_a) if www_a else '-'}")
    print(f"www_aaaa={','.join(www_aaaa) if www_aaaa else '-'}")
    print(f"apex_resolves={'yes' if apex_resolves else 'no'}")
    print(f"www_resolves={'yes' if www_resolves else 'no'}")
    print(f"www_points_to_apex={'yes' if www_points_to_apex else 'no'}")
    print(f"public_dns_check_status={status}")

    return 0 if status == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
