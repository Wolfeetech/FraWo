# OPS Home

## Zweck

Diese Datei ist die zentrale Operator-Startseite fuer den aktuellen Plattformstand, die Release-Vorbereitung und die naechsten Arbeitspakete.

## Jetzt zuerst lesen

- Einstieg fuer Wolf und Franz: `START_HERE_WOLF_FRANZ.md`
- Nutzer-Handout: `WOLF_FRANZ_HANDOUT.md`
- Abarbeitungs-Checkliste: `CHECKLIST_NEXT_STEPS_WOLF_FRANZ.md`
- Vaultwarden Start: `VAULTWARDEN_SELFHOST_START.md`
- STRATO Mail Rollout: `STRATO_MAIL_ACCOUNT_ROLLOUT_CHECKLIST.md`
- STRATO Mail Client Setup: `STRATO_MAIL_CLIENT_SETUP.md`
- Executive Roadmap: `EXECUTIVE_ROADMAP.md`
- Gesamtstatus: `PLATFORM_STATUS.md`
- Gesamt-Roadmap: `MASTERPLAN.md`
- Tool-Betriebsanweisungen: `OPERATIONS/TOOLS_OPERATIONS_INDEX.md`
- Zugangsregister: `ACCESS_REGISTER.md`
- Vaultwarden-Referenzregister: `ACCESS_REGISTER_VAULTWARDEN_REFERENCES.md`
- Identitaetsstandard: `IDENTITY_STANDARD.md`
- Release-Akte: `RELEASE_READINESS_2026-04-01.md`

## Release und Public

- Public Edge: `PUBLIC_EDGE_ARCHITECTURE_PLAN.md`
- Mail-Rollout: `MAIL_SYSTEM_ROLLOUT.md`
- Mail -> Paperless -> Nextcloud: `MAIL_TO_PAPERLESS_NEXTCLOUD_ARCHITECTURE.md`
- Nextcloud Mail + Odoo Mail: `NEXTCLOUD_MAIL_AND_ODOO_MAIL_ARCHITECTURE.md`
- Vaultwarden + STRATO Runbook: `BITWARDEN_STRATO_EXECUTION_RUNBOOK.md`
- Vaultwarden Recovery Sheet: `VAULTWARDEN_RECOVERY_SHEET.md`
- Vaultwarden Internal HTTPS Rollout: `VAULTWARDEN_INTERNAL_HTTPS_ROLLOUT.md`
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
- Produktiver Vaultwarden-Login ist nur ueber `https://vault.hs27.internal` freigegeben.
- Der erste produktive Vaultwarden-Benutzer ist `wolf@frawo-tech.de`.
- Das Vaultwarden-Master-Passwort wird nur manuell gesetzt und nur offline gesichert.
- Passwoerter muessen in `Vaultwarden`, nicht dauerhaft in Markdown-Dateien, enden.
- `Rentner OS` fuer Stockenweiler startet als Managed Support Service, nicht als voll integrierter Zweitstandort.

## Offene manuelle Blocker

1. Internen `HTTPS`-Pfad fuer Vaultwarden bauen.
2. `wolf@frawo-tech.de` als ersten produktiven Vaultwarden-Benutzer anlegen und Recovery offline sichern.
3. Produktive `STRATO`- und Core-Infra-Logins nach Vaultwarden uebernehmen.
4. Externen Off-LAN-Scan vom Handy testen.
5. Website-/DNS-/TLS-Release-Gate auf Gruen ziehen.
