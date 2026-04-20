# Website Release Audit Report

Generated from `C:\WORKSPACE\PROJEKTE\Active\FraWo\artifacts\website_release_audit\20260330_161613\summary.tsv`.

This audit covers the website release track only.
It is separate from the business MVP gate and from full internal certification.

## Codex

- `document-ownership-check`: `passed` - C:\Python313\python.exe ./scripts/document_ownership_check.py (`C:\WORKSPACE\PROJEKTE\Active\FraWo\artifacts\website_release_audit\20260330_161613\document-ownership-check.log`)
- `public-dns-check`: `passed` - C:\Python313\python.exe ./scripts/public_dns_check.py (`C:\WORKSPACE\PROJEKTE\Active\FraWo\artifacts\website_release_audit\20260330_161613\public-dns-check.log`)
- `public-http-redirect-check`: `failed` - C:\Python313\python.exe ./scripts/public_http_redirect_check.py (`C:\WORKSPACE\PROJEKTE\Active\FraWo\artifacts\website_release_audit\20260330_161613\public-http-redirect-check.log`)
- `public-dualstack-edge-check`: `failed` - C:\Python313\python.exe ./scripts/public_dualstack_edge_check.py (`C:\WORKSPACE\PROJEKTE\Active\FraWo\artifacts\website_release_audit\20260330_161613\public-dualstack-edge-check.log`)
- `public-https-check`: `failed` - C:\Python313\python.exe ./scripts/public_https_check.py (`C:\WORKSPACE\PROJEKTE\Active\FraWo\artifacts\website_release_audit\20260330_161613\public-https-check.log`)
- `public-mail-dns-check`: `failed` - C:\Python313\python.exe ./scripts/public_mail_dns_check.py (`C:\WORKSPACE\PROJEKTE\Active\FraWo\artifacts\website_release_audit\20260330_161613\public-mail-dns-check.log`)
- `public-edge-preview-check`: `failed` - C:\Python313\python.exe ./scripts/public_edge_preview_check.py (`C:\WORKSPACE\PROJEKTE\Active\FraWo\artifacts\website_release_audit\20260330_161613\public-edge-preview-check.log`)

## Gemini Browser AI

- `public_browser_acceptance_verified`: `pending_manual` - Visibly verify apex and www browser behavior for the website release scope.
- `public_radio_integration_verified`: `pending_manual` - Visibly verify the public website includes the intended radio presence or player path.

## Admin-only

- `website_target_system_verified`: `pending_manual` - Confirm the target system is the public Odoo website frontend on VM220 and not a public Odoo admin path.
- `public_mail_model_verified`: `pending_manual` - Confirm webmaster, franz, info and noreply are correct for the public release.
- `tls_automation_verified`: `pending_manual` - Confirm the chosen public TLS automation path is configured and documented.
- `spf_dkim_dmarc_verified`: `pending_manual` - Confirm SPF, DKIM and DMARC are all intentionally configured for release.
- `rollback_runbook_verified`: `pending_manual` - Confirm rollback for DNS, TLS and host-switch is complete and usable.

## Wolfi

- `website_content_verified`: `pending_manual` - Confirm the public Odoo-managed website content is the intended GbR release content.
