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

---

## 6. Zusammenfassung & Regeln für den Alltag

1. **Keine Daten duplizieren:** Ein Vorgang hat genau einen CRM-Lead und (bei Auftrag) ein verknüpftes Angebot.
2. **Keine Kaltakquise-Erfindungen:** Nur echte Kontakte und Leads erfassen. Zukunftsoptionen über den Filter `🌱 Zukunftspläne` einsteuern.
3. **1-Klick-Angebote nutzen:** Angebote immer über die Vorlagen generieren — das spart Zeit, verhindert Tippfehler und sichert die Nachverfolgung.
4. **Prüfen am Ziel:** Jedes versendete Dokument und jede Änderung am echten Datensatz nachprüfen.
