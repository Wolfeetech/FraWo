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
- Odoo- und Nextcloud-Reachability-Drift vom `2026-04-07` sind behoben; die internen und mobilen Frontdoors antworten wieder, und das Odoo-Masterprojekt ist jetzt auf den kanonischen SSOT-Stand normalisiert.
- Die echten Restblocker liegen jetzt nicht mehr bei Odoo-Reachability, sondern bei sichtbarer Operator-Abnahme und den offenen MVP-Gates `device_rollout_verified` sowie `vaultwarden_recovery_material_verified`.

## Operative Reihenfolge (MVP Ready Path)

1. **MVP-Abnahme:** sichtbare Geraete-/2FA-Abnahme und Vaultwarden-Recovery-Evidenz abschliessen.
2. **Odoo-SSOT fortfuehren:** API-Key-Hardening fuer `agent@`, Incoming-Alias vorbereiten und Board-Governance im Alltag bestaetigen.
3. **Website-Branding:** Logo-Upload und CI-Farben (Deep Forest/UV Power) in Odoo anwenden.
4. **App-Testmails und Release Gates:** SMTP-Restpfade in Odoo pruefen und `release-mvp-gate` auf GRUEN ziehen.

## Verweise

- Gesamt-Roadmap: `MASTERPLAN.md`
- Mail-Rollout: `MAIL_SYSTEM_ROLLOUT.md`
- Vaultwarden Referenz: `ACCESS_REGISTER_VAULTWARDEN_REFERENCES.md`
- Stockenweiler: `STOCKENWEILER_REMOTE_SUPPORT_PLAN.md`
