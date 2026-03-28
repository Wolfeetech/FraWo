# Website Release Prompt

## Purpose

- Use this prompt for research and planning limited to the first public website release.
- This prompt is not for internal app rollout and not for full internal certification.

## Deciding Sources

- `INTRODUCTION_PROMPT.md`
- `RELEASE_READINESS_2026-04-01.md`
- `PUBLIC_EDGE_ARCHITECTURE_PLAN.md`
- `MASTERPLAN.md`
- current `artifacts/` tree, which currently contains no dedicated website gate artifact

## Current Hard Release Boundary

- Planned first public release is website-only.
- Current scope:
  - `frawo-tech.de` redirects to `www.frawo-tech.de`
  - `www.frawo-tech.de` serves the public GbR website
- Explicitly not in scope:
  - public `Nextcloud`
  - public `Paperless`
  - public `Odoo`
  - public `Home Assistant`
  - public `Proxmox`
  - public `PBS`
  - public `AdGuard`
  - public toolbox admin paths
  - public radio path in the first release

## Current Hard Facts

- Public Edge is not live.
- The current workspace policy keeps internal business apps internal or Tailscale-only.
- There is no separate green public website gate artifact in `artifacts/` yet.
- The internal Business-MVP is on a separate track and currently has a technical green audit but still a blocked manual gate.

## Current Website Release Blockers

- target system for `www.frawo-tech.de` is not yet green in the current release docs
- DNS / redirect model still needs final verification
- TLS automation still needs final verification
- SPF, DKIM, and DMARC still need final verification
- rollback for DNS / TLS / host switch still needs final verification
- visible mail model for `webmaster`, `franz`, `info`, and `noreply` is still not fully verified

## Guardrails

- Do not assume the first website release depends on `PBS` being green.
- Do not assume the first website release includes any internal business UI.
- Do not assume `radio.frawo-tech.de` belongs to the first release.
- Do not describe any website target as live unless it is verified separately.
- Keep the website scope small and rollback-friendly.
