# Gemini Browser MVP Acceptance Prompt

## Purpose

- Use this prompt in Gemini Browser AI to execute the open browser-visible MVP acceptance checks.
- Scope is intentionally limited to the manual evidence owned by `gemini_browser_ai` in `manifests/release_mvp_gate/manual_checks.json`.

## Read First

1. `INTRODUCTION_PROMPT.md`
2. `BUSINESS_MVP_PROMPT.md`
3. `artifacts/release_mvp_gate/20260328_072307/release_mvp_gate.md`
4. `ACCESS_REGISTER_VAULTWARDEN_REFERENCES.md`

## Scope

You are only verifying these four manual evidence items:

1. `frawo_access_verified`
2. `vaultwarden_visible_spotcheck`
3. `wolf_login_walkthrough`
4. `franz_login_walkthrough`

Do not expand into:

- `PBS`
- `Radio/AzuraCast`
- `surface-go-frontend`
- public website release
- infrastructure changes

## Working Rules

- Use the browser to verify visible reality, not repo claims.
- Do not change server configuration.
- Do not change passwords.
- Do not mark a check as passed unless the post-login or post-click result is visibly successful.
- If a login step needs operator credentials or operator takeover, stop at that point and ask the operator to take over only for the login action, then continue verification afterwards.
- If something fails, capture the exact page, URL, and visible error text.

## Required URLs

- Portal: `http://portal.hs27.internal`
- Franz portal: `http://portal.hs27.internal/franz/`
- Vaultwarden: `https://vault.hs27.internal`
- Nextcloud: `http://cloud.hs27.internal`
- Paperless: `http://paperless.hs27.internal`
- Odoo: `http://odoo.hs27.internal`

## Vaultwarden Reference Targets

Verify visible access to these imported entries where applicable:

- `FraWo / Business Apps / Nextcloud - franz`
- `FraWo / Business Apps / Paperless - franz`
- `FraWo / Business Apps / Odoo - franz@frawo-tech.de`
- `FraWo / Business Apps / Nextcloud Admin`
- `FraWo / Business Apps / Paperless Admin`
- `FraWo / Business Apps / Odoo Admin`

## Execution Steps

### 1. FraWo access for Franz

- Open `https://vault.hs27.internal`.
- With operator takeover if needed, log in as `Franz`.
- Verify that `Franz` can open the `FraWo` organization.
- Verify that the required business entries for Franz are visible and accessible in the organization.
- Minimum expected visible items:
  - `Nextcloud - franz`
  - `Paperless - franz`
  - `Odoo - franz@frawo-tech.de`

Pass condition for `frawo_access_verified`:

- Franz can enter `FraWo`
- and see the required MVP business entries

### 2. Vaultwarden visible spot-check

- In Vaultwarden, verify visible and usable presence of the core imported entries:
  - `Nextcloud Admin`
  - `Paperless Admin`
  - `Odoo Admin`
- You do not need to expose or copy passwords.
- It is enough to confirm the items exist, open correctly, and visibly contain the expected username and URL structure.

Pass condition for `vaultwarden_visible_spotcheck`:

- the core imported entries are present
- titles are correct
- usernames and URLs visibly match the expected systems

### 3. Wolf walkthrough

- Using operator takeover for login if needed, verify this visible sequence for `Wolf`:
  - Vaultwarden opens
  - Nextcloud login succeeds and lands in the app
  - Paperless login succeeds and lands in the app
  - Odoo login succeeds and lands in the app

Pass condition for `wolf_login_walkthrough`:

- all four steps complete successfully in the browser

### 4. Franz walkthrough

- Using operator takeover for login if needed, verify this visible sequence for `Franz`:
  - Vaultwarden opens
  - Nextcloud login succeeds and lands in the app
  - Paperless login succeeds and lands in the app
  - Odoo login succeeds and lands in the app

Pass condition for `franz_login_walkthrough`:

- all four steps complete successfully in the browser

## Final Output Format

Return the result in exactly this structure:

```text
MVP Browser Acceptance Result

frawo_access_verified: passed|failed
last_verified: YYYY-MM-DD
evidence: ...

vaultwarden_visible_spotcheck: passed|failed
last_verified: YYYY-MM-DD
evidence: ...

wolf_login_walkthrough: passed|failed
last_verified: YYYY-MM-DD
evidence: ...

franz_login_walkthrough: passed|failed
last_verified: YYYY-MM-DD
evidence: ...

Open blockers:
- ...
```

If any check fails, include the exact failing URL and the visible error text.
