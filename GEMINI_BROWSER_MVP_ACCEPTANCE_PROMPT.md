# Gemini Browser MVP Acceptance Prompt

## Purpose

- Use this prompt in Gemini Browser AI to execute the currently open browser-visible MVP acceptance work.
- Scope is intentionally limited to the remaining rollout-visible part of `device_rollout_verified`.

## Read First

1. `INTRODUCTION_PROMPT.md`
2. `BUSINESS_MVP_PROMPT.md`
3. `artifacts/release_mvp_gate/latest_release_mvp_gate.md`
4. `OPERATIONS/USER_ONBOARDING_OPERATIONS.md`
5. `OPERATOR_TODO_QUEUE.md`

## Scope

You are only verifying the still-open MVP rollout item:

1. `device_rollout_verified`

Do not expand into:

- `vaultwarden_recovery_material_verified`
- `PBS`
- `Radio/AzuraCast` expansion
- public website release
- infrastructure changes

## Working Rules

- Use the browser to verify visible reality, not repo claims.
- Do not change server configuration.
- Do not change passwords.
- Do not mark the rollout as passed unless the visible entry path and app targets are really usable.
- If a device-local step needs operator takeover or the real device in hand, stop at that point and say so plainly.
- If something fails, capture the exact URL and the visible error text.

## Required Entry Paths

- Franz laptop path: `http://portal.hs27.internal/franz/`
- Franz mobile path: `http://100.99.206.128:8447/franz/`
- Nextcloud: `http://cloud.hs27.internal`
- Paperless: `http://paperless.hs27.internal`
- Odoo: `http://odoo.hs27.internal`
- Vaultwarden: `https://vault.hs27.internal`

## Execution Steps

### 1. Surface Laptop acceptance

- Open `http://portal.hs27.internal/franz/`
- Verify that the Franz start page is visibly usable as the primary entrypoint
- Verify that the direct targets for `Nextcloud`, `Paperless`, `Odoo`, and `Vaultwarden` are visibly present and clickable
- If login is required, operator takeover is allowed only for the login step
- Count this device as passed only if the laptop start path is visibly usable for everyday work

### 2. iPhone acceptance

- Open `http://100.99.206.128:8447/franz/`
- Use a mobile viewport if the real iPhone browser is not directly available
- Verify that the mobile Franz entry page is visibly usable
- Verify that the core targets for `Nextcloud`, `Paperless`, `Odoo`, and `Vaultwarden` are visibly present from that mobile start path
- If the browser session cannot prove the real device-local step, say that clearly instead of inventing completion

## Pass Condition

`device_rollout_verified` may only be treated as `passed` if:

- the Franz laptop path is visibly usable
- the Franz mobile path is visibly usable
- the direct core targets are present from both entry paths
- no visible blocker remains for the everyday start path

## Final Output Format

Return the result in exactly this structure:

```text
MVP Device Rollout Result

device_rollout_verified: passed|failed
last_verified: YYYY-MM-DD

surface_laptop: passed|failed
surface_laptop_evidence: ...

iphone: passed|failed
iphone_evidence: ...

Open blockers:
- ...
```

If any part fails, include the exact failing URL and the visible error text.
