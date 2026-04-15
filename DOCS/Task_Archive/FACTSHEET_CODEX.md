# Handoff Factsheet (Codex & Operations)

Stand: `2026-04-10`
Status: **Business Ready (8/10)**

## 1. Technischer Status-Quo

### Odoo (VM 220) - Single Source of Truth
- **Datenbank:** `FraWo_GbR` (aktiv & verknüpft)
- **User:** `wolf@frawo-tech.de` (Admin), `franz@frawo-tech.de`, `agent@frawo-tech.de`
- **Branding:** High-End Hybrid (Deep Forest `#064e3b`)
- **Tasks:** Masterplan (IDs 273-276) sind wiederhergestellt und live.

### Kommunikations-Infrastruktur
- **SMTP-Relay:** Strato (`smtp.strato.de:587`)
- **Hardening:** `extra_hosts` Eintrag für `smtp.strato.de:81.169.145.133` in Docker-Stacks (Nextcloud + Odoo) gegen DNS-Drift.
- **DNS:** Interner Resolver via AdGuard (`toolbox.hs27.internal`).

## 2. Kritische Logins & Pfade

| Dienst | URL | Login |
| --- | --- | --- |
| Odoo | `odoo.hs27.internal` | `wolf@frawo-tech.de` |
| Nextcloud | `cloud.hs27.internal` | `wolf@frawo-tech.de` |
| Vaultwarden | `vault.hs27.internal` | `wolf@frawo-tech.de` |
| Toolbox | `10.1.0.20` | `root` (SSH Key) |

## 3. Offene Punkte (Handoff an Codex)

- **Stocki-HDD:** Die Einbindung des Remote-Speichers aus Stockenweiler ist vorbereitet (Tailscale steht), muss aber noch final in Nextcloud gemountet werden (`files_external`).
- **Website-Audit:** Der inhaltliche Check der Odoo-Snippets auf "KI-Texte" sollte durch Franz/Wolf nach dem Release-Gate erfolgen.

## 4. Next Actions for Operator

- [ ] **Release-Gate:** Setzen des `release-mvp-gate.md` auf GRÜN.
- [ ] **Email-Test:** Versand einer Testmail aus Odoo an `franz@frawo-tech.de`.
