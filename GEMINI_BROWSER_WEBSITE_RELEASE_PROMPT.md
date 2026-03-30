# Gemini Browser Website Release Prompt

Bitte pruefe den oeffentlichen Website-Release jetzt sichtbar im Browser. Keine Server-, DNS- oder Mail-Konfiguration aendern.

## Zuerst lesen

1. `INTRODUCTION_PROMPT.md`
2. `WEBSITE_RELEASE_PROMPT.md`
3. `RELEASE_READINESS_2026-04-01.md`
4. `artifacts/website_release_gate/20260330_154459/website_release_gate.md`

## Scope

Nur diese sichtbare Browser-Abnahme:

- `http://frawo-tech.de`
- `http://www.frawo-tech.de`
- `https://frawo-tech.de`
- `https://www.frawo-tech.de`

Keine Infrastruktur-Aenderungen. Keine Admin-Logins. Keine internen `hs27.internal`-Dienste in den Scope ziehen.

## Arbeitsweise

1. `http://frawo-tech.de` oeffnen
2. sichtbares Verhalten notieren:
   - final sichtbare URL
   - ob Redirect passiert
   - Seitentitel oder sichtbarer Fehler
3. `http://www.frawo-tech.de` oeffnen und genauso pruefen
4. `https://frawo-tech.de` oeffnen und genauso pruefen
5. `https://www.frawo-tech.de` oeffnen und genauso pruefen
6. Wenn TLS-/Browserfehler sichtbar sind:
   - die sichtbare Fehlermeldung exakt notieren
   - keine Vermutungen erfinden
7. Wenn `frawo-tech.de` nicht auf `www.frawo-tech.de` umleitet, klar als Fehler markieren
8. Wenn `www.frawo-tech.de` sichtbar laedt:
   - pruefen, ob eine sichtbare Radio-Praesenz, ein Radio-Block oder ein Player-Pfad vorhanden ist
   - genau notieren, was sichtbar ist oder fehlt

## Erwarteter Zielstand

- `frawo-tech.de` leitet auf `https://www.frawo-tech.de` um
- `www.frawo-tech.de` liefert die oeffentliche GbR-Website ueber die Odoo-Website
- auf der Website ist eine sichtbare Radio-Praesenz oder ein Player-Pfad integriert
- HTTPS ist ohne sichtbaren Browserfehler nutzbar

## Antwortformat

Website Release Browser Result

apex_http: passed|failed
apex_http_url: ...
apex_http_observation: ...

www_http: passed|failed
www_http_url: ...
www_http_observation: ...

apex_https: passed|failed
apex_https_url: ...
apex_https_observation: ...

www_https: passed|failed
www_https_url: ...
www_https_observation: ...

public_browser_acceptance_verified: passed|failed
evidence: ...

public_radio_integration_verified: passed|failed
radio_observation: ...

blockers:
- ...
