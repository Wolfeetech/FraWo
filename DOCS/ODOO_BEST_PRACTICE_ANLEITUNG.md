# FraWo Odoo 19 Best-Practice Anleitung & Prozess-Leitfaden

**Stand:** September 2026 | **Gilt für:** Wolf Prinz & Franz Bienert (FraWo GbR)  
**System:** Odoo 19 Community auf CT140 (`10.1.0.112:8069`, DB `FraWo_GbR`)

---

## 1. Warum Odoo sich oft wie ein „riesiges Notizboard“ anfühlte — und wie es richtig funktioniert

In vielen Standard-Installationen ist Odoo anfangs leer und unkonfiguriert. Ohne eingerichtete Vorlagen, Automatismen und Teams muss man jede Zeile, jeden Preis und jedes Zahlungsziel mühsam per Hand eintippen.

**Der Unterschied zwischen Bastellösung und Open-Source Best Practice:**
- **Falsch (Bastel-Falle):** Man baut externe Python-Skripte oder Bots, die im Hintergrund pollen und Daten dubios hin- und herkopieren (Historie: *odoo-agent-poll-Desaster*).
- **Richtig (Odoo Best Practice):** Man nutzt die nativen Odoo-Standards (fertige Angebotsvorlagen, integrierte Fälligkeits-Aktivitäten, Stufen-Checklisten/Requirements, automatische Statusübergänge und saubere deutsche E-Mail-Templates).

---

## 2. Der geführte 4-Schritte-Workflow („SAP-Style“)

So läuft ein Geschäftsvorfall bei FraWo ab — **ohne Tipparbeit, in unter 60 Sekunden**:

### Schritt 1: Interessent kommt rein (CRM-Lead)
- **Wo:** Menü **CRM** ➔ Pipeline
- **Was tun:** Auf `+ Neu` in der Spalte **🔵 Neuer Lead** klicken oder einen bestehenden Lead öffnen.
- **Eingabe:** Nur 2 Felder nötig:
  1. *Bezeichnung* (z. B. `Weingut Gierer: Hoffest 2027`)
  2. *Kunde / Partner* auswählen (z. B. `Weingut Gierer`)
- **Was Odoo jetzt weiß:** Team (`🎧 Veranstaltungstechnik`), Verkäufer (`Wolf Prinz`) und Kontaktdaten sind automatisch verknüpft.
- **Weitergehen:** Klick oben links auf den Smart-Button **Neues Angebot**.

---

### Schritt 2: Das 15-Sekunden-Angebot (Angebotsvorlagen)
Sobald du auf **Neues Angebot** klickst, öffnet sich das Angebotsformular. Kunde und Verkäufer sind bereits eingetragen.

- **Was tun:** Im Feld **Angebotsvorlage** das passende FraWo-Paket auswählen:
  - `🎪 Event-Paket: Ton, Licht & Betreuung (Hoffeste, Feiern, Open-Air)`
  - `⚽ 5m Riesen-Fußballdart (Event-Attraktion & Verleih)`
  - `🔊 PA-/Event-Verleih (Privat & Feiern)`
  - `🔊 PA-/Event-Verleih (Full / Groß-Event bis 500 PAX)`
  - `Veranstaltungstechnik (1 Tag - Fachkraft gem. DGUV V17/18)`
  - `🔨 Zimmermann & Holzarbeiten (Tagessatz Franz Bienert)`
- **Was automatisch passiert:**
  - Alle Positionen (PA-Set, Licht, Mischpult, Fachkraft, Anfahrt) werden mit korrekten Preisen und Beschreibungstexten geladen.
  - Gültigkeit wird automatisch auf **30 Tage** datiert.
  - Zahlungsziel (30 Tage) und Kleinunternehmer-Klausel (§19 UStG) sind vorformuliert.
- **Feinschliff (optional):** Datum im Feld *Liefertermin / Eventdatum* eintragen, eventuell Kilometer bei Anfahrt anpassen.

