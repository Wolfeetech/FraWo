# Odoo Wartungsauftrag Server

Stand: `2026-03-26`

## Status

Dieses Dokument ist nur noch historischer Auftrags- und Planungskontext.

Fuer operative Arbeit gilt der kanonische Betriebsstand in:

- `OPERATIONS/MAIL_OPERATIONS.md`
- `OPERATIONS/USER_ONBOARDING_OPERATIONS.md`
- `STRESS_TEST_READINESS.md`
- `PLATFORM_STATUS.md`

## Urspruenglicher Auftrag

Der Wartungsauftrag diente dazu, den Homeserver auf einen kontrollierten internen Stresstest vorzubereiten und dabei Mail-, Secret- und Benutzerbasis sauberzuziehen.

## Heute Noch Relevante Bloecke

1. Alias-/Postfachmodell in `STRATO` final verifizieren:
   - `wolf@frawo-tech.de` bleibt sichtbare Alias-Identitaet ueber `webmaster@...`
   - `franz@frawo-tech.de` ist das eigene echte Postfach von Franz
   - `info@frawo-tech.de` und `noreply@frawo-tech.de` sind technisch noch sauber zu klaeren
2. `Franz` in `FraWo` sichtbar verifizieren und seine Endgeraete pruefen.
3. das alte Klartext-Register nur noch extern vorhalten; im Workspace nur noch mit Vaultwarden-Referenzen arbeiten.
4. Sichtbare App-Mailtests fuer `Nextcloud`, `Paperless` und `Odoo` abschliessen; `AzuraCast` spaeter nach Pi-SSH-Reparatur.
5. Danach den internen Nutzerdurchlauf ohne Passwort-Nacharbeit dokumentieren.

## Odoo Im Aktuellen Zielbild

- `Odoo` ist Teil der internen Kernplattform.
- `Odoo` ist nicht der persoenliche Mailclient fuer Wolf oder Franz.
- `Odoo` nutzt Mail spaeter nur fuer Prozess-, Alias- und Systemkontext.

## Relevante Dateien

- `OPERATIONS/MAIL_OPERATIONS.md`
- `OPERATIONS/USER_ONBOARDING_OPERATIONS.md`
- `NEXTCLOUD_MAIL_AND_ODOO_MAIL_ARCHITECTURE.md`
- `MAIL_TO_PAPERLESS_NEXTCLOUD_ARCHITECTURE.md`
- `STRESS_TEST_READINESS.md`

## Kurztext Fuer Odoo Beschreibung

Historischer Wartungsauftrag zur Stabilisierung des `Homeserver 2027` vor internem Stresstest. Der operative Stand liegt inzwischen in den kanonischen Wiki-Dateien fuer Mail, Benutzer-Onboarding, Plattformstatus und Stresstest-Readiness.
