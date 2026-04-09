# Website Release Audit Report

Generated from `/mnt/c/Users/StudioPC/Documents/Homeserver 2027 Workspace/artifacts/website_release_audit/20260330_063108/summary.tsv`.

This audit covers the website release track only.
It is separate from the business MVP gate and from full internal certification.

## Codex

- `document-ownership-check`: `passed` - make document-ownership-check (`/mnt/c/Users/StudioPC/Documents/Homeserver 2027 Workspace/artifacts/website_release_audit/20260330_063108/document-ownership-check.log`)
- `public-dns-check`: `passed` - python3 ./scripts/public_dns_check.py (`/mnt/c/Users/StudioPC/Documents/Homeserver 2027 Workspace/artifacts/website_release_audit/20260330_063108/public-dns-check.log`)
- `public-http-redirect-check`: `failed` - python3 ./scripts/public_http_redirect_check.py (`/mnt/c/Users/StudioPC/Documents/Homeserver 2027 Workspace/artifacts/website_release_audit/20260330_063108/public-http-redirect-check.log`)
- `public-https-check`: `failed` - python3 ./scripts/public_https_check.py (`/mnt/c/Users/StudioPC/Documents/Homeserver 2027 Workspace/artifacts/website_release_audit/20260330_063108/public-https-check.log`)
- `public-mail-dns-check`: `failed` - python3 ./scripts/public_mail_dns_check.py (`/mnt/c/Users/StudioPC/Documents/Homeserver 2027 Workspace/artifacts/website_release_audit/20260330_063108/public-mail-dns-check.log`)

## Gemini Browser AI

- `public-browser-acceptance-verified`: `pending_manual` - Visibly verify apex and www browser behavior for the website release scope.

## Admin-only

- `website-target-system-verified`: `pending_manual` - Confirm the target system and hosting path for www.frawo-tech.de.
- `public-mail-model-verified`: `pending_manual` - Confirm webmaster, franz, info and noreply are correct for the public release.
- `tls-automation-verified`: `pending_manual` - Confirm the chosen public TLS automation path is configured and documented.
- `spf-dkim-dmarc-verified`: `pending_manual` - Confirm SPF, DKIM and DMARC are all intentionally configured for release.
- `rollback-runbook-verified`: `pending_manual` - Confirm rollback for DNS, TLS and host-switch is complete and usable.

## Wolfi

- `website-content-verified`: `pending_manual` - Confirm the public website content is the intended GbR release content.
