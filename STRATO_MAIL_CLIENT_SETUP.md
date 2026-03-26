# STRATO Mail Client Setup

Stand: `2026-03-26`

## Status

- `imap.strato.de:993` erreichbar
- `smtp.strato.de:465` erreichbar
- Auf dem StudioPC ist `Outlook` vorhanden

## Wichtige Regel

- Login immer mit dem **echten Postfach**
- nicht mit Aliasen wie:
  - `wolf@frawo-tech.de`
  - `info@frawo-tech.de`
  - `noreply@frawo-tech.de`

Fuer den aktuellen Owner-Pfad ist das echte Postfach:

- `webmaster@...`

## Aktueller Mail-Standard

- echtes technisches Postfach:
  - `webmaster@...`
- Aliasse auf dieses Postfach:
  - `wolf@frawo-tech.de`
  - `info@frawo-tech.de`
  - `noreply@frawo-tech.de`
- zweites echtes Postfach als Ziel:
  - `franz@frawo-tech.de`

## Manuelle IMAP-Daten

- Kontotyp: `IMAP`
- Eingangsserver: `imap.strato.de`
- Port eingehend: `993`
- Verschluesselung eingehend: `SSL/TLS`
- Ausgangsserver: `smtp.strato.de`
- Port ausgehend: `465`
- Verschluesselung ausgehend: `SSL/TLS`
- Benutzername eingehend: echtes Postfach
- Benutzername ausgehend: echtes Postfach

## Outlook Reihenfolge

1. `Outlook` oeffnen
2. `Konto hinzufuegen`
3. echte Postfachadresse eingeben
4. falls Auto-Setup scheitert:
   - `IMAP` manuell waehlen
   - Serverdaten aus dieser Datei eintragen
5. nach erfolgreichem Login testen:
   - Empfang an `wolf@frawo-tech.de`
   - Empfang an `info@frawo-tech.de`
   - spaeter Versand mit sichtbarer Absenderadresse pruefen

## Definition Of Done

- Login mit dem echten `webmaster`-Postfach klappt
- Mail an `wolf@frawo-tech.de` kommt an
- Mail an `info@frawo-tech.de` kommt an
- SMTP-Versand ueber `smtp.strato.de` funktioniert
