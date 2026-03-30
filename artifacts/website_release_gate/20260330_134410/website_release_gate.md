# Website Release Gate

Decision: `BLOCKED`

Website audit summary: `C:\Users\StudioPC\Documents\Homeserver 2027 Workspace\artifacts\website_release_audit\20260330_134359\summary.tsv`
Manual evidence: `C:\Users\StudioPC\Documents\Homeserver 2027 Workspace\manifests\website_release_gate\manual_checks.json`

## Scope Note

This gate covers the public website release track only.
It is not the same as the business MVP gate or the full internal production seal.

## Critical Website Codex Checks

- `document-ownership-check`: `passed`
- `public-dns-check`: `passed`
- `public-http-redirect-check`: `failed`
- `public-https-check`: `failed`
- `public-mail-dns-check`: `failed`

## Critical Website Manual Evidence

- `website_target_system_verified`: `passed` - The target system is explicitly decided as the public Odoo website frontend on VM220 and not a public Odoo admin path; last_verified=2026-03-30; evidence=VM220 serves the Odoo website on /; toolbox Caddy preview serves Host www.frawo-tech.de to 192.168.2.22:8069 and apex frawo-tech.de redirects to https://www.frawo-tech.de{uri}.
- `website_content_verified`: `pending` - The public Odoo-managed website content is the intended GbR release content
- `public_browser_acceptance_verified`: `failed` - Apex and www browser behavior are visibly verified for the website release scope; last_verified=2026-03-30; evidence=Gemini browser check: apex and www HTTP show STRATO placeholder page without redirect; apex and www HTTPS show ERR_SSL_PROTOCOL_ERROR; no public GbR content visible.
- `public_radio_integration_verified`: `passed` - The public website visibly includes the intended radio presence or player path; last_verified=2026-03-30; evidence=Toolbox Caddy preview serves www.frawo-tech.de/radio/public/frawo-funk to AzuraCast; Host www.frawo-tech.de on 192.168.2.20 returns FraWo - Funk - AzuraCast with HTTP 200.
- `public_mail_model_verified`: `pending` - Public release mail model for webmaster, franz, info and noreply is verified
- `tls_automation_verified`: `pending` - The chosen public TLS automation path is configured and documented
- `spf_dkim_dmarc_verified`: `pending` - SPF, DKIM and DMARC are all intentionally configured for public release
- `rollback_runbook_verified`: `pending` - Rollback for DNS, TLS and host-switch is complete and usable

## Blocked Reasons

- critical website Codex check not green: public-http-redirect-check=failed
- critical website Codex check not green: public-https-check=failed
- critical website Codex check not green: public-mail-dns-check=failed
- critical website manual evidence not green: website_content_verified=pending
- critical website manual evidence not green: public_browser_acceptance_verified=failed
- critical website manual evidence not green: public_mail_model_verified=pending
- critical website manual evidence not green: tls_automation_verified=pending
- critical website manual evidence not green: spf_dkim_dmarc_verified=pending
- critical website manual evidence not green: rollback_runbook_verified=pending