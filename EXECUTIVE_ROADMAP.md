# Executive Roadmap (FraWo GbR)

## Zweck

Diese Datei ist die kompakteste Fuehrungsansicht fuer den aktuellen Projektstand. Sie ersetzt keine Fachdokumente, sondern verdichtet den Masterplan auf die operative Reihenfolge.

## Zielbild

- interner Business-MVP stabil und sichtbar freigabefaehig
- **Brand Identity:** Finalisiert am `2026-04-07` (`High-End Hybrid`)
- **Website-Release:** `www.frawo-tech.de` (Odoo-basiert) mit Fokus auf Handwerk/IT-Symbiose und Radio-Integration
- Vollzertifizierung fuer `PBS`, `surface-go-frontend` und `Radio/AzuraCast` getrennt vom MVP
- technisch verifizierte FRAWO-Mailpfade bei `STRATO`

## Stand Heute (Audit 2026-04-07)

- **Status:** Konsistent mit lokalem `NETWORK_STATE.md` und Dashboard-Audit.
- **Brand Kit:** Assets lokal unter `brand_assets/` verfuegbar; `IDENTITY_STANDARD.md` aktualisiert.
- Business-Kern intern laeuft: `Portal`, `Vaultwarden`, `Nextcloud`, `Paperless`, `Odoo`.
- `Vaultwarden` ist intern ueber `HTTPS` erreichbar.
- `webmaster@frawo-tech.de` und `franz@frawo-tech.de` sind technisch gegen `IMAP` und `SMTP AUTH` verifiziert.
- **Blockiert:** Odoo Reachability-Drift. Spot-Check `2026-04-07`: `http://100.99.206.128:8447/` ist gruen, aber `http://100.99.206.128:8444/web/login` ist nicht erreichbar und `http://odoo.hs27.internal/web/login` liefert `502`.

## Operative Reihenfolge (MVP Ready Path)

1. **Odoo Reachability Fix:** internen Odoo-Upstream (`10.1.0.22:8069`) und danach die Caddy-Proxy-Kette verifizieren, bevor weitere Odoo-Automation aktiviert wird.
2. **Website-Branding:** Logo-Upload und CI-Farben (Deep Forest/UV Power) in Odoo anwenden.
3. **App-Testmails:** Abschluss der SMTP-Integration in Odoo (`test_odoo_smtp.py`).
4. **Release Gates:** `release-mvp-gate` auf GRUEN ziehen.

## Verweise

- Gesamt-Roadmap: `MASTERPLAN.md`
- Mail-Rollout: `MAIL_SYSTEM_ROLLOUT.md`
- Vaultwarden Referenz: `ACCESS_REGISTER_VAULTWARDEN_REFERENCES.md`
- Stockenweiler: `STOCKENWEILER_REMOTE_SUPPORT_PLAN.md`
