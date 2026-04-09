# Website Release Audit Report

Generated from `C:\Users\StudioPC\Documents\Homeserver 2027 Workspace\artifacts\website_release_audit\20260330_111718\summary.tsv`.

This audit covers the website release track only.
It is separate from the business MVP gate and from full internal certification.

## Codex

- `document-ownership-check`: `passed` - C:\Python313\python.exe ./scripts/document_ownership_check.py (`C:\Users\StudioPC\Documents\Homeserver 2027 Workspace\artifacts\website_release_audit\20260330_111718\document-ownership-check.log`)
- `public-dns-check`: `passed` - C:\Python313\python.exe ./scripts/public_dns_check.py (`C:\Users\StudioPC\Documents\Homeserver 2027 Workspace\artifacts\website_release_audit\20260330_111718\public-dns-check.log`)
- `public-http-redirect-check`: `failed` - C:\Python313\python.exe ./scripts/public_http_redirect_check.py (`C:\Users\StudioPC\Documents\Homeserver 2027 Workspace\artifacts\website_release_audit\20260330_111718\public-http-redirect-check.log`)
- `public-https-check`: `failed` - C:\Python313\python.exe ./scripts/public_https_check.py (`C:\Users\StudioPC\Documents\Homeserver 2027 Workspace\artifacts\website_release_audit\20260330_111718\public-https-check.log`)
- `public-mail-dns-check`: `failed` - C:\Python313\python.exe ./scripts/public_mail_dns_check.py (`C:\Users\StudioPC\Documents\Homeserver 2027 Workspace\artifacts\website_release_audit\20260330_111718\public-mail-dns-check.log`)

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
