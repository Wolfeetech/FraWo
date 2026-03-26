# OPS Home

## Zweck

Diese Datei ist die zentrale Operator-Startseite fuer den aktuellen Plattformstand, die Release-Vorbereitung und die naechsten Arbeitspakete.

## Jetzt zuerst lesen

- Executive Roadmap: `EXECUTIVE_ROADMAP.md`
- Gesamtstatus: `PLATFORM_STATUS.md`
- Gesamt-Roadmap: `MASTERPLAN.md`
- Tool-Betriebsanweisungen: `OPERATIONS/TOOLS_OPERATIONS_INDEX.md`
- Zugangsregister: `ACCESS_REGISTER.md`
- Identitaetsstandard: `IDENTITY_STANDARD.md`
- Release-Akte: `RELEASE_READINESS_2026-04-01.md`

## Release und Public

- Public Edge: `PUBLIC_EDGE_ARCHITECTURE_PLAN.md`
- Mail-Rollout: `MAIL_SYSTEM_ROLLOUT.md`
- Bitwarden + STRATO Runbook: `BITWARDEN_STRATO_EXECUTION_RUNBOOK.md`
- Hosting-Optionen: `ONLINE_HOSTING_OPTIONS.md`
- Google-Drive-Plan: `GOOGLE_DRIVE_INTEGRATION_PLAN.md`
- Odoo-Studio-Entscheidung: `ODOO_STUDIO_DECISION.md`

## Betrieb und Benutzer

- Mobile-Scan-Workflow: `MOBILE_SCAN_WORKFLOW.md`
- Stress-Test-Readiness: `STRESS_TEST_READINESS.md`
- Stockenweiler / Rentner OS: `STOCKENWEILER_REMOTE_SUPPORT_PLAN.md`
- Medien / Radio Baseline: `AZURACAST_FIRST_STATION_BASELINE.md`
- Jellyfin User Setup: `JELLYFIN_USER_SETUP_PLAN.md`

## Aktuelle Leitplanken

- Interne Plattform ist betriebsfaehig.
- Oeffentlich live gehen zum `2026-04-01` soll nur die Website auf `www.frawo-tech.de`.
- Interne Apps bleiben intern oder Tailscale-only.
- Mailboxen entstehen zuerst bei `STRATO`.
- Passwoerter muessen in `Bitwarden Cloud`, nicht dauerhaft in Markdown-Dateien, enden.
- `Rentner OS` fuer Stockenweiler startet als Managed Support Service, nicht als voll integrierter Zweitstandort.

## Offene manuelle Blocker

1. STRATO-Mailboxen anlegen.
2. Bitwarden-Organisation/Vault aufsetzen.
3. Produktive Logins nach Bitwarden uebernehmen.
4. Externen Off-LAN-Scan vom Handy testen.
5. Website-/DNS-/TLS-Release-Gate auf Gruen ziehen.
