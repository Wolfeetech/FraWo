# Executive Roadmap

## Zweck

Diese Datei ist die kompakteste Fuehrungsansicht fuer den aktuellen Projektstand. Sie ersetzt keine Fachdokumente, sondern verdichtet den Masterplan auf die operative Reihenfolge.

## Zielbild

- interner Business-MVP stabil und sichtbar freigabefaehig
- Website-First-Release auf `www.frawo-tech.de` am `2026-04-01`, getragen durch die Odoo-Website mit integrierter Radio-Praesenz
- Vollzertifizierung fuer `PBS`, `surface-go-frontend` und `Radio/AzuraCast` getrennt vom MVP
- technisch verifizierte FRAWO-Mailpfade bei `STRATO`
- produktive Secret-Ablage in `Vaultwarden` innerhalb der Organisation `FraWo`

## Stand Heute (Audit 2026-04-07)

- **Status:** Konsistent mit lokalem `NETWORK_STATE.md` und Inventory.
- Business-Kern intern laeuft: `Portal`, `Vaultwarden`, `Nextcloud`, `Paperless`, `Odoo`.
- `Vaultwarden` ist intern ueber `HTTPS` erreichbar.
- `webmaster@frawo-tech.de` und `franz@frawo-tech.de` sind technisch gegen `IMAP` und `SMTP AUTH` verifiziert.
- Lokale Proxmox-Business-Backups sind vorhanden.
- **Blockiert:** `PBS` (nicht gruen), `surface-go-frontend` (nicht erreichbar), `Radio/AzuraCast` (nicht integriert).

## Operative Reihenfolge (MVP Ready Path)

1. **Business-MVP sichtbar freigeben:**
   - Franz Zugriff auf `FraWo` Kern-Collections in Vaultwarden.
   - Gemeinsamer Durchlauf (Wolf/Franz) durch Apps.
2. **STRATO Mail-Verifizierung:**
   - Test der Postfaecher `wolf@`, `franz@`, `info@`, `noreply@`.
3. **App-Testmails:**
   - Abschluss der SMTP-Integration in Odoo (`test_odoo_smtp.py`).
4. **Release Gates:**
   - `release-mvp-gate` auf GRUEN ziehen.

## Verweise

- Gesamt-Roadmap: `MASTERPLAN.md`
- Mail-Rollout: `MAIL_SYSTEM_ROLLOUT.md`
- Vaultwarden Referenz: `ACCESS_REGISTER_VAULTWARDEN_REFERENCES.md`
- Stockenweiler: `STOCKENWEILER_REMOTE_SUPPORT_PLAN.md`
