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

## 5. Audit: Open-Source Best Practice vs. Community-Add-Ons (OCA)

### Ehrliche Analyse des Bestands:
1. **Was bisher schief lief:**
   - Eigene Hintergrund-Skripte versuchten künstlich Leads zu generieren oder Deadlines zu polinternalisieren. Das führte zu Geisterdaten und Spam.
   - **Lösung:** Streng nach `AGENTS.md` keine eigenen Daemon-Skripte mehr. Odoos interne `base.automation` übernimmt die Event-Logik sauber und synchron.

2. **Welche OCA Community-Module lohnen sich wirklich für FraWo?**
   - **`rental` / `sale_renting` (OCA):**
     - *Nutzen:* Ermöglicht echte Geräte-Verfügbarkeitsprüfungen (z. B. „Ist das Fußballdart am 15.08. doppelt gebucht?").
     - *Status bei FraWo:* Aktuell reicht die Terminkalender-Automatik (Automation ID 18), da FraWo 1x Fußballdart und 2 PA-Sets besitzt. Sobald der Gerätepool wächst, ist das OCA-Mietmodul die erste Wahl.
   - **`account_invoice_ubl` / XRechnung (OCA / Odoo e-invoicing):**
     - *Nutzen:* Gesetzlich vorgeschriebenes elektronisches Rechnungsformat für Behörden und Kommunen (Stadt Wangen, Bauhof).
     - *Empfehlung:* Bei der ersten offiziellen Rechnung an die Stadt Wangen zuschalten.
   - **Website Lead Scraper / Event-Bots:**
     - *Warnung:* Es gibt im Odoo App Store diverse "Lead Scraper". Fast alle sind fehleranfällig, erzeugen Dubletten-Müll und verstoßen gegen DSGVO/Wettbewerbsrecht (Cold-Calling-Verbot).
     - *Best Practice:* Gezielte Recherche von Veranstaltungen am Bodensee (Komm & See, Stadtfeste) und saubere, kuratierte Stammdatenpflege — Qualität vor Quantität.
