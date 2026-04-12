# Executive Roadmap (FraWo GbR)

## Zweck

Diese Datei ist die kompakteste Fuehrungsansicht fuer den aktuellen Projektstand. Sie ersetzt keine Fachdokumente, sondern verdichtet den Masterplan auf die operative Reihenfolge.

## Zielbild

- interner Business-MVP stabil und sichtbar freigabefaehig
- **Brand Identity:** Finalisiert am `2026-04-07` (`High-End Hybrid`)
- **Website-Release:** `www.frawo-tech.de` (Odoo-basiert) als professioneller FraWo-Eventdienstleister-Auftritt mit belastbarer Public-Edge-Auslieferung
- Vollzertifizierung fuer `PBS`, `surface-go-frontend` und `Radio/AzuraCast` getrennt vom MVP
- technisch verifizierte FRAWO-Mailpfade bei `STRATO`

## Stand Heute (Audit 2026-04-09)

- **Status:** Konsistent mit lokalem `NETWORK_STATE.md` und Dashboard-Audit.
- **Brand Kit:** Assets lokal unter `brand_assets/` verfuegbar; `IDENTITY_STANDARD.md` aktualisiert.
- Business-Kern intern laeuft: `Portal`, `Vaultwarden`, `Nextcloud`, `Paperless`, `Odoo`.
- `Vaultwarden` ist intern ueber `HTTPS` erreichbar.
- `webmaster@frawo-tech.de` und `franz@frawo-tech.de` sind technisch gegen `IMAP` und `SMTP AUTH` verifiziert.
- Odoo- und Nextcloud-Reachability-Drift vom `2026-04-07` sind behoben; die internen und mobilen Frontdoors antworten wieder, und das Odoo-Masterprojekt ist jetzt auf den kanonischen SSOT-Stand normalisiert.
- Abendverifikation `2026-04-09`: `Portal=200`, `Odoo=200`, `Paperless=302`, `Nextcloud status=200`, `Vaultwarden alive=200`; mobile Frontdoors `8444=200`, `8445=200`, `8446=302`, `8447=200`.
- Die Odoo-Website auf `VM 220` ist inhaltlich sichtbar auf FraWo gezogen und gestalterisch in Arbeit; echte Bildassets sind wieder eingebunden, `Poppins` ist CI-weit gesetzt, und fuer Design/Hosting liegt jetzt ein separater Claude-Handoff samt Implementierungs-Assets unter `Codex/website/`.
- Der semantische Website-Pfad ist ebenfalls bereinigt: `web.base.url=https://www.frawo-tech.de`, `website.domain=NULL`, dadurch rendern `canonical` und `og:url` im Host-Preview wieder korrekt fuer `www.frawo-tech.de`.
- Die echten Restblocker liegen jetzt nicht mehr bei Odoo-Reachability, sondern bei sichtbarer Operator-Abnahme und den offenen MVP-Gates `device_rollout_verified` sowie `vaultwarden_recovery_material_verified`.
- Der Website-Track ist damit nicht mehr primaer am Odoo-Inhalt blockiert, sondern weiter am getrennten Public-Edge-/Forwarding-Nachweis.
- Der Public-Edge-Block ist jetzt klar eingegrenzt: Caddy kann ACME wieder sauber anfahren, aber `92.211.33.54` liefert fuer `frawo-tech.de` und `www.frawo-tech.de` weiter `Connection refused`; der Restpunkt sitzt damit am externen Forwarding/NAT-Pfad, nicht mehr im Odoo-Website-Inhalt.
- `agent@frawo-tech.de` ist als Alias auf `webmaster@frawo-tech.de` technisch zustellbar verifiziert; offen bleibt die bewusste Incoming-Strategie fuer Odoo ohne serverseitiges `n8n`.
- Diese Incoming-Strategie ist jetzt technisch umgesetzt: `VM 200` trennt `agent@` weiter nach `Aliases.Agent`, die Odoo-Bridge uebernimmt daraus Tasks ins Masterprojekt, und der Timer `hs27-odoo-agent-intake.timer` laeuft aktiv.

## Operative Reihenfolge (MVP Ready Path)

1. **MVP-Abnahme:** sichtbare Geraete-/2FA-Abnahme und Vaultwarden-Recovery-Evidenz abschliessen.
2. **Odoo-SSOT fortfuehren:** laufenden `agent@`-Intake im Alltag bestaetigen, Board-Governance stabil halten und den Bot-Secret-/API-Key-Pfad spaeter weiter haerten.
3. **Website-Public-Edge:** externen Pfad fuer `www.frawo-tech.de` sauber verifizieren, nachdem der Odoo-Inhalt jetzt gruen ist.
4. **HA Proxy Polish:** kleinen Reverse-Proxy-/Trust-Drift fuer `ha.hs27.internal` bereinigen oder bewusst aus dem morgigen Demo-Scope nehmen.
5. **App-Testmails und Release Gates:** SMTP-Restpfade in Odoo pruefen und `release-mvp-gate` auf GRUEN ziehen.

## Heute Abend Parallelspur

- **Claude Track:** FraWo-Website-Design, Text und Hosting-Analyse anhand `CLAUDE_WEBSITE_HOSTING_HANDOFF.md` und `Codex/website/`.
- **Codex Track:** Runtime-SSOT sauber halten, Executive-/Operator-Sicht aktualisieren und die nicht-websitegebundenen MVP-/Odoo-/Mail-Restpunkte weiter vorbereiten.
- **Nicht kollidieren:** keine parallelen Blind-Edits in Odoo-Website-Views, solange Claude den Design-/Hosting-Finish vorbereitet.
- **Ziel fuer morgen produktiv:** interner Business-Core bleibt stabil; Website-Finish und Public-Edge werden getrennt und bewusst freigegeben.
- **Ziel fuer morgen vorzeigbar:** Demo ueber den internen/Tailscale-Pfad ist jetzt realistisch gruen; Public WWW bleibt ein separater Edge-Release.

## Verweise

- Gesamt-Roadmap: `MASTERPLAN.md`
- Mail-Rollout: `MAIL_SYSTEM_ROLLOUT.md`
- Vaultwarden Referenz: `ACCESS_REGISTER_VAULTWARDEN_REFERENCES.md`
- Stockenweiler: `STOCKENWEILER_REMOTE_SUPPORT_PLAN.md`
