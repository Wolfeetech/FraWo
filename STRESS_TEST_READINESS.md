# Stress Test Readiness

Stand: `2026-03-30`

## Zweck

Dieses Dokument ist nur noch das kurze Uebergangs-Gate zwischen dem aktuellen
Arbeits-MVP und dem spaeteren Produktions-/Zertifizierungsblock.

Der operative Detailstand liegt in:

- `OPERATOR_TODO_QUEUE.md`
- `OPERATIONS/USER_ONBOARDING_OPERATIONS.md`
- `OPERATIONS/MAIL_OPERATIONS.md`
- `OPERATIONS/PRODUCTION_READINESS_OPERATIONS.md`

## Letzter verifizierter Lauf

- letzter voller Stresslauf: `artifacts/stress_tests/20260327_181859`
- letzter Produktionsentscheid: `artifacts/production_gate/20260327_182022/production_gate.md`
- letzter Business-MVP-Auditlauf: `artifacts/release_mvp_audit/20260328_004657`
- letzter Business-MVP-Entscheid: `artifacts/release_mvp_gate/20260328_004741/release_mvp_gate.md`
- letzter Website-Auditlauf: `artifacts/website_release_audit/20260330_063108`
- letzter Website-Release-Entscheid: `artifacts/website_release_gate/20260330_063116/website_release_gate.md`

## Aktueller Befund

- Die Kernbasis fuer den Arbeits-MVP ist tragfaehig:
  - `Vaultwarden` ist live
  - `Franz` hat die `FraWo`-Einladung angenommen
  - das Root-Portal und der Franz-Pfad sind auf den Arbeits-MVP reduziert
  - `Nextcloud`, `Paperless` und `Odoo` sind im SMTP-Baseline-Check gruen
- der neue technische MVP-Gate-Stand ist jetzt sauber:
  - alle kritischen Codex-Pruefungen im `release-mvp-audit` sind gruen
  - `release-mvp-gate` blockiert nur noch an manueller Evidenz
- der Website-Track ist jetzt ebenfalls getrennt pruefbar:
  - `public-dns-check` gruen
  - `public-http-redirect-check` rot
  - `public-https-check` rot
  - `public-mail-dns-check` rot
  - `website-release-gate` bleibt damit aktuell korrekt `BLOCKED`
- Der Arbeits-MVP ist aber noch nicht sichtbar abgenommen:
  - Wolf- und Franz-Durchlauf fehlen
  - sichtbare Vaultwarden-Stichprobe fehlt
  - sichtbare App-Testmails fehlen
  - `STRATO`-Send/Receive fuer die finalen Mailpfade ist noch nicht komplett abgenommen

## Nicht nur SSO

`SSO` oder ein spaeterer zentraler Auth-Proxy ist wichtig, aber nicht die
einzige echte Baustelle.

Die realen aktuellen Schwachpunkte sind:

1. sichtbare MVP-Abnahme fuer Wolf, Franz, Vault, `Nextcloud`, `Paperless`, `Odoo`
2. saubere Mail-Abnahme fuer `webmaster`, `franz`, `noreply`
3. Klartext-Artefakte bleiben ausserhalb des Workspaces; im Repo gilt nur noch das Referenzregister
4. Doku-Drift zwischen Kanon, Uebergangsdokumenten und alten Artefakten

## Spaeterer Zertifizierungsblock

Diese Punkte blockieren nicht den heutigen Arbeits-MVP, aber weiter das spaetere
professionelle Produktionssiegel:

- `PBS`
- `surface-go-frontend`
- `AzuraCast`-SMTP / `raspberry_pi_radio`-SSH
- sichtbare Shared-Frontend- und Shared-Device-Abnahme

## Naechste sinnvolle Reihenfolge

1. sichtbare MVP-Abnahme fuer Wolf und Franz
2. sichtbare Mailtests fuer `Nextcloud`, `Paperless`, `Odoo`
3. den Workspace auf `ACCESS_REGISTER_VAULTWARDEN_REFERENCES.md` als einzige Repo-Referenz festziehen
4. erst danach Erweiterungsblock wieder oeffnen
5. den Zertifizierungsblock mit `PBS` und Shared Frontend getrennt ziehen
