# STRATO Mail Account Rollout Checklist

Stand: `2026-03-26`

## Ziel

Diese Liste loest das aktuelle Henne-Ei-Problem sauber:

- Vaultwarden ist bereits intern live
- produktiv blockiert ist Vaultwarden aktuell noch durch fehlendes `HTTPS`
- jetzt kommen deshalb zuerst die echten FRAWO-Mailboxen bei STRATO
- danach wird Vaultwarden mit internem `HTTPS` sauber vorgeschaltet
- erst dann werden die finalen Identitaeten und Passwoerter zentral uebernommen

## Aktueller Zwischenstand

- [x] `wolf@frawo-tech.de` als Alias auf `wolf@yourparty.tech` angelegt
- [x] `info@frawo-tech.de` als Alias auf `wolf@yourparty.tech` angelegt
- [x] `noreply@frawo-tech.de` als Alias auf `wolf@yourparty.tech` angelegt
- [ ] `franz@frawo-tech.de` braucht ein eigenes Login und damit ein eigenes echtes Postfach
- [ ] Aktuell ist kein freies zusaetzliches Postfach verfuegbar

## Direkte Links

- STRATO Kunden-Login:
  - `https://www.strato.de/faq/vertrag/der-strato-kunden-login/`
- STRATO Mailboxen anlegen:
  - `https://www.strato.de/faq/mail/e-mail-adressen-einrichten-und-bearbeiten/`
- STRATO Webmail:
  - `https://webmail.strato.de/`
- STRATO Webmail Login-Hilfe:
  - `https://www.strato.de/faq/article/2265/Wie-logge-ich-mich-in-den-STRATO-Webmail-ein.html`

## Wichtige Einschraenkung

- Bei einem `STRATO Domain-Paket` ist `STRATO Webmail` laut STRATO-FAQ nicht nutzbar.
- In diesem Fall sind die richtigen Zugriffspfade:
  - `IMAP`: `imap.strato.de`
  - `POP3`: `pop3.strato.de`
  - `SMTP`: `smtp.strato.de`
- Der Login in Mailclients erfolgt immer mit dem **echten Postfach**, nicht mit dem Alias.

## Abarbeitung

### 1. Voruebergehende sichere Ablage vorbereiten

- [ ] Eine temporaere Offline-Ablage festlegen:
  - Papierliste
  - oder lokale, nicht geteilte Notiz
- [ ] Dort nur fuer den Uebergang festhalten:
  - STRATO Kundennummer
  - STRATO Kundenpasswort
  - neue Mail-Passwoerter
- [ ] Nach produktivem Vaultwarden-Setup diese Zwischenablage wieder bereinigen

### 2. In STRATO einloggen

- [ ] STRATO Kunden-Login aufrufen
- [ ] Mit Kundennummer und Kundenpasswort einloggen
- [ ] Das Paket mit `frawo-tech.de` oeffnen
- [ ] Bereich `E-Mail` -> `Verwaltung` aufrufen

### 3. Diese Mailboxen anlegen

- [ ] `wolf@frawo-tech.de`
- [ ] `franz@frawo-tech.de`
- [ ] `info@frawo-tech.de`
- [ ] `noreply@frawo-tech.de`

Empfohlene Reihenfolge:

1. `wolf@frawo-tech.de`
2. `franz@frawo-tech.de`
3. `info@frawo-tech.de`
4. `noreply@frawo-tech.de`

## Entscheidung Fuer Franz

`franz@frawo-tech.de` darf **kein** Alias auf `wolf@yourparty.tech` sein, wenn Franz ein eigenes Login bekommen soll.

Professionell gibt es jetzt nur zwei saubere Wege:

1. `webmaster@...` ist ungenutzt:
   - altes `webmaster`-Postfach in `franz@frawo-tech.de` umstellen oder ersetzen
2. `webmaster@...` wird noch gebraucht:
   - Tarif erweitern / zusaetzliches Postfach buchen

Nicht sauber:

- `franz@frawo-tech.de` nur als Alias auf Wolf
- `franz@frawo-tech.de` als Alias auf `webmaster`, wenn Franz dann technisch mit `webmaster` arbeitet

### 4. Fuer jede Mailbox sofort tun

- [ ] Passwort setzen
- [ ] Passwort **sofort** in Vaultwarden speichern
- [ ] Optional Alias/Funktion notieren
- [ ] Kurz in Webmail testen:
  - `https://webmail.strato.de/`

### 5. Zielbelegung

- [ ] `wolf@frawo-tech.de`
  - persoenlicher Hauptaccount von Wolf
- [ ] `franz@frawo-tech.de`
  - persoenlicher Hauptaccount von Franz
- [ ] `info@frawo-tech.de`
  - Kontakt / Aussenkommunikation
- [ ] `noreply@frawo-tech.de`
  - Systemmails fuer Nextcloud, Paperless, Odoo, AzuraCast

### 6. Nach produktivem Vaultwarden-Setup uebernehmen

- [ ] `Mail & Domains / STRATO Kunden-Login`
- [ ] `Mail & Domains / wolf@frawo-tech.de`
- [ ] `Mail & Domains / franz@frawo-tech.de`
- [ ] `Mail & Domains / info@frawo-tech.de`
- [ ] `Mail & Domains / noreply@frawo-tech.de`

### 7. Danach im Projekt nachziehen

- [ ] Interne `HTTPS`-Frontdoor fuer Vaultwarden bauen
- [ ] Ersten produktiven Vaultwarden-Benutzer anlegen
- [ ] Vaultwarden-Hauptnutzer bei Bedarf von Uebergangs-Mail auf `wolf@frawo-tech.de` umstellen
- [ ] `ACCESS_REGISTER.md` spaeter von Klartext auf Vaultwarden-Referenzen umbauen
- [ ] SMTP-Standardisierung vorbereiten:
  - Nextcloud -> `noreply@frawo-tech.de`
  - Paperless -> `noreply@frawo-tech.de`
  - Odoo -> `noreply@frawo-tech.de`
  - AzuraCast -> `noreply@frawo-tech.de`

## Nicht tun

- Kein Master-Passwort in Markdown schreiben
- Keine neuen Mail-Passwoerter nur lokal im Browser lassen
- `info@frawo-tech.de` nicht als persoenlichen Admin-Login missbrauchen

## Abschlusskriterium

- alle 4 Mailboxen existieren
- alle 4 Mailboxen sind in Vaultwarden gespeichert
- mindestens `wolf@frawo-tech.de` und `franz@frawo-tech.de` koennen sich in Webmail anmelden
- danach ist das Henne-Ei-Problem fuer Identitaet und Secrets praktisch geloest