---

### Schritt 3: Absenden & Automatische Nachfass-Garantie
- **Was tun:** Klick auf den grünen Button **Per E-Mail senden**.
- **Was automatisch passiert:**
  - Odoo öffnet das fertige deutsche FraWo-E-Mail-Template. Die PDF-Kalkulation ist bereits als Anhang angehängt.
  - Klick auf **Senden**.
- **Die neue FraWo-Automatik greift sofort im Hintergrund:**
  1. Der CRM-Lead rückt vollautomatisch von *Neuer Lead* auf **📄 Angebot erstellt** vor.
  2. Für Wolf wird automatisch eine Fälligkeits-Aktivität terminiert:
     - **Typ:** `📞 Angebot nachfassen`
     - **Fällig am:** Heute + 5 Tage
     - **Titel:** `📞 Angebot S000XX nachfassen (Kunde)`
     - **Ergebnis:** Kein Angebot geht mehr im Tagesgeschäft verloren. Wenn die 5 Tage um sind, erinnert Odoo (im Tagesbericht und im Aktivitätsmenü oben rechts).

---

### Schritt 4: Zusage & Automatische Übergabe an die Praxis
Der Kunde ruft an oder schreibt: *„Passt, machen wir so!“*

- **Was tun:** Angebot öffnen und auf den Button **Bestätigen** klicken.
- **Was vollautomatisch passiert (ohne weitere Klicks):**
  1. **CRM:** Der Lead springt auf **🤝 Gewonnen**.
  2. **Kalender:** Ein Kalendereintrag wird für das Eventdatum angelegt (inkl. Positionen und Kundenadresse).
  3. **Projekt & Aufgaben:** Ein Projekt wird erzeugt — Franz und Wolf sehen die Packliste und den Termin direkt auf ihrem Board.
  4. **Nachfass-Aktivität:** Wird automatisch als erledigt archiviert.

---

## 3. Verkaufsteams & Dashboard

Die drei getrennten FraWo-Sparten sind jetzt fest in Odoo verankert:

| Team | Leitung | Mitglieder | Fokus |
|---|---|---|---|
| **🎧 Veranstaltungstechnik & Event-Produktion** | Wolf Prinz | Wolf & Franz | Ton, Licht, Betreuung Hoffeste, Festivals, L.H. Subcontracting |
| **📦 Verleih & Mietpark (Dry Hire & Event-Module)** | Wolf Prinz | Wolf | Fußballdart, PA-Systeme, Licht-Sets, Beamer, Zubehör |
| **🔧 Werkstatt & Audio-Manufaktur (Lautsprecherbau & Service)** | Franz Bienert | Franz & Wolf | Lautsprecher-Eigenbau, Reparaturen, Holz/Montage |

**Vorteil im Alltag:**
- Wolf filtert im CRM mit einem Klick auf sein Team und sieht nur seine Baustellen.
- Franz öffnet Odoo und sieht im Werkstatt-Team sofort, welche Reparaturen oder Holzarbeiten anstehen.

### Gespeicherte CRM-Ansichten (Realität vs. Zukunft)

Damit Zukunftspläne nicht den Blick auf das Tagesgeschäft verstellen, gibt es zwei saubere Filter:
- **`🔥 Was jetzt ansteht (Herbst 2026)`** *(Standardansicht beim Öffnen)*: Zeigt ausschließlich akute Vorgänge (z. B. Lukis Herbst/Winter-Aufträge, Eishalle, Closing).
- **`🌱 Zukunftspläne (Saison 2027)`** *(Favoriten-Filter)*: Zeigt den kuratierten Pool für die kommende Saison (Winzer-Netzwerk, Fußballdart Stadtfest Wangen). Keine Hektik, keine erfundenen Angebote — sauber datiert auf Frühjahr 2027.

---

