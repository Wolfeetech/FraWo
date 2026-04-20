# HTTPS Baseline Audit Report

Generated from `/mnt/c/Users/Admin/Documents/Private_Networking/artifacts/https_baseline_audit/20260420_141723/summary.tsv`.

This audit covers only the minimal public HTTPS baseline for frawo-tech.de and www.frawo-tech.de.
It is intentionally smaller than the full website-release gate.

## Codex

- `public-dns-check`: `failed` - /usr/bin/python3 ./scripts/public_dns_check.py (`/mnt/c/Users/Admin/Documents/Private_Networking/artifacts/https_baseline_audit/20260420_141723/public-dns-check.log`)
- `public-http-redirect-check`: `failed` - /usr/bin/python3 ./scripts/public_http_redirect_check.py (`/mnt/c/Users/Admin/Documents/Private_Networking/artifacts/https_baseline_audit/20260420_141723/public-http-redirect-check.log`)
- `public-https-check`: `failed` - /usr/bin/python3 ./scripts/public_https_check.py (`/mnt/c/Users/Admin/Documents/Private_Networking/artifacts/https_baseline_audit/20260420_141723/public-https-check.log`)

## Operator

- `public_browser_acceptance_https`: `pending_manual` - Open http://frawo-tech.de, https://frawo-tech.de, http://www.frawo-tech.de and https://www.frawo-tech.de and confirm the public behavior matches the HTTPS-baseline goal.
- `public_scope_guardrail`: `pending_manual` - Confirm no admin UI is exposed publicly while the HTTPS baseline is being activated.
