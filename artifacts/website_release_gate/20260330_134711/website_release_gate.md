# Website Release Gate

Decision: `BLOCKED`

Website audit summary: `artifacts\website_release_audit\20260330_134359\summary.tsv`
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

- `website_target_system_verified`: `passed` - The target system is explicitly decided as the public Odoo website frontend on VM220 and not a public Odoo admin path; last_verified=2026-03-30; evidence=VM220 serves the Odoo website on / with title Home | FraWo; direct Host-header preview on 192.168.2.22 returns apex redirect and www homepage; direct global IPv6 HTTP preview on 2a00:1e:ef80:7c01:be24:11ff:feaa:bbcc also returns the FraWo homepage.
- `website_content_verified`: `pending` - The public Odoo-managed website content is the intended GbR release content
- `public_browser_acceptance_verified`: `failed` - Apex and www browser behavior are visibly verified for the website release scope; last_verified=2026-03-30; evidence=Gemini browser check: apex and www HTTP show STRATO placeholder page without redirect; apex and www HTTPS show ERR_SSL_PROTOCOL_ERROR; no public GbR content visible.
- `public_radio_integration_verified`: `passed` - The public website visibly includes the intended radio presence or player path; last_verified=2026-03-30; evidence=VM220 public-edge preview and toolbox preview both serve www.frawo-tech.de/radio/public/frawo-funk to AzuraCast; Host www.frawo-tech.de on 192.168.2.22 and 192.168.2.20 returns FraWo - Funk - AzuraCast with HTTP 200.
- `public_mail_model_verified`: `pending` - Public release mail model for webmaster, franz, info and noreply is verified; evidence=webmaster@frawo-tech.de and franz@frawo-tech.de are technically verified for IMAP and SMTP AUTH; public release decision for info@frawo-tech.de and noreply@frawo-tech.de is still open.
- `tls_automation_verified`: `pending` - The chosen public TLS automation path is configured and documented; evidence=Caddy public edge is deployed on VM220 and listening on 80/443, but ACME issuance is still blocked because public A/AAAA for frawo-tech.de and www.frawo-tech.de still point to STRATO parking addresses instead of the Odoo edge.
- `spf_dkim_dmarc_verified`: `pending` - SPF, DKIM and DMARC are all intentionally configured for public release; evidence=MX and DMARC are visible in the live checks; SPF is currently not visible and DKIM is not yet documented as verified for release.
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