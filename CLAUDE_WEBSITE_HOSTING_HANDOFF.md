# Claude Website + Hosting Handoff

Dieser Handoff ist dafuer gedacht, direkt an Claude weitergegeben zu werden.
Kein Secret-Text. Keine Passwoerter. Fokus nur auf `FraWo` Website-Design und Hosting.

## Auftrag

Bearbeite die `FraWo`-Website so, dass sie sprachlich, visuell und technisch auf einem deutlich professionelleren Niveau liegt.

Zielbild:
- kleine Firma, aber Auftritt auf dem Niveau serioeser groesserer Anbieter
- visuell eher in der Anspruchsrichtung von `sunshine live` und `NTS`
- nicht kopieren, aber in Sachen Klarheit, Rhythmus, Professionalitaet und redaktioneller Strenge mithalten

## Harte Regeln

- CI-Schrift ist `Poppins`
- verschiedene Schriftschnitte/Gewichte sind erlaubt und gewuenscht
- kein `Handwerk`
- keine HWK-nahe Sprache
- kein KI-Slang
- kein Agentursprech
- kein LinkedIn-/Branding-Workshop-Ton
- keine erfundene Groesse
- keine Buzzwords wie `innovativ`, `ganzheitlich`, `massgeschneidert`, `Leidenschaft`, `Vision`, `Premium`
- Sprache muss nach echtem Betreiber / technischem Eventdienstleister klingen

## FraWo in einem Satz

`FraWo` ist ein kleiner, aber ernstzunehmender Eventdienstleister fuer technische Setups, Ablauf, Zuspielung, Betreuung vor Ort und digitale Besucher-/Event-Information, sowie Sonderbauten   im Bereich Event- und Medientechnik. 


## Aktueller Live-Stack

- Website-Engine: `Odoo 17`
- Odoo intern: `http://odoo.hs27.internal`
- Odoo mobil/frontdoor: `http://100.99.206.128:8444`
- Odoo VM: `10.1.0.22`
- Reverse proxy / frontdoor: `toolbox` via Caddy
- Odoo-Website wird aktuell direkt in Odoo-Views gepflegt

## Aktuelle Website-Fakten

- Homepage und Kontaktseite sind aktuell in Odoo angepasst
- die Sprache wurde bereits mehrfach korrigiert, ist aber noch nicht auf Endniveau
- reale Odoo-Bildassets sind vorhanden und sollen weiter benutzt werden
- live sichtbare Bilder:
  - `/web/image/1803`
  - `/web/image/1798`
  - `/web/image/1801`
  - `/web/image/1797`
  - `/web/image/1805`
  - `/web/image/1806`

## Design-Richtung

Bitte die Seite nicht wie eine generische kleine Firmen-Landingpage behandeln.

Gesuchte Qualitaeten:
- starke Hero-Dramaturgie
- klare Typohierarchie
- reduzierte, belastbare Texte
- starke Bildflaechen
- modulare Inhaltsbloecke
- ruhige, technische Souveraenitaet
- professioneller Eindruck auch auf Mobile

Nicht gewollt:
- weichgespuelte Standard-Startseite
- stockige 08/15-Dreikarten-Website ohne Haltung
- textlastige Prompt-Sprache
- Behauptungen ohne Substanz

## Inhaltliche Positionierung

FraWo soll als folgendes lesbar werden:
- Eventtechnik
- Ton, Licht, Zuspielung
- technische Betreuung vor Ort
- Ablauf und Umbauten
- Event-Webseite / Besucherinformation / digitale Informationspfade

Nicht lesbar sein soll:
- Marketingagentur
- IT-Beratung ohne Realweltbezug
- Handwerksbetrieb
- Radio-/Medienprojekt ohne Eventfokus

## Was bereits gut ist

- `Poppins` ist gesetzt und soll CI-Standard bleiben
- echte Bilder sind vorhanden
- Odoo-Runtime ist aktuell gruen
- Kontaktpfade sind echt:
  - `info@frawo-tech.de`
  - `+49 151 55243164`

## Was noch offen ist

### Design

- Homepage braucht noch einen echten End-Finish
- Kontaktseite soll denselben Standard halten wie die Homepage
- Copy muss komplett nach echter Firma statt nach generiertem Prompt klingen
- Header, Footer, Hero, Bildzuschnitte, Rhythmus und Mobile spacing muessen auf ein Endniveau gezogen werden
- SEO-/OpenGraph-/Meta-Basis sollte mitgeprueft werden

### Hosting / Public Edge

- interner Business-Core ist gruen
- Public-Website-Pfad ist historisch noch als eigener Restblock beschrieben
- aktueller Caddy-Stand im Repo zeigt nur Teilmappings und ist nicht automatisch finaler Live-Release-Beweis
- Claude soll Hosting nicht blind umbauen, sondern zuerst sauber analysieren und dann einen konkreten, risikoarmen Plan formulieren

