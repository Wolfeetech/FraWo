# Internal Communication Standard

Stand: `2026-03-26`

## Zweck

Diese Datei ist der kanonische Betriebsstandard fuer interne Kommunikation und Mail im aktuellen Homeserver-Stand.

## Kurzentscheidung

- In dieser Phase gibt es **keinen eigenen Mailserver** auf dem Homeserver.
- `STRATO` bleibt Mail-Provider fuer Empfang und Versand.
- `Vaultwarden` ist die Secret-Ablage fuer Mail- und App-Zugaenge.
- `Nextcloud` bleibt die zentrale interne Arbeitsoberflaeche.
- `Nextcloud Mail` ist der spaetere zentrale Mailzugang fuer Benutzer.
- `Paperless` bekommt spaeter nur eine dedizierte Dokumenten-Mailbox.
- `Odoo` nutzt Mail nur fuer Prozess- und Systemkontext, nicht als persoenlichen Mailclient.

## Kommunikationsmodell

### Persoenliche Kommunikation

- `wolf@frawo-tech.de`
  - sichtbare Arbeitsidentitaet, technisch aktuell ueber `webmaster@...`
- `franz@frawo-tech.de`
  - eigenes echtes Postfach
- Provider: `STRATO`
- Zugang: zuerst `STRATO`-Web-/Mailclient-Test, spaeter bevorzugt `Nextcloud Mail`

### Funktionskommunikation

- `info@frawo-tech.de`
  - Kontakt und allgemeiner Eingang
- `noreply@frawo-tech.de`
  - System- und App-Absender
- spaeter `documents@frawo-tech.de`
  - dedizierter Paperless-Eingang

### Interne Arbeitskommunikation

- operative Zusammenarbeit laeuft zuerst ueber:
  - `Nextcloud`
  - `Paperless`
  - `Odoo`
  - Mail ueber `STRATO`
- Ein eigener Chat-/Groupware-Block ist aktuell **nicht** Release-kritisch und wird in dieser Phase nicht neu eingefuehrt.

## Kein eigener Mailserver Jetzt

Nicht in dieser Phase:

- kein Postfix-/Dovecot-Rollout auf dem Homeserver
- kein MX-Betrieb auf eigener Infrastruktur
- kein kompletter Groupware- oder Chat-Stack nur fuer den ersten internen Deploy

Begruendung:

- `STRATO` loest das robuste Provider-Thema bereits
- der aktuelle Engpass ist Identitaet, Mailbox-Aufbau und App-SMTP, nicht MTA-Betrieb
- ein eigener Mailserver wuerde DNS-, Reputation-, Spam-, TLS-, Abuse- und Betriebsaufwand in den kritischen Pfad ziehen

## Zielreihenfolge

1. Alias-/Postfachmodell in `STRATO` verifizieren und bereinigen
2. Mail-Zugaenge in `Vaultwarden / Mail & Domains` verifizieren
3. `Nextcloud Mail` als zentrale Benutzeroberflaeche vorbereiten
4. `noreply@frawo-tech.de` als SMTP-Absender fuer Apps standardisieren
5. spaeter `documents@frawo-tech.de` fuer `Paperless` anbinden
6. erst danach ueber weitere Kommunikationsbausteine entscheiden

## Rollen Pro System

| System | Rolle im Kommunikationsmodell |
| --- | --- |
| `STRATO` | Provider fuer Empfang und Versand |
| `Vaultwarden` | Secret-Ablage fuer Mail- und App-Credentials |
| `Nextcloud` | zentrale Benutzer- und spaetere Mail-Oberflaeche |
| `Paperless` | Dokumenteneingang per dedizierter IMAP-Mailbox, spaeter |
| `Odoo` | Prozess-, Alias- und Systemmail, nicht persoenliche Inbox |
| `AzuraCast` | System- und Adminhinweise ueber SMTP |

## Direkte Naechste Schritte

### Mailbasis

- `wolf@frawo-tech.de` als Alias-/Loginpfad ueber `webmaster@...` pruefen
- `franz@frawo-tech.de` als eigenes echtes Postfach sichtbar pruefen
- `info@frawo-tech.de` als Rollenpfad im `STRATO`-Paket pruefen
- `noreply@frawo-tech.de` als Rollenpfad im `STRATO`-Paket pruefen
- SPF, DKIM und DMARC dokumentieren

### Interne Kommunikation

- `Nextcloud` als zentrale Oberflaeche fuer Wolf und Franz festziehen
- spaeter `Nextcloud Mail` fuer die persoenlichen Mailboxen anbinden
- kein neuer Chat-Stack in den ersten internen Deploy ziehen

### App-Mail

- `Nextcloud` -> `noreply@frawo-tech.de`
- `Paperless` -> `noreply@frawo-tech.de`
- `Odoo` -> `noreply@frawo-tech.de`
- `AzuraCast` -> `noreply@frawo-tech.de`

## Definition Of Done

- `wolf@frawo-tech.de` ist als Alias-/Loginpfad ueber `webmaster@...` dokumentiert und getestet
- `franz@frawo-tech.de` ist als echtes Postfach nutzbar
- `info` und `noreply` sind sauber definiert und gespeichert
- Mail-Zugaenge liegen in `Vaultwarden`
- App-SMTP-Zielbild ist dokumentiert und bereit fuer Umsetzung
- es gibt keinen offenen Irrtum mehr, dass jetzt ein eigener Mailserver gebaut werden soll
