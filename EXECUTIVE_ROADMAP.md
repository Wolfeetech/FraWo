# Executive Roadmap (FraWo GbR)

## Zweck

Diese Datei ist die kompakteste Fuehrungsansicht fuer den aktuellen Projektstand. Sie ersetzt keine Fachdokumente, sondern verdichtet den Masterplan auf die operative Reihenfolge.

## Zielbild

- interner Business-MVP stabil und sichtbar freigabefaehig
- **Brand Identity:** Finalisiert am 07.04.2026 ("High-End Hybrid")
- **Website-Release:** `www.frawo-tech.de` (Odoo-basiert) mit Fokus auf Handwerk/IT-Symbiose und Radio-Integration
- Vollzertifizierung fuer `PBS`, `surface-go-frontend` und `Radio/AzuraCast` getrennt vom MVP
- technisch verifizierte FRAWO-Mailpfade bei `STRATO`

## Stand Heute (Audit 2026-04-07)

- **Status:** Konsistent mit lokalem `NETWORK_STATE.md` und Dashboard-Audit.
- **Brand Kit:** Assets lokal unter `brand_assets/` verfügbar; `IDENTITY_STANDARD.md` aktualisiert.
- Business-Kern intern laeuft: `Portal`, `Vaultwarden`, `Nextcloud`, `Paperless`, `Odoo`.
- `Vaultwarden` ist intern ueber `HTTPS` erreichbar.
- `webmaster@frawo-tech.de` und `franz@frawo-tech.de` sind technisch gegen `IMAP` und `SMTP AUTH` verifiziert.
- **Blockiert:** Odoo Erreichbarkeit für `frawo-tech.de` via Caddy (Lane 1 der Tages-Roadmap).

## Operative Reihenfolge (MVP Ready Path)

1. **Odoo Reachability Fix:** Caddy-Proxy-Kette für `frawo-tech.de` wiederherstellen.
2. **Website-Branding:** Logo-Upload und CI-Farben (Deep Forest/UV Power) in Odoo anwenden.
3. **App-Testmails:** Abschluss der SMTP-Integration in Odoo (`test_odoo_smtp.py`).
4. **Release Gates:** `release-mvp-gate` auf GRUEN ziehen.

## Verweise

- Gesamt-Roadmap: `MASTERPLAN.md`
- Mail-Rollout: `MAIL_SYSTEM_ROLLOUT.md`
- Vaultwarden Referenz: `ACCESS_REGISTER_VAULTWARDEN_REFERENCES.md`
- Stockenweiler: `STOCKENWEILER_REMOTE_SUPPORT_PLAN.md`
