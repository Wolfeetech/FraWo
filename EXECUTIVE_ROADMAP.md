# Executive Roadmap

## Zweck

Diese Datei ist die kompakteste Fuehrungsansicht fuer den aktuellen Projektstand. Sie ersetzt keine Fachdokumente, sondern verdichtet den Masterplan auf die operative Reihenfolge.

## Zielbild

- interner Plattformbetrieb stabil und reproduzierbar
- Website-First-Release auf `www.frawo-tech.de` am `2026-04-01`
- reale FRAWO-Mailboxen bei `STRATO`
- produktive Secret-Ablage in `Vaultwarden` innerhalb der Organisation `FraWo`
- Stockenweiler als erster externer `Rentner OS`-Testkunde ueber `Tailscale-only`

## Stand Heute

- Infrastruktur intern laeuft
- Media/Radio laufen auf dem SMB-Zielpfad
- Kern-Logins und personengebundene App-User sind gesetzt
- Public Edge ist noch bewusst nicht live
- Mail und Secrets sind der groesste offene Betriebsblock
- Storage ist operativ beruhigt, aber architektonisch noch nicht final

## Jetzt in Reihenfolge

1. `Vaultwarden` intern per `HTTPS` fertigstellen
2. Organisation `FraWo` und die Collections produktiv aufsetzen
3. produktive Logins aus `ACCESS_REGISTER.md` nach Vaultwarden ueberfuehren
4. STRATO-Mailboxen anlegen:
   - `wolf@frawo-tech.de`
   - `franz@frawo-tech.de`
   - `info@frawo-tech.de`
   - `noreply@frawo-tech.de`
5. SPF, DKIM, DMARC dokumentieren und testen
6. Website-Release-Gate fuer `www.frawo-tech.de` auf Gruen ziehen
7. danach Stockenweiler / `Rentner OS` v1 vorbereiten

## Nicht Jetzt

- keine oeffentlichen Admin-UIs
- kein breiter Radio-Public-Rollout
- kein Site-to-Site-VPN nach Stockenweiler
- kein Google-Workspace-Cutover
- keine Google-Drive-Integration vor dem ersten stabilen Release

## Definition Of Success

- Secrets liegen produktiv in Vaultwarden innerhalb der Organisation `FraWo`, nicht nur in Markdown
- Mail funktioniert real fuer Wolf, Franz und Systemabender
- `www.frawo-tech.de` ist klein, sauber und kontrolliert live
- interner Betrieb bleibt unangetastet stabil
- erster externer Supportpfad nach Stockenweiler ist kontrolliert nutzbar
- die Plattform haelt einen kontrollierten internen Stresstest aus

## Verweise

- Gesamt-Roadmap: `MASTERPLAN.md`
- Release-Akte: `RELEASE_READINESS_2026-04-01.md`
- Stress-Test: `STRESS_TEST_READINESS.md`
- Mail-Rollout: `MAIL_SYSTEM_ROLLOUT.md`
- Vaultwarden + STRATO Runbook: `BITWARDEN_STRATO_EXECUTION_RUNBOOK.md`
- Google Drive: `GOOGLE_DRIVE_INTEGRATION_PLAN.md`
- Zugangsregister: `ACCESS_REGISTER.md`
- Stockenweiler: `STOCKENWEILER_REMOTE_SUPPORT_PLAN.md`