## 4. CRM-Stufen: Eingebaute Checklisten (Requirements)

Kein Rätselraten mehr, wann ein Vorgang wohin geschoben wird. Jede Spalte im CRM hat ab sofort eine klare Handlungsanweisung:

1. **🔵 Neuer Lead:** Bedarf erfasst, Ansprechpartner & Kontaktdaten geprüft, Team zugewiesen.
2. **📞 Qualifiziert:** Erstgespräch/Telefonat geführt, Eventdatum & Location geklärt, Budgetrahmen abgestimmt.
3. **📄 Angebot erstellt:** Angebotsvorlage gewählt, Mail versendet, Nachfass-Aktivität aktiv. *(Wird automatisch gesetzt!)*
4. **🤝 Gewonnen:** Auftrag erteilt, Bestätigt geklickt, Übergabe an Projekt/Kalender erfolgt. *(Wird automatisch gesetzt!)*
5. **❌ Nicht gewonnen:** Absagegrund ausgewählt (ausgeklappt nur bei Bedarf).

---

## 5. Audit & Grundeinrichtung: Alle Module im Best-Practice-Zustand

### A. Rechtssicherheit & Dokumenten-Layout (GbR / § 19 UStG)
- **Gesellschafter-Angabe:** Im PDF-Report-Footer und in allen Schreiben korrekt als `Gesellschafter: Wolfgang Prinz & Franz Bienert` tituliert (BGB-konform statt „Geschäftsführer“).
- **Kleinunternehmer-Klausel:** Auf `res.company` als sauberer Klartext ohne HTML-Tags hinterlegt:
  *„Gemäß § 19 UStG wird keine Umsatzsteuer berechnet (Kleinunternehmerstatus). Zahlbar innerhalb des vereinbarten Zahlungsziels ohne Abzug auf das angegebene Geschäftskonto.“*
- **Bankverbindung:** N26 Business (`DE 31 1001 ...`, BIC `NTSBDEB1XXX`) fest im Bericht-Footer verankert und im Journal `N26 — FraWo Space (Wolf)` (N26) gemappt.
- **Produkt-Steuern:** 100 % aller aktiven Verkaufs- und Verleihprodukte (inkl. Distanzstangen, Adapter, PA-Sets) sind auf Steuer ID 15 (`Steuerbefreit §19 UStG`) normiert.

### B. E-Mail-Vorlagen (Einheitliches deutsches FraWo-Design)
Alle Kern-Vorlagen nutzen dasselbe responsive, aufgeräumte Design mit FraWo-CI-Signatur:
1. **Angebot versenden (Template 13):** Unverbindliches Angebot mit PDF-Anhang und direktem Ansprechpartner.
2. **Auftragsbestätigung (Template 14):** Verbindliche Bestätigung disponierter Leistungen/Ausrüstung für den Kundentermin.
3. **Rechnung versenden (Template 7):** Transparente Abrechnung mit Fälligkeitsdatum, Rechnungsnummer und Bankverbindung.

