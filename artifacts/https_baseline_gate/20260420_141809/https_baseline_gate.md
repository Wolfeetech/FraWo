# HTTPS Baseline Gate

Decision: `BLOCKED`

HTTPS baseline audit summary: `/mnt/c/Users/Admin/Documents/Private_Networking/artifacts/https_baseline_audit/20260420_141723/summary.tsv`

## Scope Note

This gate covers only the minimal public HTTPS baseline for frawo-tech.de and www.frawo-tech.de.
It is intentionally smaller than the full website-release gate.

## Critical HTTPS-Baseline Checks

- `public-dns-check`: `failed`
- `public-http-redirect-check`: `failed`
- `public-https-check`: `failed`

## Blocked Reasons

- critical https-baseline check not green: public-dns-check=failed
- critical https-baseline check not green: public-http-redirect-check=failed
- critical https-baseline check not green: public-https-check=failed