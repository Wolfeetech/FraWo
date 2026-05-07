# Odoo Agent Intake Restore Checklist (2026-05-03)

## Ausgangslage

- Der historische Intake-Pfad auf `VM 200 nextcloud` ist aktuell drifted.
- Live vorhanden ist derzeit nur `homeserver-compose-nextcloud.service`.
- Die dokumentierten Alias-Router- und Odoo-Intake-Dateien sowie ihre systemd-Units fehlen aktuell.
- `agent@frawo-tech.de` existiert in Odoo weiter, hat aber derzeit `0` API-Keys.
- DNS wirkt konfiguriert, loest externe IMAP-Ziele auf `VM 200` aber aktuell nicht belastbar auf.

## Restore-Gates

- Kein produktiver Lauf, bevor `imap.strato.de` auf `VM 200` wieder sauber aufgeloest wird.
- Kein neuer `agent@`-API-Key ohne root-only Ablagepfad ausserhalb des Repos.
- Kein `--apply`, bevor der Alias-Router auf `Aliases.Agent` wieder verifiziert arbeitet.

## Technische Mindestschritte

1. DNS auf `VM 200` reparieren und gegen `imap.strato.de` verifizieren.
2. Den produktiven IMAP-Secret-Pfad auf `VM 200` wiederherstellen oder neu definieren.
3. Alias-Router-Runtime wieder ausrollen:
   - `/opt/homeserver2027/tools/nextcloud_imap_alias_router.py`
   - `/usr/local/sbin/nextcloud_alias_router_runner.sh`
   - `hs27-nextcloud-alias-router.service`
   - `hs27-nextcloud-alias-router.timer`
4. Odoo-Intake-Runtime wieder ausrollen:
   - `/opt/homeserver2027/tools/odoo_rpc_client.py`
   - `/opt/homeserver2027/tools/odoo_agent_intake_bridge.py`
   - `/usr/local/sbin/odoo_agent_intake_runner.sh`
   - `hs27-odoo-agent-intake.service`
   - `hs27-odoo-agent-intake.timer`
5. Root-only Odoo-Credential-Pfad wiederherstellen:
   - `/root/.config/homeserver2027/odoo_agent_rpc.env`
6. Auf `VM 220` einen frischen `agent@`-API-Key nur dann erzeugen, wenn Schritt 5 bereits sicher vorbereitet ist.
7. Zuerst `dry-run`, danach erst ein kontrollierter einzelner `--apply`.

## Verifikation

- `systemctl list-timers` zeigt beide Timer wieder `enabled` und `active`.
- `getent hosts imap.strato.de` ist auf `VM 200` wieder gruen.
- Alias-Mail an `agent@frawo-tech.de` landet sichtbar in `Aliases.Agent`.
- `odoo_agent_intake_bridge.py --dry-run` erkennt genau die erwartete Mail.
- Ein einzelner `--apply` erzeugt genau einen Odoo-Task und verschiebt die Mail nach `Aliases.Agent.Processed`.
