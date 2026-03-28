# OPS Home

## Zweck

Diese Datei ist die zentrale Operator-Startseite fuer den aktuellen Plattformstand, die Release-Vorbereitung und die naechsten Arbeitspakete.

## Kanonischer Wiki-Stand

Diese Dateien sind ab jetzt die Zielstruktur, in die wir offene Arbeit und Wissen Schritt fuer Schritt zusammenziehen:

- `OPS_HOME.md`
  - zentrale Startseite und Arbeitsreihenfolge
- `PLATFORM_STATUS.md`
  - verifizierter Plattform- und Incident-Status
- `OPERATIONS/TOOLS_OPERATIONS_INDEX.md`
  - Einstieg in die dienstspezifischen Betriebsanweisungen
- `OPERATIONS/*.md`
  - kanonische Runbooks pro Dienst
- `OPERATIONS/OPERATOR_ROUTINES.md`
  - kanonischer Start-, Close- und Handoff-Pfad fuer den Operator-Tag
- `OPERATIONS/MAIL_OPERATIONS.md`
  - kanonischer Mail-, Mailbox- und App-SMTP-Betriebspfad
- `OPERATIONS/PRODUCTION_READINESS_OPERATIONS.md`
  - kanonischer Freigabe- und Zertifizierungspfad fuer produktiven Betrieb
- `OPERATIONS/DOCUMENT_OWNERSHIP_OPERATIONS.md`
  - kanonischer Zuständigkeitsstandard fuer Markdown-Seiten
- `OPERATIONS/USER_ONBOARDING_OPERATIONS.md`
  - kanonischer Benutzer-, Geraete- und Onboardingpfad
- `IDENTITY_STANDARD.md`
  - Benutzer-, Rollen- und Organisationsstandard
- `INTERNAL_COMMUNICATION_STANDARD.md`
  - kanonischer Kommunikations- und Mail-Grundsatz
- `MAIL_SYSTEM_ROLLOUT.md`
  - Mail-Rollout und SMTP-Zielzustand
- `ACCESS_REGISTER_VAULTWARDEN_REFERENCES.md`
  - passwortfreie Arbeitsreferenz

## Uebergangsdokumente Mit Rueckbauziel

Diese Dateien bleiben nur so lange bestehen, bis ihr Inhalt sauber in den Wiki-Kanon ueberfuehrt ist:

- `START_HERE_WOLF_FRANZ.md`
- `WOLF_FRANZ_HANDOUT.md`
- `CHECKLIST_NEXT_STEPS_WOLF_FRANZ.md`
- `MORNING_ROUTINE.md`
- `EVENING_ROUTINE.md`
- `STRATO_MAIL_ACCOUNT_ROLLOUT_CHECKLIST.md`
- `STRATO_MAIL_CLIENT_SETUP.md`
- `STRESS_TEST_READINESS.md`
- `BITWARDEN_STRATO_EXECUTION_RUNBOOK.md`

## Jetzt zuerst lesen

- `INTRODUCTION_PROMPT.md`
- `BUSINESS_MVP_PROMPT.md` oder `WEBSITE_RELEASE_PROMPT.md` oder `FULL_CERTIFICATION_PROMPT.md` je nach Arbeitsmodus
- `GEMINI_BROWSER_MVP_ACCEPTANCE_PROMPT.md` fuer die offenen Browser-Abnahmen im MVP
- `AI_BOOTSTRAP_CONTEXT.md`
- `OPERATOR_TODO_QUEUE.md`
- Release-MVP-Gate: `artifacts/release_mvp_gate/...`
- Produktions-Gate: `OPERATIONS/PRODUCTION_READINESS_OPERATIONS.md`
- Dokument-Ownership: `OPERATIONS/DOCUMENT_OWNERSHIP_OPERATIONS.md`
- Benutzer-Onboarding: `OPERATIONS/USER_ONBOARDING_OPERATIONS.md`
- Operator-Routinen: `OPERATIONS/OPERATOR_ROUTINES.md`
- Vaultwarden Start: `VAULTWARDEN_SELFHOST_START.md`
- Mail Operations: `OPERATIONS/MAIL_OPERATIONS.md`
- Executive Roadmap: `EXECUTIVE_ROADMAP.md`
- Gesamtstatus: `PLATFORM_STATUS.md`
- Gesamt-Roadmap: `MASTERPLAN.md`
- Tool-Betriebsanweisungen: `OPERATIONS/TOOLS_OPERATIONS_INDEX.md`
- Vaultwarden-Referenzregister: `ACCESS_REGISTER_VAULTWARDEN_REFERENCES.md`
- Identitaetsstandard: `IDENTITY_STANDARD.md`
- Release-Akte: `RELEASE_READINESS_2026-04-01.md`

## Release und Public

- Public Edge: `PUBLIC_EDGE_ARCHITECTURE_PLAN.md`
- Release-MVP-Gate: `make release-mvp-gate`
- Mail-Rollout: `OPERATIONS/MAIL_OPERATIONS.md`
- Interner Kommunikationsstandard: `INTERNAL_COMMUNICATION_STANDARD.md`
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
- Produktions-Freigabe: `OPERATIONS/PRODUCTION_READINESS_OPERATIONS.md`
- Dokument-Ownership: `OPERATIONS/DOCUMENT_OWNERSHIP_OPERATIONS.md`
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

1. `Vaultwarden` fuer Wolf und Franz sichtbar gegenpruefen.
2. Wolf- und Franz-Durchlauf fuer `Vault`, `Nextcloud`, `Paperless`, `Odoo` sichtbar abschliessen.
3. `STRATO`-Send/Receive fuer `webmaster`, `franz`, `noreply` sichtbar verifizieren.
4. Sichtbare App-Testmails fuer `Nextcloud`, `Paperless`, `Odoo` abschliessen.
5. Das alte Klartext-Register bleibt nur noch als Desktop-Archiv ausserhalb des Workspaces; im Repo gilt nur noch `ACCESS_REGISTER_VAULTWARDEN_REFERENCES.md`.
6. Erweiterungen wie `Media`, `Radio`, `surface-go-frontend` und `PBS` erst nach stabilem Arbeits-MVP wieder aufmachen.