### C. Rechnungsstellung & E-Invoicing (XRechnung / ZUGFeRD)
- **Status bei FraWo:** Odoo 19 Kernmodul `account_edi_ubl_cii` ist aktiv.
- **Behörden-Setup:** Für kommunale Auftraggeber (*Große Kreisstadt Wangen* #59, *Bauhof Wangen* #28) ist das Format `xrechnung` mit Leitweg-ID (Peppol EAS `0204`) und 30 Tage Zahlungsziel im Partnerstamm scharfgeschaltet.
- **Standard-Journale:** Übersichtlich auf Deutsch benannt (*Kundenrechnungen (INV)*, *Lieferantenrechnungen (BILL)*, *Barkasse (CSH1)*, *Sonstige Vorgänge (MISC)*).

### D. Werkstatt, Wartung & Gerätepark (`maintenance`)
- **Team:** `🔧 Werkstatt & Technik-Service` mit Franz Bienert und Wolf Prinz.
- **Gerätepark:** Alle 63 Equipment-Positionen sind konsistent auf `company_id = 1` (FraWo GbR) und Team 1 gebucht.
- **Stufen:** Praxistaugliche deutsche Wartungs-Pipeline:
  1. *📥 Neu eingegangen (Prüfung/Defekt)*
  2. *🔧 In Reparatur / Wartung*
  3. *✅ Repariert & Geprüft (Einsatzbereit)*
  4. *🛑 Ausgemustert / Ersatzteilspender*
  5. *📅 Regelmäßige DGUV-Wartung*

### E. Materialwirtschaft, Disposition & Stammdaten-Qualität (SAP-Level ERP)
- **Debitoren- & Kreditoren-Nummernkreise (`res.partner.ref`):**
  - **Debitoren (`D-10001` bis `D-10019`):** 26 Kundenstämme (L.H., Trommlerzug, Baas TV, Wangen, Winzer-Netzwerk) besitzen eine offizielle Debitorennummer für Rechnungsdruck, DATEV-Vorbereitung und Direkt-Suche im Odoo-Suchschlitz.
  - **Kreditoren (`K-70001` bis `K-70024`):** 24 Lieferanten (Thomann, Reichelt, Alternate, Amazon, Bauhaus, Galaxus, JLCPCB, Versorger) besitzen feste Kreditorennummern.
- **Bereinigung des Verkaufskatalogs (`sale_ok`):** 41 interne Werkstatt-Rohstoffe, Spulen, Kondensatoren, Leergehäuse und Dämmmaterialien wurden auf `sale_ok = False` gesetzt (`purchase_ok` und Stücklisten-Verwendung bleiben 100 % erhalten). Der Angebots-Katalog ist dadurch vollkommen frei von Bauteil-Müll und zeigt nur buchbare Pakete, Dienstleistungen und Verbrauchsmaterial.
- **Warengruppen & Kategorien-Hierarchie (`product.category`):** 100 % aller Warengruppen sind sauber unter dem Wurzelknoten `All` strukturiert. Verwaiste Artikel wurden exakt ihren Fachkategorien zugeordnet (0 unzugeordnete Produkte).
- **Material-Disposition & Mindestbestände (`stock.warehouse.orderpoint`):**
  - Werkstatt & Lautsprecherbau: Multiplex-Platten, D3-Leim, Spax-Schrauben, Strukturlack, Dämmstoff, Speakon-Buchsen.
  - Event-Verbrauchsmaterial (Neu angelegt): Advance AT200 Gaffa-Tape (schwarz), Procell AA Mignon (10er), Procell 9V-Blöcke, Neutrik NC3MXX / NC3FXX XLR-Stecker und -Buchsen mit automatischen Meldebeständen.
- **Instandhaltung & DGUV V3 (`maintenance.request`):** Die wiederkehrende Jahresprüfung aller ortsveränderlichen Betriebsmittel (#14, 1 Jahr Intervall, Fälligkeit 01.10.2026) ist zusammen mit den Lautsprecher-Prüfungen in der Stufe *📅 Regelmäßige DGUV-Wartung* fixiert.
- **Geschäftspartner-Qualität (Debitor/Kreditor - `res.partner`):**
  - ISO-Ländercodes korrigiert (Thomann, Alternate, Amazon, JLCPCB, Anthropic und Versorger stehen sauber auf `DE`, `CN`, `US`).
  - Zahlungskonditionen zu 100 % standardisiert (SaaS/Kreditkarte: *Sofort fällig*; Rechnungssteller/Kunden: *14 Tage netto* / *30 Tage netto*).
  - Test-Leichen archiviert (`FraWo Testkunde`).
- **Beleg-Hygiene (`sale.order`):** 7 Phantom-Angebote (0 € / 140 € ohne Produkt-Zuordnung) storniert; die Verkaufsübersicht zeigt exakt die 8 echten, aktiven Vorgänge.
- **Projekt- & Stufenintegrität (`project.task`):** Gemäß AGENTS.md-Prüfregel auditierte Aufgaben auf archivierten Projekten in aktive Standardprojekte überführt (Unsichtbare Tasks = 0).

### F. Reale Event-Anker 2026/2027 & Dienstleistungs-Erweiterungen
- **Laufende Real-Termine Herbst 2026:**
  - *12.09.2026 (Bregenz Beach Bar):* Leichte Liebe Open Air (Task #1057) für Luki / L.H. (360 € Tagessatz/Anfahrt, PSA mitbringen, reiner Helfer/Sub-Job).
  - *15.09.2026 (BPM Arena Lindau):* Wolfmix W1 Einlassshow-Presets (Task #1356) zur Vorbereitung der Heimspielpremiere der EV Lindau Islanders.
  - *26.09.2026:* Closing Summer 2026 (Task #1059).
  - *31.10.2026:* Halloweenparty (Task #1061).
- **Strategische Winzer-Termine Bodensee 2027 (CRM-Cockpit):**
  - *20.03.2027 (Sa):* **LAGO Weinfestival in der Inselhalle Lindau** (Wolfs Hauptarbeitsplatz / Heimspiel) – zentraler Hebel für den persönlichen Beziehungsaufbau zu Gierer, Haug, Maate, Lanz.
  - *02.–03.07.2027 (Fr/Sa):* **Komm & See 2027** – Weinfestival der Bodensee-Winzer (Nonnenhorn, Wasserburg, Lindau, Bodolz).
  - *13.–14.08.2027:* **Winzerfest Nonnenhorn** (Uferpromenade).
- **Neue abrechnungsfähige Dienstleistungen:**
  - `[SRV-LOG-VERSAND]` *Versand- & Logistik-Support (Kommissionierung & Fulfillment)* (45,00 €/Std.) – zur sauberen Abrechnung der B2B-Unterstützung für die Naper GmbH (Ken Kurtzweg).
  - `[SRV-DMX-PROG]` *DMX-Lichtprogrammierung & Wolfmix W1 Show-Setup* (65,00 €/Std.) – für Show-Programmierung und Fixture-Setups vor Ort.

### G. Standard-Einsatzvorlagen (Templates für Events & B2B)
- **🎪 Event-Einsatz & Betreuung (Task #1449):**
  - Standardisiertes 5-Phasen-Gerüst: *Event-Steckbrief & Stromversorgung* (Schuko/CEE), *Lager-Packliste* (Ton, Licht, Strom, PSA), *Aufbau & Einmessen* (DIN 15905-5 Lärmschutz, DSP-Limiter), *Live-Betrieb*, *Abbau & Abrechnung*.
  - Verankert im Vorlagenprojekt (#164) und sofort duplizierbar für jeden anstehenden Auftrag.
- **📦 B2B Logistik & Fulfillment-Support (Angebotsvorlage #8):**
  - Fertig konfiguriertes Angebots-Template mit 10-Stunden-Startkontingent (450,00 € gem. § 19 UStG) für die Naper GmbH.
  - Mit der Quick-Quote-Engine (`python quick_quote.py --lead 83 --template 8`) in unter 2 Sekunden als Angebot `S00052` generiert und mit Lead #83 verknüpft.

### H. DevOps, Cron-Health & Tagesbericht-Präzision (Regel 7)
- **Tagesbericht an Wolf (Cron 44 / Server-Aktion 828):**
  - Läuft täglich um **12:04 Uhr MESZ** (10:04 UTC) und sendet die Lageübersicht an `wolf@frawo.tech`.
  - **100 % Standort-Präzision:** Alle 17 zuvor ortlosen Aufgaben in den Stufen *Als Nächstes* und *In Arbeit* wurden mit exakten Orts-Tags (`@rk22`, `@villa`, `@unterwegs`, `@remote`) versehen.
  - **Ergebnis:** Aufgaben ohne Ort = **0**. Wolf erhält jeden Mittag einen glasklaren, nach Standorten sortierten Einsatzplan ohne Graumeldungen.
- **Queue-Bereinigung (`TAG_BEANTWORTET` = 160):**
  - Vollständig eingepflegte Rückmeldungen (#1413 Zielkunden, #1421 PSA-Größen & FraWo-Print, #1365 Stromkosten-Berechnung 270,13 €, #1422 Christiane-Rücklage, #1406 Werkstatt-Einordnung, #385 Elvis-Sub) wurden von Tag 160 befreit.
  - Task #996 (KOHL Strato 191,76 €) wurde auf Tag 153 (`🙋 braucht Wolf`) gesetzt, da die Überweisungsdaten vollständig vorliegen und nur noch die Bankfreigabe durch Wolf ansteht.
  - **Ergebnis:** Offene Aufgaben mit Tag 160 = **0**! Die Agenten-Queue ist komplett abgearbeitet.

### I. Strategischer Realismus & Rechtssicherheit (Handwerk & Gewerbe)
- **Handwerksrechtliche Abgrenzung (Franz als Zimmerergeselle):**
  - *Eigenbedarf für Verleihpark:* Lautsprechergehäuse, Bassboxen, Racks und Kisten für das eigene Betriebsvermögen dürfen Franz und Wolf zu 100 % legal selbst bauen.
  - *Kundenaufträge:* Reine IHK-Dienstleistungen (Reparatur von Beschallungsanlagen, Chassis-Tausch, Sickeninstandsetzung, Frequenzweichenbau, REW-Akustikmessung & DSP-Einmessung).
  - *Außenauftritt:* Nie als „Schreinerei/Tischlerei“ oder „Meisterbetrieb“ werben, sondern als *„Veranstaltungstechnik & Akustikbau“* oder *„Reparatur von Beschallungsanlagen“*.
- **Investitionsrealismus:**
  - Keine teuren Kredite für CNC-Fräsen (handgeführte Oberfräse mit Fräszirkel liefert millimetergenaue Chassisausschnitte für Prototypen und Kleinserien).
  - Werkstatt-Grundausstattung (Absaugung Klasse M, Tauchsäge, Fräszirkel, Werkbank) wird schrittweise aus dem laufenden Cashflow finanziert (~1.250–2.150 €).
- **Akute Wochenend-Vorbereitung:**
  - *Samstag, 12.09.:* Leichte Liebe Open Air (Bregenz) – reiner Helfer-/Sub-Job (Task #1057), Wolf kommt nach 14 Uhr aus der Inselhalle, Sonntagfrüh 07:30 Uhr zurück.
  - *Sonntag/Montag, 13./14.09.:* Besichtigung & Abholung Getränkeautomat mit Alois (Task #1181) – technische FI-Prüfung vor Ort, Verhandlungsziel 50–100 €, 24h Stehzeit vor Inbetriebnahme beachten.
  - *Dienstag, 15.09.:* Wolfmix W1 Einlassshow-Presets Eishalle (Task #1356).

---

## 6. Zusammenfassung & Regeln für den Alltag

1. **Keine Daten duplizieren:** Ein Vorgang hat genau einen CRM-Lead und (bei Auftrag) ein verknüpftes Angebot.
2. **Keine Kaltakquise-Erfindungen:** Nur echte Kontakte und Leads erfassen. Zukunftsoptionen über den Filter `🌱 Zukunftspläne` einsteuern.
3. **1-Klick-Angebote nutzen:** Angebote immer über die Vorlagen generieren — das spart Zeit, verhindert Tippfehler und sichert die Nachverfolgung.
4. **Prüfen am Ziel:** Jedes versendete Dokument und jede Änderung am echten Datensatz nachprüfen.
