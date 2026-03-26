# Start Here Fuer Wolf Und Franz

## Zweck

Diese Datei ist der einfache Einstieg fuer den aktuellen internen Betriebsstand.
Sie ist bewusst kurz und verweist nur auf die naechsten echten Arbeitsdateien.

Stand dieser Uebersicht: `2026-03-26`

## Live-Zwischenstand Jetzt

- `portal.hs27.internal`: `200`
- `cloud.hs27.internal`: `200`
- `paperless.hs27.internal`: `200`
- `odoo.hs27.internal`: `200`
- `ha.hs27.internal`: `200`
- `media.hs27.internal`: `200`
- `radio.hs27.internal/login`: `200`

Das heisst:

- die internen Hauptdienste antworten gerade sauber
- der interne Betrieb ist aktuell live
- der oeffentliche Release ist weiter bewusst noch nicht offen

## So startest du jetzt

1. Portal oeffnen: `http://portal.hs27.internal`
2. Aktuelle Zugangslage lesen: `ACCESS_REGISTER.md`
3. Tagessteuerung lesen: `EXECUTIVE_ROADMAP.md`
4. Wenn etwas unklar ist: `OPS_HOME.md`

## Wer nutzt was

### Wolf

- `Nextcloud`
- `Paperless`
- `Odoo`
- `Home Assistant`
- `Jellyfin`
- `AzuraCast`

### Franz

- `Nextcloud`
- `Paperless`
- `Odoo`
- `Jellyfin`
- `Radio`

### Gemeinsam

- `Portal`
- `Jellyfin`
- `Radio`

## Was jetzt als Naechstes zu tun ist

1. `Bitwarden Cloud` produktiv einrichten
2. aktuelle produktive Logins aus `ACCESS_REGISTER.md` nach Bitwarden uebernehmen
3. `STRATO`-Mailboxen anlegen:
   - `wolf@frawo-tech.de`
   - `franz@frawo-tech.de`
   - `info@frawo-tech.de`
   - `noreply@frawo-tech.de`
4. erst danach den Website-Release fuer `www.frawo-tech.de` freigeben

## Wichtige Grenze

Das neue Portal-Element `Vorstellungsrunde / Anmeldeboard` ist im Repo vorbereitet, aber noch nicht als live ausgerollt bestaetigt.
Der aktuelle Live-Status oben bezieht sich auf die Dienste selbst, nicht auf diese neue Portal-Oberflaechenversion.

## Wenn du direkt weiterlesen willst

- Handout: `WOLF_FRANZ_HANDOUT.md`
- Operator-Startseite: `OPS_HOME.md`
- Gesamtstatus: `PLATFORM_STATUS.md`
