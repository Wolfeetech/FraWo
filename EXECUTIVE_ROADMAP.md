# Executive Roadmap

## Zweck

Diese Datei ist die kompakteste Fuehrungsansicht fuer den aktuellen Projektstand. Sie ersetzt keine Fachdokumente, sondern verdichtet den Masterplan auf die operative Reihenfolge.

## Zielbild

- interner Business-MVP stabil und sichtbar freigabefaehig
- Website-First-Release auf `www.frawo-tech.de` am `2026-04-01`, getragen durch die Odoo-Website mit integrierter Radio-Praesenz
- Vollzertifizierung fuer `PBS`, `surface-go-frontend` und `Radio/AzuraCast` getrennt vom MVP
- technisch verifizierte FRAWO-Mailpfade bei `STRATO`
- produktive Secret-Ablage in `Vaultwarden` innerhalb der Organisation `FraWo`

## Stand Heute

- Business-Kern intern laeuft:
  - `Portal`
  - `Vaultwarden`
  - `Nextcloud`
  - `Paperless`
  - `Odoo`
- Kern-Logins und personengebundene App-User sind gesetzt
- `Vaultwarden` ist intern ueber `HTTPS` erreichbar
- `Vaultwarden`-Invite fuer `Franz` ist angenommen
- Basis-Import der bestehenden App-Logins in die Organisation `FraWo` ist erfolgt
- `webmaster@frawo-tech.de` und `franz@frawo-tech.de` sind technisch gegen `IMAP` und `SMTP AUTH` verifiziert
- lokale Proxmox-Business-Backups sind real vorhanden und timerbasiert
- Public Edge ist noch bewusst nicht live
- Vollzertifizierung ist weiter blockiert:
  - `PBS` nicht gruen
  - `surface-go-frontend` nicht erreichbar
  - `Radio/AzuraCast` nicht als integrierter Produktionspfad verifiziert

## Jetzt in Reihenfolge

1. Business-MVP sichtbar freigeben:
   - `Franz` sieht `FraWo` und Kern-Collections
   - Wolf- und Franz-Durchlauf durch `Vault`, `Nextcloud`, `Paperless`, `Odoo`
   - Franz `Surface Laptop` und `iPhone` sichtbar abnehmen
2. `STRATO`-Alias-/Postfachmodell sichtbar verifizieren:
   - `wolf@frawo-tech.de` als Alias ueber `webmaster@...`
   - `franz@frawo-tech.de` als eigenes Postfach
   - `info@frawo-tech.de` technisch pruefen
   - `noreply@frawo-tech.de` technisch pruefen
3. sichtbare App-Testmails fuer `Nextcloud`, `Paperless` und `Odoo` abschliessen
4. `release-mvp-gate` auf Gruen ziehen
5. parallel den Website-Release fuer `www.frawo-tech.de` vorbereiten:
   - Zielsystem = Odoo-Website auf `VM220`
   - DNS/Redirect
   - TLS
   - sichtbare Radio-Integration auf der Website
   - SPF/DKIM/DMARC
   - Rollback
6. Vollzertifizierung getrennt weiterfuehren:
   - `PBS`
   - `surface-go-frontend`
   - `Radio/AzuraCast`
7. erst danach Stockenweiler / `Rentner OS` v1 vorbereiten

## Nicht Jetzt

- keine oeffentlichen Admin-UIs
- kein separates `radio.frawo-tech.de` als Pflicht im ersten Release; Radio muss in die Website integriert sein
- kein Site-to-Site-VPN nach Stockenweiler
- kein Google-Workspace-Cutover
- keine Google-Drive-Integration vor dem ersten stabilen Release

## Definition Of Success

- Secrets liegen produktiv in Vaultwarden innerhalb der Organisation `FraWo`, nicht nur in Markdown
- Mail funktioniert sichtbar fuer Wolf, Franz und die Systemabsender des MVP
- `release-mvp-gate` meldet `MVP_READY`
- `www.frawo-tech.de` ist als Odoo-Website klein, sauber und kontrolliert live, inklusive sichtbarer Radio-Praesenz
- interner Betrieb bleibt unangetastet stabil
- `production-gate` darf getrennt weiter `BLOCKED` bleiben, solange `PBS`, `surface-go` und `Radio` offen sind

## Verweise

- Gesamt-Roadmap: `MASTERPLAN.md`
- Release-Akte: `RELEASE_READINESS_2026-04-01.md`
- Stress-Test: `STRESS_TEST_READINESS.md`
- Mail-Rollout: `MAIL_SYSTEM_ROLLOUT.md`
- Vaultwarden + STRATO Uebergang: `BITWARDEN_STRATO_EXECUTION_RUNBOOK.md`
- Google Drive: `GOOGLE_DRIVE_INTEGRATION_PLAN.md`
- Vaultwarden-Referenzregister: `ACCESS_REGISTER_VAULTWARDEN_REFERENCES.md`
- Stockenweiler: `STOCKENWEILER_REMOTE_SUPPORT_PLAN.md`