## Wichtige technische Grenzen

- keine Secrets in Dateien schreiben
- keine direkten SQL-Schreibfixes an Odoo-Datenbank ohne frischen Rueckweg
- keine destruktiven Hosting-Aenderungen ohne klaren Rollback
- Odoo-Filestore nicht mit Nextcloud/Paperless live zusammenwerfen
- Website-Design und Hosting sauber trennen:
  - Odoo = Inhalt/Views
  - Caddy/Public Edge = Auslieferung / Domains / Frontdoor

## Relevante Dateien im Repo

- `OPERATIONS/ODOO_OPERATIONS.md`
- `LIVE_CONTEXT.md`
- `MEMORY.md`
- `AI_SERVER_HANDOFF.md`
- `current_caddy.txt`
- `current_caddy_utf8.txt`

### Website-Backups / Rueckwege

- `Codex/website_backups/frawo_public_website_prepolish_20260408.sql`
- `Codex/website_backups/frawo_public_website_polish_20260408.sql`
- `Codex/website_backups/frawo_event_site_pre_rebuild_20260409.sql`
- `Codex/website_backups/frawo_site_before_layout_restore_20260409.sql`
- `Codex/website_backups/frawo_site_after_layout_restore_20260409.sql`
- `Codex/website_backups/frawo_site_before_content_fix_20260409.sql`
- `Codex/website_backups/frawo_site_before_pro_standard_redesign_20260409.sql`

## Aktueller Caddy-Hinweis

Die im Repo sichtbaren Caddy-Dateien zeigen u. a.:
- `funk.frawo-tech.de`
- `media.frawo-tech.de`
- `agent.frawo-tech.de`
- interne `.hs27.internal`-Hosts

Claude soll daraus nicht blind schliessen, dass der Public-Edge sauber final ist.
Erst Ist-Zustand sauber lesen, dann eine konkrete Hosting-Empfehlung geben.

## Was Claude liefern soll

### 1. Website-Design-Review

Kurz und hart:
- was wirkt professionell
- was wirkt billig / generisch / KI-haft
- was muss zuerst weg

### 2. Neuer Textsatz

Bitte komplett neu, nicht nur polieren:
- Hero
- Leistungsbloecke
- Arbeitsweise
- Warum FraWo
- CTA
- Kontaktseite

### 3. Design-System-Vorschlag

Konkrete Empfehlung fuer:
- Hero-Aufbau
- Grid
- Typohierarchie
- Bildnutzung
- Footer
- Mobile-Verhalten

### 4. Hosting-Analyse

Nur fuer Website/Public Edge:
- Odoo-Auslieferung
- Caddy-/Frontdoor-Lage
- Domain-/TLS-/Redirect-Fragen
- was heute live ist
- was fuer einen sauberen echten Release noch fehlt

### 5. Sichere Umsetzungsreihenfolge

Bitte in folgender Form:
1. inhalts-/designseitige Low-Risk-Aenderungen
2. visuelle Endabnahme
3. Hosting-/Edge-Pruefung
4. erst dann Public Release

## Sprachliche Erwartung an Claude

Jeder Satz muss durch diesen Test:

`Wuerde ein echter technischer Eventdienstleister das genau so sagen?`

Wenn nicht: neu schreiben.

## Direkter Startprompt fuer Claude

```text
Du arbeitest an der Website von `FraWo GbR`.

Kontext:
FraWo ist ein kleiner, aber ernstzunehmender Eventdienstleister fuer technische Setups, Ton, Licht, Zuspielung, Ablauf, Betreuung vor Ort und digitale Besucherinformation.

Dein Auftrag:
1. Pruefe die bestehende Website sprachlich, visuell und strukturell.
2. Ersetze jede KI-/Agentur-/LinkedIn-Sprache durch klare, echte Betreiber-Sprache.
3. Hebe die Website gestalterisch auf einen professionelleren Standard mit Anspruch in der Referenzrichtung von `sunshine live` und `NTS`.
4. Beruecksichtige auch den Hosting-/Public-Edge-Teil der Website, aber nimm dort keine blinden Annahmen vor.

Harte Regeln:
- CI-Schrift ist `Poppins`
- verschiedene Schriftschnitte/Gewichte nutzen
- kein `Handwerk`
- keine HWK-nahe Sprache
- kein Agentursprech
- kein KI-Slang
- keine erfundene Groesse
- keine Buzzwords

Arbeite auf Basis dieses Handoffs und liefere:
- ein kurzes, ehrliches Review
- komplette neue Website-Texte
- konkrete Design-Richtung
- Hosting-/Public-Edge-Einschaetzung
- empfohlene Umsetzungsreihenfolge
```
