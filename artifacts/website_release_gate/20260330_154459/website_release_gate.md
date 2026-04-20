# Website Release Gate

Decision: `BLOCKED`

Website audit summary: `C:\WORKSPACE\PROJEKTE\Active\FraWo\artifacts\website_release_audit\20260330_154447\summary.tsv`
Manual evidence: `C:\WORKSPACE\PROJEKTE\Active\FraWo\manifests\website_release_gate\manual_checks.json`

## Scope Note

This gate covers the public website release track only.
It is not the same as the business MVP gate or the full internal production seal.

## Critical Website Codex Checks

- `document-ownership-check`: `passed`
- `public-dns-check`: `passed`
- `public-http-redirect-check`: `passed`
- `public-https-check`: `failed`
- `public-mail-dns-check`: `failed`

## Critical Website Manual Evidence

- `website_target_system_verified`: `passed` - The target system is explicitly decided as the public Odoo website frontend on VM220 and not a public Odoo admin path; last_verified=2026-03-30; evidence=VM220 serves the Odoo website on / with title Home | FraWo; direct Host-header preview on 192.168.2.22 returns apex redirect and www homepage; direct global IPv6 HTTP preview on 2a00:1e:ef80:7c01:be24:11ff:feaa:bbcc also returns the FraWo homepage.
- `website_content_verified`: `passed` - The public Odoo-managed website content is the intended GbR release content; last_verified=2026-03-30; evidence=Gemini browser check after STRATO DNS cutover: http://www.frawo-tech.de shows the real FraWo Odoo website with FraWo branding, address, contact CTA, and no public Odoo admin path.
- `public_browser_acceptance_verified`: `failed` - Apex and www browser behavior are visibly verified for the website release scope; last_verified=2026-03-30; evidence=Gemini browser check after DNS cutover: apex HTTP now redirects to https://www.frawo-tech.de and www HTTP shows the real FraWo website, but apex/www HTTPS still fail with ERR_SSL_PROTOCOL_ERROR. Local curl verification shows public HTTP currently works over IPv6 while IPv4 port 80 still times out/refuses.
- `public_radio_integration_verified`: `passed` - The public website visibly includes the intended radio presence or player path; last_verified=2026-03-30; evidence=VM220 public-edge preview and toolbox preview both serve www.frawo-tech.de/radio/public/frawo-funk to AzuraCast; Host www.frawo-tech.de on 192.168.2.22 and 192.168.2.20 returns FraWo - Funk - AzuraCast with HTTP 200.
- `public_mail_model_verified`: `pending` - Public release mail model for webmaster, franz, info and noreply is verified; evidence=webmaster@frawo-tech.de and franz@frawo-tech.de are technically verified for IMAP and SMTP AUTH; public release decision for info@frawo-tech.de and noreply@frawo-tech.de is still open.
- `tls_automation_verified`: `pending` - The chosen public TLS automation path is configured and documented; evidence=Caddy on VM220 is active on 80/443 and ACME now hits the cutover target, but certificate issuance still fails because the public IPv4 path 92.211.33.54:80/443 is not open. IPv6 HTTP is live; router forwarding for IPv4 remains the concrete blocker.
- `spf_dkim_dmarc_verified`: `pending` - SPF, DKIM and DMARC are all intentionally configured for public release; evidence=MX and DMARC are visible in the live checks; SPF is currently not visible and DKIM is not yet documented as verified for release.
- `rollback_runbook_verified`: `pending` - Rollback for DNS, TLS and host-switch is complete and usable

## Blocked Reasons

- critical website Codex check not green: public-https-check=failed
- critical website Codex check not green: public-mail-dns-check=failed
- critical website manual evidence not green: public_browser_acceptance_verified=failed
- critical website manual evidence not green: public_mail_model_verified=pending
- critical website manual evidence not green: tls_automation_verified=pending
- critical website manual evidence not green: spf_dkim_dmarc_verified=pending
- critical website manual evidence not green: rollback_runbook_verified=pending
