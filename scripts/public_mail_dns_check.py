#!/usr/bin/env python3
from __future__ import annotations

import sys
from typing import List

import dns.resolver


DOMAIN = "frawo-tech.de"
DMARC = "_dmarc.frawo-tech.de"


def lookup(name: str, rtype: str) -> List[str]:
    resolver = dns.resolver.Resolver()
    resolver.timeout = 4
    resolver.lifetime = 8
    try:
        return [answer.to_text().strip('"').rstrip(".") for answer in resolver.resolve(name, rtype)]
    except Exception:
        return []


def main() -> int:
    mx_records = lookup(DOMAIN, "MX")
    txt_records = lookup(DOMAIN, "TXT")
    dmarc_records = lookup(DMARC, "TXT")

    spf_present = any(record.lower().startswith("v=spf1") for record in txt_records)
    dmarc_present = any(record.lower().startswith("v=dmarc1") for record in dmarc_records)
    mx_present = bool(mx_records)

    status = "passed" if mx_present and spf_present and dmarc_present else "failed"

    print(f"mail_domain={DOMAIN}")
    print(f"mx_records={'; '.join(mx_records) if mx_records else '-'}")
    print(f"txt_records={'; '.join(txt_records) if txt_records else '-'}")
    print(f"dmarc_records={'; '.join(dmarc_records) if dmarc_records else '-'}")
    print(f"mx_present={'yes' if mx_present else 'no'}")
    print(f"spf_present={'yes' if spf_present else 'no'}")
    print(f"dmarc_present={'yes' if dmarc_present else 'no'}")
    print("dkim_selector_status=manual_verification_required")
    print(f"public_mail_dns_check_status={status}")

    return 0 if status == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
